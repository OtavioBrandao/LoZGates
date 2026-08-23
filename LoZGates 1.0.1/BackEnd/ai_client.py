"""Cliente sincrono e testavel para o provedor de IA ou o proxy local."""

import logging

import requests

from config import AISettings


logger = logging.getLogger(__name__)


class AIClientError(RuntimeError):
    def __init__(self, user_message, status_code=None):
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code


class AIConfigurationError(AIClientError):
    pass


class AIClient:
    def __init__(self, settings=None, session=None):
        self.settings = settings or AISettings.from_environment()
        self.session = session or requests.Session()

    @property
    def configured(self):
        return bool(self.settings.service_url or self.settings.api_key)

    def complete(self, messages, max_tokens=500, temperature=0.2):
        if not isinstance(messages, list) or not messages:
            raise AIClientError("A solicitação enviada à IA está vazia.")
        payload = {
            "messages": messages,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
        }
        if self.settings.service_url:
            return self._request_service(payload)
        return self._request_provider(payload)

    def _request_service(self, payload):
        url = f"{self.settings.service_url}/v1/chat/completions"
        response = self._post(url, payload, headers={})
        data = self._json_response(response)
        content = data.get("content") if isinstance(data, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise AIClientError("O serviço de IA retornou uma resposta inválida.")
        return content.strip()

    def _request_provider(self, payload):
        if not self.settings.api_key:
            raise AIConfigurationError(
                "A IA não está configurada. Defina LOZGATES_AI_API_KEY ou GROQ_API_KEY."
            )
        provider_payload = {
            **payload,
            "model": self.settings.model,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.api_key}",
        }
        response = self._post(self.settings.api_url, provider_payload, headers)
        data = self._json_response(response)
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise AIClientError("O provedor de IA retornou uma resposta inválida.") from error
        if not isinstance(content, str) or not content.strip():
            raise AIClientError("O provedor de IA retornou uma resposta vazia.")
        return content.strip()

    def _post(self, url, payload, headers):
        try:
            response = self.session.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.settings.timeout_seconds,
            )
        except requests.Timeout as error:
            logger.warning("Timeout ao consultar a IA em %s", url)
            raise AIClientError(
                "A IA demorou mais que o limite configurado para responder."
            ) from error
        except requests.RequestException as error:
            logger.warning("Falha de rede ao consultar a IA em %s: %s", url, error)
            raise AIClientError(
                "O serviço de IA está indisponível. Verifique sua conexão e tente novamente."
            ) from error

        if response.status_code >= 400:
            message = self._http_error_message(response.status_code)
            logger.warning(
                "Servico de IA respondeu HTTP %s em %s",
                response.status_code,
                url,
            )
            raise AIClientError(message, response.status_code)
        return response

    @staticmethod
    def _json_response(response):
        try:
            return response.json()
        except (ValueError, requests.JSONDecodeError) as error:
            raise AIClientError("O serviço de IA retornou dados que não são JSON válido.") from error

    @staticmethod
    def _http_error_message(status_code):
        if status_code == 400:
            return "A solicitação enviada à IA foi rejeitada. Verifique modelo e configuração."
        if status_code == 401:
            return "A chave da IA foi recusada. Verifique LOZGATES_AI_API_KEY."
        if status_code == 403:
            return "O modelo de IA não está liberado para esta chave ou organização."
        if status_code == 429:
            return "O limite de requisições da IA foi atingido. Aguarde e tente novamente."
        if status_code >= 500:
            return "O provedor de IA está temporariamente indisponível."
        return f"A comunicação com a IA falhou (HTTP {status_code})."
