import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import threading
from BackEnd.ai_assistant import AIAssistant
from config import make_window_visible_robust

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
        self.popup.geometry("500x600")
        self.popup.resizable(True, True)
        
        # Centralizar popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (250)
        y = (self.popup.winfo_screenheight() // 2) - (300)
        self.popup.geometry(f"500x600+{x}+{y}")
        
        self.setup_ui()
        self.popup.focus()
        
        # Solicitar sugestão inicial automaticamente
        if expression:
            self.get_initial_suggestion()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.popup)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Assistente de IA para Lógica Proposicional",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Expressão atual
        if self.expression:
            expr_label = ctk.CTkLabel(
                main_frame,
                text=f"Expressão: {self.expression}",
                font=ctk.CTkFont(size=12),
                wraplength=450
            )
            expr_label.pack(pady=(0, 10))
        
        # Área de chat
        self.chat_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        self.chat_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame de entrada
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", padx=5, pady=(5, 10))
        
        # Campo de entrada
        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Digite sua pergunta sobre a simplificação..."
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        # Botão enviar
        send_button = ctk.CTkButton(
            input_frame,
            text="Enviar",
            width=80,
            command=self.send_message
        )
        send_button.pack(side="right", padx=(5, 10), pady=10)
        
        # Botões de ação rápida
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", padx=5, pady=(0, 10))
        
        suggest_button = ctk.CTkButton(
            action_frame,
            text="Nova Sugestão",
            command=self.get_suggestion,
            width=120
        )
        suggest_button.pack(side="left", padx=10, pady=5)
        
        explain_button = ctk.CTkButton(
            action_frame,
            text="Explicar Leis",
            command=self.explain_laws,
            width=120
        )
        explain_button.pack(side="left", padx=5, pady=5)
        
        close_button = ctk.CTkButton(
            action_frame,
            text="Fechar",
            command=self.popup.destroy,
            width=80
        )
        close_button.pack(side="right", padx=10, pady=5)
        
        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self.send_message())
    
    def add_message(self, sender, message, is_error=False):
        message_frame = ctk.CTkFrame(self.chat_frame)
        message_frame.pack(fill="x", padx=5, pady=2)
        
        # Cor baseada no remetente
        if sender == "Você":
            bg_color = "#2b2b2b"
        elif is_error:
            bg_color = "#4a1a1a"
        else:
            bg_color = "#1a3a1a"
        
        message_frame.configure(fg_color=bg_color)
        
        # Label do remetente
        sender_label = ctk.CTkLabel(
            message_frame,
            text=f"{sender}:",
            font=ctk.CTkFont(weight="bold", size=11)
        )
        sender_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Mensagem
        msg_label = ctk.CTkLabel(
            message_frame,
            text=message,
            wraplength=450,
            justify="left",
            font=ctk.CTkFont(size=11)
        )
        msg_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Scroll para baixo
        self.popup.after(100, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        try:
            self.chat_frame._parent_canvas.yview_moveto(1.0)
        except:
            pass
    
    def send_message(self):
        message = self.entry.get().strip()
        if not message:
            return
        
        self.add_message("Você", message)
        self.entry.delete(0, "end")
        
        # Mostrar indicador de carregamento
        loading_frame = ctk.CTkFrame(self.chat_frame)
        loading_frame.pack(fill="x", padx=5, pady=2)
        loading_frame.configure(fg_color="#1a3a1a")
        
        loading_label = ctk.CTkLabel(
            loading_frame,
            text="IA está pensando...",
            font=ctk.CTkFont(slant="italic")
        )
        loading_label.pack(padx=10, pady=5)
        
        def callback(response, error):
            loading_frame.destroy()
            
            if error:
                self.add_message("IA", f"Erro: {error}", is_error=True)
            else:
                self.add_message("IA", response or "Desculpe, não consegui gerar uma resposta.")
        
        self.ai_assistant.ask_question(message, self.expression, callback)
    
    def get_suggestion(self):
        if not self.expression:
            self.add_message("Sistema", "Nenhuma expressão disponível para análise.", is_error=True)
            return
        
        self.add_message("Você", "Solicitar nova sugestão")
        
        # Indicador de carregamento
        loading_frame = ctk.CTkFrame(self.chat_frame)
        loading_frame.pack(fill="x", padx=5, pady=2)
        loading_frame.configure(fg_color="#1a3a1a")
        
        loading_label = ctk.CTkLabel(
            loading_frame,
            text="IA analisando expressão...",
            font=ctk.CTkFont(slant="italic")
        )
        loading_label.pack(padx=10, pady=5)
        
        def callback(response, error):
            loading_frame.destroy()
            
            if error:
                self.add_message("IA", f"Erro: {error}", is_error=True)
            else:
                self.add_message("IA", response or "Não consegui gerar uma sugestão específica.")
        
        self.ai_assistant.get_ai_suggestion(self.expression, self.step_context, callback)
    
    def get_initial_suggestion(self):
        def callback(response, error):
            if error:
                self.add_message("IA", f"Erro ao conectar: {error}", is_error=True)
            else:
                welcome_msg = f"Olá! Vou ajudar você a simplificar a expressão: {self.expression}"
                self.add_message("IA", welcome_msg)
                if response:
                    self.add_message("IA", response)
        
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