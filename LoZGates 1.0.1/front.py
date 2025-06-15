import customtkinter as ctk
from PIL import Image, ImageTk 
import threading
import tkinter as tk
from tkinter import font
import os
from imagem import converte_matrix_para_tkinter_imagem_icon
from tabela import gerar_tabela_verdade, verificar_conclusao
from converter import converter_para_algebra_booleana
from equivalencia import tabela
botao_ver_circuito = None

# Configuração inicial
ctk.set_appearance_mode("dark")  # Modo escuro
ctk.set_default_color_theme("blue")  # Tema azul

janela = ctk.CTk()
janela.title("LoZ Gates")
largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()
largura = int(largura_tela * 0.8)
altura = int(altura_tela * 0.8)

janela.geometry(f"{largura}x{altura}")

bytes_per_row = 32  # Número de bytes por linha na matriz
icon = converte_matrix_para_tkinter_imagem_icon(bytes_per_row)
janela.iconbitmap(icon)
janela.resizable(False, False)

# Função para alternar entre os frames
def show_frame(frame):
    frame.tkraise()
    
import time

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
    
    # Remove imagem antiga se existir
    caminho_imagem = os.path.join(pasta_base, "assets", "circuito.png")
    if os.path.exists(caminho_imagem):
        os.remove(caminho_imagem)

    # Executa o Pygame em uma thread
    thread = threading.Thread(target=rodar_pygame)
    thread.start()

    # Espera a imagem ser criada antes de continuar
    def aguardar_imagem():
        tempo_max = 5  # segundos
        tempo_passado = 0
        while not os.path.exists(caminho_imagem) and tempo_passado < tempo_max:
            time.sleep(0.1)
            tempo_passado += 0.1
        if os.path.exists(caminho_imagem):
            atualizar_imagem_circuito()
        else:
            print("Erro: A imagem do circuito não foi criada a tempo.")

    # Espera a imagem num thread separado para não travar a GUI
    threading.Thread(target=aguardar_imagem).start()


def trocar_para_abas():
    pasta_base = os.path.dirname(os.path.abspath(__file__))
    pasta_assets = os.path.join(pasta_base, "assets")
    os.makedirs(pasta_assets, exist_ok=True)

    # Caminho para salvar o arquivo entrada.txt dentro de assets
    caminho_entrada = os.path.join(pasta_assets, "entrada.txt")

    expressao = entrada.get().strip().upper().replace(" ", "")
    with open(caminho_entrada, "w", encoding="utf-8") as file: 
        file.write(expressao) 

    saida = converter_para_algebra_booleana(expressao)

    ver_circuito_pygame(saida)
    show_frame(frame_abas)
    def aguarda_e_mostra():
        # espera o circuito ser salvo e imagem estar disponível
        caminho_img = os.path.join(pasta_base, "assets", "circuito.png")
        for _ in range(50):  # 50 tentativas ~5s
            if os.path.exists(caminho_img):
                break
            time.sleep(0.1)
        atualizar_imagem_circuito()
        janela.after(0, lambda: show_frame(frame_abas))  # mostra o frame principal na thread da GUI

    threading.Thread(target=aguarda_e_mostra).start()


def confirmar_expressao():
    global botao_ver_circuito
    if botao_ver_circuito:  # Se já existir, destrói e recria
        botao_ver_circuito.destroy()

    botao_ver_circuito = ctk.CTkButton(
        principal, 
        text="Ver Circuito / Expressão", 
        fg_color="#B0E0E6", 
        text_color="#000080", 
        hover_color="#8B008B", 
        border_width=2,
        border_color="#708090",
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=lambda: trocar_para_abas())
    botao_ver_circuito.place(relx=0.5, y=500, anchor="center")


def exibir_tabela_verdade(expressao):
        # Cria uma nova janela
        janela_tabela = ctk.CTkToplevel(janela)
        janela_tabela.title("Tabela Verdade")
        janela_tabela.geometry("400x400")
        janela_tabela.lift()               # Traz para frente
        janela_tabela.attributes('-topmost', True)  # Mantém no topo
        janela_tabela.after(10, lambda: janela_tabela.attributes('-topmost', False))
        # Gera a tabela verdade usando a função do backend
        variaveis, combinacoes, resultados = gerar_tabela_verdade(expressao)

        # Cria um frame para exibir a tabela verdade
        frame_tabela = ctk.CTkFrame(janela_tabela)
        frame_tabela.pack(pady=10, padx=10, fill="both", expand=True)

        # Cria um label para o cabeçalho da tabela
        cabecalho = " ".join(variaveis) + " | Resultado"
        label_cabecalho = ctk.CTkLabel(frame_tabela, text=cabecalho, font=("Arial", 20))
        label_cabecalho.pack()

        # Adiciona uma linha separadora
        separador = ctk.CTkLabel(frame_tabela, text="-" * (len(variaveis) * 3 + 12))
        separador.pack()

        # Adiciona as linhas da tabela
        for valores, resultado in zip(combinacoes, resultados):
            linha = " ".join(str(int(v)) for v in valores) + " | " + str(int(resultado))
            label_linha = ctk.CTkLabel(frame_tabela, text=linha, font=("Arial", 20))
            label_linha.pack()

        # Verifica a conclusão da expressão
        conclusao = verificar_conclusao(resultados)
        label_conclusao = ctk.CTkLabel(frame_tabela, text=conclusao, font=("Arial", 14, "bold"))
        label_conclusao.pack(pady=10)

def comparar():
    expressao2 = entrada2.get().strip().upper()
    expressao3 = entrada3.get().strip().upper()
    
    if not expressao2 or not expressao3:
        print("As expressões não podem estar vazias.")
        return
    
    valor = tabela(expressao2, expressao3)
    
    if valor == 1:
        equivalente.place(relx=0.5, y=300, anchor="center")
        nao_equivalente.place_forget()
    else:
        nao_equivalente.place(relx=0.5, y=300, anchor="center")
        equivalente.place_forget()
        
def voltar_para(frame):
    global botao_ver_circuito
    if botao_ver_circuito:
        botao_ver_circuito.destroy()
        botao_ver_circuito = None

    # limpa as entradas
    entrada.delete(0, tk.END) 
    entrada2.delete(0, tk.END)  
    entrada3.delete(0, tk.END) 
    
    # escreve digite aqui
    entrada.configure(placeholder_text="Digite aqui")
    entrada2.configure(placeholder_text="Digite aqui")
    entrada3.configure(placeholder_text="Digite aqui")
    
    # limpa o "é equivalente e o não é equivalente"
    equivalente.place_forget()
    nao_equivalente.place_forget()

    show_frame(frame)  # troca o frame

    # Força o foco para a janela (tira o foco de qualquer campo antigo)
    janela.focus_set()

    # Se voltando para a tela principal, seta foco corretamente
    if frame == principal:
        entrada.focus_set()


def atualizar_imagem_circuito():
    caminho_img = os.path.join(pasta_base, "assets", "circuito.png")
    if os.path.exists(caminho_img):
        imagem_pil = Image.open(caminho_img)
        imagem_tk = ImageTk.PhotoImage(imagem_pil)
        imagem_circuito.configure(image=imagem_tk, text="")  # remove o texto
        imagem_circuito.image = imagem_tk  # mantém referência
        
# Frames principais
frame_inicio = ctk.CTkFrame(
    janela, 
    width=largura, 
    height=altura, 
    fg_color="#000057")

principal = ctk.CTkFrame(
    janela, 
    width=largura, 
    height=altura, 
    fg_color="#000057")

frame_equivalencia = ctk.CTkFrame(
    janela,
    width=largura,
    height=altura,
    fg_color="#000057")

frame_escolha = ctk.CTkFrame(
    janela,
    width=largura,
    height=altura,
    fg_color="#000057")
frame_abas = ctk.CTkFrame(
    janela,
    width=largura,
    height=altura,
    fg_color="#000057")
for frame in (frame_inicio, principal, frame_equivalencia, frame_escolha, frame_abas):
    frame.place(relx=0.5, rely=0.5, anchor="center")

    
# ---------------- Frame de Início ----------------
frame_inicio_conteudo = ctk.CTkFrame(
    frame_inicio, 
    fg_color="#000057", 
    corner_radius=30)

frame_inicio_conteudo.place(
    relx=0.5, 
    rely=0.5, 
    anchor="center")

from customtkinter import CTkFont
import os

# Caminho da fonte Momentz.ttf dentro da pasta assets (opcional agora)
pasta_base = os.path.dirname(os.path.abspath(__file__))
caminho_fonte = os.path.join(pasta_base, "assets", "Momentz.ttf")

fonte_momentz = CTkFont(family="Momentz", size=30)

# Exemplo de uso
label_inicio = ctk.CTkLabel(
    frame_inicio_conteudo,
    text="LoZ Gates",
    font=fonte_momentz,
    text_color="white",
    fg_color="#000057"
)
label_inicio.pack(pady=30)

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
botao_start.pack(pady=30)

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
botao_info.pack(pady=20)

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
botao_tarefas.place(relx=0.5, y=300, anchor="center")

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
botao_equivalencia.place(relx=0.5, y=400, anchor="center")    
    
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
    command=lambda: voltar_para(frame_inicio))
botao_voltar4.place(relx=0.5, y=500, anchor="center")

# ---------------- Frame de Tarefas----------------
label_tarefas = ctk.CTkLabel(
    principal, 
    text="Digite a expressão em Lógica Proposicional:", 
    font=("Arial Bold", 20), 
    text_color="white", 
    fg_color=None)
label_tarefas.place(relx=0.5, y=150, anchor="center")

entrada = ctk.CTkEntry(
    principal, 
    width=300, 
    placeholder_text="Digite aqui", 
    font=("Arial", 14))
entrada.place(relx=0.5, y=200, anchor="center")

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
    command= confirmar_expressao)
bot.place(relx=0.5, y=300, anchor="center")

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
    command=lambda: voltar_para(frame_escolha))
botao_voltar1.place(relx=0.5, y=400, anchor="center")
# ---------------- Frame de Abas----------------
# Criar o novo frame com abas
frame_abas = ctk.CTkFrame(janela, width=largura, height=altura, fg_color="#000057")
frame_abas.place(x=0, y=0)

abas = ctk.CTkTabview(frame_abas, width=largura, height=altura, fg_color="#000057")
abas.pack()

# Aba do circuito
aba_circuito = abas.add("      Circuito      ")
imagem_circuito = ctk.CTkLabel(aba_circuito, text="")
imagem_circuito.pack()

# Aba da expressão
aba_expressao = abas.add("      Expressão      ")
label_simplificacao = ctk.CTkLabel(aba_expressao, text="Tabela da Verdade")
label_simplificacao.pack()

botao_tabela = ctk.CTkButton(aba_expressao, text="Tabela Verdade", command=lambda:exibir_tabela_verdade(entrada.get().strip().upper())) 
botao_tabela.pack()

botao_voltar5 = ctk.CTkButton(
    frame_abas,
    text="Voltar", 
    fg_color="goldenrod", 
    text_color="#000080", 
    hover_color="#8B008B", 
    border_width=2,
    border_color="#708090",
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: voltar_para(principal))
botao_voltar5.place(relx=0.5, y=700, anchor="center")


# ---------------- Frame de Informações ----------------
frame_info = ctk.CTkFrame(janela, width=largura, height=altura, fg_color="#000057")
frame_info.place(x=0, y=0)


textbox_info = ctk.CTkTextbox(
    frame_info, 
    width=600, 
    height=300, 
    font=("Arial", 20), 
    text_color="white", 
    fg_color="#000057"
)
textbox_info.place(relx=0.5, rely=0.4, anchor="center")

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
3- Comparar expressões
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
    command=lambda: voltar_para(frame_inicio))
botao_voltar2.place(relx=0.5, rely=0.85, anchor="center")

 # ---------------- Frame de Equivalência ----------------
label_escolha = ctk.CTkLabel(
        frame_escolha, 
        text="Escolha a opção desejada:", 
        font=("Arial Bold", 20), 
        text_color="white", 
        fg_color=None)
label_escolha.place(relx=0.5, y=200, anchor="center")

entrada2 = ctk.CTkEntry(
        frame_equivalencia,
        width=300,
        placeholder_text="Digite aqui",
        font=("Arial", 14))
entrada2.place(relx=0.5, y=200, anchor="center")

entrada3 = ctk.CTkEntry(
        frame_equivalencia,
        width=300,
        placeholder_text="Digite aqui",
        font=("Arial", 14))
entrada3.place(relx=0.5, y=250, anchor="center")

botao_comparar = ctk.CTkButton(
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
        command=comparar)
botao_comparar.place(relx=0.5, y=350, anchor="center")

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
    command=lambda: voltar_para(frame_escolha))
botao_voltar3.place(relx=0.5, y=420, anchor="center")

titulo = ctk.CTkLabel(
        frame_equivalencia, 
        text="Digite a expressão para comparar:", 
        font=("Arial Bold", 20), 
        text_color="white", 
        fg_color=None)
titulo.place(relx=0.5, y=130, anchor="center")

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
