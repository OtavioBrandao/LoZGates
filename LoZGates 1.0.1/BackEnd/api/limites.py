"""
Limites de proteção do servidor. A tabela-verdade e a equivalência crescem
com 2^n linhas: no desktop isso só deixava o programa lento, mas num servidor
compartilhado uma expressão enorme travaria todos os alunos. Os limites ficam
bem acima de qualquer exercício do banco de problemas (o maior tem 12
variáveis).
"""
from BackEnd.api.erros import LimiteExcedido
from BackEnd.core.expression_ast import collect_variables, parse

TAMANHO_MAXIMO_DA_EXPRESSAO = 300
VARIAVEIS_NA_TABELA_VERDADE = 12
VARIAVEIS_NA_EQUIVALENCIA = 16
COMPONENTES_NO_CIRCUITO = 300
TAMANHO_MAXIMO_DA_PERGUNTA = 1000


def conferir_variaveis(maximo: int, *expressoes: str) -> None:
    variaveis = set()
    for expressao in expressoes:
        variaveis |= collect_variables(parse(expressao))
    if len(variaveis) > maximo:
        raise LimiteExcedido(
            f"A expressão tem {len(variaveis)} variáveis; o máximo aqui é {maximo} "
            f"({2 ** maximo} linhas na tabela-verdade)."
        )
