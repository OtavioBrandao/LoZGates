"""
Tradução das exceções do core para respostas HTTP com mensagem clara.

Formato de todo erro:
    {"erro": {"tipo": "...", "mensagem": "...", "posicao": 3}}   (posicao só em expressão inválida)
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from BackEnd.ai_client import AIClientError, AIConfigurationError
from BackEnd.circuito_logico.logic.validacao import CircuitoInvalido
from BackEnd.core.expression_ast import ExpressaoInvalida
from BackEnd.core.sessao_interativa import EstadoInvalido
from BackEnd.telemetria.reconstrucao import TelemetriaInvalida

logger = logging.getLogger(__name__)


class LimiteExcedido(ValueError):
    """A entrada é válida, mas grande demais para o servidor processar."""


class NaoEncontrado(LookupError):
    pass


def _resposta(status: int, tipo: str, mensagem: str, **extra) -> JSONResponse:
    return JSONResponse(status_code=status, content={"erro": {"tipo": tipo, "mensagem": mensagem, **extra}})


def registrar(app: FastAPI) -> None:
    @app.exception_handler(ExpressaoInvalida)
    async def expressao_invalida(_: Request, erro: ExpressaoInvalida):
        return _resposta(422, "expressao_invalida", erro.mensagem, posicao=erro.posicao)

    @app.exception_handler(EstadoInvalido)
    async def estado_invalido(_: Request, erro: EstadoInvalido):
        return _resposta(422, "estado_invalido", str(erro))

    @app.exception_handler(CircuitoInvalido)
    async def circuito_invalido(_: Request, erro: CircuitoInvalido):
        return _resposta(422, "circuito_invalido", str(erro))

    @app.exception_handler(TelemetriaInvalida)
    async def telemetria_invalida(_: Request, erro: TelemetriaInvalida):
        return _resposta(422, "telemetria_invalida", str(erro))

    @app.exception_handler(LimiteExcedido)
    async def limite_excedido(_: Request, erro: LimiteExcedido):
        return _resposta(422, "limite_excedido", str(erro))

    @app.exception_handler(NaoEncontrado)
    async def nao_encontrado(_: Request, erro: NaoEncontrado):
        return _resposta(404, "nao_encontrado", str(erro))

    @app.exception_handler(AIConfigurationError)
    async def ia_nao_configurada(_: Request, erro: AIConfigurationError):
        return _resposta(503, "ia_nao_configurada", erro.user_message)

    @app.exception_handler(AIClientError)
    async def ia_indisponivel(_: Request, erro: AIClientError):
        return _resposta(502, "ia_indisponivel", erro.user_message)

    @app.exception_handler(RequestValidationError)
    async def requisicao_invalida(_: Request, erro: RequestValidationError):
        primeiro = erro.errors()[0] if erro.errors() else {}
        campo = ".".join(str(parte) for parte in primeiro.get("loc", ()) if parte != "body")
        mensagem = primeiro.get("msg", "Requisição inválida.")
        return _resposta(422, "requisicao_invalida", f"{campo}: {mensagem}" if campo else mensagem)
