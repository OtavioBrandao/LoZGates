from itertools import product

def pegar_termos(expressao, variaveis):
    minterms = []
    n = len(variaveis)
    expressao_modificada = expressao.replace("!", "not ").replace("|", " or ").replace(">", "<=").replace("&", " and ")
    
    for values in product([0, 1], repeat=n):
        assignment = dict(zip(variaveis, values))
        if eval(expressao_modificada, assignment):
            minterms.append(values)
    return minterms

def gerar_mapa_karnaugh(minterms, variaveis):
    n = len(variaveis)
    mapa = ""
    
    if n == 2:
        mapa += "\n"
        mapa += f"Mapa de Karnaugh para 2 variáveis:\n"
        mapa += "\n"
        mapa += f"   {variaveis[1]}'     {variaveis[1]}\n"
        mapa += "     +-------+-------+\n"
        
        for i in range(2):
            row = f"{variaveis[0]}'" if i == 0 else f"{variaveis[0]}"
            row += " |"
            for j in range(2):
                if (i, j) in minterms:
                    row += "   1   |"
                else:
                    row += "   0   |"
            mapa += row + "\n"
            mapa += "     +-------+-------+\n"
    
    elif n == 3:
        mapa += f"Mapa de Karnaugh para 3 variáveis:\n"
        mapa += "\n"
        mapa += f"      {variaveis[1]}'{variaveis[2]}'   {variaveis[1]}'{variaveis[2]}   {variaveis[1]}{variaveis[2]}   {variaveis[1]}{variaveis[2]}'\n"
        mapa += "     +-------+-------+-------+-------+\n"
        
        for i in range(2):
            row = f"{variaveis[0]}'" if i == 0 else f"{variaveis[0]}"
            row += " |"
            for j in range(4):
                if (i, j // 2, j % 2) in minterms:
                    row += "   1   |"
                else:
                    row += "   0   |"
            mapa += row + "\n"
            mapa += "     +-------+-------+-------+-------+\n"
    
    elif n == 4:
        mapa += f"Mapa de Karnaugh para 4 variáveis:\n"
        mapa += "\n"
        mapa += f"      {variaveis[2]}'{variaveis[3]}'   {variaveis[2]}'{variaveis[3]}   {variaveis[2]}{variaveis[3]}   {variaveis[2]}{variaveis[3]}'\n"
        mapa += "     +-------+-------+-------+-------+\n"
        
        for i in [0, 1, 3, 2]:
            row = f"{variaveis[0]}'{variaveis[1]}'" if i == 0 else \
                f"{variaveis[0]}'{variaveis[1]}" if i == 1 else \
                f"{variaveis[0]}{variaveis[1]}" if i == 3 else \
                f"{variaveis[0]}{variaveis[1]}'"
            row += " |"
    
            for j in [0, 1, 3, 2]:  
                p = i // 2
                q = i % 2
                r = j // 2
                t = j % 2
                if (p, q, r, t) in minterms:
                    row += "   1   |"
                else:
                    row += "   0   |"
            mapa += row + "\n"
            mapa += "     +-------+-------+-------+-------+\n"
    
    else:
        mapa += "Número de variáveis não suportado.\n"
    return mapa

def karnaugh_map(expressao, variaveis):
    minterms = pegar_termos(expressao, variaveis)
    return gerar_mapa_karnaugh(minterms, variaveis)
    
def analisar(expressao):
    variaveis = set()
    for char in expressao:
        if char.upper() in ('P', 'Q', 'R', 'S', 'T'):
            variaveis.add(char.upper())
    return sorted(variaveis)
