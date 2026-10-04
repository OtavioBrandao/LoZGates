"""
Correção do circuito montado pelo aluno no editor interativo.

A interação (posicionar, arrastar, ligar fios, desfazer) acontece no
navegador. Aqui fica o raciocínio que o interface_update fazia em
CircuitoInterativoManual: validação estrutural, simulação porta a porta e
comparação com a expressão por tabela-verdade, com as mesmas regras.

Novidade: as portas usadas são conferidas contra as do modo de desafio. Antes
isso só era garantido pela paleta da interface.
"""
from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Optional, Set

from BackEnd.circuito_logico.logic.componentes import TIPOS, TIPOS_DE_PORTA
from BackEnd.circuito_logico.modos import MODOS, portas_permitidas
from BackEnd.core.expression_ast import avaliar, collect_variables, parse

ENTRADAS_ESPERADAS = {'and': 2, 'or': 2, 'not': 1, 'nand': 2, 'nor': 2, 'xor': 2, 'xnor': 2, 'output': 1}
MAXIMO_DE_ITERACOES = 15
MAXIMO_DE_FALHAS_RELATADAS = 8


class CircuitoInvalido(ValueError):
    """A descrição do circuito (netlist) está malformada."""


@dataclass(frozen=True)
class Componente:
    id: str
    tipo: str
    nome: str = ""


@dataclass(frozen=True)
class Fio:
    origem: str      # id do componente cuja saída alimenta o fio
    destino: str     # id do componente que recebe
    entrada: int     # índice da entrada no destino


@dataclass
class Netlist:
    """Componentes na ordem do editor (a simulação percorre nessa ordem, como antes)."""
    componentes: List[Componente]
    fios: List[Fio]

    def __post_init__(self):
        self.por_id: Dict[str, Componente] = {}
        for componente in self.componentes:
            if componente.tipo not in TIPOS:
                raise CircuitoInvalido(f"Tipo de componente desconhecido: {componente.tipo!r}")
            if componente.id in self.por_id:
                raise CircuitoInvalido(f"Componente repetido: {componente.id!r}")
            self.por_id[componente.id] = componente
        # entradas[id][i] = id do componente ligado à entrada i
        self.entradas: Dict[str, Dict[int, str]] = {c.id: {} for c in self.componentes}
        for fio in self.fios:
            if fio.origem not in self.por_id or fio.destino not in self.por_id:
                raise CircuitoInvalido("Fio ligado a um componente que não existe.")
            if fio.origem == fio.destino:
                raise CircuitoInvalido("Um componente não pode ser ligado a si mesmo.")
            origem, destino = self.por_id[fio.origem], self.por_id[fio.destino]
            if origem.tipo == 'output':
                raise CircuitoInvalido("A saída do circuito não alimenta outros componentes.")
            if not 0 <= fio.entrada < ENTRADAS_ESPERADAS.get(destino.tipo, 0):
                raise CircuitoInvalido(f"{destino.tipo.upper()} não tem a entrada {fio.entrada}.")
            if fio.entrada in self.entradas[fio.destino]:
                raise CircuitoInvalido("Uma entrada só pode receber um fio.")
            self.entradas[fio.destino][fio.entrada] = fio.origem


def montar_netlist(dados: dict) -> Netlist:
    try:
        componentes = [Componente(str(c['id']), str(c['tipo']), str(c.get('nome', ''))) for c in dados['componentes']]
        fios = [Fio(str(f['origem']), str(f['destino']), int(f['entrada'])) for f in dados.get('fios', [])]
    except (KeyError, TypeError, ValueError) as erro:
        raise CircuitoInvalido(f"Descrição do circuito incompleta: {erro}") from erro
    return Netlist(componentes, fios)


def _saida_da_porta(tipo: str, entradas: List[bool]) -> bool:
    if tipo == 'and':
        return all(entradas)
    if tipo == 'or':
        return any(entradas)
    if tipo == 'not':
        return not entradas[0]
    if tipo == 'nand':
        return not all(entradas)
    if tipo == 'nor':
        return not any(entradas)
    if tipo == 'xor':
        return sum(entradas) % 2 == 1
    if tipo == 'xnor':
        return sum(entradas) % 2 == 0
    return entradas[0]  # output


def simular(netlist: Netlist, valores: Dict[str, bool]) -> Dict[str, Optional[bool]]:
    """
    Valor na saída de cada componente (None se não deu para calcular), com a
    propagação do original: no máximo 15 passadas pela lista de componentes;
    uma porta só é calculada quando todas as suas entradas estão ligadas e
    já calculadas.
    """
    saidas: Dict[str, bool] = {
        c.id: valores[c.nome] for c in netlist.componentes if c.tipo == 'variable' and c.nome in valores
    }
    if saidas:
        for _ in range(MAXIMO_DE_ITERACOES):
            mudou = False
            for componente in netlist.componentes:
                if componente.id in saidas or componente.tipo == 'variable':
                    continue
                ligadas = netlist.entradas[componente.id]
                origens = [ligadas.get(i) for i in range(ENTRADAS_ESPERADAS[componente.tipo])]
                if any(o is None or o not in saidas for o in origens):
                    continue
                saidas[componente.id] = _saida_da_porta(componente.tipo, [saidas[o] for o in origens])
                mudou = True
            if not mudou:
                break
    return {c.id: saidas.get(c.id) for c in netlist.componentes}


@dataclass
class ResultadoValidacao:
    correto: bool
    motivo: str
    variaveis: List[str]
    variaveis_faltando: List[str] = field(default_factory=list)
    portas_nao_permitidas: List[str] = field(default_factory=list)
    falhas: List[Dict] = field(default_factory=list)
    combinacoes: int = 0


def _alcancaveis(netlist: Netlist, partida: str) -> Set[str]:
    """Componentes de onde chega sinal até `partida` (andando pelos fios para trás)."""
    vistos: Set[str] = set()
    pilha = [partida]
    while pilha:
        atual = pilha.pop()
        if atual in vistos:
            continue
        vistos.add(atual)
        pilha.extend(netlist.entradas[atual].values())
    return vistos


def _ha_porta_no_caminho(netlist: Netlist, atual: str, vistos: Set[str]) -> bool:
    """Como _has_logic_gate_in_path: para na primeira porta ou na variável."""
    if atual in vistos:
        return False
    vistos.add(atual)
    tipo = netlist.por_id[atual].tipo
    if tipo in TIPOS_DE_PORTA:
        return True
    if tipo == 'variable':
        return False
    return any(_ha_porta_no_caminho(netlist, origem, vistos) for origem in netlist.entradas[atual].values())


def validar_circuito(expressao_booleana: str, netlist: Netlist, modo: str = 'livre') -> ResultadoValidacao:
    if modo not in MODOS:
        raise CircuitoInvalido(f"Modo de desafio desconhecido: {modo!r}")
    arvore = parse(expressao_booleana)
    variaveis = sorted(collect_variables(arvore))

    permitidas = portas_permitidas(modo)
    if permitidas is not None:
        proibidas = sorted({c.tipo for c in netlist.componentes if c.tipo in TIPOS_DE_PORTA} - set(permitidas))
        if proibidas:
            return ResultadoValidacao(False, 'porta_nao_permitida', variaveis, portas_nao_permitidas=proibidas)

    saida = next((c for c in netlist.componentes if c.tipo == 'output'), None)
    if saida is None:
        return ResultadoValidacao(False, 'sem_saida', variaveis)
    if len(netlist.entradas[saida.id]) != 1:
        return ResultadoValidacao(False, 'saida_desconectada', variaveis)

    ligadas = {
        netlist.por_id[i].nome for i in _alcancaveis(netlist, saida.id) if netlist.por_id[i].tipo == 'variable'
    }
    if modo != 'minimal':
        faltando = sorted(set(variaveis) - ligadas)
        if faltando:
            return ResultadoValidacao(False, 'variaveis_desconectadas', variaveis, variaveis_faltando=faltando)
        if not _ha_porta_no_caminho(netlist, saida.id, set()):
            return ResultadoValidacao(False, 'sem_portas', variaveis)
    elif not ligadas:
        return ResultadoValidacao(False, 'nenhuma_variavel', variaveis)

    falhas = []
    combinacoes = list(product([False, True], repeat=len(variaveis)))
    for combinacao in combinacoes:
        valores = dict(zip(variaveis, combinacao))
        obtido = simular(netlist, valores)[saida.id]
        if obtido is None:
            return ResultadoValidacao(False, 'simulacao_incompleta', variaveis, combinacoes=len(combinacoes))
        esperado = avaliar(arvore, valores)
        if obtido != esperado:
            falhas.append({'entradas': valores, 'esperado': esperado, 'obtido': obtido})

    if falhas:
        return ResultadoValidacao(False, 'tabela_diferente', variaveis,
                                  falhas=falhas[:MAXIMO_DE_FALHAS_RELATADAS], combinacoes=len(combinacoes))
    return ResultadoValidacao(True, 'correto', variaveis, combinacoes=len(combinacoes))
