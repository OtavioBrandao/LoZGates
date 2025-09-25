import customtkinter as ctk
from customtkinter import CTkFont
import threading
import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageTk, ImageOps
import time
import webbrowser
import urllib.parse
from contextlib import redirect_stdout
import copy
import re

from config import ASSETS_PATH, informacoes, duvida_circuitos
from FrontEnd.design_tokens import Colors, Typography, Dimensions, Spacing, TabConfig, get_font, get_title_font

from BackEnd.imagem import converte_matrix_para_tkinter_imagem_icon
from BackEnd.tabela import gerar_tabela_verdade, verificar_conclusao
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.equivalencia import tabela
from BackEnd.identificar_lei import principal_simplificar
import BackEnd.simplificador_interativo as simpli
import BackEnd.principal as circuito_integrado

from FrontEnd.buttons import Button
from FrontEnd.problems_interface import setup_problems_interface
from FrontEnd.step_view import StepView, StepParser

from BackEnd.circuito_logico.circuit_mode_selector import CircuitModeManager
from FrontEnd.circuit_mode_interface import CircuitModeSelector
from FrontEnd.ai_chat_popup import AIChatPopup

from FrontEnd.logging_system import DetailedUserLogger, DetailedDataSharingDialog, ImprovedGoogleFormsSubmitter
user_logger = DetailedUserLogger("1.0-beta")

expressao_global = ""
botao_ver_circuito = None
label_convertida = None
arvore_interativa = None
passo_atual_info = None
nos_ignorados = set()
historico_interativo = []
botoes_leis = []
circuito_interativo_instance = None
does_it_has_interactveon = False

# Variáveis para a nova interface interativa
label_expressao_inicial = None
label_analise_atual = None
scroll_passos = None
contador_passos = 0
frame_expressao_inicial = None
frame_analise = None
frame_passos = None
frame_controles_interativo = None

def inicializar_interface():

    ctk.set_appearance_mode("dark")  # Modo escuro
    ctk.set_default_color_theme("blue")  # Tema azul
    janela = ctk.CTk()
    janela.title("LoZ Gates")
    janela.configure(bg=Colors.PRIMARY_BG)
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
        label = tk.Label(popup, text=mensagem, font=("Trebuchet MS", 12), fg="white", bg="#1a1a1a")
        label.pack(pady=(20, 10))

        botao_ok = tk.Button(popup, text="OK", bg="#7A2020", fg="white", command=popup.destroy)
        botao_ok.configure(width=8, height=1)
        botao_ok.pack(pady=(0, 10))

    def popup_duvida(mensagem):
        popup = tk.Toplevel(janela)  # <- tk.Toplevel ao invés de ctk.CTkToplevel
        popup.attributes('-topmost', True)
        popup.after(10, lambda: popup.attributes('-topmost', False))
        popup.title("Ajuda")
        popup.iconbitmap(os.path.join(ASSETS_PATH, "endeota.ico"))
        popup.configure(bg="#1a1a1a")
        # Cria o textbox e insere a mensagem de ajuda/informação
        textbox = tk.Text(popup, wrap="word", font=("Trebuchet MS", 12), fg="white", bg="#1a1a1a", borderwidth=0)
        textbox.pack(padx=10, pady=10, fill="both", expand=True)
        # Escreve a mensagem recebida + informações extras
        info_extra = "\n\nLoZ Gates - Ajuda\nEste aplicativo permite criar, visualizar e simplificar expressões de lógica proposicional.\nUse as abas para acessar circuitos, expressões e problemas reais."
        textbox.insert("1.0", info_extra + mensagem)
        textbox.configure(state="disabled")

        # Tamanho e centralização
        largura_popup = 400
        altura_popup = 400
        popup.geometry(f"{largura_popup}x{altura_popup}")
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (largura_popup // 2)
        y = (popup.winfo_screenheight() // 2) - (altura_popup // 2)
        popup.geometry(f"{largura_popup}x{altura_popup}+{x}+{y}")

    def trocar_para_abas():
        try:
            caminho_entrada = os.path.join(ASSETS_PATH, "entrada.txt")
            start_time = time.time()
            expressao = entrada.get().strip().upper().replace(" ", "")
            
            user_logger.log_expression_entered(expressao, bool(expressao))
            
            if not expressao:
                user_logger.log_error("validation_error", "Empty expression")
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
            
            # Mostrar frame das abas (a criação do circuito interativo acontecerá no callback da aba)
            show_frame(frame_abas)
            duration = time.time() - start_time
            user_logger.log_feature_used("circuit_generation", duration)
            
        except Exception as e:
            popup_erro(f"Erro ao processar expressão: {e}")
            print(f"Erro detalhado: {e}")
            
    #Detecta mudança de aba e recria o circuito se necessário
    def on_tab_change():
        global does_it_have_interaction
        try:
            atual_tab = abas.get()
            user_logger.log_tab_changed("tab_navigation", atual_tab)
            if atual_tab == "  Circuito Interativo  ":
                # Garante que a expressão existe antes de criar qualquer coisa
                if not expressao_global:
                    print("Expressão global não definida - não é possível criar circuito")
                    return
                    
                # Atualiza display da expressão se a instância existir
                if (circuito_interativo_instance and 
                    hasattr(circuito_interativo_instance, 'update_expression_display')):
                    circuito_interativo_instance.update_expression_display()
                    
                # Só cria se realmente necessário
                if_necessary_create_a_circuit()
        except Exception as e:
            print(f"Erro ao detectar mudança de aba: {e}")
           
    def if_necessary_create_a_circuit():
        """Cria o circuito interativo apenas se ele não existir ou estiver vazio"""
        global circuito_interativo_instance, does_it_have_interaction
        
        # Verifica se o frame está vazio ou se a instância não existe
        frame_vazio = len(frame_circuito_interativo.winfo_children()) == 0
        instancia_inexistente = circuito_interativo_instance is None
        
        # Só cria se não existir
        if frame_vazio or instancia_inexistente:
            print("Criando interface de seleção de modo...")
            # Usa a expressão atual da entrada, não uma vazia
            expressao_atual = entrada.get().strip().upper().replace(" ", "") if entrada.get().strip() else expressao_global
            if expressao_atual:
                create_interactive_circuit(expressao_atual)
            else:
                print("Nenhuma expressão disponível para criar circuito")
        else:
            print("Interface já existe - mantendo")

    def create_interactive_circuit(expressao):
        """Cria o circuito interativo com seleção de modos."""
        global circuito_interativo_instance, does_it_have_interaction
        
        # LOG INÍCIO DO CIRCUITO INTERATIVO
        user_logger.log_circuit_interaction_start()
        
        def get_global_expression():
            return expressao_global if expressao_global else expressao
        
        if circuito_interativo_instance:
            try:
                circuito_interativo_instance.cleanup()
            except:
                pass
        
        for widget in frame_circuito_interativo.winfo_children():
            widget.destroy()
        
        try:
            circuito_interativo_instance = CircuitModeSelector(
                frame_circuito_interativo, 
                CircuitModeManager(),
                Button,
                get_global_expression,
                logger=user_logger 
            )
            does_it_have_interaction = False
            print("Interface de circuito com modos criada!")
            
        except Exception as e:
            print(f"Erro ao criar interface: {e}")
            does_it_have_interaction = False
            
            error_label = ctk.CTkLabel(
                frame_circuito_interativo,
                text=f"Erro ao criar circuito interativo: {e}",
                text_color="red"
            )
            error_label.pack(expand=True)
            
    def confirmar_expressao():
        global botao_ver_circuito
        if botao_ver_circuito:  
            botao_ver_circuito.destroy()

        expressao_texto = entrada.get().strip()
        if not expressao_texto:
            user_logger.log_expression_entered("", False)
            popup_erro("A expressão não pode estar vazia.")
            return
        
        # LOG DA EXPRESSÃO INSERIDA
        user_logger.log_expression_entered(expressao_texto.upper().replace(" ", ""), True)
        
        try:
            esconder_botoes_simplificar()
        except:
            pass
        
        botao_ver_circuito = Button.botao_padrao("🔌Ver Circuito", principal)
        botao_ver_circuito.configure(command=lambda: trocar_para_abas())
        botao_ver_circuito.place(relx=0.5, y=500, anchor="center")

    def exibir_tabela_verdade(expressao):
        try:
            janela_tabela = ctk.CTkToplevel(janela)
            janela_tabela.title("Tabela Verdade")
            janela_tabela.geometry("1000x700")
            janela_tabela.lift()
            janela_tabela.attributes('-topmost', True)
            janela_tabela.after(10, lambda: janela_tabela.attributes('-topmost', False))
            janela_tabela.configure(fg_color=Colors.PRIMARY_BG)

            # Gera a tabela verdade usando a função do backend
            dados_tabela = gerar_tabela_verdade(expressao)
            
            # Extrai os dados do dicionário retornado
            colunas = dados_tabela["colunas"]
            tabela = dados_tabela["tabela"]
            resultados_finais = dados_tabela["resultados_finais"]

            # Container principal
            main_container = ctk.CTkFrame(
                janela_tabela,
                fg_color=Colors.PRIMARY_BG,
                corner_radius=0
            )
            main_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

            # Título da janela
            titulo_tabela = ctk.CTkLabel(
                main_container,
                text=f"Tabela Verdade: {expressao}",
                font=get_title_font(Typography.SIZE_TITLE_MEDIUM),
                text_color=Colors.TEXT_ACCENT
            )
            titulo_tabela.pack(pady=(Spacing.SM, Spacing.LG))

            # Frame da tabela com design padronizado
            frame_tabela_container = ctk.CTkFrame(
                main_container,
                fg_color=Colors.SURFACE_LIGHT,
                corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
            )
            frame_tabela_container.pack(fill="both", expand=True, pady=(0, Spacing.MD))

            # Área scrollável para a tabela
            frame_tabela = ctk.CTkScrollableFrame(
                frame_tabela_container,
                fg_color=Colors.SURFACE_DARK,
                corner_radius=Dimensions.CORNER_RADIUS_SMALL
            )
            frame_tabela.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)

            # Calcular larguras otimizadas para cada coluna
            larguras = []
            for i, col in enumerate(colunas):
                max_len = len(str(col))
                for linha in tabela:
                    if i < len(linha):
                        max_len = max(max_len, len(str(linha[i])))
                larguras.append(max(max_len + 1, 3))  # Mínimo 3, +1 para espaçamento

            # Cabeçalho da tabela
            header_frame = ctk.CTkFrame(
                frame_tabela,
                fg_color=Colors.SURFACE_MEDIUM,
                corner_radius=Dimensions.CORNER_RADIUS_SMALL
            )
            header_frame.pack(fill="x", pady=(0, Spacing.XS))

            cabecalho_str = " │ ".join([f"{str(col):^{w}}" for col, w in zip(colunas, larguras)])
            label_cabecalho = ctk.CTkLabel(
                header_frame,
                text=cabecalho_str,
                font=("Consolas", 12, "bold"),
                text_color=Colors.TEXT_ACCENT
            )
            label_cabecalho.pack(pady=Spacing.SM)

            # Linhas da tabela
            for i, linha_valores in enumerate(tabela):
                linha_frame = ctk.CTkFrame(
                    frame_tabela,
                    fg_color=Colors.SURFACE_LIGHT if i % 2 == 0 else Colors.SURFACE_MEDIUM,
                    corner_radius=Dimensions.CORNER_RADIUS_SMALL
                )
                linha_frame.pack(fill="x", pady=Spacing.XS)

                linha_str = " │ ".join([f"{str(val):^{w}}" for val, w in zip(linha_valores, larguras)])
                label_linha = ctk.CTkLabel(
                    linha_frame,
                    text=linha_str,
                    font=("Consolas", 12),
                    text_color=Colors.TEXT_PRIMARY
                )
                label_linha.pack(pady=Spacing.XS)

            # Frame para conclusão
            conclusao_frame = ctk.CTkFrame(
                main_container,
                fg_color=Colors.SURFACE_MEDIUM,
                corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
            )
            conclusao_frame.pack(fill="x", pady=(0, Spacing.MD))

            # Verifica a conclusão da expressão
            conclusao = verificar_conclusao(resultados_finais)
            
            # Define cor baseada no tipo de conclusão
            if "TAUTOLOGIA" in conclusao:
                cor_conclusao = Colors.SUCCESS
            elif "CONTRADIÇÃO" in conclusao:
                cor_conclusao = Colors.ERROR
            else:
                cor_conclusao = Colors.INFO

            label_conclusao = ctk.CTkLabel(
                conclusao_frame,
                text=conclusao,
                font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
                text_color=cor_conclusao
            )
            label_conclusao.pack(pady=Spacing.MD)

            # Botão para fechar
            botao_fechar = Button.botao_padrao("Fechar", main_container)
            botao_fechar.configure(command=janela_tabela.destroy)
            botao_fechar.pack(pady=Spacing.SM)
            
        except Exception as e:
            popup_erro(f"Erro ao gerar tabela verdade: {e}")
            print(f"Erro detalhado: {e}")

    def comparar():
        try:
            expressao2 = entrada2.get().strip().upper()
            expressao3 = entrada3.get().strip().upper()
            
            if not expressao2 or not expressao3:
                popup_erro("As expressões não podem estar vazias.")
                return
            
            valor = tabela(expressao2, expressao3)
            resultado = valor == 1

            # LOG DETALHADO COM EXPRESSÕES REAIS
            user_logger.log_equivalence_check_with_expressions(
                expressao2, expressao3, resultado
            )
            
            if resultado:
                equivalente.place(relx=0.5, y=360, anchor="center")
                nao_equivalente.place_forget()
            else:
                nao_equivalente.place(relx=0.5, y=360, anchor="center")
                equivalente.place_forget()
                
        except Exception as e:
            user_logger.log_error("equivalence_check_error", str(e), "comparar_function")
            popup_erro(f"Erro ao comparar expressões: {e}")
              
    def go_back_to(frame):
        try:
            global botao_ver_circuito, circuito_interativo_instance, does_it_have_interaction
            
            if botao_ver_circuito:
                botao_ver_circuito.destroy()
                botao_ver_circuito = None

            # Lógica melhorada para parar o circuito
            if circuito_interativo_instance:
                # Se voltando para frame_abas, NÃO para o circuito
                if frame == frame_abas:
                    print("Voltando para abas - mantendo circuito ativo")
                else:
                    # Para qualquer outro destino, para o circuito
                    try:
                        circuito_interativo_instance.cleanup()
                        circuito_interativo_instance = None
                        does_it_have_interaction = False
                        print("Circuito interativo limpo")
                    except Exception as e:
                        print(f"Erro ao limpar circuito: {e}")

            # Limpa as entradas apenas se não for para certas telas
            if frame not in [frame_abas, frame_resolucao_direta, frame_interativo]:
                entrada.delete(0, tk.END) 
                does_it_have_interaction = False
                try:
                    esconder_botoes_simplificar()  # Reset dos botões ao limpar entrada
                except:
                    pass

            entrada2.delete(0, tk.END)  
            entrada3.delete(0, tk.END) 
            
            entrada.configure(placeholder_text="Digite aqui")
            entrada2.configure(placeholder_text="Digite aqui")
            entrada3.configure(placeholder_text="Digite aqui")
            
            equivalente.place_forget()
            nao_equivalente.place_forget()
            
            # Esconde os resultados da aba de expressão ao voltar apenas se NÃO for para frame_abas
            if frame != frame_abas:
                label_convertida.pack_forget()
                log_simplificacao_textbox.pack_forget()
                step_view.pack_forget()
                try:
                    esconder_botoes_simplificar()  # Esconde botões de simplificação
                except:
                    pass

            show_frame(frame)
            janela.focus_set()

            if frame == principal:
                entrada.focus_set()
            
            # Se voltando para frame_abas, garante que a interface esteja disponível
            if frame == frame_abas and expressao_global:
                janela.after(200, if_necessary_create_a_circuit)
            
        except Exception as e:
            popup_erro(f"Erro ao voltar: {e}")
            print(f"Erro detalhado: {e}")
       
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
    
    #------------- DEFININDO OS FRAMES DA INTERFACE -------------
    
    frame_inicio = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_inicio.grid(row=0, column=0, sticky="nsew")

    principal = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    principal.grid(row=0, column=0, sticky="nsew")

    frame_equivalencia = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_equivalencia.grid(row=0, column=0, sticky="nsew")

    frame_abas = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_abas.grid(row=0, column=0, sticky="nsew")

    frame_resolucao_direta = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_resolucao_direta.grid(row=0, column=0, sticky="nsew")

    scroll_conteudo = ctk.CTkScrollableFrame(frame_resolucao_direta, fg_color=Colors.PRIMARY_BG)
    scroll_conteudo.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)

    frame_interativo = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_interativo.grid(row=0, column=0, sticky="nsew")

    frame_problemas_reais = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_problemas_reais.grid(row=0, column=0, sticky="nsew")

    scroll_problemas_reais = ctk.CTkScrollableFrame(frame_problemas_reais, fg_color=Colors.PRIMARY_BG)
    scroll_problemas_reais.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)
    scroll_problemas_reais._scrollbar.grid_remove()

    frame_explicacao_problemas_reais = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_explicacao_problemas_reais.grid(row=0, column=0, sticky="nsew")

    #---------------- FRAME DE INÍCIO ----------------
 
    fonte_momentz = CTkFont(family="Momentz", size=Typography.SIZE_TITLE_LARGE + 2)
    label_inicio = ctk.CTkLabel(
        frame_inicio,
        text="<LoZ Gates>",
        font=fonte_momentz,
        text_color=Colors.TEXT_PRIMARY,
        fg_color=Colors.PRIMARY_BG
    )
    label_inicio.place(relx=0.5, y=200, anchor="center")

    botao_circuitos = Button.botao_padrao("💡Circuitos e Expressões", frame_inicio)
    botao_circuitos.configure(command=lambda: show_frame(principal))
    botao_circuitos.place(relx=0.5, y=300, anchor="center")

    botao_equivalencia = Button.botao_padrao("🔄Equivalência Lógica", frame_inicio)
    botao_equivalencia.configure(command=lambda: show_frame(frame_equivalencia))
    botao_equivalencia.place(relx=0.5, y=400, anchor="center")
    
    botao_info = Button.botao_padrao("❔Ajuda", frame_inicio)
    botao_info.configure(command=lambda: show_frame(frame_info))
    botao_info.place(relx=0.5, y=500, anchor="center")

    #---------------- FRAME DOS CIRCUITOS E DAS EXPRESSÕES ----------------

    label_tarefas = ctk.CTkLabel(
        principal, 
        text="Digite a expressão em Lógica Proposicional:", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.TEXT_PRIMARY, 
        fg_color=None
    )
    label_tarefas.place(relx=0.5, y=150, anchor="center")

    entrada = ctk.CTkEntry(
        principal, 
        width=350, 
        placeholder_text="Digite aqui", 
        font=get_font(Typography.SIZE_BODY_SMALL),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
    )
    entrada.place(relx=0.5, y=200, anchor="center")
    entrada.bind("<Return>", lambda event: confirmar_expressao())

    botao_confirmar_expressao = Button.botao_padrao("✅Confirmar", principal, style="success")
    botao_confirmar_expressao.configure(command=confirmar_expressao, hover_color="#16723D")
    botao_confirmar_expressao.place(relx=0.5, y=280, anchor="center")
    
    botao_problemas_reais = Button.botao_padrao("🔬Problemas Reais", principal)
    botao_problemas_reais.configure(command=lambda: show_frame(frame_problemas_reais))
    botao_problemas_reais.place(relx=0.5, y=360, anchor="center")

    botao_go_back_to_inicio = Button.botao_voltar("Voltar", principal)
    botao_go_back_to_inicio.configure(command=lambda: go_back_to(frame_inicio))
    botao_go_back_to_inicio.place(relx=0.5, y=440, anchor="center")
    
    #---------------- FRAME DOS PROBLEMAS REAIS ----------------

    setup_problems_interface(scroll_problemas_reais, go_back_to, principal, Button)
    
    #---------------- FRAME DE ABAS ----------------

    abas = ctk.CTkTabview(
        master=frame_abas, 
        fg_color=Colors.PRIMARY_BG, 
        segmented_button_fg_color=TabConfig.BACKGROUND_COLOR, 
        segmented_button_selected_color=TabConfig.SELECTED_COLOR,
        segmented_button_selected_hover_color=TabConfig.SELECTED_HOVER, 
        segmented_button_unselected_color=TabConfig.UNSELECTED_COLOR,
        segmented_button_unselected_hover_color=TabConfig.UNSELECTED_HOVER, 
        command=on_tab_change
    )
    abas.pack(expand=True, fill="both")

    #---------------------- ABA DO CIRCUITO ----------------------

    aba_circuito = abas.add("      Circuito      ")
    scroll_frame1 = ctk.CTkScrollableFrame(aba_circuito, fg_color=Colors.PRIMARY_BG)
    scroll_frame1.pack(expand=True, fill="both")

    label_circuito_expressao = ctk.CTkLabel(
        scroll_frame1, 
        font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD), 
        text_color=Colors.TEXT_ACCENT, 
        text=""
    )
    label_circuito_expressao.pack(pady=Spacing.MD)

    botao_duvida1 = Button.botao_duvida(scroll_frame1)
    botao_duvida1.place(relx=0.95, y=5, anchor="ne")
    botao_duvida1.configure(command=lambda: popup_duvida(duvida_circuitos))

    imagem_circuito = ctk.CTkLabel(scroll_frame1, text="")
    imagem_circuito.pack(pady=Spacing.MD)

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
            
    botao_salvar = Button.botao_padrao("💾 Salvar circuito como PNG", scroll_frame1)
    botao_salvar.configure(command=salvar_imagem)
    botao_salvar.pack(pady=Spacing.LG)
 #------------------------------------------------ ABA DO CIRCUITO INTERATIVO  ----------------------------------------------
    aba_circuito_interativo = abas.add("  Circuito Interativo  ")
    frame_circuito_interativo = tk.Frame(aba_circuito_interativo, bg=Colors.PRIMARY_BG)
    frame_circuito_interativo.pack(expand=True, fill="both", padx=Spacing.SM, pady=Spacing.SM)
    
 #------------------------------------------------ ABA DE EXPRESSÃO  ----------------------------------------------
 
    aba_expressao = abas.add("      Expressão      ")
    scroll_frame2 = ctk.CTkScrollableFrame(aba_expressao, fg_color=Colors.PRIMARY_BG)
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

    # Componente StepView para visualização passo a passo
    step_view = StepView(scroll_conteudo)
    
    frame_borda = ctk.CTkFrame(
        master=scroll_conteudo,
        fg_color=Colors.TEXT_PRIMARY, 
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
    )
    label_convertida = ctk.CTkLabel(
        scroll_frame2, 
        text="", 
        font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD), 
        text_color=Colors.TEXT_PRIMARY
    )
    log_simplificacao_textbox = ctk.CTkTextbox(
        frame_borda,  
        wrap="word", 
        font=get_font(Typography.SIZE_SUBTITLE), 
        height=600, 
        width=900
    )
    log_simplificacao_textbox.configure(fg_color=Colors.SURFACE_DARK)

    def mostrar_expressao_convertida():
        try:
            # Esconde elementos antigos
            log_simplificacao_textbox.pack_forget()
            step_view.pack_forget()
            label_solucao.pack_forget()
            frame_borda.pack_forget()
            
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
        

    label_solucao = ctk.CTkLabel(
        scroll_conteudo, 
        text="Solução da expressão:", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.TEXT_PRIMARY
    )

    def expressao_simplificada():
        try:
            # 1. Pega a expressão mais recente direto da caixa de entrada principal
            entrada_txt = entrada.get().strip().upper()
            if not entrada_txt:
                popup_erro("A expressão na tela principal está vazia.")
                return

            # 2. Converte para o formato de álgebra booleana
            expressao_para_simplificar = converter_para_algebra_booleana(entrada_txt)
            
            # Esconde componentes antigos e mostra StepView
            if label_solucao.winfo_ismapped():
                label_solucao.pack_forget()
                log_simplificacao_textbox.pack_forget()
                frame_borda.pack_forget()

            label_solucao.pack(pady=Spacing.LG)
            step_view.pack(fill="both", expand=True, pady=Spacing.MD)
            step_view.configure(height=800)
            botao_go_back_to_aba2.pack(pady=Spacing.MD)

            # Inicializa StepView
            step_view.reset(expressao_para_simplificar)
            
            # Parser para converter log em passos
            parser = StepParser(step_view)
            
            class StepLogger:
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

            step_logger = StepLogger(parser)

            def simplificar_thread():
                with redirect_stdout(step_logger):
                    try:
                        # 3. Usa a expressão recém-capturada e convertida
                        principal_simplificar(expressao_para_simplificar)
                        # Finaliza o parsing
                        janela.after(0, lambda: parser.finalize_parsing(expressao_para_simplificar, True))
                    except Exception as e:
                        janela.after(0, lambda: popup_erro(f"\n--- OCORREU UM ERRO ---\n{e}"))

            threading.Thread(target=simplificar_thread).start()
        except Exception as e:
            popup_erro(f"Erro ao simplificar expressão: {e}")
            
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

    def executar_conversao():
        try:
            esconder_botoes_simplificar()  # Esconde botões antigos primeiro
        except:
            pass
        mostrar_expressao_convertida()
        mostrar_botoes_simplificar()   # Mostra novos botões
    
    def go_to_interactive():
        #Função wrapper para garantir a ordem correta das chamadas
        show_frame(frame_interativo)
        parte_interativa()

    def executar_simplificacao_interativa():
        esconder_botoes_simplificar()
        go_to_interactive()
    
    botao_converter = Button.botao_padrao("🔗Realizar conversão", scroll_frame2)
    botao_converter.configure(command=executar_conversao)
    botao_converter.pack(pady=Spacing.MD)

    botao_interativo = Button.botao_padrao("🔎Simplificar - Interativo", scroll_frame2)
    botao_interativo.configure(command=executar_simplificacao_interativa)

    
    # Variáveis globais para componentes interativos (serão criadas dinamicamente)
    escolher_caminho = None
    area_expressao = None
    
#---------------------- PARTE DA SIMPLFICAÇÃO ---------------------------------
    # Variável para controlar visibilidade dos botões
    botoes_visiveis = False
    
    def mostrar_botoes_simplificar():
        global botoes_visiveis
        if not botoes_visiveis:
            botao_solucao.pack(pady=Spacing.MD)
            botao_interativo.pack(pady=Spacing.MD)
            botoes_visiveis = True
    
    def esconder_botoes_simplificar():
        global botoes_visiveis
        try:
            if botoes_visiveis:
                botao_solucao.pack_forget()
                botao_interativo.pack_forget()
                botoes_visiveis = False
        except:
            botoes_visiveis = False

    def executar_simplificacao_resultado():
        try:
            esconder_botoes_simplificar()
        except:
            pass
        show_frame(frame_resolucao_direta)
        expressao_simplificada()

    def executar_simplificacao_interativa():
        esconder_botoes_simplificar()
        go_to_interactive()

    botao_solucao = Button.botao_padrao("🔍Simplificar - Resultado", scroll_frame2)
    botao_solucao.configure(command=executar_simplificacao_resultado)

    def voltar_para_abas():
        # Mostra os botões novamente quando voltar para as abas
        if expressao_booleana_atual:  # Se há uma expressão convertida
            mostrar_botoes_simplificar()
        go_back_to(frame_abas)
    
    botao_go_back_to_aba2 = Button.botao_voltar("Voltar", scroll_conteudo)
    botao_go_back_to_aba2.configure(command=voltar_para_abas)
    botao_go_back_to_aba2.pack(side="bottom", pady=Spacing.MD)
    
    def finalizar_sessao_expressao(expression, resolvida=False):
        # """Finaliza a sessão e registra os dados finais"""
        # global tempo_inicio_expressao, tentativas_atuais
    
        # if tempo_inicio_expressao is None:
        #     return
        
        # tempo_total = time.time() - tempo_inicio_expressao
    
        # tempo_inicio_expressao = None
        # tentativas_atuais = 0
        pass


#------------------ MODO INTERATIVO LÓGICA E FUNÇÕES MODIFICADAS ----------------------
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
        global contador_passos

        if not historico_de_estados:
            print("Nada para desfazer.") 
            return

        # LOG DO UNDO
        user_logger.log_simplification_undo()

        estado_anterior = historico_de_estados.pop()
        arvore_interativa = estado_anterior['arvore']
        historico_interativo = estado_anterior['historico']
        nos_ignorados = estado_anterior['ignorados']
        passo_atual_info = estado_anterior['passo_info']
        
        if contador_passos > 0:
            contador_passos -= 1
        
        reconstruir_area_passos()

        if not historico_de_estados:
            botao_desfazer.configure(state="disabled")
        atualizar_ui_interativa()
  
    def inicializar_area_passos():
        """Inicializa a área de passos com a expressão inicial"""
        global scroll_passos, contador_passos
        contador_passos = 0
        
        # Limpa área anterior
        for widget in scroll_passos.winfo_children():
            widget.destroy()
        
        # Adiciona passo inicial
        adicionar_passo_inicial(str(arvore_interativa))
    
    def adicionar_passo_inicial(expressao_inicial):
        """Adiciona o passo inicial à área de passos"""
        passo_frame = ctk.CTkFrame(
            scroll_passos,
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        passo_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        titulo_passo = ctk.CTkLabel(
            passo_frame,
            text="Estado Inicial",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_passo.pack(pady=(Spacing.SM, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        expressao_label = ctk.CTkLabel(
            passo_frame,
            text=expressao_inicial,
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=700
        )
        expressao_label.pack(pady=(0, Spacing.SM), padx=Spacing.SM, anchor="w")
    
    def adicionar_passo_sucesso(lei_nome, subexpressao, antes, depois, resultado):
        """Adiciona um passo de sucesso à área de passos"""
        global contador_passos
        contador_passos += 1
        
        passo_frame = ctk.CTkFrame(
            scroll_passos,
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        passo_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        # Título com número do passo e lei
        titulo_passo = ctk.CTkLabel(
            passo_frame,
            text=f"Passo {contador_passos} — {lei_nome}",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_passo.pack(pady=(Spacing.SM, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        # Subexpressão analisada
        if subexpressao:
            sub_label = ctk.CTkLabel(
                passo_frame,
                text=f"Subexpressão: {subexpressao}",
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_SECONDARY
            )
            sub_label.pack(pady=(0, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        # Transformação
        transform_frame = ctk.CTkFrame(
            passo_frame,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        transform_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        transform_text = f"{antes} → {depois}"
        transform_label = ctk.CTkLabel(
            transform_frame,
            text=transform_text,
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=700
        )
        transform_label.pack(pady=Spacing.SM, padx=Spacing.SM)
        
        # Resultado
        resultado_frame = ctk.CTkFrame(passo_frame, fg_color="transparent")
        resultado_frame.pack(fill="x", pady=(Spacing.XS, Spacing.SM), padx=Spacing.SM)
        
        status_label = ctk.CTkLabel(
            resultado_frame,
            text=f"✔ {resultado}",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.SUCCESS
        )
        status_label.pack(side="left")
        
        # Auto-scroll para o final
        scroll_passos.after(100, lambda: scroll_passos._parent_canvas.yview_moveto(1.0))
    
    def adicionar_passo_pular(subexpressao):
        """Adiciona um passo de pular à área de passos"""
        passo_frame = ctk.CTkFrame(
            scroll_passos,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        passo_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        titulo_passo = ctk.CTkLabel(
            passo_frame,
            text="Subexpressão Ignorada",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_SECONDARY
        )
        titulo_passo.pack(pady=(Spacing.SM, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        sub_label = ctk.CTkLabel(
            passo_frame,
            text=f"↷ '{subexpressao}' foi ignorada",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        sub_label.pack(pady=(0, Spacing.SM), padx=Spacing.SM, anchor="w")
        
        # Auto-scroll para o final
        scroll_passos.after(100, lambda: scroll_passos._parent_canvas.yview_moveto(1.0))
    
    def atualizar_area_passos():
        """Atualiza a área de passos (chamada quando necessário)"""
        # Esta função pode ser expandida se necessário para atualizações dinâmicas
        pass
    
    def reconstruir_area_passos():
        """Reconstrói a área de passos baseada no histórico atual"""
        global scroll_passos
        
        # Limpa área atual
        for widget in scroll_passos.winfo_children():
            widget.destroy()
        
        # Adiciona passo inicial
        if historico_interativo and len(historico_interativo) > 0:
            # Extrai expressão inicial do primeiro item do histórico
            primeiro_item = historico_interativo[0]
            if "Expressão Inicial:" in primeiro_item:
                expressao_inicial = primeiro_item.replace("Expressão Inicial:", "").strip()
                adicionar_passo_inicial(expressao_inicial)
            
            # Reconstrói passos baseado no histórico
            passo_num = 0
            i = 1
            while i < len(historico_interativo):
                linha = historico_interativo[i]
                if "✓ Lei" in linha and "aplicada com sucesso" in linha:
                    passo_num += 1
                    # Extrai nome da lei
                    lei_match = re.search(r"Lei '(.+?)' aplicada", linha)
                    lei_nome = lei_match.group(1) if lei_match else "Lei desconhecida"
                    
                    # Próxima linha deve ter a nova expressão
                    if i + 1 < len(historico_interativo):
                        proxima_linha = historico_interativo[i + 1]
                        if "Nova Expressão:" in proxima_linha:
                            nova_expr = proxima_linha.replace("Nova Expressão:", "").strip()
                            adicionar_passo_sucesso(lei_nome, "", "(anterior)", "(simplificada)", nova_expr)
                            i += 1  # Pula a próxima linha já processada
                elif "↷ Sub-expressão" in linha and "ignorada" in linha:
                    # Extrai subexpressão ignorada
                    ignore_match = re.search(r"'(.+?)' ignorada", linha)
                    subexpr = ignore_match.group(1) if ignore_match else "desconhecida"
                    adicionar_passo_pular(subexpr)
                i += 1

    def on_lei_selecionada(indice_lei):
        global arvore_interativa, passo_atual_info, historico_interativo, nos_ignorados, botao_desfazer
        global expressao_global, contador_passos

        if not passo_atual_info:
            return

        salvar_estado_atual()
        botao_desfazer.configure(state="normal")

        lei_usada = simpli.LEIS_LOGICAS[indice_lei]['nome']
        subexpressao_antes = str(passo_atual_info['no_atual'])
        
        nova_arvore, sucesso = simpli.aplicar_lei_e_substituir(arvore_interativa, passo_atual_info, indice_lei)
        
        # LOG DA APLICAÇÃO DE LEI
        user_logger.log_law_applied(lei_usada, sucesso, contador_passos + 1)
        
        if sucesso:
            arvore_interativa = nova_arvore
            
            historico_interativo.append(f"✓ Lei '{lei_usada}' aplicada com sucesso.")
            historico_interativo.append(f"   Nova Expressão: {str(arvore_interativa)}")
            nos_ignorados = set()
            
            adicionar_passo_sucesso(
                lei_usada, subexpressao_antes, subexpressao_antes,
                "(simplificada)", str(arvore_interativa)
            )
            iniciar_rodada_interativa()
        else:
            # LOG DA FALHA
            full_expression_state = str(arvore_interativa)
            reason_for_failure = f"Lei não aplicável à subexpressão '{subexpressao_antes}' no contexto de '{full_expression_state}'"
            user_logger.log_simplification_step_failed(lei_usada, contador_passos + 1, reason_for_failure, full_expression_state)
            
            historico_de_estados.pop()
            if not historico_de_estados:
                botao_desfazer.configure(state="disabled")
            popup_erro("Não foi possível aplicar esta lei.")

    def on_pular_selecionado():
        global nos_ignorados, passo_atual_info, historico_interativo, botao_desfazer, contador_passos
        if passo_atual_info and passo_atual_info['no_atual']:
            salvar_estado_atual()
            botao_desfazer.configure(state="normal")
            subexpressao_ignorada = str(passo_atual_info['no_atual'])
            
            # LOG DO PULAR
            user_logger.log_simplification_skip(contador_passos)
            
            nos_ignorados.add(passo_atual_info['no_atual'])
            historico_interativo.append(f"↷ Sub-expressão '{subexpressao_ignorada}' ignorada.")
            adicionar_passo_pular(subexpressao_ignorada)
            iniciar_rodada_interativa()

    def atualizar_ui_interativa():
        global botoes_leis, label_expressao_inicial, label_analise_atual, scroll_passos
        
        # Atualiza expressão inicial
        if label_expressao_inicial and arvore_interativa:
            label_expressao_inicial.configure(text=str(arvore_interativa))
        
        # Atualiza análise atual
        if passo_atual_info:
            sub_expr = str(passo_atual_info['no_atual'])
            label_analise_atual.configure(
                text=f"🔍 Analisando subexpressão: '{sub_expr}'\n📚 Selecione uma lei para aplicar.",
                text_color=Colors.TEXT_PRIMARY
            )
            
            # Habilita botões
            if botoes_leis:
                for botao in botoes_leis:
                    botao.configure(state="normal")
            if botao_pular:
                botao_pular.configure(state="normal")
        else:
            label_analise_atual.configure(
                text="✅ Simplificação concluída!\n🎉 Nenhuma outra lei pode ser aplicada.",
                text_color=Colors.SUCCESS
            )
            
            if historico_interativo: # Garante que a sessão foi iniciada
                total_steps = contador_passos
                laws_used = [line for line in historico_interativo if "✓ Lei" in line]
                user_logger.log_simplification_completed(total_steps, laws_used)
                
                # Reseta o histórico para não logar a mesma sessão duas vezes
                historico_interativo = [] 
            
            # Finaliza a sessão quando não há mais possibilidades
            finalizar_sessao_expressao(str(expressao_global), resolvida=True)
            
            # Desabilita botões
            if botoes_leis:
                for botao in botoes_leis:
                    botao.configure(state="disabled")
            if botao_pular:
                botao_pular.configure(state="disabled")
        
        # Atualiza área de passos
        atualizar_area_passos()

    def iniciar_rodada_interativa():
        global passo_atual_info
        passo_atual_info = simpli.encontrar_proximo_passo(arvore_interativa, nos_a_ignorar=nos_ignorados)
        atualizar_ui_interativa()
        
    def parte_interativa():
        global arvore_interativa, historico_interativo, nos_ignorados, passo_atual_info, expressao_global, botoes_leis, historico_de_estados, simplification_start_time
        
        if not expressao_global:
            popup_erro("Por favor, primeiro insira e converta uma expressão.")
            go_back_to(frame_abas)
            show_frame(principal) 
            return
            
        try:
            simplification_start_time = time.time()
            
            # LOG INÍCIO DA SESSÃO INTERATIVA
            user_logger.log_interactive_simplification_start(expressao_global)
            
            arvore_interativa = simpli.construir_arvore(expressao_global)
        except Exception as e:
            popup_erro(f"Erro ao construir a expressão: {e}")
            go_back_to(scroll_frame2)
            return

        historico_interativo = [f"Expressão Inicial: {str(arvore_interativa)}"]
        nos_ignorados = set()
        passo_atual_info = None
        historico_de_estados = []
        
        criar_interface_interativa_padronizada()
        inicializar_area_passos()
        iniciar_rodada_interativa()
        duration = time.time() - simplification_start_time
        user_logger.log_feature_used("interactive_mode", duration)
        
    def limpar_frame_interativo():
        for widget in frame_interativo.winfo_children():
            widget.destroy()
    
    def abrir_chat_ia():
        """Abre o popup de chat com IA para o simplificador interativo"""
        try:
            expressao_atual = str(arvore_interativa) if arvore_interativa else expressao_global
            contexto_passo = ""
            
            if passo_atual_info:
                subexpr = str(passo_atual_info['no_atual'])
                contexto_passo = f"Analisando subexpressão: {subexpr}"
            
            AIChatPopup(janela, expressao_atual, contexto_passo)
        except Exception as e:
            popup_erro(f"Erro ao abrir chat com IA: {e}")
    
    def criar_interface_interativa_padronizada():
        global escolher_caminho, area_expressao, botoes_leis, botao_pular, botao_desfazer
        global frame_expressao_inicial, frame_analise, frame_passos, frame_controles_interativo
        
        # Container principal com scroll
        main_container = ctk.CTkScrollableFrame(frame_interativo, fg_color=Colors.PRIMARY_BG)
        main_container.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)
        
        # Configurar grid para expansão
        main_container.grid_rowconfigure(2, weight=1)  # frame_passos deve expandir
        main_container.grid_columnconfigure(0, weight=1)
        
        # 1. SEÇÃO: Expressão Inicial
        frame_expressao_inicial = ctk.CTkFrame(
            main_container,
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        frame_expressao_inicial.pack(fill="x", pady=(0, Spacing.MD))
        
        # Container para título e botão IA
        header_frame = ctk.CTkFrame(frame_expressao_inicial, fg_color="transparent")
        header_frame.pack(fill="x", pady=(Spacing.SM, Spacing.XS), padx=Spacing.SM)
        
        titulo_inicial = ctk.CTkLabel(
            header_frame,
            text="Expressão Inicial",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_inicial.pack(side="left")
        
        # Botão Sugestão de IA
        botao_ia = Button.botao_padrao("🤖 Sugestão de IA", header_frame)
        botao_ia.configure(
            command=abrir_chat_ia,
            width=140,
            height=32,
            font=get_font(Typography.SIZE_BODY_SMALL)
        )
        botao_ia.pack(side="right")
        
        # Label para mostrar a expressão inicial (será atualizada dinamicamente)
        global label_expressao_inicial
        label_expressao_inicial = ctk.CTkLabel(
            frame_expressao_inicial,
            text="",
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=800
        )
        label_expressao_inicial.pack(pady=(0, Spacing.SM), padx=Spacing.SM)
        
        # 2. SEÇÃO: Análise Atual
        frame_analise = ctk.CTkFrame(
            main_container,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        frame_analise.pack(fill="x", pady=(0, Spacing.MD))
        
        titulo_analise = ctk.CTkLabel(
            frame_analise,
            text="Análise",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_analise.pack(pady=(Spacing.SM, Spacing.XS))
        
        # Label para mostrar a subexpressão sendo analisada
        global label_analise_atual
        label_analise_atual = ctk.CTkLabel(
            frame_analise,
            text="Aguardando início da análise...",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=800
        )
        label_analise_atual.pack(pady=(0, Spacing.SM), padx=Spacing.SM)
        
        # 3. SEÇÃO: Passos da Simplificação (área scrollável)
        frame_passos = ctk.CTkFrame(
            main_container,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        frame_passos.pack(fill="both", expand=True, pady=(0, Spacing.MD))
        
        titulo_passos = ctk.CTkLabel(
            frame_passos,
            text="Passos da Simplificação",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_passos.pack(pady=(Spacing.SM, Spacing.XS))
        
        # Área scrollável para os passos
        global scroll_passos
        scroll_passos = ctk.CTkScrollableFrame(
            frame_passos,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=330
        )
        scroll_passos.pack(fill="both", expand=True, padx=Spacing.SM, pady=(0, Spacing.SM))
        
        # 4. SEÇÃO: Seleção de Leis
        frame_leis = ctk.CTkFrame(
            main_container,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        frame_leis.pack(fill="x", pady=(0, Spacing.MD))
        
        titulo_leis = ctk.CTkLabel(
            frame_leis,
            text="Selecione uma Lei para Aplicar:",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        titulo_leis.pack(pady=Spacing.SM)
        
        # Grid de botões de leis
        frame_grid_leis = ctk.CTkFrame(frame_leis, fg_color="transparent")
        frame_grid_leis.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
        
        botoes_info = [
            {"texto": "Inversa", "desc": "A * ~A = 0", "idx": 0},
            {"texto": "Nula", "desc": "A * 0 = 0", "idx": 1},
            {"texto": "Identidade", "desc": "A * 1 = A", "idx": 2},
            {"texto": "Idempotente", "desc": "A * A = A", "idx": 3},
            {"texto": "Absorção", "desc": "A * (A+B) = A", "idx": 4},
            {"texto": "De Morgan", "desc": "~(A*B) = ~A+~B", "idx": 5},
            {"texto": "Distributiva", "desc": "(A+B)*(A+C)", "idx": 6},
            {"texto": "Associativa", "desc": "(A*B)*C", "idx": 7},
            {"texto": "Comutativa", "desc": "B*A = A*B", "idx": 8},
        ]
        
        botoes_leis = []
        for i, info in enumerate(botoes_info):
            row = i // 3
            col = i % 3
            
            btn = Button.botao_padrao(f"{info['texto']}\n({info['desc']})", frame_grid_leis)
            btn.configure(command=lambda idx=info["idx"]: on_lei_selecionada(idx))
            btn.grid(row=row, column=col, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
            frame_grid_leis.grid_columnconfigure(col, weight=1)
            botoes_leis.append(btn)
        
        # 5. SEÇÃO: Controles
        frame_controles_interativo = ctk.CTkFrame(main_container, fg_color="transparent")
        frame_controles_interativo.pack(fill="x", pady=Spacing.MD)
        
        # Botões de controle
        botao_desfazer = Button.botao_padrao("↩ Desfazer", frame_controles_interativo)
        botao_desfazer.configure(command=on_desfazer_selecionado, state="disabled")
        botao_desfazer.pack(side="left", padx=Spacing.SM)
        
        botao_pular = Button.botao_padrao("↪ Pular", frame_controles_interativo)
        botao_pular.configure(command=on_pular_selecionado)
        botao_pular.pack(side="left", padx=Spacing.SM)
        
        # Botão voltar
        botao_voltar_interativo = Button.botao_voltar("Voltar", frame_controles_interativo)
        botao_voltar_interativo.configure(
            command=lambda: [finalizar_sessao_expressao(str(expressao_global), resolvida=False), limpar_frame_interativo(), go_back_to(frame_abas)]
        )
        botao_voltar_interativo.pack(side="right", padx=Spacing.SM)
    #------------------------------------------------------------------------
    # BOTÃO DE RELATÓRIO HTML COMENTADO CONFORME SOLICITADO
    # botao_relatorio = Button.botao_padrao("📊 Gerar Relatório HTML", frame_inicio)
    # botao_relatorio.configure(command=generate_html_log)
    # botao_relatorio.pack(pady=Spacing.MD)

    botao_tabela_verdade = Button.botao_padrao("🔢Tabela Verdade", scroll_frame2)
    botao_tabela_verdade.configure(command=lambda: exibir_tabela_verdade(entrada.get().strip().upper()))
    botao_tabela_verdade.pack(pady=Spacing.MD)

    botao_pedir_ajuda_ia = Button.botao_padrao("❓Pedir ajuda à IA", scroll_frame2)
    botao_pedir_ajuda_ia.configure(command=lambda: abrir_duvida_expressao(entrada.get().strip().upper()))
    botao_pedir_ajuda_ia.pack(pady=Spacing.MD)

    # Botões das partes de abas que voltam pro frame de inserir a expressão para ver o circuito
    botao_voltar_principal_2 = Button.botao_voltar("Voltar", scroll_frame2)
    botao_voltar_principal_2.configure(command=lambda: go_back_to(principal))
    botao_voltar_principal_2.pack(pady=Spacing.XXL)

    botao_voltar_principal = Button.botao_voltar("Voltar", scroll_frame1)
    botao_voltar_principal.configure(command=lambda: go_back_to(principal))
    botao_voltar_principal.pack(pady=Spacing.XXL)

    #---------------- FRAME DE INFORMAÇÕES ----------------

    frame_info = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_info.grid(row=0, column=0, sticky="nsew")

    textbox_info = ctk.CTkTextbox(
        frame_info, 
        font=get_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.TEXT_PRIMARY, 
        fg_color=Colors.PRIMARY_BG
    )
    textbox_info.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)
    textbox_info.configure(fg_color=Colors.SURFACE_MEDIUM, text_color=Colors.TEXT_PRIMARY)
    info_text = informacoes
    textbox_info.insert("0.0", info_text)
    textbox_info.configure(state="disable")

    botao_voltar_info = Button.botao_voltar("Voltar", frame_info)
    botao_voltar_info.configure(command=lambda: go_back_to(frame_inicio))
    botao_voltar_info.pack(pady=Spacing.LG)

    #---------------- FRAME DE EQUIVALÊNCIA ----------------

    titulo = ctk.CTkLabel(
        frame_equivalencia, 
        text="Digite as expressões que deseja comparar:", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.TEXT_PRIMARY, 
        fg_color=None
    )
    titulo.place(relx=0.5, y=130, anchor="center")

    entrada2 = ctk.CTkEntry(
        frame_equivalencia, 
        width=350, 
        placeholder_text="Primeira expressão", 
        font=get_font(Typography.SIZE_BODY_SMALL),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
    )
    entrada2.place(relx=0.5, y=200, anchor="center")

    entrada3 = ctk.CTkEntry(
        frame_equivalencia, 
        width=350, 
        placeholder_text="Segunda expressão", 
        font=get_font(Typography.SIZE_BODY_SMALL),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
    )
    entrada3.place(relx=0.5, y=250, anchor="center")

    botao_comparar = Button.botao_padrao("✅Comparar", frame_equivalencia, style="success")
    botao_comparar.configure(command=comparar)
    botao_comparar.place(relx=0.5, y=320, anchor="center")

    botao_voltar_equivalencia = Button.botao_voltar("Voltar", frame_equivalencia)
    botao_voltar_equivalencia.configure(command=lambda: go_back_to(frame_inicio))
    botao_voltar_equivalencia.place(relx=0.5, y=400, anchor="center")

    equivalente = ctk.CTkLabel(
        frame_equivalencia, 
        text="✅ São equivalentes!", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.SUCCESS, 
        fg_color=None
    )
    nao_equivalente = ctk.CTkLabel(
        frame_equivalencia, 
        text="❌ Não são equivalentes", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.ERROR, 
        fg_color=None
    )
    
    def on_closing(): #Função chamada quando a aplicação é fechada.
        user_logger.end_session()
        
        if user_logger.should_prompt_data_sharing():
            try:
                dialog = DetailedDataSharingDialog(user_logger)
                result = dialog.show_dialog()
                
                if result == True:
                    print("Usuário aceitou enviar os dados detalhados. Preparando para envio...")
                    
                    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd9QNzL1_1MpD0cy_PUA4b59Kpy998015HIsfIT60VC6nOHZA/formResponse"
                    
                    ENTRY_MAPPING = {
                        'app_version': 'entry.695751574',
                        'platform': 'entry.2115172041',
                        'submission_date': 'entry.1953189469',
                        'summary_json': 'entry.415910834'
                    }
                    
                    submitter = ImprovedGoogleFormsSubmitter(FORM_URL, ENTRY_MAPPING)
                    data_to_send = DetailedUserLogger.create_formatted_shareable_data(user_logger)  # NOVA FUNÇÃO
                    
                    success = submitter.submit_data(data_to_send)
                    
                    if success:
                        user_logger._save_settings() 
                    else:
                        print("O envio falhou. Os dados não foram enviados.")
                        
                elif result == "never":
                    user_logger.logging_enabled = False
                    user_logger._save_settings()
                    
            except Exception as e:
                print(f"Erro no dialog de compartilhamento: {e}")
        
        janela.destroy()
        
    janela.protocol("WM_DELETE_WINDOW", on_closing) 
    show_frame(frame_inicio)
    janela.mainloop()