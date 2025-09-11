"""
Módulo contendo as classes de nós da AST (Abstract Syntax Tree)
para representação de expressões lógicas booleanas.
"""

class Node:
    """Classe base para todos os nós da AST."""
    pass

class VariableNode(Node):
    """Nó representando uma variável lógica."""
    
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

class OperatorNode(Node):
    """Nó representando um operador lógico."""
    
    def __init__(self, op, children):
        self.op = op
        self.children = children
    
    def __str__(self):
        if self.op == '~' and len(self.children) == 1:
            return f"~{self.children[0]}"
        elif len(self.children) == 2:
            return f"({self.children[0]} {self.op} {self.children[1]})"
        return f"{self.op}({', '.join(str(child) for child in self.children)})"