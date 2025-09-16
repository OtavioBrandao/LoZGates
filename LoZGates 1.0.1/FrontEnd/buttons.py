# Fábricas de botões padronizadas - UI/UX unificada com design tokens
# Atualizado para usar sistema de design consistente

import customtkinter as ctk
from .design_tokens import Colors, Typography, Dimensions, get_font

class Button:
    def __init__(self, nome, comando, botao):
        self.nome = nome
        self.comando = comando
        self.botao = botao
    
    @staticmethod
    def botao_duvida(frame, size="normal"):
        """Botão de ajuda/dúvida com ícone"""
        width = 50 if size == "normal" else 40
        height = 50 if size == "normal" else 40
        font_size = Typography.SIZE_BODY if size == "normal" else Typography.SIZE_BODY_SMALL
        
        botao = ctk.CTkButton(
            frame,
            text="❓",
            fg_color=Colors.BUTTON_PRIMARY,
            text_color=Colors.BUTTON_TEXT,
            hover_color=Colors.BUTTON_PRIMARY_HOVER,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            width=width,
            height=height,
            font=get_font(font_size),
            corner_radius=Dimensions.CORNER_RADIUS_LARGE,
        )
        return botao

    @staticmethod
    def botao_voltar(nome, frame, size="normal"):
        """Botão de voltar com cor dourada distintiva"""
        width = Dimensions.BUTTON_WIDTH_STANDARD if size == "normal" else Dimensions.BUTTON_WIDTH_SMALL
        height = Dimensions.BUTTON_HEIGHT_STANDARD if size == "normal" else Dimensions.BUTTON_HEIGHT_SMALL
        
        botao = ctk.CTkButton(
            frame,
            text="← " + nome,
            fg_color=Colors.ACCENT_GOLD,
            text_color=Colors.BUTTON_TEXT,
            hover_color=Colors.ACCENT_GOLD_HOVER,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            width=width,
            height=height,
            font=get_font(Typography.SIZE_BODY),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        )
        return botao
    
    @staticmethod
    def botao_padrao(nome, frame, size="normal", style="primary"):
        """Botão padrão com variações de tamanho e estilo"""
        width = Dimensions.BUTTON_WIDTH_STANDARD if size == "normal" else Dimensions.BUTTON_WIDTH_SMALL
        height = Dimensions.BUTTON_HEIGHT_STANDARD if size == "normal" else Dimensions.BUTTON_HEIGHT_SMALL
        
        # Cores baseadas no estilo
        if style == "success":
            fg_color = Colors.SUCCESS
            hover_color = "#45A049"
            text_color = Colors.TEXT_PRIMARY
        elif style == "warning":
            fg_color = Colors.WARNING
            hover_color = "#F57C00"
            text_color = Colors.TEXT_PRIMARY
        elif style == "error":
            fg_color = Colors.ERROR
            hover_color = "#D32F2F"
            text_color = Colors.TEXT_PRIMARY
        else:  # primary (padrão)
            fg_color = Colors.BUTTON_PRIMARY
            hover_color = Colors.BUTTON_PRIMARY_HOVER
            text_color = Colors.BUTTON_TEXT
        
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
        """Botão customizado para casos especiais"""
        if hover_color is None:
            hover_color = Colors.BUTTON_PRIMARY_HOVER
        if text_color is None:
            text_color = Colors.TEXT_PRIMARY if fg_color in [Colors.SUCCESS, Colors.WARNING, Colors.ERROR] else Colors.BUTTON_TEXT
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