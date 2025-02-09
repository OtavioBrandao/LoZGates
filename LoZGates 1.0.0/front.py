import customtkinter as ctk
from PIL import Image  # Apenas Image, sem ImageTk
import threading

# Configuração inicial
ctk.set_appearance_mode("dark")  # Modo escuro
ctk.set_default_color_theme("blue")  # Tema azul

janela = ctk.CTk()
janela.title("LoZ Gates")
janela.geometry("1000x500")
janela.iconbitmap(r"C:\Users\Otávio\Desktop\Estudo e Trabalho\Códigos\Gerador de Circuito Lógico\LOZ_Logic_Gate_Icon.ico")
janela.resizable(False, False)

#C:\Users\Otávio\Desktop\Estudo e Trabalho\Códigos\Gerador de Circuito Lógico\icone.ico
# Carregar a imagem com CTkImage
#bg_image = ctk.CTkImage(Image.open(r"C:\Users\Otávio\Desktop\Estudo e Trabalho\Códigos\Gerador de Circuito Lógico\teste.png"), size=(1000, 500))

# Função para alternar entre os frames
def show_frame(frame):
    frame.tkraise()
    
def ver_circuito_pygame(expressao):
    def rodar_pygame():
        try:
            import circuito_logico
            if hasattr(circuito_logico, "plotar_circuito_logico"):
                circuito_logico.plotar_circuito_logico(expressao)
            else:
                print("Erro: A função 'plotar_circuito_logico' não foi encontrada no módulo 'circuito_logico'.")
        except ImportError as e:
            print(f"Erro ao importar 'circuito_logico': {e}")
    
    # Executa o Pygame em uma nova thread, pra o principal ainda ser o front
    threading.Thread(target=rodar_pygame).start()

def clicked():
    expressao = entrada.get()
    if not expressao.strip():
        print("Não pode estar vazio.")
        return
    expressao = expressao.upper()  # Converte para maiúsculas
    with open(r"C:\Users\Otávio\Desktop\Estudo e Trabalho\Códigos\Gerador de Circuito Lógico\entrada.txt", "w") as file:
        file.write(expressao)

   
    from converter import converter_para_algebra_booleana
    saida = converter_para_algebra_booleana(expressao)

    from tabela import gerar_tabela_verdade
    
    from karnaugh import analisar
    variaveis = analisar(expressao)
    from karnaugh import karnaugh_map 

    ver_circuito = ctk.CTkButton(
        principal, 
        text="Ver Circuito Lógico", 
        fg_color="#B0E0E6", 
        text_color="#000080", 
        hover_color="#8B008B", 
        border_width=2,
        border_color="#708090",
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=lambda: ver_circuito_pygame(saida))
    ver_circuito.place(x=100, y=400)
    
    label = ctk.CTkLabel(
        janela, 
        text=f"Expressão em Álgebra Booleana:\n {saida}", 
        fg_color="#000057", 
        text_color="white", 
        font=("Arial", 16))
    label.place(x=380, y=240)
    
    tabela_verdade = ctk.CTkButton(
        principal, 
        text="Tabela verdade", 
        fg_color="#B0E0E6", 
        text_color="#000080", 
        hover_color="#8B008B", 
        border_width=2,
        border_color="#708090",
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=lambda: gerar_tabela_verdade(expressao))
    tabela_verdade.place(x=100, y=200)
    
    karnaugh = ctk.CTkButton(
        principal, 
        text="Mapa de Karnaugh",
        fg_color="#B0E0E6", 
        text_color="#000080", 
        hover_color="#8B008B", 
        border_width=2,
        border_color="#708090",
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=lambda: karnaugh_map(expressao, variaveis))
    karnaugh.place(x=100, y=300)

from equivalencia import tabela

def clicked2():
    expressao2 = entrada2.get().strip().upper()
    expressao3 = entrada3.get().strip().upper()
    
    if not expressao2 or not expressao3:
        print("As expressões não podem estar vazias.")
        return
    
    valor = tabela(expressao2, expressao3)
    
    if valor == 1:
        equivalente.place(x=423, y=300)
        nao_equivalente.place_forget()
    else:
        nao_equivalente.place(x=415, y=300)
        equivalente.place_forget()
         
# Frames principais
frame_inicio = ctk.CTkFrame(
    janela, 
    width=1000, 
    height=500, 
    fg_color="#000057")

principal = ctk.CTkFrame(
    janela, 
    width=1000, 
    height=500, 
    fg_color="#000057")

frame_equivalencia = ctk.CTkFrame(
    janela,
    width=1000,
    height=500,
    fg_color="#000057")

frame_escolha = ctk.CTkFrame(
    janela,
    width=1000,
    height=500,
    fg_color="#000057")

for frame in (frame_inicio, principal, frame_equivalencia, frame_escolha):
    frame.place(x=0, y=0)
    
    '''bg_label = ctk.CTkLabel(
        frame, 
        image=bg_image, 
        text="")'''
    
    '''bg_label.place(
        x=0, 
        y=0, 
        relwidth=1, 
        relheight=1)'''
    
# ---------------- Frame de Início ----------------
frame_inicio_conteudo = ctk.CTkFrame(
    frame_inicio, 
    fg_color="#000057", 
    corner_radius=30)

frame_inicio_conteudo.place(
    relx=0.5, 
    rely=0.5, 
    anchor="center")

label_inicio = ctk.CTkLabel(
    frame_inicio_conteudo, 
    text="LoZ Gates", 
    font=("Arial Bold", 30), 
    text_color="white", 
    fg_color="#000057")
label_inicio.pack(pady=20)

botao_start = ctk.CTkButton(
    frame_inicio_conteudo, 
    text="Começar", 
    fg_color="#B0E0E6", 
    text_color="#000080", 
    hover_color="#8B008B",
    border_width=2,
    border_color="#708090",
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(frame_escolha))
botao_start.pack(pady=10)

botao_info = ctk.CTkButton(
    frame_inicio_conteudo, 
    text="Informações", 
    fg_color="#B0E0E6", 
    text_color="#000080", 
    hover_color="#8B008B", 
    border_width=2,
    border_color="#708090",
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(frame_info))
botao_info.pack(pady=10)

# ---------------- Frame de Escolha ----------------
botao_tarefas = ctk.CTkButton(
    frame_escolha,
    text="Circuitos",
    fg_color="#B0E0E6",
    text_color="#000080",
    hover_color="#8B008B",
    border_width=2,
    border_color="#708090",
    width=200,
    height=50,
    font=("Arial", 16),
    command=lambda: show_frame(principal))
botao_tarefas.place(x=400, y=200)

botao_equivalencia = ctk.CTkButton(
        frame_escolha,
        text="Equivalência",
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        width=200,
        height=50,
        font=("Arial", 16),
        command=lambda: show_frame(frame_equivalencia))
botao_equivalencia.place(x=400, y=300)    
    
botao_voltar4 = ctk.CTkButton(
        frame_escolha,
        text="Voltar", 
        fg_color="goldenrod", 
        text_color="#000080", 
        hover_color="#8B008B", 
        border_width=2,
        border_color="#708090",
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=lambda: show_frame(frame_inicio))
botao_voltar4.place(x=400, y=400)

# ---------------- Frame de Tarefas ----------------
label_tarefas = ctk.CTkLabel(
    principal, 
    text="Digite a expressão em Lógica Proposicional:", 
    font=("Arial Bold", 20), 
    text_color="white", 
    fg_color=None)
label_tarefas.place(x=300, y=130)

entrada = ctk.CTkEntry(
    principal, 
    width=300, 
    placeholder_text="Digite aqui", 
    font=("Arial", 14))
entrada.place(x=350, y=200)

bot = ctk.CTkButton(
    principal, 
    text="Confirmar", 
    fg_color="#B0E0E6", 
    text_color="#000080", 
    hover_color="#8B008B", 
    border_width=2,
    border_color="#708090",
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command= clicked)
bot.place(x=400, y=300)

botao_voltar1 = ctk.CTkButton(
    principal, 
    text="Voltar", 
    fg_color="goldenrod", 
    text_color="#000080", 
    hover_color="#8B008B", 
    border_width=2,
    border_color="#708090",
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(frame_escolha))
botao_voltar1.place(x=400, y=400)


# ---------------- Frame de Informações ----------------
frame_info = ctk.CTkFrame(janela, width=1000, height=500, fg_color="#000057")
frame_info.pack(fill="both", expand=True, padx=0, pady=0)

textbox_info = ctk.CTkTextbox(frame_info, width=600, height=300, font=("Arial", 20), text_color="white")
textbox_info.pack(pady=20)

# Definindo o conteúdo do Textbox
info_text = """
Alunos responsáveis:
Larissa de Souza, Otávio Menezes e Zilderlan Santos.
================================================

Átomos aceitos:
P, Q, R, S e T.

Representação de símbolos:
'&' (e), '|' (ou), '!' (não) e '>' (implica).

---------------------------------Atenção:-------------------------------
O usuário consegue realizar as seguintes funções:
1- Ver o circuito equivalente
2- Tabela verdade
3- Mapa de Karnaugh
4- Comparar expressões
================================================

Universidade Federal de Alagoas
Instituto de Computação
Professor Doutor Evandro de Barros Costa
================================================
"""

textbox_info.insert("0.0", info_text)  # Inserir o texto no Textbox
textbox_info.configure(state="disable")  # Desativar edição para evitar modificações

botao_voltar2 = ctk.CTkButton(
    frame_info, 
    text="Voltar", 
    fg_color="goldenrod", 
    text_color="#000080", 
    hover_color="#8B008B", 
    border_width=2,
    border_color="#708090",
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(frame_inicio))
botao_voltar2.place(x=400, y=400)

 # ---------------- Frame de Equivalência ----------------
label_escolha = ctk.CTkLabel(
        frame_escolha, 
        text="Escolha a opção desejada:", 
        font=("Arial Bold", 20), 
        text_color="white", 
        fg_color=None)
label_escolha.place(x=385, y=130)

entrada2 = ctk.CTkEntry(
        frame_equivalencia,
        width=300,
        placeholder_text="Digite aqui",
        font=("Arial", 14))
entrada2.place(x=350, y=200)

entrada3 = ctk.CTkEntry(
        frame_equivalencia,
        width=300,
        placeholder_text="Digite aqui",
        font=("Arial", 14))
entrada3.place(x=350, y=250)

botao_confirmar2 = ctk.CTkButton(
        frame_equivalencia, 
        text="Confirmar", 
        fg_color="#B0E0E6", 
        text_color="#000080", 
        hover_color="#8B008B", 
        border_width=2,
        border_color="#708090",
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=clicked2)
botao_confirmar2.place(x=400, y=350)

botao_voltar3 = ctk.CTkButton(
        frame_equivalencia, 
        text="Voltar", 
        fg_color="goldenrod", 
        text_color="#000080", 
        hover_color="#8B008B", 
        border_width=2,
        border_color="#708090",
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=lambda: show_frame(frame_escolha))
botao_voltar3.place(x=400, y=420)

titulo = ctk.CTkLabel(
        frame_equivalencia, 
        text="Digite a expressão para comparar:", 
        font=("Arial Bold", 20), 
        text_color="white", 
        fg_color=None)
titulo.place(x=350, y=130)

equivalente = ctk.CTkLabel(
        frame_equivalencia, 
        text="É equivalente :)", 
        font=("Arial Bold", 20), 
        text_color="white", 
        fg_color=None)

nao_equivalente = ctk.CTkLabel(
        frame_equivalencia, 
        text="Não é equivalente :(", 
        font=("Arial Bold", 20), 
        text_color="white", 
        fg_color=None)

# Exibe o frame inicial
show_frame(frame_inicio)

# Loop principal
janela.mainloop()