"""
Concorrência no "Simplificar — Interativo".

No interface_update a busca do próximo passo guardava um cursor GLOBAL no
módulo (_todos_os_nos_ordenados, _indice_no_atual, _chave_busca_atual). Num
servidor web, com vários alunos, uma sessão mexeria no cursor da outra. Agora
a busca é uma função pura e o estado da sessão viaja inteiro como JSON (D4).

Estes testes provam que duas sessões intercaladas, ou várias rodando em
threads ao mesmo tempo, dão exatamente o mesmo resultado de quando cada uma
roda sozinha.
"""
import ast
import inspect
import random
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

import BackEnd.simplificador_interativo as simpli
from BackEnd.core import sessao_interativa as sessao
from tests.paridade import oraculo

INSTANTE = 1_790_000_000.0
PASSOS = 16
EXPRESSOES = [
    "(A&1)|(B&!B)|C&C",
    "!(A&B)|(A&!C)",
    "(P|Q)&(P|R)",
    "A&(A|B)&!(C|D)",
    "(X&Y)|(X&!Y)",
    "(A&1)|(B&!B)|C&C",   # repetida de propósito: duas sessões com a mesma expressão
]


def escolher_acao(visao, sorteio):
    """
    Um aluno que costuma acertar: aplica uma lei que serve à subexpressão em
    análise, pula a que não tem lei, e às vezes erra a lei ou desfaz.
    """
    sorte = sorteio.random()
    if not visao["subexpressao"]:
        return ("desfazer",) if sorte < 0.5 else ("pular",)
    no = simpli.construir_arvore(visao["subexpressao"])
    aplicaveis = [i for i, lei in enumerate(simpli.LEIS_LOGICAS) if lei["verifica"](no)]
    if aplicaveis and sorte < 0.65:
        return ("lei", sorteio.choice(aplicaveis))
    if not aplicaveis and sorte < 0.6:
        return ("pular",)
    if sorte < 0.8:
        return ("lei", sorteio.randrange(len(simpli.LEIS_LOGICAS)))
    return ("pular",) if sorte < 0.92 else ("desfazer",)


def executar(resposta, acao):
    if acao[0] == "lei":
        return sessao.aplicar_lei(resposta.estado, acao[1])
    if acao[0] == "pular":
        return sessao.pular(resposta.estado)
    return sessao.desfazer(resposta.estado)


def foto(resposta):
    """Tudo o que o aluno vê e o que vai para o registro de uso (sem o tempo decorrido)."""
    eventos = [
        (e["metodo"], e["argumentos"][:1] if e["metodo"] == "log_simplification_completed" else e["argumentos"])
        for e in resposta.eventos
    ]
    return resposta.visao, resposta.mensagem, eventos


def aluno(expressao, semente):
    """Uma sessão inteira, uma foto por ação (gerador: dá para intercalar com outra sessão)."""
    sorteio = random.Random(semente)
    resposta = sessao.iniciar(expressao, agora=INSTANTE)
    yield foto(resposta)
    for _ in range(PASSOS):
        resposta = executar(resposta, escolher_acao(resposta.visao, sorteio))
        yield foto(resposta)


def sozinha(expressao, semente):
    return list(aluno(expressao, semente))


def test_modulo_nao_tem_estado_global():
    fonte = inspect.getsource(simpli)
    assert not [no for no in ast.walk(ast.parse(fonte)) if isinstance(no, ast.Global)]
    for nome in ("_todos_os_nos_ordenados", "_indice_no_atual", "_chave_busca_atual"):
        assert not hasattr(simpli, nome)


def test_busca_do_proximo_passo_e_pura():
    """Chamar de novo, ou no meio de buscas em outras árvores, devolve o mesmo nó."""
    arvore1 = simpli.construir_arvore("((A*1)+(B*~B))")
    arvore2 = simpli.construir_arvore("(~(A*B)+(A*~C))")
    primeiro = simpli.encontrar_proximo_passo(arvore1)["no_atual"]
    simpli.encontrar_proximo_passo(arvore2)
    assert simpli.encontrar_proximo_passo(arvore1)["no_atual"] is primeiro
    assert simpli.encontrar_proximo_passo(arvore1)["no_atual"] is primeiro


def test_no_codigo_antigo_uma_busca_interferia_na_outra():
    """Documenta o problema corrigido: no interface_update o resultado dependia das outras sessões."""
    antigo = oraculo.modulo("BackEnd.simplificador_interativo")
    antigo.reiniciar_busca()
    arvore1 = antigo.construir_arvore("((A*1)+(B*~B))")
    arvore2 = antigo.construir_arvore("(~(A*B)+(A*~C))")
    sem_ninguem = [str(antigo.encontrar_proximo_passo(arvore1)["no_atual"]) for _ in range(2)]
    antigo.reiniciar_busca()
    primeiro = str(antigo.encontrar_proximo_passo(arvore1)["no_atual"])
    antigo.encontrar_proximo_passo(arvore2)  # outra sessão usa o mesmo cursor global
    depois_da_outra = str(antigo.encontrar_proximo_passo(arvore1)["no_atual"])
    antigo.reiniciar_busca()
    assert sem_ninguem[0] != sem_ninguem[1]  # o cursor avançava sozinho
    assert [primeiro, depois_da_outra] != sem_ninguem  # e a outra sessão mudava o resultado


@pytest.mark.parametrize("i, j", [(0, 1), (2, 3), (4, 5), (0, 5)])
def test_duas_sessoes_intercaladas_nao_interferem(i, j):
    esperado_i, esperado_j = sozinha(EXPRESSOES[i], 100 + i), sozinha(EXPRESSOES[j], 200 + j)

    sessao_i, sessao_j = aluno(EXPRESSOES[i], 100 + i), aluno(EXPRESSOES[j], 200 + j)
    fotos_i, fotos_j = [], []
    for foto_i, foto_j in zip(sessao_i, sessao_j):  # uma ação de cada sessão por vez
        fotos_i.append(foto_i)
        fotos_j.append(foto_j)

    assert fotos_i == esperado_i
    assert fotos_j == esperado_j
    # As sessões andaram de verdade: leis aplicadas e vários estados diferentes
    assert esperado_i[-1][0]["contador_passos"] + esperado_j[-1][0]["contador_passos"] >= 3
    assert len({repr(f[0]) for f in esperado_i}) >= 4 and len({repr(f[0]) for f in esperado_j}) >= 4


def test_sessoes_em_threads_simultaneas_nao_interferem():
    """O FastAPI atende rotas síncronas em várias threads: 12 sessões ao mesmo tempo."""
    trabalhos = [(EXPRESSOES[k % len(EXPRESSOES)], 300 + k) for k in range(12)]
    esperados = [sozinha(expressao, semente) for expressao, semente in trabalhos]
    largada = threading.Barrier(len(trabalhos))

    def rodar(trabalho):
        largada.wait()  # todas começam juntas
        return sozinha(*trabalho)

    intervalo = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)  # troca de thread o mais cedo possível, para intercalar ao máximo
    try:
        with ThreadPoolExecutor(max_workers=len(trabalhos)) as executor:
            obtidos = list(executor.map(rodar, trabalhos))
    finally:
        sys.setswitchinterval(intervalo)
    assert obtidos == esperados
    assert sum(e[-1][0]["contador_passos"] for e in esperados) >= 12


def test_duas_sessoes_intercaladas_pela_api(cliente):
    """De ponta a ponta pelo HTTP: o servidor não guarda nada entre as requisições."""
    def acao_http(estado, acao):
        if acao[0] == "lei":
            return cliente.post("/api/simplificacao/interativa/aplicar", json={"estado": estado, "lei": acao[1]}).json()
        rota = "pular" if acao[0] == "pular" else "desfazer"
        return cliente.post(f"/api/simplificacao/interativa/{rota}", json={"estado": estado}).json()

    def aluno_http(expressao, semente):
        sorteio = random.Random(semente)
        resposta = cliente.post("/api/simplificacao/interativa/iniciar", json={"expressao": expressao}).json()
        yield resposta["visao"]
        for _ in range(PASSOS):
            resposta = acao_http(resposta["estado"], escolher_acao(resposta["visao"], sorteio))
            yield resposta["visao"]

    a, b = EXPRESSOES[0], EXPRESSOES[3]
    esperado_a, esperado_b = list(aluno_http(a, 11)), list(aluno_http(b, 12))
    intercaladas = list(zip(aluno_http(a, 11), aluno_http(b, 12)))
    assert [x for x, _ in intercaladas] == esperado_a
    assert [y for _, y in intercaladas] == esperado_b
    assert esperado_a[-1]["contador_passos"] >= 1
