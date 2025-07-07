import time

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
    return node
 
# ------------------ Processo de Simplificação -------------------
def aplicar_leis_recursivo(node):
    """
    Percorre a árvore (pós-ordem) e tenta aplicar as leis em cada nó
    Retorna o nó e substitui o original
    """
    if node is None:
        return None

    #simplifica recursivamente os filhos primeiro
    if node.esquerda:
        node.esquerda = aplicar_leis_recursivo(node.esquerda)
    if node.direita:
        node.direita = aplicar_leis_recursivo(node.direita)
        
    original_str = str(node) #Guarda o estado original para detectar mudanças
    
    #aplica um conjunto de leis que retornam um novo nó em caso de mudança
    novo_no = node
    
    leis_a_aplicar = [nula, inversa, idempotente, identidade, absorcao, demorgan, associativa, distributiva, comutativa]
    
    for lei in leis_a_aplicar:
        novo_no = lei(novo_no)

    #se teve alguma mudança, imprime o passo
    if str(novo_no) != original_str:
        #print(f"Passo de simplificação: {original_str} -> {novo_no}\n\n")
        return aplicar_leis_recursivo(novo_no)
        
    return novo_no

def simplificar(arvore):
    #Aplica as leis lógicas na árvore até que nenhuma outra simplificação seja possível

    print("--- Iniciando Simplificação ---")
    passo = 1
    while True:
        expressao_anterior = str(arvore)
        print(f"\nIteração {passo}: tentando simplificar {expressao_anterior}")
        arvore = aplicar_leis_recursivo(arvore)
        expressao_atual = str(arvore)
        
        if expressao_anterior == expressao_atual:
            print("\nNenhuma outra simplificação foi possível.")
            break
        
        print(f"Árvore intermediária: {expressao_atual}")
        passo += 1
        time.sleep(1) #tempo pra ver
        
    return arvore

# ------------------ Laço Principal de Execução -------------------
def principal_simplificar(expressao_usuario):
 
    #expressao_usuario = input("\nDigite a expressão lógica (use !, &, |) ou 'sair' para terminar: ")
    expressao_usuario = expressao_usuario.replace("+", "|").replace("*", "&").replace("~", "!")
    print(f"\n=======================================================")
    print(f"Expressão Original: {expressao_usuario}")
    print(f"=======================================================")

    try:
        arvore = construir_arvore(expressao_usuario)
        print(f"Árvore Inicial: {arvore}")
        
        arvore_simplificada = simplificar(arvore)
        
        print("\n------------------ Resultado Final -------------------")
        print(f"Expressão Original    : {expressao_usuario}")
        print(f"Expressão Simplificada: {arvore_simplificada}")
        print("--------------------------------------------------------\n")

    except Exception as e:
        print(f"Ocorreu um erro ao processar a expressão: {e}")
        print("Por favor, verifique se a sintaxe está correta (ex: 'P & (Q | !R)').")
        


'''
-------------------------casos testes------------------

(!(P|Q)|!P)&P
P&!P&Q

'''