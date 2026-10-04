# FrontEnd/screens/resolver/resolver_screen.py
# Resolver — Etapa 8: Redesign pedagógico com 3 zonas claras
#
# REGRA ABSOLUTA PRESERVADA:
# - 9 leis SEMPRE habilitadas (state="normal")
# - Validação ocorre APÓS clique (popup existente)
# - Undo/Pular/histórico não alterados

import customtkinter as ctk
import logging

import BackEnd.simplificador_interativo as simpli

from FrontEnd.styles.design_tokens import (
    Colors, Typography, Dimensions, Spacing,
    get_font, get_title_font, get_code_font
)
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

        self.main_container.grid_rowconfigure(2, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # ════════════════════════════════════════════════════════════
        # ZONA 1 — CONTEXTO: Expressão atual + Subexpressão em análise
        # ════════════════════════════════════════════════════════════

        self.frame_expressao_inicial = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
        )
        self.frame_expressao_inicial.pack(fill="x", pady=(0, Spacing.SM))

        # Header da zona 1
        z1_header = ctk.CTkFrame(self.frame_expressao_inicial, fg_color="transparent")
        z1_header.pack(fill="x", padx=Spacing.MD, pady=(Spacing.MD, Spacing.XS))

        titulo_inicial = ctk.CTkLabel(
            z1_header,
            text="Expressão Atual",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
        )
        titulo_inicial.pack(side="left")

        # Botão Sugestão de IA (canto direito do header)
        botao_ia = Button.botao_padrao("  IA", z1_header)
        botao_ia.configure(
            command=self.abrir_chat_ia,
            width=80,
            height=28,
            font=get_font(Typography.SIZE_CAPTION),
        )
        botao_ia.pack(side="right")

        # Expressão atual em fonte monoespacada
        self.label_expressao_inicial = ctk.CTkLabel(
            self.frame_expressao_inicial,
            text="",
            font=get_code_font(Typography.SIZE_CODE),
            text_color=Colors.TEXT_CODE,
            wraplength=800,
        )
        self.label_expressao_inicial.pack(pady=(0, Spacing.XS), padx=Spacing.MD)

        # Separador + Subexpressão em análise (destaque principal)
        sep_label = ctk.CTkLabel(
            self.frame_expressao_inicial,
            text="▼  Subexpressão em análise:",
            font=get_font(Typography.SIZE_CAPTION),
            text_color=Colors.TEXT_MUTED,
        )
        sep_label.pack(anchor="w", padx=Spacing.MD)

        self.frame_analise_bg = ctk.CTkFrame(
            self.frame_expressao_inicial,
            fg_color=Colors.PRIMARY_MUTED,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_ACTIVE,
        )
        self.frame_analise_bg.pack(fill="x", padx=Spacing.MD, pady=(Spacing.XS, Spacing.MD))

        self.label_analise_atual = ctk.CTkLabel(
            self.frame_analise_bg,
            text="Aguardando início da análise...",
            # Destaque MAIOR: CODE_LARGE para subexpressão (era SIZE_BODY_SMALL)
            font=get_code_font(Typography.SIZE_CODE_LARGE, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=800,
        )
        self.label_analise_atual.pack(pady=Spacing.MD, padx=Spacing.LG)

        # ════════════════════════════════════════════════════════════
        # ZONA 2 — LEIS: Agrupadas visualmente em Básicas / Estruturais
        # ════════════════════════════════════════════════════════════
        # REGRA ABSOLUTA: os 9 botões ficam SEMPRE state="normal"

        self.frame_leis = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
        )
        self.frame_leis.pack(fill="x", pady=(0, Spacing.SM))

        z2_header = ctk.CTkFrame(self.frame_leis, fg_color="transparent")
        z2_header.pack(fill="x", padx=Spacing.MD, pady=(Spacing.MD, Spacing.XS))

        titulo_leis = ctk.CTkLabel(
            z2_header,
            text="Escolha uma Lei para Aplicar",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
        )
        titulo_leis.pack(side="left")

        # Grupo "Básicas"
        grp_basicas = ctk.CTkFrame(self.frame_leis, fg_color="transparent")
        grp_basicas.pack(fill="x", padx=Spacing.MD, pady=(Spacing.XS, 0))

        ctk.CTkLabel(
            grp_basicas,
            text="Básicas",
            font=get_font(Typography.SIZE_CAPTION, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", pady=(0, Spacing.XS))

        self.frame_grid_basicas = ctk.CTkFrame(grp_basicas, fg_color="transparent")
        self.frame_grid_basicas.pack(fill="x")

        # Grupo "Estruturais"
        grp_estruturais = ctk.CTkFrame(self.frame_leis, fg_color="transparent")
        grp_estruturais.pack(fill="x", padx=Spacing.MD, pady=(Spacing.SM, Spacing.MD))

        ctk.CTkLabel(
            grp_estruturais,
            text="Estruturais",
            font=get_font(Typography.SIZE_CAPTION, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", pady=(0, Spacing.XS))

        self.frame_grid_estruturais = ctk.CTkFrame(grp_estruturais, fg_color="transparent")
        self.frame_grid_estruturais.pack(fill="x")

        # Definição dos 9 botões em dois grupos (visual apenas — lógica preservada)
        basicas = [
            {"texto": "Inversa",     "desc": "A · ¬A = 0",   "idx": 0},
            {"texto": "Nula",        "desc": "A · 0 = 0",    "idx": 1},
            {"texto": "Identidade",  "desc": "A · 1 = A",    "idx": 2},
            {"texto": "Idempotente", "desc": "A · A = A",    "idx": 3},
        ]
        estruturais = [
            {"texto": "Absorção",    "desc": "A·(A+B)=A",     "idx": 4},
            {"texto": "De Morgan",   "desc": "¬(A·B)=¬A+¬B", "idx": 5},
            {"texto": "Distributiva","desc": "(A+B)·(A+C)",   "idx": 6},
            {"texto": "Associativa", "desc": "(A·B)·C",       "idx": 7},
            {"texto": "Comutativa",  "desc": "B·A = A·B",     "idx": 8},
        ]

        self.botoes_leis = []
        self.frame_grid_leis = self.frame_grid_basicas  # alias para reflow

        # Cria botões básicos
        self._botoes_basicos = []
        for info in basicas:
            btn = Button.botao_lei(
                f"{info['texto']}\n{info['desc']}",
                self.frame_grid_basicas,
            )
            btn.configure(command=lambda idx=info["idx"]: self.controller.on_lei_selecionada(idx))
            self._botoes_basicos.append(btn)
            self.botoes_leis.append(btn)

        # Cria botões estruturais
        self._botoes_estruturais = []
        for info in estruturais:
            btn = Button.botao_lei(
                f"{info['texto']}\n{info['desc']}",
                self.frame_grid_estruturais,
            )
            btn.configure(command=lambda idx=info["idx"]: self.controller.on_lei_selecionada(idx))
            self._botoes_estruturais.append(btn)
            self.botoes_leis.append(btn)

        # ════════════════════════════════════════════════════════════
        # ZONA 3 — HISTÓRICO + CONTROLES
        # ════════════════════════════════════════════════════════════

        self.frame_passos = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
        )
        self.frame_passos.pack(fill="both", expand=True, pady=(0, Spacing.SM))

        z3_header = ctk.CTkFrame(self.frame_passos, fg_color="transparent")
        z3_header.pack(fill="x", padx=Spacing.MD, pady=(Spacing.MD, Spacing.XS))

        titulo_passos = ctk.CTkLabel(
            z3_header,
            text="Histórico de Passos",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
        )
        titulo_passos.pack(side="left")

        self.scroll_passos = ctk.CTkScrollableFrame(
            self.frame_passos,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=200,
        )
        self.scroll_passos.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.SM))

        # ── Barra de controles ──────────────────────────────────────
        # Hierarquia: primary=Pular | warning=Desfazer | ghost=Voltar

        self.frame_controles_interativo = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.frame_controles_interativo.pack(fill="x", pady=Spacing.SM)

        self.botao_pular = Button.botao_padrao("Pular →", self.frame_controles_interativo)
        self.botao_pular.configure(command=self.controller.on_pular_selecionado, width=140)

        self.botao_desfazer = Button.botao_padrao("↶ Desfazer", self.frame_controles_interativo, style="warning")
        self.botao_desfazer.configure(
            command=self.controller.on_desfazer_selecionado, state="disabled", width=140
        )

        self.botao_voltar_interativo = Button.botao_voltar("Voltar", self.frame_controles_interativo)
        self.botao_voltar_interativo.configure(command=self.voltar_tela, width=140)

        self.control_buttons = [self.botao_pular, self.botao_desfazer, self.botao_voltar_interativo]

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
            expressao_atual = simpli.formatar(self.controller.state.arvore_interativa) if self.controller.state.arvore_interativa else self.controller.state.expressao_global
            contexto_passo = ""

            if self.controller.state.passo_atual_info:
                subexpr = simpli.formatar(self.controller.state.passo_atual_info['no_atual'])
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
        # Atualiza botão Desfazer
        if self.controller.state.historico_de_estados:
            self.botao_desfazer.configure(state="normal")
        else:
            self.botao_desfazer.configure(state="disabled")

        # REGRA PEDAGÓGICA: leis SEMPRE habilitadas
        if self.controller.state.sessao_simplificacao_concluida:
            self.botao_pular.configure(state="disabled")
            for btn in self.botoes_leis:
                btn.configure(state="disabled")
        else:
            self.botao_pular.configure(state="normal")
            for btn in self.botoes_leis:
                btn.configure(state="normal")  # SEMPRE normal

        # Atualiza expressão atual
        if self.controller.state.arvore_interativa:
            self.label_expressao_inicial.configure(
                text=simpli.formatar(self.controller.state.arvore_interativa)
            )

        # Atualiza subexpressão em análise (zona de maior destaque)
        if self.controller.state.motivo_parada_interativo == "no_further_simplification":
            self.label_analise_atual.configure(
                text="✓  Expressão totalmente simplificada!",
                text_color=Colors.TEXT_SUCCESS,
            )
            self.frame_analise_bg.configure(border_color=Colors.SUCCESS)
            self.controller.concluir_sessao()
        elif self.controller.state.motivo_parada_interativo == "maximum_steps":
            self.label_analise_atual.configure(
                text="!  Limite máximo de transformações atingido.",
                text_color=Colors.TEXT_WARNING,
            )
            self.frame_analise_bg.configure(border_color=Colors.WARNING)
            self.controller.concluir_sessao()
        elif self.controller.state.motivo_parada_interativo == "repeated_state":
            self.label_analise_atual.configure(
                text="!  Transformação resultou em estado repetido.",
                text_color=Colors.TEXT_WARNING,
            )
            self.frame_analise_bg.configure(border_color=Colors.WARNING)
            self.controller.concluir_sessao()
        elif self.controller.state.passo_atual_info and self.controller.state.passo_atual_info['no_atual']:
            subexpr = simpli.formatar(self.controller.state.passo_atual_info['no_atual'])
            self.label_analise_atual.configure(
                text=subexpr,
                text_color=Colors.TEXT_PRIMARY,
            )
            self.frame_analise_bg.configure(border_color=Colors.BORDER_ACTIVE)
        else:
            self.label_analise_atual.configure(
                text="Aguardando próxima análise...",
                text_color=Colors.TEXT_SECONDARY,
            )
            self.frame_analise_bg.configure(border_color=Colors.BORDER_DEFAULT)

    def adicionar_passo_sucesso(self, lei, expr_antes, expr_marcada, justificativa, expr_depois):
        n = self.controller.state.contador_passos
        frame_passo = ctk.CTkFrame(
            self.scroll_passos,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.SUCCESS,
        )
        frame_passo.pack(fill="x", pady=Spacing.XS)

        header_frame = ctk.CTkFrame(frame_passo, fg_color="transparent")
        header_frame.pack(fill="x", padx=Spacing.SM, pady=(Spacing.SM, 0))

        lbl_step = ctk.CTkLabel(
            header_frame,
            text=f"✓  Passo {n}:",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_SUCCESS,
        )
        lbl_step.pack(side="left")

        lbl_lei = ctk.CTkLabel(
            header_frame,
            text=lei,
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
        )
        lbl_lei.pack(side="right")

        content_frame = ctk.CTkFrame(frame_passo, fg_color="transparent")
        content_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)

        lbl_antes = ctk.CTkLabel(
            content_frame,
            text=f"Antes:  {expr_antes}",
            font=get_code_font(Typography.SIZE_CAPTION),
            text_color=Colors.TEXT_SECONDARY,
        )
        lbl_antes.pack(anchor="w")

        lbl_depois = ctk.CTkLabel(
            content_frame,
            text=f"Depois:  {expr_depois}",
            font=get_code_font(Typography.SIZE_CAPTION, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY,
        )
        lbl_depois.pack(anchor="w")

        self.scroll_passos._parent_canvas.yview_moveto(1.0)

    def adicionar_passo_pular(self, expr_ignorada):
        frame_passo = ctk.CTkFrame(
            self.scroll_passos,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.WARNING,
        )
        frame_passo.pack(fill="x", pady=Spacing.XS)

        lbl_acao = ctk.CTkLabel(
            frame_passo,
            text="→  Subexpressão pulada:",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_WARNING,
        )
        lbl_acao.pack(anchor="w", padx=Spacing.SM, pady=(Spacing.SM, 0))

        lbl_expr = ctk.CTkLabel(
            frame_passo,
            text=expr_ignorada,
            font=get_code_font(Typography.SIZE_CAPTION),
            text_color=Colors.TEXT_SECONDARY,
        )
        lbl_expr.pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.SM))

        self.scroll_passos._parent_canvas.yview_moveto(1.0)

    def reconstruir_area_passos(self):
        self.limpar_area_passos()
        for item in self.controller.state.historico_interativo:
            lbl = ctk.CTkLabel(
                self.scroll_passos,
                text=item,
                font=get_code_font(Typography.SIZE_CAPTION),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w",
                justify="left",
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

        # Layout responsivo dos botões de leis em dois grupos
        law_columns_basicas = responsive_columns(container_width, item_minimum=200, maximum=4)
        for column in range(4):
            self.frame_grid_basicas.grid_columnconfigure(
                column, weight=1 if column < law_columns_basicas else 0
            )
        for index, button in enumerate(self._botoes_basicos):
            button.grid(
                row=index // law_columns_basicas,
                column=index % law_columns_basicas,
                padx=Spacing.XS,
                pady=Spacing.XS,
                sticky="ew",
            )

        law_columns_estruturais = responsive_columns(container_width, item_minimum=200, maximum=5)
        for column in range(5):
            self.frame_grid_estruturais.grid_columnconfigure(
                column, weight=1 if column < law_columns_estruturais else 0
            )
        for index, button in enumerate(self._botoes_estruturais):
            button.grid(
                row=index // law_columns_estruturais,
                column=index % law_columns_estruturais,
                padx=Spacing.XS,
                pady=Spacing.XS,
                sticky="ew",
            )

        # Layout responsivo dos controles
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
