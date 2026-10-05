"""Contrato do parser canônico (BackEnd/core/expression_ast.py)."""
import copy
import itertools

import pytest

from BackEnd.core.expression_ast import (
    ExpressaoInvalida,
    OperatorNode,
    VariableNode,
    avaliar,
    caminho_ate,
    collect_variables,
    no_no_caminho,
    parse,
    percorrer,
    to_string,
    to_string_com_trechos,
    to_string_minimo,
    to_string_minimo_com_trechos,
    tree_size,
)


def tabela(expr):
    arvore = parse(expr)
    variaveis = sorted(collect_variables(arvore))
    return [
        int(avaliar(arvore, dict(zip(variaveis, combo))))
        for combo in itertools.product([False, True], repeat=len(variaveis))
    ]


@pytest.mark.parametrize("entrada, esperado", [
    ("A&B|C", "((A&B)|C)"),
    ("A|B&C", "(A|(B&C))"),
    ("!A&B", "(!A&B)"),
    ("!(A&B)", "!(A&B)"),
    ("A>B|C", "(A>(B|C))"),
    ("A|B>C", "((A|B)>C)"),
    ("A<>B>C", "(A<>(B>C))"),
    ("!!A", "!!A"),
])
def test_precedencia(entrada, esperado):
    assert to_string(parse(entrada)) == esperado


def test_implicacao_associa_a_direita():
    assert parse("A>B>C") == parse("A>(B>C)")
    assert parse("A>B>C") != parse("(A>B)>C")
    assert tabela("A>B>C") == tabela("A>(B>C)") == [1, 1, 1, 1, 1, 1, 0, 1]


def test_demais_binarios_associam_a_esquerda():
    assert parse("A&B&C") == parse("(A&B)&C")
    assert parse("A|B|C") == parse("(A|B)|C")
    assert parse("A<>B<>C") == parse("(A<>B)<>C")


def test_sinonimos_e_espacos_produzem_a_mesma_arvore():
    assert parse("A*B+~C") == parse("A & B | !C")
    assert parse("A->B") == parse("A>B")
    assert parse("A<->B") == parse("A<>B")


def test_minusculas_viram_maiusculas():
    assert parse("a&b") == parse("A&B")
    assert collect_variables(parse("p>q")) == {"P", "Q"}


def test_constantes_nao_sao_variaveis():
    assert collect_variables(parse("A&1|0")) == {"A"}
    assert avaliar(parse("1"), {}) is True
    assert avaliar(parse("A&0"), {"A": True}) is False


@pytest.mark.parametrize("entrada, trecho_da_mensagem, posicao", [
    ("", "vazia", 0),
    ("   ", "vazia", 0),
    ("AB", "Falta um operador entre 'A' e 'B'", 1),
    ("A1", "Falta um operador entre 'A' e '1'", 1),
    ("A2", "só as constantes 0 e 1", 1),
    ("A=B", "Caractere inválido '='", 1),
    ("A<B", "use '<>'", 1),
    ("A-B", "use '>'", 1),
    ("(A&B", "não foi fechado", 0),
    ("A&B)", "sem abertura", 3),
    ("()", "Parênteses vazios", 0),
    ("A&", "termina sem", 2),
    ("&A", "Falta um operando antes de '&'", 0),
    ("A&&B", "Falta um operando antes de '&'", 2),
    ("(A|)", "Falta um operando antes de ')'", 3),
    ("A_B", "Caractere inválido '_'", 1),
    ("é", "sem acento", 0),
])
def test_erros_tem_mensagem_e_posicao(entrada, trecho_da_mensagem, posicao):
    with pytest.raises(ExpressaoInvalida) as erro:
        parse(entrada)
    assert trecho_da_mensagem in str(erro.value)
    assert erro.value.posicao == posicao
    assert isinstance(erro.value, ValueError)


def test_entrada_que_nao_e_texto():
    with pytest.raises(TypeError):
        parse(None)


def test_aninhamento_extremo_vira_erro_claro():
    with pytest.raises(ExpressaoInvalida):
        parse("(" * 2000 + "A" + ")" * 2000)


def test_nos_nao_sao_hasheaveis_regra_4():
    arvore = parse("(A&B)|(A&B)")
    esquerda, direita = arvore.children
    assert esquerda == direita and esquerda is not direita
    with pytest.raises(TypeError):
        {esquerda}
    ignorados = {id(esquerda)}
    assert id(direita) not in ignorados


def test_parenteses_do_usuario_sao_registrados_sem_afetar_igualdade():
    fonte = "((A&B))|C"
    arvore = parse(fonte)
    conjuncao = arvore.children[0]
    assert [fonte[a:b] for a, b in conjuncao.parenteses] == ["((A&B))", "(A&B)"]
    assert arvore.children[1].parenteses == ()
    assert arvore == parse("A&B|C")


def test_copia_profunda_preserva_estrutura_e_metadados():
    arvore = parse("(A>B)&!C")
    copia = copy.deepcopy(arvore)
    assert copia == arvore and copia is not arvore
    assert copia.children[0].parenteses == arvore.children[0].parenteses


def test_reimpressao_estavel_nos_dois_estilos():
    for expr in ["A&B|!C", "(A>B)<>C", "!(A|B)&1"]:
        arvore = parse(expr)
        assert parse(to_string(arvore, style="logic")) == arvore
        assert parse(to_string(arvore, style="boolean")) == arvore
    assert to_string(parse("A&B|!C"), style="boolean") == "((A*B)+~C)"


@pytest.mark.parametrize("entrada, minimo", [
    ("((A))", "A"),
    ("(A&B)&C", "A&B&C"),
    ("A&(B&C)", "A&(B&C)"),        # sem os parênteses seria (A&B)&C: outra árvore
    ("A|(B&C)", "A|B&C"),
    ("(A|B)&C", "(A|B)&C"),
    ("!(A&B)", "!(A&B)"),
    ("!(!A)", "!!A"),
    ("(!A)&B", "!A&B"),
    ("A>(B>C)", "A>B>C"),          # a implicação associa à direita
    ("(A>B)>C", "(A>B)>C"),
    ("(A<>B)<>C", "A<>B<>C"),      # a bi-implicação, à esquerda
    ("A<>(B<>C)", "A<>(B<>C)"),
    ("(A>B)<>C", "A>B<>C"),
    ("A<>(B>C)", "A<>B>C"),
    ("(A<>B)>C", "(A<>B)>C"),
    ("A>(B<>C)", "A>(B<>C)"),
    ("(A|B)>(C&D)", "A|B>C&D"),
    ("!(A>B)", "!(A>B)"),
    ("(A&1)|(0)", "A&1|0"),
])
def test_impressao_minima(entrada, minimo):
    arvore = parse(entrada)
    assert to_string_minimo(arvore) == minimo
    assert parse(minimo) == arvore


def test_impressao_minima_rele_a_mesma_arvore_em_todo_o_corpus():
    from tests.paridade import corpus
    for expr in corpus.TODAS:
        arvore = parse(expr)
        for estilo in ("logic", "boolean"):
            texto = to_string_minimo(arvore, style=estilo)
            assert parse(texto) == arvore, (expr, texto)
            assert len(texto) <= len(to_string(arvore, style=estilo))
            assert to_string_minimo(parse(texto), style=estilo) == texto  # já não sobra nada para tirar


def test_trechos_da_impressao_minima():
    arvore = parse("!(A&B)|C")
    texto, trechos = to_string_minimo_com_trechos(arvore, style="boolean")
    assert texto == "~(A*B)+C"
    negacao, c = arvore.children
    conjuncao = negacao.children[0]
    assert trechos[id(arvore)] == (0, len(texto))
    assert texto[slice(*trechos[id(negacao)])] == "~(A*B)"
    assert texto[slice(*trechos[id(conjuncao)])] == "A*B"  # sem os parênteses que o pai pôs
    assert texto[slice(*trechos[id(c)])] == "C"


def test_cada_trecho_minimo_rele_o_proprio_no_em_todo_o_corpus():
    from tests.paridade import corpus
    for expr in corpus.TODAS:
        arvore = parse(expr)
        texto, trechos = to_string_minimo_com_trechos(arvore, style="boolean")
        assert texto == to_string_minimo(arvore, style="boolean")
        for _, no in percorrer(arvore):
            assert parse(texto[slice(*trechos[id(no)])]) == no, (expr, texto, trechos[id(no)])


def test_trechos_apontam_cada_no_no_texto_impresso():
    arvore = parse("A&(B|C)")
    texto, trechos = to_string_com_trechos(arvore, style="boolean")
    assert texto == "(A*(B+C))"
    disjuncao = arvore.children[1]
    inicio, fim = trechos[id(disjuncao)]
    assert texto[inicio:fim] == "(B+C)"
    assert trechos[id(arvore)] == (0, len(texto))


def test_caminhos_por_identidade():
    arvore = parse("(A&B)|(A&B)")
    direita = arvore.children[1]
    assert caminho_ate(arvore, direita) == (1,)
    assert no_no_caminho(arvore, (1, 0)) is direita.children[0]
    assert [c for c, _ in percorrer(arvore)] == [(), (0,), (0, 0), (0, 1), (1,), (1, 0), (1, 1)]
    with pytest.raises(ValueError):
        no_no_caminho(arvore, (0, 0, 0))


def test_tamanho_da_arvore():
    assert tree_size(parse("A")) == 1
    assert tree_size(parse("!A&B")) == 4


def test_tipos_canonicos():
    arvore = parse("!A&B")
    assert isinstance(arvore, OperatorNode)
    assert isinstance(arvore.esquerda, OperatorNode) and arvore.esquerda.valor == '!'
    assert isinstance(arvore.direita, VariableNode) and arvore.direita.valor == 'B'
