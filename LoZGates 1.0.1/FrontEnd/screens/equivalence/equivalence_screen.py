# FrontEnd/screens/equivalence/equivalence_screen.py
# Tela de Equivalência — Etapa 8: Redesign visual
# Motor de comparação NÃO alterado (via EquivalenceController)
# Testado: P>Q e Q>P → NÃO EQUIVALENTES; P>Q e !P|Q → EQUIVALENTES

import customtkinter as ctk
import tkinter as tk

from FrontEnd.styles.design_tokens import (
    Colors, Dimensions, Spacing, Typography,
    get_font, get_title_font, get_code_font
)
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
        # Card central
        card = ctk.CTkFrame(
            self,
            fg_color=Colors.SURFACE_DARK,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            corner_radius=Dimensions.CORNER_RADIUS_LARGE,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Título com ícone ⟺
        titulo = ctk.CTkLabel(
            card,
            text="⟺  Equivalência Lógica",
            font=get_title_font(Typography.SIZE_TITLE_SMALL),
            text_color=Colors.TEXT_PRIMARY,
        )
        titulo.pack(padx=Spacing.XXL, pady=(Spacing.XXL, Spacing.XS))

        hint = ctk.CTkLabel(
            card,
            text="Digite as duas expressões e verifique se são logicamente equivalentes.",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=460,
            justify="center",
        )
        hint.pack(padx=Spacing.XL, pady=(0, Spacing.LG))

        # Label Expressão A
        lbl_a = ctk.CTkLabel(
            card,
            text="Expressão A:",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
        )
        lbl_a.pack(anchor="w", padx=Spacing.XL)

        self.entrada2 = ctk.CTkEntry(
            card,
            width=400,
            height=42,
            placeholder_text="Ex.: P > Q",
            font=get_code_font(Typography.SIZE_CODE),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_color=Colors.BORDER_DEFAULT,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
        )
        self.entrada2.pack(fill="x", padx=Spacing.XL, pady=(Spacing.XS, Spacing.MD))
        self.entrada2.bind("<Return>", lambda _: self.on_compare())

        # Separador visual ⟺
        sep_frame = ctk.CTkFrame(card, fg_color="transparent")
        sep_frame.pack(fill="x", padx=Spacing.XL, pady=Spacing.XS)

        sep_line_l = ctk.CTkFrame(sep_frame, fg_color=Colors.BORDER_DEFAULT, height=2)
        sep_line_l.pack(side="left", fill="x", expand=True, pady=8)

        sep_label = ctk.CTkLabel(
            sep_frame,
            text="  ⟺  comparar  ",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_MUTED,
        )
        sep_label.pack(side="left")

        sep_line_r = ctk.CTkFrame(sep_frame, fg_color=Colors.BORDER_DEFAULT, height=2)
        sep_line_r.pack(side="left", fill="x", expand=True, pady=8)

        # Label Expressão B
        lbl_b = ctk.CTkLabel(
            card,
            text="Expressão B:",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
        )
        lbl_b.pack(anchor="w", padx=Spacing.XL)

        self.entrada3 = ctk.CTkEntry(
            card,
            width=400,
            height=42,
            placeholder_text="Ex.: !P | Q",
            font=get_code_font(Typography.SIZE_CODE),
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_color=Colors.BORDER_DEFAULT,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
        )
        self.entrada3.pack(fill="x", padx=Spacing.XL, pady=(Spacing.XS, Spacing.LG))
        self.entrada3.bind("<Return>", lambda _: self.on_compare())

        # Botão Comparar
        botao_comparar = Button.botao_padrao("⟺  Comparar Expressões", card, style="success")
        botao_comparar.configure(command=self.on_compare)
        botao_comparar.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

        # Área de resultado — caixa com fundo colorido (não só texto)
        self.resultado_frame = ctk.CTkFrame(
            card,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_THICK,
            border_color=Colors.BORDER_DEFAULT,
        )
        self.resultado_frame.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))
        self.resultado_frame.pack_forget()  # oculto até haver resultado

        self.label_resultado = ctk.CTkLabel(
            self.resultado_frame,
            text="",
            font=get_title_font(Typography.SIZE_TITLE_SMALL),
            text_color=Colors.TEXT_PRIMARY,
            pady=Spacing.MD,
        )
        self.label_resultado.pack(pady=Spacing.MD)

        # Botão Voltar
        botao_voltar = Button.botao_voltar("Voltar", card)
        botao_voltar.configure(command=self.on_back)
        botao_voltar.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.XXL))

    def on_compare(self):
        try:
            expr1 = self.entrada2.get()
            expr2 = self.entrada3.get()

            resultado = self.controller.compare(expr1, expr2)

            self.resultado_frame.pack(fill="x", padx=Spacing.XL, pady=(0, Spacing.MD))

            if resultado:
                self.resultado_frame.configure(
                    fg_color=Colors.SUCCESS_MUTED,
                    border_color=Colors.SUCCESS,
                )
                self.label_resultado.configure(
                    text="✓  São equivalentes!",
                    text_color=Colors.TEXT_SUCCESS,
                )
            else:
                self.resultado_frame.configure(
                    fg_color=Colors.ERROR_MUTED,
                    border_color=Colors.ERROR,
                )
                self.label_resultado.configure(
                    text="✕  Não são equivalentes",
                    text_color=Colors.TEXT_ERROR,
                )

        except ValueError as ve:
            popup_erro(str(ve))
        except Exception as e:
            self.controller.user_logger.log_error("equivalence_check_error", str(e), "comparar_function")
            popup_erro(f"Erro ao comparar expressões: {e}")

    def on_back(self):
        # Limpa campos e resultado ao sair — comportamento preservado
        self.entrada2.delete(0, tk.END)
        self.entrada3.delete(0, tk.END)
        self.entrada2.configure(placeholder_text="Ex.: P > Q")
        self.entrada3.configure(placeholder_text="Ex.: !P | Q")
        self.resultado_frame.pack_forget()
        self.navigation.show_screen("home")
