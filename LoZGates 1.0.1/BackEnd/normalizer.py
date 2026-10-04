import logging

from BackEnd.core.expression_ast import (
    AND,
    IFF,
    IMPLIES,
    NOT,
    OR,
    OperatorNode,
    VariableNode,
    parse,
)


logger = logging.getLogger(__name__)

#Precedências (menor número = maior precedência)
_PRECEDENCIA = {AND: 1, OR: 2, IMPLIES: 3, IFF: 4}


def normalize_tree_variables(tree, var_map=None, counter=None):
    #Normaliza variáveis na árvore para A, B, C... mantendo estrutura (devolve árvore nova)
    if var_map is None:
        var_map = {}
    if counter is None:
        counter = [0]

    if isinstance(tree, VariableNode):
        if tree.eh_constante:
            return VariableNode(tree.name)
        if tree.name not in var_map:
            var_map[tree.name] = chr(65 + counter[0])
            counter[0] += 1
        return VariableNode(var_map[tree.name])

    #Nó interno (operador): filhos da esquerda para a direita
    return OperatorNode(tree.op, [normalize_tree_variables(c, var_map, counter) for c in tree.children])


def normalize_for_comparison(expression):
    #Normaliza expressão para comparação estrutural.
    """
    Exemplos:
    - "(A&B)&C" -> "A&B&C"  (redundante)
    - "A&(B&C)" -> "A&B&C" (redundante)
    - "(A>B)|C" -> "(A>B)|C" (parênteses ESSENCIAIS - mantém)
    - "(A>B)>C" -> "(A>B)>C" e "A>(B>C)" -> "A>B>C" (a implicação associa à direita)
    - "X&Y" -> "A&B" (normaliza variáveis)
    """
    try:
        tree = parse(expression)
    except ValueError:
        logger.warning("Expressão inválida %r; usando normalização simples", expression)
        return simple_normalize(expression)

    return tree_to_canonical_string(normalize_tree_variables(tree))


def _eh_binario(node):
    return isinstance(node, OperatorNode) and node.op in _PRECEDENCIA


def tree_to_canonical_string(tree):
    #Arvore para string, só com os parênteses necessários
    if isinstance(tree, VariableNode):
        return tree.name

    if tree.op == NOT:
        operand = tree_to_canonical_string(tree.children[0])
        #Adiciona parênteses se operando for uma operação binária
        if _eh_binario(tree.children[0]):
            operand = f"({operand})"
        return f"!{operand}"

    #Operadores binários
    esquerda, direita = tree.children
    left_str = tree_to_canonical_string(esquerda)
    right_str = tree_to_canonical_string(direita)
    current_prec = _PRECEDENCIA[tree.op]

    #Adiciona parênteses à esquerda se necessário
    if _eh_binario(esquerda):
        left_prec = _PRECEDENCIA[esquerda.op]
        if left_prec > current_prec:
            left_str = f"({left_str})"
        #A implicação associa à direita: (A>B)>C precisa dos parênteses
        elif tree.op == IMPLIES and esquerda.op == IMPLIES:
            left_str = f"({left_str})"

    #Adiciona parênteses à direita se necessário
    if _eh_binario(direita):
        right_prec = _PRECEDENCIA[direita.op]
        if right_prec > current_prec:
            right_str = f"({right_str})"

    return f"{left_str}{tree.op}{right_str}"


def simple_normalize(expression):
    #Normalização simples como fallback (só para entradas que nem são expressões válidas)
    expr = expression.strip().upper().replace(" ", "")

    variables_found = []
    for char in expr:
        if char.isalpha() and char not in variables_found:
            variables_found.append(char)

    mapping = {}
    for i, var in enumerate(variables_found):
        if i < 26:
            mapping[var] = chr(65 + i)

    normalized = expr
    for original_var in sorted(mapping.keys(), key=len, reverse=True):
        normalized_var = mapping[original_var]
        placeholder = f"§{normalized_var}§"
        normalized = normalized.replace(original_var, placeholder)

    normalized = normalized.replace("§", "")
    return normalized


def expressions_are_structurally_equivalent(expr1, expr2):
    #Verifica se duas expressões têm a mesma estrutura lógica.
    """
    Exemplos:
    - "A&B&C" e "(A&B)&C" → True
    - "X&Y" e "P&Q" → True (mesma estrutura, variáveis diferentes)
    - "(A>B)|C" e "A>(B|C)" → False (estrutura diferente)
    """
    norm1 = normalize_for_comparison(expr1)
    norm2 = normalize_for_comparison(expr2)

    logger.debug("Comparacao estrutural: %r -> %r / %r -> %r", expr1, norm1, expr2, norm2)

    return norm1 == norm2
