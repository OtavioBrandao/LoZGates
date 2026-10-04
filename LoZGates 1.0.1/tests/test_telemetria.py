"""Registro de uso no navegador, reconstruído no servidor (BackEnd/telemetria)."""
import pytest

from BackEnd.telemetria.google_forms import ENTRY_MAPPING, ImprovedGoogleFormsSubmitter, criar_previa
from BackEnd.telemetria.reconstrucao import TelemetriaInvalida, enviar, reconstruir, resumir, sessao_gravada
from tests.paridade import sessao_de_uso


def test_reconstrucao_usa_horarios_do_aluno_e_identidade_do_cliente():
    registro = reconstruir(sessao_gravada(sessao_de_uso.como_dados()))
    sessao = registro.current_session
    assert sessao["user_id"] == "aluno-123"
    assert sessao["platform"] == "Navegador de teste"
    # 1_790_000_000 UTC = 2026-09-21 14:13:20 -> 11:13:20 em Brasília
    assert sessao["start_time"] == "2026-09-21T11:13:20"
    assert sessao["duration_seconds"] == round(sessao_de_uso.FIM - sessao_de_uso.INICIO, 2)
    assert sessao["events_count"] == len(sessao["events"]) == len(sessao_de_uso.CHAMADAS)  # um evento por chamada
    assert sessao["interactive_circuit"]["components_added"] == {"nand": 1}
    assert sessao["interactive_simplification"]["laws_applied"] == {"Identidade (A * 1 = A)": 1}


def test_resumo_e_previa():
    resultado = resumir(sessao_gravada(sessao_de_uso.como_dados()))
    assert resultado["resumo"]["equivalence_checks"]["total_checks"] == 2
    assert "VERIFICAÇÃO DE EQUIVALÊNCIA" in resultado["previa"]
    assert resultado["previa"] == criar_previa(resultado["resumo"])


@pytest.mark.parametrize("dados, trecho", [
    ({}, "incompleta"),
    ({**sessao_de_uso.como_dados(), "chamadas": [{"metodo": "end_session", "argumentos": [], "momento": 1}]}, "desconhecido"),
    ({**sessao_de_uso.como_dados(), "chamadas": [{"metodo": "log_error", "argumentos": [], "momento": 1}]}, "Argumentos inválidos"),
])
def test_dados_invalidos(dados, trecho):
    with pytest.raises(TelemetriaInvalida, match=trecho):
        reconstruir(sessao_gravada(dados))


class ClienteFalso:
    def __init__(self, status=200):
        self.status = status
        self.envios = []

    def post(self, url, data, timeout):
        self.envios.append((url, data))
        return type("Resposta", (), {"status_code": self.status})()


def test_envio_ao_formulario_usa_os_mesmos_campos():
    cliente = ClienteFalso()
    assert enviar(sessao_gravada(sessao_de_uso.como_dados()), ImprovedGoogleFormsSubmitter(sessao=cliente))
    (url, campos), = cliente.envios
    assert url.endswith("/formResponse")
    assert set(campos) == set(ENTRY_MAPPING.values())
    assert not enviar(sessao_gravada(sessao_de_uso.como_dados()), ImprovedGoogleFormsSubmitter(sessao=ClienteFalso(500)))
