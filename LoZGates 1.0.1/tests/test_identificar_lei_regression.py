from BackEnd.core.expression_ast import OperatorNode, VariableNode
from BackEnd.identificar_lei import demorgan, nula, construir_arvore

def test_demorgan_retorna_tipos_canonicos():
    arvore = construir_arvore("!(A&B)")
    resultado = demorgan(arvore)
    assert isinstance(resultado, OperatorNode)
    assert resultado.op == '|'
    assert isinstance(resultado.children[0], OperatorNode)  # !A
    assert resultado.children[0].op == '!'

def test_nula_retorna_variablenode():
    arvore = construir_arvore("A&0")
    resultado = nula(arvore)
    assert isinstance(resultado, VariableNode)
    assert resultado.name == '0'