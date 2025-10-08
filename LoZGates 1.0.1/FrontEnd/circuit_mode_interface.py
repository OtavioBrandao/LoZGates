import customtkinter as ctk
import tkinter as tk
from .design_tokens import Colors, Typography, Dimensions, Spacing, get_font, get_title_font

class CircuitModeSelector:
    def __init__(self, parent_frame: ctk.CTkFrame, circuit_manager, Button, get_global_expression_func, logger=None):
        self.parent_frame = parent_frame
        self.circuit_manager = circuit_manager
        self.Button = Button
        self.get_global_expression = get_global_expression_func  #Função para pegar expressão global
        
        self.logger = logger #adicionei para o log
        
        #Estados
        self.is_circuit_active = False
        self.current_mode = None  #Inicializa como None ao invés de 'livre'
        
        #Armazena referências dos botões de modo
        self.mode_buttons = {} 
        
        self.setup_interface()
    
    def setup_interface(self): #Configura a interface.
        self.main_container = ctk.CTkScrollableFrame(self.parent_frame, fg_color=Colors.PRIMARY_BG)
        self.main_container.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        #Título
        title_label = ctk.CTkLabel(
            self.main_container,
            text="🔌 Circuito Interativo - Escolha o Desafio",
            font=get_title_font(Typography.SIZE_TITLE_SMALL),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(pady=Spacing.MD)
        
        #Mostra expressão atual
        self.expression_display = ctk.CTkLabel(
            self.main_container,
            text="Expressão: Não definida",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        self.expression_display.pack(pady=Spacing.MD)
        
        #Atualiza expressão
        self.update_expression_display()
        
        #Frame para seleção de modos
        modes_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        modes_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
        
        modes_title = ctk.CTkLabel(
            modes_frame,
            text="Selecione o Modo de Desafio:",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        modes_title.pack(pady=Spacing.MD)
        
        #Grid de botões de modo (2 colunas)
        self.create_mode_buttons(modes_frame)
        
        #Frame de controles
        self.create_control_panel()
        
        #Panel de informações (criado mas não mostrado)
        self.create_info_panel()
        
        #Frame para o circuito (inicialmente oculto)
        self.create_circuit_area()
    
    def create_mode_buttons(self, parent): #Cria os botões de seleção de modo.
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(pady=Spacing.MD)
        
        modes = self.circuit_manager.get_all_modes()
        
        #Organiza em grid 2x3
        row, col = 0, 0
        for mode_key, mode_info in modes.items():
            #Função para capturar o mode_key corretamente
            def make_select_mode(mk):
                return lambda: self.select_mode(mk)
            
            mode_btn = ctk.CTkButton(
                button_frame,
                text=f"{mode_info['icon']} {mode_info['name']}\n{mode_info['difficulty']}",
                font=get_font(Typography.SIZE_CAPTION, Typography.WEIGHT_BOLD),
                width=Dimensions.BUTTON_WIDTH_STANDARD,
                height=70,
                fg_color=mode_info['color'],
                hover_color=self._darken_color(mode_info['color']),
                corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
                border_width=Dimensions.BORDER_WIDTH_STANDARD,
                border_color=Colors.BORDER_DEFAULT,
                command=make_select_mode(mode_key)
            )
            mode_btn.grid(row=row, column=col, padx=Spacing.SM, pady=Spacing.XS)
            
            #Armazena referência do botão
            self.mode_buttons[mode_key] = mode_btn
            
            col += 1
            if col > 1:  #2 colunas
                col = 0
                row += 1
        
        #Descrição do modo selecionado
        self.mode_description = ctk.CTkLabel(
            parent,
            text="Escolha um modo para ver detalhes",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=600
        )
        self.mode_description.pack(pady=Spacing.MD)
    
    def create_control_panel(self): #Cria o painel de controles.
        control_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        control_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
        
        buttons_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        buttons_frame.pack(pady=Spacing.MD)
        
        self.start_btn = ctk.CTkButton(
            buttons_frame,
            text="🚀 Iniciar Desafio",
            width=160,
            height=Dimensions.BUTTON_HEIGHT_STANDARD,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            fg_color=Colors.SUCCESS,
            hover_color="#45A049",
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            command=self.start_circuit
        )
        self.start_btn.pack(side="left", padx=Spacing.SM)
        
        self.stop_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹️ Parar",
            width=Dimensions.BUTTON_WIDTH_SMALL,
            height=Dimensions.BUTTON_HEIGHT_STANDARD,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            fg_color=Colors.ERROR,
            hover_color="#D32F2F",
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            state="disabled",
            command=self.stop_circuit
        )
        self.stop_btn.pack(side="left", padx=Spacing.SM)
        
        self.tips_btn = ctk.CTkButton(
            buttons_frame,
            text="💡 Dicas",
            width=Dimensions.BUTTON_WIDTH_SMALL,
            height=Dimensions.BUTTON_HEIGHT_STANDARD,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            fg_color="#070BDB",
            hover_color="#0A0D97",
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            state="disabled",
            command=self.show_tips
        )
        self.tips_btn.pack(side="left", padx=Spacing.SM)
        
        #Novo botão para controles
        self.controls_btn = ctk.CTkButton(
            buttons_frame,
            text="🎮 Controles",
            width=Dimensions.BUTTON_WIDTH_SMALL,
            height=Dimensions.BUTTON_HEIGHT_STANDARD,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            fg_color=Colors.WARNING,
            hover_color="#723B05",
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT,
            state = "disabled",
            command=self.show_controls
        )
        self.controls_btn.pack(side="left", padx=Spacing.SM)
        
        #Status
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Escolha um modo e clique em 'Iniciar Desafio'",
            font=get_font(Typography.SIZE_CAPTION),
            text_color=Colors.TEXT_SECONDARY
        )
        self.status_label.pack(pady=(0, Spacing.MD))
    
    def create_circuit_area(self):
        """Cria área para o circuito."""
        self.circuit_container = ctk.CTkFrame(
            self.main_container, 
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        #Inicialmente não empacotado
        
        expression = self.get_global_expression()
        circuit_title = ctk.CTkLabel(
            self.circuit_container,
            text=f"🎯 Monte o Circuito {expression}",
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        circuit_title.pack(pady=Spacing.MD)
        
        #Frame interno para pygame
        self.circuit_frame = tk.Frame(
            self.circuit_container,
            bg=Colors.SURFACE_DARK,
            height=600
        )
        self.circuit_frame.pack(fill="both", expand=True, padx=Spacing.SM, pady=(0, Spacing.SM))
    
    def create_info_panel(self): #Cria painel de informações.
        self.info_container = ctk.CTkFrame(
            self.main_container, 
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        #Inicialmente não empacotado
        
        info_title = ctk.CTkLabel(
            self.info_container,
            text="ℹ️ Informações",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        info_title.pack(pady=Spacing.MD)
        
        self.info_text = ctk.CTkTextbox(
            self.info_container,
            height=400,
            font=get_font(Typography.SIZE_CAPTION),
            fg_color=Colors.SURFACE_DARK,
            text_color=Colors.TEXT_SECONDARY
        )
        self.info_text.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
    
    def update_expression_display(self): #Atualiza a exibição da expressão atual.
        expression = self.get_global_expression()
        if expression:
            self.expression_display.configure(
                text=f"Expressão: {expression}",
                text_color=Colors.TEXT_ACCENT
            )
        else:
            self.expression_display.configure(
                text="⚠️ Nenhuma expressão definida - Vá para a tela principal primeiro",
                text_color=Colors.WARNING
            )
    
    def update_mode_buttons_state(self): #Atualiza o estado dos botões de modo baseado no status do circuito.
        for mode_key, button in self.mode_buttons.items():
            if self.is_circuit_active:
                #Desabilita todos os botões exceto o selecionado
                if mode_key == self.current_mode:
                    button.configure(state="normal")
                else:
                    button.configure(state="disabled")
            else:
                #Reabilita todos os botões
                button.configure(state="normal")
    
    def select_mode(self, mode_key: str): #Seleciona um modo.
        #Só permite trocar de modo se o circuito não estiver ativo
        if self.is_circuit_active and mode_key != self.current_mode:
            self.status_label.configure(
                text="⚠️ Pare o circuito antes de trocar de modo",
                text_color=Colors.WARNING
            )
            return
        
        self.current_mode = mode_key
        self.circuit_manager.set_mode(mode_key)
        mode_info = self.circuit_manager.get_mode_info(mode_key)
        
        #Atualiza descrição
        desc_text = f"🎯 {mode_info['name']} - {mode_info['difficulty']}\n"
        desc_text += f"📝 {mode_info['description']}\n"
        
        if mode_info['restrictions']:
            desc_text += f"🔒 Portas permitidas: {', '.join(mode_info['restrictions']).upper()}"
        else:
            desc_text += f"🔓 Use qualquer porta lógica"
        
        self.mode_description.configure(text=desc_text)
        
        #Atualiza estado dos botões
        self.update_mode_buttons_state()
        
        #Atualiza status
        expression = self.get_global_expression()
        if expression:
            if self.is_circuit_active:
                self.status_label.configure(
                    text=f"Status: Desafio ativo - {mode_info['name']} | Pressione ESPAÇO para testar",
                    text_color=Colors.TEXT_ACCENT
                )
            else:
                self.status_label.configure(
                    text=f"Modo selecionado: {mode_info['name']} | Pronto para iniciar!",
                    text_color=Colors.SUCCESS
                )
        else:
            self.status_label.configure(
                text="⚠️ Defina uma expressão na tela principal primeiro",
                text_color=Colors.WARNING
            )
    
    def start_circuit(self): #Inicia o circuito interativo.
        expression = self.get_global_expression()
        
        if not expression:
            self.status_label.configure(
                text="❌ Erro: Defina uma expressão na tela principal primeiro",
                text_color=Colors.ERROR
            )
            return
        
        if self.current_mode is None:
            self.status_label.configure(
                text="⚠️ Selecione um modo de desafio primeiro",
                text_color=Colors.WARNING
            )
            return
        
        try:
            # LOG DO MODO SELECIONADO
            if self.logger:
                self.logger.log_event("circuit_mode_selected", {
                    "mode": self.current_mode,
                    "expression": expression[:30],
                    "restrictions": self.circuit_manager.get_mode_info(self.current_mode).get('restrictions')
                })
            
            self.circuit_container.pack(fill="both", expand=True, pady=Spacing.MD, padx=Spacing.LG)
            
            circuit = self.circuit_manager.create_circuit(self.circuit_frame, expression, logger=self.logger)

            #Atualiza estados
            self.is_circuit_active = True
            
            #Atualiza botões
            self.start_btn.configure(state="disabled")
            self.tips_btn.configure(state="normal")
            self.stop_btn.configure(state="normal")
            self.controls_btn.configure(state="normal")
            
            #Atualiza estado dos botões de modo
            self.update_mode_buttons_state()
            
            #Status simplificado
            mode_info = self.circuit_manager.get_mode_info(self.current_mode)
            status_text = f"Status: Desafio ativo - {mode_info['name']} | Pressione ESPAÇO para testar"
            
            self.status_label.configure(
                text=status_text,
                text_color=Colors.TEXT_ACCENT
            )
            
            print(f"✅ Circuito iniciado - Expressão: {expression} | Modo: {mode_info['name']}")
            
        except Exception as e:
            #Reverte estado em caso de erro
            self.is_circuit_active = False
            self.update_mode_buttons_state()
            
            self.status_label.configure(
                text=f"❌ Erro ao iniciar: {str(e)}",
                text_color=Colors.ERROR
            )
            print(f"❌ Erro: {e}")
    
    def stop_circuit(self): #Para o circuito.
        try:
            self.circuit_manager.stop_current_circuit()
            
            #Esconde área do circuito
            self.circuit_container.pack_forget()

            #Esconde painel de informações
            self.info_container.pack_forget()
            self.info_text.configure(state="normal")
            self.info_text.delete("1.0", "end")
            
            #Atualiza estados
            self.is_circuit_active = False
            
            #Atualiza botões
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.tips_btn.configure(state="disabled")
            self.controls_btn.configure(state="disabled")
            
            #Reabilita todos os botões de modo
            self.update_mode_buttons_state()
            
            self.status_label.configure(
                text="⏹️ Circuito parado - Selecione um modo para reiniciar",
                text_color=Colors.WARNING
            )
            
        except Exception as e:
            print(f"Erro ao parar circuito: {e}")
    
    def show_tips(self): #Mostra dicas específicas do modo.
        if self.logger and self.current_mode:
            self.logger.log_event("circuit_tips_viewed", {
                "mode": self.current_mode,
                "circuit_active": self.is_circuit_active
            })
        
        #Mostra painel se não estiver visível
        if not self.info_container.winfo_ismapped():
            self.info_container.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD, before=self.circuit_container)
        
        if self.current_mode is None:
            tips_text = "Primeiro selecione um modo de desafio para ver dicas específicas."
        else:
            mode_info = self.circuit_manager.get_mode_info(self.current_mode)
            tips = self.circuit_manager.get_mode_tips(self.current_mode)
            
            tips_text = f"💡 DICAS - {mode_info['name']} ({mode_info['difficulty']})\n\n"
            
            for i, tip in enumerate(tips, 1):
                tips_text += f"  {i}. {tip}\n\n"
        
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", tips_text)
        self.info_text.configure(state="disabled")
    
    def show_controls(self): #Mostra informações de controle do jogo.
        #Mostra painel se não estiver visível
        if not self.info_container.winfo_ismapped():
            self.info_container.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD, before=self.circuit_container)
        
        controls_text = "🎮 CONTROLES BÁSICOS:\n\n"
        controls_text += "  • TAB: Mostrar/esconder painel de componentes\n"
        controls_text += "  • Espaço: Testar circuito\n"
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
        controls_text += "  6. Pressione ESPAÇO para testar!\n"
        controls_text += "  7. Implemente a expressão corretamente!"
        
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", controls_text)
        self.info_text.configure(state="disabled")
    
    def cleanup(self): #Limpa recursos.
        if self.is_circuit_active:
            self.stop_circuit()
    
    def _darken_color(self, hex_color: str) -> str: #Escurece cor para hover.
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, int(c * 0.7)) for c in rgb)
        return f"#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}"