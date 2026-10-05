"""
Cenários de paridade do editor do circuito interativo.

O editor agora roda no navegador (frontend/src/circuito/editor/modelo.ts). Para
provar que ele se comporta como o pygame do interface_update, este módulo roda
o código ORIGINAL (o oráculo congelado: CircuitoInterativoManual, Component,
CircuitDrawer, ComponentPalette) em situações sorteadas e grava as respostas
num JSON que o teste do frontend (modelo.test.ts) confere.

    python -m tests.paridade.editor_circuito      # regrava o JSON

tests/paridade/test_paridade_editor.py garante que o JSON gravado é o que o
oráculo produz hoje.
"""
import json
import os
import pathlib
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

from BackEnd.circuito_logico.logic.componentes import definicoes  # noqa: E402
from tests.paridade import oraculo  # noqa: E402

antigo_componentes = oraculo.modulo("BackEnd.circuito_logico.interactive.components")
antigo_interativo = oraculo.modulo("BackEnd.circuito_logico.interactive.interactive_circuit")
antigo_paleta = oraculo.modulo("BackEnd.circuito_logico.interactive.palette")
antigo_drawer = oraculo.modulo("BackEnd.circuito_logico.rendering.drawer")
antigo_camera = oraculo.modulo("BackEnd.circuito_logico.rendering.camera")

ARQUIVO = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "src" / "circuito" / "editor" / "paridade-editor.json"
TIPOS = ["variable", "and", "or", "not", "nand", "nor", "xor", "xnor", "output"]
# Tela usada nos cenários de arrasto (câmera na origem, zoom 1)
LARGURA_TELA, ALTURA_TELA = 800, 600


class _CameraIdentidade:
    zoom = 1.0

    @staticmethod
    def world_to_screen(ponto):
        return (int(ponto[0]), int(ponto[1]))


_desenhista = None


def _desenhar(componente):
    """O desenho recalcula os pinos das portas a cada quadro; fazemos o mesmo."""
    global _desenhista
    if _desenhista is None:
        pygame.font.init()
        _desenhista = antigo_drawer.CircuitDrawer(pygame.Surface((10, 10)), _CameraIdentidade())
    componente.update_connection_points()
    _desenhista.draw_component(componente)
    return componente


def _componente(dados):
    return _desenhar(antigo_componentes.ComponentFactory.create_component(dados["tipo"], dados["x"], dados["y"], "A"))


def _circuito(layout):
    circuito = object.__new__(antigo_interativo.CircuitoInterativoManual)
    circuito.components = [_componente(c) for c in layout]
    circuito.wires = []
    circuito.collision_margin = 10
    circuito.ghost_component = None
    circuito.selected_component = None
    circuito.connecting = False
    circuito.placing_component = False
    circuito.logger = None
    circuito.camera = antigo_camera.Camera(LARGURA_TELA, ALTURA_TELA)
    circuito.save_state = lambda *_: None
    return circuito


def _coordenada(sorteio, inicio, fim):
    # Quase sempre inteiros (como o editor costuma ter), às vezes valores quebrados (da espiral)
    valor = sorteio.uniform(inicio, fim)
    return round(valor, 3) if sorteio.random() < 0.3 else int(valor)


def _layout(sorteio, quantidade):
    return [
        {"tipo": sorteio.choice(TIPOS), "x": _coordenada(sorteio, -250, 250), "y": _coordenada(sorteio, -200, 200)}
        for _ in range(quantidade)
    ]


def _perto_de(sorteio, layout):
    alvo = sorteio.choice(layout)
    return alvo["x"] + _coordenada(sorteio, -90, 90), alvo["y"] + _coordenada(sorteio, -90, 90)


def cenarios_de_posicao(sorteio, quantidade=150):
    """check_collision e find_valid_position para um componente novo."""
    saida = []
    for _ in range(quantidade):
        layout = _layout(sorteio, sorteio.randint(1, 8))
        circuito = _circuito(layout)
        tipo = sorteio.choice(TIPOS)
        x, y = _perto_de(sorteio, layout)
        novo = _componente({"tipo": tipo, "x": x, "y": y})
        valida = circuito.find_valid_position(novo, x, y)
        saida.append({
            "layout": layout, "tipo": tipo, "x": x, "y": y,
            "colide": bool(circuito.check_collision(novo, x, y)),
            "valida": [float(valida[0]), float(valida[1])],
        })
    # Um caso sem lugar livre: a espiral desiste e devolve a posição pedida
    lotado = [{"tipo": "and", "x": x, "y": y} for x in range(-300, 301, 60) for y in range(-300, 301, 60)]
    circuito = _circuito(lotado)
    novo = _componente({"tipo": "or", "x": 0, "y": 0})
    valida = circuito.find_valid_position(novo, 0, 0)
    saida.append({"layout": lotado, "tipo": "or", "x": 0, "y": 0, "colide": True, "valida": [float(valida[0]), float(valida[1])]})
    return saida


def cenarios_de_clique(sorteio, quantidade=300):
    """Qual componente e qual pino o clique (handle_mouse_click) acerta."""
    saida = []
    for _ in range(quantidade):
        layout = _layout(sorteio, sorteio.randint(1, 6))
        circuito = _circuito(layout)
        if sorteio.random() < 0.5:
            # Mira num pino de verdade (com um desvio), para exercitar o raio de 15
            alvo = sorteio.choice(circuito.components)
            pinos = alvo.inputs + alvo.outputs
            px, py = sorteio.choice(pinos)
            ponto = (px + sorteio.uniform(-18, 18), py + sorteio.uniform(-18, 18))
        else:
            ponto = _perto_de(sorteio, layout)
        ponto = (round(ponto[0], 3), round(ponto[1], 3))
        indice, pino = None, None
        for i, componente in enumerate(circuito.components):
            if componente.contains_point(ponto):
                indice = i
                encontrado = circuito.find_connection_point(componente, ponto)
                if encontrado:
                    pino = ["saida" if encontrado[0] == "output" else "entrada", encontrado[1]]
                break
        saida.append({"layout": layout, "ponto": list(ponto), "componente": indice, "pino": pino})
    return saida


def cenarios_de_arrasto(sorteio, quantidade=150):
    """handle_mouse_drag: para onde o componente selecionado vai (ou se fica)."""
    saida = []
    for _ in range(quantidade):
        layout = _layout(sorteio, sorteio.randint(2, 6))
        circuito = _circuito(layout)
        selecionado = sorteio.randrange(len(layout))
        circuito.selected_component = circuito.components[selecionado]
        mundo = _perto_de(sorteio, layout)
        tela = (round(mundo[0] + LARGURA_TELA / 2, 3), round(mundo[1] + ALTURA_TELA / 2, 3))
        circuito.handle_mouse_drag(tela)
        final = circuito.components[selecionado]
        saida.append({
            "layout": layout, "selecionado": selecionado, "tela": list(tela),
            "final": [float(final.x), float(final.y)],
        })
    return saida


def cenarios_de_paleta():
    """ComponentPalette.resize + get_button_rect em vários tamanhos de área."""
    saida = []
    for largura, altura in [(320, 240), (360, 500), (640, 480), (800, 600), (1200, 700), (1920, 1080), (500, 900), (300, 200)]:
        paleta = antigo_paleta.ComponentPalette(largura, altura)
        botoes = [list(paleta.get_button_rect(i)) for i in range(len(paleta.components))]
        saida.append({
            "largura": largura, "altura": altura,
            "paleta": [paleta.x, paleta.y, paleta.width, paleta.height],
            "botoes": botoes,
        })
    return saida


def cenarios(semente=2026):
    sorteio = random.Random(semente)
    return {
        "_gerado_por": "python -m tests.paridade.editor_circuito (oráculo do interface_update)",
        "definicoes": json.loads(json.dumps(definicoes())),
        "posicao": cenarios_de_posicao(sorteio),
        "clique": cenarios_de_clique(sorteio),
        "arrasto": cenarios_de_arrasto(sorteio),
        "paleta": cenarios_de_paleta(),
    }


def texto():
    return json.dumps(cenarios(), ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    ARQUIVO.write_text(texto(), encoding="utf-8")
    print(f"Gravado: {ARQUIVO}")
