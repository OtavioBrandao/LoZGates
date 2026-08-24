import copy
import io
import logging
from contextlib import redirect_stdout

from BackEnd.simplificador_interativo import (
    MAX_SIMPLIFICATION_STEPS,
    SimplificationGuard,
    calcular_complexidade,
)


logger = logging.getLogger(__name__)

class Node:
    """
    Representa um nó na árvore de expressão
    O valor pode ser um operador, uma variável ou uma constante
    """
    def __init__(self, valor, esquerda=None, direita=None):
        self.valor = valor
        self.esquerda = esquerda
        self.direita = direita

    def __str__(self):
        #Constroi a representação em string da expressão de forma recursiva
        if self.valor in ('&', '|'):
            #Adiciona parênteses para manter a precedência correta
            return f"({self.esquerda}{self.valor}{self.direita})"
        elif self.valor == '!':
            #A negação é prefixa
            return f"!{self.esquerda}"
        else:
            return str(self.valor)

def construir_arvore(expr):
    """
    Analisa uma string de expressão lógica e a converte em uma árvore de expressão
    Respeita a precedência: ! > & > |
    """
    expr = expr.replace(" ", "")

    def construir_arvore_or(s):
        #Divide a expressão por '|' de menor precedência
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            c = s[i]
            if c == ')': depth += 1
            elif c == '(': depth -= 1
            elif c == '|' and depth == 0:
                #Encontrou um '|' no nível base, cria um nó recursivamente
                return Node('|', construir_arvore_or(s[:i]), construir_arvore_and(s[i+1:]))
        return construir_arvore_and(s)

    def construir_arvore_and(s):
        #Divide pelo '&'
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            c = s[i]
            if c == ')': depth += 1
            elif c == '(': depth -= 1
            elif c == '&' and depth == 0:
                return Node('&', construir_arvore_and(s[:i]), construir_arvore_not(s[i+1:]))
        return construir_arvore_not(s)

    def construir_arvore_not(s):
        #Lida com negação, parênteses e etc
        if s.startswith('!'):
            return Node('!', esquerda=construir_arvore_or(s[1:]))
        elif s.startswith('(') and s.endswith(')'):
            return construir_arvore_or(s[1:-1])
        else:
            return Node(s)

    return construir_arvore_or(expr)

# ------------------ Leis Lógicas (Retornam o nó modificado) -------------------
def sao_inversos(n1, n2):
    if not n1 or not n2:
        return False
    return (n1.valor == '!' and str(n1.esquerda) == str(n2)) or \
           (n2.valor == '!' and str(n2.esquerda) == str(n1))

def demorgan(node):
    #!(A & B) = !A | !B  e  !(A | B) = !A & !B
    if node.valor == '!' and node.esquerda and node.esquerda.valor in ('&', '|'):
        inner = node.esquerda
        op_original = inner.valor
        
        # Cria a nova estrutura baseada na lei
        novo_op = '|' if op_original == '&' else '&'
        novo_no = Node(novo_op, Node('!', inner.esquerda), Node('!', inner.direita))
        
        print(f"Aplicando De Morgan em '{node}' -> '{novo_no}'\n")
        return novo_no
    return node

def identidade(node):
    #A & 1 = A  e  A | 0 = A
    if node.valor == '&':
        if str(node.esquerda) == '1':
          print(f"Aplicando Identidade em '{node}' -> '{node.direita}'\n")
          return node.direita
        if str(node.direita) == '1': 
          print(f"Aplicando Identidade em '{node}' -> '{node.esquerda}'\n")
          return node.esquerda
    
    elif node.valor == '|':
        if str(node.esquerda) == '0':
          print(f"Aplicando Identidade em '{node}' -> '{node.direita}'\n")
          return node.direita
        if str(node.direita) == '0': 
          print(f"Aplicando Identidade em '{node}' -> '{node.esquerda}'\n")
          return node.esquerda
        
    return node

def nula(node):
    #A & 0 = 0  e  A | 1 = 1
    if node.valor == '&':
        if str(node.esquerda) == '0' or str(node.direita) == '0':
            print(f"Aplicando Nula em '{node}' -> '0'\n")
            return Node('0')
    elif node.valor == '|':
        if str(node.esquerda) == '1' or str(node.direita) == '1':
            print(f"Aplicando Nula em '{node}' -> '1'\n")
            return Node('1')
    return node

def idempotente(node):
    #A & A = A  e  A | A = A
    if node.valor in ('&', '|') and str(node.esquerda) == str(node.direita):
        print(f"Aplicando Idempotência em '{node}' -> '{node.esquerda}'\n")
        return node.esquerda
    return node

def inversa(node):
    #A & !A = 0  e  A | !A = 1
    if node.esquerda and node.direita and sao_inversos(node.esquerda, node.direita):
        if node.valor == '&': 
          print(f"Aplicando Inversa em '{node}' -> '0'\n")
          return Node('0')
        
        if node.valor == '|': 
          print(f"Aplicando Inversa em '{node}' -> '1'\n")
          return Node('1')
    return node

def absorcao(node):
    #A & (A | B) = A  e  A | (A & B) = A
    if node.valor == '&' and node.direita and node.direita.valor == '|':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            print(f"Aplicando Absorção em '{node}' -> '{node.esquerda}'\n")
            return node.esquerda
    if node.valor == '&' and node.esquerda and node.esquerda.valor == '|':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            print(f"Aplicando Absorção em '{node}' -> '{node.direita}'\n")
            return node.direita
    if node.valor == '|' and node.direita and node.direita.valor == '&':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            print(f"Aplicando Absorção em '{node}' -> '{node.esquerda}'\n")
            return node.esquerda
    if node.valor == '|' and node.esquerda and node.esquerda.valor == '&':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            print(f"Aplicando Absorção em '{node}' -> '{node.direita}'\n")
            return node.direita
    return node

def associativa(node):
    #(A | B) | C = A | (B | C) e (A & B) & C = A & (B & C)
    #coisa para a direita
    if node.valor in ('&', '|') and node.esquerda and node.esquerda.valor == node.valor:
        op = node.valor
        a = node.esquerda.esquerda
        b = node.esquerda.direita
        c = node.direita
        novo_no = Node(op, a, Node(op, b, c))
        print(f"Aplicando Associativa em '{node}' -> '{novo_no}'\n")
        return novo_no
    return node

def comutativa(node):
    if node.valor in ('&', '|'):
        if node.esquerda and node.direita and str(node.direita) < str(node.esquerda):
             novo_no = Node(node.valor, node.direita, node.esquerda)
             print(f"Aplicando Comutativa em '{node}' -> '{novo_no}'\n")
             return novo_no
    return node

def distributiva(node):
    #(A|B)&(A|C) -> A|(B&C)
    if node.valor == '&' and (node.esquerda and node.direita and
                              node.esquerda.valor == '|' and node.direita.valor == '|'):
        a, b = node.esquerda.esquerda, node.esquerda.direita
        c, d = node.direita.esquerda, node.direita.direita
        common, o1, o2 = (None, None, None)
        
        if str(a) == str(c): common, o1, o2 = a, b, d
        elif str(a) == str(d): common, o1, o2 = a, b, c
        elif str(b) == str(c): common, o1, o2 = b, a, d
        elif str(b) == str(d): common, o1, o2 = b, a, c

        if common:
            novo_no = Node('|', common, Node('&', o1, o2))
            print(f"Aplicando Distributiva em '{node}' -> '{novo_no}'\n")
            return novo_no

    #(A&B)|(A&C) -> A&(B|C)
    if node.valor == '|' and (node.esquerda and node.direita and
                              node.esquerda.valor == '&' and node.direita.valor == '&'):
        a, b = node.esquerda.esquerda, node.esquerda.direita
        c, d = node.direita.esquerda, node.direita.direita
        common, o1, o2 = (None, None, None)

        if str(a) == str(c): common, o1, o2 = a, b, d
        elif str(a) == str(d): common, o1, o2 = a, b, c
        elif str(b) == str(c): common, o1, o2 = b, a, d
        elif str(b) == str(d): common, o1, o2 = b, a, c

        if common:
            novo_no = Node('&', common, Node('|', o1, o2))
            print(f"Aplicando Distributiva em '{node}' -> '{novo_no}'\n")
            return novo_no
    return node

# ------------------ Processo de Simplificação -------------------
LEIS_AUTOMATICAS = [
    ("Nula", nula),
    ("Inversa", inversa),
    ("Idempotência", idempotente),
    ("Identidade", identidade),
    ("Absorção", absorcao),
    ("De Morgan", demorgan),
    ("Distributiva", distributiva),
]


def _aplicar_primeira_reducao(node):
    """Apply at most one strictly reducing rule, traversing children first."""
    if node is None:
        return node, False, None

    if node.esquerda:
        new_left, changed, law_name = _aplicar_primeira_reducao(node.esquerda)
        if changed:
            node.esquerda = new_left
            return node, True, law_name
    if node.direita:
        new_right, changed, law_name = _aplicar_primeira_reducao(node.direita)
        if changed:
            node.direita = new_right
            return node, True, law_name

    original_complexity = calcular_complexidade(node)
    for law_name, law in LEIS_AUTOMATICAS:
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            candidate = law(node)
        if str(candidate) == str(node):
            continue
        if calcular_complexidade(candidate) >= original_complexity:
            logger.debug(
                "Automatic rule did not reduce complexity: rule=%s before=%s after=%s",
                law_name,
                node,
                candidate,
            )
            continue
        print(captured_output.getvalue(), end="")
        return candidate, True, law_name

    return node, False, None


def aplicar_leis_recursivo(node):
    """Compatibility helper: perform one safe reducing traversal."""
    candidate, _, _ = _aplicar_primeira_reducao(copy.deepcopy(node))
    return candidate


def simplificar(arvore, max_steps=MAX_SIMPLIFICATION_STEPS):
    """Simplify finitely, keeping the last accepted expression."""

    print("--- Iniciando Simplificação ---")
    logger.info("simplification started: expression=%s", arvore)
    guard = SimplificationGuard(arvore, max_steps=max_steps)

    for passo in range(1, guard.max_steps + 1):
        expressao_anterior = str(arvore)
        print(f"\nIteração {passo}: tentando simplificar {expressao_anterior}")
        candidate, changed, law_name = _aplicar_primeira_reducao(copy.deepcopy(arvore))

        if not changed:
            print("\nNenhuma outra simplificação foi possível.")
            logger.info(
                "no further simplification: expression=%s steps=%s",
                arvore,
                guard.accepted_steps,
            )
            return arvore

        decision = guard.consider(candidate)
        if not decision.accepted:
            if decision.reason == "repeated_state":
                print("\nEstado equivalente já visitado; simplificação encerrada.")
                logger.warning(
                    "repeated state detected: expression=%s step=%s",
                    candidate,
                    passo,
                )
            elif decision.reason == "maximum_steps":
                print("\nLimite de segurança atingido; mantendo a última expressão válida.")
                logger.warning(
                    "maximum steps reached: expression=%s limit=%s",
                    arvore,
                    guard.max_steps,
                )
            else:
                print("\nA transformação não reduziu a complexidade; simplificação encerrada.")
                logger.warning(
                    "simplification stopped without progress: before=%s candidate=%s",
                    arvore,
                    candidate,
                )
            return arvore

        arvore = candidate
        logger.info(
            "rule applied: rule=%s step=%s complexity=%s expression=%s",
            law_name,
            passo,
            calcular_complexidade(arvore),
            arvore,
        )
        print(f"Árvore intermediária: {arvore}")

        if not arvore.esquerda and not arvore.direita:
            logger.info(
                "simplification completed: expression=%s steps=%s",
                arvore,
                guard.accepted_steps,
            )
            return arvore

    logger.warning(
        "maximum steps reached: expression=%s limit=%s",
        arvore,
        guard.max_steps,
    )
    print("\nLimite de segurança atingido; mantendo a última expressão válida.")

    return arvore

# ------------------ Laço Principal de Execução -------------------
def principal_simplificar(expressao_usuario):
 
    #expressao_usuario = input("\nDigite a expressão lógica (use !, &, |) ou 'sair' para terminar: ")
    expressao_usuario = expressao_usuario.replace("+", "|").replace("*", "&").replace("~", "!")
    print(f"\n=====================================================================")
    print(f"\t\tExpressão Original: {expressao_usuario}")
    print(f"=====================================================================")

    try:
        arvore = construir_arvore(expressao_usuario)
        
        arvore_simplificada = simplificar(arvore)
        
        print("\n------------------ Resultado Final -------------------")
        print(f"Expressão Original    : {expressao_usuario}")
        print(f"Expressão Simplificada: {arvore_simplificada}")
        print("------------------------------------------------------\n")
        return arvore_simplificada

    except Exception as e:
        logger.exception("simplification exception: expression=%s", expressao_usuario)
        print(f"Ocorreu um erro ao processar a expressão: {e}")
        print("Por favor, verifique se a sintaxe está correta (ex: 'P & (Q | !R)').")
        return None
        
'''
-------------------------casos testes------------------

(!(P|Q)|!P)&P
P&!P&Q

'''
