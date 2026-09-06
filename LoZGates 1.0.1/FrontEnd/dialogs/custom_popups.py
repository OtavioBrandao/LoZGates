# FrontEnd/dialogs/custom_popups.py
# Popups padronizados com CustomTkinter — Design System Etapa 8
# Preserva comportamento existente, melhora apenas o visual.

import customtkinter as ctk
from config import apply_window_icon
from FrontEnd.utils.responsive import calculate_window_layout


def popup_erro(mensagem, parent=None):
    """Popup de erro — visual consistente com o Design System."""
    from FrontEnd.styles.design_tokens import Colors, Typography, Dimensions, Spacing, get_font

    popup = ctk.CTkToplevel(parent)
    popup.attributes('-topmost', True)
    popup.after(10, lambda: popup.attributes('-topmost', False))
    popup.title("Erro")

    try:
        apply_window_icon(popup)
    except Exception:
        pass

    popup_layout = calculate_window_layout(
        popup.winfo_screenwidth(),
        popup.winfo_screenheight(),
        preferred=(460, 200),
        minimum=(320, 160),
        margin=24,
    )
    popup.geometry(popup_layout.geometry)
    popup.configure(fg_color=Colors.SURFACE_DARK)
    popup.resizable(False, False)

    # Ícone + mensagem
    content_frame = ctk.CTkFrame(popup, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=Spacing.XL, pady=(Spacing.XL, Spacing.MD))

    icon_label = ctk.CTkLabel(
        content_frame,
        text="✕",
        font=get_font(Typography.SIZE_TITLE_LARGE, Typography.WEIGHT_BOLD),
        text_color=Colors.ERROR,
    )
    icon_label.pack(pady=(0, Spacing.SM))

    label = ctk.CTkLabel(
        content_frame,
        text=mensagem,
        font=get_font(Typography.SIZE_BODY),
        text_color=Colors.TEXT_PRIMARY,
        wraplength=max(260, popup_layout.width - 60),
        justify="center",
    )
    label.pack(pady=(0, Spacing.MD))

    botao_ok = ctk.CTkButton(
        popup,
        text="OK",
        width=100,
        height=Dimensions.BUTTON_HEIGHT_SMALL,
        fg_color=Colors.ERROR,
        hover_color=Colors.ERROR_HOVER,
        text_color="#FFFFFF",
        font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        command=popup.destroy,
    )
    botao_ok.pack(pady=(0, Spacing.XL))


def popup_duvida(mensagem, parent=None):
    """Popup de ajuda/dúvida — visual consistente com o Design System."""
    from FrontEnd.styles.design_tokens import Colors, Typography, Dimensions, Spacing, get_font

    popup = ctk.CTkToplevel(parent)
    popup.attributes('-topmost', True)
    popup.after(10, lambda: popup.attributes('-topmost', False))
    popup.title("Ajuda")

    try:
        apply_window_icon(popup)
    except Exception:
        pass

    popup_layout = calculate_window_layout(
        popup.winfo_screenwidth(),
        popup.winfo_screenheight(),
        preferred=(520, 520),
        minimum=(340, 320),
        margin=24,
    )
    popup.geometry(popup_layout.geometry)
    popup.configure(fg_color=Colors.SURFACE_DARK)
    popup.resizable(True, True)

    # Header
    header = ctk.CTkFrame(popup, fg_color=Colors.SURFACE_MEDIUM, corner_radius=0)
    header.pack(fill="x")

    title_label = ctk.CTkLabel(
        header,
        text="?   Ajuda",
        font=get_font(Typography.SIZE_TITLE_SMALL, Typography.WEIGHT_BOLD),
        text_color=Colors.TEXT_ACCENT,
    )
    title_label.pack(pady=Spacing.MD, padx=Spacing.XL, anchor="w")

    # Texto de ajuda
    info_extra = "LoZ Gates — Ferramenta educacional para Lógica Proposicional e Circuitos Digitais.\n\n"
    textbox = ctk.CTkTextbox(
        popup,
        wrap="word",
        font=get_font(Typography.SIZE_BODY),
        fg_color=Colors.SURFACE_DARK,
        text_color=Colors.TEXT_PRIMARY,
        border_width=0,
    )
    textbox.pack(padx=Spacing.LG, pady=Spacing.MD, fill="both", expand=True)
    textbox.insert("1.0", info_extra + mensagem)
    textbox.configure(state="disabled")

    botao_fechar = ctk.CTkButton(
        popup,
        text="Fechar",
        width=120,
        height=Dimensions.BUTTON_HEIGHT_SMALL,
        fg_color=Colors.SURFACE_MEDIUM,
        hover_color=Colors.SURFACE_LIGHT,
        text_color=Colors.TEXT_SECONDARY,
        font=get_font(Typography.SIZE_BODY),
        corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
        border_width=Dimensions.BORDER_WIDTH_STANDARD,
        border_color=Colors.BORDER_DEFAULT,
        command=popup.destroy,
    )
    botao_fechar.pack(pady=(0, Spacing.LG))
