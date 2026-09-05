import customtkinter as ctk
from customtkinter import CTkFont

from FrontEnd.utils.responsive import calculate_window_layout
from FrontEnd.styles.design_tokens import Colors, Dimensions, Spacing, Typography, get_font
from FrontEnd.buttons import Button
from FrontEnd.interactive_help import show_interactive_help

class HomeScreen(ctk.CTkFrame):
    def __init__(self, parent, navigation_controller, root_window):
        super().__init__(parent, fg_color=Colors.PRIMARY_BG)
        
        self.navigation = navigation_controller
        self.root_window = root_window
        
        self.grid(row=0, column=0, sticky="nsew")
        self._build_ui()

    def _build_ui(self):
        home_card = ctk.CTkFrame(
            self,
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
        botao_circuitos.configure(command=lambda: self.navigation.show_screen("principal"))
        botao_circuitos.pack(fill="x", padx=Spacing.XL, pady=Spacing.SM)

        botao_equivalencia = Button.botao_padrao("🔄 Equivalência Lógica", home_card)
        botao_equivalencia.configure(command=lambda: self.navigation.show_screen("equivalencia"))
        botao_equivalencia.pack(fill="x", padx=Spacing.XL, pady=Spacing.SM)

        botao_info = Button.botao_padrao("❔ Ajuda e manual", home_card)
        botao_info.configure(command=lambda: show_interactive_help(self.root_window))
        botao_info.pack(fill="x", padx=Spacing.XL, pady=(Spacing.SM, Spacing.XXL))
