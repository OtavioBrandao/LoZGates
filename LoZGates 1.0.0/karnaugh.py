import threading
import itertools
from itertools import product

def get_minterms(expressao, variables):
    minterms = []
    n = len(variables)
    for values in product([0, 1], repeat=n):
        assignment = dict(zip(variables, values))
        if eval(expressao, assignment):
            minterms.append(values)
    return minterms

def print_karnaugh_map(minterms, variables):
    n = len(variables)
    if n == 2:
        print("Mapa de Karnaugh para 2 variáveis:")
        print("  0 1")
        for i in range(2):
            row = f"{i}|"
            for j in range(2):
                if (i, j) in minterms:
                    row += "1 "
                else:
                    row += "0 "
            print(row)
    elif n == 3:
        print("Mapa de Karnaugh para 3 variáveis:")
        print("  00 01 11 10")
        for i in range(2):
            row = f"{i}|"
            for j in range(4):
                if (i, j // 2, j % 2) in minterms:
                    row += "1 "
                else:
                    row += "0 "
            print(row)
    elif n == 4:
        print("Mapa de Karnaugh para 4 variáveis:")
        print("  00 01 11 10")
        for i in range(4):
            row = f"{i}|"
            for j in range(4):
                if (i // 2, i % 2, j // 2, j % 2) in minterms:
                    row += "1 "
                else:
                    row += "0 "
            print(row)
    else:
        print("Número de variáveis não suportado.")

def karnaugh_map(expressao, variables):
    minterms = get_minterms(expressao, variables)
    print_karnaugh_map(minterms, variables)
    
def analisar(expressao):
    variaveis = set()
    for char in expressao:
        if char.upper() in ('P', 'Q', 'R', 'S', 'T'):
            variaveis.add(char.upper())
    return sorted(variaveis)  # Retorna uma lista ordenada


#arrumar para implica e negado