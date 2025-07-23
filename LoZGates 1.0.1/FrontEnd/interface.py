import customtkinter as ctk
import threading
import tkinter as tk
import os
import sys
from PIL import Image, ImageTk, ImageOps
from tkinter import font
from BackEnd.imagem import converte_matrix_para_tkinter_imagem_icon
from BackEnd.tabela import gerar_tabela_verdade, verificar_conclusao
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.equivalencia import tabela
from config import ASSETS_PATH
import time
from customtkinter import CTkFont
import webbrowser
import urllib.parse
from BackEnd.identificar_lei import principal_simplificar, simplificar
from contextlib import redirect_stdout


botao_ver_circuito = None
label_convertida = None

def inicializar_interface():

    # Configuração inicial
    ctk.set_appearance_mode("dark")  # Modo escuro
    ctk.set_default_color_theme("blue")  # Tema azul

    janela = ctk.CTk()
    janela.title("LoZ Gates")
    janela.configure(bg="#000057")
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    largura = int(largura_tela * 0.8)
    altura = int(altura_tela * 0.8)

    janela.geometry(f"{largura}x{altura}")
    janela.grid_rowconfigure(0, weight=1)
    janela.grid_columnconfigure(0, weight=1)


    bytes_per_row = 32  # Número de bytes por linha na matriz
    icon = converte_matrix_para_tkinter_imagem_icon(bytes_per_row)
    janela.iconbitmap(icon)
    janela.resizable(True, True)

    # Função para alternar entre os frames
    def show_frame(frame):
        frame.tkraise()

    def ver_circuito_pygame(expressao):
        def rodar_pygame():
            try:
                import BackEnd.circuito_logico
                if hasattr(BackEnd.circuito_logico, "plotar_circuito_logico"):
                    BackEnd.circuito_logico.plotar_circuito_logico(expressao)
                else:
                    popup_erro("Erro: A função 'plotar_circuito_logico' não foi encontrada no módulo 'circuito_logico'.")
            except ImportError as e:
                popup_erro(f"Erro ao importar 'circuito_logico': {e}")
        
        # Remove imagem antiga se existir
        caminho_imagem = os.path.join(ASSETS_PATH, "circuito.png")
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
                popup_erro("Erro: A imagem do circuito não foi criada a tempo.")

        # Espera a imagem num thread separado para não travar a GUI
        threading.Thread(target=aguardar_imagem).start()

    def popup_erro(mensagem):
        popup = ctk.CTkToplevel(janela)
        popup.attributes('-topmost', True)
        popup.after(10, lambda: popup.attributes('-topmost', False))
        popup.title("Erro")

        # Tamanho e centralização
        largura_popup = 300
        altura_popup = 120
        popup.geometry(f"{largura_popup}x{altura_popup}")
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (largura_popup // 2)
        y = (popup.winfo_screenheight() // 2) - (altura_popup // 2)
        popup.geometry(f"{largura_popup}x{altura_popup}+{x}+{y}")

        # Cor de fundo
        popup.configure(fg_color="#1a1a1a")  # fundo escuro

        # Conteúdo
        label = ctk.CTkLabel(
            popup,
            text=mensagem,
            font=("Arial", 14),
            text_color="white"
        )
        label.pack(pady=(20, 10))

        botao_ok = ctk.CTkButton(
            popup,
            text="OK",
            fg_color="red",
            text_color="white",
            hover_color="#8B0000",
            command=popup.destroy
        )
        botao_ok.pack(pady=(0, 10))


    def trocar_para_abas():
        caminho_entrada = os.path.join(ASSETS_PATH, "entrada.txt")

        expressao = entrada.get().strip().upper().replace(" ", "")

        label_circuito_expressao.configure(text=f"Expressão Lógica Proposicional: {expressao}")
        
        with open(caminho_entrada, "w", encoding="utf-8") as file: 
            file.write(expressao) 

        saida = converter_para_algebra_booleana(expressao)

        ver_circuito_pygame(saida)
        show_frame(frame_abas)
        def aguarda_e_mostra():
            # espera o circuito ser salvo e imagem estar disponível
            caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
            for _ in range(50):  # 50 tentativas ~5s
                if os.path.exists(caminho_img):
                    break
                time.sleep(0.1)
            atualizar_imagem_circuito()
            janela.after(0, lambda: show_frame(frame_abas))  # mostra o frame principal na thread da GUI

        threading.Thread(target=aguarda_e_mostra).start()


    def confirmar_expressao():
        global botao_ver_circuito
        if botao_ver_circuito:  
            botao_ver_circuito.destroy()

        if not entrada.get().strip():
            popup_erro("A expressão não pode estar vazia.")
            return
        
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
        janela_tabela = ctk.CTkToplevel(janela)
        janela_tabela.title("Tabela Verdade")
        janela_tabela.geometry("800x600") #Aumentei a largura para caber, ja que nao sei colocar scroll pro lado
        janela_tabela.lift()
        janela_tabela.attributes('-topmost', True)
        janela_tabela.after(10, lambda: janela_tabela.attributes('-topmost', False))

        #Gera a tabela verdade usando a função do backend
        dados_tabela = gerar_tabela_verdade(expressao)
        
        #Extrai os dados do dicionário retornado
        colunas = dados_tabela["colunas"]
        tabela = dados_tabela["tabela"]
        resultados_finais = dados_tabela["resultados_finais"]

        #Cria um frame para exibir a tabela verdade
        frame_tabela = ctk.CTkScrollableFrame(janela_tabela)
        frame_tabela.pack(pady=10, padx=10, fill="both", expand=True)

        cabecalho_str = " | ".join([f"{col:^10}" for col in colunas])
        label_cabecalho = ctk.CTkLabel(frame_tabela, text=cabecalho_str, font=("Consolas", 14, "bold"))
        label_cabecalho.pack(pady=(5, 0))

        separador_str = "-".join(["-" * 10 for _ in colunas])
        separador = ctk.CTkLabel(frame_tabela, text=separador_str, font=("Consolas", 14))
        separador.pack()

        #Adiciona as linhas da tabela
        for linha_valores in tabela:
            linha_str = " | ".join([f"{str(val):^10}" for val in linha_valores])
            label_linha = ctk.CTkLabel(frame_tabela, text=linha_str, font=("Consolas", 14))
            label_linha.pack()

        #Verifica a conclusão da expressão (Tautologia, Contradição ou Satisfatível)
        conclusao = verificar_conclusao(resultados_finais)
        label_conclusao = ctk.CTkLabel(frame_tabela, text=conclusao, font=("Arial", 16, "bold"))
        label_conclusao.pack(pady=20)

    def comparar():
        expressao2 = entrada2.get().strip().upper()
        expressao3 = entrada3.get().strip().upper()
        
        if not expressao2 or not expressao3:
            popup_erro("As expressões não podem estar vazias.")
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
        if frame not in [frame_abas, frame_resolucao_direta, frame_educacional, frame_interativo]:
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
        
        # Esconde os resultados da aba de expressão ao voltar apenas se NÃO for para frame_abas
        if frame != frame_abas:
            label_convertida.pack_forget()
            log_simplificacao_textbox.pack_forget()
            botao_simplificacao.pack_forget()

        show_frame(frame)  # troca o frame

        # Força o foco para a janela (tira o foco de qualquer campo antigo)
        janela.focus_set()

        # Se voltando para a tela principal, seta foco corretamente
        if frame == principal:
            entrada.focus_set()
        
        label_convertida.pack_forget()
    
    def atualizar_imagem_circuito():
        caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
        if os.path.exists(caminho_img):
            imagem_pil = Image.open(caminho_img)

            # Adiciona borda branca de 10px
            borda = 10
            imagem_com_borda = ImageOps.expand(imagem_pil, border=borda, fill="white")

            imagem_tk = ImageTk.PhotoImage(imagem_com_borda)
            imagem_circuito.configure(image=imagem_tk, text="")
            imagem_circuito.image = imagem_tk  # Mantém uma referência à imagem para evitar que seja coletada pelo garbage collector
    
    # Definição de cada frame do app
    frame_inicio = ctk.CTkFrame(janela, fg_color="#000057")
    frame_inicio.grid(row=0, column=0, sticky="nsew")

    principal = ctk.CTkFrame(janela, fg_color="#000057")
    principal.grid(row=0, column=0, sticky="nsew")

    frame_equivalencia = ctk.CTkFrame(janela, fg_color="#000057")
    frame_equivalencia.grid(row=0, column=0, sticky="nsew")

    frame_escolha = ctk.CTkFrame(janela, fg_color="#000057")
    frame_escolha.grid(row=0, column=0, sticky="nsew")

    frame_abas = ctk.CTkFrame(janela, fg_color="#000057")
    frame_abas.grid(row=0, column=0, sticky="nsew")

    frame_educacional = ctk.CTkFrame(janela, fg_color="#000057")
    frame_educacional.grid(row=0, column=0, sticky="nsew")


    frame_resolucao_direta = ctk.CTkFrame(janela, fg_color="#000057")
    frame_resolucao_direta.grid(row=0, column=0, sticky="nsew")

    scroll_conteudo = ctk.CTkScrollableFrame(frame_resolucao_direta, fg_color="#000057")
    scroll_conteudo.pack(expand=True, fill="both", padx=20, pady=20)


    frame_interativo = ctk.CTkFrame(janela, fg_color="#000057")
    frame_interativo.grid(row=0, column=0, sticky="nsew")

    frame_problemas_reais = ctk.CTkFrame(janela, fg_color="#000057")
    frame_problemas_reais.grid(row=0, column=0, sticky="nsew")

    frame_explicacao_problemas_reais = ctk.CTkFrame(janela, fg_color="#000057")
    frame_explicacao_problemas_reais.grid(row=0, column=0, sticky="nsew")


    # ---------------- Frame de Início ----------------
    frame_inicio_conteudo = ctk.CTkFrame(
        frame_inicio, 
        fg_color="#000057", 
        corner_radius=30)

    frame_inicio_conteudo.pack(expand=True)


    frame_inicio_conteudo.place(
        relx=0.5, 
        rely=0.5, 
        anchor="center")

    caminho_fonte = os.path.join(ASSETS_PATH, "Momentz.ttf")
    fonte_momentz = CTkFont(family="Momentz", size=30)

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
        width=250,
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
            width=250,
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

    # ---------------- Frame dos Circuitos e expressões----------------
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

    botao_problemas_reais = ctk.CTkButton(
        principal,
        text="Problemas Reais",
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        width=200,
        height=50,
        font=("Arial", 16),
        command=lambda: (show_frame(frame_problemas_reais), problemas_reais())
    )
    botao_problemas_reais.place(relx=0.5, y=400, anchor="center")

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
    botao_voltar1.place(relx=0.5, y=500, anchor="center")
    # ---------------- Frames dos problemas reais ----------------
     
    def problemas_reais():

        label_problemas = ctk.CTkLabel(frame_problemas_reais, text="Aqui você pode ver alguns problemas do mundo real que podem ser representados por circuitos lógicos e lógica proposicional.",
                     font=("Arial", 18), text_color="white")
        label_problemas.pack(pady=20)

        container_problemas = ctk.CTkScrollableFrame(frame_problemas_reais, fg_color="#B7B7DD", height=1200, width=300)
        container_problemas.pack(pady=20)


        problemas = ["Problema 1", "Problema 2", "Problema 3", "Problema 4", "Problema 5", "Problema 6", "Problema 7", "Problema 8", "Problema 9", "Problema 10",
        "Problema 11", "Problema 12", "Problema 13", "Problema 14", "Problema 15", "Problema 16", "Problema 17", "Problema 18", "Problema 19", "Problema 20"]
        # Ver um if pra ver se o problema é facil dificil ou medio, talvez ver a possibilidade de usar POO pra o problema
        for problema in problemas:
            botao_problema = ctk.CTkButton(
                container_problemas,
                text=problema,
                fg_color="#B0E0E6",
                text_color="#000080",
                hover_color="#8B008B",
                border_width=2,
                border_color="#708090",
                width=250,
                height=50,
                font=("Arial", 16),
            )
            botao_problema.pack(pady=10)
    # ---------------- Frame de Abas----------------
    abas = ctk.CTkTabview(
        master=frame_abas,
        fg_color="#000057",
        segmented_button_fg_color="#FFFFFF",
        segmented_button_selected_color="#4441F7",
        segmented_button_selected_hover_color="#0B1658",
        segmented_button_unselected_color="#001E44",
        segmented_button_unselected_hover_color="#4682B4"
    )
    abas.pack(expand=True, fill="both")

    from tkinter import filedialog  

    # Aba do circuito
    aba_circuito = abas.add("      Circuito      ")
    scroll_frame1 = ctk.CTkScrollableFrame(aba_circuito, fg_color="#000057")
    scroll_frame1.pack(expand=True, fill="both")

    label_circuito_expressao = ctk.CTkLabel(
        scroll_frame1,
        font=("Arial", 16, "bold"),
        text_color="cyan",
        text=""  
    )
    label_circuito_expressao.pack(pady=10)

    imagem_circuito = ctk.CTkLabel(scroll_frame1, text="")
    imagem_circuito.pack(pady=10)

    def salvar_imagem():
        caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
        if os.path.exists(caminho_img):
            caminho_salvar = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("Imagem PNG", "*.png")],
                title="Salvar Circuito Como PNG"
            )
            if caminho_salvar:
                img = Image.open(caminho_img)
                img.save(caminho_salvar)
        else:
            popup_erro("Imagem não encontrada.")

    botao_salvar = ctk.CTkButton(
        scroll_frame1,
        text="Salvar Circuito como PNG",
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        width=220,
        height=40,
        font=("Arial", 16),
        command=salvar_imagem
    )
    botao_salvar.pack(pady=20)

 # ------------------------------------------------ Aba de Expressão ----------------------------------------------

    aba_expressao = abas.add("      Expressão      ")
    scroll_frame2 = ctk.CTkScrollableFrame(aba_expressao, fg_color="#000057")
    scroll_frame2.pack(expand=True, fill="both")

    expressao_booleana_atual = ""

    class GUILogger:
        def __init__(self, textbox_widget):
            self.textbox = textbox_widget
            self.largura_linha = 150

        def write(self, text):
            linhas = text.splitlines()
            self.textbox.configure(state="normal")
            for linha in linhas:
                linha = linha.strip()
                if linha:
                    #queria que ele centralizasse o texto, mas não consegui
                    if len(linha) > self.largura_linha:
                        # Divide a linha em partes menores
                        partes = [linha[i:i+self.largura_linha] for i in range(0, len(linha), self.largura_linha)]
                        for parte in partes:
                            self.textbox.insert("end", parte.strip() + "\n")
                    else:
                        self.textbox.insert("end", linha.strip() + "\n")
            self.textbox.see("end")

    frame_borda = ctk.CTkFrame(
        master=scroll_conteudo,
        fg_color="white", 
        corner_radius=10  
    )
    
    label_convertida = ctk.CTkLabel(scroll_frame2, text="", font=("Arial", 16, "bold"), text_color="white")
    log_simplificacao_textbox = ctk.CTkTextbox(frame_borda,  wrap="word", font=("Consolas", 18), height=600, width=900)
    log_simplificacao_textbox.configure(fg_color="#1c1c1c")

    def mostrar_expressao_convertida():
        botao_simplificacao.pack_forget()
        log_simplificacao_textbox.pack_forget()
        
        nonlocal expressao_booleana_atual

        entrada_txt = entrada.get().strip().upper()
        if not entrada_txt:
            popup_erro("Digite uma expressão primeiro.")
            return

        saida_booleana = converter_para_algebra_booleana(entrada_txt)
        
        expressao_booleana_atual = saida_booleana
        
        label_convertida.configure(text=f"Expressão em Álgebra Booleana: {saida_booleana}")
        label_convertida.pack(pady=10)
        
        botao_simplificacao.pack(pady=15)

    label_solucao = ctk.CTkLabel(
        scroll_conteudo,
        text="Solução da expressão:",
        font=("Arial", 20, "bold"),
        text_color="white"
    )

    def expressao_simplificada():
        if not expressao_booleana_atual:
            popup_erro("Erro: Nenhuma expressão convertida encontrada.")
            return
        # Solução talvez um pouco ineficiente, mas funciona
        if label_solucao.winfo_ismapped():
            label_solucao.pack_forget()
            log_simplificacao_textbox.pack_forget()
            frame_borda.pack_forget()
            botao_voltar8.pack_forget()

        label_solucao.pack(pady=20)
        frame_borda.pack(pady=10)
        frame_borda.configure(width=800)
        log_simplificacao_textbox.pack(padx=10, pady=10, fill="both", expand=True)

        log_simplificacao_textbox.configure(state="normal")
        log_simplificacao_textbox.delete("1.0", "end")
        log_simplificacao_textbox.configure(text_color="#39FF14",spacing3=-27)

        botao_voltar8.pack(pady=20)
        
        gui_logger = GUILogger(log_simplificacao_textbox)

        with redirect_stdout(gui_logger):
            try:
                principal_simplificar(expressao_booleana_atual)
            except Exception as e:
                popup_erro(f"\n--- OCORREU UM ERRO ---\n{e}")

    def abrir_duvida_expressao(expressao):
        if not expressao:
            popup_erro("Digite uma expressão primeiro.")
            return
        
        pergunta = f"Como posso simplificar a seguinte expressão lógica proposicional e qual sua interpretação? Como ela fica em álgebra booleana e qual sua tabela verdade? {expressao}"
        query = urllib.parse.quote(pergunta)
        url = f"https://chat.openai.com/?q={query}"
        webbrowser.open(url)

    botao_conversao = ctk.CTkButton(
        scroll_frame2,
        text="Realizar conversão",
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        command=mostrar_expressao_convertida
    )
    botao_conversao.pack(pady=10)

    botao_simplificacao = ctk.CTkButton(
        scroll_frame2,
        text="Simplificar expressão",
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        command=lambda: show_frame(frame_educacional)
    )

    # Definição do frame educacional (frame pai aqui)
    label_educacional = ctk.CTkLabel(
        frame_educacional,
        text="Escolha o que deseja fazer:",
        font=("Arial Bold", 20),
        text_color="white",
        fg_color=None
    )
    label_educacional.pack(pady=100, padx=100)

    botao_interativo = ctk.CTkButton(
        frame_educacional,
        text="Tentar Simplificar",
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        width=200,
        height=50,
        font=("Arial", 16),
        command=lambda: (show_frame(frame_interativo), parte_interativa())
    )
    botao_interativo.pack(pady=(30, 10))

    escolher_caminho = ctk.CTkFrame(
            frame_interativo,
            fg_color="#FFFFFF",
            height=800,
            width=200
        )
    
    botao_voltar9 = ctk.CTkButton(
        escolher_caminho,
        text="Voltar",
        fg_color="goldenrod",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        width=200,
        height=50,
        font=("Arial", 16),
        command=lambda: voltar_para(frame_educacional)
    )
    

    # Frame da resposta -----------------------------------------------
    botao_solucao = ctk.CTkButton(
        frame_educacional,
        text="Ver Solução",
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        width=200,
        height=50,
        font=("Arial", 16),
        border_color="#708090",
        command=lambda: (show_frame(frame_resolucao_direta), expressao_simplificada())
    )
    botao_solucao.pack(pady=10)

    botao_voltar8 = ctk.CTkButton(
        scroll_conteudo,
        text="Voltar",
        fg_color="goldenrod",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        width=200,
        height=50,
        font=("Arial", 16),
        command=lambda: voltar_para(frame_educacional)
    )

    #------------------------------------------------------------------------
    def parte_interativa():
    # Frame da parte interativa
        escolher_caminho.pack_propagate(False)
        escolher_caminho.pack(side="right", padx=(0, 350), pady=10)

        area_expressao = ctk.CTkTextbox(
        master=frame_interativo,
        fg_color="#1c1c1c",
        text_color="#39FF14",
        font=("Consolas", 16),
        wrap="word",
        width=800,
        height=800,
        )
        area_expressao.pack(side="left", padx=(250, 0), pady=10)

        botao_voltar9.pack(pady=10)

    
    botao_voltar7 = ctk.CTkButton(
        frame_educacional,
        text="Voltar",
        fg_color="goldenrod",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",
        width=200,
        height=50,
        font=("Arial", 16),
        command=lambda: voltar_para(frame_abas)
    )
    botao_voltar7.pack(pady=(10))

    botao_tabela = ctk.CTkButton(
        scroll_frame2, 
        text="Tabela Verdade", 
        command=lambda:exibir_tabela_verdade(entrada.get().strip().upper()), 
        fg_color="#B0E0E6",
        text_color="#000080",
        hover_color="#8B008B",
        border_width=2,
        border_color="#708090",) 
    botao_tabela.pack(pady=10)

    botao_ia = ctk.CTkButton(
    scroll_frame2,
    text="Pedir ajuda à IA",
    fg_color="#B0E0E6",
    text_color="#000080",
    hover_color="#8B008B",
    border_width=2,
    border_color="#708090",
    command=lambda: abrir_duvida_expressao(entrada.get().strip().upper()))
    botao_ia.pack(pady=10)

    botao_voltar5 = ctk.CTkButton(
        scroll_frame2,
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
    botao_voltar5.pack(pady=30)

    botao_voltar6 = ctk.CTkButton(
        scroll_frame1,
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
    botao_voltar6.pack(pady=30)

    # ---------------- Frame de Informações ----------------
    frame_info = ctk.CTkFrame(janela, fg_color="#000057")
    frame_info.grid(row=0, column=0, sticky="nsew")

    textbox_info = ctk.CTkTextbox(
        frame_info, 
        font=("Arial", 20), 
        text_color="white", 
        fg_color="#000057"
    )
    textbox_info.pack(expand=True, fill="both", padx=20, pady=20)
    # Definindo o conteúdo do Textbox
    info_text = """
    Alunos responsáveis:
    Larissa de Souza, Otávio Menezes, Zilderlan Santos e
    David Oliveira.
    ================================================
    Átomos aceitos:
    P, Q, R, S e T.
   
    Representação de símbolos:
    '&' (e), '|' (ou), '!' (não) e '>' (implica).
    ---------------------------------Atenção:-------------------------------
    Na hora de digitar a expressão, o usuário deve indicar quem é a operação raiz da expressão.
    Exemplo: (P & Q) | ((P | Q) & (R | S))

    ->((P > Q) & (R | S)) é uma das subexpressões;
    ->(P & Q) é outra subexpressão;
    
    O que conecta as duas é o operador '|', que é a operação raiz da expressão como um todo.
    ---------------------------------Funções:-------------------------------
    O usuário consegue realizar as seguintes funções:
    1- Ver o circuito equivalente
    2- Tabela verdade
    3- Converter a expressão para Álgebra Booleana e comparar as expressões
    4- Simplificar a expressão lógica proposicional
    5- Verificar se duas expressões são equivalentes
    6- Pedir ajuda à IA para simplificar a expressão lógica proposicional
    -------------------------------Motivação:-------------------------------
    A proposta é desenvolver uma aplicação com interface amigável que permita que o aluno possa entender as interações da Lógica Proposicional
    com Circuitos Digitais. Além de interligar as áreas do conhecimento, a aplicação será uma ferramenta de apoio ao aprendizado, permitindo que
    o aluno praticar e entender melhor os conceitos que envolvem as duas áreas.
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
    botao_voltar2.pack(pady=20)


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
            text="Digite as expressões que deseja comparar:", 
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