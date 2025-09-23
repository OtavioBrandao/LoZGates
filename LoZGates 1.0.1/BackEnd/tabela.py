import itertools
from BackEnd.equivalencia import UniversalLogicAnalyzer

def gerar_tabela_verdade(expressao):
    analyzer = UniversalLogicAnalyzer()
    variaveis = sorted(analyzer.extract_variables(expressao)) 
    sub_expressoes = extrair_sub_expressoes(expressao)
    colunas = montar_colunas(variaveis, sub_expressoes, expressao)
    combinacoes = list(itertools.product([False, True], repeat=len(variaveis)))
    
    tabela_completa = []
    resultados_finais = []
    
    for combo in combinacoes:
        valores_linha = dict(zip(variaveis, combo))
        
        #Calcula resultado para cada coluna
        resultados_linha = []
        for coluna in colunas:
            try:
                resultado_bool = analyzer.analyze_expression(coluna, valores_linha)
                resultados_linha.append(int(resultado_bool))
            except Exception as e:
                print(f"Erro ao avaliar '{coluna}' com {valores_linha}: {e}")
                resultados_linha.append(0)  #Valor padrão em caso de erro
        
        tabela_completa.append(resultados_linha)
        
        #Armazena resultado da expressão completa (última coluna)
        if resultados_linha:
            resultados_finais.append(resultados_linha[-1])
    
    return {
        "colunas": colunas,
        "tabela": tabela_completa,
        "resultados_finais": resultados_finais,
        "total_combinacoes": len(combinacoes),
        "total_variaveis": len(variaveis)
    }

def extrair_sub_expressoes(expressao):
    sub_expressoes = set()
    
    for i in range(len(expressao)):
        if expressao[i] == '(':
            contador_parenteses = 1
            for j in range(i + 1, len(expressao)):
                if expressao[j] == '(':
                    contador_parenteses += 1
                elif expressao[j] == ')':
                    contador_parenteses -= 1
                
                #Quando encontra o fechamento correspondente
                if contador_parenteses == 0:
                    sub_expr = expressao[i:j+1]
                    #Só adiciona se não for uma variável simples entre parênteses
                    conteudo = sub_expr[1:-1].strip()
                    if len(conteudo) > 1 or not conteudo.isalpha():
                        sub_expressoes.add(sub_expr)
                    break
    
    return sub_expressoes

def montar_colunas(variaveis, sub_expressoes, expressao_completa):
    colunas = variaveis.copy()
    
    #Adiciona sub-expressões ordenadas por tamanho (complexidade)
    sub_expressoes_ordenadas = sorted(sub_expressoes, key=len)
    colunas.extend(sub_expressoes_ordenadas)
    
    #Adiciona expressão completa se não estiver nas colunas
    if expressao_completa not in colunas:
        colunas.append(expressao_completa)
    
    return colunas

def verificar_conclusao(resultados):
    if not resultados:
        return "Nenhum resultado para analisar."
    
    #Filtra apenas resultados válidos
    resultados_validos = [r for r in resultados if isinstance(r, int) and r in [0, 1]]
    
    if len(resultados_validos) != len(resultados):
        return "Expressão contém erros de avaliação."
    
    #Conta verdadeiros e falsos
    verdadeiros = sum(resultados_validos)
    total = len(resultados_validos)
    
    if verdadeiros == total:
        return f"A expressão é uma TAUTOLOGIA."
    elif verdadeiros == 0:
        return f"A expressão é uma CONTRADIÇÃO."
    else:
        return f"A expressão é SATISFATÍVEL."

def imprimir_tabela_formatada(resultado_tabela):
    colunas = resultado_tabela["colunas"]
    tabela = resultado_tabela["tabela"]
    
    #Calcula largura das colunas
    larguras = [max(len(str(col)), 3) for col in colunas]
    
    #Imprime cabeçalho
    print(" | ".join(f"{col:^{larg}}" for col, larg in zip(colunas, larguras)))
    print("-" * (sum(larguras) + 3 * (len(colunas) - 1)))
    
    #Imprime linhas
    for linha in tabela:
        print(" | ".join(f"{val:^{larg}}" for val, larg in zip(linha, larguras)))