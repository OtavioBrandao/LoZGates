class Conversorlogical:
    def __init__(self):
        """Inicializa o conversor com mapeamentos de operadores"""
        self.logical_operators = {
            '&': '*',    #AND
            '|': '+',    #OR  
            '!': '~',    #NOT
        }
        
        #Histórico de conversões para debug
        self.history = []
    
    def erase_expression(self, expression): 
        """Remove espaços e normaliza a expressão"""
        return expression.replace(" ", "").strip()
    
    def find_left_operand(self, expr, pos):
        """Encontra o operando à esquerda de uma posição"""
        j = pos - 1
        
        #Se termina com ')', encontra a expressão completa entre parênteses
        if j >= 0 and expr[j] == ')':
            count = 1
            j -= 1
            while j >= 0 and count > 0:
                if expr[j] == ')':
                    count += 1
                elif expr[j] == '(':
                    count -= 1
                j -= 1
            return expr[j+1:pos], j+1
        else:
            #Operando simples (variável ou negação)
            start = j
            #Inclui negação se houver
            if j > 0 and expr[j-1] in ['!', '~']:
                start = j - 1
            return expr[start:pos], start
    
    def find_right_operand(self, expr, pos):
        """Encontra o operando à direita de uma posição"""
        k = pos
        
        #Se começa com '(', encontra a expressão completa entre parênteses
        if k < len(expr) and expr[k] == '(':
            count = 1
            k += 1
            start = k
            while k < len(expr) and count > 0:
                if expr[k] == '(':
                    count += 1
                elif expr[k] == ')':
                    count -= 1
                k += 1
            return expr[start:k-1], k
        else:
            #Operando simples ou com negação
            start = k
            if k < len(expr) and expr[k] in ['!', '~']:
                k += 1
            if k < len(expr):
                k += 1
            return expr[start:k], k
    
    def replace_bi_implications(self, expr):
        """
            Converte bi-implicações (A <-> B) para ((~A + B) * (~B + A))
            Suporta tanto '<->' quanto '<>'
        """
        original_expr = expr
        i = 0
        
        while i < len(expr):
            #Verifica '<->' ou '<>'
            if (i + 2 < len(expr) and expr[i:i+3] == '<->') or \
               (i + 1 < len(expr) and expr[i:i+2] == '<>'):
                
                op_size = 3 if expr[i:i+3] == '<->' else 2
                
                #Encontra operando esquerdo
                a, a_start = self.find_left_operand(expr, i)
                
                #Encontra operando direito
                b, b_end = self.find_right_operand(expr, i + op_size)
                
                #A <-> B = ((~A + B) * (~B + A))
                new_expr = (expr[:a_start] + 
                           f"((~{a}+{b})*(~{b}+{a}))" + 
                           expr[b_end:])
                
                self.history.append(f"Bi-implicação: {expr} -> {new_expr}")
                return self.replace_bi_implications(new_expr)
            
            i += 1
        
        return expr
    
    def replace_implications(self, expr):
        """
            Converte implicações (A -> B) para (~A + B)
            Suporta tanto '->' quanto '>'
        """
        i = 0
        
        while i < len(expr):
            #Verifica '->' ou '>'
            if (i + 1 < len(expr) and expr[i:i+2] == '->') or \
               (expr[i] == '>' and (i == 0 or expr[i-1] not in '<')):
                
                op_size = 2 if expr[i:i+2] == '->' else 1
                
                #Encontra operando esquerdo
                a, a_start = self.find_left_operand(expr, i)
                
                #Encontra operando direito  
                b, b_end = self.find_right_operand(expr, i + op_size)
                
                #A -> B = (~A + B)
                new_expr = (expr[:a_start] + 
                           f"(~{a}+{b})" + 
                           expr[b_end:])
                
                self.history.append(f"Implicação: {expr} -> {new_expr}")
                return self.replace_implications(new_expr)
            
            i += 1
        
        return expr
    
    def replace_basic_operators(self, expr):
        """Substitui operadores lógicos básicos por símbolos algébricos"""
        original_expr = expr
        
        for logical, algebraic in self.logical_operators.items():
            if logical in expr:
                expr = expr.replace(logical, algebraic)
        
        if expr != original_expr:
            self.history.append(f"Operadores básicos: {original_expr} -> {expr}")
        
        return expr
    
    def optimize_parentheses(self, expr):
        """Remove parênteses desnecessários (opcional)"""
        #Implementação simples - pode ser expandida
        return expr
    
    def convert_to_boolean_algebra(self, expression, show_steps=False):
        """Converte uma expressão de lógica proposicional para álgebra booleana"""
        self.history = []  #Reset do histórico
        
        #Limpa a expressão
        expr = self.erase_expression(expression)
        self.history.append(f"Original: {expression}")
        
        if expr != expression.replace(" ", ""):
            self.history.append(f"Limpa: {expr}")
        
        #Converte operadores compostos primeiro
        expr = self.replace_bi_implications(expr)
        expr = self.replace_implications(expr)
        
        #Converte operadores básicos
        expr = self.replace_basic_operators(expr)
        
        #Otimizações (se necessário)
        expr = self.optimize_parentheses(expr)
        
        #Mostra passos se solicitado
        if show_steps:
            self.show_history()
        
        return expr
    
    def show_history(self):
        """Mostra o histórico de conversões"""
        print("=== Passos da Conversão ===")
        for i, step in enumerate(self.history, 1):
            print(f"{i}. {step}")
        print("=" * 28)
    
    def validate_expression(self, expression):
        """Valida se a expressão tem parênteses balanceados"""
        count = 0
        for i, char in enumerate(expression):
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count < 0:
                    return False, f"Parêntese fechado sem abertura na posição {i}"
        
        if count != 0:
            return False, f"Parênteses não balanceados: {count} abertos não fechados"
        
        return True, ""
    
    def convert_batch(self, expressions):
        """Converte múltiplas expressões de uma vez"""
        results = {}
        
        for expr in expressions:
            valid, error = self.validate_expression(expr)
            if valid:
                results[expr] = self.convert_to_boolean_algebra(expr)
            else:
                results[expr] = f"ERRO: {error}"
        
        return results

#Função para compatibilidade, para nao mudar chamadas externas
def converter_para_algebra_booleana(expression):
    """Função de compatibilidade"""
    conversor = Conversorlogical()
    return conversor.convert_to_boolean_algebra(expression)