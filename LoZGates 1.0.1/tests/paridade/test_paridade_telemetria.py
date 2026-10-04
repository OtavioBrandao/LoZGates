"""
Paridade do registro de uso: a mesma sessão, refeita no DetailedUserLogger
original (oráculo) e reconstruída pelo servidor novo, produz exatamente o mesmo
JSON — é ele que chega ao Google Forms da pesquisa.
"""
from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("customtkinter")

from BackEnd.telemetria.reconstrucao import dados_para_envio, reconstruir, resumir, sessao_gravada  # noqa: E402
from tests.paridade import oraculo, sessao_de_uso  # noqa: E402

antigo = oraculo.modulo("FrontEnd.services.logging_service")


class Relogio:
    def __init__(self):
        self.instante = sessao_de_uso.INICIO
        self.fuso = timezone(timedelta(minutes=sessao_de_uso.FUSO_MINUTOS))

    def time(self):
        return self.instante

    def agora(self):
        return datetime.fromtimestamp(self.instante, self.fuso).replace(tzinfo=None)


class PlataformaFalsa:
    @staticmethod
    def platform():
        return "Navegador de teste"

    @staticmethod
    def system():
        return "Windows"


@pytest.fixture
def registro_antigo(monkeypatch, tmp_path):
    relogio = Relogio()
    monkeypatch.setattr(antigo, "time", relogio)
    monkeypatch.setattr(antigo, "datetime", type("DatetimeFalso", (), {"now": staticmethod(relogio.agora)}))
    monkeypatch.setattr(antigo, "platform", PlataformaFalsa)
    for nome in ("ACTIVITY_LOG_PATH", "ACTIVITY_SETTINGS_PATH", "LEGACY_ACTIVITY_LOG_PATH", "LEGACY_ACTIVITY_SETTINGS_PATH"):
        monkeypatch.setattr(antigo, nome, tmp_path / f"{nome}.json")
    monkeypatch.setattr(antigo.DetailedUserLogger, "_generate_anonymous_id", lambda self: "aluno-123")

    registro = antigo.DetailedUserLogger("1.0-beta")
    for (metodo, argumentos), momento in zip(sessao_de_uso.CHAMADAS, sessao_de_uso.momentos()):
        relogio.instante = momento
        getattr(registro, metodo)(*argumentos)
    relogio.instante = sessao_de_uso.FIM
    registro.end_session()
    return registro


def test_sessao_gravada_identica(registro_antigo):
    novo = reconstruir(sessao_gravada(sessao_de_uso.como_dados()))
    assert novo.current_session == registro_antigo.current_session


def test_resumo_enviado_a_pesquisa_identico(registro_antigo):
    resumo_novo = resumir(sessao_gravada(sessao_de_uso.como_dados()))["resumo"]
    assert resumo_novo == registro_antigo.get_current_session_summary()


def test_campos_do_formulario(registro_antigo):
    envio = dados_para_envio(sessao_gravada(sessao_de_uso.como_dados(envio=sessao_de_uso.FIM + 5)))
    assert envio["app_version"] == "1.0"
    assert envio["platform"] == "Windows"
    assert envio["summary_json"] == registro_antigo.get_current_session_summary()
    assert envio["submission_date"] == datetime.fromtimestamp(
        sessao_de_uso.FIM + 5, timezone(timedelta(minutes=sessao_de_uso.FUSO_MINUTOS))
    ).replace(tzinfo=None).isoformat()
