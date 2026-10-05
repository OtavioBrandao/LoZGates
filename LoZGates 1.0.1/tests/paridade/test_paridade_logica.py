"""
Paridade com o interface_update original (oráculo congelado): tabela-verdade,
equivalência, conversão, simplificação automática e correção de problemas.
Toda diferença precisa estar em diferencas_aprovadas.py.
"""
import contextlib
import io
import itertools
import re

import pytest

from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.core.expression_ast import parse, to_string_minimo
from BackEnd.equivalencia import check_universal_equivalence, comparar_expressoes
from BackEnd.identificar_lei import simplificar_expressao
from BackEnd.problemas import verificar_resposta
from BackEnd.problems_bank import Problems_bank
from BackEnd.tabela import gerar_tabela_verdade
from tests.paridade import corpus, diferencas_aprovadas, oraculo

antigo_tabela = oraculo.modulo("BackEnd.tabela")
antigo_equivalencia = oraculo.modulo("BackEnd.equivalencia")
antigo_conversor = oraculo.modulo("BackEnd.converter")
antigo_lei = oraculo.modulo("BackEnd.identificar_lei")
antigo_validar_resposta = oraculo.validar_resposta_problema()


@pytest.mark.parametrize("expr", corpus.TODAS)
def test_tabela_verdade(expr):
    antiga, nova = antigo_tabela.gerar_tabela_verdade(expr), gerar_tabela_verdade(expr)
    variaveis = antiga["total_variaveis"]
    assert nova["colunas"][:variaveis] == antiga["colunas"][:variaveis]
    assert nova["colunas"][-1] == antiga["colunas"][-1]
    # Mesmas colunas; só a ordem entre colunas de mesmo tamanho pode mudar (determinismo)
    assert sorted(nova["colunas"]) == sorted(antiga["colunas"])
    assert [len(c) for c in nova["colunas"]] == [len(c) for c in antiga["colunas"]]
    for linha_antiga, linha_nova in zip(antiga["tabela"], nova["tabela"]):
        assert dict(zip(nova["colunas"], linha_nova)) == dict(zip(antiga["colunas"], linha_antiga))
    assert nova["resultados_finais"] == antiga["resultados_finais"]
    assert nova["total_combinacoes"] == antiga["total_combinacoes"]


PARES = list(itertools.combinations(corpus.CURADAS[:40], 2)) + [
    ("A&B", "X&Y"), ("P>Q", "!P|Q"), ("A>B>C", "A>(B>C)"), ("A>B>C", "(A>B)>C"),
    ("A<>B", "(A&B)|(!A&!B)"), ("A&!A", "0"), ("AB", "A&B"), ("A&", "A"),
]


@pytest.mark.parametrize("expr1, expr2", PARES)
def test_equivalencia(expr1, expr2):
    assert check_universal_equivalence(expr1, expr2) == antigo_equivalencia.check_universal_equivalence(expr1, expr2)


@pytest.mark.parametrize("expr", corpus.TODAS)
def test_conversao_para_algebra_booleana(expr):
    antiga, nova = antigo_conversor.converter_para_algebra_booleana(expr), converter_para_algebra_booleana(expr)
    assert comparar_expressoes(expr, nova).equivalentes, "a conversão nova tem que preservar o significado"
    assert nova == to_string_minimo(parse(nova), style="boolean"), "D3e: a conversão não pode ter parênteses sobrando"
    if not diferencas_aprovadas.mesma_arvore(nova, antiga):
        # D3b: só a conversão de > e <> pode mudar a árvore; o resto difere no máximo em parênteses (D3e)
        assert diferencas_aprovadas.tem_implicacao(expr), f"diferença não aprovada: {antiga!r} -> {nova!r}"


def leis_impressas(saida):
    return re.findall(r"Aplicando (.+?) em '", saida)


@pytest.mark.parametrize("expr", corpus.TODAS)
def test_simplificacao_automatica(expr):
    conversao_antiga = antigo_conversor.converter_para_algebra_booleana(expr)
    nova = simplificar_expressao(expr)
    assert comparar_expressoes(expr, nova.expressao_final).equivalentes
    if not diferencas_aprovadas.mesma_arvore(conversao_antiga, nova.expressao_booleana):
        assert diferencas_aprovadas.tem_implicacao(expr)  # D3b: a entrada da simplificação mudou
        return
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        antiga = antigo_lei.principal_simplificar(conversao_antiga)
    assert antiga is not None, saida.getvalue()
    assert parse(nova.expressao_final) == parse(str(antiga))  # D3f: mesma árvore, só sem parênteses sobrando
    assert [passo.lei for passo in nova.passos] == leis_impressas(saida.getvalue())


def variantes_de_resposta():
    casos = []
    for problema in Problems_bank:
        correta = problema.answer
        casos.append((correta, correta))
        casos.append((correta.lower(), correta))
        casos.append(("!(" + correta + ")", correta))
        letras = sorted(set(c for c in correta if c.isalpha()))
        if len(letras) >= 2:  # mesma estrutura, variáveis trocadas por outras letras
            livres = [c for c in "QRSTUWXYZ" if c not in letras]
            renomeada = correta.translate(str.maketrans(dict(zip(letras, livres))))
            casos.append((renomeada, correta))
    casos += [("A&B", "B&A"), ("P>Q", "!P|Q"), ("A&B", "A|B"), ("X>Y", "P>Q"), ("(P>Q)>R", "A>B>C")]
    return casos


@pytest.mark.parametrize("resposta, correta", variantes_de_resposta())
def test_correcao_de_problemas(resposta, correta):
    antiga = antigo_validar_resposta(resposta, correta)
    nova = verificar_resposta(resposta, correta)
    if (nova.correta, nova.mensagem) != antiga:
        # D3a: "(P>Q)>R" deixou de ser aceita como resposta de "A>B>C"
        assert any(diferencas_aprovadas.tem_implicacao_encadeada_sem_parenteses(e) for e in (resposta, correta))
        return
    assert (nova.correta, nova.mensagem) == antiga


def test_d3a_resposta_com_implicacao_encadeada():
    assert antigo_validar_resposta("(P>Q)>R", "A>B>C")[0] is True   # o caso que o oráculo aceitava
    assert verificar_resposta("(P>Q)>R", "A>B>C").correta is False  # leitura à direita: estruturas diferentes
    assert verificar_resposta("P>(Q>R)", "A>B>C").correta is True


@pytest.mark.parametrize("resposta", ["AB&C", "A&", "(A|B", "A=B"])
def test_resposta_invalida_agora_explica_o_erro(resposta):
    antiga = antigo_validar_resposta(resposta, "A&B&C")
    nova = verificar_resposta(resposta, "A&B&C")
    assert antiga[0] is False and nova.correta is False
    assert nova.tipo == "invalida"  # D3c: antes dizia só "Resposta incorreta"
    assert nova.mensagem.startswith("❌ Expressão inválida:")
