"""Scripted real-Tk workflow smoke; requires a graphical Windows session."""

import os
import sys
import tempfile
import time
from pathlib import Path

import customtkinter as ctk
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def button_with_text(window, fragment):
    for widget in descendants(window):
        if isinstance(widget, ctk.CTkButton) and fragment in str(widget.cget("text")):
            return widget
    raise AssertionError(f"Botão não encontrado: {fragment}")


def main_entry(window):
    for widget in descendants(window):
        if isinstance(widget, ctk.CTkEntry):
            if widget.cget("placeholder_text") == "Ex.: (A & B) | !C":
                return widget
    raise AssertionError("Entrada principal não encontrada")


def has_label(window, expected_text):
    return any(
        isinstance(widget, ctk.CTkLabel)
        and str(widget.cget("text")) == expected_text
        for widget in descendants(window)
    )


def simplification_view(window):
    from FrontEnd.components.step_view import StepView

    for widget in descendants(window):
        if isinstance(widget, StepView):
            return widget
    raise AssertionError("StepView não encontrada")


def wait_until(window, predicate, timeout=3):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        window.update_idletasks()
        window.update()
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError("Fluxo da interface excedeu o tempo esperado")


def run():
    temporary_data = tempfile.TemporaryDirectory()
    os.environ["LOZGATES_DATA_DIR"] = temporary_data.name
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

    from config import CIRCUIT_IMAGE_PATH
    import BackEnd.principal as circuit_renderer

    def fake_render(_expression, _x, width, height):
        CIRCUIT_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (min(width, 640), min(height, 360)), "white").save(
            CIRCUIT_IMAGE_PATH
        )

    circuit_renderer.plotar_circuito_logico = fake_render

    def workflow_mainloop(window):
        window.state("normal")
        window.geometry("1024x768")
        window.update()

        entry = main_entry(window)
        entry.insert(
            0,
            "((A & B) | (A & !B)) | ((A & C) | (A & !C)) | (A & D)",
        )
        button_with_text(window, "Confirmar").invoke()
        window.update()
        navigation = window._lozgates_navigation
        for _iteration in range(2):
            circuit_button = button_with_text(window, "Ver Circuito")
            circuit_button.invoke()
            wait_until(window, lambda: navigation.current_view == "circuit")
            wait_until(window, CIRCUIT_IMAGE_PATH.exists)
            wait_until(window, lambda: circuit_button.cget("state") == "normal")

            navigation.show_tab("expression")
            button_with_text(window, "Realizar conversão").invoke()
            window.update()
            step_view = simplification_view(window)
            button_with_text(window, "Simplificar - Resultado").invoke()
            wait_until(
                window,
                lambda: step_view.header.cget("text") == "Progresso da Simplificação"
                and step_view.footer.winfo_ismapped(),
            )
            if not has_label(window, "Expressão Resultante") or not has_label(window, "A"):
                raise AssertionError("Resultado simplificado A não foi exibido")

        navigation.show_tab("circuit")
        window.update()
        navigation.show_tab("expression")
        window.update()
        if navigation.current_view != "expression":
            raise AssertionError("Navegação não permaneceu disponível")
        window.destroy()

    ctk.CTk.mainloop = workflow_mainloop
    from main import main

    try:
        main()
    finally:
        temporary_data.cleanup()
    print("UI_WORKFLOW_OK: circuit -> expression -> simplification -> navigation")


if __name__ == "__main__":
    run()
