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

# Importar o módulo de circuito corrigido
import BackEnd.circuito_logico as circuito_integrado

expressao_global = ""
botao_ver_circuito = None
label_convertida = None
arvore_interativa = None
passo_atual_info = None
nos_ignorados = set()
historico_interativo = []
botoes_leis = []
circuito_interativo_instance = None

def inicializar_interface():

    ctk.set_appearance_mode("dark")  #Modo escuro
    ctk.set_default_color_theme("blue")  #Tema azul
    janela = ctk.CTk()
    janela.title("LoZ Gates")
    janela.configure(bg="#082347")
    janela.minsize(1280, 720)
    try:
        janela.wm_attributes('-zoomed', True)
    except (tk.TclError, AttributeError):
        janela.after(250, lambda: janela.state('zoomed'))
    janela.grid_rowconfigure(0, weight=1)
    janela.grid_columnconfigure(0, weight=1)
    bytes_per_row = 32  #Número de bytes por linha na matriz
    icon = converte_matrix_para_tkinter_imagem_icon(bytes_per_row)
    janela.iconbitmap(icon)
    janela.resizable(True, True)

    def show_frame(frame):
        frame.tkraise()

    def ver_circuito_pygame(expressao):
        def rodar_pygame():
            try:
                # Chamada corrigida para a função de plotagem
                circuito_integrado.plotar_circuito_logico(expressao, 0, 1200, 800)
                print("Circuito gerado com sucesso!")
            except Exception as e:
                print(f"Erro ao gerar circuito: {e}")
                janela.after(0, lambda: popup_erro(f"Erro ao gerar circuito: {e}"))
        
        #Remove imagem antiga se existir
        caminho_imagem = os.path.join(ASSETS_PATH, "circuito.png")
        if os.path.exists(caminho_imagem):
            try:
                os.remove(caminho_imagem)
            except Exception as e:
                print(f"Aviso: Não foi possível remover imagem anterior: {e}")

        #Executa o Pygame em uma thread
        thread = threading.Thread(target=rodar_pygame)
        thread.start()

        #Espera a imagem ser criada antes de continuar
        def aguardar_imagem():
            tempo_max = 10  # Aumentado para 10 segundos
            tempo_passado = 0
            while not os.path.exists(caminho_imagem) and tempo_passado < tempo_max:
                time.sleep(0.2)
                tempo_passado += 0.2
            
            if os.path.exists(caminho_imagem):
                janela.after(0, atualizar_imagem_circuito)
            else:
                janela.after(0, lambda: popup_erro("Erro: A imagem do circuito não foi criada a tempo."))

        #Espera a imagem num thread separado para não travar a GUI
        threading.Thread(target=aguardar_imagem).start()

    def popup_erro(mensagem):
        popup = tk.Toplevel(janela)
        popup.attributes('-topmost', True)
        popup.after(10, lambda: popup.attributes('-topmost', False))
        popup.title("Erro")
        
        # Verificar se o ícone existe antes de tentar usá-lo
        try:
            icon_path = os.path.join(ASSETS_PATH, "endeota.ico")
            if os.path.exists(icon_path):
                popup.iconbitmap(icon_path)
        except:
            pass  # Ignora erro se não conseguir carregar ícone

        # Tamanho e centralização
        largura_popup = 400
        altura_popup = 120
        popup.geometry(f"{largura_popup}x{altura_popup}")
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (largura_popup // 2)
        y = (popup.winfo_screenheight() // 2) - (altura_popup // 2)
        popup.geometry(f"{largura_popup}x{altura_popup}+{x}+{y}")

        # Cor de fundo
        popup.configure(bg="#1a1a1a")

        # Conteúdo
        label = tk.Label(popup, text=mensagem, font=("Trebuchet MS", 12), fg="white", bg="#1a1a1a")
        label.pack(pady=(20, 10))

        botao_ok = tk.Button(popup, text="OK", bg="#7A2020", fg="white", command=popup.destroy)
        botao_ok.configure(width=8, height=1)
        botao_ok.pack(pady=(0, 10))

    def trocar_para_abas():
        try:
            caminho_entrada = os.path.join(ASSETS_PATH, "entrada.txt")
            expressao = entrada.get().strip().upper().replace(" ", "")
            
            if not expressao:
                popup_erro("A expressão não pode estar vazia.")
                return
                
            label_circuito_expressao.configure(text=f"Expressão Lógica Proposicional: {expressao}")
            
            # Criar diretório se não existir
            os.makedirs(ASSETS_PATH, exist_ok=True)
            
            with open(caminho_entrada, "w", encoding="utf-8") as file: 
                file.write(expressao) 

            saida = converter_para_algebra_booleana(expressao)
            global expressao_global
            expressao_global = saida

            # Gerar circuito pygame
            ver_circuito_pygame(saida)
            
            # Criar circuito interativo na nova aba
            criar_circuito_interativo(expressao)
            
            # Mostrar frame das abas
            show_frame(frame_abas)
            
        except Exception as e:
            popup_erro(f"Erro ao processar expressão: {e}")
            print(f"Erro detalhado: {e}")

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
        try:
            janela_tabela = ctk.CTkToplevel(janela)
            janela_tabela.title("Tabela Verdade")
            janela_tabela.geometry("800x600")
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
            frame_tabela.configure(fg_color="#082347")

            cabecalho_str = " | ".join([f"{col:^10}" for col in colunas])
            label_cabecalho = ctk.CTkLabel(frame_tabela, text=cabecalho_str, font=("Trebuchet MS", 14, "bold"))
            label_cabecalho.pack(pady=(5, 0))

            separador_str = "-".join(["-" * 10 for _ in colunas])
            separador = ctk.CTkLabel(frame_tabela, text=separador_str, font=("Trebuchet MS", 14))
            separador.pack()

            #Adiciona as linhas da tabela
            for linha_valores in tabela:
                linha_str = " | ".join([f"{str(val):^10}" for val in linha_valores])
                label_linha = ctk.CTkLabel(frame_tabela, text=linha_str, font=("Trebuchet MS", 14))
                label_linha.pack()

            #Verifica a conclusão da expressão (Tautologia, Contradição ou Satisfatível)
            conclusao = verificar_conclusao(resultados_finais)
            label_conclusao = ctk.CTkLabel(frame_tabela, text=conclusao, font=("Trebuchet MS", 16, "bold"))
            label_conclusao.pack(pady=20)
            
        except Exception as e:
            popup_erro(f"Erro ao gerar tabela verdade: {e}")

    def comparar():
        try:
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
                
        except Exception as e:
            popup_erro(f"Erro ao comparar expressões: {e}")
            
    def voltar_para(frame):
        global botao_ver_circuito, circuito_interativo_instance
        if botao_ver_circuito:
            botao_ver_circuito.destroy()
            botao_ver_circuito = None

        # Parar circuito interativo se estiver rodando
        if circuito_interativo_instance:
            try:
                circuito_interativo_instance.stop()
                circuito_interativo_instance = None
            except:
                pass

        #limpa as entradas
        if frame not in [frame_abas, frame_resolucao_direta, frame_interativo]:
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

        show_frame(frame)  #troca o frame

        #Força o foco para a janela (tira o foco de qualquer campo antigo)
        janela.focus_set()

        #Se voltando para a tela principal, seta foco corretamente
        if frame == principal:
            entrada.focus_set()
        
        label_convertida.pack_forget()
    
    def atualizar_imagem_circuito():
        try:
            caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
            if os.path.exists(caminho_img):
                imagem_pil = Image.open(caminho_img)

                #Adiciona borda branca de 10px
                borda = 10
                imagem_com_borda = ImageOps.expand(imagem_pil, border=borda, fill="white")

                imagem_tk = ImageTk.PhotoImage(imagem_com_borda)
                imagem_circuito.configure(image=imagem_tk, text="")
                imagem_circuito.image = imagem_tk  #Mantém uma referência à imagem
            else:
                imagem_circuito.configure(text="Imagem do circuito não encontrada", image="")
        except Exception as e:
            print(f"Erro ao atualizar imagem: {e}")
            imagem_circuito.configure(text=f"Erro ao carregar imagem: {e}", image="")
    
    def criar_circuito_interativo(expressao):
        """Cria o circuito interativo na aba correspondente"""
        global circuito_interativo_instance
        
        # Limpar instância anterior se existir
        if circuito_interativo_instance:
            try:
                circuito_interativo_instance.stop()
            except:
                pass
        
        # Limpar o frame antes de criar novo circuito
        for widget in frame_circuito_interativo.winfo_children():
            widget.destroy()
        
        # Criar novo circuito interativo
        try:
            circuito_interativo_instance = circuito_integrado.criar_circuito_integrado(
                frame_circuito_interativo, expressao
            )
        except Exception as e:
            print(f"Erro ao criar circuito interativo: {e}")
            # Mostrar mensagem de erro no frame
            error_label = ctk.CTkLabel(
                frame_circuito_interativo,
                text=f"Erro ao criar circuito interativo: {e}",
                text_color="red"
            )
            error_label.pack(expand=True)
    
    #------------- DEFININDO OS FRAMES DA INTERFACE -------------
    
    frame_inicio = ctk.CTkFrame(janela, fg_color="#082347")
    frame_inicio.grid(row=0, column=0, sticky="nsew")

    principal = ctk.CTkFrame(janela, fg_color="#082347")
    principal.grid(row=0, column=0, sticky="nsew")

    frame_equivalencia = ctk.CTkFrame(janela, fg_color="#082347")
    frame_equivalencia.grid(row=0, column=0, sticky="nsew")

    frame_abas = ctk.CTkFrame(janela, fg_color="#082347")
    frame_abas.grid(row=0, column=0, sticky="nsew")

    frame_resolucao_direta = ctk.CTkFrame(janela, fg_color="#082347")
    frame_resolucao_direta.grid(row=0, column=0, sticky="nsew")

    scroll_conteudo = ctk.CTkScrollableFrame(frame_resolucao_direta, fg_color="#082347")
    scroll_conteudo.pack(expand=True, fill="both", padx=20, pady=20)

    frame_interativo = ctk.CTkFrame(janela, fg_color="#082347")
    frame_interativo.grid(row=0, column=0, sticky="nsew")

    frame_problemas_reais = ctk.CTkFrame(janela, fg_color="#232369")
    frame_problemas_reais.grid(row=0, column=0, sticky="nsew")

    scroll_problemas_reais = ctk.CTkScrollableFrame(frame_problemas_reais, fg_color="#082347")
    scroll_problemas_reais.pack(expand=True, fill="both", padx=20, pady=20)
    scroll_problemas_reais._scrollbar.grid_remove()

    frame_explicacao_problemas_reais = ctk.CTkFrame(janela, fg_color="#082347")
    frame_explicacao_problemas_reais.grid(row=0, column=0, sticky="nsew")

    #---------------- FRAME DE INÍCIO ----------------
 
    fonte_momentz = CTkFont(family="Momentz", size=30)
    label_inicio = ctk.CTkLabel(frame_inicio,text="<LoZ Gates>",font=fonte_momentz,text_color="white",fg_color="#082347")
    label_inicio.place(relx=0.5, y=200, anchor="center")

    botao_info = Button.botao_padrao("Ajuda", frame_inicio)
    botao_info.configure(command=lambda: show_frame(frame_info))

    botao_circuitos = Button.botao_padrao("Circuitos e Expressões", frame_inicio)
    botao_circuitos.configure(command=lambda: show_frame(principal))
    botao_circuitos.place(relx=0.5, y=300, anchor="center")

    botao_equivalencia = Button.botao_padrao("Equivalência Lógica", frame_inicio)
    botao_equivalencia.configure(command=lambda: show_frame(frame_equivalencia))
    botao_equivalencia.place(relx=0.5, y=400, anchor="center")    
    botao_info.place(relx=0.5, y=500, anchor="center")

    #---------------- FRAME DOS CIRCUITOS E DAS EXPRESSÕES ----------------

    label_tarefas = ctk.CTkLabel(principal, text="Digite a expressão em Lógica Proposicional:", font=("Trebuchet MS Bold", 20), text_color="white", fg_color=None)
    label_tarefas.place(relx=0.5, y=150, anchor="center")

    entrada = ctk.CTkEntry(principal, width=300, placeholder_text="Digite aqui", font=("Trebuchet MS", 14))
    entrada.place(relx=0.5, y=200, anchor="center")
    entrada.bind("<Return>", lambda event: confirmar_expressao())

    botao_confirmar_expressao = Button.botao_padrao("Confirmar", principal)
    botao_confirmar_expressao.configure(command=confirmar_expressao)
    botao_confirmar_expressao.place(relx=0.5, y=300, anchor="center")
    
    botao_problemas_reais = Button.botao_padrao("Problemas Reais", principal)
    botao_problemas_reais.configure(command=lambda: (show_frame(frame_problemas_reais)))
    botao_problemas_reais.place(relx=0.5, y=400, anchor="center")

    botao_voltar_para_inicio = Button.botao_voltar("Voltar", principal)
    botao_voltar_para_inicio.configure(command=lambda: voltar_para(frame_inicio))
    botao_voltar_para_inicio.place(relx=0.5, y=500, anchor="center")
    
    #---------------- FRAME DOS PROBLEMAS REAIS ----------------

    label = ctk.CTkLabel(scroll_problemas_reais, text="", fg_color="#082347")
    label.pack(pady=10)

    label_problemas = ctk.CTkLabel(scroll_problemas_reais, text="Aqui você pode ver alguns problemas do mundo real que podem ser representados por circuitos lógicos e lógica proposicional.",
                    font=("Trebuchet MS", 18), text_color="white")
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
        master=frame_abas, fg_color="#082347", 
        segmented_button_fg_color="#FFFFFF", segmented_button_selected_color="#4441F7",
        segmented_button_selected_hover_color="#0B1658", segmented_button_unselected_color="#001E44",
        segmented_button_unselected_hover_color="#4682B4"
    )
    abas.pack(expand=True, fill="both")

    #---------------------- ABA DO CIRCUITO ESTÁTICO ----------------------

    aba_circuito = abas.add("      Circuito      ")
    scroll_frame1 = ctk.CTkScrollableFrame(aba_circuito, fg_color="#082347")
    scroll_frame1.pack(expand=True, fill="both")

    label_circuito_expressao = ctk.CTkLabel(scroll_frame1, font=("Trebuchet MS", 16, "bold"), text_color="cyan", text="")
    label_circuito_expressao.pack(pady=10)

    imagem_circuito = ctk.CTkLabel(scroll_frame1, text="Gerando circuito...")
    imagem_circuito.pack(pady=10)

    def salvar_imagem():
        try:
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
                    popup_erro("Imagem salva com sucesso!")
            else:
                popup_erro("Imagem não encontrada.")
        except Exception as e:
            popup_erro(f"Erro ao salvar imagem: {e}")
            
    botao_salvar = Button.botao_padrao("Salvar circuito como PNG", scroll_frame1)
    botao_salvar.configure(command=salvar_imagem)
    botao_salvar.pack(pady=20)
    
    #---------------------- ABA DO CIRCUITO INTERATIVO ----------------------
    
    aba_circuito_interativo = abas.add("  Circuito Interativo  ")
    frame_circuito_interativo = tk.Frame(aba_circuito_interativo, bg="#082347")
    frame_circuito_interativo.pack(expand=True, fill="both", padx=10, pady=10)
    
 #------------------------------------------------ ABA DE EXPRESSÃO  ----------------------------------------------
 
    aba_expressao = abas.add("      Expressão      ")
    scroll_frame2 = ctk.CTkScrollableFrame(aba_expressao, fg_color="#082347")
    scroll_frame2.pack(expand=True, fill="both")
    expressao_booleana_atual = ""

    class GUILogger:
        def __init__(self, textbox_widget):
            self.textbox = textbox_widget
            self.largura_linha = 150

        def write(self, text):
            try:
                linhas = text.splitlines()
                self.textbox.configure(state="normal")
                for linha in linhas:
                    linha = linha.strip()
                    if linha:
                        if len(linha) > self.largura_linha:
                            #Divide a linha em partes menores
                            partes = [linha[i:i+self.largura_linha] for i in range(0, len(linha), self.largura_linha)]
                            for parte in partes:
                                self.textbox.insert("end", parte.strip() + "\n")
                        else:
                            self.textbox.insert("end", linha.strip() + "\n")
                self.textbox.see("end")
            except Exception as e:
                print(f"Erro no logger: {e}")

    frame_borda = ctk.CTkFrame(master=scroll_conteudo,fg_color="white", corner_radius=10)
    label_convertida = ctk.CTkLabel(scroll_frame2, text="", font=("Trebuchet MS", 16, "bold"), text_color="white")
    log_simplificacao_textbox = ctk.CTkTextbox(frame_borda,  wrap="word", font=("Trebuchet MS", 18), height=600, width=900)
    log_simplificacao_textbox.configure(fg_color="#1c1c1c")

    def mostrar_expressao_convertida():
        try:
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
        except Exception as e:
            popup_erro(f"Erro ao converter expressão: {e}")

    label_solucao = ctk.CTkLabel(scroll_conteudo, text="Solução da expressão:", font=("Trebuchet MS", 20, "bold"), text_color="white")

    def expressao_simplificada():
        try:
            # 1. Pega a expressão mais recente direto da caixa de entrada principal
            entrada_txt = entrada.get().strip().upper()
            if not entrada_txt:
                popup_erro("A expressão na tela principal está vazia.")
                return

            # 2. Converte para o formato de álgebra booleana
            expressao_para_simplificar = converter_para_algebra_booleana(entrada_txt)
            
            # O resto da função continua igual, mas usando a nova variável
            if label_solucao.winfo_ismapped():
                label_solucao.pack_forget()
                log_simplificacao_textbox.pack_forget()
                frame_borda.pack_forget()

            label_solucao.pack(pady=20)
            frame_borda.pack(pady=10)
            frame_borda.configure(width=800)
            log_simplificacao_textbox.pack(padx=10, pady=10, fill="both", expand=True)
            log_simplificacao_textbox.configure(state="normal")
            log_simplificacao_textbox.delete("1.0", "end")
            log_simplificacao_textbox.configure(text_color="#39FF14", spacing3=-27)
            botao_voltar_para_aba2.pack(pady=10)

            gui_logger = GUILogger(log_simplificacao_textbox)

            def simplificar_thread():
                with redirect_stdout(gui_logger):
                    try:
                        # 3. Usa a expressão recém-capturada e convertida
                        principal_simplificar(expressao_para_simplificar)
                    except Exception as e:
                        janela.after(0, lambda: popup_erro(f"\n--- OCORREU UM ERRO ---\n{e}"))

            threading.Thread(target=simplificar_thread).start()
        except Exception as e:
            popup_erro(f"Erro na simplificação: {e}")

    def abrir_duvida_expressao(expressao):
        try:
            if not expressao:
                popup_erro("Digite uma expressão primeiro.")
                return
            
            pergunta = f"Como posso simplificar a seguinte expressão lógica proposicional e qual sua interpretação? Como ela fica em álgebra booleana e qual sua tabela verdade? {expressao}"
            query = urllib.parse.quote(pergunta)
            url = f"https://chat.openai.com/?q={query}"
            webbrowser.open(url)
        except Exception as e:
            popup_erro(f"Erro ao abrir IA: {e}")

    botao_converter = Button.botao_padrao("Realizar conversão", scroll_frame2)
    botao_converter.configure(command=lambda: (mostrar_expressao_convertida(), mostrar_botoes_simplificar()))
    botao_converter.pack(pady=10)

    def go_to_interactive():
        #Função wrapper para garantir a ordem correta das chamadas
        show_frame(frame_interativo)
        parte_interativa()

    botao_interativo = Button.botao_padrao("Simplificar - interativo", scroll_frame2)
    botao_interativo.configure(command=go_to_interactive)

    
    escolher_caminho = ctk.CTkFrame(frame_interativo, fg_color="#000033", corner_radius=10, height=800, width=280)
    area_expressao = ctk.CTkTextbox(master=frame_interativo,fg_color="#1c1c1c", text_color="#39FF14", font=("Trebuchet MS", 16), wrap="word", width=800, height=800)
    
    #---------------------- PARTE DA SIMPLFICAÇÃO ---------------------------------
    def mostrar_botoes_simplificar():
        botao_solucao.pack(pady=10)
        botao_interativo.pack(pady=10)

    botao_solucao = Button.botao_padrao("Simplificar - resultado", scroll_frame2)
    botao_solucao.configure(command=lambda: (show_frame(frame_resolucao_direta), expressao_simplificada()))

    botao_voltar_para_aba2 = Button.botao_voltar("Voltar", scroll_conteudo)
    botao_voltar_para_aba2.configure(command = lambda: voltar_para(frame_abas))
    botao_voltar_para_aba2.pack(side="bottom", pady = 10)
    

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
            voltar_para(scroll_frame2)
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
                border_width=2, border_color="#708090", width=250, height=45,font=("Trebuchet MS", 12),
                command=lambda idx=info["idx"]: on_lei_selecionada(idx)
            )
            btn.pack(pady=5, padx=10)
            botoes_leis.append(btn)
        
        global botao_pular, botao_desfazer

        botao_voltar_interativo = Button.botao_voltar("Voltar", escolher_caminho)
        botao_voltar_interativo.configure(command=lambda: voltar_para(frame_abas), width=250, height=45)
        botao_voltar_interativo.pack(pady=5, padx=10)

        botao_pular = ctk.CTkButton(
            escolher_caminho, text="Pular ↪",
            fg_color="#DAA520", text_color="#000080", hover_color="#8B008B",
            border_width=2, border_color="#708090",
            font=("Trebuchet MS", 16), command=on_pular_selecionado, width=100
        )
        botao_pular.pack(side="left", padx=20, pady=10)

        botao_desfazer = ctk.CTkButton(
            escolher_caminho, text="Desfazer ↩",
            fg_color="#C0C0C0", text_color="#000000", hover_color="#A9A9A9",
            border_width=2, border_color="#696969",
            font=("Trebuchet MS", 16), command=on_desfazer_selecionado, state="disabled", width=100
        )
        botao_desfazer.pack(side="right", padx=20, pady=10)



       

        iniciar_rodada_interativa()

    #------------------------------------------------------------------------

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

    frame_info = ctk.CTkFrame(janela, fg_color="#082347")
    frame_info.grid(row=0, column=0, sticky="nsew")

    textbox_info = ctk.CTkTextbox(frame_info, font=("Trebuchet MS", 20), text_color="white", fg_color="#082347")
    textbox_info.pack(expand=True, fill="both", padx=20, pady=20)
    textbox_info.configure(fg_color="#00002C", text_color="white")  #Permitir edição para inserir o texto
    info_text = informacoes
    textbox_info.insert("0.0", info_text)  #Inserir o texto no Textbox
    textbox_info.configure(state="disable")  #Desativar edição para evitar modificações

    botao_voltar_info = Button.botao_voltar("Voltar", frame_info)
    botao_voltar_info.configure(command=lambda: voltar_para(frame_inicio))
    botao_voltar_info.pack(pady=20)

    #---------------- FRAME DE EQUIVALÊNCIA ----------------

    entrada2 = ctk.CTkEntry(frame_equivalencia, width=300, placeholder_text="Digite aqui", font=("Trebuchet MS", 14))
    entrada2.place(relx=0.5, y=200, anchor="center")

    entrada3 = ctk.CTkEntry(frame_equivalencia, width=300, placeholder_text="Digite aqui", font=("Trebuchet MS", 14))
    entrada3.place(relx=0.5, y=250, anchor="center")

    botao_comparar = Button.botao_padrao("Confirmar", frame_equivalencia)
    botao_comparar.configure(command=comparar)
    botao_comparar.place(relx=0.5, y=350, anchor="center")

    botao_voltar_equivalencia = Button.botao_voltar("Voltar", frame_equivalencia)
    botao_voltar_equivalencia.configure(command=lambda: voltar_para(frame_inicio))
    botao_voltar_equivalencia.place(relx=0.5, y=420, anchor="center")

    titulo = ctk.CTkLabel(frame_equivalencia, text="Digite as expressões que deseja comparar:", font=("Trebuchet MS Bold", 20), text_color="white", fg_color=None)
    titulo.place(relx=0.5, y=130, anchor="center")

    equivalente = ctk.CTkLabel(frame_equivalencia, text="É equivalente 😁", font=("Trebuchet MS Bold", 20), text_color="white", fg_color=None)
    nao_equivalente = ctk.CTkLabel(frame_equivalencia, text="Não é equivalente 😩", font=("Trebuchet MS Bold", 20), text_color="white", fg_color=None)
 
    show_frame(frame_inicio)
    janela.mainloop()