# FrontEnd/components/feedback_banner.py
# Componente de feedback visual reutilizável (sucesso / erro / aviso / info)
# NÃO substitui popups existentes — complementa com feedback inline

import customtkinter as ctk
from FrontEnd.styles.design_tokens import Colors, Typography, Dimensions, Spacing, get_font


class FeedbackBanner(ctk.CTkFrame):
    """
    Banner de feedback inline para exibir mensagens de estado.

    Tipos disponíveis: 'success', 'error', 'warning', 'info'

    Uso:
        banner = FeedbackBanner(parent)
        banner.show("✓ Expressão simplificada!", "success")
        banner.hide()
    """

    TYPE_CONFIG = {
        "success": {
            "icon": "✓",
            "fg": Colors.SURFACE_DARK,
            "border": Colors.SUCCESS,
            "text_color": Colors.TEXT_SUCCESS,
        },
        "error": {
            "icon": "✕",
            "fg": Colors.SURFACE_DARK,
            "border": Colors.ERROR,
            "text_color": Colors.TEXT_ERROR,
        },
        "warning": {
            "icon": "!",
            "fg": Colors.SURFACE_DARK,
            "border": Colors.WARNING,
            "text_color": Colors.TEXT_WARNING,
        },
        "info": {
            "icon": "i",
            "fg": Colors.SURFACE_DARK,
            "border": Colors.BORDER_ACTIVE,
            "text_color": Colors.TEXT_ACCENT,
        },
    }

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            **kwargs,
        )
        self._label = ctk.CTkLabel(
            self,
            text="",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=600,
            justify="left",
        )
        self._label.pack(padx=Spacing.MD, pady=Spacing.SM)
        # Inicialmente oculto
        self.pack_forget()

    def show(self, message: str, feedback_type: str = "info"):
        """Exibe o banner com a mensagem e tipo especificados."""
        config = self.TYPE_CONFIG.get(feedback_type, self.TYPE_CONFIG["info"])
        icon = config["icon"]
        self.configure(
            fg_color=config["fg"],
            border_color=config["border"],
        )
        self._label.configure(
            text=f"  {icon}  {message}",
            text_color=config["text_color"],
        )
        self.pack(fill="x", padx=Spacing.XS, pady=Spacing.XS)

    def hide(self):
        """Oculta o banner."""
        self.pack_forget()

    def clear(self):
        """Alias de hide()."""
        self.hide()
