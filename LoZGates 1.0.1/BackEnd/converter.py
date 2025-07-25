def substituir_implicacoes(expr): 
    i = 0
    while i < len(expr):
        if expr[i] == '>':
            #  lado esquerdo 
            j = i - 1
            if expr[j] == ')':
                count = 1
                j -= 1
                while j >= 0 and count > 0:
                    if expr[j] == ')':
                        count += 1
                    elif expr[j] == '(':
                        count -= 1
                    j -= 1
                a = expr[j+1:i]
                a_start = j+1
            else:
                a = expr[j]
                a_start = j

            # lado direito 
            k = i + 1
            if expr[k] == '(':
                count = 1
                k += 1
                start = k
                while k < len(expr) and count > 0:
                    if expr[k] == '(':
                        count += 1
                    elif expr[k] == ')':
                        count -= 1
                    k += 1
                b = expr[start:k-1]
                b_end = k
            else:
                b = expr[k]
                b_end = k + 1

            nova_expr = expr[:a_start] + f"(~{a}+{b})" + expr[b_end:]
            return substituir_implicacoes(nova_expr)  # recursivo para múltiplos >

        i += 1
    return expr

def converter_para_algebra_booleana(expressao):
    expressao = expressao.replace(" ", "")
    expressao = substituir_implicacoes(expressao)
    expressao = expressao.replace("&", "*").replace("|", "+").replace("!", "~")
    
    return expressao
