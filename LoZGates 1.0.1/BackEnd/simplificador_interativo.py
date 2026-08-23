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

def pode_distributiva(node):
    if not node or not node.esquerda or not node.direita:
        return False
    if node.valor == '*':
        return node.esquerda.valor == '+' or node.direita.valor == '+'
    if node.valor == '+':
        return node.esquerda.valor == '*' or node.direita.valor == '*'
    return False

def pode_associativa(node):
    if not node: return False
    #(A op B) op C  -> A op (B op C)
    if node.valor in ('*', '+') and node.esquerda and node.esquerda.valor == node.valor:
        return True
    #A op (B op C) -> (A op B) op C
    if node.valor in ('*', '+') and node.direita and node.direita.valor == node.valor:
        return True
    return False

def pode_comutativa(node):
    if not node or not node.esquerda or not node.direita: return False
    #Aplica para ordenar (ex: B * A -> A * B)
    return node.valor in ('*', '+') and str(node.direita) < str(node.esquerda)


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
        a, b = node.esquerda.esquerda, node.esquerda.direita
        c, d = node.direita.esquerda, node.direita.direita
        common, o1, o2 = (None, None, None)
        if str(a) == str(c): common, o1, o2 = a, b, d
        elif str(a) == str(d): common, o1, o2 = a, b, c
        elif str(b) == str(c): common, o1, o2 = b, a, d
        elif str(b) == str(d): common, o1, o2 = b, a, c
        if common:
            return Node('+', common, Node('*', o1, o2))
            
    #Expansão: A * (B + C) -> (A * B) + (A * C)
    if node.valor == '*':
        if node.direita and node.direita.valor == '+':
            a, b, c = node.esquerda, node.direita.esquerda, node.direita.direita
            return Node('+', Node('*', a, b), Node('*', a, c))
        if node.esquerda and node.esquerda.valor == '+':
            a, b, c = node.direita, node.esquerda.esquerda, node.esquerda.direita
            return Node('+', Node('*', a, b), Node('*', a, c))

    #Expansão dual: A + (B * C) -> (A + B) * (A + C)
    if node.valor == '+':
        if node.direita and node.direita.valor == '*':
            a, b, c = node.esquerda, node.direita.esquerda, node.direita.direita
            return Node('*', Node('+', a, b), Node('+', a, c))
        if node.esquerda and node.esquerda.valor == '*':
            a, b, c = node.direita, node.esquerda.esquerda, node.esquerda.direita
            return Node('*', Node('+', a, b), Node('+', a, c))

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
    {"nome": "Distributiva ((A+B)*(A+C) = A+(B*C))", "verifica": pode_distributiva, "aplica": distributiva},
    
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
