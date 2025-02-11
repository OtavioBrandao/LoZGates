import itertools

def gerar_tabela_verdade(expressao):
    variaveis = sorted(set(filter(str.isalpha, expressao)))  # Extrai variáveis únicas
    
    def avaliar(expressao, valores):
        expressao_modificada = expressao
        for var, val in zip(variaveis, valores):
            expressao_modificada = expressao_modificada.replace(var, str(int(val)))
        expressao_modificada = (
            expressao_modificada.replace("&", " and ")
            .replace("|", " or ")
            .replace("!", " not ")
            .replace(">", " <= ")
        )
        return eval(expressao_modificada)
    
    combinacoes = list(itertools.product([False, True], repeat=len(variaveis)))
    resultados = [avaliar(expressao, valores) for valores in combinacoes]
    
    # Retorna as combinações e os resultados
    return variaveis, combinacoes, resultados

def verificar_conclusao(resultados):
    if all(resultados):
        return "A expressão é uma TAUTOLOGIA."
    elif any(resultados):
        return "A expressão é SATISFATÍVEL."
    else:
        return "A expressão é uma CONTRADIÇÃO."