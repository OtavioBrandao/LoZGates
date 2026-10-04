import copy
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.core.expression_ast import (
    OperatorNode,
    VariableNode,
    no_no_caminho,
    parse,
    to_string_com_trechos,
)
from BackEnd.simplificador_interativo import (
    MAX_SIMPLIFICATION_STEPS,
    SimplificationGuard,
    calcular_complexidade,
)


logger = logging.getLogger(__name__)

# Nome mantido por compatibilidade: é o próprio parser canônico.
construir_arvore = parse

# ------------------ Leis Lógicas (retornam o nó modificado) -------------------
# As leis são funções puras: não imprimem nada. Quem anuncia o passo aplicado
# é o laço de simplificação, e só quando a redução é aceita.

def sao_inversos(n1, n2):
    if not n1 or not n2:
        return False
    return (n1.valor == '!' and str(n1.esquerda) == str(n2)) or \
           (n2.valor == '!' and str(n2.esquerda) == str(n1))

def demorgan(node):
    #!(A & B) = !A | !B  e  !(A | B) = !A & !B
    if node.valor == '!' and node.esquerda and node.esquerda.valor in ('&', '|'):
        inner = node.esquerda
        novo_op = '|' if inner.valor == '&' else '&'
        return OperatorNode(novo_op, [
            OperatorNode('!', [inner.esquerda]),
            OperatorNode('!', [inner.direita]),
        ])
    return node

def identidade(node):
    #A & 1 = A  e  A | 0 = A
    if node.valor == '&':
        if str(node.esquerda) == '1':
            return node.direita
        if str(node.direita) == '1':
            return node.esquerda
    elif node.valor == '|':
        if str(node.esquerda) == '0':
            return node.direita
        if str(node.direita) == '0':
            return node.esquerda
    return node

def nula(node):
    #A & 0 = 0  e  A | 1 = 1
    if node.valor == '&':
        if str(node.esquerda) == '0' or str(node.direita) == '0':
            return VariableNode('0')
    elif node.valor == '|':
        if str(node.esquerda) == '1' or str(node.direita) == '1':
            return VariableNode('1')
    return node

def idempotente(node):
    #A & A = A  e  A | A = A
    if node.valor in ('&', '|') and str(node.esquerda) == str(node.direita):
        return node.esquerda
    return node

def inversa(node):
    #A & !A = 0  e  A | !A = 1
    if node.esquerda and node.direita and sao_inversos(node.esquerda, node.direita):
        if node.valor == '&':
            return VariableNode('0')
        if node.valor == '|':
            return VariableNode('1')
    return node

def absorcao(node):
    #A & (A | B) = A  e  A | (A & B) = A
    if node.valor == '&' and node.direita and node.direita.valor == '|':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return node.esquerda
    if node.valor == '&' and node.esquerda and node.esquerda.valor == '|':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            return node.direita
    if node.valor == '|' and node.direita and node.direita.valor == '&':
        if str(node.esquerda) == str(node.direita.esquerda) or str(node.esquerda) == str(node.direita.direita):
            return node.esquerda
    if node.valor == '|' and node.esquerda and node.esquerda.valor == '&':
        if str(node.direita) == str(node.esquerda.esquerda) or str(node.direita) == str(node.esquerda.direita):
            return node.direita
    return node

def associativa(node):
    #(A | B) | C = A | (B | C) e (A & B) & C = A & (B & C)
    if node.valor in ('&', '|') and node.esquerda and node.esquerda.valor == node.valor:
        op = node.valor
        a = node.esquerda.esquerda
        b = node.esquerda.direita
        c = node.direita
        return OperatorNode(op, [a, OperatorNode(op, [b, c])])
    return node

def comutativa(node):
    if node.valor in ('&', '|'):
        if node.esquerda and node.direita and str(node.direita) < str(node.esquerda):
            return OperatorNode(node.valor, [node.direita, node.esquerda])
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
            return OperatorNode('|', [common, OperatorNode('&', [o1, o2])])

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
            return OperatorNode('&', [common, OperatorNode('|', [o1, o2])])
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


@dataclass(frozen=True)
class _Reducao:
    lei: str
    caminho: Tuple[int, ...]      # onde a lei foi aplicada, em índices de `children`
    antes: str
    depois: str


def _aplicar_primeira_reducao(node, caminho=(), anunciar=True):
    """Aplica no máximo uma lei que reduza de verdade, visitando os filhos primeiro."""
    if node is None:
        return node, False, None

    if node.esquerda:
        new_left, changed, reducao = _aplicar_primeira_reducao(node.esquerda, caminho + (0,), anunciar)
        if changed:
            node.esquerda = new_left
            return node, True, reducao
    if node.direita:
        new_right, changed, reducao = _aplicar_primeira_reducao(node.direita, caminho + (1,), anunciar)
        if changed:
            node.direita = new_right
            return node, True, reducao

    original_complexity = calcular_complexidade(node)
    for law_name, law in LEIS_AUTOMATICAS:
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
        if anunciar:
            print(f"Aplicando {law_name} em '{node}' -> '{candidate}'\n")
        return candidate, True, _Reducao(law_name, caminho, str(node), str(candidate))

    return node, False, None


def aplicar_leis_recursivo(node):
    """Compatibility helper: perform one safe reducing traversal."""
    candidate, _, _ = _aplicar_primeira_reducao(copy.deepcopy(node))
    return candidate


@dataclass(frozen=True)
class PassoSimplificacao:
    iteracao: int
    lei: str
    caminho: Tuple[int, ...]
    subexpressao_antes: str
    subexpressao_depois: str
    expressao_antes: str
    expressao_depois: str
    trecho_antes: Tuple[int, int]     # onde a subexpressão está em expressao_antes
    trecho_depois: Tuple[int, int]    # onde o resultado está em expressao_depois


@dataclass
class ResultadoSimplificacao:
    expressao_original: str
    expressao_booleana: str
    expressao_inicial: str
    expressao_final: str
    motivo_parada: str
    passos: List[PassoSimplificacao] = field(default_factory=list)


def _registrar_passo(passos, iteracao, reducao, arvore_antes, arvore_depois):
    texto_antes, trechos_antes = to_string_com_trechos(arvore_antes)
    texto_depois, trechos_depois = to_string_com_trechos(arvore_depois)
    passos.append(PassoSimplificacao(
        iteracao=iteracao,
        lei=reducao.lei,
        caminho=reducao.caminho,
        subexpressao_antes=reducao.antes,
        subexpressao_depois=reducao.depois,
        expressao_antes=texto_antes,
        expressao_depois=texto_depois,
        trecho_antes=trechos_antes[id(no_no_caminho(arvore_antes, reducao.caminho))],
        trecho_depois=trechos_depois[id(no_no_caminho(arvore_depois, reducao.caminho))],
    ))


def _simplificar(arvore, max_steps, anunciar, passos):
    """Núcleo comum: devolve (árvore final, motivo da parada)."""
    if anunciar:
        print("--- Iniciando Simplificação ---")
    logger.info("simplification started: expression=%s", arvore)
    guard = SimplificationGuard(arvore, max_steps=max_steps)

    for passo in range(1, guard.max_steps + 1):
        expressao_anterior = str(arvore)
        if anunciar:
            print(f"\nIteração {passo}: tentando simplificar {expressao_anterior}")
        candidate, changed, reducao = _aplicar_primeira_reducao(copy.deepcopy(arvore), anunciar=anunciar)

        if not changed:
            if anunciar:
                print("\nNenhuma outra simplificação foi possível.")
            logger.info(
                "no further simplification: expression=%s steps=%s",
                arvore,
                guard.accepted_steps,
            )
            return arvore, "no_further_simplification"

        decision = guard.consider(candidate)
        if not decision.accepted:
            if decision.reason == "repeated_state":
                if anunciar:
                    print("\nEstado equivalente já visitado; simplificação encerrada.")
                logger.warning(
                    "repeated state detected: expression=%s step=%s",
                    candidate,
                    passo,
                )
            elif decision.reason == "maximum_steps":
                if anunciar:
                    print("\nLimite de segurança atingido; mantendo a última expressão válida.")
                logger.warning(
                    "maximum steps reached: expression=%s limit=%s",
                    arvore,
                    guard.max_steps,
                )
            else:
                if anunciar:
                    print("\nA transformação não reduziu a complexidade; simplificação encerrada.")
                logger.warning(
                    "simplification stopped without progress: before=%s candidate=%s",
                    arvore,
                    candidate,
                )
            return arvore, decision.reason

        if passos is not None:
            _registrar_passo(passos, passo, reducao, arvore, candidate)
        arvore = candidate
        logger.info(
            "rule applied: rule=%s step=%s complexity=%s expression=%s",
            reducao.lei,
            passo,
            calcular_complexidade(arvore),
            arvore,
        )
        if anunciar:
            print(f"Árvore intermediária: {arvore}")

        if not arvore.esquerda and not arvore.direita:
            logger.info(
                "simplification completed: expression=%s steps=%s",
                arvore,
                guard.accepted_steps,
            )
            return arvore, "completed"

    logger.warning(
        "maximum steps reached: expression=%s limit=%s",
        arvore,
        guard.max_steps,
    )
    if anunciar:
        print("\nLimite de segurança atingido; mantendo a última expressão válida.")

    return arvore, "maximum_steps"


def simplificar(arvore, max_steps=MAX_SIMPLIFICATION_STEPS):
    """Simplify finitely, keeping the last accepted expression."""
    return _simplificar(arvore, max_steps, anunciar=True, passos=None)[0]


def simplificar_expressao(expressao_usuario, max_steps=MAX_SIMPLIFICATION_STEPS) -> ResultadoSimplificacao:
    """
    Fluxo completo do "Simplificar — Resultado", sem imprimir nada: converte
    para álgebra booleana (como a interface sempre fez) e simplifica,
    devolvendo cada passo aceito. Erros de sintaxe sobem como
    ExpressaoInvalida.
    """
    booleana = converter_para_algebra_booleana(expressao_usuario)
    logica = booleana.replace("+", "|").replace("*", "&").replace("~", "!")
    arvore = construir_arvore(logica)
    inicial = str(arvore)
    passos: List[PassoSimplificacao] = []
    final, motivo = _simplificar(arvore, max_steps, anunciar=False, passos=passos)
    return ResultadoSimplificacao(
        expressao_original=expressao_usuario,
        expressao_booleana=booleana,
        expressao_inicial=inicial,
        expressao_final=str(final),
        motivo_parada=motivo,
        passos=passos,
    )

# ------------------ Laço Principal de Execução -------------------
def principal_simplificar(expressao_usuario):

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

    except ValueError as e:
        logger.warning("simplification rejected: expression=%s error=%s", expressao_usuario, e)
        print(f"Ocorreu um erro ao processar a expressão: {e}")
        print("Por favor, verifique se a sintaxe está correta (ex: 'P & (Q | !R)').")
        return None

'''
-------------------------casos testes------------------

(!(P|Q)|!P)&P
P&!P&Q

'''
