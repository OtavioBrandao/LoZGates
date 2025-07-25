import time
passar_pro_front = []

class Node:
    """
    Representa um nó na árvore de expressão.
    O valor pode ser um operador, uma variável ou uma constante.
    """
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
    if node.valor == '*' and node.direita.valor == '+':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return True
    #(A + B) * A ou (B + A) * A
    if node.valor == '*' and node.esquerda.valor == '+':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            return True
    #A + (A * B) ou A + (B * A)
    if node.valor == '+' and node.direita.valor == '*':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return True
    #(A * B) + A ou (B * A) + A
    if node.valor == '+' and node.esquerda.valor == '*':
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

#------------------ Processo Interativo -------------------

def encontrar_e_aplicar_interativo(node):
    """
    Percorre a árvore (pós-ordem). Para cada nó, permite ao usuário TENTAR
    aplicar qualquer lei. Se a lei escolhida for inaplicável, informa o usuário.
    Retorna o nó modificado e um flag indicando se houve mudança.
    """
    if node is None:
        return None, False

    #1. Tenta simplificar os filhos primeiro.
    mudou_na_subarvore = False
    
    no_filho_esquerdo, mudou_esquerda = encontrar_e_aplicar_interativo(node.esquerda)
    if mudou_esquerda:
        node.esquerda = no_filho_esquerdo
        mudou_na_subarvore = True

    no_filho_direito, mudou_direita = encontrar_e_aplicar_interativo(node.direita)
    if mudou_direita:
        node.direita = no_filho_direito
        mudou_na_subarvore = True
    
    #Se uma mudança já ocorreu em um filho, reiniciamos a busca do topo para garantir que a expressão inteira seja reavaliada.
    if mudou_na_subarvore:
        return node, True

    #2. Se nenhuma mudança ocorreu nos filhos, interage com o usuário para o nó atual.
    #Este laço continua até o usuário aplicar uma lei com sucesso ou pular (0).
    while True:
        passar_pro_front.append("\n--------------------------------------------------------")
        passar_pro_front.append(f"Expressão atual: {str(arvore_global)}")
        passar_pro_front.append(f"\nAnalisando a sub-expressão: '{node}'")
        passar_pro_front.append("Qual lei você gostaria de TENTAR aplicar?")
        
        #3. Sempre mostra TODAS as leis
        for i, lei in enumerate(LEIS_LOGICAS, 1):
            print(f"  {i}. {lei['nome']}")
        print("  0. Pular / Nenhuma")

        #4. Obtém a escolha do usuário
        try:
            escolha = int(input("\nEscolha uma opção: "))
            if not (0 <= escolha <= len(LEIS_LOGICAS)):
                passar_pro_front.append("Opção inválida. Tente novamente.")
                time.sleep(1)
                continue
        except ValueError:
            print("Por favor, digite um número.")
            time.sleep(1)
            continue
            
        #5. Processa a escolha
        if escolha == 0:
            passar_pro_front.append("Ok, pulando este nó.")
            return node, False #Nenhuma mudança feita neste nó

        lei_escolhida = LEIS_LOGICAS[escolha - 1]

        #6. VERIFICA se a lei escolhida é aplicável
        if lei_escolhida["verifica"](node):
            #Se for, aplica a lei e retorna.
            antigo_no_str = str(node)
            novo_no = lei_escolhida["aplica"](node)
            passar_pro_front.append(f"\nÓtimo~ A lei '{lei_escolhida['nome']}' foi aplicada com sucesso.")
            passar_pro_front.append(f"'{antigo_no_str}'  ->  '{novo_no}'")
            time.sleep(2)
            return novo_no, True #Retorna o nó modificado e indica que houve mudança
        else:
            #Se não for, informa o usuário e o laço continua, mostrando as opções novamente.
            passar_pro_front.append(f"\nAVISO: A lei '{lei_escolhida['nome']}' não pode ser aplicada na sub-expressão '{node}'.")
            passar_pro_front.append("Por favor, escolha outra lei ou pule (0).")
            time.sleep(2.5) #Pausa para o usuário ler o aviso


def modo_interativo(expressao_usuario):
    global arvore_global

    passar_pro_front.append(f"\n=======================================================")
    passar_pro_front.append(f"Expressão Original: {expressao_usuario}")
    passar_pro_front.append(f"=======================================================")

    try:
        arvore = construir_arvore(expressao_usuario)
        arvore_global = arvore
        print(f"Árvore Inicial: {arvore}")
        
        #O laço de simplificação continua enquanto houver mudanças
        houve_mudanca_geral = True
        while houve_mudanca_geral:
            arvore_global, houve_mudanca_geral = encontrar_e_aplicar_interativo(arvore_global)
            
            if not houve_mudanca_geral:
                passar_pro_front.append("\nNenhuma outra simplificação foi aplicada ou você pulou todas as opções.")
                break
        
        passar_pro_front.append("\n------------------ Resultado Final -------------------")
        passar_pro_front.append(f"Expressão Original    : {expressao_usuario}")
        passar_pro_front.append(f"Expressão Simplificada: {arvore_global}")
        passar_pro_front.append("--------------------------------------------------------\n")

    except Exception as e:
        print(f"Ocorreu um erro ao processar a expressão: {e}")
        print("Por favor, verifique se a sintaxe está correta (ex: 'P * (Q + ~R)').")
    return passar_pro_front

#------------------ Laço Principal de Execução -------------------
if __name__ == "__main__":
    arvore_global = None 
    while True:
        expressao_do_usuario = input("\nDigite a expressão lógica (use ~, *, +) ou 'sair' para terminar: ")
        if expressao_do_usuario.lower() == 'sair':
            break
        modo_interativo(expressao_do_usuario)