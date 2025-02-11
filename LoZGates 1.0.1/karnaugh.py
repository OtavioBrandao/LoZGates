from itertools import product

def get_minterms(expressao, variables):
    minterms = []
    n = len(variables)
    for values in product([0, 1], repeat=n):
        assignment = dict(zip(variables, values))
        if eval(expressao, assignment):
            minterms.append(values)
    return minterms

def generate_karnaugh_map(minterms, variables):
    n = len(variables)
    mapa = ""
    if n == 2:
        mapa += "Mapa de Karnaugh para 2 variáveis:\n"
        mapa += "  0 1\n"
        for i in range(2):
            row = f"{i}|"
            for j in range(2):
                if (i, j) in minterms:
                    row += "1 "
                else:
                    row += "0 "
            mapa += row + "\n"
    elif n == 3:
        mapa += "Mapa de Karnaugh para 3 variáveis:\n"
        mapa += "  00 01 11 10\n"
        for i in range(2):
            row = f"{i}|"
            for j in range(4):
                if (i, j // 2, j % 2) in minterms:
                    row += "1 "
                else:
                    row += "0 "
            mapa += row + "\n"
    elif n == 4:
        mapa += "Mapa de Karnaugh para 4 variáveis:\n"
        mapa += "  00 01 11 10\n"
        for i in range(4):
            row = f"{i}|"
            for j in range(4):
                if (i // 2, i % 2, j // 2, j % 2) in minterms:
                    row += "1 "
                else:
                    row += "0 "
            mapa += row + "\n"
    else:
        mapa += "Número de variáveis não suportado.\n"
    return mapa

def karnaugh_map(expressao, variables):
    # Substitui a implicação pela sua forma equivalente
    expressao_modificada = expressao.replace(">", "<=")
    minterms = get_minterms(expressao_modificada, variables)
    return generate_karnaugh_map(minterms, variables)
    
def analisar(expressao):
    variaveis = set()
    for char in expressao:
        if char.upper() in ('P', 'Q', 'R', 'S', 'T'):
            variaveis.add(char.upper())
    return sorted(variaveis)