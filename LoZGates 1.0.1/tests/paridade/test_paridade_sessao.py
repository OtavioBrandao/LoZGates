"""
Paridade do "Simplificar — Interativo": sequências de ações (aplicar lei,
pular, desfazer) rodam ao mesmo tempo no ResolverController original e na
sessão sem estado nova, e tudo o que o aluno vê precisa ser igual a cada passo.
"""
import random

import pytest

from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.core import sessao_interativa as sessao
from tests.paridade import corpus, oraculo

antigo_simpli = oraculo.modulo("BackEnd.simplificador_interativo")
AntigoController = oraculo.modulo("FrontEnd.screens.resolver.resolver_controller").ResolverController
AntigoState = oraculo.modulo("FrontEnd.screens.resolver.resolver_state").ResolverState
antigo_conversor = oraculo.modulo("BackEnd.converter")


class RegistroFalso:
    def __init__(self):
        self.chamadas = []

    def __getattr__(self, metodo):
        return lambda *argumentos: self.chamadas.append({"metodo": metodo, "argumentos": list(argumentos)})


class TelaFalsa:
    """O que a ResolverScreen fazia com o controller: avisos e o encerramento da sessão."""

    def __init__(self, controller):
        self.controller = controller
        self.avisos = []

    def atualizar_ui(self):
        if self.controller.state.motivo_parada_interativo in ("no_further_simplification", "maximum_steps", "repeated_state"):
            self.controller.concluir_sessao()

    def popup_erro(self, mensagem):
        self.avisos.append(mensagem)

    def adicionar_passo_sucesso(self, *argumentos):
        pass

    def adicionar_passo_pular(self, *argumentos):
        pass

    def reconstruir_area_passos(self):
        pass


def visao_antiga(controller):
    estado = controller.state
    passo = estado.passo_atual_info
    return {
        "expressao": str(estado.arvore_interativa),
        "subexpressao": str(passo["no_atual"]) if passo else None,
        "motivo_parada": estado.motivo_parada_interativo,
        "concluida": estado.sessao_simplificacao_concluida,
        "pode_desfazer": bool(estado.historico_de_estados),
        "contador_passos": estado.contador_passos,
    }


def comparavel(visao):
    return {chave: visao[chave] for chave in
            ("expressao", "subexpressao", "motivo_parada", "concluida", "pode_desfazer", "contador_passos")}


def sem_tempo(eventos):
    """O tempo decorrido em log_simplification_completed depende do relógio."""
    return [
        {**e, "argumentos": e["argumentos"][:1]} if e["metodo"] == "log_simplification_completed" else e
        for e in eventos
    ]


def roteiros(quantidade=120, passos=12, semente=7):
    sorteio = random.Random(semente)
    expressoes = [e for e in corpus.TODAS
                  if antigo_conversor.converter_para_algebra_booleana(e) == converter_para_algebra_booleana(e)]
    for _ in range(quantidade):
        acoes = []
        for _ in range(passos):
            escolha = sorteio.random()
            acoes.append(("lei", sorteio.randrange(9)) if escolha < 0.65 else ("pular",) if escolha < 0.85 else ("desfazer",))
        yield sorteio.choice(expressoes), acoes


@pytest.mark.parametrize("expr, acoes", list(roteiros()))
def test_roteiro_de_acoes_igual_ao_desktop(expr, acoes):
    booleana = converter_para_algebra_booleana(expr)
    antigo_simpli.reiniciar_busca()
    registro = RegistroFalso()
    controller = AntigoController(AntigoState(), registro)
    tela = TelaFalsa(controller)
    controller.set_view(tela)
    controller.iniciar_simplificacao(booleana)

    resposta = sessao.iniciar(booleana)
    assert comparavel(resposta.visao) == visao_antiga(controller)
    assert sem_tempo(resposta.eventos) == sem_tempo(registro.chamadas)

    for acao in acoes:
        registro.chamadas.clear()
        tela.avisos.clear()
        antigo_simpli.reiniciar_busca()  # o cursor global antigo só valia dentro de uma mesma árvore
        if acao[0] == "lei":
            controller.on_lei_selecionada(acao[1])
            resposta = sessao.aplicar_lei(resposta.estado, acao[1])
        elif acao[0] == "pular":
            controller.on_pular_selecionado()
            resposta = sessao.pular(resposta.estado)
        else:
            controller.on_desfazer_selecionado()
            resposta = sessao.desfazer(resposta.estado)
        assert comparavel(resposta.visao) == visao_antiga(controller), acao
        assert ([resposta.mensagem] if resposta.mensagem else []) == tela.avisos, acao
        assert sem_tempo(resposta.eventos) == sem_tempo(registro.chamadas), acao
