"""
Reconstrução, no servidor, de uma sessão de uso gravada no navegador (D6).

Os dados ficam no navegador: ele guarda só a lista de chamadas ao registro de
uso (método, argumentos e o instante de cada uma). Para montar o resumo, a
prévia do diálogo de consentimento e o envio à pesquisa, as chamadas são
refeitas, na mesma ordem e com os mesmos horários, num DetailedUserLogger em
memória. Assim o JSON que chega ao Google Forms é calculado pelo mesmo código
de sempre, e o servidor não guarda nada.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from BackEnd.telemetria.google_forms import ImprovedGoogleFormsSubmitter, criar_previa
from BackEnd.telemetria.registro_uso import DetailedUserLogger

# Só estes métodos podem ser refeitos a partir dos dados do navegador
METODOS_PERMITIDOS = frozenset({
    "log_event",
    "log_expression_entered",
    "log_interactive_simplification_start",
    "log_law_applied",
    "log_simplification_skip",
    "log_simplification_undo",
    "log_simplification_completed",
    "log_simplification_step_failed",
    "log_circuit_interaction_start",
    "log_component_action",
    "log_circuit_test",
    "log_equivalence_check_with_expressions",
    "log_feature_used",
    "log_error",
    "log_tab_changed",
})
MAXIMO_DE_CHAMADAS = 5000


class TelemetriaInvalida(ValueError):
    """Os dados de uso enviados pelo navegador estão malformados."""


class RelogioDeReconstrucao:
    """Relógio parado no instante de cada chamada, no fuso do aluno."""

    def __init__(self, instante: float, fuso_minutos: int):
        self.instante = instante
        self.fuso = timezone(timedelta(minutes=fuso_minutos))

    def time(self) -> float:
        return self.instante

    def now(self) -> datetime:
        # Sem fuso no texto, como o desktop gravava (datetime.now().isoformat())
        return datetime.fromtimestamp(self.instante, self.fuso).replace(tzinfo=None)


@dataclass
class Chamada:
    metodo: str
    argumentos: List[Any]
    momento: float


@dataclass
class SessaoGravada:
    id_usuario: str
    plataforma: str
    sistema: str
    inicio: float
    fim: float
    fuso_minutos: int = 0
    versao_app: str = "1.0-beta"
    chamadas: List[Chamada] = field(default_factory=list)
    envio: Optional[float] = None


def sessao_gravada(dados: Dict[str, Any]) -> SessaoGravada:
    try:
        chamadas = [
            Chamada(str(c["metodo"]), list(c.get("argumentos", [])), float(c["momento"]))
            for c in dados.get("chamadas", [])
        ]
        sessao = SessaoGravada(
            id_usuario=str(dados["id_usuario"]),
            plataforma=str(dados["plataforma"]),
            sistema=str(dados["sistema"]),
            inicio=float(dados["inicio"]),
            fim=float(dados["fim"]),
            fuso_minutos=int(dados.get("fuso_minutos", 0)),
            versao_app=str(dados.get("versao_app", "1.0-beta")),
            chamadas=chamadas,
            envio=None if dados.get("envio") is None else float(dados["envio"]),
        )
    except (KeyError, TypeError, ValueError) as erro:
        raise TelemetriaInvalida(f"Sessão de uso incompleta: {erro}") from erro
    if len(sessao.chamadas) > MAXIMO_DE_CHAMADAS:
        raise TelemetriaInvalida("Sessão de uso grande demais.")
    for chamada in sessao.chamadas:
        if chamada.metodo not in METODOS_PERMITIDOS:
            raise TelemetriaInvalida(f"Registro de uso desconhecido: {chamada.metodo!r}")
    return sessao


def reconstruir(sessao: SessaoGravada) -> DetailedUserLogger:
    """Refaz as chamadas num registro em memória e encerra a sessão, como o desktop ao fechar."""
    relogio = RelogioDeReconstrucao(sessao.inicio, sessao.fuso_minutos)
    registro = DetailedUserLogger(
        sessao.versao_app,
        user_id=sessao.id_usuario,
        plataforma=sessao.plataforma,
        sistema=sessao.sistema,
        relogio=relogio,
        persistir=False,
    )
    for chamada in sessao.chamadas:
        relogio.instante = chamada.momento
        try:
            getattr(registro, chamada.metodo)(*chamada.argumentos)
        except TypeError as erro:
            raise TelemetriaInvalida(f"Argumentos inválidos para {chamada.metodo}: {erro}") from erro
    relogio.instante = sessao.fim
    registro.end_session()
    return registro


def resumir(sessao: SessaoGravada) -> Dict[str, Any]:
    """Sessão encerrada, resumo dela e a prévia que o diálogo de consentimento mostra."""
    registro = reconstruir(sessao)
    resumo = registro.get_current_session_summary()
    return {"sessao": registro.current_session, "resumo": resumo, "previa": criar_previa(resumo)}


def dados_para_envio(sessao: SessaoGravada) -> Dict[str, Any]:
    registro = reconstruir(sessao)
    if sessao.envio is not None:
        registro._relogio.instante = sessao.envio
    return DetailedUserLogger.create_formatted_shareable_data(registro)


def enviar(sessao: SessaoGravada, enviador: Optional[ImprovedGoogleFormsSubmitter] = None) -> bool:
    """Envia ao Google Forms da pesquisa (só depois do consentimento, no navegador)."""
    return (enviador or ImprovedGoogleFormsSubmitter()).submit_data(dados_para_envio(sessao))
