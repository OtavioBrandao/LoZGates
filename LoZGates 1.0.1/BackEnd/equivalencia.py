import re
from itertools import product

class UniversalLogicAnalyzer:
    def __init__(self):
        self.operators = {
            '&': lambda a, b: a and b,
            '|': lambda a, b: a or b,
            '>': lambda a, b: (not a) or b,
            '<>': lambda a, b: a == b,
            '=': lambda a, b: a == b,
            '!': lambda a: not a
        }
    
    def extract_variables(self, *expressions):
        all_vars = set()
        
        for expr in expressions:
            #Remove espaços e encontra todas as (variáveis)
            clean_expr = expr.replace(' ', '')
            variables = re.findall(r'[A-Z]', clean_expr)
            all_vars.update(variables)
        
        #Retorna ordenado para consistência
        return sorted(list(all_vars))
    
    def tokenize(self, expression): #Converte string em tokens para análise mais simples
        tokens = []
        i = 0
        expression = expression.replace(' ', '')  #Remove espaços
        
        while i < len(expression):
            if expression[i:i+2] == '<>':
                tokens.append('<>')
                i += 2
            elif expression[i:i+2] == '->':
                tokens.append('>')  #Converte -> para >
                i += 2
            elif expression[i] in '()&|>!=':
                tokens.append(expression[i])
                i += 1
            elif expression[i].isalpha():  #Variável (qualquer letra)
                tokens.append(expression[i])
                i += 1
            elif expression[i].isdigit():  #Números (0, 1)
                tokens.append(expression[i])
                i += 1
            else:
                i += 1
        
        return tokens
    
    def evaluate_expression(self, tokens, values):
        if not tokens:
            return False
            
        if len(tokens) == 1:
            return self.evaluate_token(tokens[0], values)
        
        #Processa parênteses primeiro
        while '(' in tokens:
            tokens = self.process_parentheses(tokens, values)
        
        #Processa negação
        tokens = self.process_negation(tokens, values)
        
        #Processa operadores binários por precedência
        #Ordem: <> (bi-implicação), > (implicação), & (AND), | (OR)
        for op in ['<>', '>', '&', '|']:
            tokens = self.process_operator(tokens, op, values)
        
        return tokens[0] if isinstance(tokens[0], bool) else self.evaluate_token(tokens[0], values)
    
    def evaluate_token(self, token, values):
        if isinstance(token, bool):
            return token
        elif token == '1':
            return True
        elif token == '0':
            return False
        elif token in values:
            return values[token]
        else:
            print(f"AVISO: Variável '{token}' não encontrada, assumindo False")
            return False
    
    def process_parentheses(self, tokens, values):
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
        result = self.evaluate_expression(sub_tokens, values)
        
        return tokens[:start] + [result] + tokens[end:]
    
    def process_negation(self, tokens, values):
        result = []
        i = 0
        
        while i < len(tokens):
            if tokens[i] == '!' and i + 1 < len(tokens):
                value = self.evaluate_token(tokens[i+1], values)
                result.append(not value)
                i += 2
            else:
                result.append(tokens[i])
                i += 1
        
        return result
    
    def process_operator(self, tokens, operator, values):
        #Para implicação, processa da direita para esquerda
        if operator == '>':
            indices = [i for i, token in enumerate(tokens) if token == operator]
            for idx in reversed(indices):
                left = self.evaluate_token(tokens[idx-1], values)
                right = self.evaluate_token(tokens[idx+1], values)
                result = self.operators[operator](left, right)
                tokens = tokens[:idx-1] + [result] + tokens[idx+2:]
        else:
            #Outros operadores da esquerda para direita
            while operator in tokens:
                idx = tokens.index(operator)
                left = self.evaluate_token(tokens[idx-1], values)
                right = self.evaluate_token(tokens[idx+1], values)
                result = self.operators[operator](left, right)
                tokens = tokens[:idx-1] + [result] + tokens[idx+2:]
        
        return tokens
    
    def analyze_expression(self, expression, values):
        tokens = self.tokenize(expression)
        return self.evaluate_expression(tokens, values)


def check_universal_equivalence(expr1, expr2, debug=False):
    analyzer = UniversalLogicAnalyzer()    
    variables = analyzer.extract_variables(expr1, expr2)         #Extrai automaticamente todas as variáveis únicas
    
    if debug:
        print(f"🔍 Analisando equivalência:")
        print(f"   Expressão 1: {expr1}")
        print(f"   Expressão 2: {expr2}")
        print(f"   Variáveis detectadas: {variables}")
        print(f"   Total de combinações: {2**len(variables)}")
        print()
    
    combinations = list(product([False, True], repeat=len(variables))) #Gera todas as combinações possíveis
    
    differences = []
    
    for combination in combinations:
        values = dict(zip(variables, combination))
        
        try:
            result1 = analyzer.analyze_expression(expr1, values)
            result2 = analyzer.analyze_expression(expr2, values)
            
            if result1 != result2:
                differences.append({
                    'values': values.copy(),
                    'result1': result1,
                    'result2': result2
                })
                
                if debug:
                    print(f"❌ Diferença encontrada: {values}")
                    print(f"   {expr1} = {result1}")
                    print(f"   {expr2} = {result2}")
        
        except Exception as e:
            print(f"❌ Erro ao analisar {values}: {e}")
            return False
    
    if differences:
        if debug:
            print(f"\n📊 Resultado: NÃO EQUIVALENTES")
            print(f"   Diferenças encontradas: {len(differences)}")
        return False
    else:
        if debug:
            print(f"✅ Resultado: EQUIVALENTES")
        return True


def generate_universal_truth_table(expression, debug=False):
    analyzer = UniversalLogicAnalyzer()
    variables = analyzer.extract_variables(expression)
    combinations = list(product([False, True], repeat=len(variables)))
    
    print(f"\n📊 Tabela Verdade para: {expression}")
    print(f"🔢 Variáveis: {', '.join(variables)}")
    print(f"📈 Combinações: {len(combinations)}")
    print()
    
    #Cabeçalho
    header = " | ".join(variables + ["Resultado"])
    print(header)
    print("-" * len(header))
    
    #Linhas da tabela
    for combination in combinations:
        values = dict(zip(variables, combination))
        
        try:
            result = analyzer.analyze_expression(expression, values)
            line_values = [str(int(v)) for v in combination] + [str(int(result))]
            print(" | ".join(f"{v:^{len(var)}}" for v, var in zip(line_values, variables + ["Resultado"])))
            
        except Exception as e:
            if debug:
                print(f"Erro na combinação {values}: {e}")


#Função compatível com código original
def tabela(sentence1, sentence2):
    return 1 if check_universal_equivalence(sentence1, sentence2) else 2