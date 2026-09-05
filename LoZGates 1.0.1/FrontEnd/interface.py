import customtkinter as ctk
from customtkinter import CTkFont
import threading
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageOps
import time
import webbrowser
import urllib.parse
from contextlib import redirect_stdout
import copy
import logging
import queue
import re

from config import (
    CIRCUIT_IMAGE_PATH,
    INPUT_CACHE_PATH,
    apply_window_icon,
    duvida_circuitos,
    informacoes,
)
from FrontEnd.design_tokens import Colors, Typography, Dimensions, Spacing, TabConfig, get_font, get_title_font
from FrontEnd.responsive import (
    calculate_window_layout,
    calculate_wraplength,
    responsive_columns,
)
from FrontEnd.navigation import (
    CIRCUIT_TAB,
    EXPRESSION_TAB,
    INTERACTIVE_CIRCUIT_TAB,
    NavigationController,
)

from BackEnd.tabela import gerar_tabela_verdade, verificar_conclusao
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.equivalencia import tabela
from BackEnd.normalizer import normalize_for_comparison, expressions_are_structurally_equivalent
from BackEnd.identificar_lei import principal_simplificar
import BackEnd.simplificador_interativo as simpli
import BackEnd.principal as circuito_integrado

from FrontEnd.buttons import Button
from FrontEnd.problems_interface import setup_problems_interface
from FrontEnd.step_view import StepView, StepParser

from FrontEnd.interactive_help import show_interactive_help

from BackEnd.circuito_logico.circuit_mode_selector import CircuitModeManager
from FrontEnd.circuit_mode_interface import CircuitModeSelector
from FrontEnd.ai_chat_popup import AIChatPopup
from FrontEnd.problems_interface import IntegratedProblemsInterface

from FrontEnd.logging_system import DetailedUserLogger, DetailedDataSharingDialog, ImprovedGoogleFormsSubmitter

logger = logging.getLogger(__name__)
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

#Variáveis para a nova interface interativa
label_expressao_inicial = None
label_analise_atual = None
scroll_passos = None
contador_passos = 0
sessao_simplificacao_concluida = False
frame_expressao_inicial = None
frame_analise = None
frame_passos = None
frame_controles_interativo = None
simplification_guard = None
motivo_parada_interativo = None

def inicializar_interface():

    ctk.set_appearance_mode("dark")  #Modo escuro
    ctk.set_default_color_theme("blue")  #Tema azul
    janela = ctk.CTk()
    janela.title("LoZ Gates")
    janela.configure(bg=Colors.PRIMARY_BG)
    window_layout = calculate_window_layout(
        janela.winfo_screenwidth(), janela.winfo_screenheight()
    )
    janela.geometry(window_layout.geometry)
    janela.minsize(window_layout.minimum_width, window_layout.minimum_height)
    try:
        janela.state('zoomed')
    except (tk.TclError, AttributeError):
        logger.debug("Maximizacao automatica indisponivel nesta plataforma")
    janela.grid_rowconfigure(0, weight=1)
    janela.grid_columnconfigure(0, weight=1)
    apply_window_icon(janela)
        
    janela.resizable(True, True)

    navigation = None
    circuit_generation_in_progress = False
    simplification_in_progress = False
    circuit_image_source = None
    circuit_resize_job = None

    def show_frame(frame, view_name=None):
        if navigation is None:
            frame.tkraise()
            return
        navigation.show_frame(frame, view_name=view_name)

    def show_tab(view_name):
        if navigation is None:
            raise RuntimeError("Navegação por abas ainda não foi inicializada.")
        navigation.show_tab(view_name)

    def ver_circuito_pygame(expressao, on_complete=None):
        result_queue = queue.Queue(maxsize=1)

        def rodar_pygame():
            try:
                circuito_integrado.plotar_circuito_logico(expressao, 0, 1200, 800)
                logger.info("Circuito estatico gerado com sucesso")
                result_queue.put((True, None))
            except Exception as error:
                logger.exception("Erro ao gerar circuito estatico")
                result_queue.put((False, str(error)))
        
        #Remove imagem antiga se existir
        caminho_imagem = CIRCUIT_IMAGE_PATH
        if caminho_imagem.exists():
            try:
                caminho_imagem.unlink()
            except OSError:
                logger.warning("Nao foi possivel remover a imagem anterior", exc_info=True)

        #Executa o Pygame em uma thread
        thread = threading.Thread(target=rodar_pygame, daemon=True)
        thread.start()

        #Consulta o worker com after(), sem bloquear ou atualizar Tk fora da UI.
        started_at = time.monotonic()

        def poll_generation():
            try:
                succeeded, error_message = result_queue.get_nowait()
            except queue.Empty:
                if time.monotonic() - started_at < 10:
                    janela.after(100, poll_generation)
                    return
                succeeded, error_message = False, "A geração excedeu o limite de 10 segundos."

            if succeeded and caminho_imagem.exists():
                atualizar_imagem_circuito()
            else:
                popup_erro(
                    f"Erro ao gerar circuito: {error_message}"
                    if error_message
                    else "Erro: a imagem do circuito não foi criada."
                )
            if on_complete:
                on_complete(succeeded and caminho_imagem.exists())

        janela.after(100, poll_generation)

    def popup_erro(mensagem):
        popup = tk.Toplevel(janela)  #<- tk.Toplevel ao invés de ctk.CTkToplevel
        popup.attributes('-topmost', True)
        popup.after(10, lambda: popup.attributes('-topmost', False))
        popup.title("Erro")
        apply_window_icon(popup)

        popup_layout = calculate_window_layout(
            popup.winfo_screenwidth(),
            popup.winfo_screenheight(),
            preferred=(460, 180),
            minimum=(320, 160),
            margin=24,
        )
        popup.geometry(popup_layout.geometry)

        #Cor de fundo
        popup.configure(bg="#1a1a1a")  #como é Tk puro, use 'bg' e não 'fg_color'

        #Conteúdo
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

    def popup_duvida(mensagem):
        popup = tk.Toplevel(janela)  #<- tk.Toplevel ao invés de ctk.CTkToplevel
        popup.attributes('-topmost', True)
        popup.after(10, lambda: popup.attributes('-topmost', False))
        popup.title("Ajuda")
        apply_window_icon(popup)
        popup.configure(bg="#1a1a1a")
        #Cria o textbox e insere a mensagem de ajuda/informação
        textbox = tk.Text(popup, wrap="word", font=("Trebuchet MS", 12), fg="white", bg="#1a1a1a", borderwidth=0)
        textbox.pack(padx=10, pady=10, fill="both", expand=True)
        #Escreve a mensagem recebida + informações extras
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

    def trocar_para_abas(target_view="circuit"):
        nonlocal circuit_generation_in_progress
        if circuit_generation_in_progress:
            logger.info("Circuit generation ignored because one is already running")
            return
        try:
            caminho_entrada = INPUT_CACHE_PATH
            start_time = time.time()
            expressao = entrada.get().strip().upper().replace(" ", "")
            
            user_logger.log_expression_entered(expressao, bool(expressao))
            
            if not expressao:
                user_logger.log_error("validation_error", "Empty expression")
                popup_erro("A expressão não pode estar vazia.")
                return
                
            label_circuito_expressao.configure(text=f"Expressão Lógica Proposicional: {expressao}")
            
            caminho_entrada.parent.mkdir(parents=True, exist_ok=True)
            caminho_entrada.write_text(expressao, encoding="utf-8")

            saida = converter_para_algebra_booleana(expressao)
            global expressao_global
            expressao_global = saida

            circuit_generation_in_progress = True
            if botao_ver_circuito and botao_ver_circuito.winfo_exists():
                botao_ver_circuito.configure(state="disabled", text="Processando...")

            def finish_generation(_succeeded):
                nonlocal circuit_generation_in_progress
                circuit_generation_in_progress = False
                try:
                    if botao_ver_circuito and botao_ver_circuito.winfo_exists():
                        botao_ver_circuito.configure(
                            state="normal", text="🔌 Ver Circuito"
                        )
                except tk.TclError:
                    pass

            #Gerar circuito pygame
            ver_circuito_pygame(saida, on_complete=finish_generation)
            
            #Uma ação explícita escolhe sua aba; depois a navegação volta a ser livre.
            show_tab(target_view)
            duration = time.time() - start_time
            user_logger.log_feature_used("circuit_generation", duration)
            
        except Exception as e:
            circuit_generation_in_progress = False
            try:
                if botao_ver_circuito and botao_ver_circuito.winfo_exists():
                    botao_ver_circuito.configure(
                        state="normal", text="🔌 Ver Circuito"
                    )
            except tk.TclError:
                pass
            logger.exception("Erro ao processar expressao")
            popup_erro(f"Erro ao processar expressão: {e}")
            
    #Detecta mudança de aba e recria o circuito se necessário
    def on_tab_change():
        global does_it_have_interaction
        try:
            atual_tab = abas.get()
            if navigation is not None:
                navigation.sync_tab(atual_tab)
            user_logger.log_tab_changed("tab_navigation", atual_tab)
            if atual_tab == INTERACTIVE_CIRCUIT_TAB:
                #Garante que a expressão existe antes de criar qualquer coisa
                if not expressao_global:
                    logger.warning("Expressao global ausente ao abrir circuito")
                    return
                    
                #Atualiza display da expressão se a instância existir
                if (circuito_interativo_instance and 
                    hasattr(circuito_interativo_instance, 'update_expression_display')):
                    circuito_interativo_instance.update_expression_display()
                    
                #Só cria se realmente necessário
                if_necessary_create_a_circuit()
        except Exception:
            logger.exception("Erro ao detectar mudanca de aba")
           
    def if_necessary_create_a_circuit():
        global circuito_interativo_instance, does_it_have_interaction
        
        #Verifica se o frame está vazio ou se a instância não existe
        frame_vazio = len(frame_circuito_interativo.winfo_children()) == 0
        instancia_inexistente = circuito_interativo_instance is None
        
        #Só cria se não existir
        if frame_vazio or instancia_inexistente:
            logger.debug("Criando interface de selecao de modo")
            #Usa a expressão atual da entrada, não uma vazia
            expressao_atual = entrada.get().strip().upper().replace(" ", "") if entrada.get().strip() else expressao_global
            if expressao_atual:
                create_interactive_circuit(expressao_atual)
            else:
                logger.warning("Nenhuma expressao disponivel para criar circuito")
        else:
            logger.debug("Interface de circuito existente sera preservada")

    def create_interactive_circuit(expressao):
        global circuito_interativo_instance, does_it_have_interaction
        
        #LOG INÍCIO DO CIRCUITO INTERATIVO
        user_logger.log_circuit_interaction_start()
        
        def get_global_expression():
            return expressao_global if expressao_global else expressao
        
        if circuito_interativo_instance:
            try:
                circuito_interativo_instance.cleanup()
            except Exception:
                logger.exception("Erro ao limpar instancia anterior do circuito")
        
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
            logger.info("Interface de circuito com modos criada")
            
        except Exception as error:
            logger.exception("Erro ao criar interface de circuito")
            does_it_have_interaction = False
            
            error_label = ctk.CTkLabel(
                frame_circuito_interativo,
                text=f"Erro ao criar circuito interativo: {error}",
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
        
        #LOG DA EXPRESSÃO INSERIDA
        user_logger.log_expression_entered(expressao_texto.upper().replace(" ", ""), True)
        
        try:
            esconder_botoes_simplificar()
        except (NameError, AttributeError):
            logger.debug("Botoes de simplificacao ainda nao foram inicializados")
        
        botao_ver_circuito = Button.botao_padrao("🔌 Ver Circuito", principal_card)
        botao_ver_circuito.configure(command=trocar_para_abas)
        botao_ver_circuito.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

    def exibir_tabela_verdade(expressao):
        try:
            janela_tabela = ctk.CTkToplevel(janela)
            janela_tabela.title("Tabela Verdade")
            table_layout = calculate_window_layout(
                janela_tabela.winfo_screenwidth(),
                janela_tabela.winfo_screenheight(),
                preferred=(1000, 700),
                minimum=(640, 480),
            )
            janela_tabela.geometry(table_layout.geometry)
            janela_tabela.minsize(
                table_layout.minimum_width, table_layout.minimum_height
            )
            janela_tabela.lift()
            janela_tabela.attributes('-topmost', True)
            janela_tabela.after(10, lambda: janela_tabela.attributes('-topmost', False))
            janela_tabela.configure(fg_color=Colors.PRIMARY_BG)

            #Gera a tabela verdade usando a função do backend
            dados_tabela = gerar_tabela_verdade(expressao)
            
            #Extrai os dados do dicionário retornado
            colunas = dados_tabela["colunas"]
            tabela = dados_tabela["tabela"]
            resultados_finais = dados_tabela["resultados_finais"]

            #Container principal
            main_container = ctk.CTkFrame(
                janela_tabela,
                fg_color=Colors.PRIMARY_BG,
                corner_radius=0
            )
            main_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

            #Título da janela
            titulo_tabela = ctk.CTkLabel(
                main_container,
                text=f"Tabela Verdade: {expressao}",
                font=get_title_font(Typography.SIZE_TITLE_MEDIUM),
                text_color=Colors.TEXT_ACCENT
            )
            titulo_tabela.pack(pady=(Spacing.SM, Spacing.LG))

            #Frame da tabela com design padronizado
            frame_tabela_container = ctk.CTkFrame(
                main_container,
                fg_color=Colors.SURFACE_LIGHT,
                corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
            )
            frame_tabela_container.pack(fill="both", expand=True, pady=(0, Spacing.MD))

            #Área scrollável para a tabela
            frame_tabela = ctk.CTkScrollableFrame(
                frame_tabela_container,
                fg_color=Colors.SURFACE_DARK,
                corner_radius=Dimensions.CORNER_RADIUS_SMALL
            )
            frame_tabela.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)

            #Calcular larguras otimizadas para cada coluna
            larguras = []
            for i, col in enumerate(colunas):
                max_len = len(str(col))
                for linha in tabela:
                    if i < len(linha):
                        max_len = max(max_len, len(str(linha[i])))
                larguras.append(max(max_len + 1, 3))  #Mínimo 3, +1 para espaçamento

            #Cabeçalho da tabela
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

            #Linhas da tabela
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

            #Frame para conclusão
            conclusao_frame = ctk.CTkFrame(
                main_container,
                fg_color=Colors.SURFACE_MEDIUM,
                corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
            )
            conclusao_frame.pack(fill="x", pady=(0, Spacing.MD))

            #Verifica a conclusão da expressão
            conclusao = verificar_conclusao(resultados_finais)
            
            #Define cor baseada no tipo de conclusão
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

            #Botão para fechar
            botao_fechar = Button.botao_padrao("Fechar", main_container)
            botao_fechar.configure(command=janela_tabela.destroy)
            botao_fechar.pack(pady=Spacing.SM)
            
        except Exception as e:
            popup_erro(f"Erro ao gerar tabela verdade: {e}")
            logger.exception("Erro ao gerar tabela verdade")

    def comparar():
            try:
                expressao2 = entrada2.get().strip().upper()
                expressao3 = entrada3.get().strip().upper()
                
                if not expressao2 or not expressao3:
                    popup_erro("As expressões não podem estar vazias.")
                    return
                
                logger.debug("Comparando expressoes %s e %s", expressao2, expressao3)
                
                # VERIFICAÇÃO: Equivalência lógica semântica via Tabela Verdade Universal
                from BackEnd.equivalencia import check_universal_equivalence
                resultado = check_universal_equivalence(expressao2, expressao3, debug=False)
                
                if resultado:
                    logger.info("Expressoes logicamente equivalentes")
                else:
                    logger.info("Expressoes nao equivalentes")

                #LOG DETALHADO COM EXPRESSÕES REAIS
                user_logger.log_equivalence_check_with_expressions(
                    expressao2, expressao3, resultado
                )
                
                if resultado:
                    equivalente.pack(padx=Spacing.XL, pady=Spacing.XS)
                    nao_equivalente.pack_forget()
                else:
                    nao_equivalente.pack(padx=Spacing.XL, pady=Spacing.XS)
                    equivalente.pack_forget()
                    
            except Exception as e:
                user_logger.log_error("equivalence_check_error", str(e), "comparar_function")
                popup_erro(f"Erro ao comparar expressões: {e}")
              
    def go_back_to(frame):
        try:
            global botao_ver_circuito, circuito_interativo_instance, does_it_have_interaction
            
            if botao_ver_circuito:
                botao_ver_circuito.destroy()
                botao_ver_circuito = None

            #Lógica melhorada para parar o circuito
            if circuito_interativo_instance:
                #Se voltando para frame_abas, NÃO para o circuito
                if frame == frame_abas:
                    logger.debug("Voltando para abas com circuito ativo")
                else:
                    #Para qualquer outro destino, para o circuito
                    try:
                        circuito_interativo_instance.cleanup()
                        circuito_interativo_instance = None
                        does_it_have_interaction = False
                        logger.info("Circuito interativo limpo")
                    except Exception:
                        logger.exception("Erro ao limpar circuito interativo")

            #Limpa as entradas apenas se não for para certas telas
            if frame not in [frame_abas, frame_resolucao_direta, frame_interativo]:
                entrada.delete(0, tk.END) 
                does_it_have_interaction = False
                try:
                    esconder_botoes_simplificar()  #Reset dos botões ao limpar entrada
                except (NameError, AttributeError):
                    logger.debug("Botoes de simplificacao indisponiveis durante limpeza")

            entrada2.delete(0, tk.END)  
            entrada3.delete(0, tk.END) 
            
            entrada.configure(placeholder_text="Digite aqui")
            entrada2.configure(placeholder_text="Digite aqui")
            entrada3.configure(placeholder_text="Digite aqui")
            
            equivalente.place_forget()
            nao_equivalente.place_forget()
            
            #Esconde os resultados da aba de expressão ao voltar apenas se NÃO for para frame_abas
            if frame != frame_abas:
                label_convertida.pack_forget()
                log_simplificacao_textbox.pack_forget()
                step_view.pack_forget()
                try:
                    esconder_botoes_simplificar()  #Esconde botões de simplificação
                except (NameError, AttributeError):
                    logger.debug("Botoes de simplificacao indisponiveis durante retorno")

            show_frame(frame)
            janela.focus_set()

            if frame == principal:
                entrada.focus_set()
            
            #Se voltando para frame_abas, garante que a interface esteja disponível
            if frame == frame_abas and expressao_global:
                janela.after(200, if_necessary_create_a_circuit)
            
        except Exception as e:
            popup_erro(f"Erro ao voltar: {e}")
            logger.exception("Erro ao retornar para a tela anterior")
       
    def atualizar_imagem_circuito():
        nonlocal circuit_image_source
        try:
            caminho_img = CIRCUIT_IMAGE_PATH
            if caminho_img.exists():
                with Image.open(caminho_img) as imagem_pil:
                    circuit_image_source = imagem_pil.convert("RGB")

                render_circuit_image()
            else:
                imagem_circuito.configure(text="Imagem do circuito não encontrada", image="")
        except Exception as e:
            logger.exception("Erro ao atualizar imagem do circuito")
            imagem_circuito.configure(text=f"Erro ao carregar imagem: {e}", image="")

    def render_circuit_image():
        if circuit_image_source is None:
            return
        try:
            available_width = max(320, scroll_frame1.winfo_width() - 2 * Spacing.LG)
            scale = min(1.0, available_width / circuit_image_source.width)
            display_size = (
                max(1, int(circuit_image_source.width * scale)),
                max(1, int(circuit_image_source.height * scale)),
            )
            resized = circuit_image_source.resize(display_size, Image.Resampling.LANCZOS)

            borda = min(10, max(2, display_size[0] // 80))
            imagem_com_borda = ImageOps.expand(resized, border=borda, fill="white")

            imagem_tk = ctk.CTkImage(
                light_image=imagem_com_borda,
                dark_image=imagem_com_borda,
                size=imagem_com_borda.size,
            )
            imagem_circuito.configure(image=imagem_tk, text="")
            imagem_circuito.image = imagem_tk
        except (tk.TclError, OSError):
            logger.exception("Erro ao redimensionar imagem do circuito")

    def schedule_circuit_image_resize(_event=None):
        nonlocal circuit_resize_job
        if circuit_resize_job is not None:
            janela.after_cancel(circuit_resize_job)
        circuit_resize_job = janela.after(120, render_circuit_image)
    
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

    home_card = ctk.CTkFrame(
        frame_inicio,
        fg_color=Colors.SURFACE_DARK,
        border_width=Dimensions.BORDER_WIDTH_STANDARD,
        border_color=Colors.BORDER_DEFAULT,
        corner_radius=Dimensions.CORNER_RADIUS_LARGE,
    )
    home_card.place(relx=0.5, rely=0.5, anchor="center")

    fonte_momentz = CTkFont(family="Momentz", size=Typography.SIZE_TITLE_LARGE + 2)
    label_inicio = ctk.CTkLabel(
        home_card,
        text="<LoZ Gates>",
        font=fonte_momentz,
        text_color=Colors.TEXT_PRIMARY,
        fg_color="transparent"
    )
    label_inicio.pack(padx=Spacing.XXL, pady=(Spacing.XXL, Spacing.XS))

    home_subtitle = ctk.CTkLabel(
        home_card,
        text="Lógica proposicional e circuitos digitais, passo a passo.",
        font=get_font(Typography.SIZE_BODY_SMALL),
        text_color=Colors.TEXT_SECONDARY,
        wraplength=420,
    )
    home_subtitle.pack(padx=Spacing.XL, pady=(0, Spacing.XL))

    botao_circuitos = Button.botao_padrao("💡 Circuitos e Expressões", home_card)
    botao_circuitos.configure(command=lambda: show_frame(principal))
    botao_circuitos.pack(fill="x", padx=Spacing.XL, pady=Spacing.SM)

    botao_equivalencia = Button.botao_padrao("🔄 Equivalência Lógica", home_card)
    botao_equivalencia.configure(command=lambda: show_frame(frame_equivalencia))
    botao_equivalencia.pack(fill="x", padx=Spacing.XL, pady=Spacing.SM)
    
    botao_info = Button.botao_padrao("❔ Ajuda e manual", home_card)
    botao_info.configure(command=lambda: show_interactive_help(janela))
    botao_info.pack(fill="x", padx=Spacing.XL, pady=(Spacing.SM, Spacing.XXL))

    #---------------- FRAME DOS CIRCUITOS E DAS EXPRESSÕES ----------------

    principal_card = ctk.CTkFrame(
        principal,
        fg_color=Colors.SURFACE_DARK,
        border_width=Dimensions.BORDER_WIDTH_STANDARD,
        border_color=Colors.BORDER_DEFAULT,
        corner_radius=Dimensions.CORNER_RADIUS_LARGE,
    )
    principal_card.place(relx=0.5, rely=0.5, anchor="center")

    label_tarefas = ctk.CTkLabel(
        principal_card,
        text="Digite a expressão em Lógica Proposicional:", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.TEXT_PRIMARY, 
        fg_color=None
    )
    label_tarefas.pack(padx=Spacing.XL, pady=(Spacing.XXL, Spacing.SM))

    syntax_hint = ctk.CTkLabel(
        principal_card,
        text="Use & para E, | para OU, ! para NÃO e parênteses para prioridade.",
        font=get_font(Typography.SIZE_CAPTION),
        text_color=Colors.TEXT_SECONDARY,
        wraplength=460,
    )
    syntax_hint.pack(padx=Spacing.XL, pady=(0, Spacing.MD))

    entrada = ctk.CTkEntry(
        principal_card,
        width=350, 
        placeholder_text="Ex.: (A & B) | !C",
        font=get_font(Typography.SIZE_BODY_SMALL),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
    )
    entrada.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))
    entrada.bind("<Return>", lambda event: confirmar_expressao())

    botao_confirmar_expressao = Button.botao_padrao("✅ Confirmar", principal_card, style="success")
    botao_confirmar_expressao.configure(command=confirmar_expressao, hover_color="#16723D")
    botao_confirmar_expressao.pack(fill="x", padx=Spacing.XL, pady=Spacing.SM)
    
    botao_problemas_reais = Button.botao_padrao("🔬 Banco de problemas", principal_card)
    botao_problemas_reais.configure(command=lambda: show_frame(frame_problemas_reais))
    botao_problemas_reais.pack(fill="x", padx=Spacing.XL, pady=Spacing.SM)

    botao_go_back_to_inicio = Button.botao_voltar("Voltar", principal_card)
    botao_go_back_to_inicio.configure(command=lambda: go_back_to(frame_inicio))
    botao_go_back_to_inicio.pack(fill="x", padx=Spacing.XL, pady=(Spacing.SM, Spacing.XXL))
    
    #---------------- FRAME DOS PROBLEMAS REAIS ----------------
    def handle_problem_answer(expression, destination):
        #Preenche o campo de entrada principal
        entrada.delete(0, tk.END)
        entrada.insert(0, expression)
        
        #Log da ação
        user_logger.log_feature_used("problem_answer_analysis", 0)
        
        #Navega baseado no destino
        if destination == "circuit":
            #Confirma expressão e vai para circuito
            confirmar_expressao()
            janela.after(500, trocar_para_abas)
        
        elif destination == "simplifier":
            #Confirma expressão e vai para simplificador
            confirmar_expressao()
            janela.after(
                500,
                lambda: [
                    trocar_para_abas("expression"),
                    janela.after(200, executar_conversao),
                ],
            )
        
        elif destination == "table":
            #Abre diretamente a tabela verdade
            exibir_tabela_verdade(expression)

    def setup_problems_interface_with_callback(scroll_container, voltar_callback, principal_frame, button_class):
        interface = IntegratedProblemsInterface(scroll_container)
        
        #Configura o callback ANTES de criar a interface
        interface.main_entry_callback = handle_problem_answer
        
        #Cria a tela principal
        interface.create_problems_main_screen(scroll_container, voltar_callback, principal_frame)

    #Use esta função no lugar da original
    setup_problems_interface_with_callback(scroll_problemas_reais, go_back_to, principal, Button)
        
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
    abas.pack(expand=True, fill="both", padx=Spacing.SM, pady=Spacing.SM)

    #---------------------- ABA DO CIRCUITO ----------------------

    aba_circuito = abas.add(CIRCUIT_TAB)
    scroll_frame1 = ctk.CTkScrollableFrame(aba_circuito, fg_color=Colors.PRIMARY_BG)
    scroll_frame1.pack(expand=True, fill="both")

    circuit_header = ctk.CTkFrame(scroll_frame1, fg_color="transparent")
    circuit_header.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)

    label_circuito_expressao = ctk.CTkLabel(
        circuit_header,
        font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD), 
        text_color=Colors.TEXT_ACCENT, 
        text=""
    )
    label_circuito_expressao.pack(side="left", expand=True, padx=Spacing.SM)
    circuit_header.bind(
        "<Configure>",
        lambda event: label_circuito_expressao.configure(
            wraplength=max(220, event.width - 100)
        ),
        add="+",
    )

    botao_duvida1 = Button.botao_duvida(circuit_header, size="small")
    botao_duvida1.pack(side="right", padx=Spacing.SM)
    botao_duvida1.configure(command=lambda: popup_duvida(duvida_circuitos))

    imagem_circuito = ctk.CTkLabel(scroll_frame1, text="")
    imagem_circuito.pack(fill="x", padx=Spacing.MD, pady=Spacing.MD)
    scroll_frame1.bind("<Configure>", schedule_circuit_image_resize, add="+")

    def salvar_imagem():
        try:
            caminho_img = CIRCUIT_IMAGE_PATH
            if caminho_img.exists():
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
    aba_circuito_interativo = abas.add(INTERACTIVE_CIRCUIT_TAB)
    frame_circuito_interativo = tk.Frame(aba_circuito_interativo, bg=Colors.PRIMARY_BG)
    frame_circuito_interativo.pack(expand=True, fill="both", padx=Spacing.SM, pady=Spacing.SM)
    
 #------------------------------------------------ ABA DE EXPRESSÃO  ----------------------------------------------
 
    aba_expressao = abas.add(EXPRESSION_TAB)
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
            except Exception:
                logger.exception("Erro ao encaminhar saida do simplificador para a interface")

    #Componente StepView para visualização passo a passo
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
            #Esconde elementos antigos
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
        nonlocal simplification_in_progress
        if simplification_in_progress:
            logger.info("Duplicate simplification request ignored")
            return
        try:
            #1. Pega a expressão mais recente direto da caixa de entrada principal
            entrada_txt = entrada.get().strip().upper()
            if not entrada_txt:
                popup_erro("A expressão na tela principal está vazia.")
                return

            simplification_in_progress = True

            #2. Converte para o formato de álgebra booleana
            expressao_para_simplificar = converter_para_algebra_booleana(entrada_txt)
            
            #Esconde componentes antigos e mostra StepView
            if label_solucao.winfo_ismapped():
                label_solucao.pack_forget()
                log_simplificacao_textbox.pack_forget()
                frame_borda.pack_forget()

            label_solucao.pack(pady=Spacing.LG)
            step_view.pack(fill="both", expand=True, pady=Spacing.MD)
            step_view.configure(height=800)
            botao_go_back_to_aba2.pack(pady=Spacing.MD)

            #Inicializa StepView
            step_view.reset(expressao_para_simplificar)
            step_view.set_processing(True)
            botao_go_back_to_aba2.configure(state="disabled")
            
            #Parser para converter log em passos
            parser = StepParser(step_view)
            step_events = queue.Queue()
            
            class StepLogger:
                def __init__(self, event_queue):
                    self.event_queue = event_queue
                    self.buffer = ""
                    
                def write(self, text):
                    self.buffer += text
                    while "\n" in self.buffer:
                        line, self.buffer = self.buffer.split("\n", 1)
                        if line.strip():
                            self.event_queue.put(("line", line))
                    return len(text)
                            
                def flush(self):
                    if self.buffer.strip():
                        self.event_queue.put(("line", self.buffer))
                    self.buffer = ""

            step_logger = StepLogger(step_events)

            def simplificar_thread():
                error_message = None
                result = None
                try:
                    with redirect_stdout(step_logger):
                        #3. Usa a expressão recém-capturada e convertida
                        result = principal_simplificar(expressao_para_simplificar)
                    if result is None:
                        error_message = "Não foi possível simplificar a expressão informada."
                except Exception as error:
                    logger.exception("simplification exception in UI worker")
                    error_message = str(error)
                finally:
                    step_logger.flush()
                    step_events.put(("done", result is not None, error_message))

            def poll_simplification():
                nonlocal simplification_in_progress
                completed = None
                while True:
                    try:
                        event = step_events.get_nowait()
                    except queue.Empty:
                        break
                    if event[0] == "line":
                        parser.parse_log_line(event[1])
                    else:
                        completed = event

                if completed is None:
                    janela.after(40, poll_simplification)
                    return

                _, succeeded, error_message = completed
                parser.finalize_parsing(expressao_para_simplificar, succeeded)
                step_view.set_processing(False)
                botao_go_back_to_aba2.configure(state="normal")
                simplification_in_progress = False
                if error_message:
                    popup_erro(f"Erro ao simplificar expressão: {error_message}")

            threading.Thread(
                target=simplificar_thread,
                name="lozgates-simplifier",
                daemon=True,
            ).start()
            janela.after(40, poll_simplification)
        except Exception as error:
            simplification_in_progress = False
            try:
                botao_go_back_to_aba2.configure(state="normal")
                step_view.set_processing(False)
            except (NameError, tk.TclError):
                pass
            logger.exception("simplification exception while preparing UI")
            popup_erro(f"Erro ao simplificar expressão: {error}")
            
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
            esconder_botoes_simplificar()  #Esconde botões antigos primeiro
        except (NameError, AttributeError):
            logger.debug("Botoes antigos ainda nao foram inicializados")
        mostrar_expressao_convertida()
        mostrar_botoes_simplificar()   #Mostra novos botões
    
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

    
    #Variáveis globais para componentes interativos (serão criadas dinamicamente)
    escolher_caminho = None
    area_expressao = None
    
#---------------------- PARTE DA SIMPLFICAÇÃO ---------------------------------
    #Variável para controlar visibilidade dos botões
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
        except (NameError, AttributeError, tk.TclError):
            logger.debug("Botao interativo indisponivel ao ocultar")
            botoes_visiveis = False

    def executar_simplificacao_resultado():
        try:
            esconder_botoes_simplificar()
        except (NameError, AttributeError):
            logger.debug("Botoes de simplificacao indisponiveis")
        show_frame(frame_resolucao_direta)
        expressao_simplificada()

    def executar_simplificacao_interativa():
        esconder_botoes_simplificar()
        go_to_interactive()

    botao_solucao = Button.botao_padrao("🔍Simplificar - Resultado", scroll_frame2)
    botao_solucao.configure(command=executar_simplificacao_resultado)

    def voltar_para_abas():
        #Mostra os botões novamente quando voltar para as abas
        if expressao_booleana_atual:  #Se há uma expressão convertida
            mostrar_botoes_simplificar()
        go_back_to(frame_abas)
    
    botao_go_back_to_aba2 = Button.botao_voltar("Voltar", scroll_conteudo)
    botao_go_back_to_aba2.configure(command=voltar_para_abas)
    botao_go_back_to_aba2.pack(side="bottom", pady=Spacing.MD)
    
    def finalizar_sessao_expressao(expression, resolvida=False):
        #"""Finaliza a sessão e registra os dados finais"""
        #global tempo_inicio_expressao, tentativas_atuais
    
        #if tempo_inicio_expressao is None:
        #    return
        
        #tempo_total = time.time() - tempo_inicio_expressao
    
        #tempo_inicio_expressao = None
        #tentativas_atuais = 0
        pass


#------------------ MODO INTERATIVO LÓGICA E FUNÇÕES MODIFICADAS ----------------------
    def salvar_estado_atual():
        global historico_de_estados, arvore_interativa, historico_interativo, nos_ignorados
        
        arvore_copiada, ignorados_copiados = copy.deepcopy((arvore_interativa, nos_ignorados))
        
        estado = {
            'arvore': arvore_copiada,
            'historico': list(historico_interativo),
            'ignorados': ignorados_copiados,
        }
        historico_de_estados.append(estado)

    def on_desfazer_selecionado():
        global historico_de_estados, arvore_interativa, historico_interativo, nos_ignorados, passo_atual_info, botao_desfazer
        global contador_passos, sessao_simplificacao_concluida
        global simplification_guard, motivo_parada_interativo

        if not historico_de_estados:
            logger.debug("Nenhum estado de simplificacao para desfazer")
            return

        #LOG DO UNDO
        user_logger.log_simplification_undo()

        estado_anterior = historico_de_estados.pop()
        arvore_interativa = estado_anterior['arvore']
        historico_interativo = estado_anterior['historico']
        nos_ignorados = estado_anterior.get('ignorados', set())
        passo_atual_info = None
        sessao_simplificacao_concluida = False
        motivo_parada_interativo = None
        simplification_guard = simpli.SimplificationGuard(arvore_interativa)
        simpli.reiniciar_busca()
        
        reconstruir_area_passos()

        if not historico_de_estados:
            botao_desfazer.configure(state="disabled")
        iniciar_rodada_interativa()
  
    def inicializar_area_passos():
        global scroll_passos, contador_passos
        contador_passos = 0
        
        #Limpa área anterior
        for widget in scroll_passos.winfo_children():
            widget.destroy()
        
        #Adiciona passo inicial
        adicionar_passo_inicial(str(arvore_interativa))
    
    def adicionar_passo_inicial(expressao_inicial):
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
        global contador_passos
        contador_passos += 1
        
        passo_frame = ctk.CTkFrame(
            scroll_passos,
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        passo_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        #Título com número do passo e lei
        titulo_passo = ctk.CTkLabel(
            passo_frame,
            text=f"Passo {contador_passos} — {lei_nome}",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_passo.pack(pady=(Spacing.SM, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        #Subexpressão analisada
        if subexpressao:
            sub_label = ctk.CTkLabel(
                passo_frame,
                text=f"Subexpressão: {subexpressao}",
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_SECONDARY
            )
            sub_label.pack(pady=(0, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        #Transformação
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
        
        #Resultado
        resultado_frame = ctk.CTkFrame(passo_frame, fg_color="transparent")
        resultado_frame.pack(fill="x", pady=(Spacing.XS, Spacing.SM), padx=Spacing.SM)
        
        status_label = ctk.CTkLabel(
            resultado_frame,
            text=f"✔ {resultado}",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.SUCCESS
        )
        status_label.pack(side="left")
        
        #Auto-scroll para o final
        scroll_passos.after(100, lambda: scroll_passos._parent_canvas.yview_moveto(1.0))
    
    def adicionar_passo_pular(subexpressao):
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
        
        #Auto-scroll para o final
        scroll_passos.after(100, lambda: scroll_passos._parent_canvas.yview_moveto(1.0))
    
    def atualizar_area_passos():
        #Esta função pode ser expandida se necessário para atualizações dinâmicas
        pass
    
    def reconstruir_area_passos():
        global scroll_passos, contador_passos
        contador_passos = 0
        
        #Limpa área atual
        for widget in scroll_passos.winfo_children():
            widget.destroy()
        
        #Adiciona passo inicial
        if historico_interativo and len(historico_interativo) > 0:
            #Extrai expressão inicial do primeiro item do histórico
            primeiro_item = historico_interativo[0]
            if "Expressão Inicial:" in primeiro_item:
                expressao_inicial = primeiro_item.replace("Expressão Inicial:", "").strip()
                adicionar_passo_inicial(expressao_inicial)
            
            #Reconstrói passos baseado no histórico
            passo_num = 0
            i = 1
            while i < len(historico_interativo):
                linha = historico_interativo[i]
                if "✓ Lei" in linha and "aplicada com sucesso" in linha:
                    passo_num += 1
                    #Extrai nome da lei
                    lei_match = re.search(r"Lei '(.+?)' aplicada", linha)
                    lei_nome = lei_match.group(1) if lei_match else "Lei desconhecida"
                    
                    #Próxima linha deve ter a nova expressão
                    if i + 1 < len(historico_interativo):
                        proxima_linha = historico_interativo[i + 1]
                        if "Nova Expressão:" in proxima_linha:
                            nova_expr = proxima_linha.replace("Nova Expressão:", "").strip()
                            adicionar_passo_sucesso(lei_nome, "", "(anterior)", "(simplificada)", nova_expr)
                            i += 1  #Pula a próxima linha já processada
                elif "↷ Sub-expressão" in linha and "ignorada" in linha:
                    #Extrai subexpressão ignorada
                    ignore_match = re.search(r"'(.+?)' ignorada", linha)
                    subexpr = ignore_match.group(1) if ignore_match else "desconhecida"
                    adicionar_passo_pular(subexpr)
                i += 1

    def on_lei_selecionada(indice_lei):
        global arvore_interativa, passo_atual_info, historico_interativo
        global nos_ignorados, contador_passos, historico_de_estados, botao_desfazer
        global sessao_simplificacao_concluida, motivo_parada_interativo
        
        if not passo_atual_info:
            return
            
        try:
            lei_usada = simpli.LEIS_LOGICAS[indice_lei]['nome']
            subexpressao_antes = str(passo_atual_info['no_atual'])
            
            # Validação Pedagógica: se não for aplicável, mostra popup e interrompe sem logar falha profunda
            if not simpli.LEIS_LOGICAS[indice_lei]['verifica'](passo_atual_info['no_atual']):
                popup_erro("Esta lei não pode ser aplicada à subexpressão atual.")
                return

            salvar_estado_atual()
            botao_desfazer.configure(state="normal")
            
            nova_arvore, sucesso = simpli.aplicar_lei_e_substituir(
                arvore_interativa, passo_atual_info, indice_lei
            )

            user_logger.log_law_applied(lei_usada, sucesso, contador_passos + 1)

            if sucesso:
                decision = simplification_guard.consider(nova_arvore)
                if not decision.accepted:
                    estado_anterior = historico_de_estados.pop()
                    arvore_interativa = estado_anterior['arvore']
                    historico_interativo = estado_anterior['historico']
                    passo_atual_info = None
                    motivo_parada_interativo = decision.reason
                    simpli.reiniciar_busca()
                    if decision.reason == "maximum_steps":
                        logger.warning(
                            "maximum steps reached in interactive simplification: limit=%s",
                            simplification_guard.max_steps,
                        )
                    elif decision.reason == "repeated_state":
                        logger.warning(
                            "repeated state detected in interactive simplification: %s",
                            nova_arvore,
                        )
                    else:
                        logger.warning(
                            "interactive transformation stopped without progress: %s",
                            nova_arvore,
                        )
                    atualizar_ui_interativa()
                    return

                arvore_interativa = nova_arvore
                motivo_parada_interativo = None
                sessao_simplificacao_concluida = False

                historico_interativo.append(f"✓ Lei '{lei_usada}' aplicada com sucesso.")
                historico_interativo.append(f"   Nova Expressão: {str(arvore_interativa)}")
                nos_ignorados = set()

                logger.info(
                    "rule applied in interactive simplification: rule=%s step=%s expression=%s",
                    lei_usada,
                    contador_passos + 1,
                    arvore_interativa,
                )
                adicionar_passo_sucesso(
                    lei_usada, subexpressao_antes, subexpressao_antes,
                    "(simplificada)", str(arvore_interativa)
                )
                iniciar_rodada_interativa()
            else:
                full_expression_state = str(arvore_interativa)
                reason_for_failure = f"Lei não aplicável à subexpressão '{subexpressao_antes}' no contexto de '{full_expression_state}'"
                user_logger.log_simplification_step_failed(
                    lei_usada,
                    contador_passos + 1,
                    reason_for_failure,
                    full_expression_state,
                )

                historico_de_estados.pop()
                if not historico_de_estados:
                    botao_desfazer.configure(state="disabled")
                popup_erro("Esta transformação não reduz a expressão atual.")
                iniciar_rodada_interativa()
        except Exception:
            logger.exception("simplification exception in interactive rule handler")
            popup_erro("Não foi possível aplicar a lei selecionada.")
            iniciar_rodada_interativa()

    def on_pular_selecionado():
        global nos_ignorados, passo_atual_info, historico_interativo, botao_desfazer, contador_passos, sessao_simplificacao_concluida
        if passo_atual_info and passo_atual_info['no_atual']:
            salvar_estado_atual()
            botao_desfazer.configure(state="normal")
            subexpressao_ignorada = str(passo_atual_info['no_atual'])
            
            #LOG DO PULAR
            user_logger.log_simplification_skip(contador_passos)
            
            nos_ignorados.add(passo_atual_info['no_atual'])
            sessao_simplificacao_concluida = False
            historico_interativo.append(f"↷ Sub-expressão '{subexpressao_ignorada}' ignorada.")
            adicionar_passo_pular(subexpressao_ignorada)
            iniciar_rodada_interativa()

    def atualizar_ui_interativa():
        global botoes_leis, label_expressao_inicial, label_analise_atual, scroll_passos
        global sessao_simplificacao_concluida
        
        #Atualiza expressão inicial
        if label_expressao_inicial and arvore_interativa:
            label_expressao_inicial.configure(text=str(arvore_interativa))
        
        #Atualiza análise atual
        if passo_atual_info:
            sub_expr = str(passo_atual_info['no_atual'])
            orientacao = "Selecione uma lei para tentar transformar a subexpressão."
            label_analise_atual.configure(
                text=f"🔍 Analisando subexpressão: '{sub_expr}'\n📚 {orientacao}",
                text_color=Colors.TEXT_PRIMARY
            )
            
            #Mantém todos os botões habilitados (Abordagem Pedagógica)
            if botoes_leis:
                for botao in botoes_leis:
                    botao.configure(state="normal")
            if botao_pular:
                botao_pular.configure(state="normal")
        else:
            stop_messages = {
                "repeated_state": "Estado equivalente já visitado. A simplificação foi encerrada.",
                "maximum_steps": "Limite de segurança atingido. A última expressão válida foi mantida.",
                "no_progress": "A próxima transformação não reduziria a expressão.",
                "no_further_simplification": "Não foram encontradas outras simplificações.",
            }
            stop_message = stop_messages.get(
                motivo_parada_interativo,
                "Não foram encontradas outras simplificações.",
            )
            label_analise_atual.configure(
                text=f"✅ Simplificação encerrada\n{stop_message}",
                text_color=Colors.SUCCESS
            )
            
            if historico_interativo and not sessao_simplificacao_concluida:
                sessao_simplificacao_concluida = True
                total_steps = contador_passos
                
                #Extrai nomes das leis do histórico
                laws_used = []
                for line in historico_interativo:
                    if "✓ Lei" in line and "aplicada com sucesso" in line:
                        #Extrai o nome da lei da linha do histórico
                        import re
                        lei_match = re.search(r"Lei '(.+?)' aplicada", line)
                        if lei_match:
                            laws_used.append(lei_match.group(1))
                
                #CHAMA A FUNÇÃO DE LOG DE CONCLUSÃO
                user_logger.log_simplification_completed(total_steps, laws_used)
                logger.info(
                    "Simplificacao concluida: %s passos, %s leis aplicadas",
                    total_steps,
                    len(laws_used),
                )
            
            #Desabilita botões
            if botoes_leis:
                for botao in botoes_leis:
                    botao.configure(state="disabled")
            if botao_pular:
                botao_pular.configure(state="disabled")
        
        #Atualiza área de passos
        atualizar_area_passos()

    def iniciar_rodada_interativa():
        global passo_atual_info, motivo_parada_interativo
        passo_atual_info = simpli.encontrar_proximo_passo(arvore_interativa, nos_a_ignorar=nos_ignorados)
        if passo_atual_info is None and motivo_parada_interativo is None:
            motivo_parada_interativo = "no_further_simplification"
            logger.info(
                "no further simplification in interactive mode: expression=%s",
                arvore_interativa,
            )
        atualizar_ui_interativa()
        
    def parte_interativa():
        global arvore_interativa, historico_interativo, nos_ignorados, passo_atual_info, expressao_global, botoes_leis, historico_de_estados, simplification_start_time, sessao_simplificacao_concluida
        global simplification_guard, motivo_parada_interativo
        
        if not expressao_global:
            popup_erro("Por favor, primeiro insira e converta uma expressão.")
            go_back_to(frame_abas)
            show_frame(principal) 
            return
            
        try:
            simplification_start_time = time.time()
            
            #LOG INÍCIO DA SESSÃO INTERATIVA
            user_logger.log_interactive_simplification_start(expressao_global)
            logger.info("simplification started in interactive mode: %s", expressao_global)
            
            arvore_interativa = simpli.construir_arvore(expressao_global)
        except Exception as e:
            popup_erro(f"Erro ao construir a expressão: {e}")
            go_back_to(scroll_frame2)
            return

        historico_interativo = [f"Expressão Inicial: {str(arvore_interativa)}"]
        nos_ignorados = set()
        passo_atual_info = None
        historico_de_estados = []
        sessao_simplificacao_concluida = False
        motivo_parada_interativo = None
        simplification_guard = simpli.SimplificationGuard(arvore_interativa)
        simpli.reiniciar_busca()
        
        criar_interface_interativa_padronizada()
        inicializar_area_passos()
        iniciar_rodada_interativa()
        duration = time.time() - simplification_start_time
        user_logger.log_feature_used("interactive_mode", duration)
        
    def limpar_frame_interativo():
        for widget in frame_interativo.winfo_children():
            widget.destroy()
    
    def abrir_chat_ia():
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
        
        #Container principal com scroll
        main_container = ctk.CTkScrollableFrame(frame_interativo, fg_color=Colors.PRIMARY_BG)
        main_container.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)
        
        #Configurar grid para expansão
        main_container.grid_rowconfigure(2, weight=1)  #frame_passos deve expandir
        main_container.grid_columnconfigure(0, weight=1)
        
        #1. SEÇÃO: Expressão Inicial
        frame_expressao_inicial = ctk.CTkFrame(
            main_container,
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        frame_expressao_inicial.pack(fill="x", pady=(0, Spacing.MD))
        
        #Container para título e botão IA
        header_frame = ctk.CTkFrame(frame_expressao_inicial, fg_color="transparent")
        header_frame.pack(fill="x", pady=(Spacing.SM, Spacing.XS), padx=Spacing.SM)
        
        titulo_inicial = ctk.CTkLabel(
            header_frame,
            text="Expressão Inicial",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_inicial.pack(side="left")
        
        #Botão Sugestão de IA
        botao_ia = Button.botao_padrao("🤖 Sugestão de IA", header_frame)
        botao_ia.configure(
            command=abrir_chat_ia,
            width=140,
            height=32,
            font=get_font(Typography.SIZE_BODY_SMALL)
        )
        botao_ia.pack(side="right")
        
        #Label para mostrar a expressão inicial (será atualizada dinamicamente)
        global label_expressao_inicial
        label_expressao_inicial = ctk.CTkLabel(
            frame_expressao_inicial,
            text="",
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=800
        )
        label_expressao_inicial.pack(pady=(0, Spacing.SM), padx=Spacing.SM)
        
        #2. SEÇÃO: Análise Atual
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
        
        #Label para mostrar a subexpressão sendo analisada
        global label_analise_atual
        label_analise_atual = ctk.CTkLabel(
            frame_analise,
            text="Aguardando início da análise...",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=800
        )
        label_analise_atual.pack(pady=(0, Spacing.SM), padx=Spacing.SM)
        
        #3. SEÇÃO: Passos da Simplificação (área scrollável)
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
        
        #Área scrollável para os passos
        global scroll_passos
        scroll_passos = ctk.CTkScrollableFrame(
            frame_passos,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=240
        )
        scroll_passos.pack(fill="both", expand=True, padx=Spacing.SM, pady=(0, Spacing.SM))
        
        #4. SEÇÃO: Seleção de Leis
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
        
        #Grid de botões de leis
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
        for info in botoes_info:
            btn = Button.botao_padrao(f"{info['texto']}\n({info['desc']})", frame_grid_leis)
            btn.configure(command=lambda idx=info["idx"]: on_lei_selecionada(idx))
            botoes_leis.append(btn)
        
        #5. SEÇÃO: Controles
        frame_controles_interativo = ctk.CTkFrame(main_container, fg_color="transparent")
        frame_controles_interativo.pack(fill="x", pady=Spacing.MD)
        
        #Botões de controle
        botao_desfazer = Button.botao_padrao("↩ Desfazer", frame_controles_interativo)
        botao_desfazer.configure(
            command=on_desfazer_selecionado, state="disabled", width=140
        )
        
        botao_pular = Button.botao_padrao("↪ Pular", frame_controles_interativo)
        botao_pular.configure(command=on_pular_selecionado, width=140)
        
        #Botão voltar
        botao_voltar_interativo = Button.botao_voltar("Voltar", frame_controles_interativo)
        botao_voltar_interativo.configure(
            command=lambda: [finalizar_sessao_expressao(str(expressao_global), resolvida=False), limpar_frame_interativo(), go_back_to(frame_abas)],
            width=140,
        )

        control_buttons = [botao_desfazer, botao_pular, botao_voltar_interativo]

        def reflow_interactive_layout(event=None):
            container_width = (
                event.width if event is not None else main_container.winfo_width()
            )
            wraplength = calculate_wraplength(container_width)
            label_expressao_inicial.configure(wraplength=wraplength)
            label_analise_atual.configure(wraplength=wraplength)

            law_columns = responsive_columns(container_width, item_minimum=250, maximum=3)
            for column in range(3):
                frame_grid_leis.grid_columnconfigure(
                    column, weight=1 if column < law_columns else 0
                )
            for index, button in enumerate(botoes_leis):
                button.grid(
                    row=index // law_columns,
                    column=index % law_columns,
                    padx=Spacing.XS,
                    pady=Spacing.XS,
                    sticky="ew",
                )

            control_columns = 3 if container_width >= 560 else 1
            for column in range(3):
                frame_controles_interativo.grid_columnconfigure(
                    column, weight=1 if column < control_columns else 0
                )
            for index, button in enumerate(control_buttons):
                button.grid(
                    row=index // control_columns,
                    column=index % control_columns,
                    padx=Spacing.XS,
                    pady=Spacing.XS,
                    sticky="ew",
                )

        main_container.bind("<Configure>", reflow_interactive_layout, add="+")
        main_container.after(0, reflow_interactive_layout)
    #------------------------------------------------------------------------
    #BOTÃO DE RELATÓRIO HTML COMENTADO CONFORME SOLICITADO
    #botao_relatorio = Button.botao_padrao("📊 Gerar Relatório HTML", frame_inicio)
    #botao_relatorio.configure(command=generate_html_log)
    #botao_relatorio.pack(pady=Spacing.MD)

    botao_tabela_verdade = Button.botao_padrao("🔢Tabela Verdade", scroll_frame2)
    botao_tabela_verdade.configure(command=lambda: exibir_tabela_verdade(entrada.get().strip().upper()))
    botao_tabela_verdade.pack(pady=Spacing.MD)

    botao_pedir_ajuda_ia = Button.botao_padrao("❓Pedir ajuda à IA", scroll_frame2)
    botao_pedir_ajuda_ia.configure(command=lambda: abrir_duvida_expressao(entrada.get().strip().upper()))
    botao_pedir_ajuda_ia.pack(pady=Spacing.MD)

    #Botões das partes de abas que voltam pro frame de inserir a expressão para ver o circuito
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

    equivalencia_card = ctk.CTkFrame(
        frame_equivalencia,
        fg_color=Colors.SURFACE_DARK,
        border_width=Dimensions.BORDER_WIDTH_STANDARD,
        border_color=Colors.BORDER_DEFAULT,
        corner_radius=Dimensions.CORNER_RADIUS_LARGE,
    )
    equivalencia_card.place(relx=0.5, rely=0.5, anchor="center")

    titulo = ctk.CTkLabel(
        equivalencia_card,
        text="Digite as expressões que deseja comparar:", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.TEXT_PRIMARY, 
        fg_color=None
    )
    titulo.pack(padx=Spacing.XL, pady=(Spacing.XXL, Spacing.SM))

    equivalencia_hint = ctk.CTkLabel(
        equivalencia_card,
        text="A comparação considera equivalência lógica e estrutural.",
        font=get_font(Typography.SIZE_CAPTION),
        text_color=Colors.TEXT_SECONDARY,
        wraplength=460,
    )
    equivalencia_hint.pack(padx=Spacing.XL, pady=(0, Spacing.MD))

    entrada2 = ctk.CTkEntry(
        equivalencia_card,
        width=350, 
        placeholder_text="Primeira expressão", 
        font=get_font(Typography.SIZE_BODY_SMALL),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
    )
    entrada2.pack(fill="x", padx=Spacing.XL, pady=Spacing.XS)

    entrada3 = ctk.CTkEntry(
        equivalencia_card,
        width=350, 
        placeholder_text="Segunda expressão", 
        font=get_font(Typography.SIZE_BODY_SMALL),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
    )
    entrada3.pack(fill="x", padx=Spacing.XL, pady=Spacing.XS)

    botao_comparar = Button.botao_padrao("✅ Comparar", equivalencia_card, style="success")
    botao_comparar.configure(command=comparar)
    botao_comparar.pack(fill="x", padx=Spacing.XL, pady=(Spacing.MD, Spacing.SM))

    resultado_equivalencia_frame = ctk.CTkFrame(
        equivalencia_card, fg_color="transparent", height=40
    )
    resultado_equivalencia_frame.pack(fill="x", padx=Spacing.XL)
    resultado_equivalencia_frame.pack_propagate(False)

    botao_voltar_equivalencia = Button.botao_voltar("Voltar", equivalencia_card)
    botao_voltar_equivalencia.configure(command=lambda: go_back_to(frame_inicio))
    botao_voltar_equivalencia.pack(fill="x", padx=Spacing.XL, pady=(Spacing.SM, Spacing.XXL))

    equivalente = ctk.CTkLabel(
        resultado_equivalencia_frame,
        text="✅ São equivalentes!", 
        font=get_title_font(Typography.SIZE_TITLE_SMALL), 
        text_color=Colors.SUCCESS, 
        fg_color=None
    )
    nao_equivalente = ctk.CTkLabel(
        resultado_equivalencia_frame,
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
                    logger.info("Usuario autorizou o envio dos dados detalhados")
                    
                    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd9QNzL1_1MpD0cy_PUA4b59Kpy998015HIsfIT60VC6nOHZA/formResponse"
                    
                    ENTRY_MAPPING = {
                        'app_version': 'entry.695751574',
                        'platform': 'entry.2115172041',
                        'submission_date': 'entry.1953189469',
                        'summary_json': 'entry.415910834'
                    }
                    
                    submitter = ImprovedGoogleFormsSubmitter(FORM_URL, ENTRY_MAPPING)
                    data_to_send = DetailedUserLogger.create_formatted_shareable_data(user_logger)  #NOVA FUNÇÃO
                    
                    success = submitter.submit_data(data_to_send)
                    
                    if success:
                        user_logger._save_settings() 
                    else:
                        logger.warning("O envio de dados de atividade falhou")
                        
                elif result == "never":
                    user_logger.logging_enabled = False
                    user_logger._save_settings()
                    
            except Exception:
                logger.exception("Erro no dialogo de compartilhamento")
        
        janela.destroy()
        
    janela.protocol("WM_DELETE_WINDOW", on_closing)
    navigation = NavigationController(
        frame_abas,
        abas,
        frame_names={
            frame_inicio: "home",
            principal: "expression_entry",
            frame_equivalencia: "equivalence",
            frame_problemas_reais: "problems",
            frame_resolucao_direta: "simplification_result",
            frame_interativo: "interactive_simplifier",
            frame_info: "information",
        },
    )
    janela._lozgates_navigation = navigation
    show_frame(frame_inicio, view_name="home")
    janela.mainloop()
