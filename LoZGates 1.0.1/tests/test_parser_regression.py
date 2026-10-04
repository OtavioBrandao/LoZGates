import pytest
from BackEnd.core.expression_ast import parse, to_string, avaliar, collect_variables

CASOS = [
    "A&B", "A|B", "!A", "A&B|C", "(A|B)&C",
    "A>B", "!(A&B)", "A<>B",
    "(A&B)|(!C&D)", "((A&B)|C)>(D<>E)",
]

@pytest.mark.parametrize("expr", CASOS)
def test_parse_e_reimpressao_estavel(expr):
    arvore = parse(expr)
    # reparsear a string impressa deve dar a mesma árvore
    reparsed = parse(to_string(arvore, style="logic"))
    assert arvore == reparsed

@pytest.mark.parametrize("expr", CASOS)
def test_avaliacao_bate_com_motor_antigo(expr):
    from BackEnd.equivalencia import UniversalLogicAnalyzer
    analyzer = UniversalLogicAnalyzer()
    arvore = parse(expr)
    variaveis = sorted(collect_variables(arvore))
    from itertools import product
    for combo in product([False, True], repeat=len(variaveis)):
        valores = dict(zip(variaveis, combo))
        esperado = analyzer.analyze_expression(expr, valores)
        obtido = avaliar(arvore, valores)
        assert esperado == obtido, f"Divergência em {expr} com {valores}"