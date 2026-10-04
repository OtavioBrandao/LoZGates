"""
"Simplificar - Resultado" no navegador.

No desktop (FrontEnd/interface.py -> expressao_simplificada):
    - principal_simplificar() roda numa thread, com o stdout redirecionado para um
      StepLogger que entrega cada linha ao StepParser (FrontEnd/step_view.py);
    - o StepParser chama step_view.append_step()/finalize(), e o StepView (widget Tk)
      desenha os cartões na tela conforme as linhas chegam;
    - identificar_lei.simplificar() faz time.sleep(1) entre as iterações ("tempo pra
      ver"), então os cartões aparecem aos poucos.

Aqui usamos o StepParser ORIGINAL. Só trocamos:
    - o StepView (widget) por VistaDePassos, que registra os mesmos dados;
    - o time.sleep(1) por um relógio virtual: em vez de travar o navegador por N
      segundos, anotamos em que instante cada cartão apareceria, e o React revela os
      cartões com esse mesmo ritmo.
"""

import sys
import time as _time
from contextlib import contextmanager, redirect_stdout


class RelogioVirtual:
    """Substitui o módulo `time` dentro de BackEnd.identificar_lei durante a simplificação."""

    def __init__(self):
        self.agora = 0.0

    def sleep(self, segundos):
        self.agora += float(segundos)

    def __getattr__(self, nome):
        return getattr(_time, nome)


class VistaDePassos:
    """Recebe as mesmas chamadas que o StepView do desktop recebia do StepParser."""

    def __init__(self, relogio):
        self.relogio = relogio
        self.expressao_inicial = ""
        self._steps = []
        self.passos = []
        self.final = None

    # --- interface do StepView usada pelo StepParser / interface.py ---
    def reset(self, original_expression):
        self.expressao_inicial = original_expression
        self._steps = []
        self.passos = []
        self.final = None

    def append_step(self, step):
        n = len(self._steps) + 1  # numeração automática, como no StepView
        step = {**step, "iteration": n}
        self._steps.append(step)
        self.passos.append({**step, "t": self.relogio.agora})

    def finalize(self, final_expression, success, stats=None):
        self.final = {
            "expressao": final_expression,
            "sucesso": bool(success),
            "iteracoes": len(self._steps),
            "t": self.relogio.agora,
        }


class StepLogger:
    """Cópia exata da classe interna StepLogger de interface.expressao_simplificada."""

    def __init__(self, parser):
        self.parser = parser
        self.buffer = ""

    def write(self, text):
        lines = text.splitlines()
        for line in lines:
            if line.strip():
                self.parser.parse_log_line(line)

    def flush(self):
        pass


@contextmanager
def relogio_virtual_em(modulo, relogio):
    original = modulo.time
    modulo.time = relogio
    try:
        yield relogio
    finally:
        modulo.time = original


def executar_simplificacao(expressao_para_simplificar):
    """
    Executa exatamente o que a thread `simplificar_thread` fazia no desktop e devolve
    a linha do tempo dos cartões.
    """
    import BackEnd.identificar_lei as identificar_lei
    from BackEnd.identificar_lei import principal_simplificar
    from FrontEnd.step_view import StepParser

    relogio = RelogioVirtual()
    vista = VistaDePassos(relogio)
    vista.reset(expressao_para_simplificar)
    parser = StepParser(vista)
    step_logger = StepLogger(parser)

    erro = None
    with relogio_virtual_em(identificar_lei, relogio):
        with redirect_stdout(step_logger):
            try:
                principal_simplificar(expressao_para_simplificar)
                parser.finalize_parsing(expressao_para_simplificar, True)
            except Exception as e:  # mesmo tratamento do desktop
                erro = f"\n--- OCORREU UM ERRO ---\n{e}"
    return {
        "expressao_inicial": vista.expressao_inicial,
        "passos": vista.passos,
        "final": vista.final,
        "erro": erro,
    }
