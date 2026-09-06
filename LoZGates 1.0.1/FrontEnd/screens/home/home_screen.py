# FrontEnd/screens/home/home_screen.py
# Tela inicial — Etapa 8: Redesign como dashboard educacional
# Layout 2+1 cards com descrição e hover visual.
# Preserva navegação, callbacks e destinos originais.

import customtkinter as ctk
from customtkinter import CTkFont

from FrontEnd.utils.responsive import calculate_window_layout
from FrontEnd.styles.design_tokens import (
    Colors, Dimensions, Spacing, Typography, get_font, get_title_font
)
from FrontEnd.dialogs.interactive_help import show_interactive_help


class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, navigation_controller, root_window):
        super().__init__(parent, fg_color=Colors.PRIMARY_BG)

        self.navigation = navigation_controller
        self.root_window = root_window

        self.grid(row=0, column=0, sticky="nsew")
        self._build_ui()

    def _build_ui(self):
        # Container central rolável
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        outer = ctk.CTkFrame(self, fg_color=Colors.PRIMARY_BG)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # ── Header ──────────────────────────────────────────────────────
        header = ctk.CTkFrame(outer, fg_color=Colors.SURFACE_DARK, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        fonte_logo = CTkFont(family="Momentz", size=Typography.SIZE_DISPLAY)
        lbl_logo = ctk.CTkLabel(
            header,
            text="LoZ Gates",
            font=fonte_logo,
            text_color=Colors.TEXT_ACCENT,
        )
        lbl_logo.grid(row=0, column=0, padx=Spacing.XL, pady=(Spacing.XL, Spacing.XS), sticky="w")

        lbl_subtitle = ctk.CTkLabel(
            header,
            text="Lógica proposicional e circuitos digitais, passo a passo.",
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_SECONDARY,
        )
        lbl_subtitle.grid(row=1, column=0, padx=Spacing.XL, pady=(0, Spacing.XL), sticky="w")

        # Botão de ajuda no header (canto direito)
        btn_help = ctk.CTkButton(
            header,
            text="?  Ajuda",
            width=100,
            height=36,
            fg_color=Colors.SURFACE_MEDIUM,
            hover_color=Colors.SURFACE_LIGHT,
            text_color=Colors.TEXT_ACCENT,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_ACTIVE,
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            command=lambda: show_interactive_help(self.root_window),
        )
        btn_help.grid(row=0, column=1, rowspan=2, padx=Spacing.XL, pady=Spacing.LG, sticky="e")

        # ── Área principal dos cards ─────────────────────────────────────
        content = ctk.CTkFrame(outer, fg_color=Colors.PRIMARY_BG)
        content.grid(row=1, column=0, sticky="nsew", padx=Spacing.XL, pady=Spacing.XL)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Card 1 — Expressões & Circuitos
        self._make_card(
            parent=content,
            row=0, col=0,
            symbol="⬡",
            title="Expressões & Circuitos",
            description=(
                "Analise expressões lógicas, gere tabelas verdade,\n"
                "simplifique e visualize circuitos."
            ),
            btn_text="Explorar →",
            command=lambda: self.navigation.show_screen("principal"),
        )

        # Card 2 — Equivalência Lógica
        self._make_card(
            parent=content,
            row=0, col=1,
            symbol="⟺",
            title="Equivalência Lógica",
            description=(
                "Compare duas expressões e verifique\n"
                "se são logicamente equivalentes."
            ),
            btn_text="Explorar →",
            command=lambda: self.navigation.show_screen("equivalencia"),
        )

        # Card 3 — Problemas (linha inteira)
        self._make_card(
            parent=content,
            row=1, col=0,
            colspan=2,
            symbol="⚑",
            title="Problemas & Exercícios",
            description=(
                "Pratique com problemas do mundo real que podem ser resolvidos\n"
                "com lógica proposicional e circuitos digitais."
            ),
            btn_text="Praticar →",
            command=lambda: self.navigation.show_screen("problemas_reais"),
            wide=True,
        )

    def _make_card(
        self,
        parent,
        row, col,
        symbol, title, description,
        btn_text, command,
        colspan=1,
        wide=False,
    ):
        """Cria um card de funcionalidade com hover visual."""

        card = ctk.CTkFrame(
            parent,
            fg_color=Colors.SURFACE_DARK,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            corner_radius=Dimensions.CORNER_RADIUS_LARGE,
        )
        card.grid(
            row=row, column=col,
            columnspan=colspan,
            padx=Spacing.MD,
            pady=Spacing.MD,
            sticky="nsew",
        )
        card.grid_columnconfigure(0, weight=1)

        # Hover: destacar borda
        def on_enter(_e):
            card.configure(border_color=Colors.BORDER_ACTIVE)

        def on_leave(_e):
            card.configure(border_color=Colors.BORDER_DEFAULT)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        # Símbolo lógico
        lbl_symbol = ctk.CTkLabel(
            card,
            text=symbol,
            font=get_font(Typography.SIZE_TITLE_LARGE, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
        )
        lbl_symbol.grid(row=0, column=0, padx=Spacing.XL, pady=(Spacing.XL, Spacing.SM), sticky="w")

        # Título do card
        lbl_title = ctk.CTkLabel(
            card,
            text=title,
            font=get_title_font(Typography.SIZE_TITLE_SMALL),
            text_color=Colors.TEXT_PRIMARY,
        )
        lbl_title.grid(row=1, column=0, padx=Spacing.XL, pady=(0, Spacing.SM), sticky="w")

        # Descrição
        lbl_desc = ctk.CTkLabel(
            card,
            text=description,
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY,
            justify="left",
            anchor="w",
        )
        lbl_desc.grid(row=2, column=0, padx=Spacing.XL, pady=(0, Spacing.LG), sticky="w")

        # Botão de ação
        btn_width = 180 if wide else 140
        btn = ctk.CTkButton(
            card,
            text=btn_text,
            width=btn_width,
            height=Dimensions.BUTTON_HEIGHT_STANDARD,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color="#000000",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            command=command,
        )
        btn.grid(
            row=3, column=0,
            padx=Spacing.XL,
            pady=(0, Spacing.XL),
            sticky="e" if not wide else "e",
        )
