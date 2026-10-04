#Módulo responsável pelo parsing e análise de expressões lógicas booleanas, incluindo criação da AST e cálculo de layouts.

from ..core.nodes import Node, VariableNode, OperatorNode

def criar_ast_de_expressao(expressao):
    tokens = list(expressao.replace(" ", ""))
    pos = 0
    
    def peek():
        return tokens[pos] if pos < len(tokens) else None
    
    def consume():
        nonlocal pos
        pos += 1
        return tokens[pos - 1]
    
    def parse_factor():
        token = peek()
        if token and token.isalpha():
            return VariableNode(consume())
        if token == '~':
            consume()
            if peek() == '(':
                consume()
                expr = parse_expression()
                consume()  # ')'
                return OperatorNode('~', [expr])
            return OperatorNode('~', [parse_factor()])
        if token == '(':
            consume()  # '('
            expr = parse_expression()
            consume()  # ')'
            return expr
        raise ValueError(f"Tenha certeza que os parentêses estão sendo fechados.")
    
    def parse_term():
        node = parse_factor()
        while peek() == '*':
            op = consume()
            right = parse_factor()
            node = OperatorNode(op, [node, right])
        return node
    
    def parse_expression():
        node = parse_term()
        while peek() == '+':
            op = consume()
            right = parse_term()
            node = OperatorNode(op, [node, right])
        return node
    
    return parse_expression()


def calcular_layout_dinamico(node, y_base=0):
    if isinstance(node, VariableNode):
        return {
            'type': 'variable', 
            'name': node.name, 
            'y_pos': y_base, 
            'height': 80, 
            'width': 0
        }
    
    if isinstance(node, OperatorNode) and node.op == '~' and isinstance(node.children[0], VariableNode):
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


def _coletar_variaveis(node):
    if isinstance(node, VariableNode):
        return {node.name}
    if isinstance(node, OperatorNode):
        return set().union(*[_coletar_variaveis(child) for child in node.children])
    return set()


def _coletar_operadores(node, operators=None):
    if operators is None:
        operators = {'*': 0, '+': 0, '~': 0}
    
    if isinstance(node, OperatorNode):
        operators[node.op] += 1
        for child in node.children:
            _coletar_operadores(child, operators)
    
    return operators