"""
Cálculo do layout do circuito a partir da AST.

O parsing é 100% delegado ao parser canônico (BackEnd.core.expression_ast):
este arquivo não tem parser nem classes de nó próprias. Os nomes antigos
continuam disponíveis para os chamadores: criar_ast_de_expressao é o próprio
parse canônico e _coletar_variaveis é o próprio collect_variables.
"""

from BackEnd.core.expression_ast import (
    AND,
    NOT,
    OR,
    OperatorNode,
    VariableNode,
    collect_variables,
    parse,
)

criar_ast_de_expressao = parse
_coletar_variaveis = collect_variables


def calcular_layout_dinamico(node, y_base=0):
    if isinstance(node, VariableNode):
        if node.eh_constante:
            # Constante 0/1: entrada fixa, sem barramento negado
            return {
                'type': 'constant',
                'name': node.name,
                'y_pos': y_base,
                'height': 80,
                'width': 0
            }
        return {
            'type': 'variable',
            'name': node.name,
            'y_pos': y_base,
            'height': 80,
            'width': 0
        }

    if (isinstance(node, OperatorNode) and node.op == NOT
            and isinstance(node.children[0], VariableNode) and not node.children[0].eh_constante):
        return {
            'type': 'negated_variable',
            'name': node.children[0].name,
            'y_pos': y_base,
            'height': 80,
            'width': 0
        }

    if isinstance(node, OperatorNode):
        child_layouts = []
        current_y = y_base
        max_width = 0

        for child in node.children:
            child_layout = calcular_layout_dinamico(child, current_y)
            child_layouts.append(child_layout)
            current_y += child_layout['height'] + 20
            max_width = max(max_width, child_layout.get('width', 0))

        total_height = current_y - y_base - 20
        return {
            'type': 'gate',
            'op': node.op,
            'y_pos': y_base + total_height / 2,
            'height': total_height,
            'width': max_width + 180,
            'children': child_layouts
        }

    return {}


def _coletar_operadores(node, operators=None):
    """Conta as portas AND, OR e NOT da árvore (símbolos canônicos & | !)."""
    if operators is None:
        operators = {AND: 0, OR: 0, NOT: 0}

    if isinstance(node, OperatorNode):
        if node.op in operators:
            operators[node.op] += 1
        for child in node.children:
            _coletar_operadores(child, operators)

    return operators
