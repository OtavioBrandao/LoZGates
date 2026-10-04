"""
Prepara o ambiente Python do navegador para os arquivos originais do LoZ Gates.

Chamado uma única vez, logo depois que o Pyodide e o pygame-ce são carregados.
"""

import functools
import os
import sys

from . import rede, tkweb

# Onde o JavaScript descompacta o código do LoZ Gates (BackEnd/, FrontEnd/, config.py, assets/)
PASTA_APP = os.environ.get("LOZGATES_APP_DIR", "/home/pyodide/lozgates")
# Pasta de trabalho: é onde o DetailedUserLogger grava user_activity_detailed.json e
# logging_settings.json (caminhos relativos, como no desktop). O JavaScript guarda
# esses arquivos no localStorage para que sobrevivam entre visitas.
PASTA_DADOS = os.environ.get("LOZGATES_DADOS_DIR", "/home/pyodide/dados")

# Elemento (oculto) que o SDL usa para ouvir o teclado. O teclado do circuito chega ao
# código original pelo bind("<KeyPress>") do QuadroWeb — igual ao desktop —, então o
# SDL não precisa (nem deve) capturar as teclas da página inteira; se capturasse,
# as caixas de texto do React deixariam de receber Backspace, espaço, setas etc.
ELEMENTO_TECLADO_SDL = "#lozgates-sdl-teclado"

_preparado = False


def corrigir_ambiente_sdl():
    """
    O código original força o driver de vídeo do Windows para embutir o pygame no Tk:
        os.environ['SDL_WINDOWID'] = ...
        os.environ['SDL_VIDEODRIVER'] = 'windows'
    No navegador o único driver é o 'emscripten' (canvas). Limpamos essas variáveis
    imediatamente antes de o SDL inicializar.
    """
    if os.environ.get("SDL_VIDEODRIVER") not in (None, "", "emscripten"):
        del os.environ["SDL_VIDEODRIVER"]
    os.environ.pop("SDL_WINDOWID", None)
    os.environ["SDL_EMSCRIPTEN_KEYBOARD_ELEMENT"] = ELEMENTO_TECLADO_SDL
    # O LoZ Gates não usa som; sem isto o pygame.init() abriria um AudioContext à toa.
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def _ajustar_pygame():
    import pygame

    if getattr(pygame, "_lozweb_ajustado", False):
        return

    init_original = pygame.init
    set_mode_original = pygame.display.set_mode

    @functools.wraps(init_original)
    def init(*args, **kwargs):
        corrigir_ambiente_sdl()
        return init_original(*args, **kwargs)

    @functools.wraps(set_mode_original)
    def set_mode(*args, **kwargs):
        corrigir_ambiente_sdl()
        return set_mode_original(*args, **kwargs)

    pygame.init = init
    pygame.display.set_mode = set_mode
    pygame._lozweb_ajustado = True


def preparar():
    global _preparado
    if _preparado:
        return
    # Módulos que o navegador não tem
    tkweb.instalar_tkinter_inerte()
    rede.instalar_requests()

    # Código do LoZ Gates importável como no desktop (import BackEnd..., import config)
    if PASTA_APP not in sys.path:
        sys.path.insert(0, PASTA_APP)

    os.makedirs(PASTA_DADOS, exist_ok=True)
    os.chdir(PASTA_DADOS)

    corrigir_ambiente_sdl()
    _ajustar_pygame()
    _preparado = True
