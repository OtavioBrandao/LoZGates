"""
"Simplificar — Interativo" sem estado no servidor.

É o fluxo do ResolverController/ResolverState do interface_update (escolher
uma lei para a subexpressão em análise, pular, desfazer), com as mesmas regras,
mensagens e eventos de uso. A diferença é que todo o estado viaja como JSON: o
cliente manda o estado atual junto com a ação e recebe o próximo. Assim vários
alunos usam o mesmo servidor sem compartilhar nada.

Dentro de uma requisição os nós ignorados são um set[int] de id() (a
igualdade dos nós é estrutural). Entre requisições eles viajam como caminhos
na árvore (índices de `children`), que não mudam ao reler o texto.
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import BackEnd.simplificador_interativo as simpli
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.core.expression_ast import caminho_ate, no_no_caminho, parse, percorrer, to_string_com_trechos

VERSAO_DO_ESTADO = 1
MOTIVOS_QUE_ENCERRAM = ("no_further_simplification", "maximum_steps", "repeated_state")

MENSAGEM_LEI_NAO_APLICAVEL = "Esta lei não pode ser aplicada à subexpressão atual."
MENSAGEM_NAO_REDUZ = "Esta transformação não reduz a expressão atual."


class EstadoInvalido(ValueError):
    """O estado recebido do cliente está corrompido ou é de outra versão."""


@dataclass
class Resposta:
    estado: dict
    visao: dict
    mensagem: Optional[str] = None
    # Chamadas para o registro de uso (nome do método do DetailedUserLogger e argumentos)
    eventos: List[dict] = field(default_factory=list)


def _evento(metodo: str, *argumentos) -> dict:
    return {"metodo": metodo, "argumentos": list(argumentos)}


def _caminho(arvore, no) -> List[int]:
    caminho = caminho_ate(arvore, no)
    if caminho is None:
        raise EstadoInvalido("Nó fora da árvore.")
    return list(caminho)


def _passo_no_caminho(arvore, caminho: Tuple[int, ...]) -> dict:
    """Reconstrói o passo_info (nó, pai e ramo) a partir do caminho."""
    no = no_no_caminho(arvore, caminho)
    if not caminho:
        return {"no_atual": no, "pai": None, "ramo": None}
    pai = no_no_caminho(arvore, caminho[:-1])
    return {"no_atual": no, "pai": pai, "ramo": "esquerda" if caminho[-1] == 0 else "direita"}


class _Sessao:
    """O ResolverController + ResolverState, operando sobre objetos vivos durante uma requisição."""

    def __init__(self):
        self.expressao_inicial = ""
        self.arvore = None
        self.ignorados: set = set()          # id() dos nós ignorados
        self.historico: List[dict] = []
        self.pilha: List[dict] = []          # snapshots para o desfazer
        self.contador_passos = 0
        self.passo_atual: Optional[dict] = None
        self.motivo_parada: Optional[str] = None
        self.concluida = False
        self.guarda: Optional[simpli.SimplificationGuard] = None
        self.inicio = 0.0
        self.mensagem: Optional[str] = None
        self.eventos: List[dict] = []

    # ------------------------------ serialização ------------------------------

    def _snapshot(self) -> dict:
        return {
            "arvore": simpli.formatar(self.arvore),
            "historico": copy.deepcopy(self.historico),
            "ignorados": [_caminho(self.arvore, no) for no in self._nos_ignorados()],
        }

    def _nos_ignorados(self):
        # Na ordem da árvore, para o JSON sair estável
        return [no for _, no in percorrer(self.arvore) if id(no) in self.ignorados]

    def para_dict(self) -> dict:
        return {
            "versao": VERSAO_DO_ESTADO,
            "expressao_inicial": self.expressao_inicial,
            "arvore": simpli.formatar(self.arvore),
            "ignorados": [_caminho(self.arvore, no) for no in self._nos_ignorados()],
            "passo_atual": None if self.passo_atual is None else _caminho(self.arvore, self.passo_atual["no_atual"]),
            "historico": copy.deepcopy(self.historico),
            "pilha_desfazer": copy.deepcopy(self.pilha),
            "contador_passos": self.contador_passos,
            "motivo_parada": self.motivo_parada,
            "concluida": self.concluida,
            "guarda": {
                "max_steps": self.guarda.max_steps,
                "passos_aceitos": self.guarda.accepted_steps,
                "complexidade_atual": self.guarda.current_complexity,
                "estados_visitados": sorted(self.guarda.visited_states),
            },
            "inicio": self.inicio,
        }

    @classmethod
    def de_dict(cls, dados: dict) -> "_Sessao":
        if not isinstance(dados, dict) or dados.get("versao") != VERSAO_DO_ESTADO:
            raise EstadoInvalido("Estado da simplificação ausente ou de outra versão.")
        try:
            sessao = cls()
            sessao.expressao_inicial = str(dados["expressao_inicial"])
            sessao.arvore = parse(dados["arvore"])
            sessao.ignorados = {id(no_no_caminho(sessao.arvore, tuple(c))) for c in dados["ignorados"]}
            caminho = dados["passo_atual"]
            sessao.passo_atual = None if caminho is None else _passo_no_caminho(sessao.arvore, tuple(caminho))
            sessao.historico = list(dados["historico"])
            sessao.pilha = list(dados["pilha_desfazer"])
            sessao.contador_passos = int(dados["contador_passos"])
            sessao.motivo_parada = dados["motivo_parada"]
            sessao.concluida = bool(dados["concluida"])
            guarda = dados["guarda"]
            sessao.guarda = simpli.SimplificationGuard(sessao.arvore, max_steps=guarda["max_steps"])
            sessao.guarda.accepted_steps = int(guarda["passos_aceitos"])
            sessao.guarda.current_complexity = int(guarda["complexidade_atual"])
            sessao.guarda.visited_states = set(guarda["estados_visitados"])
            sessao.inicio = float(dados["inicio"])
        except (KeyError, TypeError, ValueError) as erro:
            raise EstadoInvalido(f"Estado da simplificação inválido: {erro}") from erro
        return sessao

    def visao(self) -> dict:
        texto, trechos = to_string_com_trechos(self.arvore, style="boolean")
        no = self.passo_atual["no_atual"] if self.passo_atual else None
        return {
            "expressao": texto,
            "subexpressao": simpli.formatar(no) if no is not None else None,
            "trecho": list(trechos[id(no)]) if no is not None else None,
            "motivo_parada": self.motivo_parada,
            "concluida": self.concluida,
            "pode_desfazer": bool(self.pilha),
            "contador_passos": self.contador_passos,
            "historico": copy.deepcopy(self.historico),
            "leis": [lei["nome"] for lei in simpli.LEIS_LOGICAS],
        }

    def resposta(self) -> Resposta:
        return Resposta(self.para_dict(), self.visao(), self.mensagem, self.eventos)

    # ------------------------------ ResolverState ------------------------------

    def salvar_snapshot(self):
        self.pilha.append(self._snapshot())

    def restaurar_snapshot(self) -> bool:
        if not self.pilha:
            return False
        anterior = self.pilha.pop()
        self.arvore = parse(anterior["arvore"])
        self.historico = anterior["historico"]
        self.ignorados = {id(no_no_caminho(self.arvore, tuple(c))) for c in anterior["ignorados"]}
        self.passo_atual = None
        self.concluida = False
        self.motivo_parada = None
        return True

    # ------------------------------ ResolverController ------------------------------

    def iniciar(self, expressao_booleana: str, agora: float):
        self.expressao_inicial = expressao_booleana
        self.inicio = agora
        self.eventos.append(_evento("log_interactive_simplification_start", expressao_booleana))
        self.arvore = simpli.construir_arvore(expressao_booleana)
        self.guarda = simpli.SimplificationGuard(self.arvore)
        self.historico.append({"tipo": "inicial", "expressao": simpli.formatar(self.arvore)})
        self.iniciar_rodada()

    def iniciar_rodada(self):
        self.passo_atual = simpli.encontrar_proximo_passo(self.arvore, nos_a_ignorar=self.ignorados)
        if self.passo_atual is None and self.motivo_parada is None:
            self.motivo_parada = "no_further_simplification"
        self._atualizar()

    def _atualizar(self):
        # A tela do desktop encerrava a sessão ao exibir um motivo de parada definitivo
        if self.motivo_parada in MOTIVOS_QUE_ENCERRAM:
            self.concluir()

    def concluir(self):
        if self.concluida:
            return
        self.concluida = True
        decorrido = max(0.0, time.time() - self.inicio) if self.inicio else 0.0
        # Mesmos argumentos que o desktop passava (inclusive o tempo no lugar da lista de leis)
        self.eventos.append(_evento("log_simplification_completed", self.contador_passos, decorrido))

    def aplicar_lei(self, indice: int):
        if not self.passo_atual:
            return
        if not isinstance(indice, int) or not 0 <= indice < len(simpli.LEIS_LOGICAS):
            raise EstadoInvalido(f"Lei inexistente: {indice}")
        lei = simpli.LEIS_LOGICAS[indice]
        nome = lei["nome"]
        no_atual = self.passo_atual["no_atual"]
        antes = simpli.formatar(no_atual)

        # Validação pedagógica: lei que não se aplica só gera o aviso
        if not lei["verifica"](no_atual):
            self.mensagem = MENSAGEM_LEI_NAO_APLICAVEL
            return

        self.salvar_snapshot()
        nova, sucesso = simpli.aplicar_lei_e_substituir(self.arvore, self.passo_atual, indice)
        self.eventos.append(_evento("log_law_applied", nome, sucesso, self.contador_passos + 1))

        if sucesso:
            decisao = self.guarda.consider(nova)
            if not decisao.accepted:
                self.restaurar_snapshot()
                self.motivo_parada = decisao.reason
                self._atualizar()
                return
            self.arvore = nova
            self.motivo_parada = None
            self.concluida = False
            self.contador_passos += 1
            self.ignorados = set()
            self.historico.append({
                "tipo": "lei", "passo": self.contador_passos, "lei": nome,
                "antes": antes, "depois": simpli.formatar(self.arvore),
            })
            self.iniciar_rodada()
        else:
            estado_completo = simpli.formatar(self.arvore)
            motivo = f"Lei não aplicável à subexpressão '{antes}' no contexto de '{estado_completo}'"
            self.eventos.append(_evento(
                "log_simplification_step_failed", nome, self.contador_passos + 1, motivo, estado_completo))
            self.restaurar_snapshot()
            self.mensagem = MENSAGEM_NAO_REDUZ
            self.iniciar_rodada()

    def pular(self):
        if not (self.passo_atual and self.passo_atual["no_atual"]):
            return
        self.salvar_snapshot()
        no = self.passo_atual["no_atual"]
        self.eventos.append(_evento("log_simplification_skip", self.contador_passos))
        self.ignorados.add(id(no))
        self.concluida = False
        self.historico.append({"tipo": "pulo", "subexpressao": simpli.formatar(no)})
        self.iniciar_rodada()

    def desfazer(self):
        if not self.pilha:
            return
        self.eventos.append(_evento("log_simplification_undo"))
        if self.restaurar_snapshot():
            self.guarda = simpli.SimplificationGuard(self.arvore)
            self.iniciar_rodada()


# ------------------------------ funções públicas ------------------------------

def iniciar(expressao: str, agora: Optional[float] = None) -> Resposta:
    """Começa uma sessão. A expressão é convertida para álgebra booleana, como no desktop."""
    sessao = _Sessao()
    sessao.iniciar(converter_para_algebra_booleana(expressao), time.time() if agora is None else agora)
    return sessao.resposta()


def aplicar_lei(estado: dict, indice_lei: int) -> Resposta:
    sessao = _Sessao.de_dict(estado)
    sessao.aplicar_lei(indice_lei)
    return sessao.resposta()


def pular(estado: dict) -> Resposta:
    sessao = _Sessao.de_dict(estado)
    sessao.pular()
    return sessao.resposta()


def desfazer(estado: dict) -> Resposta:
    sessao = _Sessao.de_dict(estado)
    sessao.desfazer()
    return sessao.resposta()


def leis_disponiveis() -> List[Dict[str, object]]:
    return [{"indice": i, "nome": lei["nome"]} for i, lei in enumerate(simpli.LEIS_LOGICAS)]
