import itertools
import re

def avaliar_expressao(expressao, valores_variaveis):
    #Cria uma cópia da expressão para não modificar a original
    expressao_modificada = expressao
    
    #Substitui as variáveis por seus valores numéricos 
    for var, val in valores_variaveis.items():
        #Usa regex para substituir a variável como uma palavra inteira 
        expressao_modificada = re.sub(r'\b' + var + r'\b', str(val), expressao_modificada)

    expressao_modificada = (
        expressao_modificada
        .replace("&", " and ")
        .replace("|", " or ")
        .replace("!", " not ")
        .replace(">", " <= ") 
    )
    
    try:
        #Usa eval para calcular o resultado da string
        return int(eval(expressao_modificada, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Erro: {e}"

def gerar_tabela_verdade(expressao):
    #1. Encontra todas as variáveis únicas 
    variaveis = sorted(list(set(re.findall(r'[A-Z]+', expressao))))
    
    #2. Encontra todas as sub-expressões
    sub_expressoes = set()
    for i in range(len(expressao)):
        if expressao[i] == '(':
            contador_parenteses = 1
            for j in range(i + 1, len(expressao)):
                if expressao[j] == '(':
                    contador_parenteses += 1
                elif expressao[j] == ')':
                    contador_parenteses -= 1
                
                if contador_parenteses == 0:
                    sub_expressoes.add(expressao[i:j+1])
                    break
    
    #3. Monta a lista de colunas da tabela
    colunas = variaveis[:]
    
    todas_as_partes = list(sub_expressoes)
    if expressao not in todas_as_partes:
        todas_as_partes.append(expressao)
        
    todas_as_partes = [p for p in todas_as_partes if p not in variaveis]
    colunas.extend(sorted(todas_as_partes, key=len))

    #4. Gera as combinações e calcula os resultados
    combinacoes = list(itertools.product([0, 1], repeat=len(variaveis)))
    
    tabela_completa = []
    resultados_finais = []

    for combo in combinacoes:
        valores_linha_atual = dict(zip(variaveis, combo))
        
        resultados_linha = []
        for coluna in colunas:
            if coluna in variaveis:
                resultado = valores_linha_atual[coluna]
            else:
                resultado = avaliar_expressao(coluna, valores_linha_atual)
            resultados_linha.append(resultado)
        
        tabela_completa.append(resultados_linha)
        
        #Armazena o resultado da expressão completa
        if resultados_linha:
            resultados_finais.append(resultados_linha[-1])

    #Retorna um dicionário contendo todas as partes necessárias para o front-end
    return {
        "colunas": colunas,
        "tabela": tabela_completa,
        "resultados_finais": resultados_finais
    }
        
def verificar_conclusao(resultados):
    #Garante que não há erros na lista de resultados
    resultados_validos = [r for r in resultados if isinstance(r, int)]
    if len(resultados_validos) != len(resultados):
        return "Expressão contém um erro de avaliação."

    if all(resultados_validos):
        return "A expressão é uma TAUTOLOGIA."
    #Verifica se a lista não é vazia antes de chamar any()
    elif resultados_validos and any(resultados_validos):
        return "A expressão é SATISFATÍVEL."
    else:
        return "A expressão é uma CONTRADIÇÃO."