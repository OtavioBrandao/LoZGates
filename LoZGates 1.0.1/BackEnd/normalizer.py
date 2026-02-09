class ExprNode:
    #Nó de uma árvore de expressão lógica
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
    
    def __eq__(self, other):
        if not isinstance(other, ExprNode):
            return False
        return (self.value == other.value and 
                self.left == other.left and 
                self.right == other.right)
    
    def __str__(self):
        if self.value in ('&', '|', '*', '+', '>', '<>'):
            return f"({self.left}{self.value}{self.right})"
        elif self.value in ('!', '~'):
            return f"{self.value}{self.left}"
        else:
            return str(self.value)


def build_expression_tree(expr):
    #Constrói árvore de expressão respeitando precedência:
  
    expr = expr.replace(" ", "").upper()
    
    #Normaliza operadores
    expr = expr.replace("->", ">").replace("<->", "<>")
    expr = expr.replace("*", "&").replace("+", "|")
    expr = expr.replace("~", "!")
    
    def parse_bi_implication(s):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ')': depth += 1
            elif s[i] == '(': depth -= 1
            elif depth == 0 and i > 0 and s[i-1:i+1] == '<>':
                return ExprNode('<>', parse_bi_implication(s[:i-1]), parse_implication(s[i+1:]))
        return parse_implication(s)
    
    def parse_implication(s):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ')': depth += 1
            elif s[i] == '(': depth -= 1
            elif s[i] == '>' and depth == 0:
                return ExprNode('>', parse_implication(s[:i]), parse_or(s[i+1:]))
        return parse_or(s)
    
    def parse_or(s):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ')': depth += 1
            elif s[i] == '(': depth -= 1
            elif s[i] == '|' and depth == 0:
                return ExprNode('|', parse_or(s[:i]), parse_and(s[i+1:]))
        return parse_and(s)
    
    def parse_and(s):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ')': depth += 1
            elif s[i] == '(': depth -= 1
            elif s[i] == '&' and depth == 0:
                return ExprNode('&', parse_and(s[:i]), parse_not(s[i+1:]))
        return parse_not(s)
    
    def parse_not(s):
        if s.startswith('!'):
            return ExprNode('!', parse_not(s[1:]))
        elif s.startswith('(') and s.endswith(')'):
            return parse_bi_implication(s[1:-1])
        else:
            return ExprNode(s)
    
    return parse_bi_implication(expr)


def normalize_tree_variables(tree, var_map=None, counter=None):
    #Normaliza variáveis na árvore para A, B, C... mantendo estrutura
    if var_map is None:
        var_map = {}
    if counter is None:
        counter = [0]
    
    if tree.left is None and tree.right is None:  #Folha (variável)
        if tree.value not in var_map and tree.value.isalpha():
            var_map[tree.value] = chr(65 + counter[0])
            counter[0] += 1
        
        if tree.value in var_map:
            return ExprNode(var_map[tree.value])
        return tree
    
    #Nó interno (operador)
    left_normalized = normalize_tree_variables(tree.left, var_map, counter) if tree.left else None
    right_normalized = normalize_tree_variables(tree.right, var_map, counter) if tree.right else None
    
    return ExprNode(tree.value, left_normalized, right_normalized)


def normalize_for_comparison(expression):
    #Normaliza expressão para comparação estrutural.
    """
    Exemplos:
    - "(A&B)&C" -> "A&B&C"  (redundante)
    - "A&(B&C)" -> "A&B&C" (redundante)
    - "(A>B)|C" -> "(A>B)|C" (parênteses ESSENCIAIS - mantém)
    - "X&Y" -> "A&B" (normaliza variáveis)
    """
    try:
        #Constrói árvore
        tree = build_expression_tree(expression)
        
        #Normaliza variáveis
        normalized_tree = normalize_tree_variables(tree)
        
        #Converte de volta para string
        return tree_to_canonical_string(normalized_tree)
    
    except Exception as e:
        print(f"⚠️ Erro ao normalizar '{expression}': {e}")
        #Fallback para normalização simples
        return simple_normalize(expression)


def tree_to_canonical_string(tree):
    #Arvore para string
    if tree.left is None and tree.right is None:
        return tree.value
    
    if tree.value == '!':
        operand = tree_to_canonical_string(tree.left)
        #Adiciona parênteses se operando for uma operação binária
        if tree.left.value in ('&', '|', '>', '<>'):
            operand = f"({operand})"
        return f"!{operand}"
    
    #Operadores binários
    left_str = tree_to_canonical_string(tree.left)
    right_str = tree_to_canonical_string(tree.right)
    
    #Precedências (menor número = maior precedência)
    precedence = {'&': 1, '|': 2, '>': 3, '<>': 4}
    current_prec = precedence.get(tree.value, 999)
    
    #Adiciona parênteses à esquerda se necessário
    if tree.left.value in precedence:
        left_prec = precedence[tree.left.value]
        if left_prec > current_prec:
            left_str = f"({left_str})"
    
    #Adiciona parênteses à direita se necessário
    if tree.right.value in precedence:
        right_prec = precedence[tree.right.value]
        if right_prec > current_prec:
            right_str = f"({right_str})"
        #Para associatividade à direita (implicação)
        elif tree.value == '>' and right_prec == current_prec:
            right_str = f"({right_str})"
    
    return f"{left_str}{tree.value}{right_str}"


def simple_normalize(expression):
    #Normalização simples como fallback
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
    try:
        norm1 = normalize_for_comparison(expr1)
        norm2 = normalize_for_comparison(expr2)
        
        print(f"🔄 Comparação estrutural:")
        print(f"   '{expr1}' → '{norm1}'")
        print(f"   '{expr2}' → '{norm2}'")
        
        return norm1 == norm2
    
    except Exception as e:
        print(f"⚠️ Erro na comparação: {e}")
        #Fallback: compara árvores diretamente
        try:
            tree1 = build_expression_tree(expr1)
            tree2 = build_expression_tree(expr2)
            norm_tree1 = normalize_tree_variables(tree1)
            norm_tree2 = normalize_tree_variables(tree2)
            return norm_tree1 == norm_tree2
        except:
            return False