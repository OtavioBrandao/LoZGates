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
