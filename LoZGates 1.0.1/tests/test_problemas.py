"""Banco de problemas: dados válidos e regra de correção (BackEnd/problemas.py)."""
import pytest

from BackEnd.core.expression_ast import parse
from BackEnd.problemas import (
    MENSAGEM_CORRETA,
    MENSAGEM_CORRETA_ESTRUTURAL,
    MENSAGEM_INCORRETA,
    MENSAGEM_VAZIA,
    listar_problemas,
    obter_problema,
    verificar_resposta,
    verificar_resposta_do_problema,
)
from BackEnd.problems_bank import Problems_bank


@pytest.mark.parametrize("problema", Problems_bank, ids=lambda p: p.name)
def test_toda_resposta_do_banco_e_uma_expressao_valida(problema):
    parse(problema.answer)  # uma resposta inválida tornaria o problema impossível de acertar


def test_lista_e_detalhe():
    lista = listar_problemas()
    assert len(lista) == len(Problems_bank)
    assert lista[0] == {"indice": 0, "nome": "Airbags", "dificuldade": "Fácil"}
    detalhe = obter_problema(0)
    assert detalhe["resposta"] == "(V & P & I)"
    assert detalhe["pergunta"].startswith("Larissa é um engenheiro")
    with pytest.raises(IndexError):
        obter_problema(len(Problems_bank))


@pytest.mark.parametrize("resposta, correta, esperado, mensagem", [
    ("V&P&I", "(V & P & I)", True, MENSAGEM_CORRETA),
    ("i & p & v", "(V & P & I)", True, MENSAGEM_CORRETA),
    ("A>B", "P>Q", True, MENSAGEM_CORRETA_ESTRUTURAL),
    ("A|B", "P&Q", False, MENSAGEM_INCORRETA),
    ("   ", "P&Q", False, MENSAGEM_VAZIA),
])
def test_regra_de_correcao(resposta, correta, esperado, mensagem):
    correcao = verificar_resposta(resposta, correta)
    assert (correcao.correta, correcao.mensagem) == (esperado, mensagem)


def test_resposta_invalida_explica_o_erro():
    correcao = verificar_resposta("AB", "A&B")
    assert correcao.tipo == "invalida"
    assert "Falta um operador" in correcao.mensagem


def test_problema_que_tinha_resposta_malformada_agora_tem_solucao():
    indice = next(i for i, p in enumerate(Problems_bank) if "(!S|E)" in p.answer)
    assert verificar_resposta_do_problema(indice, "(X&P&R&(!S|E))&(M>!D)").correta
