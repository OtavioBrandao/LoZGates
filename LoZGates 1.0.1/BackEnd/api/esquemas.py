"""Formatos de entrada da API (validados pelo FastAPI antes de chegar ao core)."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from BackEnd.api import limites


def _nao_vazia(valor: str) -> str:
    if not valor or not valor.strip():
        raise ValueError("A expressão não pode estar vazia.")
    return valor


class Expressao(BaseModel):
    expressao: str = Field(..., max_length=limites.TAMANHO_MAXIMO_DA_EXPRESSAO)

    _validar = field_validator("expressao")(_nao_vazia)


class ParDeExpressoes(BaseModel):
    expressao1: str = Field(..., max_length=limites.TAMANHO_MAXIMO_DA_EXPRESSAO)
    expressao2: str = Field(..., max_length=limites.TAMANHO_MAXIMO_DA_EXPRESSAO)

    @field_validator("expressao1", "expressao2")
    @classmethod
    def _nao_vazias(cls, valor: str) -> str:
        if not valor or not valor.strip():
            raise ValueError("As expressões não podem estar vazias.")
        return valor


class EstadoInterativo(BaseModel):
    estado: Dict[str, Any]


class AplicacaoDeLei(EstadoInterativo):
    lei: int = Field(..., ge=0)


class Resposta(BaseModel):
    resposta: str = Field(..., max_length=limites.TAMANHO_MAXIMO_DA_EXPRESSAO)


class LayoutDoCircuito(Expressao):
    valores: Optional[Dict[str, bool]] = None


class Netlist(BaseModel):
    componentes: List[Dict[str, Any]] = Field(..., max_length=limites.COMPONENTES_NO_CIRCUITO)
    fios: List[Dict[str, Any]] = Field(default_factory=list, max_length=limites.COMPONENTES_NO_CIRCUITO * 3)


class ValidacaoDoCircuito(Expressao):
    modo: str = "livre"
    netlist: Netlist


class SimulacaoDoCircuito(BaseModel):
    netlist: Netlist
    valores: Dict[str, bool]


class PedidoDeSugestao(BaseModel):
    expressao: str = Field(..., max_length=limites.TAMANHO_MAXIMO_DA_EXPRESSAO)
    contexto: str = Field("", max_length=limites.TAMANHO_MAXIMO_DA_PERGUNTA)


class Pergunta(BaseModel):
    pergunta: str = Field(..., min_length=1, max_length=limites.TAMANHO_MAXIMO_DA_PERGUNTA)
    expressao: str = Field("", max_length=limites.TAMANHO_MAXIMO_DA_EXPRESSAO)


class SessaoDeUso(BaseModel):
    """Sessão gravada no navegador (ver BackEnd/telemetria/reconstrucao.py)."""
    id_usuario: str = Field(..., max_length=128)
    plataforma: str = Field(..., max_length=300)
    sistema: str = Field(..., max_length=100)
    inicio: float
    fim: float
    fuso_minutos: int = Field(0, ge=-14 * 60, le=14 * 60)
    versao_app: str = Field("1.0-beta", max_length=32)
    envio: Optional[float] = None
    chamadas: List[Dict[str, Any]] = Field(default_factory=list)
