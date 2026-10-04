"""
Paridade do circuito com o interface_update original: as coordenadas do layout
novo são as que o renderizador pygame desenhava, e a correção do circuito
montado dá o mesmo veredito do CircuitoInterativoManual.
"""
import os
import random

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
pygame = pytest.importorskip("pygame")
pytest.importorskip("tkinter")

from BackEnd.circuito_logico.logic.componentes import pinos  # noqa: E402
from BackEnd.circuito_logico.logic.layout import montar_layout  # noqa: E402
from BackEnd.circuito_logico.logic.validacao import montar_netlist, validar_circuito  # noqa: E402
from BackEnd.circuito_logico.modos import DICAS, MODOS  # noqa: E402
from BackEnd.converter import converter_para_algebra_booleana  # noqa: E402
from BackEnd.core.expression_ast import NOT, OperatorNode, collect_variables, parse  # noqa: E402
from tests.paridade import corpus, oraculo  # noqa: E402

antigo_conversor = oraculo.modulo("BackEnd.converter")
antigo_renderer = oraculo.modulo("BackEnd.circuito_logico.rendering.circuit_renderer")
antigo_drawer = oraculo.modulo("BackEnd.circuito_logico.rendering.drawer")
antigo_componentes = oraculo.modulo("BackEnd.circuito_logico.interactive.components")
antigo_interativo = oraculo.modulo("BackEnd.circuito_logico.interactive.interactive_circuit")
antigo_modos = oraculo.modulo("BackEnd.circuito_logico.circuit_mode_selector")

pygame.font.init()


class CameraIdentidade:
    zoom = 1.0

    @staticmethod
    def world_to_screen(ponto):
        return (int(ponto[0]), int(ponto[1]))


class DrawerGravador(antigo_drawer.CircuitDrawer):
    """O desenhista original, gravando só as chamadas feitas pelo renderizador."""

    def __init__(self):
        super().__init__(pygame.Surface((1200, 800)), CameraIdentidade())
        self.gravando = True
        self.linhas, self.textos, self.portas, self.fios, self.pontos = [], [], [], [], []

    def draw_line(self, inicio, fim, cor, largura=2):
        if self.gravando:
            self.linhas.append((tuple(inicio), tuple(fim), largura))
        super().draw_line(inicio, fim, cor, largura)

    def draw_text(self, texto, posicao, tamanho=36, cor=None):
        if self.gravando:
            self.textos.append((texto, tuple(posicao)))

    def draw_gate_shape(self, nome, x, y):
        self.gravando = False
        try:
            saida = super().draw_gate_shape(nome, x, y)
        finally:
            self.gravando = True
        self.portas.append((nome, x, y, saida))
        return saida

    def draw_smart_wire(self, inicio, fim):
        self.fios.append((tuple(inicio), tuple(fim)))

    def draw_connection_dot(self, posicao, cor=None, raio=5):
        self.pontos.append(tuple(posicao))


def desenho_antigo(expr):
    booleana = antigo_conversor.converter_para_algebra_booleana(expr)
    drawer = DrawerGravador()
    antigo_renderer.desenhar_circuito_logico_base(booleana, drawer, 1200, 800)
    return drawer


def comparaveis():
    for expr in corpus.TODAS:
        if any(c in expr for c in "01"):
            continue  # o circuito antigo não aceitava constantes (desenhava "Erro")
        if antigo_conversor.converter_para_algebra_booleana(expr) != converter_para_algebra_booleana(expr):
            continue  # D3b: a entrada do circuito mudou junto com a conversão
        yield expr


@pytest.mark.parametrize("expr", list(comparaveis()))
def test_layout_tem_as_coordenadas_do_desenho_pygame(expr):
    antigo, novo = desenho_antigo(expr), montar_layout(expr)

    barramentos = [l for l in antigo.linhas if l[0][1] == 40 and l[0][0] == l[1][0]]
    assert [b['x'] for b in novo['barramentos']] == [l[0][0] for l in barramentos]
    rotulos = [t for t in antigo.textos if t[1][1] == 25]
    assert [(b['rotulo'], b['x']) for b in novo['barramentos']] == [(t[0], t[1][0]) for t in rotulos]

    assert [(p['tipo'], p['x'], p['y'], tuple(p['saida'])) for p in novo['portas']] == antigo.portas
    assert [(tuple(f['pontos'][0]), tuple(f['pontos'][-1])) for f in novo['fios']] == antigo.fios
    assert [tuple(c['ponto']) for c in novo['conexoes']] == antigo.pontos

    linha_de_saida = [l for l in antigo.linhas if l[2] == 4]
    if novo['saida'] is None:
        assert linha_de_saida == []
    else:
        assert linha_de_saida == [(tuple(novo['saida']['de']), tuple(novo['saida']['ate']), 4)]
        assert ("SAÍDA", tuple(novo['saida']['rotulo'])) in antigo.textos


# ------------------------------ correção do circuito montado ------------------------------

def veredito_antigo(expr_booleana, componentes, fios, modo):
    """Monta o circuito com os Component/Wire originais e chama is_circuit_correct."""
    objetos = {}
    for c in componentes:
        objetos[c['id']] = antigo_componentes.ComponentFactory.create_component(c['tipo'], 0, 0, c.get('nome', ''))
    fios_antigos = []
    for f in fios:
        fio = antigo_componentes.Wire(objetos[f['origem']], 0, objetos[f['destino']], f['entrada'])
        objetos[f['origem']].output_connections.append(fio)
        objetos[f['destino']].input_connections[f['entrada']] = fio
        fios_antigos.append(fio)
    circuito = object.__new__(antigo_interativo.CircuitoInterativoManual)
    circuito.components = [objetos[c['id']] for c in componentes]
    circuito.wires = fios_antigos
    circuito.expressao = expr_booleana
    circuito.mode_key = modo
    circuito.logger = None
    return circuito.is_circuit_correct()


def circuito_da_expressao(expr_booleana):
    """O circuito "de livro" da expressão, porta a porta, como um aluno montaria."""
    arvore = parse(expr_booleana)
    variaveis = sorted(collect_variables(arvore))
    componentes = [{'id': f'var-{v}', 'tipo': 'variable', 'nome': v} for v in variaveis]
    componentes.append({'id': 'saida', 'tipo': 'output'})
    fios = []

    def montar(no):
        if not isinstance(no, OperatorNode):
            return f'var-{no.name}'
        pid = f'g{len(componentes)}'
        componentes.append({'id': pid, 'tipo': {'&': 'and', '|': 'or', NOT: 'not'}[no.op]})
        for i, filho in enumerate(no.children):
            fios.append({'origem': montar(filho), 'destino': pid, 'entrada': i})
        return pid

    fios.append({'origem': montar(arvore), 'destino': 'saida', 'entrada': 0})
    return componentes, fios


def sem_constantes_nem_implicacao(expr):
    booleana = converter_para_algebra_booleana(expr)
    return not any(c in booleana for c in "01") and collect_variables(parse(booleana))


@pytest.mark.parametrize("expr", [e for e in corpus.SEM_IMPLICACAO if sem_constantes_nem_implicacao(e)][:60])
@pytest.mark.parametrize("modo", ["livre", "basic_gates", "minimal"])
def test_circuito_de_livro_e_aceito_pelos_dois(expr, modo):
    booleana = converter_para_algebra_booleana(expr)
    componentes, fios = circuito_da_expressao(booleana)
    novo = validar_circuito(booleana, montar_netlist({'componentes': componentes, 'fios': fios}), modo)
    antigo = veredito_antigo(booleana, componentes, fios, modo)
    assert novo.correto == antigo
    tem_porta = any(c['tipo'] not in ('variable', 'output') for c in componentes)
    # Sem porta (expressão de uma variável só) os dois recusam, exceto no modo Mínimo
    assert novo.correto is (tem_porta or modo == "minimal")


def circuitos_aleatorios(quantidade=400, semente=99):
    sorteio = random.Random(semente)
    expressoes = ["A*B", "A+B", "~A", "A*~B+C", "~(A+B)", "(A+B)*(A+C)", "A*B*C"]
    for _ in range(quantidade):
        expr = sorteio.choice(expressoes)
        modo = sorteio.choice(list(MODOS))
        tipos = MODOS[modo]['restrictions'] or ['and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor']
        variaveis = sorted(collect_variables(parse(expr)))
        componentes = [{'id': f'var-{v}', 'tipo': 'variable', 'nome': v} for v in variaveis]
        componentes.append({'id': 'saida', 'tipo': 'output'})
        componentes += [{'id': f'g{i}', 'tipo': sorteio.choice(tipos)} for i in range(sorteio.randint(0, 4))]
        fios = []
        for destino in componentes:
            entradas = {'variable': 0, 'output': 1, 'not': 1}.get(destino['tipo'], 2)
            for entrada in range(entradas):
                if sorteio.random() < 0.8:
                    candidatos = [c['id'] for c in componentes if c['id'] != destino['id'] and c['tipo'] != 'output']
                    fios.append({'origem': sorteio.choice(candidatos), 'destino': destino['id'], 'entrada': entrada})
        yield expr, modo, componentes, fios


@pytest.mark.parametrize("expr, modo, componentes, fios", list(circuitos_aleatorios()))
def test_veredito_igual_em_circuitos_aleatorios(expr, modo, componentes, fios):
    novo = validar_circuito(expr, montar_netlist({'componentes': componentes, 'fios': fios}), modo)
    assert novo.correto == veredito_antigo(expr, componentes, fios, modo), novo.motivo


# ------------------------------ modos e geometria do editor ------------------------------

def test_modos_e_dicas_iguais_aos_originais():
    gerenciador = object.__new__(antigo_modos.CircuitModeManager)
    gerenciador.current_mode = None
    assert MODOS == antigo_modos.CircuitModeManager.MODES
    for chave in MODOS:
        assert DICAS[chave] == gerenciador.get_mode_tips(chave)


@pytest.mark.parametrize("tipo", ["variable", "and", "or", "not", "nand", "nor", "xor", "xnor", "output"])
def test_pinos_sao_os_do_desenho_original(tipo):
    componente = antigo_componentes.ComponentFactory.create_component(tipo, 17, 23, "A")
    DrawerGravador().draw_component(componente)  # o desenho recalcula os pinos, como a cada quadro
    esperados = pinos(tipo)
    assert componente.inputs == [(17 + dx, 23 + dy) for dx, dy in esperados['entradas']]
    assert componente.outputs == ([] if esperados['saida'] is None else [(17 + esperados['saida'][0], 23 + esperados['saida'][1])])
