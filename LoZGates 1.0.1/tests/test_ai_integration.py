import json
import threading
import unittest
import urllib.error
import urllib.request

import requests

from BackEnd.ai_assistant import AIAssistant
from BackEnd.ai_client import AIClient, AIClientError, AIConfigurationError
from config import AISettings
from services.ai_service import create_server


def settings(**overrides):
    values = {
        "api_key": "test-key",
        "api_url": "https://provider.invalid/v1/chat/completions",
        "model": "test-model",
        "timeout_seconds": 3.5,
        "service_url": "",
    }
    values.update(overrides)
    return AISettings(**values)


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=None):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.payload


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


class AIClientTests(unittest.TestCase):
    def test_missing_key_fails_before_network(self):
        session = FakeSession()
        client = AIClient(settings(api_key=""), session=session)
        with self.assertRaises(AIConfigurationError):
            client.complete([{"role": "user", "content": "teste"}])
        self.assertEqual(session.calls, [])

    def test_provider_payload_and_response(self):
        session = FakeSession(
            FakeResponse(payload={"choices": [{"message": {"content": "  resposta  "}}]})
        )
        client = AIClient(settings(), session=session)
        result = client.complete([{"role": "user", "content": "teste"}], max_tokens=42)

        self.assertEqual(result, "resposta")
        url, request = session.calls[0]
        self.assertEqual(url, "https://provider.invalid/v1/chat/completions")
        self.assertEqual(request["json"]["model"], "test-model")
        self.assertEqual(request["json"]["max_tokens"], 42)
        self.assertEqual(request["timeout"], 3.5)
        self.assertEqual(request["headers"]["Authorization"], "Bearer test-key")

    def test_timeout_and_invalid_response_are_user_friendly(self):
        timeout_client = AIClient(
            settings(), session=FakeSession(error=requests.Timeout("late"))
        )
        with self.assertRaisesRegex(AIClientError, "limite"):
            timeout_client.complete([{"role": "user", "content": "teste"}])

        invalid_client = AIClient(
            settings(), session=FakeSession(FakeResponse(payload={"choices": []}))
        )
        with self.assertRaisesRegex(AIClientError, "resposta inválida"):
            invalid_client.complete([{"role": "user", "content": "teste"}])

    def test_service_url_uses_companion_contract(self):
        session = FakeSession(FakeResponse(payload={"content": "via serviço"}))
        client = AIClient(
            settings(api_key="", service_url="http://127.0.0.1:9000"),
            session=session,
        )
        self.assertEqual(
            client.complete([{"role": "user", "content": "teste"}]),
            "via serviço",
        )
        self.assertEqual(
            session.calls[0][0],
            "http://127.0.0.1:9000/v1/chat/completions",
        )


class AIAssistantTests(unittest.TestCase):
    def test_async_error_callback_uses_error_slot(self):
        assistant = AIAssistant(settings=settings(api_key=""))
        completed = threading.Event()
        result = []

        def callback(response, error):
            result.append((response, error))
            completed.set()

        thread = assistant.ask_question("O que é AND?", "A*B", callback)
        self.assertTrue(completed.wait(2))
        thread.join(2)
        self.assertIsNone(result[0][0])
        self.assertIn("não está configurada", result[0][1])


class FakeServiceClient:
    configured = True

    def complete(self, messages, max_tokens=500, temperature=0.2):
        return f"recebi {len(messages)} mensagem(ns)"


class AIServiceTests(unittest.TestCase):
    def setUp(self):
        self.server = create_server("127.0.0.1", 0, FakeServiceClient())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)

    def test_health_and_completion_endpoints(self):
        with urllib.request.urlopen(f"{self.base_url}/health", timeout=2) as response:
            health = json.load(response)
        self.assertEqual(health, {"status": "ok", "configured": True})

        request = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(
                {"messages": [{"role": "user", "content": "teste"}]}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            result = json.load(response)
        self.assertEqual(result["content"], "recebi 1 mensagem(ns)")

    def test_invalid_request_is_rejected(self):
        request = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(request, timeout=2)
        self.assertEqual(raised.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
