import logging
from dataclasses import dataclass

from BackEnd.core.expression_ast import (
    OperatorNode,
    VariableNode,
    parse,
    to_string,
    tree_size,
)


logger = logging.getLogger(__name__)
MAX_SIMPLIFICATION_STEPS = 100

# Nome mantido por compatibilidade: é o próprio parser canônico.
construir_arvore = parse


def formatar(node):
    """
    Texto da (sub)árvore no estilo booleano (* + ~), que é o formato que o
    simplificador interativo sempre mostrou ao aluno. Use esta função para
    exibir árvores deste módulo: str(no) usa o estilo lógico (& | !).
    """
    return to_string(node, style="boolean")


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

#------------------ Funções de Verificação -------------------

def sao_inversos(n1, n2):
    if not n1 or not n2:
        return False
    return (n1.valor == '!' and str(n1.esquerda) == str(n2)) or \
           (n2.valor == '!' and str(n2.esquerda) == str(n1))

def pode_demorgan(node):
    return node and node.valor == '!' and node.esquerda and node.esquerda.valor in ('&', '|')

def pode_identidade(node):
    if not node or not node.esquerda or not node.direita: return False
    if node.valor == '&':
        return str(node.esquerda) == '1' or str(node.direita) == '1'
    elif node.valor == '|':
        return str(node.esquerda) == '0' or str(node.direita) == '0'
    return False

def pode_nula(node):
    if not node or not node.esquerda or not node.direita: return False
    if node.valor == '&':
        return str(node.esquerda) == '0' or str(node.direita) == '0'
    elif node.valor == '|':
        return str(node.esquerda) == '1' or str(node.direita) == '1'
    return False

def pode_idempotente(node):
    return node and node.valor in ('&', '|') and node.esquerda and node.direita and str(node.esquerda) == str(node.direita)

def pode_inversa(node):
    return node and node.valor in ('&', '|') and node.esquerda and node.direita and sao_inversos(node.esquerda, node.direita)

def pode_absorcao(node):
    if not node or not node.esquerda or not node.direita:
        return False
    #A & (A | B) ou A & (B | A)
    if node.valor == '&' and node.direita and node.direita.valor == '|':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return True
    #(A | B) & A ou (B | A) & A
    if node.valor == '&' and node.esquerda and node.esquerda.valor == '|':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            return True
    #A | (A & B) ou A | (B & A)
    if node.valor == '|' and node.direita and node.direita.valor == '&':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return True
    #(A & B) | A ou (B & A) | A
    if node.valor == '|' and node.esquerda and node.esquerda.valor == '&':
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
    if node.valor == '&' and node.esquerda.valor == '|' and node.direita.valor == '|':
        return _fator_comum(node.esquerda, node.direita) is not None
    if node.valor == '|' and node.esquerda.valor == '&' and node.direita.valor == '&':
        return _fator_comum(node.esquerda, node.direita) is not None
    return False

def pode_associativa(node):
    if not node: return False
    #(A op B) op C  -> A op (B op C)
    return bool(
        node.valor in ('&', '|')
        and node.esquerda
        and node.esquerda.valor == node.valor
    )

def pode_comutativa(node):
    if not node or not node.esquerda or not node.direita: return False
    #Aplica para ordenar (ex: B * A -> A * B)
    return node.valor in ('&', '|') and chave_ordenacao(node.direita) < chave_ordenacao(node.esquerda)


#------------------ Leis Lógicas -------------------

def demorgan(node):
    inner = node.esquerda
    novo_op = '|' if inner.valor == '&' else '&'
    return OperatorNode(novo_op, [
        OperatorNode('!', [inner.esquerda]),
        OperatorNode('!', [inner.direita]),
    ])

def identidade(node):
    if node.valor == '&':
        return node.direita if str(node.esquerda) == '1' else node.esquerda
    elif node.valor == '|':
        return node.direita if str(node.esquerda) == '0' else node.esquerda

def nula(node):
    return VariableNode('0') if node.valor == '&' else VariableNode('1')

def idempotente(node):
    return node.esquerda

def inversa(node):
    return VariableNode('0') if node.valor == '&' else VariableNode('1')

def absorcao(node):
    #A & (A|B) = A
    if node.valor == '&' and node.direita.valor == '|': return node.esquerda
    #(A|B) & A = A
    if node.valor == '&' and node.esquerda.valor == '|': return node.direita
    #A | (A&B) = A
    if node.valor == '|' and node.direita.valor == '&': return node.esquerda
    #(A&B) | A = A
    if node.valor == '|' and node.esquerda.valor == '&': return node.direita
    #Caso não corresponda, retorna o original (embora a verificação deva impedir isso)
    return node

def distributiva(node):
    #Simplificação: (A|B) & (A|C) -> A | (B&C)
    if node.valor == '&' and node.esquerda.valor == '|' and node.direita.valor == '|':
        factor = _fator_comum(node.esquerda, node.direita)
        if factor:
            common, o1, o2 = factor
            return OperatorNode('|', [common, OperatorNode('&', [o1, o2])])

    #Simplificação dual: (A&B) | (A&C) -> A & (B|C)
    if node.valor == '|' and node.esquerda.valor == '&' and node.direita.valor == '&':
        factor = _fator_comum(node.esquerda, node.direita)
        if factor:
            common, o1, o2 = factor
            return OperatorNode('&', [common, OperatorNode('|', [o1, o2])])

    return node #Retorna o nó original se nenhuma regra aplicou

def associativa(node):
    op = node.valor
    #(A op B) op C -> A op (B op C)
    if node.esquerda.valor == op:
        a, b, c = node.esquerda.esquerda, node.esquerda.direita, node.direita
        return OperatorNode(op, [a, OperatorNode(op, [b, c])])
    #A op (B op C) -> (A op B) op C
    elif node.direita.valor == op:
        a, b, c = node.esquerda, node.direita.esquerda, node.direita.direita
        return OperatorNode(op, [OperatorNode(op, [a, b]), c])
    return node

def comutativa(node):
    return OperatorNode(node.valor, [node.direita, node.esquerda])


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


def reiniciar_busca():
    """
    Sem efeito. A busca do próximo passo deixou de manter um cursor global
    (que seria compartilhado entre alunos num servidor web); a função fica
    por compatibilidade com quem ainda a chama.
    """

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
    """
    Próxima subexpressão a analisar: a menor (em tamanho, depois em texto)
    que não esteja entre as ignoradas. `nos_a_ignorar` identifica INSTÂNCIAS:
    um set[int] com id() dos nós (regra de igualdade estrutural). Função pura,
    sem cursor global.
    """
    ignorados = {item if isinstance(item, int) else id(item) for item in (nos_a_ignorar or ())}
    candidatos = [
        info for info in _coletar_todos_os_nos(arvore_raiz)
        if id(info['no_atual']) not in ignorados
    ]
    # O desempate usa o texto no estilo booleano, como a interface sempre mostrou
    candidatos.sort(key=lambda x: (tree_size(x['no_atual']), formatar(x['no_atual'])))
    return candidatos[0] if candidatos else None


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
            formatar(no_alvo),
            formatar(novo_no),
        )
        return arvore_raiz, False

    if pai is None:
        #A raiz da árvore foi substituída
        return novo_no, True

    if ramo == 'esquerda':
        pai.esquerda = novo_no
    elif ramo == 'direita':
        pai.direita = novo_no

    #Retorna a raiz original, que agora aponta para a árvore modificada
    return arvore_raiz, True
