def converter_para_algebra_booleana(expressao):
    resultado = ""  # String para armazenar o resultado
    i = 0

    while i < len(expressao):
        caracter = expressao[i]

        if caracter in 'PQRST':
            resultado += caracter  # Adiciona a variável diretamente
        elif caracter == '!':
            resultado += "~"  # Negação
        elif caracter == '&':
            resultado += "*"  # AND
        elif caracter == '|':
            resultado += "+"  # OR (substitui | por +)
        elif caracter == '>':
  
            # Encontrar A (tudo antes do >)
            a_start = i - 1
            while a_start >= 0 and expressao[a_start] in 'PQRST()!&|':
                a_start -= 1
            a_start += 1
            a_expressao = expressao[a_start:i]

            # Encontrar B (tudo depois do >)
            b_end = i + 1
            while b_end < len(expressao) and expressao[b_end] in 'PQRST()!&|':
                b_end += 1
            b_expressao = expressao[i + 1:b_end]

            # Converter A > B para (~A + B)
            resultado = resultado[:a_start]  # Remove A do resultado temporário
            resultado += f"(~{a_expressao}+{b_expressao})"
            i = b_end - 1  # Atualiza o índice para pular B
        elif caracter in '()':
            resultado += caracter  # Adiciona parênteses diretamente
        i += 1

    # Substituir | por + no resultado final (caso ainda haja algum | restante)
    resultado = resultado.replace("|", "+").replace("&", "*").replace("!", "~")

    return resultado
