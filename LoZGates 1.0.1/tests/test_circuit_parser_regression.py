import pytest
from BackEnd.core.expression_ast import VariableNode, OperatorNode
from BackEnd.circuito_logico.logic.parser import (
    criar_ast_de_expressao,
    _coletar_variaveis,
    calcular_layout_dinamico,
)

def test_usa_classes_canonicas_nao_as_antigas():
    arvore = criar_ast_de_expressao("A*B")
    assert isinstance(arvore, OperatorNode)
    assert isinstance(arvore.children[0], VariableNode)

def test_aceita_ambos_estilos_de_simbolo_com_o_mesmo_resultado():
    arvore_bool = criar_ast_de_expressao("A*B+~C")
    arvore_logic = criar_ast_de_expressao("A&B|!C")
    assert arvore_bool == arvore_logic

def test_layout_reconhece_negacao_no_operador_canonico():
    arvore = criar_ast_de_expressao("~A")
    layout = calcular_layout_dinamico(arvore)
    assert layout['type'] == 'negated_variable'
    assert layout['name'] == 'A'

def test_coletar_variaveis():
    arvore = criar_ast_de_expressao("A*B+C")
    assert _coletar_variaveis(arvore) == {'A', 'B', 'C'}