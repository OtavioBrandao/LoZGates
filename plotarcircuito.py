from graphviz import Digraph

def converter_para_algebra_booleana(expressao):
    resultado = ""  # String para armazenar o resultado

    i = 0
    while i < len(expressao):
        caracter = expressao[i]

        if caracter in 'PQR':
            resultado += caracter  # Adiciona a variável diretamente
        elif caracter == '!':
            if i + 1 < len(expressao) and expressao[i + 1] == '(':
                resultado += "~("  # Negação de expressão complexa
            else:
                resultado += "~"  # Negação de variável
        elif caracter == '&':
            resultado += "*"
        elif caracter == '|':
            resultado += "+"
        elif caracter == '>':
            # Converter A > B para (~A + B)
            if i > 0 and expressao[i - 1] in 'PQR' and i + 1 < len(expressao) and expressao[i + 1] in 'PQR':
                # Remove o último caractere do resultado temporário (variável antes do >)
                resultado = resultado[:-1]
                resultado += f"(~{expressao[i - 1]}+{expressao[i + 1]})"
                i += 1  # Pula a variável após o >
            elif i + 1 < len(expressao) and expressao[i + 1] == '!':
                if i > 0 and expressao[i - 1] in 'PQR' and i + 2 < len(expressao) and expressao[i + 2] in 'PQR':
                    resultado = resultado[:-1]  # Remove o último caractere do resultado temporário
                    resultado += f"(~{expressao[i - 1]}+~{expressao[i + 2]})"
                    i += 2  # Pula a variável após o !
            elif i + 1 < len(expressao) and expressao[i + 1] == '(':
                if i + 2 < len(expressao) and expressao[i + 2] in 'PQR':
                    resultado = resultado[:-1]  # Remove o último caractere do resultado temporário
                    resultado += f"{expressao[i - 1]}+({expressao[i + 2]}"
                    i += 2  # Pula a variável após o >
        elif caracter in '()':
            resultado += caracter  # Adiciona parênteses diretamente

        i += 1

    print("Expressão em Álgebra Booleana:", resultado)
    return resultado

def plotar_circuito_logico(expressao_booleana):
    dot = Digraph()

    # Dicionário para associar operações a seus tipos de porta
    operacoes = {'~': 'NOT', '*': 'AND', '+': 'OR'}

    # Variáveis para rastrear nós e operandos
    node_count = 0
    operandos = []

    # Função auxiliar para criar um nó de variável ou operação
    def criar_nodo(label):
        nonlocal node_count
        node_id = f"node{node_count}"
        dot.node(node_id, label)
        node_count += 1
        return node_id

    # Função para adicionar operações (NOT, AND, OR)
    def adicionar_operacao(operacao, operandos):
        if operacao == 'NOT':
            not_node = criar_nodo("NOT")
            if operandos[0]:
                dot.edge(operandos[0], not_node) # Adiciona a aresta do operando para o nó NOT!!!(Lari)
            return not_node
        elif operacao == 'AND':
            and_node = criar_nodo("AND")
            for operando in operandos:
                if operando:
                    dot.edge(operando, and_node)
            return and_node
        elif operacao == 'OR':
            or_node = criar_nodo("OR")
            for operando in operandos:
                if operando:
                    dot.edge(operando, or_node)
            return or_node

    # Percorrer a expressão booleana e construir o circuito lógico
    i = 0
    while i < len(expressao_booleana):
        caracter = expressao_booleana[i]

        if caracter in 'PQR':
            operandos.append(criar_nodo(caracter))
        elif caracter in operacoes:
            operacao = operacoes[caracter]
            if operacao == 'NOT':
                operando_atual = operandos.pop() if operandos else None
                novo_nodo = adicionar_operacao(operacao, [operando_atual])
                operandos.append(novo_nodo)
            else:
                # Garante que dois operandos são usados para operações binárias como AND e OR
                operando2 = operandos.pop() if operandos else None
                operando1 = operandos.pop() if operandos else None
                novo_nodo = adicionar_operacao(operacao, [operando1, operando2])
                operandos.append(novo_nodo)

        i += 1

    # Renderizar o diagrama em uma imagem
    dot.render('circuito_logico_booleana', format='png', cleanup=True)
    print("Circuito lógico salvo como 'circuito_logico_booleana.png'.")

# Exemplo de uso
expressao = input("Digite uma expressão proposicional (ex: P&Q|R):\n")
expressao_booleana = converter_para_algebra_booleana(expressao)
plotar_circuito_logico(expressao_booleana)
