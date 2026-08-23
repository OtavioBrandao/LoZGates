"""Adaptadores pequenos para embutir Pygame em Tk no Windows e no Linux."""

import logging
import os
import sys


logger = logging.getLogger(__name__)


def select_sdl_video_driver(platform_name=None, environment=None):
    """Escolhe somente drivers capazes de usar SDL_WINDOWID na plataforma."""
    environment = environment if environment is not None else os.environ
    if environment.get("SDL_VIDEODRIVER"):
        return environment["SDL_VIDEODRIVER"]

    platform_name = platform_name or sys.platform
    if platform_name.startswith("win"):
        return "windows"
    if platform_name.startswith("linux") and environment.get("DISPLAY"):
        # O embedding por ID de janela e uma funcionalidade do X11. Em uma
        # sessao Wayland pura deixamos o SDL decidir e registramos a limitacao.
        return "x11"
    return None


def configure_sdl_embedding(window_id):
    os.environ["SDL_WINDOWID"] = str(window_id)
    selected_driver = select_sdl_video_driver()
    if selected_driver:
        os.environ.setdefault("SDL_VIDEODRIVER", selected_driver)
    elif sys.platform.startswith("linux"):
        logger.warning(
            "Embedding Pygame sem DISPLAY/X11; o compositor pode abrir uma janela separada"
        )
    return selected_driver


def fit_surface_size(width, height, minimum=(320, 240)):
    """Normaliza dimensoes reais do frame sem forcar uma superficie maior."""
    min_width, min_height = minimum
    return max(min_width, int(width)), max(min_height, int(height))
