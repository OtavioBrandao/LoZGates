import customtkinter as ctk
import tkinter as tk
from BackEnd.ai_assistant import AIAssistant
from config import make_window_visible_robust
from FrontEnd.utils.responsive import calculate_window_layout
from FrontEnd.styles.design_tokens import Colors, Typography, Dimensions, Spacing, get_font, get_title_font

class AIChatPopup:
    def __init__(self, parent, expression="", step_context=""):
        self.parent = parent
        self.expression = expression
        self.step_context = step_context
        self.ai_assistant = AIAssistant()
        
        # Criar popup
        self.popup = ctk.CTkToplevel(parent)
        make_window_visible_robust(self.popup, parent=parent)
        self.popup.title("Sugestão de IA - Simplificador Lógico")
        layout = calculate_window_layout(
            self.popup.winfo_screenwidth(),
            self.popup.winfo_screenheight(),
            preferred=(560, 640),
            minimum=(360, 480),
            margin=24,
        )
        self.popup.geometry(layout.geometry)
        self.popup.minsize(layout.minimum_width, layout.minimum_height)
        self.popup.resizable(True, True)
        
        self.setup_ui()
        self.popup.focus()
        
        # Solicitar sugestão inicial automaticamente
        if expression:
            self.get_initial_suggestion()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.popup, fg_color=Colors.PRIMARY_BG)
        main_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Assistente de IA para Lógica Proposicional",
            font=get_title_font(Typography.SIZE_TITLE_SMALL),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(pady=(Spacing.MD, Spacing.SM))
        
        # Expressão atual
        if self.expression:
            expr_label = ctk.CTkLabel(
                main_frame,
                text=f"Expressão: {self.expression}",
                font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
                text_color=Colors.TEXT_CODE,
                wraplength=450
            )
            expr_label.pack(pady=(0, Spacing.MD))
        
        # Área de chat
        self.chat_frame = ctk.CTkScrollableFrame(main_frame, height=350, fg_color=Colors.SURFACE_DARK)
        self.chat_frame.pack(fill="both", expand=True, padx=Spacing.XS, pady=Spacing.XS)
        
        # Frame de entrada
        input_frame = ctk.CTkFrame(main_frame, fg_color=Colors.SURFACE_MEDIUM)
        input_frame.pack(fill="x", padx=Spacing.XS, pady=(Spacing.XS, Spacing.MD))
        
        # Campo de entrada
        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Digite sua pergunta sobre a simplificação...",
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY,
            fg_color=Colors.SURFACE_LIGHT,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(Spacing.MD, Spacing.XS), pady=Spacing.MD)
        
        # Botão enviar
        from FrontEnd.components.buttons import Button
        
        send_button = Button.botao_primario(
            "Enviar",
            input_frame,
        )
        send_button.configure(command=self.send_message, width=80)
        send_button.pack(side="right", padx=(Spacing.XS, Spacing.MD), pady=Spacing.MD)
        
        # Botões de ação rápida
        action_frame = ctk.CTkFrame(main_frame, fg_color=Colors.PRIMARY_BG)
        action_frame.pack(fill="x", padx=Spacing.XS, pady=(0, Spacing.MD))
        
        suggest_button = Button.botao_secundario(
            "Nova Sugestão",
            action_frame
        )
        suggest_button.configure(command=self.get_suggestion, width=120)
        suggest_button.pack(side="left", padx=Spacing.MD, pady=Spacing.XS)
        
        explain_button = Button.botao_secundario(
            "Explicar Leis",
            action_frame
        )
        explain_button.configure(command=self.explain_laws, width=120)
        explain_button.pack(side="left", padx=Spacing.XS, pady=Spacing.XS)
        
        close_button = Button.botao_secundario(
            "Fechar",
            action_frame
        )
        close_button.configure(command=self.popup.destroy, width=80)
        close_button.pack(side="right", padx=Spacing.MD, pady=Spacing.XS)
        
        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self.send_message())
    
    def add_message(self, sender, message, is_error=False):
        message_frame = ctk.CTkFrame(self.chat_frame, corner_radius=Dimensions.CORNER_RADIUS_MEDIUM)
        message_frame.pack(fill="x", padx=Spacing.XS, pady=2)
        
        # Cor baseada no remetente
        if sender == "Você":
            bg_color = Colors.SURFACE_LIGHT
        elif is_error:
            bg_color = Colors.ERROR_MUTED
        else:
            bg_color = Colors.SURFACE_MEDIUM
        
        message_frame.configure(fg_color=bg_color)
        
        # Label do remetente
        sender_label = ctk.CTkLabel(
            message_frame,
            text=f"{sender}:",
            font=get_font(Typography.SIZE_CAPTION, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT if sender != "Você" and not is_error else (Colors.TEXT_ERROR if is_error else Colors.TEXT_SECONDARY)
        )
        sender_label.pack(anchor="w", padx=Spacing.MD, pady=(Spacing.SM, 0))
        
        # Mensagem
        msg_label = ctk.CTkLabel(
            message_frame,
            text=message,
            wraplength=450,
            justify="left",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_PRIMARY
        )
        msg_label.pack(anchor="w", padx=Spacing.MD, pady=(0, Spacing.SM))
        
        # Scroll para baixo
        self.popup.after(100, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        try:
            self.chat_frame._parent_canvas.yview_moveto(1.0)
        except (AttributeError, tk.TclError):
            pass

    def _run_on_ui_thread(self, callback):
        """Marshal worker-thread results back to Tk's event loop."""
        try:
            if self.popup.winfo_exists():
                self.popup.after(0, callback)
        except tk.TclError:
            pass

    def _show_ai_result(self, loading_frame, response, error, fallback):
        try:
            if loading_frame is not None and loading_frame.winfo_exists():
                loading_frame.destroy()
        except tk.TclError:
            return

        if error:
            self.add_message("IA", f"Erro: {error}", is_error=True)
        else:
            self.add_message("IA", response or fallback)
    
    def send_message(self):
        message = self.entry.get().strip()
        if not message:
            return
        
        self.add_message("Você", message)
        self.entry.delete(0, "end")
        
        # Mostrar indicador de carregamento
        loading_frame = ctk.CTkFrame(self.chat_frame, corner_radius=Dimensions.CORNER_RADIUS_MEDIUM)
        loading_frame.pack(fill="x", padx=Spacing.XS, pady=2)
        loading_frame.configure(fg_color=Colors.SURFACE_MEDIUM)
        
        loading_label = ctk.CTkLabel(
            loading_frame,
            text="IA está pensando...",
            font=get_font(Typography.SIZE_CAPTION, italic=True),
            text_color=Colors.TEXT_MUTED
        )
        loading_label.pack(padx=Spacing.MD, pady=Spacing.SM)
        
        def callback(response, error):
            self._run_on_ui_thread(
                lambda: self._show_ai_result(
                    loading_frame,
                    response,
                    error,
                    "Desculpe, não consegui gerar uma resposta.",
                )
            )
        
        self.ai_assistant.ask_question(message, self.expression, callback)
    
    def get_suggestion(self):
        if not self.expression:
            self.add_message("Sistema", "Nenhuma expressão disponível para análise.", is_error=True)
            return
        
        self.add_message("Você", "Solicitar nova sugestão")
        
        # Indicador de carregamento
        loading_frame = ctk.CTkFrame(self.chat_frame, corner_radius=Dimensions.CORNER_RADIUS_MEDIUM)
        loading_frame.pack(fill="x", padx=Spacing.XS, pady=2)
        loading_frame.configure(fg_color=Colors.SURFACE_MEDIUM)
        
        loading_label = ctk.CTkLabel(
            loading_frame,
            text="IA analisando expressão...",
            font=get_font(Typography.SIZE_CAPTION, italic=True),
            text_color=Colors.TEXT_MUTED
        )
        loading_label.pack(padx=Spacing.MD, pady=Spacing.SM)
        
        def callback(response, error):
            self._run_on_ui_thread(
                lambda: self._show_ai_result(
                    loading_frame,
                    response,
                    error,
                    "Não consegui gerar uma sugestão específica.",
                )
            )
        
        self.ai_assistant.get_ai_suggestion(self.expression, self.step_context, callback)
    
    def get_initial_suggestion(self):
        def callback(response, error):
            def show_result():
                if error:
                    self.add_message("IA", f"Erro ao conectar: {error}", is_error=True)
                else:
                    welcome_msg = (
                        "Olá! Vou ajudar você a simplificar a expressão: "
                        f"{self.expression}"
                    )
                    self.add_message("IA", welcome_msg)
                    if response:
                        self.add_message("IA", response)

            self._run_on_ui_thread(show_result)
        
        self.ai_assistant.get_ai_suggestion(self.expression, self.step_context, callback)
    
    def explain_laws(self):
        self.add_message("Você", "Explicar leis da lógica")
        
        explanation = """Principais leis da lógica proposicional:

• De Morgan: ~(A∧B) = ~A∨~B e ~(A∨B) = ~A∧~B
• Distributiva: A∧(B∨C) = (A∧B)∨(A∧C)
• Absorção: A∧(A∨B) = A e A∨(A∧B) = A  
• Identidade: A∧1 = A e A∨0 = A
• Nula: A∧0 = 0 e A∨1 = 1
• Inversa: A∧~A = 0 e A∨~A = 1
• Idempotente: A∧A = A e A∨A = A

Use essas leis para simplificar sua expressão passo a passo!"""
        
        self.add_message("IA", explanation)
