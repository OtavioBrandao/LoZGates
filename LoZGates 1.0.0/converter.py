# Função de conversão para álgebra booleana
def converter_para_algebra_booleana(expressao):
    resultado = ""  # String para armazenar o resultado

    i = 0
    while i < len(expressao):
        caracter = expressao[i]

        if caracter in 'PQRST':
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
            if i > 0 and expressao[i - 1] in 'PQRST' and i + 1 < len(expressao) and expressao[i + 1] in 'PQRST':
                # Remove o último caractere do resultado temporário (variável antes do >)
                resultado = resultado[:-1]
                resultado += f"(~{expressao[i - 1]}+{expressao[i + 1]})"
                i += 1  # Pula a variável após o >
            
            elif i + 1 < len(expressao) and expressao[i + 1] == '!':
                if i > 0 and expressao[i - 1] in 'PQRST' and i + 2 < len(expressao) and expressao[i + 2] in 'PQRST':
                    resultado = resultado[:-1]  # Remove o último caractere do resultado temporário
                    resultado += f"(~{expressao[i - 1]}+~{expressao[i + 2]})"
                    i += 2  # Pula a variável após o !
            
            elif i + 1 < len(expressao) and expressao[i + 1] == '(':
                if i + 2 < len(expressao) and expressao[i + 2] in 'PQRST':
                    resultado = resultado[:-1]  # Remove o último caractere do resultado temporário
                    resultado += f"{expressao[i - 1]}+({expressao[i + 2]}"
                    i += 2  # Pula a variável após o >
        elif caracter in '()':
            resultado += caracter  # Adiciona parênteses diretamente
        i += 1
        #Para printar o resultado no nome do programa
    #titulo = f"Circuito Lógico                                                                 Original: {expressao}    Resultado: {resultado}"
    #print(resultado)
    #pygame.display.set_caption(titulo.center(50))
    return resultado