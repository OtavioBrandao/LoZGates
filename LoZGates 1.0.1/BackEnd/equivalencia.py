from itertools import product

class analyzerLogico:
    def __init__(self):
        self.operators = {
            '&': lambda a, b: a and b,
            '|': lambda a, b: a or b,
            '>': lambda a, b: (not a) or b,
            '<>': lambda a, b: a == b,  #bi-implicação
            '=': lambda a, b: a == b    #equivalência
        }
    
    def tokenizar(self, expression):
        """Converte string em tokens para análise mais fácil"""
        tokens = []
        i = 0
        while i < len(expression):
            if expression[i] == ' ':
                i += 1
                continue
            elif expression[i:i+2] == '<>':
                tokens.append('<>')
                i += 2
            elif expression[i] in '()&|>!PQR01':
                tokens.append(expression[i])
                i += 1
            else:
                i += 1
        return tokens
    
    def to_analyze_tokenizado(self, tokens, values):
        """Versão melhorada usando tokens"""
        if not tokens:
            return False
            
        result = self._evaluate_expression(tokens, values)
        return result
    
    def _evaluate_expression(self, tokens, values):
        """Avalia expressão com precedência de operators"""
        if len(tokens) == 1:
            return self._evaluate_token(tokens[0], values)
        
        #Processa parênteses primeiro
        while '(' in tokens:
            tokens = self._process_parentheses(tokens, values)
        
        #Processa negação
        tokens = self._process_negacao(tokens, values)
        
        #Processa operators binários (da righteita para leftuerda para >)
        for op in ['<>', '>', '&', '|']:
            tokens = self._process_operator(tokens, op, values)
        
        return tokens[0] if isinstance(tokens[0], bool) else self._evaluate_token(tokens[0], values)
    
    def _evaluate_token(self, token, values):
        """Avalia um token individual"""
        if isinstance(token, bool):
            return token
        elif token == '1':
            return True
        elif token == '0':
            return False
        elif token in values:
            return values[token]
        return False
    
    def _process_parentheses(self, tokens, values):
        """Processa expressões dentro de parênteses"""
        start = tokens.index('(')
        level = 1
        end = start + 1
        
        while end < len(tokens) and level > 0:
            if tokens[end] == '(':
                level += 1
            elif tokens[end] == ')':
                level -= 1
            end += 1
        
        sub_tokens = tokens[start+1:end-1]
        result = self._evaluate_expression(sub_tokens, values)
        
        return tokens[:start] + [result] + tokens[end:]
    
    def _process_negacao(self, tokens, values):
        """Processa operators de negação"""
        i = 0
        result = []
        while i < len(tokens):
            if tokens[i] == '!' and i + 1 < len(tokens):
                value = self._evaluate_token(tokens[i+1], values)
                result.append(not value)
                i += 2
            else:
                result.append(tokens[i])
                i += 1
        return result
    
    def _process_operator(self, tokens, operador, values):
        """Processa um operador específico"""
        while operador in tokens:
            idx = tokens.index(operador)
            left = self._evaluate_token(tokens[idx-1], values)
            right = self._evaluate_token(tokens[idx+1], values)
            result = self.operators[operador](left, right)
            tokens = tokens[:idx-1] + [result] + tokens[idx+2:]
        return tokens
    
    def to_analyze_original(self, expression, values):
        """Mantém compatibilidade com código original"""
        p, q, r = values.get('P', False), values.get('Q', False), values.get('R', False)
        return self.to_analyze(expression, p, q, r)
    
    def to_analyze(self, expression, p, q, r):
        """Versão melhorada do analyzer original"""
        values = {'P': p, 'Q': q, 'R': r}
        tokens = self.tokenizar(expression)
        return self.to_analyze_tokenizado(tokens, values)

def check_equivalence(sentence1, sentence2, variables=['P', 'Q', 'R']):
    """
        Versão melhorada da verificação de equivalência
        Suporta qualquer quantidade de variáveis
    """
    analyzer = analyzerLogico()
    
    #Gera todas as combinações possíveis de values
    combinations = list(product([False, True], repeat=len(variables)))
    
    for combination in combinations:
        values = dict(zip(variables, combination))
        
        try:
            result1 = analyzer.to_analyze_tokenizado(
                analyzer.tokenizar(sentence1), values
            )
            result2 = analyzer.to_analyze_tokenizado(
                analyzer.tokenizar(sentence2), values
            )
            
            if result1 != result2:
                print(f"Diferença encontrada: {values}")
                print(f"  {sentence1} = {result1}")
                print(f"  {sentence2} = {result2}")
                return False
        except Exception as e:
            print(f"Erro ao analisar {values}: {e}")
            return False
    
    return True

def generate_truth_table(expression, variables=['P', 'Q', 'R']):
    """Gera tabela verdade completa para uma expressão"""
    analyzer = analyzerLogico()
    combinations = list(product([False, True], repeat=len(variables)))
    
    print(f"Tabela verdade para: {expression}")
    print(" | ".join(variables + ["resultado"]))
    print("-" * (len(variables) * 4 + 10))
    
    for combination in combinations:
        values = dict(zip(variables, combination))
        try:
            result = analyzer.to_analyze_tokenizado(
                analyzer.tokenizar(expression), values
            )
            linha = " | ".join([str(int(v)) for v in combination] + [str(int(result))])
            print(linha)
        except Exception as e:
            print(f"Erro: {e}")

#Função compatível com código original
def tabela(sentence1, sentence2):
    """Mantém compatibilidade com função original"""
    return 1 if check_equivalence(sentence1, sentence2) else 2