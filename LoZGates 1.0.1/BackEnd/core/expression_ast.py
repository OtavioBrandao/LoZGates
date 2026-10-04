"""
Módulo único de parsing e representação de expressões lógicas.
Substitui os parsers de identificar_lei.py, simplificador_interativo.py,
normalizer.py, circuito_logico/logic/parser.py e o avaliador de
equivalencia.py.
"""
from __future__ import annotations
from typing import List, Optional, Set, Dict

# Operadores canônicos internos
AND, OR, NOT, IMPLIES, IFF = '&', '|', '!', '>', '<>'

# Aliases aceitos na entrada (sintaxe "lógica" e sintaxe "booleana")
_SYMBOL_ALIASES = {
    '*': AND, '+': OR, '~': NOT,
    '->': IMPLIES, '<->': IFF,
}


class Node:
    """Classe base. Não instanciar diretamente."""

class VariableNode(Node):
    __slots__ = ('name',)

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, VariableNode) and self.name == other.name

    def __hash__(self):
        return hash(('var', self.name))
    
    @property
    def valor(self):
        return self.name

    @property
    def esquerda(self):
        return None

    @property
    def direita(self):
        return None
    
    def __str__(self):
        from BackEnd.core.expression_ast import to_string
        return to_string(self, style="logic")


class OperatorNode(Node):
    __slots__ = ('op', 'children')

    def __init__(self, op: str, children: List[Node]):
        self.op = op
        self.children = children

    def __eq__(self, other):
        return (isinstance(other, OperatorNode)
                and self.op == other.op
                and self.children == other.children)

    def __hash__(self):
        return hash((self.op, tuple(self.children)))

    # ---- ponte de compatibilidade com o código legado (esquerda/direita) ----
    @property
    def valor(self):  # alias para o código de identificar_lei.py
        return self.op

    @property
    def esquerda(self) -> Optional[Node]:
        return self.children[0] if self.children else None

    @esquerda.setter
    def esquerda(self, value: Node):
        if not self.children:
            self.children = [value]
        else:
            self.children[0] = value

    @property
    def direita(self) -> Optional[Node]:
        return self.children[1] if len(self.children) > 1 else None

    @direita.setter
    def direita(self, value: Node):
        if len(self.children) < 2:
            self.children.append(value)
        else:
            self.children[1] = value
            
    def __str__(self):
        from BackEnd.core.expression_ast import to_string
        return to_string(self, style="logic")


# --------------------------- PARSER ---------------------------

def _normalize_symbols(expr: str) -> str:
    expr = expr.replace(" ", "")
    for alias, canonical in sorted(_SYMBOL_ALIASES.items(), key=lambda kv: -len(kv[0])):
        expr = expr.replace(alias, canonical)
    return expr


def parse(expressao: str) -> Node:
    """Ponto de entrada único. Aceita &|!><> e *+~-><->  indistintamente."""
    expr = _normalize_symbols(expressao)
    tokens = list(expr)
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def consume():
        nonlocal pos
        pos += 1
        return tokens[pos - 1]

    def match(seq: str) -> bool:
        return expr[pos:pos + len(seq)] == seq

    # precedência: <> (menor) > (implicação) | & !  (maior)
    def parse_iff():
        node = parse_implies()
        while match(IFF):
            pos_local = 2
            nonlocal pos
            pos += pos_local
            node = OperatorNode(IFF, [node, parse_implies()])
        return node

    def parse_implies():
        node = parse_or()
        while peek() == IMPLIES:
            consume()
            node = OperatorNode(IMPLIES, [node, parse_or()])
        return node

    def parse_or():
        node = parse_and()
        while peek() == OR:
            consume()
            node = OperatorNode(OR, [node, parse_and()])
        return node

    def parse_and():
        node = parse_not()
        while peek() == AND:
            consume()
            node = OperatorNode(AND, [node, parse_not()])
        return node

    def parse_not():
        if peek() == NOT:
            consume()
            return OperatorNode(NOT, [parse_not()])
        if peek() == '(':
            consume()
            node = parse_iff()
            if peek() != ')':
                raise ValueError("Parênteses não balanceados.")
            consume()
            return node
        token = peek()
        if token is None or not token.isalnum():
            raise ValueError(f"Token inesperado na expressão: '{token}'")
        consume()
        return VariableNode(token)

    if not expr:
        raise ValueError("Expressão vazia.")
    resultado = parse_iff()
    if pos != len(tokens):
        raise ValueError(f"Caracteres sobrando após a expressão: '{expr[pos:]}'")
    return resultado


# ----------------------- IMPRESSÃO (compatível com o texto legado) -----------------------

def to_string(node: Node, style: str = "logic") -> str:
    """
    style='logic'   -> usa & | !   (formato de identificar_lei.py)
    style='boolean' -> usa * + ~   (formato de simplificador_interativo.py)
    """
    symbols = {AND: '&', OR: '|', NOT: '!'} if style == "logic" else {AND: '*', OR: '+', NOT: '~'}

    def visit(n: Node) -> str:
        if isinstance(n, VariableNode):
            return n.name
        if n.op == NOT:
            return f"{symbols[NOT]}{visit(n.children[0])}"
        if n.op in (AND, OR):
            return f"({visit(n.children[0])}{symbols[n.op]}{visit(n.children[1])})"
        if n.op == IMPLIES:
            return f"({visit(n.children[0])}>{visit(n.children[1])})"
        if n.op == IFF:
            return f"({visit(n.children[0])}<>{visit(n.children[1])})"
        raise ValueError(f"Operador desconhecido: {n.op}")

    return visit(node)


# ----------------------- HELPERS usados em vários módulos -----------------------

def collect_variables(node: Node) -> Set[str]:
    if isinstance(node, VariableNode):
        return {node.name}
    return set().union(*(collect_variables(c) for c in node.children))


def tree_size(node: Node) -> int:
    if isinstance(node, VariableNode):
        return 1
    return 1 + sum(tree_size(c) for c in node.children)


def avaliar(node: Node, valores: Dict[str, bool]) -> bool:
    """Substitui o avaliador por tokens de equivalencia.py."""
    if isinstance(node, VariableNode):
        if node.name in ('0', '1'):
            return node.name == '1'
        return valores.get(node.name, False)
    if node.op == NOT:
        return not avaliar(node.children[0], valores)
    a = avaliar(node.children[0], valores)
    b = avaliar(node.children[1], valores)
    if node.op == AND:
        return a and b
    if node.op == OR:
        return a or b
    if node.op == IMPLIES:
        return (not a) or b
    if node.op == IFF:
        return a == b
    raise ValueError(f"Operador desconhecido: {node.op}")