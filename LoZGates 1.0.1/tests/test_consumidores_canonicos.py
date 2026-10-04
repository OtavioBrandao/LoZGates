"""
Cada módulo que interpreta expressões precisa usar o parser canônico.

Os testes importam DO CONSUMIDOR (e não só de expression_ast), para não se
repetir o problema da suíte "20/20" que passava sem que os arquivos
migrados fossem exercitados. Para cada consumidor, verificam que:
  - o `parse` que ele usa é o objeto canônico (`is`);
  - os nós que ele produz são OperatorNode/VariableNode canônicos;
  - o código-fonte dele não define classe *Node nem funções de parser.
"""
import ast
import importlib
import inspect

import pytest

from BackEnd.core import expression_ast
from BackEnd.core.expression_ast import OperatorNode, VariableNode

# Nomes que só um parser próprio teria (tokenizador, descida recursiva etc.)
NOMES_DE_PARSER = {
    "tokenize", "tokenizar", "parse_or", "parse_and", "parse_not", "parse_atom",
    "parse_factor", "parse_term", "parse_expression", "parse_iff", "parse_implies",
    "parse_implication", "parse_bi_implication", "construir_arvore_or",
    "construir_arvore_and", "construir_arvore_not", "find_left_operand",
    "find_right_operand", "process_parentheses", "process_negation", "process_operator",
}


def definicoes_no_codigo(nome_modulo):
    modulo = importlib.import_module(nome_modulo)
    arvore = ast.parse(inspect.getsource(modulo))
    classes = {n.name for n in ast.walk(arvore) if isinstance(n, ast.ClassDef)}
    funcoes = {n.name for n in ast.walk(arvore) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return classes, funcoes


def assert_sem_parser_proprio(nome_modulo):
    classes, funcoes = definicoes_no_codigo(nome_modulo)
    assert not [c for c in classes if c.endswith("Node")], f"{nome_modulo} define classe de nó própria"
    assert not (funcoes & NOMES_DE_PARSER), f"{nome_modulo} define funções de parser: {funcoes & NOMES_DE_PARSER}"


def assert_arvore_canonica(no):
    assert isinstance(no, (OperatorNode, VariableNode)), type(no)
    if isinstance(no, OperatorNode):
        for filho in no.children:
            assert_arvore_canonica(filho)


# ------------------------------ circuito_logico.logic.parser ------------------------------

class TestParserDoCircuito:
    modulo = "BackEnd.circuito_logico.logic.parser"

    def test_usa_o_parse_canonico(self):
        from BackEnd.circuito_logico.logic import parser
        assert parser.parse is expression_ast.parse
        assert parser.criar_ast_de_expressao is expression_ast.parse
        assert parser._coletar_variaveis is expression_ast.collect_variables

    def test_produz_nos_canonicos(self):
        from BackEnd.circuito_logico.logic.parser import criar_ast_de_expressao
        assert_arvore_canonica(criar_ast_de_expressao("(A*B)+~(C+~A)"))

    def test_sem_parser_nem_nos_proprios(self):
        assert_sem_parser_proprio(self.modulo)
        with pytest.raises(ImportError):
            importlib.import_module("BackEnd.circuito_logico.core.nodes")

    def test_layout_aceita_constantes_e_rejeita_sobras(self):
        from BackEnd.circuito_logico.logic.parser import calcular_layout_dinamico, criar_ast_de_expressao
        layout = calcular_layout_dinamico(criar_ast_de_expressao("A*1"))
        assert [filho['type'] for filho in layout['children']] == ['variable', 'constant']
        with pytest.raises(ValueError):
            criar_ast_de_expressao("A*B)")


# ------------------------------ identificar_lei ------------------------------

class TestIdentificarLei:
    modulo = "BackEnd.identificar_lei"

    def test_usa_o_parse_canonico(self):
        from BackEnd import identificar_lei
        assert identificar_lei.parse is expression_ast.parse
        assert identificar_lei.construir_arvore is expression_ast.parse

    def test_leis_produzem_nos_canonicos(self):
        from BackEnd import identificar_lei as il
        casos = [
            (il.demorgan, "!(A&B)"), (il.identidade, "A&1"), (il.nula, "A|1"),
            (il.idempotente, "B&B"), (il.inversa, "A&!A"), (il.absorcao, "A&(A|B)"),
            (il.associativa, "(A&B)&C"), (il.comutativa, "B|A"), (il.distributiva, "(A|B)&(A|C)"),
        ]
        for lei, expr in casos:
            assert_arvore_canonica(lei(il.construir_arvore(expr)))

    def test_simplificacao_produz_nos_canonicos(self):
        from BackEnd.identificar_lei import construir_arvore, simplificar
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            assert_arvore_canonica(simplificar(construir_arvore("(A&B)|(A&!B)")))

    def test_sem_parser_nem_nos_proprios_nem_troca_de_stdout(self):
        from BackEnd import identificar_lei
        assert_sem_parser_proprio(self.modulo)
        # redirect_stdout troca o sys.stdout do processo inteiro: inseguro num servidor com threads
        assert "redirect_stdout" not in inspect.getsource(identificar_lei)


# ------------------------------ simplificador_interativo ------------------------------

class TestSimplificadorInterativo:
    modulo = "BackEnd.simplificador_interativo"

    def test_usa_o_parse_canonico(self):
        from BackEnd import simplificador_interativo as si
        assert si.parse is expression_ast.parse
        assert si.construir_arvore is expression_ast.parse

    def test_todas_as_leis_produzem_nos_canonicos(self):
        from BackEnd import simplificador_interativo as si
        exemplos = ["A*~A", "A*0", "A*1", "A*A", "A*(A+B)", "~(A*B)", "(A*B)+(A*C)", "(A*B)*C", "B+A"]
        for lei, expr in zip(si.LEIS_LOGICAS, exemplos):
            arvore = si.construir_arvore(expr)
            assert lei["verifica"](arvore), lei["nome"]
            assert_arvore_canonica(lei["aplica"](arvore))

    def test_sem_parser_nem_nos_proprios(self):
        assert_sem_parser_proprio(self.modulo)

    def test_sem_estado_global_mutavel(self):
        from BackEnd import simplificador_interativo as si
        for nome in ("_todos_os_nos_ordenados", "_indice_no_atual", "_chave_busca_atual", "passar_pro_front"):
            assert not hasattr(si, nome), nome

    def test_ignorar_usa_identidade_e_nao_estrutura(self):
        from BackEnd import simplificador_interativo as si
        arvore = si.construir_arvore("(A*B)+(A*B)")
        primeiro = si.encontrar_proximo_passo(arvore)["no_atual"]
        gemeo = arvore.direita if primeiro is arvore.esquerda else arvore.esquerda
        assert primeiro == gemeo and primeiro is not gemeo
        proximo = si.encontrar_proximo_passo(arvore, nos_a_ignorar={id(primeiro)})["no_atual"]
        assert proximo is gemeo  # o gêmeo estruturalmente igual NÃO foi ignorado junto

    def test_desempate_entre_candidatas_do_mesmo_tamanho_pelo_texto(self):
        from BackEnd import simplificador_interativo as si
        # Mesmo tamanho (3 nós): vence o menor texto booleano, "(A*B)" < "(A+B)"
        arvore = si.construir_arvore("(A+B)+(A*B)")
        assert si.formatar(si.encontrar_proximo_passo(arvore)["no_atual"]) == "(A*B)"


# ------------------------------ equivalencia ------------------------------

class TestEquivalencia:
    modulo = "BackEnd.equivalencia"

    def test_usa_o_parse_canonico(self):
        from BackEnd import equivalencia
        assert equivalencia.parse is expression_ast.parse
        assert equivalencia.avaliar is expression_ast.avaliar

    def test_sem_parser_nem_avaliador_proprios(self):
        from BackEnd.equivalencia import UniversalLogicAnalyzer
        assert_sem_parser_proprio(self.modulo)
        for metodo in ("tokenize", "evaluate_expression", "evaluate_token"):
            assert not hasattr(UniversalLogicAnalyzer, metodo), metodo

    def test_equivalencia_so_por_tabela_verdade(self):
        from BackEnd.equivalencia import check_universal_equivalence, comparar_expressoes
        assert check_universal_equivalence("A&B", "B&A")
        # Sem renomear variáveis: A&B e X&Y NÃO são equivalentes (decisão D3d)
        assert not check_universal_equivalence("A&B", "X&Y")
        resultado = comparar_expressoes("P>Q", "Q>P")
        assert not resultado.equivalentes
        assert resultado.contraexemplo == {"P": False, "Q": True}
        assert (resultado.valor_1, resultado.valor_2) == (True, False)

    def test_entrada_invalida(self):
        from BackEnd.core.expression_ast import ExpressaoInvalida
        from BackEnd.equivalencia import check_universal_equivalence, comparar_expressoes
        assert check_universal_equivalence("A&", "A") is False
        with pytest.raises(ExpressaoInvalida):
            comparar_expressoes("A&", "A")


# ------------------------------ normalizer ------------------------------

class TestNormalizer:
    modulo = "BackEnd.normalizer"

    def test_usa_o_parse_canonico(self):
        from BackEnd import normalizer
        assert normalizer.parse is expression_ast.parse

    def test_sem_parser_nem_nos_proprios(self):
        from BackEnd import normalizer
        assert_sem_parser_proprio(self.modulo)
        assert not hasattr(normalizer, "ExprNode")
        assert not hasattr(normalizer, "build_expression_tree")

    def test_renomeacao_produz_nos_canonicos(self):
        from BackEnd.normalizer import normalize_tree_variables
        renomeada = normalize_tree_variables(expression_ast.parse("(X>Y)&!Z|1"))
        assert_arvore_canonica(renomeada)
        assert expression_ast.collect_variables(renomeada) == {"A", "B", "C"}

    @pytest.mark.parametrize("entrada, esperado", [
        ("(A&B)&C", "A&B&C"),
        ("A&(B&C)", "A&B&C"),
        ("(A>B)|C", "(A>B)|C"),
        ("X&Y", "A&B"),
        ("(P>Q)>R", "(A>B)>C"),
        ("P>(Q>R)", "A>B>C"),
        ("P>Q>R", "A>B>C"),
        ("!(P|Q)", "!(A|B)"),
        ("Q&P&1", "A&B&1"),
    ])
    def test_forma_normalizada(self, entrada, esperado):
        from BackEnd.normalizer import normalize_for_comparison
        assert normalize_for_comparison(entrada) == esperado

    @pytest.mark.parametrize("expr", [
        "(A>B)>C", "A>(B>C)", "A>B>C", "(A<>B)<>C", "A<>(B>C)", "!(A>B)|C&D",
        "(A|B)>(C&!D)", "A>(B|C)>D", "((A>B)>C)>D",
    ])
    def test_texto_normalizado_relido_tem_o_mesmo_significado(self, expr):
        import itertools
        from BackEnd.normalizer import normalize_tree_variables, tree_to_canonical_string
        normalizada = normalize_tree_variables(expression_ast.parse(expr))
        relida = expression_ast.parse(tree_to_canonical_string(normalizada))
        variaveis = sorted(expression_ast.collect_variables(normalizada))
        for combo in itertools.product([False, True], repeat=len(variaveis)):
            valores = dict(zip(variaveis, combo))
            assert expression_ast.avaliar(relida, valores) == expression_ast.avaliar(normalizada, valores)

    def test_estrutura_igual_com_variaveis_diferentes(self):
        from BackEnd.normalizer import expressions_are_structurally_equivalent
        assert expressions_are_structurally_equivalent("X&Y", "P&Q")
        assert expressions_are_structurally_equivalent("A&B&C", "(A&B)&C")
        assert not expressions_are_structurally_equivalent("(A>B)|C", "A>(B|C)")

    def test_entrada_invalida_usa_normalizacao_simples(self):
        from BackEnd.normalizer import normalize_for_comparison
        assert normalize_for_comparison("x y z &") == "ABC&"


# ------------------------------ converter ------------------------------

def gerar_expressoes(quantidade, semente=2026):
    """Expressões aleatórias (determinísticas) com todos os operadores e parênteses."""
    import random
    sorteio = random.Random(semente)

    def gerar(profundidade):
        if profundidade == 0 or sorteio.random() < 0.25:
            return sorteio.choice("ABC01")
        escolha = sorteio.random()
        if escolha < 0.15:
            return "!" + gerar(profundidade - 1)
        if escolha < 0.3:
            return "(" + gerar(profundidade - 1) + ")"
        return gerar(profundidade - 1) + sorteio.choice(["&", "|", ">", "<>", "*", "+", "->"]) + gerar(profundidade - 1)

    return [gerar(4) for _ in range(quantidade)]


class TestConversor:
    modulo = "BackEnd.converter"

    def test_usa_o_parse_canonico(self):
        from BackEnd import converter
        assert converter.parse is expression_ast.parse

    def test_sem_parser_proprio(self):
        assert_sem_parser_proprio(self.modulo)

    @pytest.mark.parametrize("entrada, esperado", [
        ("A>B", "(~A+B)"),
        ("A -> B", "(~A+B)"),
        ("!A | B", "~A+B"),
        ("A & B", "A*B"),
        ("A <-> B", "((~A+B)*(~B+A))"),
        ("(A>B)>C", "(~((~A+B))+C)"),
        ("!(A>B)", "~((~A+B))"),
        ("!A>B", "(~~A+B)"),
        ("(A&B)|C", "(A*B)+C"),
        ("(A>B)&C", "((~A+B))*C"),
    ])
    def test_saida_identica_a_antiga_onde_ela_estava_certa(self, entrada, esperado):
        from BackEnd.converter import converter_para_algebra_booleana
        assert converter_para_algebra_booleana(entrada) == esperado

    @pytest.mark.parametrize("entrada, esperado", [
        ("A&B>C", "(~(A*B)+C)"),          # antes: A*(~B+C)
        ("A|B>C", "(~(A+B)+C)"),          # antes: A+(~B+C)
        ("A>B&C", "(~A+B*C)"),            # antes: (~A+B)*C
        ("A&B<>C", "((~(A*B)+C)*(~C+A*B))"),
        ("A>B>C", "(~A+(~B+C))"),         # implicação associa à direita
    ])
    def test_casos_que_mudavam_o_significado(self, entrada, esperado):
        from BackEnd.converter import converter_para_algebra_booleana
        from BackEnd.equivalencia import check_universal_equivalence
        convertida = converter_para_algebra_booleana(entrada)
        assert convertida == esperado
        assert check_universal_equivalence(entrada, convertida)

    def test_conversao_nunca_muda_o_significado(self):
        from BackEnd.converter import converter_para_algebra_booleana
        from BackEnd.equivalencia import comparar_expressoes
        for expr in gerar_expressoes(400):
            convertida = converter_para_algebra_booleana(expr)
            assert not set(convertida) & set("&|!><"), (expr, convertida)
            assert comparar_expressoes(expr, convertida).equivalentes, (expr, convertida)

    def test_entrada_invalida(self):
        from BackEnd.converter import Conversorlogical, converter_para_algebra_booleana
        with pytest.raises(expression_ast.ExpressaoInvalida):
            converter_para_algebra_booleana("A&")
        lote = Conversorlogical().convert_batch(["A & B", "(A | B"])
        assert lote["A & B"] == "A*B"
        assert lote["(A | B"].startswith("ERRO:")
