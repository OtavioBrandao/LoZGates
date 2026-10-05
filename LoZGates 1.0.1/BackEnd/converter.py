"""
Conversão de lógica proposicional (& | ! > <>) para álgebra booleana (* + ~).

A conversão é feita sobre a árvore do parser canônico, então cada implicação
e cada bi-implicação recebe exatamente os operandos que a precedência manda
(antes, "A&B>C" virava "A*(~B+C)"). Os parênteses que o aluno digitou
continuam valendo para a forma da árvore, mas o texto final sai só com os
parênteses necessários: "(A|B)&(C>D)" vira "(A+B)*(~C+D)", não
"(A+B)*((~C+D))". Relido, o texto dá a mesma árvore (e o mesmo circuito).

    A -> B   = ~A + B
    A <-> B  = (~A + B) * (~B + A)
"""

from BackEnd.core.expression_ast import (
    AND,
    IFF,
    IMPLIES,
    NOT,
    OR,
    ExpressaoInvalida,
    OperatorNode,
    VariableNode,
    parse,
    to_string_minimo,
)


def _converter(no):
    texto = _converter_sem_parenteses(no)
    for _ in no.parenteses:  # parênteses que o aluno escreveu em volta deste nó
        texto = f"({texto})"
    return texto


def _negavel(no):
    """Texto do nó pronto para receber '~' na frente."""
    texto = _converter(no)
    if isinstance(no, OperatorNode) and no.op in (AND, OR) and not no.parenteses:
        return f"({texto})"
    return texto


def _converter_sem_parenteses(no):
    if isinstance(no, VariableNode):
        return no.name
    if no.op == NOT:
        return "~" + _converter(no.children[0])
    esquerda, direita = no.children
    if no.op == AND:
        return _converter(esquerda) + "*" + _converter(direita)
    if no.op == OR:
        return _converter(esquerda) + "+" + _converter(direita)
    if no.op == IMPLIES:
        return f"(~{_negavel(esquerda)}+{_converter(direita)})"
    if no.op == IFF:
        return (f"((~{_negavel(esquerda)}+{_converter(direita)})"
                f"*(~{_negavel(direita)}+{_converter(esquerda)}))")
    raise ValueError(f"Operador desconhecido: {no.op}")


class Conversorlogical:
    def __init__(self):
        #Histórico de conversões para debug
        self.history = []

    def convert_to_boolean_algebra(self, expression, show_steps=False):
        self.history = [f"Original: {expression}"]
        # _converter decide a forma da árvore (os parênteses do aluno e os de cada
        # implicação); a reimpressão tira os que não mudam essa forma
        convertida = to_string_minimo(parse(_converter(parse(expression))), style="boolean")
        self.history.append(f"Convertida: {convertida}")

        if show_steps:
            self.show_history()

        return convertida

    def show_history(self):
        print("=== Passos da Conversão ===")
        for i, step in enumerate(self.history, 1):
            print(f"{i}. {step}")
        print("=" * 28)

    def validate_expression(self, expression):
        try:
            parse(expression)
        except ExpressaoInvalida as erro:
            return False, erro.mensagem
        return True, ""

    def convert_batch(self, expressions):
        results = {}

        for expr in expressions:
            try:
                results[expr] = self.convert_to_boolean_algebra(expr)
            except ExpressaoInvalida as erro:
                results[expr] = f"ERRO: {erro.mensagem}"

        return results

#Função para compatibilidade, para nao mudar chamadas externas
def converter_para_algebra_booleana(expression):
    conversor = Conversorlogical()
    return conversor.convert_to_boolean_algebra(expression)
