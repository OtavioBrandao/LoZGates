"""
Diferenças APROVADAS entre a versão nova e o interface_update original.

Toda diferença encontrada pelos testes de paridade precisa cair numa destas
categorias; qualquer outra faz o teste falhar. Referências: decisões da
auditoria (docs/auditoria-merge.md, §9), aprovadas em 04/10/2026.
"""

# D3a — a implicação associa à direita em TODOS os módulos (A>B>C = A>(B>C)).
# No interface_update o avaliador já lia assim, mas o normalizador do banco de
# problemas lia à esquerda; por isso "(P>Q)>R" era aceita como resposta para
# "A>B>C". A diferença só pode aparecer quando uma das expressões tem uma
# implicação encadeada sem parênteses.
IMPLICACAO_A_DIREITA = "D3a"

# D3b — conversão para álgebra booleana. O conversor antigo escolhia mal os
# operandos de > e <> sem parênteses ("A&B>C" -> "A*(~B+C)"). A saída nova só
# pode diferir da antiga quando a expressão tem implicação ou bi-implicação, e
# precisa ter o mesmo significado da entrada. A simplificação, o circuito e o
# rótulo de álgebra booleana herdam essa diferença.
CONVERSAO_DE_IMPLICACAO = "D3b"

# D3c — gramática única. Entradas que o parser canônico recusa (variável com
# mais de uma letra, caractere desconhecido, parênteses desbalanceados...)
# agora geram erro com mensagem clara em vez de um resultado silencioso.
ENTRADA_INVALIDA = "D3c"

# D3e — a conversão sai só com os parênteses necessários: "(A|B)&(C>D)" virava
# "(A+B)*((~C+D))" e agora vira "(A+B)*(~C+D)" (aprovado em 05/10/2026). O
# texto novo, relido, dá a MESMA árvore que o antigo; por isso circuito,
# tabela-verdade e simplificações continuam iguais.
PARENTESES_REDUNDANTES = "D3e"

# D3f — a mesma regra nas telas de simplificação (aprovado em 05/10/2026): a
# expressão, a subexpressão em análise, o histórico e os passos aparecem só
# com os parênteses necessários. Relidos, dão a MESMA árvore que o texto do
# desktop; o registro de uso continua com o texto antigo.
PARENTESES_NAS_SIMPLIFICACOES = "D3f"

# Determinismo — na tabela-verdade antiga, a ordem entre subexpressões do
# mesmo tamanho vinha de um set() e mudava a cada execução. A nova desempata
# pela posição. O conjunto de colunas e os valores são idênticos.
ORDEM_DE_COLUNAS_EMPATADAS = "determinismo"


def tem_implicacao(expressao: str) -> bool:
    return ">" in expressao


def mesma_arvore(texto1: str, texto2: str) -> bool:
    """D3e: os dois textos são lidos como a mesma árvore (igualdade estrutural)?"""
    from BackEnd.core.expression_ast import parse
    try:
        return parse(texto1) == parse(texto2)
    except ValueError:
        return False


def tem_implicacao_encadeada_sem_parenteses(expressao: str) -> bool:
    """Há um "X>Y>Z" escrito sem parênteses, lido de forma diferente pelo normalizador antigo?"""
    from BackEnd.core.expression_ast import IMPLIES, OperatorNode, parse, percorrer
    try:
        arvore = parse(expressao)
    except ValueError:
        return False
    return any(
        isinstance(no, OperatorNode) and no.op == IMPLIES
        and isinstance(no.children[1], OperatorNode) and no.children[1].op == IMPLIES
        and not no.children[1].parenteses
        for _, no in percorrer(arvore)
    )
