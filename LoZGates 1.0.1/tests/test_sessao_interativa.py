"""Simplificação interativa sem estado no servidor (BackEnd/core/sessao_interativa.py)."""
import json

import pytest

from BackEnd.core import sessao_interativa as sessao
from BackEnd.core.sessao_interativa import EstadoInvalido

IDENTIDADE, INVERSA, NULA = 2, 0, 1


def metodos(resposta):
    return [e["metodo"] for e in resposta.eventos]


def test_inicio_mostra_a_menor_subexpressao_e_seu_trecho():
    resposta = sessao.iniciar("(A&1)|C", agora=1000.0)
    visao = resposta.visao
    assert visao["expressao"] == "((A*1)+C)"
    assert visao["subexpressao"] == "(A*1)"
    inicio, fim = visao["trecho"]
    assert visao["expressao"][inicio:fim] == "(A*1)"
    assert visao["historico"] == [{"tipo": "inicial", "expressao": "((A*1)+C)"}]
    assert not visao["pode_desfazer"] and not visao["concluida"]
    assert metodos(resposta) == ["log_interactive_simplification_start"]
    json.dumps(resposta.estado)  # o estado precisa viajar como JSON


def test_aplicar_lei_ate_concluir():
    resposta = sessao.iniciar("(A&1)|C", agora=1000.0)
    resposta = sessao.aplicar_lei(resposta.estado, IDENTIDADE)
    assert resposta.visao["expressao"] == "(A+C)"
    assert resposta.visao["historico"][-1] == {
        "tipo": "lei", "passo": 1, "lei": "Identidade (A * 1 = A)", "antes": "(A*1)", "depois": "(A+C)",
    }
    assert resposta.visao["subexpressao"] == "(A+C)"
    assert metodos(resposta) == ["log_law_applied"]
    resposta = sessao.pular(resposta.estado)
    assert resposta.visao["motivo_parada"] == "no_further_simplification"
    assert resposta.visao["concluida"] and resposta.visao["subexpressao"] is None
    assert metodos(resposta) == ["log_simplification_skip", "log_simplification_completed"]


def test_lei_que_nao_se_aplica_so_avisa():
    resposta = sessao.iniciar("(A&1)|C")
    seguinte = sessao.aplicar_lei(resposta.estado, INVERSA)
    assert seguinte.mensagem == "Esta lei não pode ser aplicada à subexpressão atual."
    assert seguinte.estado == resposta.estado and seguinte.eventos == []


def test_transformacao_recusada_volta_ao_estado_anterior(monkeypatch):
    # Com as 9 leis, toda transformação que passa na verificação reduz a
    # complexidade; o ramo de recusa é exercitado simulando a falha.
    from BackEnd import simplificador_interativo as simpli
    resposta = sessao.iniciar("(A&1)|C")
    monkeypatch.setattr(simpli, "aplicar_lei_e_substituir", lambda arvore, passo, indice: (arvore, False))
    seguinte = sessao.aplicar_lei(resposta.estado, IDENTIDADE)
    assert seguinte.mensagem == "Esta transformação não reduz a expressão atual."
    assert metodos(seguinte) == ["log_law_applied", "log_simplification_step_failed"]
    assert seguinte.eventos[0]["argumentos"] == ["Identidade (A * 1 = A)", False, 1]
    assert seguinte.visao["expressao"] == resposta.visao["expressao"]
    assert seguinte.visao["subexpressao"] == "(A*1)" and not seguinte.visao["pode_desfazer"]


def test_pular_e_desfazer():
    resposta = sessao.iniciar("(A&1)|(B&1)")
    primeira = resposta.visao["subexpressao"]
    pulou = sessao.pular(resposta.estado)
    assert pulou.visao["subexpressao"] != primeira
    assert pulou.visao["historico"][-1] == {"tipo": "pulo", "subexpressao": primeira}
    assert pulou.visao["pode_desfazer"]
    voltou = sessao.desfazer(pulou.estado)
    assert voltou.visao["subexpressao"] == primeira and not voltou.visao["pode_desfazer"]
    assert metodos(voltou) == ["log_simplification_undo"]


def test_ignorado_por_caminho_nao_ignora_o_gemeo():
    resposta = sessao.pular(sessao.iniciar("(A*B)+(A*B)").estado)
    # o primeiro (A*B) foi pulado; o segundo, estruturalmente igual, continua disponível
    assert resposta.visao["subexpressao"] == "(A*B)"
    assert resposta.estado["ignorados"] == [[0]] and resposta.estado["passo_atual"] == [1]


def test_estado_invalido():
    with pytest.raises(EstadoInvalido):
        sessao.aplicar_lei({"versao": 99}, 0)
    estado = sessao.iniciar("A&1").estado
    with pytest.raises(EstadoInvalido):
        sessao.pular({**estado, "ignorados": [[5, 5]]})
    with pytest.raises(EstadoInvalido):
        sessao.aplicar_lei(estado, 42)


def test_aceita_implicacao_convertendo_como_o_desktop():
    assert sessao.iniciar("A>B").visao["expressao"] == "(~A+B)"
