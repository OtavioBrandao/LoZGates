"""
Roda o LoZ Gates DESKTOP original (FrontEnd/interface.py) sob Xvfb e aperta os botões
de verdade (.invoke()), registrando o que aparece nos widgets. Serve para comparar com
a versão web executando a mesma sequência de cliques.
"""
import json
import os
import sys
import tkinter as tk

from pathlib import Path
APP = str(Path(__file__).resolve().parents[3])  # "LoZGates 1.0.1/"
sys.path.insert(0, APP)
os.chdir(sys.argv[2] if len(sys.argv) > 2 else os.getcwd())  # onde o logger grava seus .json

import customtkinter as ctk

# Diferença de plataforma (não de lógica): .ico não funciona como iconbitmap no Linux
tk.Wm.iconbitmap = lambda *a, **k: None
janelas = []
_ctk_init = ctk.CTk.__init__


def _init(self, *a, **k):
    _ctk_init(self, *a, **k)
    janelas.append(self)


ctk.CTk.__init__ = _init
ctk.CTk.mainloop = lambda self, *a, **k: None

import FrontEnd.interface as interface
import types
class _T:
    def __init__(self, target=None, args=(), kwargs=None, daemon=None, **k): self.t, self.a, self.k = target, args, kwargs or {}
    def start(self): self.t(*self.a, **self.k)
interface.threading = types.SimpleNamespace(Thread=_T)  # só no teste: não há mainloop, então as threads rodam na hora

interface.inicializar_interface()
janela = janelas[0]


def processar(n=30):
    for _ in range(n):
        janela.update()


def todos(widget):
    for filho in widget.winfo_children():
        yield filho
        yield from todos(filho)


def texto_de(w):
    try:
        return w.cget("text")
    except Exception:
        return None


def botao(texto_inicio, visivel=True):
    for w in todos(janela):
        if isinstance(w, ctk.CTkButton) and (texto_de(w) or "").startswith(texto_inicio):
            if not visivel or w.winfo_ismapped():
                return w
    raise RuntimeError(f"botão não encontrado: {texto_inicio}")


def popups():
    msgs = []
    for w in janela.winfo_children():
        if isinstance(w, (tk.Toplevel, ctk.CTkToplevel)):
            for filho in todos(w):
                t = texto_de(filho)
                if isinstance(filho, tk.Label) and t and t != "OK":
                    msgs.append(t)
            w.destroy()
    return msgs


def entrada():
    for w in todos(janela):
        if isinstance(w, ctk.CTkEntry) and w.cget("placeholder_text") == "Digite aqui":
            return w


def estado_interativo():
    cartoes = []
    for frame in interface.scroll_passos.winfo_children():
        textos = [texto_de(w) for w in todos(frame) if isinstance(w, ctk.CTkLabel) and texto_de(w)]
        cartoes.append(textos)
    leis = [w for w in todos(janela) if isinstance(w, ctk.CTkButton) and (texto_de(w) or "").split("\n")[0] in LEIS]
    return {
        "expressao": interface.label_expressao_inicial.cget("text"),
        "analise": interface.label_analise_atual.cget("text"),
        "cartoes": cartoes,
        "leis_habilitadas": all(b.cget("state") == "normal" for b in leis),
        "pular_habilitado": botao("↪ Pular").cget("state") == "normal",
        "desfazer_habilitado": botao("↩ Desfazer").cget("state") == "normal",
    }


LEIS = {"Inversa","Nula","Identidade","Idempotente","Absorção","De Morgan","Distributiva","Associativa","Comutativa"}
roteiro = json.loads(sys.argv[1])
saida = []
processar()
botao("💡Circuitos e Expressões").invoke()
processar()
e = entrada()
e.insert(0, roteiro["expressao"])
botao("✅Confirmar").invoke()
processar()
botao("🔌Ver Circuito").invoke()
processar(60)
popups()
interface_abas = [w for w in todos(janela) if isinstance(w, ctk.CTkTabview)][0]
interface_abas.set("      Expressão      ")
processar()
botao("🔗Realizar conversão").invoke()
processar()
botao("🔎Simplificar - Interativo").invoke()
processar()
saida.append({"acao": "iniciar", "estado": estado_interativo(), "popups": popups()})
for acao in roteiro["acoes"]:
    if acao == "pular":
        botao("↪ Pular").invoke()
    elif acao == "desfazer":
        botao("↩ Desfazer").invoke()
    else:
        leis = [w for w in todos(janela) if isinstance(w, ctk.CTkButton) and (texto_de(w) or "").split("\n")[0] in LEIS]
        leis[int(acao)].invoke()
    processar()
    saida.append({"acao": acao, "estado": estado_interativo(), "popups": popups()})
print("@@JSON@@" + json.dumps(saida, ensure_ascii=False))
