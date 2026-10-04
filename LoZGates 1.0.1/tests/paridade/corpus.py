"""Expressões usadas nos testes de paridade (válidas no interface_update e na versão nova)."""
import random

from BackEnd.problems_bank import Problems_bank

CURADAS = [
    # exemplos dos testes, do manual e da interface
    "A&B", "A|B", "!A", "A>B", "A<>B", "A->B", "A*B", "A+B", "~A", "(A*B)+~C",
    "(A&B)|(!C&D)", "((A&B)|C)>(D<>E)", "P>Q", "Q>P", "!P|Q", "!(P&Q)", "!P|!Q", "!(P|Q)", "!P&!Q",
    "P>(Q|R)", "!P|(Q|R)", "P&!P", "A|B>C", "!!A", "A&B&C", "(A&B)&C", "A&(B&C)",
    # simplificação: casos dos testes do interface_update e do TODO
    "(A&1)|(B&!B)", "((A&B)|(A&!B))|((A&C)|(A&!C))|(A&D)", "A|!A", "A|(A&B)",
    "((A|B)&1)|((A|B)&0)", "(N&H&B)|(!F|I)", "(!(P|Q)|!P)&P", "P&!P&Q", "(A|B)&(A|C)",
    "(A&B)|(A&C)", "~(A*B)", "A*(A+B)", "B+A", "(A*B)*C",
    # implicações que o conversor antigo errava (D3b)
    "A&B>C", "A>B&C", "A>B>C", "(A>B)>C", "A&B<>C", "!A>B", "!(A>B)", "(A>B)&C",
    # constantes e parênteses redundantes
    "A&1", "A|0", "1", "0", "((A))", "(A)&(B)", "!(!(A))", "(A|0)&(1|B)",
] + [problema.answer.replace(" ", "") for problema in Problems_bank]


def aleatorias(quantidade=90, semente=4242):
    sorteio = random.Random(semente)

    def gerar(profundidade):
        if profundidade == 0 or sorteio.random() < 0.3:
            return sorteio.choice("ABCD") if sorteio.random() < 0.9 else sorteio.choice("01")
        escolha = sorteio.random()
        if escolha < 0.15:
            return "!" + gerar(profundidade - 1)
        if escolha < 0.35:
            return "(" + gerar(profundidade - 1) + ")"
        return gerar(profundidade - 1) + sorteio.choice(["&", "|", ">", "<>"]) + gerar(profundidade - 1)

    return [gerar(4) for _ in range(quantidade)]


TODAS = list(dict.fromkeys(CURADAS + aleatorias()))
SEM_IMPLICACAO = [e for e in TODAS if ">" not in e]
