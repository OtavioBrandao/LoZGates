import logging
from dataclasses import dataclass


logger = logging.getLogger(__name__)
MAX_SIMPLIFICATION_STEPS = 100
passar_pro_front = []

class Node:
    def __init__(self, valor, esquerda=None, direita=None):
        self.valor = valor
        self.esquerda = esquerda
        self.direita = direita

    def __str__(self):
        if self.valor in ('*', '+'):
            return f"({self.esquerda}{self.valor}{self.direita})"
        elif self.valor == '~':
            return f"~{self.esquerda}"
        else:
            return str(self.valor)

    #Adicionamos um método para calcular o tamanho (número de nós) da subárvore
    def pegar_tamanho(self):
        size = 1 #Conta o próprio nó
        if self.esquerda:
            size += self.esquerda.pegar_tamanho()
        if self.direita:
            size += self.direita.pegar_tamanho()
        return size


def representacao_canonica(node):
    """Normaliza associação e ordem de operadores comutativos para detectar ciclos."""
    if node is None:
        return ""
    operator = {"&": "*", "|": "+", "!": "~"}.get(node.valor, node.valor)
    if operator == "~":
        return f"~{representacao_canonica(node.esquerda)}"
    if operator not in ("*", "+"):
        return str(node.valor).upper()

    operands = []

    def collect(current):
        current_operator = {"&": "*", "|": "+"}.get(
            getattr(current, "valor", None), getattr(current, "valor", None)
        )
        if current is not None and current_operator == operator:
            collect(current.esquerda)
            collect(current.direita)
        else:
            operands.append(representacao_canonica(current))

    collect(node)
    return f"{operator}({','.join(sorted(operands))})"


def chave_ordenacao(node):
    operator = {"&": "*", "|": "+", "!": "~"}.get(
        getattr(node, "valor", None), getattr(node, "valor", None)
    )
    return (1 if operator in ("*", "+", "~") else 0, representacao_canonica(node))


def calcular_complexidade(node):
    """Mede tamanho e padrões de reorganização; menor significa progresso."""
    if node is None:
        return 0
    operator = {"&": "*", "|": "+", "!": "~"}.get(node.valor, node.valor)
    if operator not in ("*", "+", "~"):
        return 2  # um nó e um literal

    left_cost = calcular_complexidade(node.esquerda)
    right_cost = calcular_complexidade(node.direita)
    base_cost = 2 + left_cost + right_cost  # nó + operador
    penalty = 0

    if operator == "~" and node.esquerda:
        child_operator = {"&": "*", "|": "+"}.get(
            node.esquerda.valor, node.esquerda.valor
        )
        if child_operator in ("*", "+"):
            penalty += 3
    if operator in ("*", "+") and node.esquerda:
        left_operator = {"&": "*", "|": "+"}.get(
            node.esquerda.valor, node.esquerda.valor
        )
        if left_operator == operator:
            penalty += 1
        if node.direita and chave_ordenacao(node.direita) < chave_ordenacao(node.esquerda):
            penalty += 1
    return base_cost + penalty


@dataclass(frozen=True)
class SimplificationDecision:
    accepted: bool
    reason: str


class SimplificationGuard:
    """Tracks finite progress for automatic and user-driven simplification."""

    def __init__(self, initial_tree, max_steps=MAX_SIMPLIFICATION_STEPS):
        self.max_steps = max(1, int(max_steps))
        self.accepted_steps = 0
        self.current_complexity = calcular_complexidade(initial_tree)
        self.visited_states = {representacao_canonica(initial_tree)}

    def consider(self, candidate):
        if self.accepted_steps >= self.max_steps:
            return SimplificationDecision(False, "maximum_steps")

        canonical = representacao_canonica(candidate)
        if canonical in self.visited_states:
            return SimplificationDecision(False, "repeated_state")

        complexity = calcular_complexidade(candidate)
        if complexity >= self.current_complexity:
            return SimplificationDecision(False, "no_progress")

        self.visited_states.add(canonical)
        self.current_complexity = complexity
        self.accepted_steps += 1
        return SimplificationDecision(True, "accepted")

def construir_arvore(expr):
    """Constroi a arvore booleana e rejeita entradas incompletas ou desbalanceadas."""
    if not isinstance(expr, str):
        raise TypeError("A expressão deve ser uma string.")

    source = expr.replace(" ", "")
    if not source:
        raise ValueError("A expressão não pode estar vazia.")

    position = 0

    def parse_or():
        nonlocal position
        node = parse_and()
        while position < len(source) and source[position] == '+':
            position += 1
            node = Node('+', node, parse_and())
        return node

    def parse_and():
        nonlocal position
        node = parse_not()
        while position < len(source) and source[position] == '*':
            position += 1
            node = Node('*', node, parse_not())
        return node

    def parse_not():
        nonlocal position
        if position < len(source) and source[position] == '~':
            position += 1
            return Node('~', esquerda=parse_not())
        return parse_atom()

    def parse_atom():
        nonlocal position
        if position >= len(source):
            raise ValueError("Operando ausente no final da expressão.")

        if source[position] == '(':
            position += 1
            node = parse_or()
            if position >= len(source) or source[position] != ')':
                raise ValueError("Parênteses desbalanceados na expressão.")
            position += 1
            return node

        start = position
        while position < len(source) and source[position] not in "*+~()":
            position += 1
        atom = source[start:position]
        if not atom:
            raise ValueError(f"Token inválido na posição {position + 1}.")
        return Node(atom)

    root = parse_or()
    if position != len(source):
        token = source[position]
        if token == ')':
            raise ValueError("Parênteses de fechamento sem abertura correspondente.")
        raise ValueError(f"Token inesperado '{token}' na posição {position + 1}.")
    return root

#------------------ Funções de Verificação -------------------

def sao_inversos(n1, n2):
    if not n1 or not n2:
        return False
    return (n1.valor == '~' and str(n1.esquerda) == str(n2)) or \
           (n2.valor == '~' and str(n2.esquerda) == str(n1))

def pode_demorgan(node):
    return node and node.valor == '~' and node.esquerda and node.esquerda.valor in ('*', '+')

def pode_identidade(node):
    if not node or not node.esquerda or not node.direita: return False
    if node.valor == '*':
        return str(node.esquerda) == '1' or str(node.direita) == '1'
    elif node.valor == '+':
        return str(node.esquerda) == '0' or str(node.direita) == '0'
    return False

def pode_nula(node):
    if not node or not node.esquerda or not node.direita: return False
    if node.valor == '*':
        return str(node.esquerda) == '0' or str(node.direita) == '0'
    elif node.valor == '+':
        return str(node.esquerda) == '1' or str(node.direita) == '1'
    return False

def pode_idempotente(node):
    return node and node.valor in ('*', '+') and node.esquerda and node.direita and str(node.esquerda) == str(node.direita)

def pode_inversa(node):
    return node and node.valor in ('*', '+') and node.esquerda and node.direita and sao_inversos(node.esquerda, node.direita)

def pode_absorcao(node):
    if not node or not node.esquerda or not node.direita:
        return False
    #A * (A + B) ou A * (B + A)
    if node.valor == '*' and node.direita and node.direita.valor == '+':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return True
    #(A + B) * A ou (B + A) * A
    if node.valor == '*' and node.esquerda and node.esquerda.valor == '+':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            return True
    #A + (A * B) ou A + (B * A)
    if node.valor == '+' and node.direita and node.direita.valor == '*':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return True
    #(A * B) + A ou (B * A) + A
    if node.valor == '+' and node.esquerda and node.esquerda.valor == '*':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            return True
    return False

def _fator_comum(left, right):
    if not left or not right or not left.esquerda or not left.direita:
        return None
    if not right.esquerda or not right.direita:
        return None
    candidates = (
        (left.esquerda, left.direita, right.esquerda, right.direita),
        (left.esquerda, left.direita, right.direita, right.esquerda),
        (left.direita, left.esquerda, right.esquerda, right.direita),
        (left.direita, left.esquerda, right.direita, right.esquerda),
    )
    for common_left, other_left, common_right, other_right in candidates:
        if str(common_left) == str(common_right):
            return common_left, other_left, other_right
    return None


def pode_distributiva(node):
    if not node or not node.esquerda or not node.direita:
        return False
    if node.valor == '*' and node.esquerda.valor == '+' and node.direita.valor == '+':
        return _fator_comum(node.esquerda, node.direita) is not None
    if node.valor == '+' and node.esquerda.valor == '*' and node.direita.valor == '*':
        return _fator_comum(node.esquerda, node.direita) is not None
    return False

def pode_associativa(node):
    if not node: return False
    #(A op B) op C  -> A op (B op C)
    return bool(
        node.valor in ('*', '+')
        and node.esquerda
        and node.esquerda.valor == node.valor
    )

def pode_comutativa(node):
    if not node or not node.esquerda or not node.direita: return False
    #Aplica para ordenar (ex: B * A -> A * B)
    return node.valor in ('*', '+') and chave_ordenacao(node.direita) < chave_ordenacao(node.esquerda)


#------------------ Leis Lógicas -------------------

def demorgan(node):
    inner = node.esquerda
    novo_op = '+' if inner.valor == '*' else '*'
    return Node(novo_op, Node('~', inner.esquerda), Node('~', inner.direita))

def identidade(node):
    if node.valor == '*':
        return node.direita if str(node.esquerda) == '1' else node.esquerda
    elif node.valor == '+':
        return node.direita if str(node.esquerda) == '0' else node.esquerda

def nula(node):
    return Node('0') if node.valor == '*' else Node('1')

def idempotente(node):
    return node.esquerda

def inversa(node):
    return Node('0') if node.valor == '*' else Node('1')

def absorcao(node):
    #A * (A+B) = A
    if node.valor == '*' and node.direita.valor == '+': return node.esquerda
    #(A+B) * A = A
    if node.valor == '*' and node.esquerda.valor == '+': return node.direita
    #A + (A*B) = A
    if node.valor == '+' and node.direita.valor == '*': return node.esquerda
    #(A*B) + A = A
    if node.valor == '+' and node.esquerda.valor == '*': return node.direita
    #Caso não corresponda, retorna o original (embora a verificação deva impedir isso)
    return node

def distributiva(node):
    #Simplificação: (A+B) * (A+C) -> A + (B*C)
    if node.valor == '*' and node.esquerda.valor == '+' and node.direita.valor == '+':
        factor = _fator_comum(node.esquerda, node.direita)
        if factor:
            common, o1, o2 = factor
            return Node('+', common, Node('*', o1, o2))

    #Simplificação dual: (A*B) + (A*C) -> A * (B+C)
    if node.valor == '+' and node.esquerda.valor == '*' and node.direita.valor == '*':
        factor = _fator_comum(node.esquerda, node.direita)
        if factor:
            common, o1, o2 = factor
            return Node('*', common, Node('+', o1, o2))

    return node #Retorna o nó original se nenhuma regra aplicou

def associativa(node):
    op = node.valor
    #(A op B) op C -> A op (B op C)
    if node.esquerda.valor == op:
        a, b, c = node.esquerda.esquerda, node.esquerda.direita, node.direita
        return Node(op, a, Node(op, b, c))
    #A op (B op C) -> (A op B) op C
    elif node.direita.valor == op:
        a, b, c = node.esquerda, node.direita.esquerda, node.direita.direita
        return Node(op, Node(op, a, b), c)
    return node

def comutativa(node):
    return Node(node.valor, node.direita, node.esquerda)


#--- Estrutura de dados que agrupa as leis, suas verificações e aplicações ---
LEIS_LOGICAS = [
    #Leis de simplificação mais fortes primeiro
    {"nome": "Inversa (A * ~A = 0)", "verifica": pode_inversa, "aplica": inversa},
    {"nome": "Nula (A * 0 = 0)", "verifica": pode_nula, "aplica": nula},
    {"nome": "Identidade (A * 1 = A)", "verifica": pode_identidade, "aplica": identidade},
    {"nome": "Idempotente (A * A = A)", "verifica": pode_idempotente, "aplica": idempotente},
    {"nome": "Absorção (A * (A+B) = A)", "verifica": pode_absorcao, "aplica": absorcao},
    {"nome": "De Morgan (~(A*B) = ~A+~B)", "verifica": pode_demorgan, "aplica": demorgan},
    {"nome": "Distributiva com fator comum", "verifica": pode_distributiva, "aplica": distributiva},
    
    #Leis de reorganização
    {"nome": "Associativa ((A*B)*C = A*(B*C))", "verifica": pode_associativa, "aplica": associativa},
    {"nome": "Comutativa (B*A = A*B)", "verifica": pode_comutativa, "aplica": comutativa},
]

#Variável global para armazenar a lista ordenada de nós
_todos_os_nos_ordenados = []
_indice_no_atual = 0
_chave_busca_atual = None


def reiniciar_busca():
    """Invalida o cursor global mantido por compatibilidade com a interface."""
    global _todos_os_nos_ordenados, _indice_no_atual, _chave_busca_atual
    _todos_os_nos_ordenados = []
    _indice_no_atual = 0
    _chave_busca_atual = None

#------------------ Funções para Controle da GUI -------------------

def _coletar_todos_os_nos(node, parent=None, branch=None, collected_nodes=None):
    if collected_nodes is None:
        collected_nodes = []
    if node:
        if node.esquerda or node.direita: #Se tiver filhos, não é um átomo sozinho
            collected_nodes.append({
                "no_atual": node,
                "pai": parent,
                "ramo": branch,
                "leis_aplicaveis": [lei['verifica'](node) for lei in LEIS_LOGICAS]
            })

        _coletar_todos_os_nos(node.esquerda, node, 'esquerda', collected_nodes)
        _coletar_todos_os_nos(node.direita, node, 'direita', collected_nodes)
    return collected_nodes

def encontrar_proximo_passo(arvore_raiz, nos_a_ignorar=None):
    global _todos_os_nos_ordenados, _indice_no_atual, _chave_busca_atual

    if nos_a_ignorar is None:
        nos_a_ignorar = set()

    chave_busca = (
        id(arvore_raiz),
        str(arvore_raiz),
        frozenset(id(node) for node in nos_a_ignorar),
    )
    if chave_busca != _chave_busca_atual:
        todos_nos_info = _coletar_todos_os_nos(arvore_raiz)
        _todos_os_nos_ordenados = [info for info in todos_nos_info if info['no_atual'] not in nos_a_ignorar]
        
        _todos_os_nos_ordenados.sort(key=lambda x: (x['no_atual'].pegar_tamanho(), str(x['no_atual'])))
        _indice_no_atual = 0
        _chave_busca_atual = chave_busca

    #Avança o índice até encontrar um nó não ignorado
    while _indice_no_atual < len(_todos_os_nos_ordenados):
        passo_atual_info = _todos_os_nos_ordenados[_indice_no_atual]
        _indice_no_atual += 1 
        return passo_atual_info

    return None


def _contem_identidade(raiz, alvo):
    if raiz is alvo:
        return True
    if raiz is None:
        return False
    return _contem_identidade(raiz.esquerda, alvo) or _contem_identidade(
        raiz.direita, alvo
    )


def aplicar_lei_e_substituir(arvore_raiz, passo_info, indice_lei):
    if not isinstance(indice_lei, int) or not 0 <= indice_lei < len(LEIS_LOGICAS):
        return arvore_raiz, False
    if not arvore_raiz or not passo_info:
        return arvore_raiz, False

    lei_escolhida = LEIS_LOGICAS[indice_lei]
    no_alvo = passo_info.get('no_atual')
    pai = passo_info.get('pai')
    ramo = passo_info.get('ramo')

    #Impede que referencias copiadas separadamente (caso do undo antigo)
    #informem sucesso sem modificar a arvore exibida.
    if pai is None:
        if no_alvo is not arvore_raiz:
            return arvore_raiz, False
    else:
        parent_is_attached = _contem_identidade(arvore_raiz, pai)
        target_matches_branch = (
            (ramo == 'esquerda' and pai.esquerda is no_alvo)
            or (ramo == 'direita' and pai.direita is no_alvo)
        )
        if not parent_is_attached or not target_matches_branch:
            return arvore_raiz, False

    #Verifica novamente por segurança
    if not lei_escolhida['verifica'](no_alvo):
        return arvore_raiz, False

    novo_no = lei_escolhida['aplica'](no_alvo)
    if novo_no is None or str(novo_no) == str(no_alvo):
        return arvore_raiz, False
    if calcular_complexidade(novo_no) >= calcular_complexidade(no_alvo):
        logger.info(
            "Transformation rejected without simplification: rule=%s before=%s after=%s",
            lei_escolhida["nome"],
            no_alvo,
            novo_no,
        )
        return arvore_raiz, False

    if pai is None:
        #A raiz da árvore foi substituída
        reiniciar_busca()
        return novo_no, True
    
    if ramo == 'esquerda':
        pai.esquerda = novo_no
    elif ramo == 'direita':
        pai.direita = novo_no

    #Retorna a raiz original, que agora aponta para a árvore modificada
    reiniciar_busca()
    return arvore_raiz, True
