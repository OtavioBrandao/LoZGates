"""
    Interface para circuito interativo.
"""

import customtkinter as ctk
import tkinter as tk

class CircuitModeSelector:
    """Seletor de modos."""
    
    def __init__(self, parent_frame: ctk.CTkFrame, circuit_manager, Button, get_global_expression_func):
        self.parent_frame = parent_frame
        self.circuit_manager = circuit_manager
        self.Button = Button
        self.get_global_expression = get_global_expression_func  #Função para pegar expressão global
        
        #Estados
        self.is_circuit_active = False
        self.current_mode = None  #Inicializa como None ao invés de 'livre'
        
        self.setup_interface()
    
    def setup_interface(self):
        """Configura a interface."""
        #Container principal
        self.main_container = ctk.CTkScrollableFrame(self.parent_frame, fg_color="#082347")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        #Título
        title_label = ctk.CTkLabel(
            self.main_container,
            text="🔌 Circuito Interativo - Escolha o Desafio",
            font=("Trebuchet MS", 20, "bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=15)
        
        #Mostra expressão atual
        self.expression_display = ctk.CTkLabel(
            self.main_container,
            text="Expressão: Não definida",
            font=("Trebuchet MS", 16, "bold"),
            text_color="#00FFFF"
        )
        self.expression_display.pack(pady=10)
        
        #Atualiza expressão
        self.update_expression_display()
        
        #Frame para seleção de modos
        modes_frame = ctk.CTkFrame(self.main_container, fg_color="#001E44")
        modes_frame.pack(fill="x", padx=20, pady=20)
        
        modes_title = ctk.CTkLabel(
            modes_frame,
            text="Selecione o Modo de Desafio:",
            font=("Trebuchet MS", 16, "bold"),
            text_color="#FFFFFF"
        )
        modes_title.pack(pady=15)
        
        #Grid de botões de modo (2 colunas)
        self.create_mode_buttons(modes_frame)
        
        #Frame de controles
        self.create_control_panel()
        
        #Frame para o circuito (inicialmente oculto)
        self.create_circuit_area()
        
        #Panel de informações
        self.create_info_panel()
    
    def create_mode_buttons(self, parent):
        """Cria os botões de seleção de modo."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(pady=15)
        
        modes = self.circuit_manager.get_all_modes()
        
        #Organiza em grid 2x3
        row, col = 0, 0
        for mode_key, mode_info in modes.items():
            mode_btn = ctk.CTkButton(
                button_frame,
                text=f"{mode_info['icon']} {mode_info['name']}\n{mode_info['difficulty']}",
                font=("Trebuchet MS", 12, "bold"),
                width=200,
                height=70,
                fg_color=mode_info['color'],
                hover_color=self._darken_color(mode_info['color']),
                command=lambda mk=mode_key: self.select_mode(mk)
            )
            mode_btn.grid(row=row, column=col, padx=10, pady=8)
            
            col += 1
            if col > 1:  #2 colunas
                col = 0
                row += 1
        
        #Descrição do modo selecionado
        self.mode_description = ctk.CTkLabel(
            parent,
            text="Escolha um modo para ver detalhes",
            font=("Trebuchet MS", 14),
            text_color="#CCCCCC",
            wraplength=600
        )
        self.mode_description.pack(pady=15)
    
    def create_control_panel(self):
        """Cria o painel de controles."""
        control_frame = ctk.CTkFrame(self.main_container, fg_color="#001E44")
        control_frame.pack(fill="x", padx=20, pady=10)
        
        buttons_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        buttons_frame.pack(pady=15)
        
        self.start_btn = ctk.CTkButton(
            buttons_frame,
            text="🚀 Iniciar Desafio",
            width=160,
            height=50,
            font=("Trebuchet MS", 16, "bold"),
            fg_color="#2D5A27",
            hover_color="#1A3D18",
            command=self.start_circuit
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹️ Parar",
            width=120,
            height=50,
            font=("Trebuchet MS", 16, "bold"),
            fg_color="#7A2020",
            hover_color="#5A1818",
            state="disabled",
            command=self.stop_circuit
        )
        self.stop_btn.pack(side="left", padx=10)
        
        self.tips_btn = ctk.CTkButton(
            buttons_frame,
            text="💡 Dicas",
            width=120,
            height=50,
            font=("Trebuchet MS", 16, "bold"),
            fg_color="#4A597C",
            hover_color="#364268",
            command=self.show_tips
        )
        self.tips_btn.pack(side="left", padx=10)
        
        #Novo botão para controles
        self.controls_btn = ctk.CTkButton(
            buttons_frame,
            text="🎮 Controles",
            width=120,
            height=50,
            font=("Trebuchet MS", 16, "bold"),
            fg_color="#2D5A5A",
            hover_color="#1A3535",
            command=self.show_controls
        )
        self.controls_btn.pack(side="left", padx=10)
        
        #Status
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Escolha um modo e clique em 'Iniciar Desafio'",
            font=("Trebuchet MS", 12),
            text_color="#CCCCCC"
        )
        self.status_label.pack(pady=(0, 15))
    
    def create_circuit_area(self):
        """Cria área para o circuito."""
        self.circuit_container = ctk.CTkFrame(self.main_container, fg_color="#000000")
        #Inicialmente não empacotado
        
        expression = self.get_global_expression()
        circuit_title = ctk.CTkLabel(
            self.circuit_container,
            text=f"🎯 Monte o Circuito {expression}",
            font=("Trebuchet MS", 18, "bold"),
            text_color="#FFFFFF"
        )
        circuit_title.pack(pady=10)
        
        #Frame interno para pygame
        self.circuit_frame = tk.Frame(
            self.circuit_container,
            bg="#000000",
            height=600
        )
        self.circuit_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def create_info_panel(self):
        """Cria painel de informações."""
        self.info_container = ctk.CTkFrame(self.main_container, fg_color="#00002C")
        #Inicialmente não empacotado
        
        info_title = ctk.CTkLabel(
            self.info_container,
            text="ℹ️ Informações",
            font=("Trebuchet MS", 16, "bold"),
            text_color="#FFFFFF"
        )
        info_title.pack(pady=15)
        
        self.info_text = ctk.CTkTextbox(
            self.info_container,
            height=200,
            font=("Trebuchet MS", 12),
            fg_color="#001122",
            text_color="#CCCCCC"
        )
        self.info_text.pack(fill="x", padx=15, pady=(0, 15))
    
    def update_expression_display(self):
        """Atualiza a exibição da expressão atual."""
        expression = self.get_global_expression()
        if expression:
            self.expression_display.configure(
                text=f"Expressão: {expression}",
                text_color="#00FFFF"
            )
        else:
            self.expression_display.configure(
                text="⚠️ Nenhuma expressão definida - Vá para a tela principal primeiro",
                text_color="#FF6600"
            )
    
    def select_mode(self, mode_key: str):
        """Seleciona um modo."""
        self.current_mode = mode_key
        self.circuit_manager.set_mode(mode_key)
        mode_info = self.circuit_manager.get_mode_info(mode_key)
        
        #Atualiza descrição
        desc_text = f"🎯 {mode_info['name']} - {mode_info['difficulty']}\n"
        desc_text += f"📝 {mode_info['description']}\n"
        
        if mode_info['restrictions']:
            desc_text += f"🔒 Portas permitidas: {', '.join(mode_info['restrictions']).upper()}"
        else:
            desc_text += f"📗 Use qualquer porta lógica"
        
        self.mode_description.configure(text=desc_text)
        
        #Atualiza status
        expression = self.get_global_expression()
        if expression:
            self.status_label.configure(
                text=f"Modo selecionado: {mode_info['name']} | Pronto para iniciar!",
                text_color="#00FF00"
            )
        else:
            self.status_label.configure(
                text="⚠️ Defina uma expressão na tela principal primeiro",
                text_color="#FF6600"
            )
    
    def start_circuit(self):
        """Inicia o circuito interativo."""
        expression = self.get_global_expression()
        
        if not expression:
            self.status_label.configure(
                text="❌ Erro: Defina uma expressão na tela principal primeiro",
                text_color="#FF0000"
            )
            return
        
        #Verifica se um modo foi selecionado
        if self.current_mode is None:
            self.status_label.configure(
                text="⚠️ Selecione um modo de desafio primeiro",
                text_color="#FF6600"
            )
            return
        
        try:
            #Mostra área do circuito
            self.circuit_container.pack(fill="both", expand=True, pady=10, padx=20)
            
            #Cria circuito com validação melhorada
            circuit = self.circuit_manager.create_circuit(self.circuit_frame, expression)
            
            #Atualiza botões
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.is_circuit_active = True
            
            #Status simplificado
            mode_info = self.circuit_manager.get_mode_info(self.current_mode)
            status_text = f"Status: Desafio ativo - {mode_info['name']}"
            if mode_info['restrictions']:
                status_text += f" | Limitado a: {', '.join(mode_info['restrictions']).upper()}"
            
            self.status_label.configure(
                text=status_text,
                text_color="#00FFFF"
            )
            
            print(f"✅ Circuito iniciado - Expressão: {expression} | Modo: {mode_info['name']}")
            
        except Exception as e:
            self.status_label.configure(
                text=f"❌ Erro ao iniciar: {str(e)}",
                text_color="#FF0000"
            )
            print(f"❌ Erro: {e}")
    
    def stop_circuit(self):
        """Para o circuito."""
        try:
            self.circuit_manager.stop_current_circuit()
            
            #Esconde área do circuito
            self.circuit_container.pack_forget()
            
            #Atualiza botões
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.is_circuit_active = False
            
            self.status_label.configure(
                text="⏹️ Circuito parado - Selecione um modo para reiniciar",
                text_color="#FFFF00"
            )
            
        except Exception as e:
            print(f"Erro ao parar circuito: {e}")
    
    def show_tips(self):
        """Mostra dicas específicas do modo."""
        if self.current_mode is None:
            tips_text = "Primeiro selecione um modo de desafio para ver dicas específicas."
        else:
            #Mostra painel se não estiver visível
            if not self.info_container.winfo_ismapped():
                self.info_container.pack(fill="x", padx=20, pady=10)
            
            mode_info = self.circuit_manager.get_mode_info(self.current_mode)
            tips = self.circuit_manager.get_mode_tips(self.current_mode)
            
            tips_text = f"💡 DICAS - {mode_info['name']} ({mode_info['difficulty']})\n\n"
            
            for i, tip in enumerate(tips, 1):
                tips_text += f"  {i}. {tip}\n\n"
            
            #Remove as informações de controle básico das dicas
            
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", tips_text)
        
        if not self.info_container.winfo_ismapped():
            self.info_container.pack(fill="x", padx=20, pady=10)
    
    def show_controls(self):
        """Mostra informações de controle do jogo."""
        #Mostra painel se não estiver visível
        if not self.info_container.winfo_ismapped():
            self.info_container.pack(fill="x", padx=20, pady=10)
        
        controls_text = "🎮 CONTROLES BÁSICOS:\n\n"
        controls_text += "  • TAB: Mostrar/esconder painel de componentes\n"
        controls_text += "  • Clique: Selecionar componente\n" 
        controls_text += "  • Arrastar: Mover componente\n"
        controls_text += "  • Bolinhas verdes: Pontos de conexão\n"
        controls_text += "  • Delete: Remover selecionado\n"
        controls_text += "  • WASD: Mover câmera\n"
        controls_text += "  • Scroll: Zoom\n"
        controls_text += "  • Ctrl+Z/Y: Desfazer/Refazer\n"
        controls_text += "  • Esc: Cancela conexão\n"
        controls_text += "  • R: Reset vista\n\n"
        controls_text += "📋 COMO JOGAR:\n\n"
        controls_text += "  1. Selecione um modo de desafio\n"
        controls_text += "  2. Clique em 'Iniciar Desafio'\n"
        controls_text += "  3. Use TAB para abrir o painel\n"
        controls_text += "  4. Adicione componentes clicando no painel\n"
        controls_text += "  5. Conecte os pontos verdes\n"
        controls_text += "  6. Implemente a expressão corretamente!"
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", controls_text)
    
    def cleanup(self):
        """Limpa recursos."""
        if self.is_circuit_active:
            self.stop_circuit()
    
    def _darken_color(self, hex_color: str) -> str:
        """Escurece cor para hover."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, int(c * 0.7)) for c in rgb)
        return f"#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}"