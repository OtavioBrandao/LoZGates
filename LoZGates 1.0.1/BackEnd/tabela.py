import itertools
import logging

from BackEnd.core.expression_ast import avaliar, collect_variables, parse, percorrer


logger = logging.getLogger(__name__)

def gerar_tabela_verdade(expressao):
    arvore = parse(expressao)
    variaveis = sorted(collect_variables(arvore))
    sub_expressoes = extrair_sub_expressoes(expressao, arvore)
    colunas = montar_colunas(variaveis, [texto for texto, _ in sub_expressoes], expressao)

    #Cada coluna é avaliada pelo nó correspondente da árvore
    nos_das_colunas = dict(sub_expressoes)
    nos_das_colunas[expressao] = arvore
    combinacoes = list(itertools.product([False, True], repeat=len(variaveis)))

    tabela_completa = []
    resultados_finais = []

    for combo in combinacoes:
        valores_linha = dict(zip(variaveis, combo))
        resultados_linha = [
            int(valores_linha[coluna]) if coluna in valores_linha
            else int(avaliar(nos_das_colunas[coluna], valores_linha))
            for coluna in colunas
        ]
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

def extrair_sub_expressoes(expressao, arvore=None):
    """
    Grupos entre parênteses que o aluno escreveu, com o texto exatamente como
    foi digitado e o nó que cada um representa. Ordem: tamanho do texto e,
    no empate, posição na expressão. Textos repetidos aparecem uma vez só.
    """
    if arvore is None:
        arvore = parse(expressao)

    grupos = []
    for _, no in percorrer(arvore):
        for inicio, fim in no.parenteses:
            sub_expr = expressao[inicio:fim]
            #Só adiciona se não for uma variável simples entre parênteses
            conteudo = sub_expr[1:-1].strip()
            if len(conteudo) > 1 or not conteudo.isalpha():
                grupos.append((len(sub_expr), inicio, sub_expr, no))

    sub_expressoes = {}
    for _, _, texto, no in sorted(grupos, key=lambda grupo: (grupo[0], grupo[1])):
        sub_expressoes.setdefault(texto, no)
    return list(sub_expressoes.items())

def montar_colunas(variaveis, sub_expressoes, expressao_completa):
    colunas = variaveis.copy()

    #Sub-expressões já vêm ordenadas por tamanho (complexidade)
    colunas.extend(sub_expressoes)

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
