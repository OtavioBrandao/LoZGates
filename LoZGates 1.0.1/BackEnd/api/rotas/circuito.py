"""Circuito gerado (layout em JSON) e editor interativo (componentes, validação, simulação)."""
from dataclasses import asdict

from fastapi import APIRouter

from BackEnd.api import limites
from BackEnd.api.esquemas import Expressao, LayoutDoCircuito, SimulacaoDoCircuito, ValidacaoDoCircuito
from BackEnd.circuito_logico.logic.componentes import componentes_iniciais, definicoes
from BackEnd.circuito_logico.logic.layout import montar_layout
from BackEnd.circuito_logico.logic.validacao import montar_netlist, simular, validar_circuito
from BackEnd.circuito_logico.modos import DICAS, MODOS
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.core.expression_ast import collect_variables, parse

router = APIRouter(prefix="/circuito")


@router.post("/layout")
def layout(entrada: LayoutDoCircuito):
    limites.conferir_variaveis(limites.VARIAVEIS_NA_EQUIVALENCIA, entrada.expressao)
    return montar_layout(entrada.expressao, entrada.valores)


@router.get("/modos")
def modos():
    return [{"chave": chave, **info, "dicas": DICAS[chave]} for chave, info in MODOS.items()]


@router.get("/componentes")
def componentes():
    return definicoes()


@router.post("/editor")
def editor(entrada: Expressao):
    """Componentes iniciais do editor: as variáveis da expressão e a saída."""
    booleana = converter_para_algebra_booleana(entrada.expressao)
    variaveis = sorted(collect_variables(parse(booleana)))
    return {"expressao_booleana": booleana, "variaveis": variaveis, "componentes": componentes_iniciais(variaveis)}


@router.post("/validar")
def validar(entrada: ValidacaoDoCircuito):
    booleana = converter_para_algebra_booleana(entrada.expressao)
    limites.conferir_variaveis(limites.VARIAVEIS_NA_EQUIVALENCIA, booleana)
    netlist = montar_netlist(entrada.netlist.model_dump())
    return asdict(validar_circuito(booleana, netlist, entrada.modo))


@router.post("/simular")
def simulacao(entrada: SimulacaoDoCircuito):
    return {"saidas": simular(montar_netlist(entrada.netlist.model_dump()), entrada.valores)}
