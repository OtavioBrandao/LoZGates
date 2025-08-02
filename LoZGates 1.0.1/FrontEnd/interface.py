import customtkinter as ctk
from customtkinter import CTkFont
import threading
import tkinter as tk
from tkinter import filedialog, font
import os
import sys
from PIL import Image, ImageTk, ImageOps
import time
import webbrowser
import urllib.parse
from contextlib import redirect_stdout
import copy

from config import ASSETS_PATH, informacoes

from BackEnd.imagem import converte_matrix_para_tkinter_imagem_icon
from BackEnd.tabela import gerar_tabela_verdade, verificar_conclusao
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.equivalencia import tabela
from BackEnd.identificar_lei import principal_simplificar
import BackEnd.simplificador_interativo as simpli

from FrontEnd.buttons import Button


expressao_global = ""
botao_ver_circuito = None
label_convertida = None
arvore_interativa = None
passo_atual_info = None
nos_ignorados = set()
historico_interativo = []
botoes_leis = []

def inicializar_interface():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    janela = ctk.CTk()
    janela.title("LoZ Gates")
    janela.configure(bg="#000057")
    janela.minsize(1100, 650) 

    def forcar_maximizar():
        janela.update_idletasks()
        janela.state('zoomed')

    janela.after(200, forcar_maximizar)
    janela.grid_rowconfigure(0, weight=1)
    janela.grid_columnconfigure(0, weight=1)
    bytes_per_row = 32
    icon = converte_matrix_para_tkinter_imagem_icon(bytes_per_row)
    janela.iconbitmap(icon)
    janela.resizable(True, True)

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
        
        #Remove imagem antiga se existir
        caminho_imagem = os.path.join(ASSETS_PATH, "circuito.png")
        if os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)

        #Executa o Pygame em uma thread
        thread = threading.Thread(target=rodar_pygame)
        thread.start()

        #Espera a imagem ser criada antes de continuar
        def aguardar_imagem():
            tempo_max = 5  #segundos
            tempo_passado = 0
            while not os.path.exists(caminho_imagem) and tempo_passado < tempo_max:
                time.sleep(0.1)
                tempo_passado += 0.1
            if os.path.exists(caminho_imagem):
                atualizar_imagem_circuito()
            else:
                popup_erro("Erro: A imagem do circuito não foi criada a tempo.")

        #Espera a imagem num thread separado para não travar a GUI
        threading.Thread(target=aguardar_imagem).start()

    def popup_erro(mensagem):
        popup = tk.Toplevel(janela)  # <- tk.Toplevel ao invés de ctk.CTkToplevel
        popup.attributes('-topmost', True)
        popup.after(10, lambda: popup.attributes('-topmost', False))
        popup.title("Erro")
        popup.iconbitmap(os.path.join(ASSETS_PATH, "endeota.ico"))

        # Tamanho e centralização
        largura_popup = 400
        altura_popup = 120
        popup.geometry(f"{largura_popup}x{altura_popup}")
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (largura_popup // 2)
        y = (popup.winfo_screenheight() // 2) - (altura_popup // 2)
        popup.geometry(f"{largura_popup}x{altura_popup}+{x}+{y}")

        # Cor de fundo
        popup.configure(bg="#1a1a1a")  # como é Tk puro, use 'bg' e não 'fg_color'

        # Conteúdo
        label = tk.Label(popup, text=mensagem, font=("Arial", 12), fg="white", bg="#1a1a1a")
        label.pack(pady=(20, 10))

        botao_ok = tk.Button(popup, text="OK", bg="#7A2020", fg="white", command=popup.destroy)
        botao_ok.configure(width=8, height=1)
        botao_ok.pack(pady=(0, 10))


    def trocar_para_abas():
        caminho_entrada = os.path.join(ASSETS_PATH, "entrada.txt")
        expressao = entrada.get().strip().upper().replace(" ", "")
        label_circuito_expressao.configure(text=f"Expressão Lógica Proposicional: {expressao}")
        
        with open(caminho_entrada, "w", encoding="utf-8") as file: 
            file.write(expressao) 

        saida = converter_para_algebra_booleana(expressao)
        global expressao_global
        expressao_global = saida

        ver_circuito_pygame(saida)
        show_frame(frame_abas)
        def aguarda_e_mostra():
            #espera o circuito ser salvo e imagem estar disponível
            caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
            for _ in range(50):  #50 tentativas ~5s
                if os.path.exists(caminho_img):
                    break
                time.sleep(0.1)
            atualizar_imagem_circuito()
            janela.after(0, lambda: show_frame(frame_abas))  #mostra o frame principal na thread da GUI

        threading.Thread(target=aguarda_e_mostra).start()

    def confirmar_expressao():
        global botao_ver_circuito
        if botao_ver_circuito:  
            botao_ver_circuito.destroy()

        if not entrada.get().strip():
            popup_erro("A expressão não pode estar vazia.")
            return
        
        botao_ver_circuito = Button.botao_padrao("Ver circuito / Expressão", principal)
        botao_ver_circuito.configure(command=lambda: trocar_para_abas())
        botao_ver_circuito.place(relx=0.5, y=500, anchor="center")


    def exibir_tabela_verdade(expressao):
        janela_tabela = ctk.CTkToplevel(janela)
        janela_tabela.title("Tabela Verdade")
        janela_tabela.geometry("800x600") #Aumentei a largura para caber, ja que nao sei colocar scroll pro lado
        janela_tabela.lift()
        janela_tabela.attributes('-topmost', True)
        janela_tabela.after(10, lambda: janela_tabela.attributes('-topmost', False))
        janela_tabela.configure(fg_color="#FFFFFF")

        #Gera a tabela verdade usando a função do backend
        dados_tabela = gerar_tabela_verdade(expressao)
        
        #Extrai os dados do dicionário retornado
        colunas = dados_tabela["colunas"]
        tabela = dados_tabela["tabela"]
        resultados_finais = dados_tabela["resultados_finais"]

        #Cria um frame para exibir a tabela verdade
        frame_tabela = ctk.CTkScrollableFrame(janela_tabela)
        frame_tabela.pack(pady=10, padx=10, fill="both", expand=True)
        frame_tabela.configure(fg_color="#000057")

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

        #limpa as entradas
        if frame not in [frame_abas, frame_resolucao_direta, frame_educacional, frame_interativo]:
            entrada.delete(0, tk.END) 

        entrada2.delete(0, tk.END)  
        entrada3.delete(0, tk.END) 
        
        #escreve digite aqui
        entrada.configure(placeholder_text="Digite aqui")
        entrada2.configure(placeholder_text="Digite aqui")
        entrada3.configure(placeholder_text="Digite aqui")
        
        #limpa o "é equivalente e o não é equivalente"
        equivalente.place_forget()
        nao_equivalente.place_forget()
        
        #Esconde os resultados da aba de expressão ao voltar apenas se NÃO for para frame_abas
        if frame != frame_abas:
            label_convertida.pack_forget()
            log_simplificacao_textbox.pack_forget()
            botao_simplificacao.pack_forget()

        show_frame(frame)  #troca o frame

        #Força o foco para a janela (tira o foco de qualquer campo antigo)
        janela.focus_set()

        #Se voltando para a tela principal, seta foco corretamente
        if frame == principal:
            entrada.focus_set()
        
        label_convertida.pack_forget()
    
    def atualizar_imagem_circuito():
        caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
        if os.path.exists(caminho_img):
            imagem_pil = Image.open(caminho_img)

            #Adiciona borda branca de 10px
            borda = 10
            imagem_com_borda = ImageOps.expand(imagem_pil, border=borda, fill="white")

            imagem_tk = ImageTk.PhotoImage(imagem_com_borda)
            imagem_circuito.configure(image=imagem_tk, text="")
            imagem_circuito.image = imagem_tk  #Mantém uma referência à imagem para evitar que seja coletada pelo garbage collector
    
    #------------- DEFININDO OS FRAMES DA INTERFACE -------------
    
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

    scroll_problemas_reais = ctk.CTkScrollableFrame(frame_problemas_reais, fg_color="#000057")
    scroll_problemas_reais.pack(expand=True, fill="both", padx=20, pady=20)
    scroll_problemas_reais._scrollbar.grid_remove()

    frame_explicacao_problemas_reais = ctk.CTkFrame(janela, fg_color="#000057")
    frame_explicacao_problemas_reais.grid(row=0, column=0, sticky="nsew")

    #---------------- FRAME DE INÍCIO ----------------

    frame_inicio_conteudo = ctk.CTkFrame(frame_inicio, fg_color="#000057", corner_radius=30)
    frame_inicio_conteudo.pack(expand=True)
    frame_inicio_conteudo.place(relx=0.5, rely=0.5, anchor="center")
    #Configuração da fonte
    fonte_momentz = CTkFont(family="Momentz", size=30)
    label_inicio = ctk.CTkLabel( frame_inicio_conteudo,text="LoZ Gates",font=fonte_momentz,text_color="white",fg_color="#000057")
    label_inicio.pack(pady=30)

    botao_start = Button.botao_padrao("Começar", frame_inicio_conteudo)
    botao_start.configure(command=lambda: show_frame(frame_escolha))
    botao_start.pack(pady=30)

    botao_info = Button.botao_padrao("Informações", frame_inicio_conteudo)
    botao_info.configure(command=lambda: show_frame(frame_info))
    botao_info.pack(pady=20)

    #---------------- FRAME DA ESCOLHA ----------------

    botao_tarefas = Button.botao_padrao("Circuitos", frame_escolha)
    botao_tarefas.configure(command=lambda: show_frame(principal), width=250, height=50)
    botao_tarefas.place(relx=0.5, y=300, anchor="center")

    botao_equivalencia = Button.botao_padrao("Equivalência", frame_escolha)
    botao_equivalencia.configure(command=lambda: show_frame(frame_equivalencia), width=250, height=50)
    botao_equivalencia.place(relx=0.5, y=400, anchor="center")    
        
    botao_voltar_escolha = Button.botao_voltar("Voltar", frame_escolha)
    botao_voltar_escolha.configure(command=lambda: voltar_para(frame_inicio))
    botao_voltar_escolha.place(relx=0.5, y=500, anchor="center") 
       
    #---------------- FRAME DOS CIRCUITOS E DAS EXPRESSÕES ----------------

    label_tarefas = ctk.CTkLabel(principal, text="Digite a expressão em Lógica Proposicional:", font=("Arial Bold", 20), text_color="white", fg_color=None)
    label_tarefas.place(relx=0.5, y=150, anchor="center")

    entrada = ctk.CTkEntry(principal, width=300, placeholder_text="Digite aqui", font=("Arial", 14))
    entrada.place(relx=0.5, y=200, anchor="center")
    entrada.bind("<Return>", lambda event: confirmar_expressao())

    botao_confirmar_expressao = Button.botao_padrao("Confirmar", principal)
    botao_confirmar_expressao.configure(command=confirmar_expressao)
    botao_confirmar_expressao.place(relx=0.5, y=300, anchor="center")
    
    botao_problemas_reais = Button.botao_padrao("Problemas Reais", principal)
    botao_problemas_reais.configure(command=lambda: (show_frame(frame_problemas_reais)))
    botao_problemas_reais.place(relx=0.5, y=400, anchor="center")

    botao_voltar_para_selecao = Button.botao_voltar("Voltar", principal)
    botao_voltar_para_selecao.configure(command=lambda: voltar_para(frame_escolha))
    botao_voltar_para_selecao.place(relx=0.5, y=500, anchor="center")
    
    #---------------- FRAME DOS PROBLEMAS REAIS ----------------

    label = ctk.CTkLabel(scroll_problemas_reais, text="", fg_color="#000057")
    label.pack(pady=10)

    label_problemas = ctk.CTkLabel(scroll_problemas_reais, text="Aqui você pode ver alguns problemas do mundo real que podem ser representados por circuitos lógicos e lógica proposicional.",
                    font=("Arial", 18), text_color="white")
    label_problemas.pack(pady=10)

    borda_branca = ctk.CTkFrame(scroll_problemas_reais, fg_color="white", corner_radius=10)
    borda_branca.pack(pady=10, padx=10)

    container_problemas = ctk.CTkScrollableFrame(borda_branca, fg_color="#000000", height=275, width=800)
    container_problemas.pack(padx=5, pady=5, fill="both", expand=True)
    container_problemas._scrollbar.grid_remove()

    problemas = [f"Problema {i+1}" for i in range(20)]

    for idx, problema in enumerate(problemas):
        botao_problema = Button.botao_padrao(problema, container_problemas)
        row = idx // 5
        col = idx % 5
        botao_problema.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    for i in range(5):
        container_problemas.grid_columnconfigure(i, weight=1)

    botao_voltar_problemas = Button.botao_voltar("Voltar", scroll_problemas_reais)
    botao_voltar_problemas.configure(command=lambda: voltar_para(principal))
    botao_voltar_problemas.pack(pady=10)

    #---------------- FRAME DE ABAS ----------------

    abas = ctk.CTkTabview(
        master=frame_abas, fg_color="#000057", 
        segmented_button_fg_color="#FFFFFF", segmented_button_selected_color="#4441F7",
        segmented_button_selected_hover_color="#0B1658", segmented_button_unselected_color="#001E44",
        segmented_button_unselected_hover_color="#4682B4"
    )
    abas.pack(expand=True, fill="both")

    #---------------------- ABA DO CIRCUITO ----------------------

    aba_circuito = abas.add("      Circuito      ")
    scroll_frame1 = ctk.CTkScrollableFrame(aba_circuito, fg_color="#000057")
    scroll_frame1.pack(expand=True, fill="both")

    label_circuito_expressao = ctk.CTkLabel(scroll_frame1, font=("Arial", 16, "bold"), text_color="cyan", text="")
    label_circuito_expressao.pack(pady=10)

    imagem_circuito = ctk.CTkLabel(scroll_frame1, text="")
    imagem_circuito.pack(pady=10)

    def salvar_imagem():
        caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
        if os.path.exists(caminho_img):
            caminho_salvar = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Imagem PNG", "*.png")], title="Salvar Circuito Como PNG")
            
            if caminho_salvar:
                img = Image.open(caminho_img)
                img.save(caminho_salvar)
        else:
            popup_erro("Imagem não encontrada.")
    botao_salvar = Button.botao_padrao("Salvar circuito como PNG", scroll_frame1)
    botao_salvar.configure(command=salvar_imagem)
    botao_salvar.pack(pady=20)
    
 #------------------------------------------------ ABA DE EXPRESSÃO  ----------------------------------------------
 
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
                        #Divide a linha em partes menores
                        partes = [linha[i:i+self.largura_linha] for i in range(0, len(linha), self.largura_linha)]
                        for parte in partes:
                            self.textbox.insert("end", parte.strip() + "\n")
                    else:
                        self.textbox.insert("end", linha.strip() + "\n")
            self.textbox.see("end")

    frame_borda = ctk.CTkFrame(master=scroll_conteudo,fg_color="white", corner_radius=10)
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

    label_solucao = ctk.CTkLabel(scroll_conteudo, text="Solução da expressão:", font=("Arial", 20, "bold"), text_color="white")

    def expressao_simplificada():
        if not expressao_booleana_atual:
            popup_erro("Erro: Nenhuma expressão convertida encontrada.")
            return

        if label_solucao.winfo_ismapped():
            label_solucao.pack_forget()
            log_simplificacao_textbox.pack_forget()
            frame_borda.pack_forget()
            botao_voltar_ver_solucao.pack_forget()

        label_solucao.pack(pady=20)
        frame_borda.pack(pady=10)
        frame_borda.configure(width=800)
        log_simplificacao_textbox.pack(padx=10, pady=10, fill="both", expand=True)
        log_simplificacao_textbox.configure(state="normal")
        log_simplificacao_textbox.delete("1.0", "end")
        log_simplificacao_textbox.configure(text_color="#39FF14", spacing3=-27)
        botao_voltar_ver_solucao.pack(pady=20)

        gui_logger = GUILogger(log_simplificacao_textbox)

        def simplificar_thread():
            with redirect_stdout(gui_logger):
                try:
                    principal_simplificar(expressao_booleana_atual)
                except Exception as e:
                    janela.after(0, lambda: popup_erro(f"\n--- OCORREU UM ERRO ---\n{e}"))

        threading.Thread(target=simplificar_thread).start()


    def abrir_duvida_expressao(expressao):
        if not expressao:
            popup_erro("Digite uma expressão primeiro.")
            return
        
        pergunta = f"Como posso simplificar a seguinte expressão lógica proposicional e qual sua interpretação? Como ela fica em álgebra booleana e qual sua tabela verdade? {expressao}"
        query = urllib.parse.quote(pergunta)
        url = f"https://chat.openai.com/?q={query}"
        webbrowser.open(url)

    botao_converter = Button.botao_padrao("Realizar conversão", scroll_frame2)
    botao_converter.configure(command=mostrar_expressao_convertida)
    botao_converter.pack(pady=10)

    botao_simplificacao = Button.botao_padrao("Simplificar expressão", scroll_frame2)
    botao_simplificacao.configure(command=lambda: show_frame(frame_educacional))

    #Definição do frame educacional (frame pai aqui)
    label_educacional = ctk.CTkLabel(frame_educacional, text="Escolha o que deseja fazer:", font=("Arial Bold", 20), text_color="white",fg_color=None)
    label_educacional.pack(pady=100, padx=100)

    def go_to_interactive():
        #Função wrapper para garantir a ordem correta das chamadas
        show_frame(frame_interativo)
        parte_interativa()

    botao_interativo = Button.botao_padrao("Simplificar - interativo", frame_educacional)
    botao_interativo.configure(command=go_to_interactive)
    botao_interativo.pack(pady=(30, 10))
    
    escolher_caminho = ctk.CTkFrame(frame_interativo, fg_color="#000033", corner_radius=10, height=800, width=280)
    area_expressao = ctk.CTkTextbox(master=frame_interativo,fg_color="#1c1c1c", text_color="#39FF14", font=("Consolas", 16), wrap="word", width=800, height=800)
    
    #---------------------- FRAME DA SIMPLFICAÇÃO ---------------------------------
    
    botao_solucao = Button.botao_padrao("Simplificar - resultado", frame_educacional)
    botao_solucao.configure(command=lambda: (show_frame(frame_resolucao_direta), expressao_simplificada()))
    botao_solucao.pack(pady=10)

    botao_voltar_ver_solucao = Button.botao_voltar("Voltar", scroll_conteudo)
    botao_voltar_ver_solucao.configure(command = lambda: voltar_para(frame_educacional))

    #------------------ MODO INTERATIVO LÓGICA E FUNÇÕES ----------------------
    def salvar_estado_atual():
        """Salva o estado atual (árvore, histórico, ignorados) na pilha de histórico."""
        global historico_de_estados, arvore_interativa, historico_interativo, nos_ignorados, passo_atual_info
        
        estado = {
            'arvore': copy.deepcopy(arvore_interativa),
            'historico': list(historico_interativo),
            'ignorados': set(nos_ignorados),
            'passo_info': copy.deepcopy(passo_atual_info)
        }
        historico_de_estados.append(estado)
    
    def on_desfazer_selecionado():
        global historico_de_estados, arvore_interativa, historico_interativo, nos_ignorados, passo_atual_info, botao_desfazer

        if not historico_de_estados:
            print("Nada para desfazer.") 
            return

        estado_anterior = historico_de_estados.pop()
        arvore_interativa = estado_anterior['arvore']
        historico_interativo = estado_anterior['historico']
        nos_ignorados = estado_anterior['ignorados']
        passo_atual_info = estado_anterior['passo_info']

        if not historico_de_estados:
            botao_desfazer.configure(state="disabled")

        atualizar_ui_interativa()
      
    def on_lei_selecionada(indice_lei):
        global arvore_interativa, passo_atual_info, historico_interativo, nos_ignorados, botao_desfazer

        if not passo_atual_info:
            return

        salvar_estado_atual() 
        botao_desfazer.configure(state="normal")

        lei_usada = simpli.LEIS_LOGICAS[indice_lei]['nome']
        nova_arvore, sucesso = simpli.aplicar_lei_e_substituir(arvore_interativa, passo_atual_info, indice_lei)

        if sucesso:
            arvore_interativa = nova_arvore
            historico_interativo.append(f"✓ Lei '{lei_usada}' aplicada.")
            historico_interativo.append(f"   Nova Expressão: {str(arvore_interativa)}")
            nos_ignorados = set()
            iniciar_rodada_interativa()
        else:
            historico_de_estados.pop()
            if not historico_de_estados:
                botao_desfazer.configure(state="disabled")
            popup_erro("Não foi possível aplicar esta lei.")


    def on_pular_selecionado():
        global nos_ignorados, passo_atual_info, historico_interativo, botao_desfazer
        if passo_atual_info and passo_atual_info['no_atual']:
            
            salvar_estado_atual()
            botao_desfazer.configure(state="normal") 

            nos_ignorados.add(passo_atual_info['no_atual'])
            historico_interativo.append(f"↷ Sub-expressão '{str(passo_atual_info['no_atual'])}' ignorada.")
            iniciar_rodada_interativa()

    def atualizar_ui_interativa():
        global botoes_leis
        
        area_expressao.configure(state="normal")
        area_expressao.delete("1.0", "end")

        texto_historico = "\n".join(historico_interativo)
        area_expressao.insert("1.0", texto_historico)

        if passo_atual_info:
            sub_expr = str(passo_atual_info['no_atual'])
            area_expressao.insert("end", f"\n\n========================================\n")
            area_expressao.insert("end", f"Analisando a sub-expressão: '{sub_expr}'\n")
            area_expressao.insert("end", "Qual lei deseja aplicar?")
            
            for botao in botoes_leis:
                botao.configure(state="normal")
            
            botao_pular.configure(state="normal")
        else:
            area_expressao.insert("end", "\n\n========================================\n")
            area_expressao.insert("end", "Simplificação finalizada. Nenhuma outra lei pôde ser aplicada.")
            
            for botao in botoes_leis:
                botao.configure(state="disabled")
            botao_pular.configure(state="disabled")

        area_expressao.configure(state="disabled")
        area_expressao.see("end") #Rola para o final
    
    def iniciar_rodada_interativa():
        global passo_atual_info
        passo_atual_info = simpli.encontrar_proximo_passo(arvore_interativa, nos_a_ignorar=nos_ignorados)
        atualizar_ui_interativa()
        
    def parte_interativa():
        global arvore_interativa, historico_interativo, nos_ignorados, passo_atual_info, expressao_global, botoes_leis, historico_de_estados
        
        if not expressao_global:
            popup_erro("Por favor, primeiro insira e converta uma expressão.")
            voltar_para(frame_abas)
            show_frame(principal) 
            return
            
        try:
            arvore_interativa = simpli.construir_arvore(expressao_global)
        except Exception as e:
            popup_erro(f"Erro ao construir a expressão: {e}")
            voltar_para(frame_educacional)
            return

        historico_interativo = [f"Expressão Inicial: {str(arvore_interativa)}"]
        nos_ignorados = set()
        passo_atual_info = None
        historico_de_estados = []

        escolher_caminho.pack_propagate(False)
        escolher_caminho.pack(side="right", fill="y", padx=20, pady=20)
        area_expressao.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        botoes_info = [
            {"texto": "Inversa (A * ~A = 0)", "idx": 0},
            {"texto": "Nula (A * 0 = 0)", "idx": 1},
            {"texto": "Identidade (A * 1 = A)", "idx": 2},
            {"texto": "Idempotente (A * A = A)", "idx": 3},
            {"texto": "Absorção (A * (A+B) = A)", "idx": 4},
            {"texto": "De Morgan (~(A*B) = ~A+~B)", "idx": 5},
            {"texto": "Distributiva ((A+B)*(A+C))", "idx": 6},
            {"texto": "Associativa ((A*B)*C)", "idx": 7},
            {"texto": "Comutativa (B*A = A*B)", "idx": 8},
        ]

        for widget in escolher_caminho.winfo_children():
            widget.destroy()
        botoes_leis = []
        
        for info in botoes_info:
            btn = ctk.CTkButton(
                escolher_caminho, text=info["texto"],
                fg_color="#B0E0E6", text_color="#000080", hover_color="#8B008B",
                border_width=2, border_color="#708090", width=250, height=45,font=("Arial", 12),
                command=lambda idx=info["idx"]: on_lei_selecionada(idx)
            )
            btn.pack(pady=5, padx=10)
            botoes_leis.append(btn)
        
        global botao_pular, botao_desfazer
        
        botao_pular = ctk.CTkButton(
            escolher_caminho, text="Pular Sugestão",
            fg_color="#DAA520", text_color="#000080", hover_color="#8B008B",
            border_width=2, border_color="#708090",
            font=("Arial", 16), command=on_pular_selecionado
        )
        botao_pular.pack(side="left", padx=10, pady=10)

        botao_desfazer = ctk.CTkButton(
            escolher_caminho, text="Desfazer",
            fg_color="#C0C0C0", text_color="#000000", hover_color="#A9A9A9",
            border_width=2, border_color="#696969",
            font=("Arial", 16), command=on_desfazer_selecionado, state="disabled"
        )
        botao_desfazer.pack(side="left", padx=10, pady=10)
            

        botao_voltar_interativo = Button.botao_voltar("Voltar", escolher_caminho)
        botao_voltar_interativo.configure(command=lambda: voltar_para(frame_educacional))
        botao_voltar_interativo.pack(pady=10, padx=10)
        
        iniciar_rodada_interativa()

    #------------------------------------------------------------------------
    
    botao_voltar_para_abas = Button.botao_voltar("Voltar", frame_educacional)
    botao_voltar_para_abas.configure(command=lambda: voltar_para(frame_abas))
    botao_voltar_para_abas.pack(pady=10)

    botao_tabela_verdade = Button.botao_padrao("Tabela Verdade", scroll_frame2)
    botao_tabela_verdade.configure(command=lambda: exibir_tabela_verdade(entrada.get().strip().upper()))
    botao_tabela_verdade.pack(pady=10)

    botao_pedir_ajuda_ia = Button.botao_padrao("Pedir ajuda à IA", scroll_frame2)
    botao_pedir_ajuda_ia.configure(command=lambda: abrir_duvida_expressao(entrada.get().strip().upper()))
    botao_pedir_ajuda_ia.pack(pady=10)
    
    #Botões das partes de abas que voltam pro frame de inserir a expressão para ver o circuito
    botao_voltar_principal_2 = Button.botao_voltar("Voltar", scroll_frame2)
    botao_voltar_principal_2.configure(command=lambda: voltar_para(principal))
    botao_voltar_principal_2.pack(pady=30)

    botao_voltar_principal = Button.botao_voltar("Voltar", scroll_frame1)
    botao_voltar_principal.configure(command=lambda: voltar_para(principal))
    botao_voltar_principal.pack(pady=30)

    #---------------- FRAME DE INFORMAÇÕES ----------------
    
    frame_info = ctk.CTkFrame(janela, fg_color="#000057")
    frame_info.grid(row=0, column=0, sticky="nsew")

    textbox_info = ctk.CTkTextbox(frame_info, font=("Arial", 20), text_color="white", fg_color="#000057")
    textbox_info.pack(expand=True, fill="both", padx=20, pady=20)
    textbox_info.configure(fg_color="#00002C", text_color="white")  #Permitir edição para inserir o texto
    #Definindo o conteúdo do Textbox
    info_text = informacoes
    textbox_info.insert("0.0", info_text)  #Inserir o texto no Textbox
    textbox_info.configure(state="disable")  #Desativar edição para evitar modificações

    botao_voltar_info = Button.botao_voltar("Voltar", frame_info)
    botao_voltar_info.configure(command=lambda: voltar_para(frame_inicio))
    botao_voltar_info.pack(pady=20)

    #---------------- FRAME DE EQUIVALÊNCIA ----------------
    
    label_escolha = ctk.CTkLabel(frame_escolha, text="Escolha a opção desejada:", font=("Arial Bold", 20), text_color="white", fg_color=None)
    label_escolha.place(relx=0.5, y=200, anchor="center")

    entrada2 = ctk.CTkEntry(frame_equivalencia, width=300, placeholder_text="Digite aqui", font=("Arial", 14))
    entrada2.place(relx=0.5, y=200, anchor="center")

    entrada3 = ctk.CTkEntry(frame_equivalencia, width=300, placeholder_text="Digite aqui", font=("Arial", 14))
    entrada3.place(relx=0.5, y=250, anchor="center")

    botao_comparar = Button.botao_padrao("Confirmar", frame_equivalencia)
    botao_comparar.configure(command=comparar)
    botao_comparar.place(relx=0.5, y=350, anchor="center")

    botao_voltar_equivalencia = Button.botao_voltar("Voltar", frame_equivalencia)
    botao_voltar_equivalencia.configure(command=lambda: voltar_para(frame_escolha))
    botao_voltar_equivalencia.place(relx=0.5, y=420, anchor="center")

    titulo = ctk.CTkLabel(frame_equivalencia, text="Digite as expressões que deseja comparar:", font=("Arial Bold", 20), text_color="white", fg_color=None)
    titulo.place(relx=0.5, y=130, anchor="center")

    equivalente = ctk.CTkLabel(frame_equivalencia, text="É equivalente 😁", font=("Arial Bold", 20), text_color="white", fg_color=None)
    nao_equivalente = ctk.CTkLabel(frame_equivalencia, text="Não é equivalente 😩", font=("Arial Bold", 20), text_color="white", fg_color=None)
 
    show_frame(frame_inicio)
    janela.mainloop()