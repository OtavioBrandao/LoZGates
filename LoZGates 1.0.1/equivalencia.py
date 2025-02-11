def analisar(expressao, p, q, r):
    resultado = 0
    i = 0
    tamanho = len(expressao)
    
    while i < tamanho:
        caracter = expressao[i]
        
        if caracter == '1':
            resultado = 1
        elif caracter == '0':
            resultado = 0
        elif caracter == 'P':
            resultado = p
        elif caracter == 'Q':
            resultado = q
        elif caracter == 'R':
            resultado = r
        elif caracter == '!':
            i += 1
            if expressao[i] == 'P':
                resultado = not p
            elif expressao[i] == 'Q':
                resultado = not q
            elif expressao[i] == 'R':
                resultado = not r
            elif expressao[i] == '1':
                resultado = 0
            elif expressao[i] == '0':
                resultado = 1
        elif caracter == '&':
            resultado = resultado and analisar(expressao[i+1:], p, q, r)
            break
        elif caracter == '|':
            resultado = resultado or analisar(expressao[i+1:], p, q, r)
            break
        elif caracter == '>':
            resultado = (not resultado) or analisar(expressao[i+1:], p, q, r)
            break
        elif caracter == '(':
            j = i + 1
            cont_parenteses = 1
            while j < tamanho and cont_parenteses > 0:
                if expressao[j] == '(':
                    cont_parenteses += 1
                if expressao[j] == ')':
                    cont_parenteses -= 1
                j += 1
            subexpressao = expressao[i+1:j-1]
            resultado = analisar(subexpressao, p, q, r)
            i = j - 1
        i += 1
    return resultado

def tabela(sentenca, sentenca2):
    PTab = [False, False, False, False, True, True, True, True]
    QTab = [False, False, True, True, False, False, True, True]
    RTab = [False, True, False, True, False, True, False, True]
    
    for i in range(8):
        S1 = analisar(sentenca, PTab[i], QTab[i], RTab[i])
        S2 = analisar(sentenca2, PTab[i], QTab[i], RTab[i])
        if S1 != S2:
            return 2
    return 1