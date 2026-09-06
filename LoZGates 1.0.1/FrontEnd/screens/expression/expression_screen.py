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
from FrontEnd.styles.design_tokens import Colors, Typography, Dimensions, Spacing, TabConfig, get_font, get_title_font
from FrontEnd.utils.responsive import (
    calculate_window_layout,
    calculate_wraplength,
    responsive_columns,
)
from FrontEnd.app.navigation import (
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

from FrontEnd.components.buttons import Button
from FrontEnd.screens.problems.problems_screen import setup_problems_interface
from FrontEnd.components.step_view import StepView, StepParser

from FrontEnd.dialogs.interactive_help import show_interactive_help

from BackEnd.circuito_logico.circuit_mode_selector import CircuitModeManager
from FrontEnd.screens.circuit.circuit_mode_interface import CircuitModeSelector
from FrontEnd.dialogs.ai_chat_popup import AIChatPopup
from FrontEnd.dialogs.custom_popups import popup_erro, popup_duvida
from FrontEnd.screens.problems.problems_screen import IntegratedProblemsInterface

from FrontEnd.services.logging_service import DetailedUserLogger
from FrontEnd.services.google_forms_service import ImprovedGoogleFormsSubmitter
from FrontEnd.dialogs.data_sharing_dialog import DetailedDataSharingDialog

logger = logging.getLogger(__name__)
user_logger = None # Will be initialized in setup_legacy_screens

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

def setup_legacy_screens(janela):

    global user_logger
    user_logger = janela.user_logger

    navigation = janela.navigation

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
        try:
            atual_tab = abas.get()
            if navigation is not None:
                navigation.sync_tab(atual_tab)
            user_logger.log_tab_changed("tab_navigation", atual_tab)
            if atual_tab == INTERACTIVE_CIRCUIT_TAB:
                frame_circuito_interativo.initialize_if_needed()
        except Exception:
            logger.exception("Erro ao detectar mudanca de aba")

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

    def go_back_to(frame):
        try:
            global botao_ver_circuito
            
            if botao_ver_circuito:
                botao_ver_circuito.destroy()
                botao_ver_circuito = None

            #Lógica melhorada para parar o circuito
            #Se voltando para frame_abas, NÃO para o circuito
            if frame == frame_abas:
                logger.debug("Voltando para abas com circuito ativo")
            else:
                #Para qualquer outro destino, para o circuito
                frame_circuito_interativo.cleanup()

            #Limpa as entradas apenas se não for para certas telas
            if frame not in [frame_abas, frame_resolucao_direta, frame_interativo]:
                entrada.delete(0, tk.END) 
                does_it_have_interaction = False
                try:
                    esconder_botoes_simplificar()  #Reset dos botões ao limpar entrada
                except (NameError, AttributeError):
                    logger.debug("Botoes de simplificacao indisponiveis durante limpeza")

            entrada.configure(placeholder_text="Digite aqui")
            
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
                janela.after(200, on_tab_change)
            
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
    
    from FrontEnd.screens.home.home_screen import HomeScreen
    frame_inicio = HomeScreen(janela, navigation, janela)

    principal = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    principal.grid(row=0, column=0, sticky="nsew")

    from FrontEnd.screens.equivalence.equivalence_controller import EquivalenceController
    from FrontEnd.screens.equivalence.equivalence_screen import EquivalenceScreen
    
    equivalence_controller = EquivalenceController(user_logger)
    frame_equivalencia = EquivalenceScreen(janela, navigation, equivalence_controller)

    frame_abas = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_abas.grid(row=0, column=0, sticky="nsew")

    frame_resolucao_direta = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_resolucao_direta.grid(row=0, column=0, sticky="nsew")

    scroll_conteudo = ctk.CTkScrollableFrame(frame_resolucao_direta, fg_color=Colors.PRIMARY_BG)
    scroll_conteudo.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)

    from FrontEnd.screens.resolver.resolver_state import ResolverState
    from FrontEnd.screens.resolver.resolver_controller import ResolverController
    from FrontEnd.screens.resolver.resolver_screen import ResolverScreen
    
    resolver_state = ResolverState()
    resolver_controller = ResolverController(resolver_state, user_logger=user_logger)
    def get_resolver_expr():
        return expressao_global
        
    frame_interativo = ResolverScreen(janela, navigation, resolver_controller, get_resolver_expr)
    resolver_controller.set_view(frame_interativo)

    frame_problemas_reais = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_problemas_reais.grid(row=0, column=0, sticky="nsew")

    scroll_problemas_reais = ctk.CTkScrollableFrame(frame_problemas_reais, fg_color=Colors.PRIMARY_BG)
    scroll_problemas_reais.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)
    scroll_problemas_reais._scrollbar.grid_remove()

    frame_explicacao_problemas_reais = ctk.CTkFrame(janela, fg_color=Colors.PRIMARY_BG)
    frame_explicacao_problemas_reais.grid(row=0, column=0, sticky="nsew")



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
    from FrontEnd.screens.circuit.circuit_controller import CircuitController
    from FrontEnd.screens.circuit.circuit_screen import CircuitScreen
    
    circuit_controller = CircuitController(user_logger)
    def get_circuit_expr():
        return expressao_global if expressao_global else entrada.get().strip().upper().replace(" ", "")

    frame_circuito_interativo = CircuitScreen(aba_circuito_interativo, navigation, circuit_controller, get_circuit_expr)
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
        if not expressao_global:
            popup_erro("Por favor, primeiro insira e converta uma expressão.")
            go_back_to(frame_abas)
            show_frame(principal) 
            return
        frame_interativo.initialize_if_needed()

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

    navigation.tab_frame = frame_abas
    navigation.tabview = abas
    navigation.frame_names = {
        frame_inicio: "home",
        principal: "expression_entry",
        frame_equivalencia: "equivalence",
        frame_problemas_reais: "problems",
        frame_resolucao_direta: "simplification_result",
        frame_interativo: "interactive_simplifier",
        frame_info: "information",
    }
    # Registra as telas para o novo sistema de navegação (show_screen)
    navigation.register_screen("home", frame_inicio)
    navigation.register_screen("principal", principal)
    navigation.register_screen("equivalencia", frame_equivalencia)
    navigation.register_screen("problemas_reais", frame_problemas_reais)
    navigation.register_screen("resolucao", frame_resolucao_direta)
    navigation.register_screen("interativo", frame_interativo)
    navigation.register_screen("informacao", frame_info)
    
    janela._lozgates_navigation = navigation

