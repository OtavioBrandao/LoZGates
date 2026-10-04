import logging
from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Optional

from BackEnd.core.expression_ast import avaliar, collect_variables, parse


logger = logging.getLogger(__name__)


class UniversalLogicAnalyzer:
    """
    Fachada de compatibilidade sobre o parser canônico. O antigo avaliador
    por tokens (tokenize/evaluate_expression) deixou de existir: toda
    avaliação passa por expression_ast.parse e expression_ast.avaliar.
    """

    def extract_variables(self, *expressions):
        #Variáveis de todas as expressões, ordenadas para consistência
        variaveis = set()
        for expr in expressions:
            variaveis |= collect_variables(parse(expr))
        return sorted(variaveis)

    def analyze_expression(self, expression, values):
        return avaliar(parse(expression), values)


@dataclass(frozen=True)
class ResultadoEquivalencia:
    equivalentes: bool
    variaveis: List[str]
    # Primeira combinação em que as expressões diferem (None se equivalentes)
    contraexemplo: Optional[Dict[str, bool]] = None
    valor_1: Optional[bool] = None
    valor_2: Optional[bool] = None


def comparar_expressoes(expr1, expr2) -> ResultadoEquivalencia:
    """
    Equivalência lógica por tabela-verdade: as duas expressões têm o mesmo
    valor em todas as combinações das variáveis de ambas? Entrada inválida
    sobe como ExpressaoInvalida, com a mensagem para o aluno.
    """
    arvore1, arvore2 = parse(expr1), parse(expr2)
    variaveis = sorted(collect_variables(arvore1) | collect_variables(arvore2))
    for combinacao in product([False, True], repeat=len(variaveis)):
        valores = dict(zip(variaveis, combinacao))
        resultado1, resultado2 = avaliar(arvore1, valores), avaliar(arvore2, valores)
        if resultado1 != resultado2:
            return ResultadoEquivalencia(False, variaveis, valores, resultado1, resultado2)
    return ResultadoEquivalencia(True, variaveis)


def check_universal_equivalence(expr1, expr2, debug=False):
    """Compatibilidade: como comparar_expressoes, mas entrada inválida vira False."""
    try:
        resultado = comparar_expressoes(expr1, expr2)
    except ValueError as erro:
        logger.warning("Expressão inválida na verificação de equivalência: %s", erro)
        return False

    if debug:
        print(f"🔍 Analisando equivalência:")
        print(f"   Expressão 1: {expr1}")
        print(f"   Expressão 2: {expr2}")
        print(f"   Variáveis detectadas: {resultado.variaveis}")
        print(f"   Total de combinações: {2 ** len(resultado.variaveis)}")
        if resultado.equivalentes:
            print(f"✅ Resultado: EQUIVALENTES")
        else:
            print(f"❌ Diferença encontrada: {resultado.contraexemplo}")
            print(f"\n📊 Resultado: NÃO EQUIVALENTES")
    return resultado.equivalentes


#Função compatível com código original
def tabela(sentence1, sentence2):
    return 1 if check_universal_equivalence(sentence1, sentence2) else 2
