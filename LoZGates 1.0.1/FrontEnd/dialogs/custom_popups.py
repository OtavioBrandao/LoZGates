import tkinter as tk
from config import apply_window_icon
from FrontEnd.utils.responsive import calculate_window_layout

def popup_erro(mensagem, parent=None):
    popup = tk.Toplevel(parent)
    popup.attributes('-topmost', True)
    popup.after(10, lambda: popup.attributes('-topmost', False))
    popup.title("Erro")
    
    try:
        apply_window_icon(popup)
    except Exception:
        pass

    popup_layout = calculate_window_layout(
        popup.winfo_screenwidth(),
        popup.winfo_screenheight(),
        preferred=(460, 180),
        minimum=(320, 160),
        margin=24,
    )
    popup.geometry(popup_layout.geometry)

    # Cor de fundo
    popup.configure(bg="#1a1a1a")

    # Conteúdo
    label = tk.Label(
        popup,
        text=mensagem,
        font=("Segoe UI", 11),
        fg="white",
        bg="#1a1a1a",
        wraplength=max(260, popup_layout.width - 50),
    )
    label.pack(pady=(20, 10))

    botao_ok = tk.Button(popup, text="OK", bg="#7A2020", fg="white", command=popup.destroy)
    botao_ok.configure(width=8, height=1)
    botao_ok.pack(pady=(0, 10))


def popup_duvida(mensagem, parent=None):
    popup = tk.Toplevel(parent)
    popup.attributes('-topmost', True)
    popup.after(10, lambda: popup.attributes('-topmost', False))
    popup.title("Ajuda")
    
    try:
        apply_window_icon(popup)
    except Exception:
        pass
        
    popup.configure(bg="#1a1a1a")
    # Cria o textbox e insere a mensagem de ajuda/informação
    textbox = tk.Text(popup, wrap="word", font=("Trebuchet MS", 12), fg="white", bg="#1a1a1a", borderwidth=0)
    textbox.pack(padx=10, pady=10, fill="both", expand=True)
    # Escreve a mensagem recebida + informações extras
    info_extra = "\n\nLoZ Gates - Ajuda\nEste aplicativo permite criar, visualizar e simplificar expressões de lógica proposicional.\nUse as abas para acessar circuitos, expressões e problemas reais."
    textbox.insert("1.0", info_extra + mensagem)
    textbox.configure(state="disabled")

    popup_layout = calculate_window_layout(
        popup.winfo_screenwidth(),
        popup.winfo_screenheight(),
        preferred=(520, 520),
        minimum=(340, 320),
        margin=24,
    )
    popup.geometry(popup_layout.geometry)
