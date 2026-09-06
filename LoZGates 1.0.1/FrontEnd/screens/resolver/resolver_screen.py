import customtkinter as ctk
import logging

from FrontEnd.styles.design_tokens import Colors, Typography, Dimensions, Spacing, get_font, get_title_font
from FrontEnd.components.buttons import Button
from FrontEnd.utils.responsive import calculate_wraplength, responsive_columns
from FrontEnd.dialogs.custom_popups import popup_erro
from FrontEnd.dialogs.ai_chat_popup import AIChatPopup

logger = logging.getLogger(__name__)

class ResolverScreen(ctk.CTkFrame):
    def __init__(self, parent, navigation_controller, controller, get_global_expression_cb, on_close_cb=None):
        super().__init__(parent, fg_color=Colors.PRIMARY_BG)
        
        self.navigation = navigation_controller
        self.controller = controller
        self.get_global_expression_cb = get_global_expression_cb
        self.on_close_cb = on_close_cb
        
        self.grid(row=0, column=0, sticky="nsew")
        self.is_initialized = False

        self.botoes_leis = []
        self.botao_desfazer = None
        self.botao_pular = None
        self.label_expressao_inicial = None
        self.label_analise_atual = None
        self.scroll_passos = None
        
        self._build_ui()

    def _build_ui(self):
        # Container principal com scroll
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=Colors.PRIMARY_BG)
        self.main_container.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)
        
        # Configurar grid para expansão
        self.main_container.grid_rowconfigure(2, weight=1)  # frame_passos deve expandir
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # 1. SEÇÃO: Expressão Inicial
        self.frame_expressao_inicial = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        self.frame_expressao_inicial.pack(fill="x", pady=(0, Spacing.MD))
        
        header_frame = ctk.CTkFrame(self.frame_expressao_inicial, fg_color="transparent")
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
            command=self.abrir_chat_ia,
            width=140,
            height=32,
            font=get_font(Typography.SIZE_BODY_SMALL)
        )
        botao_ia.pack(side="right")
        
        self.label_expressao_inicial = ctk.CTkLabel(
            self.frame_expressao_inicial,
            text="",
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=800
        )
        self.label_expressao_inicial.pack(pady=(0, Spacing.SM), padx=Spacing.SM)
        
        # 2. SEÇÃO: Análise Atual
        self.frame_analise = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        self.frame_analise.pack(fill="x", pady=(0, Spacing.MD))
        
        titulo_analise = ctk.CTkLabel(
            self.frame_analise,
            text="Análise",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_analise.pack(pady=(Spacing.SM, Spacing.XS))
        
        self.label_analise_atual = ctk.CTkLabel(
            self.frame_analise,
            text="Aguardando início da análise...",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=800
        )
        self.label_analise_atual.pack(pady=(0, Spacing.SM), padx=Spacing.SM)
        
        # 3. SEÇÃO: Passos da Simplificação (área scrollável)
        self.frame_passos = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        self.frame_passos.pack(fill="both", expand=True, pady=(0, Spacing.MD))
        
        titulo_passos = ctk.CTkLabel(
            self.frame_passos,
            text="Passos da Simplificação",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        titulo_passos.pack(pady=(Spacing.SM, Spacing.XS))
        
        self.scroll_passos = ctk.CTkScrollableFrame(
            self.frame_passos,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=240
        )
        self.scroll_passos.pack(fill="both", expand=True, padx=Spacing.SM, pady=(0, Spacing.SM))
        
        # 4. SEÇÃO: Seleção de Leis
        self.frame_leis = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        self.frame_leis.pack(fill="x", pady=(0, Spacing.MD))
        
        titulo_leis = ctk.CTkLabel(
            self.frame_leis,
            text="Selecione uma Lei para Aplicar:",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        titulo_leis.pack(pady=Spacing.SM)
        
        self.frame_grid_leis = ctk.CTkFrame(self.frame_leis, fg_color="transparent")
        self.frame_grid_leis.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
        
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
        
        self.botoes_leis = []
        for info in botoes_info:
            btn = Button.botao_padrao(f"{info['texto']}\n({info['desc']})", self.frame_grid_leis)
            btn.configure(command=lambda idx=info["idx"]: self.controller.on_lei_selecionada(idx))
            self.botoes_leis.append(btn)
        
        # 5. SEÇÃO: Controles
        self.frame_controles_interativo = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_controles_interativo.pack(fill="x", pady=Spacing.MD)
        
        self.botao_desfazer = Button.botao_padrao("↩ Desfazer", self.frame_controles_interativo)
        self.botao_desfazer.configure(
            command=self.controller.on_desfazer_selecionado, state="disabled", width=140
        )
        
        self.botao_pular = Button.botao_padrao("↪ Pular", self.frame_controles_interativo)
        self.botao_pular.configure(command=self.controller.on_pular_selecionado, width=140)
        
        self.botao_voltar_interativo = Button.botao_voltar("Voltar", self.frame_controles_interativo)
        self.botao_voltar_interativo.configure(
            command=self.voltar_tela,
            width=140,
        )

        self.control_buttons = [self.botao_desfazer, self.botao_pular, self.botao_voltar_interativo]

        self.main_container.bind("<Configure>", self.reflow_interactive_layout, add="+")
        self.main_container.after(0, self.reflow_interactive_layout)

    def initialize_if_needed(self):
        expressao = self.get_global_expression_cb()
        if not expressao:
            logger.warning("Nenhuma expressao disponivel para iniciar resolucao iterativa")
            return

        self.limpar_area_passos()
        self.controller.iniciar_simplificacao(expressao)
        self.is_initialized = True

    def abrir_chat_ia(self):
        try:
            expressao_atual = str(self.controller.state.arvore_interativa) if self.controller.state.arvore_interativa else self.controller.state.expressao_global
            contexto_passo = ""
            
            if self.controller.state.passo_atual_info:
                subexpr = str(self.controller.state.passo_atual_info['no_atual'])
                contexto_passo = f"Analisando subexpressão: {subexpr}"
            
            AIChatPopup(self, expressao_atual, contexto_passo)
        except Exception as e:
            popup_erro(f"Erro ao abrir chat com IA: {e}")

    def limpar_area_passos(self):
        if hasattr(self, 'scroll_passos') and self.scroll_passos:
            for child in self.scroll_passos.winfo_children():
                child.destroy()

    def popup_erro(self, msg):
        popup_erro(msg)

    def atualizar_ui(self):
        # Atualiza botoes
        if self.controller.state.historico_de_estados:
            self.botao_desfazer.configure(state="normal")
        else:
            self.botao_desfazer.configure(state="disabled")

        if self.controller.state.sessao_simplificacao_concluida:
            self.botao_pular.configure(state="disabled")
            for btn in self.botoes_leis:
                btn.configure(state="disabled")
        else:
            self.botao_pular.configure(state="normal")
            for btn in self.botoes_leis:
                # Regra pedagógica estrita: Leis sempre ficam habilitadas
                btn.configure(state="normal")

        # Atualiza labels
        if self.controller.state.arvore_interativa:
            self.label_expressao_inicial.configure(text=str(self.controller.state.arvore_interativa))
            
        if self.controller.state.motivo_parada_interativo == "no_further_simplification":
            self.label_analise_atual.configure(
                text="✅ Expressão totalmente simplificada!",
                text_color=Colors.SUCCESS
            )
            self.controller.concluir_sessao()
        elif self.controller.state.motivo_parada_interativo == "maximum_steps":
            self.label_analise_atual.configure(
                text="⚠️ Limite máximo de transformações atingido.",
                text_color=Colors.WARNING
            )
            self.controller.concluir_sessao()
        elif self.controller.state.motivo_parada_interativo == "repeated_state":
            self.label_analise_atual.configure(
                text="⚠️ Transformação resultou em estado repetido.",
                text_color=Colors.WARNING
            )
            self.controller.concluir_sessao()
        elif self.controller.state.passo_atual_info and self.controller.state.passo_atual_info['no_atual']:
            subexpr = str(self.controller.state.passo_atual_info['no_atual'])
            self.label_analise_atual.configure(
                text=f"Avaliando subexpressão: {subexpr}",
                text_color=Colors.TEXT_PRIMARY
            )
        else:
            self.label_analise_atual.configure(
                text="Aguardando próxima análise...",
                text_color=Colors.TEXT_SECONDARY
            )

    def adicionar_passo_sucesso(self, lei, expr_antes, expr_marcada, justificativa, expr_depois):
        frame_passo = ctk.CTkFrame(self.scroll_passos, fg_color=Colors.SURFACE_MEDIUM, corner_radius=Dimensions.CORNER_RADIUS_SMALL)
        frame_passo.pack(fill="x", pady=Spacing.XS)

        # Header do passo (número e lei)
        header_frame = ctk.CTkFrame(frame_passo, fg_color="transparent")
        header_frame.pack(fill="x", padx=Spacing.SM, pady=(Spacing.SM, 0))

        lbl_step = ctk.CTkLabel(
            header_frame, 
            text=f"Passo {self.controller.state.contador_passos}:",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        lbl_step.pack(side="left")

        lbl_lei = ctk.CTkLabel(
            header_frame,
            text=lei,
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.SUCCESS
        )
        lbl_lei.pack(side="right")

        # Corpo do passo (expressões)
        content_frame = ctk.CTkFrame(frame_passo, fg_color="transparent")
        content_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)

        lbl_antes = ctk.CTkLabel(
            content_frame,
            text=f"Antes: {expr_antes}",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        lbl_antes.pack(anchor="w")

        lbl_depois = ctk.CTkLabel(
            content_frame,
            text=f"Depois: {expr_depois}",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        lbl_depois.pack(anchor="w")
        
        # Scrolla para o final automaticamente
        self.scroll_passos._parent_canvas.yview_moveto(1.0)

    def adicionar_passo_pular(self, expr_ignorada):
        frame_passo = ctk.CTkFrame(self.scroll_passos, fg_color=Colors.SURFACE_MEDIUM, corner_radius=Dimensions.CORNER_RADIUS_SMALL)
        frame_passo.pack(fill="x", pady=Spacing.XS)

        lbl_acao = ctk.CTkLabel(
            frame_passo,
            text=f"⏭ Subexpressão ignorada:",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.WARNING
        )
        lbl_acao.pack(anchor="w", padx=Spacing.SM, pady=(Spacing.SM, 0))

        lbl_expr = ctk.CTkLabel(
            frame_passo,
            text=expr_ignorada,
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        lbl_expr.pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.SM))
        
        self.scroll_passos._parent_canvas.yview_moveto(1.0)

    def reconstruir_area_passos(self):
        self.limpar_area_passos()
        # No histórico antigo era textual. Idealmente reconstruir os frames.
        # Por simplicidade, podemos apenas exibir os passos numéricos em string,
        # ou varrer historico_interativo. Como o projeto atual gera strings lineares,
        # a gente recria com labels simples.
        for item in self.controller.state.historico_interativo:
            lbl = ctk.CTkLabel(
                self.scroll_passos,
                text=item,
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w",
                justify="left"
            )
            lbl.pack(fill="x", padx=Spacing.SM, pady=2)
        
        self.scroll_passos._parent_canvas.yview_moveto(1.0)

    def voltar_tela(self):
        self.controller.concluir_sessao()
        self.is_initialized = False
        if self.on_close_cb:
            self.on_close_cb()
        else:
            self.navigation.show_screen("home")

    def reflow_interactive_layout(self, event=None):
        container_width = event.width if event is not None else self.main_container.winfo_width()
        wraplength = calculate_wraplength(container_width)
        
        if self.label_expressao_inicial:
            self.label_expressao_inicial.configure(wraplength=wraplength)
        if self.label_analise_atual:
            self.label_analise_atual.configure(wraplength=wraplength)

        law_columns = responsive_columns(container_width, item_minimum=250, maximum=3)
        for column in range(3):
            self.frame_grid_leis.grid_columnconfigure(
                column, weight=1 if column < law_columns else 0
            )
        for index, button in enumerate(self.botoes_leis):
            button.grid(
                row=index // law_columns,
                column=index % law_columns,
                padx=Spacing.XS,
                pady=Spacing.XS,
                sticky="ew",
            )

        control_columns = 3 if container_width >= 560 else 1
        for column in range(3):
            self.frame_controles_interativo.grid_columnconfigure(
                column, weight=1 if column < control_columns else 0
            )
        for index, button in enumerate(self.control_buttons):
            button.grid(
                row=index // control_columns,
                column=index % control_columns,
                padx=Spacing.XS,
                pady=Spacing.XS,
                sticky="ew",
            )
