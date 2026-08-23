"""Small HTTP boundary around the optional AI provider integration."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from BackEnd.ai_client import AIClient, AIClientError, AIConfigurationError
from BackEnd.logging_config import configure_logging
from config import AISettings, ensure_runtime_directories


logger = logging.getLogger(__name__)
MAX_REQUEST_BYTES = 1_000_000


class AIServiceHandler(BaseHTTPRequestHandler):
    """Serve health checks and OpenAI-shaped completion requests."""

    server_version = "LoZGatesAI/1.0"

    @property
    def ai_client(self) -> AIClient:
        return self.server.ai_client  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path != "/health":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})
            return
        configured = self.ai_client.configured
        self._send_json(
            HTTPStatus.OK,
            {
                "status": "ok" if configured else "degraded",
                "configured": configured,
            },
        )

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path != "/v1/chat/completions":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})
            return
        try:
            payload = self._read_json()
            messages = payload.get("messages")
            if not isinstance(messages, list) or not messages:
                raise ValueError("O campo 'messages' deve ser uma lista não vazia.")
            content = self.ai_client.complete(
                messages,
                max_tokens=payload.get("max_tokens", 500),
                temperature=payload.get("temperature", 0.2),
            )
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except AIConfigurationError as exc:
            self._send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": exc.user_message},
            )
        except AIClientError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"error": exc.user_message},
            )
        except Exception:
            logger.exception("Unexpected AI service failure")
            self._send_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "Falha interna no serviço de IA."},
            )
        else:
            self._send_json(HTTPStatus.OK, {"content": content})

    def _read_json(self) -> dict:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Content-Length inválido.") from exc
        if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
            raise ValueError("Corpo da requisição ausente ou grande demais.")
        try:
            payload = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("O corpo precisa ser um objeto JSON válido.") from exc
        if not isinstance(payload, dict):
            raise ValueError("O corpo precisa ser um objeto JSON.")
        return payload

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:
        logger.debug("HTTP %s - %s", self.address_string(), format % args)


def create_server(
    host: str,
    port: int,
    client: AIClient | None = None,
) -> ThreadingHTTPServer:
    if client is None:
        direct_settings = replace(
            AISettings.from_environment(),
            service_url="",
        )
        client = AIClient(settings=direct_settings)
    server = ThreadingHTTPServer((host, port), AIServiceHandler)
    server.ai_client = client  # type: ignore[attr-defined]
    return server


def main() -> None:
    ensure_runtime_directories()
    configure_logging()
    host = os.getenv("LOZGATES_AI_SERVICE_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("LOZGATES_AI_SERVICE_PORT", "8000"))
    except ValueError as exc:
        raise SystemExit("LOZGATES_AI_SERVICE_PORT precisa ser um inteiro.") from exc

    server = create_server(host, port)
    logger.info("AI service listening on %s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("AI service interrupted")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
