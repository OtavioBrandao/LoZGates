import pytest
from fastapi.testclient import TestClient

from BackEnd.ai_client import AIConfigurationError
from BackEnd.api.app import criar_app


class AssistenteFalso:
    """IA de mentira: os testes da API não saem para a rede."""

    def __init__(self, configurada=True):
        self.configured = configurada
        self.pedidos = []

    def sugerir(self, expressao, contexto=""):
        if not self.configured:
            raise AIConfigurationError("A IA não está configurada. Defina LOZGATES_AI_API_KEY ou GROQ_API_KEY.")
        self.pedidos.append(("sugestao", expressao, contexto))
        return f"Lei: Identidade\nResultado: {expressao}"

    def perguntar(self, pergunta, expressao):
        self.pedidos.append(("pergunta", pergunta, expressao))
        return f"Resposta para: {pergunta}"


class EnviadorFalso:
    def __init__(self, sucesso=True):
        self.sucesso = sucesso
        self.envios = []

    def submit_data(self, dados):
        self.envios.append(dados)
        return self.sucesso


@pytest.fixture
def assistente():
    return AssistenteFalso()


@pytest.fixture
def enviador():
    return EnviadorFalso()


@pytest.fixture
def cliente(assistente, enviador):
    return TestClient(criar_app(assistente=assistente, enviador_de_formulario=enviador, pasta_do_frontend=None))
