"""Banco de problemas, assistente de IA, registro de uso e textos de ajuda."""
from dataclasses import asdict

from fastapi import APIRouter, Request

import config
from BackEnd.api.erros import NaoEncontrado
from BackEnd.api.esquemas import PedidoDeSugestao, Pergunta, Resposta, SessaoDeUso
from BackEnd.problemas import listar_problemas, obter_problema, verificar_resposta_do_problema
from BackEnd.telemetria import reconstrucao

router = APIRouter()


# ------------------------------ banco de problemas ------------------------------

@router.get("/problemas")
def problemas():
    return listar_problemas()


def _problema(indice: int):
    try:
        return obter_problema(indice)
    except IndexError as erro:
        raise NaoEncontrado(str(erro)) from erro


@router.get("/problemas/{indice}")
def problema(indice: int):
    return _problema(indice)


@router.post("/problemas/{indice}/verificar")
def verificar(indice: int, entrada: Resposta):
    _problema(indice)
    return asdict(verificar_resposta_do_problema(indice, entrada.resposta))


# ------------------------------ assistente de IA (proxy; a chave fica no servidor) ------------------------------

@router.get("/ia/estado")
def estado_da_ia(request: Request):
    return {"configurada": request.app.state.assistente.configured}


@router.post("/ia/sugestao")
def sugestao(entrada: PedidoDeSugestao, request: Request):
    return {"resposta": request.app.state.assistente.sugerir(entrada.expressao, entrada.contexto)}


@router.post("/ia/pergunta")
def pergunta(entrada: Pergunta, request: Request):
    return {"resposta": request.app.state.assistente.perguntar(entrada.pergunta, entrada.expressao)}


# ------------------------------ registro de uso (os dados ficam no navegador) ------------------------------

@router.post("/telemetria/resumo")
def resumo_de_uso(entrada: SessaoDeUso):
    return reconstrucao.resumir(reconstrucao.sessao_gravada(entrada.model_dump()))


@router.post("/telemetria/enviar")
def enviar_uso(entrada: SessaoDeUso, request: Request):
    sessao = reconstrucao.sessao_gravada(entrada.model_dump())
    return {"enviado": reconstrucao.enviar(sessao, request.app.state.enviador_de_formulario)}


# ------------------------------ textos de ajuda ------------------------------

@router.get("/conteudo")
def conteudo():
    return {
        "boas_vindas": config.welcome_message,
        "duvida_circuitos": config.duvida_circuitos,
        "informacoes": config.informacoes,
        "exemplos": config.INTERACTIVE_EXAMPLES,
        "dicas": config.CONTEXTUAL_TIPS,
        "perguntas_frequentes": config.COMMON_FAQ,
    }
