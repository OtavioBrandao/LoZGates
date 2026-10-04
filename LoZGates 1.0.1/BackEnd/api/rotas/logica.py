"""Expressão, tabela-verdade, simplificações e equivalência."""
from dataclasses import asdict

from fastapi import APIRouter

from BackEnd.api import limites
from BackEnd.api.esquemas import AplicacaoDeLei, EstadoInterativo, Expressao, ParDeExpressoes
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.core import sessao_interativa
from BackEnd.core.expression_ast import collect_variables, parse
from BackEnd.equivalencia import comparar_expressoes
from BackEnd.identificar_lei import simplificar_expressao
from BackEnd.tabela import classificar_conclusao, gerar_tabela_verdade, verificar_conclusao

router = APIRouter()


@router.post("/expressao/converter")
def converter(entrada: Expressao):
    """Expressão em álgebra booleana e suas variáveis."""
    booleana = converter_para_algebra_booleana(entrada.expressao)
    return {
        "expressao": entrada.expressao,
        "expressao_booleana": booleana,
        "variaveis": sorted(collect_variables(parse(booleana))),
    }


@router.post("/expressao/tabela-verdade")
def tabela_verdade(entrada: Expressao):
    limites.conferir_variaveis(limites.VARIAVEIS_NA_TABELA_VERDADE, entrada.expressao)
    tabela = gerar_tabela_verdade(entrada.expressao)
    return {
        **tabela,
        "conclusao": verificar_conclusao(tabela["resultados_finais"]),
        "tipo_conclusao": classificar_conclusao(tabela["resultados_finais"]),
    }


@router.post("/simplificacao/automatica")
def simplificacao_automatica(entrada: Expressao):
    """Simplificar — Resultado: cada passo aceito, com o trecho afetado."""
    return asdict(simplificar_expressao(entrada.expressao))


@router.get("/simplificacao/interativa/leis")
def leis():
    return sessao_interativa.leis_disponiveis()


@router.post("/simplificacao/interativa/iniciar")
def iniciar_interativa(entrada: Expressao):
    return asdict(sessao_interativa.iniciar(entrada.expressao))


@router.post("/simplificacao/interativa/aplicar")
def aplicar_lei(entrada: AplicacaoDeLei):
    return asdict(sessao_interativa.aplicar_lei(entrada.estado, entrada.lei))


@router.post("/simplificacao/interativa/pular")
def pular(entrada: EstadoInterativo):
    return asdict(sessao_interativa.pular(entrada.estado))


@router.post("/simplificacao/interativa/desfazer")
def desfazer(entrada: EstadoInterativo):
    return asdict(sessao_interativa.desfazer(entrada.estado))


@router.post("/equivalencia")
def equivalencia(entrada: ParDeExpressoes):
    """Equivalência só por tabela-verdade (D3d), com o primeiro contraexemplo."""
    limites.conferir_variaveis(limites.VARIAVEIS_NA_EQUIVALENCIA, entrada.expressao1, entrada.expressao2)
    return asdict(comparar_expressoes(entrada.expressao1, entrada.expressao2))
