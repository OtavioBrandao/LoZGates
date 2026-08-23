"""Smoke manual da arvore Tk em tamanhos diferentes; requer um ambiente com tela."""

import os
import sys
from pathlib import Path

import customtkinter as ctk


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


WINDOW_SIZES = ((800, 600), (1024, 768), (1600, 900))


def smoke_mainloop(window):
    window.state("normal")
    for width, height in WINDOW_SIZES:
        window.geometry(f"{width}x{height}")
        window.update_idletasks()
        window.update()
    window.destroy()


def run():
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    ctk.CTk.mainloop = smoke_mainloop
    from main import main

    main()
    print("UI_SMOKE_OK: 800x600, 1024x768, 1600x900")


if __name__ == "__main__":
    run()
