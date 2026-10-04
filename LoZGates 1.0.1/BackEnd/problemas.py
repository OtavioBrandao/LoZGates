"""
Banco de problemas: consulta e correção das respostas.

A regra de correção é a do interface_update (que ficava dentro da tela de
problemas em CustomTkinter): a resposta está certa se for logicamente
equivalente à esperada, ou se tiver a mesma estrutura com outros nomes de
variáveis (ex.: a>b no lugar de p>q).
"""
import textwrap
from dataclasses import dataclass
from typing import Dict, List

from BackEnd.core.expression_ast import ExpressaoInvalida, parse
from BackEnd.equivalencia import check_universal_equivalence
from BackEnd.normalizer import expressions_are_structurally_equivalent, normalize_for_comparison
from BackEnd.problems_bank import Problems_bank

MENSAGEM_VAZIA = "⚠️ Por favor, digite uma resposta"
MENSAGEM_CORRETA = "✅ Resposta correta! Parabéns!"
MENSAGEM_CORRETA_ESTRUTURAL = (
    "✅ Resposta correta! Sua expressão tem a mesma estrutura lógica "
    "(apenas os nomes das variáveis diferem)."
)
MENSAGEM_INCORRETA = "❌ Resposta incorreta. Sua expressão não é logicamente equivalente à resposta esperada."


@dataclass(frozen=True)
class Correcao:
    correta: bool
    mensagem: str
    tipo: str   # 'vazia', 'invalida', 'equivalente', 'estrutural' ou 'incorreta'


def listar_problemas() -> List[Dict]:
    return [
        {"indice": indice, "nome": problema.name, "dificuldade": problema.difficulty}
        for indice, problema in enumerate(Problems_bank)
    ]


def obter_problema(indice: int) -> Dict:
    """Levanta IndexError se o problema não existir."""
    if not 0 <= indice < len(Problems_bank):
        raise IndexError(f"Problema {indice} não existe.")
    problema = Problems_bank[indice]
    return {
        "indice": indice,
        "nome": problema.name,
        "dificuldade": problema.difficulty,
        # O texto é o mesmo da versão desktop, sem a indentação do código-fonte
        "pergunta": textwrap.dedent(problema.question).strip("\n"),
        "resposta": problema.answer,
    }


def verificar_resposta(resposta: str, correta: str) -> Correcao:
    if not resposta.strip():
        return Correcao(False, MENSAGEM_VAZIA, "vazia")

    resposta_limpa = resposta.strip().upper().replace(" ", "")
    correta_limpa = correta.strip().upper().replace(" ", "")

    try:
        parse(resposta_limpa)
    except ExpressaoInvalida as erro:
        return Correcao(False, f"❌ Expressão inválida: {erro.mensagem}", "invalida")

    #PRIMEIRA VERIFICAÇÃO: equivalência lógica direta
    if check_universal_equivalence(resposta_limpa, correta_limpa):
        return Correcao(True, MENSAGEM_CORRETA, "equivalente")

    #SEGUNDA VERIFICAÇÃO: mesma estrutura com outras variáveis
    if expressions_are_structurally_equivalent(resposta_limpa, correta_limpa):
        if check_universal_equivalence(
            normalize_for_comparison(resposta_limpa), normalize_for_comparison(correta_limpa)
        ):
            return Correcao(True, MENSAGEM_CORRETA_ESTRUTURAL, "estrutural")

    return Correcao(False, MENSAGEM_INCORRETA, "incorreta")


def verificar_resposta_do_problema(indice: int, resposta: str) -> Correcao:
    return verificar_resposta(resposta, obter_problema(indice)["resposta"])
