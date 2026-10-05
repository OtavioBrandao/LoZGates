"""
Paridade de ponta a ponta: o corpus passa pelos endpoints HTTP da API nova e o
resultado é comparado com o interface_update original (oráculo). Só as
diferenças de diferencas_aprovadas.py são aceitas.
"""
import pytest

from tests.paridade import corpus, diferencas_aprovadas, oraculo

antigo_tabela = oraculo.modulo("BackEnd.tabela")
antigo_equivalencia = oraculo.modulo("BackEnd.equivalencia")
antigo_conversor = oraculo.modulo("BackEnd.converter")
antigo_validar_resposta = oraculo.validar_resposta_problema()


@pytest.mark.parametrize("expr", corpus.TODAS)
def test_converter_e_tabela_via_api(cliente, expr):
    conversao = cliente.post("/api/expressao/converter", json={"expressao": expr}).json()
    if not diferencas_aprovadas.mesma_arvore(conversao["expressao_booleana"], antigo_conversor.converter_para_algebra_booleana(expr)):
        assert diferencas_aprovadas.tem_implicacao(expr)  # D3b; sem implicação, só os parênteses podem mudar (D3e)

    tabela = cliente.post("/api/expressao/tabela-verdade", json={"expressao": expr}).json()
    antiga = antigo_tabela.gerar_tabela_verdade(expr)
    assert tabela["resultados_finais"] == antiga["resultados_finais"]
    assert sorted(tabela["colunas"]) == sorted(antiga["colunas"])
    assert tabela["conclusao"] == antigo_tabela.verificar_conclusao(antiga["resultados_finais"])


def pares_pequenos():
    from BackEnd.core.expression_ast import collect_variables, parse
    for expr1, expr2 in zip(corpus.TODAS, corpus.TODAS[1:] + corpus.TODAS[:1]):
        # o motor antigo reavalia o texto a cada linha: pares grandes só deixariam o teste lento
        if len(collect_variables(parse(expr1)) | collect_variables(parse(expr2))) <= 10:
            yield expr1, expr2


@pytest.mark.parametrize("expr1, expr2", list(pares_pequenos()))
def test_equivalencia_via_api(cliente, expr1, expr2):
    dados = cliente.post("/api/equivalencia", json={"expressao1": expr1, "expressao2": expr2}).json()
    assert dados["equivalentes"] == antigo_equivalencia.check_universal_equivalence(expr1, expr2)


@pytest.mark.parametrize("indice", range(len(corpus.Problems_bank)))
def test_correcao_de_problemas_via_api(cliente, indice):
    correta = corpus.Problems_bank[indice].answer
    for resposta in (correta, correta.lower(), "!(" + correta + ")"):
        dados = cliente.post(f"/api/problemas/{indice}/verificar", json={"resposta": resposta}).json()
        assert (dados["correta"], dados["mensagem"]) == antigo_validar_resposta(resposta, correta)
