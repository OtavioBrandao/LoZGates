import customtkinter as ctk
import tkinter as tk

from FrontEnd.styles.design_tokens import Colors, Dimensions, Spacing, Typography, get_font, get_title_font
from FrontEnd.components.buttons import Button
from FrontEnd.dialogs.custom_popups import popup_erro

class EquivalenceScreen(ctk.CTkFrame):
    def __init__(self, parent, navigation_controller, controller):
        super().__init__(parent, fg_color=Colors.PRIMARY_BG)
        
        self.navigation = navigation_controller
        self.controller = controller
        
        self.grid(row=0, column=0, sticky="nsew")
        
        self._build_ui()

    def _build_ui(self):
        equivalencia_card = ctk.CTkFrame(
            self,
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

        self.entrada2 = ctk.CTkEntry(
            equivalencia_card,
            width=350, 
            placeholder_text="Primeira expressão", 
            font=get_font(Typography.SIZE_BODY_SMALL),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        self.entrada2.pack(fill="x", padx=Spacing.XL, pady=Spacing.XS)

        self.entrada3 = ctk.CTkEntry(
            equivalencia_card,
            width=350, 
            placeholder_text="Segunda expressão", 
            font=get_font(Typography.SIZE_BODY_SMALL),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        self.entrada3.pack(fill="x", padx=Spacing.XL, pady=Spacing.XS)

        botao_comparar = Button.botao_padrao("✅ Comparar", equivalencia_card, style="success")
        botao_comparar.configure(command=self.on_compare)
        botao_comparar.pack(fill="x", padx=Spacing.XL, pady=(Spacing.MD, Spacing.SM))

        self.resultado_equivalencia_frame = ctk.CTkFrame(
            equivalencia_card, fg_color="transparent", height=40
        )
        self.resultado_equivalencia_frame.pack(fill="x", padx=Spacing.XL)
        self.resultado_equivalencia_frame.pack_propagate(False)

        botao_voltar_equivalencia = Button.botao_voltar("Voltar", equivalencia_card)
        botao_voltar_equivalencia.configure(command=self.on_back)
        botao_voltar_equivalencia.pack(fill="x", padx=Spacing.XL, pady=(Spacing.SM, Spacing.XXL))

        self.label_equivalente = ctk.CTkLabel(
            self.resultado_equivalencia_frame,
            text="✅ São equivalentes!", 
            font=get_title_font(Typography.SIZE_TITLE_SMALL), 
            text_color=Colors.SUCCESS, 
            fg_color=None
        )
        
        self.label_nao_equivalente = ctk.CTkLabel(
            self.resultado_equivalencia_frame,
            text="❌ Não são equivalentes", 
            font=get_title_font(Typography.SIZE_TITLE_SMALL), 
            text_color=Colors.ERROR, 
            fg_color=None
        )

    def on_compare(self):
        try:
            expr1 = self.entrada2.get()
            expr2 = self.entrada3.get()
            
            resultado = self.controller.compare(expr1, expr2)
            
            if resultado:
                self.label_equivalente.pack(padx=Spacing.XL, pady=Spacing.XS)
                self.label_nao_equivalente.pack_forget()
            else:
                self.label_nao_equivalente.pack(padx=Spacing.XL, pady=Spacing.XS)
                self.label_equivalente.pack_forget()
                
        except ValueError as ve:
            popup_erro(str(ve))
        except Exception as e:
            self.controller.user_logger.log_error("equivalence_check_error", str(e), "comparar_function")
            popup_erro(f"Erro ao comparar expressões: {e}")

    def on_back(self):
        # Limpa os campos e resultado ao sair da tela
        self.entrada2.delete(0, tk.END)
        self.entrada3.delete(0, tk.END)
        self.entrada2.configure(placeholder_text="Primeira expressão")
        self.entrada3.configure(placeholder_text="Segunda expressão")
        self.label_equivalente.pack_forget()
        self.label_nao_equivalente.pack_forget()
        
        # Voltar para a tela anterior (ou "home")
        self.navigation.show_screen("home")
