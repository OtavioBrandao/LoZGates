# FrontEnd/components/buttons.py
# Fábricas de botões padronizadas — Design System Etapa 8
# Hierarquia visual clara: primary > success > warning > error > ghost > law

import customtkinter as ctk
from FrontEnd.styles.design_tokens import Colors, Typography, Dimensions, Spacing, get_font


class Button:
    def __init__(self, nome, comando, botao):
        self.nome = nome
        self.comando = comando
        self.botao = botao

    @staticmethod
    def botao_duvida(frame, size="normal"):
        """Botão de ajuda/dúvida (ícone ?)."""
        width  = 44 if size == "normal" else 36
        height = 44 if size == "normal" else 36
        font_size = Typography.SIZE_BODY if size == "normal" else Typography.SIZE_BODY_SMALL

        botao = ctk.CTkButton(
            frame,
            text="?",
            fg_color=Colors.SURFACE_MEDIUM,
            text_color=Colors.TEXT_ACCENT,
            hover_color=Colors.SURFACE_LIGHT,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_ACTIVE,
            width=width,
            height=height,
            font=get_font(font_size, Typography.WEIGHT_BOLD),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        )
        return botao

    @staticmethod
    def botao_voltar(nome, frame, size="normal"):
        """
        Botão de navegação secundária (Voltar).
        Agora usa variante ghost — sem preenchimento de cor forte.
        """
        width  = Dimensions.BUTTON_WIDTH_STANDARD if size == "normal" else Dimensions.BUTTON_WIDTH_SMALL
        height = Dimensions.BUTTON_HEIGHT_STANDARD if size == "normal" else Dimensions.BUTTON_HEIGHT_SMALL

        botao = ctk.CTkButton(
            frame,
            text="← " + nome,
            fg_color=Colors.SURFACE_MEDIUM,
            text_color=Colors.TEXT_SECONDARY,
            hover_color=Colors.SURFACE_LIGHT,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            width=width,
            height=height,
            font=get_font(Typography.SIZE_BODY),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        )
        return botao

    @staticmethod
    def botao_ghost(nome, frame, size="normal"):
        """
        Botão fantasma — ação secundária sem cor de fundo forte.
        Usa borda sutil e texto secundário.
        """
        width  = Dimensions.BUTTON_WIDTH_STANDARD if size == "normal" else Dimensions.BUTTON_WIDTH_SMALL
        height = Dimensions.BUTTON_HEIGHT_STANDARD if size == "normal" else Dimensions.BUTTON_HEIGHT_SMALL

        botao = ctk.CTkButton(
            frame,
            text=nome,
            fg_color=Colors.SURFACE_MEDIUM,
            text_color=Colors.TEXT_SECONDARY,
            hover_color=Colors.SURFACE_LIGHT,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            width=width,
            height=height,
            font=get_font(Typography.SIZE_BODY),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        )
        return botao

    @staticmethod
    def botao_lei(nome, frame):
        """
        Botão para as 9 leis do Resolver.
        REGRA PEDAGÓGICA: SEMPRE habilitados, nunca usar state='disabled' para leis.
        Visual discreto — surface com borda de destaque ao hover.
        """
        botao = ctk.CTkButton(
            frame,
            text=nome,
            fg_color=Colors.SURFACE_DARK,
            text_color=Colors.TEXT_PRIMARY,
            hover_color=Colors.SURFACE_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            height=Dimensions.BUTTON_HEIGHT_STANDARD,
            font=get_font(Typography.SIZE_BODY_SMALL),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        )
        return botao

    @staticmethod
    def botao_padrao(nome, frame, size="normal", style="primary"):
        """
        Botão padrão com hierarquia por estilo.

        Estilos disponíveis:
            primary  — ação principal (azul)
            success  — ação positiva (verde)
            warning  — ação reversível / atenção (âmbar)
            error    — ação destrutiva (vermelho)
        """
        width  = Dimensions.BUTTON_WIDTH_STANDARD if size == "normal" else Dimensions.BUTTON_WIDTH_SMALL
        height = Dimensions.BUTTON_HEIGHT_STANDARD if size == "normal" else Dimensions.BUTTON_HEIGHT_SMALL

        if style == "success":
            fg_color    = Colors.SUCCESS
            hover_color = Colors.SUCCESS_HOVER
            text_color  = "#FFFFFF"
        elif style == "warning":
            fg_color    = Colors.WARNING
            hover_color = "#C8922A"
            text_color  = "#000000"
        elif style == "error":
            fg_color    = Colors.ERROR
            hover_color = Colors.ERROR_HOVER
            text_color  = "#FFFFFF"
        else:  # primary (padrão)
            fg_color    = Colors.PRIMARY
            hover_color = Colors.PRIMARY_HOVER
            text_color  = "#000000"

        botao = ctk.CTkButton(
            frame,
            text=nome,
            fg_color=fg_color,
            text_color=text_color,
            hover_color=hover_color,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            width=width,
            height=height,
            font=get_font(Typography.SIZE_BODY),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        )
        return botao

    @staticmethod
    def botao_especial(nome, frame, fg_color, hover_color=None, text_color=None, width=None, height=None):
        """Botão com cores personalizadas. Para casos específicos que os estilos não cobrem."""
        if hover_color is None:
            hover_color = Colors.PRIMARY_HOVER
        if text_color is None:
            text_color = Colors.TEXT_PRIMARY
        if width is None:
            width = Dimensions.BUTTON_WIDTH_STANDARD
        if height is None:
            height = Dimensions.BUTTON_HEIGHT_STANDARD

        botao = ctk.CTkButton(
            frame,
            text=nome,
            fg_color=fg_color,
            text_color=text_color,
            hover_color=hover_color,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            width=width,
            height=height,
            font=get_font(Typography.SIZE_BODY),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        )
        return botao