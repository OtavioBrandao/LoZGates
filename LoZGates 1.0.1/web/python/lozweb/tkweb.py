"""
Substitutos do Tkinter para o navegador.

No desktop, o pygame era "embutido" num tk.Frame (via SDL_WINDOWID) e o laço de
desenho rodava com frame.after(16, self._tick). No navegador, o pygame desenha
num <canvas> e este módulo oferece um objeto com a MESMA interface de tk.Frame
que os arquivos originais usam — assim CircuitoInterativoManual e
CircuitoInterativo rodam sem nenhuma linha alterada.

Métodos de tk.Frame usados pelo código original (e implementados aqui):
    after, update, update_idletasks, winfo_width, winfo_height, winfo_id,
    winfo_children, configure/config, focus_set, bind, unbind, destroy
"""

import sys
import types
import traceback


# --------------------------------------------------------------------------
# Evento no formato do Tkinter
# --------------------------------------------------------------------------

class EventoTk:
    """Imita o objeto `event` que o Tkinter passa para os callbacks de bind()."""

    def __init__(self, keysym="", state=0, char="", widget=None, x=0, y=0, delta=0):
        self.keysym = keysym
        self.state = state
        self.char = char
        self.widget = widget
        self.x = x
        self.y = y
        self.delta = delta

    def __repr__(self):
        return f"<EventoTk keysym={self.keysym!r} state={self.state:#x}>"


# Nomes de tecla do navegador (KeyboardEvent.key) -> keysym do Tkinter
_KEYSYM_TK = {
    "ArrowUp": "Up",
    "ArrowDown": "Down",
    "ArrowLeft": "Left",
    "ArrowRight": "Right",
    " ": "space",
    "Spacebar": "space",
    "Escape": "Escape",
    "Esc": "Escape",
    "Delete": "Delete",
    "Del": "Delete",
    "Backspace": "BackSpace",
    "Enter": "Return",
    "Tab": "Tab",
    "Shift": "Shift_L",
    "Control": "Control_L",
    "Alt": "Alt_L",
    "Meta": "Meta_L",
    "Home": "Home",
    "End": "End",
    "PageUp": "Prior",
    "PageDown": "Next",
    "Insert": "Insert",
}

# Bits de modificadores no campo `state` do Tkinter (X11)
ESTADO_SHIFT = 0x1
ESTADO_CONTROL = 0x4
ESTADO_ALT = 0x8


def keysym_de(tecla_navegador: str) -> str:
    """Converte KeyboardEvent.key para o keysym equivalente do Tkinter."""
    if tecla_navegador in _KEYSYM_TK:
        return _KEYSYM_TK[tecla_navegador]
    # Letras, números e símbolos: o Tk usa o próprio caractere ('a', 'A', '1'...)
    # Teclas de função: 'F1'..'F12' têm o mesmo nome nos dois.
    return tecla_navegador


def estado_de(ctrl: bool, shift: bool, alt: bool) -> int:
    estado = 0
    if shift:
        estado |= ESTADO_SHIFT
    if ctrl:
        estado |= ESTADO_CONTROL
    if alt:
        estado |= ESTADO_ALT
    return estado


# --------------------------------------------------------------------------
# O "tk.Frame" do navegador
# --------------------------------------------------------------------------

class QuadroWeb:
    """
    Faz o papel do tk.Frame onde o pygame era embutido.

    agendar(ms, funcao) -> id   : equivalente ao after() do Tk (no navegador: setTimeout)
    medir() -> (largura, altura): tamanho em pixels da área reservada ao canvas
    focar()                     : dá foco de teclado ao canvas
    exibir_mensagem(texto, cor) : mostra um texto no lugar do canvas (usado quando
                                  o código original cria um tk.Label de erro)
    """

    def __init__(self, agendar, medir, focar=None, exibir_mensagem=None, cancelar=None):
        self._agendar = agendar
        self._cancelar = cancelar
        self._medir = medir
        self._focar = focar
        self._exibir_mensagem = exibir_mensagem
        self._binds = {}
        self._filhos = []
        self._destruido = False
        self.opcoes = {}

    # --- laço de eventos -------------------------------------------------
    def after(self, ms, func=None, *args):
        if func is None:
            # after(ms) sem função bloquearia o Tk; o código original não usa.
            return None

        def executar():
            if self._destruido:
                return
            try:
                func(*args)
            except Exception:
                # Mesmo comportamento do Tk: imprime o erro e o programa segue.
                print("Exception in Tkinter callback", file=sys.stderr)
                traceback.print_exc()

        return self._agendar(int(ms), executar)

    def after_idle(self, func, *args):
        return self.after(0, func, *args)

    def after_cancel(self, ident):
        if self._cancelar and ident is not None:
            self._cancelar(ident)

    def update(self):
        pass

    def update_idletasks(self):
        pass

    # --- geometria -------------------------------------------------------
    def winfo_width(self):
        return int(self._medir()[0])

    def winfo_height(self):
        return int(self._medir()[1])

    def winfo_id(self):
        # Só é usado para SDL_WINDOWID, que não tem efeito no navegador.
        return 1

    def winfo_exists(self):
        return not self._destruido

    def winfo_children(self):
        return list(self._filhos)

    def winfo_ismapped(self):
        return not self._destruido

    # --- aparência / foco ------------------------------------------------
    def configure(self, **opcoes):
        self.opcoes.update(opcoes)

    config = configure

    def focus_set(self):
        if self._focar and not self._destruido:
            self._focar()

    focus = focus_set

    # --- eventos de teclado/mouse ---------------------------------------
    def bind(self, sequencia, funcao=None, add=None):
        if funcao is None:
            return self._binds.get(sequencia)
        if add:
            self._binds.setdefault(sequencia, []).append(funcao)
        else:
            self._binds[sequencia] = [funcao]
        return sequencia

    def unbind(self, sequencia, funcid=None):
        self._binds.pop(sequencia, None)

    def disparar(self, sequencia, evento=None):
        """Chamado pelo navegador quando ocorre um evento (tecla, mouse entrando...)."""
        if self._destruido:
            return None
        if evento is None:
            evento = EventoTk(widget=self)
        resultado = None
        for funcao in list(self._binds.get(sequencia, [])):
            try:
                resultado = funcao(evento)
            except Exception:
                print("Exception in Tkinter callback", file=sys.stderr)
                traceback.print_exc()
            if resultado == "break":
                break
        return resultado

    def disparar_tecla(self, tipo, tecla, ctrl=False, shift=False, alt=False):
        sequencia = "<KeyPress>" if tipo == "keydown" else "<KeyRelease>"
        evento = EventoTk(
            keysym=keysym_de(tecla),
            state=estado_de(ctrl, shift, alt),
            char=tecla if len(tecla) == 1 else "",
            widget=self,
        )
        return self.disparar(sequencia, evento)

    # --- ciclo de vida ---------------------------------------------------
    def _registrar_filho(self, filho):
        self._filhos.append(filho)

    def _remover_filho(self, filho):
        if filho in self._filhos:
            self._filhos.remove(filho)

    def _mostrar_texto(self, texto, cor=None):
        if self._exibir_mensagem:
            self._exibir_mensagem(texto, cor)

    def pack(self, **kw):
        pass

    def pack_forget(self):
        pass

    def grid(self, **kw):
        pass

    def place(self, **kw):
        pass

    def destroy(self):
        self._destruido = True
        self._binds.clear()
        self._filhos.clear()


# --------------------------------------------------------------------------
# Módulos `tkinter` e `customtkinter` inertes
# --------------------------------------------------------------------------

def _nada(*args, **kwargs):
    return None


class WidgetInerte:
    """
    Qualquer widget do (custom)tkinter no navegador.

    Os arquivos originais importam tkinter/customtkinter no topo (ex.: problems_bank,
    step_view, logging_system) mesmo quando só queremos a lógica deles. Este widget
    aceita qualquer chamada e não desenha nada: a interface web é feita em React.
    """

    def __init__(self, master=None, *args, **kwargs):
        self.master = master
        self.opcoes = dict(kwargs)
        if isinstance(master, QuadroWeb):
            master._registrar_filho(self)

    def __getattr__(self, nome):
        if nome.startswith("__"):
            raise AttributeError(nome)
        return _nada

    def destroy(self):
        if isinstance(self.master, QuadroWeb):
            self.master._remover_filho(self)


class LabelWeb(WidgetInerte):
    """
    tk.Label criado dentro do QuadroWeb. O código original usa isso para mostrar
    erros no lugar do pygame, ex.:
        tk.Label(self.parent_frame, text=f"Erro Pygame: {e}", fg="red", bg="black").pack()
    """

    def pack(self, *args, **kwargs):
        if isinstance(self.master, QuadroWeb):
            self.master._mostrar_texto(self.opcoes.get("text", ""), self.opcoes.get("fg"))

    grid = pack
    place = pack


class TclError(Exception):
    pass


def _modulo_inerte(nome, extras=None):
    modulo = types.ModuleType(nome)
    modulo.__file__ = f"<lozweb:{nome}>"

    def __getattr__(attr):
        if attr.startswith("__"):
            raise AttributeError(attr)
        return WidgetInerte

    modulo.__getattr__ = __getattr__
    for chave, valor in (extras or {}).items():
        setattr(modulo, chave, valor)
    return modulo


def instalar_tkinter_inerte():
    """Registra `tkinter` e `customtkinter` em sys.modules (o Pyodide não tem Tk)."""
    tk = _modulo_inerte(
        "tkinter",
        {
            "Label": LabelWeb,
            "TclError": TclError,
            "END": "end",
            "INSERT": "insert",
            "NORMAL": "normal",
            "DISABLED": "disabled",
            "Widget": WidgetInerte,
            "Frame": WidgetInerte,
            "Tk": WidgetInerte,
            "Toplevel": WidgetInerte,
        },
    )
    tk.__path__ = []  # permite `from tkinter import filedialog`
    filedialog = _modulo_inerte("tkinter.filedialog")
    scrolledtext = _modulo_inerte("tkinter.scrolledtext")
    tk.filedialog = filedialog
    tk.scrolledtext = scrolledtext

    ctk = _modulo_inerte("customtkinter", {"CTkLabel": LabelWeb})

    sys.modules["tkinter"] = tk
    sys.modules["tkinter.filedialog"] = filedialog
    sys.modules["tkinter.scrolledtext"] = scrolledtext
    sys.modules["customtkinter"] = ctk
