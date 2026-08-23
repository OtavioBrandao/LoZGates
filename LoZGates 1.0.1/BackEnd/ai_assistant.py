"""Asynchronous, UI-agnostic facade for the optional AI integration."""

from __future__ import annotations

import logging
import re
import threading
from collections.abc import Callable

from BackEnd.ai_client import AIClient, AIClientError
from config import AISettings


logger = logging.getLogger(__name__)
AIResultCallback = Callable[[str | None, str | None], None]


class AIAssistant:
    """Prepare prompts and perform requests outside the Tkinter event loop."""

    def __init__(
        self,
        settings: AISettings | None = None,
        client: AIClient | None = None,
    ) -> None:
        self.client = client or AIClient(settings=settings)

    @property
    def configured(self) -> bool:
        return self.client.configured

    def get_ai_suggestion(
        self,
        expression: str,
        step_context: str = "",
        callback: AIResultCallback | None = None,
    ) -> threading.Thread:
        prompt = f"""Analise esta expressão de lógica proposicional:

Expressão: {expression}
Contexto do passo: {step_context or "não informado"}

Identifique uma lei aplicável, explique o passo e mostre o resultado esperado.
Considere De Morgan, distributiva, absorção, identidade, nula, inversa e
idempotência. Responda em português no formato:

Lei: [nome]
Aplicação: [explicação]
Resultado: [expressão]
"""
        return self._request_async(
            prompt,
            "Você é um professor especialista em lógica proposicional. "
            "Seja preciso, didático e não invente equivalências.",
            max_tokens=400,
            callback=callback,
        )

    def ask_question(
        self,
        question: str,
        expression: str,
        callback: AIResultCallback | None = None,
    ) -> threading.Thread:
        prompt = f"""Responda à pergunta sobre lógica proposicional.

Expressão em análise: {expression or "não informada"}
Pergunta: {question}

Explique de forma didática, use símbolos lógicos apropriados e inclua um
exemplo apenas quando ele ajudar. Responda em português.
"""
        return self._request_async(
            prompt,
            "Você é um professor de lógica proposicional. Seja claro e preciso.",
            max_tokens=500,
            callback=callback,
        )

    def _request_async(
        self,
        prompt: str,
        system_prompt: str,
        *,
        max_tokens: int,
        callback: AIResultCallback | None,
    ) -> threading.Thread:
        def make_request() -> None:
            try:
                response = self.client.complete(
                    [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.2,
                )
            except AIClientError as exc:
                logger.warning("AI request unavailable: %s", exc)
                if callback:
                    callback(None, exc.user_message)
                return
            except Exception:
                logger.exception("Unexpected AI assistant failure")
                if callback:
                    callback(None, "Não foi possível consultar a IA neste momento.")
                return

            if callback:
                callback(self._format_response(response), None)

        thread = threading.Thread(
            target=make_request,
            name="lozgates-ai-request",
            daemon=True,
        )
        thread.start()
        return thread

    def _format_response(self, response: str) -> str:
        """Normalize whitespace and notation for presentation in the chat."""
        if not response:
            return "Resposta não disponível."

        response = re.sub(r"\n\s*\n\s*\n", "\n\n", response.strip())
        response = self._fix_math_formatting(response)
        response = re.sub(r"\. ([A-ZÁÉÍÓÚ])", r".\n\n\1", response)
        response = re.sub(r"\n[-*] ", "\n• ", response)

        for old, new in (("<->", "↔"), ("->", "→"), ("*", "∧"), ("+", "∨"), ("~", "¬")):
            response = response.replace(old, new)
        return response

    @staticmethod
    def _fix_math_formatting(text: str) -> str:
        text = re.sub(
            r"\(\s*([^)]+?)\s*\)",
            lambda match: f"({match.group(1).replace(chr(10), '').strip()})",
            text,
        )
        text = re.sub(r"\n\s*([∧∨¬→↔≡])\s*\n", r" \1 ", text)
        text = re.sub(
            r"([A-Z])\s*\n\s*([∧∨¬→↔≡])\s*\n\s*([A-Z¬])",
            r"\1 \2 \3",
            text,
        )
        text = re.sub(r"([A-Z¬])\s+([∧∨])\s+([A-Z¬])", r"\1\2\3", text)
        text = re.sub(
            r"([A-Z¬()]+)\s*≡\s*([A-Z¬()0-9]+)", r"\1 ≡ \2", text
        )
        return text

    def format_mathematical_text(self, text: str) -> str:
        """Public compatibility helper used by the interface."""
        text = text.replace("~", "¬").replace("*", "∧").replace("+", "∨")
        text = re.sub(r"\(P¬P\)", "(P∧¬P)", text)
        text = self._fix_math_formatting(text)
        if "Lei:" in text and "Aplicação:" in text:
            text = re.sub(r"Lei:\s*([^\n]+)", r"**Lei:** \1", text)
            text = re.sub(r"Aplicação:\s*", "\n**Aplicação:**\n", text)
        return text
