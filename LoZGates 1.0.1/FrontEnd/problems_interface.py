# Interface de problemas do mundo real - UI/UX padronizada
# Atualizado com design tokens e componentes unificados

import customtkinter as ctk
from BackEnd.problems_bank import Problems_bank, ProblemsToFrame
from .design_tokens import Colors, Typography, Dimensions, Spacing, get_font, get_title_font

class IntegratedProblemsInterface:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.problems_handler = ProblemsToFrame(Problems_bank)
        self.current_frame = None
    
    def create_problems_main_screen(self, scroll_problemas_reais, voltar_para, principal):
        """Cria a tela principal com a lista de problemas"""
        
        header_frame = ctk.CTkFrame(scroll_problemas_reais, fg_color="transparent")
        header_frame.pack(pady=Spacing.LG, padx=Spacing.LG, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🔬 Problemas do Mundo Real", 
            font=get_title_font(Typography.SIZE_TITLE_LARGE), 
            text_color=Colors.ACCENT_CYAN
        )
        title_label.pack(pady=(0, Spacing.SM))
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Explore problemas reais que podem ser resolvidos com circuitos lógicos e lógica proposicional",
            font=get_font(Typography.SIZE_BODY), 
            text_color=Colors.TEXT_SECONDARY,
            wraplength=700
        )
        subtitle_label.pack(pady=(0, Spacing.LG))
        
        # Container principal com borda estilizada
        main_container = ctk.CTkFrame(
            scroll_problemas_reais, 
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_ACCENT
        )
        main_container.pack(pady=Spacing.LG, padx=Spacing.XXL, fill="both", expand=True)
        
        # Frame interno para os problemas
        problems_frame = ctk.CTkScrollableFrame(
            main_container, 
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=400,
            width=850
        )
        problems_frame.pack(padx=Spacing.MD, pady=Spacing.MD, fill="both", expand=True)
        
        # Configurar grid para responsividade
        for i in range(4):  # 4 colunas
            problems_frame.grid_columnconfigure(i, weight=1)
        
        # Criar botões dos problemas
        self.create_problem_buttons(problems_frame, scroll_problemas_reais, voltar_para, principal)
        
        # Botão voltar estilizado
        back_button = ctk.CTkButton(
            scroll_problemas_reais,
            text="← Voltar ao Menu Principal",
            command=lambda: voltar_para(principal),
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            fg_color=Colors.ACCENT_GOLD,
            text_color=Colors.BUTTON_TEXT,
            border_color=Colors.BORDER_DEFAULT,
            hover_color=Colors.ACCENT_GOLD_HOVER,
            corner_radius=Dimensions.CORNER_RADIUS_LARGE,
            height=Dimensions.BUTTON_HEIGHT_STANDARD,
            width=Dimensions.BUTTON_WIDTH_LARGE,
            border_width=Dimensions.BORDER_WIDTH_STANDARD
        )
        back_button.pack(pady=Spacing.XXL)
    
    def create_problem_buttons(self, container, scroll_problemas_reais, voltar_para, principal):
        """Cria os botões para cada problema"""
        
        # Dicionário de cores para diferentes dificuldades
        difficulty_colors = {
            "Fácil": (Colors.SUCCESS, "#09BB62"  ),
            "Médio": (Colors.WARNING, "#F38D08"),
            "Difícil": (Colors.ERROR, "#D32F2F"),
            "Supremo":(Colors.HEHEHE, "#B019AB")
        }
        
        for idx, problem in enumerate(Problems_bank):
            # Determinar cor baseada na dificuldade
            difficulty = getattr(problem, 'difficulty', 'Fácil')
            fg_color, hover_color = difficulty_colors.get(difficulty, difficulty_colors["Fácil"])
            
            # Criar botão personalizado para cada problema
            problem_button = ctk.CTkButton(
                container,
                text=f"{problem.name}\n({difficulty})",
                command=lambda i=idx: self.show_problem_detail(i, scroll_problemas_reais, voltar_para, principal),
                font=get_font(Typography.SIZE_CAPTION, Typography.WEIGHT_BOLD),
                fg_color=fg_color,
                hover_color=hover_color,
                corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
                height=80,
                width=180,
                text_color=Colors.TEXT_PRIMARY,
                border_width=Dimensions.BORDER_WIDTH_STANDARD,
                border_color=Colors.BORDER_DEFAULT
            )
            
            # Posicionar no grid (4 colunas)
            row = idx // 4
            col = idx % 4
            problem_button.grid(row=row, column=col, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
    
    def show_problem_detail(self, problem_index, parent_container, voltar_para, principal):
        """Mostra os detalhes de um problema específico"""
        
        # Limpar o container atual
        for widget in parent_container.winfo_children():
            widget.destroy()
        
        # Obter o problema atual
        current_problem = Problems_bank[problem_index]
        
        # Container principal
        detail_container = ctk.CTkFrame(
            parent_container, 
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_ACCENT
        )
        detail_container.pack(pady=Spacing.XXL, padx=Spacing.XXL, fill="both", expand=True)
        
        # Header com nome do problema
        header_frame = ctk.CTkFrame(
            detail_container, 
            fg_color=Colors.SURFACE_MEDIUM, 
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        header_frame.pack(pady=Spacing.LG, padx=Spacing.LG, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"📋 {current_problem.name}",
            font=get_title_font(Typography.SIZE_TITLE_MEDIUM),
            text_color=Colors.ACCENT_CYAN
        )
        title_label.pack(pady=Spacing.MD)
        
        # Badge de dificuldade
        difficulty_colors = {
            "Fácil": Colors.SUCCESS,
            "Médio": Colors.WARNING, 
            "Difícil": Colors.ERROR,
            "Supremo": Colors.HEHEHE,
        }
        
        difficulty_frame = ctk.CTkFrame(
            header_frame, 
            fg_color=difficulty_colors.get(current_problem.difficulty, Colors.SUCCESS),
            corner_radius=Dimensions.CORNER_RADIUS_LARGE
        )
        difficulty_frame.pack(pady=(0, Spacing.MD))
        
        difficulty_label = ctk.CTkLabel(
            difficulty_frame,
            text=f"Nível: {current_problem.difficulty}",
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        difficulty_label.pack(padx=Spacing.LG, pady=Spacing.XS)
        
        # Frame do conteúdo
        content_frame = ctk.CTkScrollableFrame(
            detail_container,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=300
        )
        content_frame.pack(pady=Spacing.LG, padx=Spacing.LG, fill="both", expand=True)
        
        # Questão
        question_label = ctk.CTkLabel(
            content_frame,
            text="📝 Problema:",
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=Colors.ACCENT_CYAN,
            anchor="w"
        )
        question_label.pack(pady=(Spacing.LG, Spacing.SM), padx=Spacing.LG, fill="x")
        
        question_text = ctk.CTkTextbox(
            content_frame,
            font=get_font(Typography.SIZE_BODY_SMALL),
            fg_color=Colors.SURFACE_DARK,
            text_color=Colors.TEXT_PRIMARY,
            height=200,
            wrap="word"
        )
        question_text.pack(pady=(0, Spacing.LG), padx=Spacing.LG, fill="both")
        question_text.insert("1.0", current_problem.question)
        question_text.configure(state="disabled")
        
        # Frame para a resposta (inicialmente oculto)
        answer_frame = ctk.CTkFrame(
            content_frame, 
            fg_color=Colors.SURFACE_DARK, 
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        
        answer_title = ctk.CTkLabel(
            answer_frame,
            text="💡 Resposta:",
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=Colors.SUCCESS,
            anchor="w"
        )
        answer_title.pack(pady=(Spacing.MD, Spacing.SM), padx=Spacing.LG, fill="x")
        
        answer_text = ctk.CTkLabel(
            answer_frame,
            text=current_problem.answer,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color="#90EE90",
            wraplength=600,
            justify="center"
        )
        answer_text.pack(pady=(0, Spacing.MD), padx=Spacing.LG)
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(detail_container, fg_color="transparent")
        buttons_frame.pack(pady=Spacing.LG, fill="x")
        
        # Botão para mostrar/ocultar resposta
        show_answer_button = ctk.CTkButton(
            buttons_frame,
            text="🔍 Mostrar Resposta",
            command=lambda: self.toggle_answer(answer_frame, show_answer_button),
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            fg_color=Colors.BUTTON_PRIMARY,
            hover_color=Colors.BUTTON_PRIMARY_HOVER,
            text_color=Colors.BUTTON_TEXT,
            corner_radius=Dimensions.CORNER_RADIUS_LARGE,
            height=Dimensions.BUTTON_HEIGHT_SMALL,
            width=Dimensions.BUTTON_WIDTH_STANDARD,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT
        )
        show_answer_button.pack(side="left", padx=Spacing.LG)

        back_to_list_button = ctk.CTkButton(
            buttons_frame,
            text="📋 Voltar à Lista",
            command=lambda: self.back_to_problems_list(parent_container, voltar_para, principal),
            font=get_font(Typography.SIZE_BODY_SMALL, Typography.WEIGHT_BOLD),
            fg_color=Colors.ACCENT_GOLD,
            hover_color=Colors.ACCENT_GOLD_HOVER,
            corner_radius=Dimensions.CORNER_RADIUS_LARGE,
            height=Dimensions.BUTTON_HEIGHT_SMALL,
            width=Dimensions.BUTTON_WIDTH_STANDARD,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_DEFAULT
        )
        back_to_list_button.pack(side="right", padx=Spacing.LG)
        
        self.answer_frame = answer_frame
        self.show_answer_button = show_answer_button
        self.answer_visible = False
    
    def toggle_answer(self, answer_frame, button):
        """Alterna a visibility da resposta"""
        if self.answer_visible:
            answer_frame.pack_forget()
            button.configure(text="🔍 Mostrar Resposta")
            self.answer_visible = False
        else:
            answer_frame.pack(pady=(0, Spacing.LG), padx=Spacing.LG, fill="x")
            button.configure(text="🙈 Ocultar Resposta")
            self.answer_visible = True
    
    def back_to_problems_list(self, parent_container, voltar_para, principal):
        """Volta para a lista de problemas"""
        for widget in parent_container.winfo_children():
            widget.destroy()
        
        self.create_problems_main_screen(parent_container, voltar_para, principal)


def setup_problems_interface(scroll_problemas_reais, voltar_para, principal, Button):
    """Função para integrar com o código existente"""
    interface = IntegratedProblemsInterface(scroll_problemas_reais)
    interface.create_problems_main_screen(scroll_problemas_reais, voltar_para, principal)