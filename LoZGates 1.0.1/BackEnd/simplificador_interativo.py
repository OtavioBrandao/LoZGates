import time
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
    expr = expr.replace(" ", "")

    def construir_arvore_or(s):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            c = s[i]
            if c == ')': depth += 1
            elif c == '(': depth -= 1
            elif c == '+' and depth == 0:
                return Node('+', construir_arvore_or(s[:i]), construir_arvore_and(s[i+1:]))
        return construir_arvore_and(s)

    def construir_arvore_and(s):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            c = s[i]
            if c == ')': depth += 1
            elif c == '(': depth -= 1
            elif c == '*' and depth == 0:
                return Node('*', construir_arvore_and(s[:i]), construir_arvore_not(s[i+1:]))
        return construir_arvore_not(s)

    def construir_arvore_not(s):
        if s.startswith('~'):
            return Node('~', esquerda=construir_arvore_or(s[1:]))
        elif s.startswith('(') and s.endswith(')'):
            return construir_arvore_or(s[1:-1])
        else:
            return Node(s)

    return construir_arvore_or(expr)

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
    if not node: return False
    #A + (B * C) -> (A + B) * (A + C)
    if node.valor == '+' and node.direita and node.direita.valor == '*':
        return True
    if node.valor == '+' and node.esquerda and node.esquerda.valor == '*':
        return True
    #A * (B + C) -> (A * B) + (A * C) (a mais comum para expansão)
    if node.valor == '*' and node.direita and node.direita.valor == '+':
        return True
    if node.valor == '*' and node.esquerda and node.esquerda.valor == '+':
        return True
    #(A+B) * (A+C) -> A + (B*C) (a mais comum para simplificação)
    if node.valor == '*' and node.esquerda and node.direita and node.esquerda.valor == '+' and node.direita.valor == '+':
        a, b = node.esquerda.esquerda, node.esquerda.direita
        c, d = node.direita.esquerda, node.direita.direita
        if any(str(x) == str(y) for x in [a,b] for y in [c,d]):
            return True
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
    global _todos_os_nos_ordenados, _indice_no_atual

    if nos_a_ignorar is None:
        nos_a_ignorar = set()

    #Na primeira chamada ou se a árvore mudou ou se o índice atual está fora dos limites refazemos a lista de todos os nós.
    #Usamos o ID do objeto para verificar se a árvore é a mesma.
    if not _todos_os_nos_ordenados or id(arvore_raiz) != getattr(encontrar_proximo_passo, '_ultima_arvore_id', None):
        todos_nos_info = _coletar_todos_os_nos(arvore_raiz) 
        _todos_os_nos_ordenados = [info for info in todos_nos_info if info['no_atual'] not in nos_a_ignorar]
        
        _todos_os_nos_ordenados.sort(key=lambda x: (x['no_atual'].pegar_tamanho(), str(x['no_atual'])))
        _indice_no_atual = 0
        setattr(encontrar_proximo_passo, '_ultima_arvore_id', id(arvore_raiz)) #Salva o ID da árvore

    #Avança o índice até encontrar um nó não ignorado
    while _indice_no_atual < len(_todos_os_nos_ordenados):
        passo_atual_info = _todos_os_nos_ordenados[_indice_no_atual]
        _indice_no_atual += 1 
        return passo_atual_info

    return None

def aplicar_lei_e_substituir(arvore_raiz, passo_info, indice_lei):
    lei_escolhida = LEIS_LOGICAS[indice_lei]
    no_alvo = passo_info['no_atual']
    pai = passo_info['pai']
    ramo = passo_info['ramo']

    #Verifica novamente por segurança
    if not lei_escolhida['verifica'](no_alvo):
        return arvore_raiz, False

    novo_no = lei_escolhida['aplica'](no_alvo)

    if pai is None:
        #A raiz da árvore foi substituída
        return novo_no, True
    
    if ramo == 'esquerda':
        pai.esquerda = novo_no
    elif ramo == 'direita':
        pai.direita = novo_no

    #Retorna a raiz original, que agora aponta para a árvore modificada
    return arvore_raiz, True