import customtkinter as ctk
from BackEnd.problems_bank import Problems_bank, ProblemsToFrame

class IntegratedProblemsInterface:
        def __init__(self, parent_window):
            self.parent = parent_window
            self.problems_handler = ProblemsToFrame(Problems_bank)
            self.current_frame = None
        
        def create_problems_main_screen(self, scroll_problemas_reais, voltar_para, principal):
            """Cria a tela principal com a lista de problemas"""
            
            header_frame = ctk.CTkFrame(scroll_problemas_reais, fg_color="transparent")
            header_frame.pack(pady=20, padx=20, fill="x")
            
            title_label = ctk.CTkLabel(
                header_frame, 
                text="🔬 Problemas do Mundo Real", 
                font=("Trebuchet MS", 28, "bold"), 
                text_color="#00D4FF"
            )
            title_label.pack(pady=(0, 10))
            
            subtitle_label = ctk.CTkLabel(
                header_frame,
                text="Explore problemas reais que podem ser resolvidos com circuitos lógicos e lógica proposicional",
                font=("Trebuchet MS", 16), 
                text_color="#CCCCCC",
                wraplength=700
            )
            subtitle_label.pack(pady=(0, 20))
            
            # Container principal com borda estilizada
            main_container = ctk.CTkFrame(
                scroll_problemas_reais, 
                fg_color="#1A1A2E",
                corner_radius=15,
                border_width=2,
                border_color="#00D4FF"
            )
            main_container.pack(pady=20, padx=30, fill="both", expand=True)
            
            # Frame interno para os problemas
            problems_frame = ctk.CTkScrollableFrame(
                main_container, 
                fg_color="#16213E",
                corner_radius=10,
                height=400,
                width=850
            )
            problems_frame.pack(padx=15, pady=15, fill="both", expand=True)
            
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
                font=("Trebuchet MS", 16, "bold"),
                fg_color="#DAA520",
                border_color="#708090",
                hover_color="#B8860B",
                corner_radius=25,
                height=50,
                width=250
            )
            back_button.pack(pady=30)
        
        def create_problem_buttons(self, container, scroll_problemas_reais, voltar_para, principal):
            """Cria os botões para cada problema"""
            
            # Dicionário de cores para diferentes dificuldades
            difficulty_colors = {
                "Fácil": ("#4CAF50", "#45A049"),      # Verde
                "Média": ("#FF9800", "#F57C00"),      # Laranja  
                "Difícil": ("#F44336", "#D32F2F")     # Vermelho
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
                    font=("Trebuchet MS", 12, "bold"),
                    fg_color=fg_color,
                    hover_color=hover_color,
                    corner_radius=15,
                    height=80,
                    width=180,
                    text_color="white",
                    border_width=2,
                    border_color="#708090"
                )
                
                # Posicionar no grid (4 colunas)
                row = idx // 4
                col = idx % 4
                problem_button.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
        
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
                fg_color="#1A1A2E",
                corner_radius=15,
                border_width=2,
                border_color="#00D4FF"
            )
            detail_container.pack(pady=30, padx=30, fill="both", expand=True)
            
            # Header com nome do problema
            header_frame = ctk.CTkFrame(detail_container, fg_color="#16213E", corner_radius=10)
            header_frame.pack(pady=20, padx=20, fill="x")
            
            title_label = ctk.CTkLabel(
                header_frame,
                text=f"📋 {current_problem.name}",
                font=("Trebuchet MS", 24, "bold"),
                text_color="#00D4FF"
            )
            title_label.pack(pady=15)
            
            # Badge de dificuldade
            difficulty_colors = {
                "Fácil": "#4CAF50",
                "Média": "#FF9800", 
                "Difícil": "#F44336"
            }
            
            difficulty_frame = ctk.CTkFrame(
                header_frame, 
                fg_color=difficulty_colors.get(current_problem.difficulty, "#4CAF50"),
                corner_radius=20
            )
            difficulty_frame.pack(pady=(0, 15))
            
            difficulty_label = ctk.CTkLabel(
                difficulty_frame,
                text=f"Nível: {current_problem.difficulty}",
                font=("Trebuchet MS", 14, "bold"),
                text_color="white"
            )
            difficulty_label.pack(padx=20, pady=8)
            
            # Frame do conteúdo
            content_frame = ctk.CTkScrollableFrame(
                detail_container,
                fg_color="#16213E",
                corner_radius=10,
                height=300
            )
            content_frame.pack(pady=20, padx=20, fill="both", expand=True)
            
            # Questão
            question_label = ctk.CTkLabel(
                content_frame,
                text="📝 Problema:",
                font=("Trebuchet MS", 18, "bold"),
                text_color="#00D4FF",
                anchor="w"
            )
            question_label.pack(pady=(20, 10), padx=20, fill="x")
            
            question_text = ctk.CTkTextbox(
                content_frame,
                font=("Trebuchet MS", 14),
                fg_color="#0F1419",
                text_color="white",
                height=200,
                wrap="word"
            )
            question_text.pack(pady=(0, 20), padx=20, fill="both")
            question_text.insert("1.0", current_problem.question)
            question_text.configure(state="disabled")
            
            # Frame para a resposta (inicialmente oculto)
            answer_frame = ctk.CTkFrame(content_frame, fg_color="#0F1419", corner_radius=10)
            
            answer_title = ctk.CTkLabel(
                answer_frame,
                text="💡 Resposta:",
                font=("Trebuchet MS", 18, "bold"),
                text_color="#4CAF50",
                anchor="w"
            )
            answer_title.pack(pady=(15, 10), padx=20, fill="x")
            
            answer_text = ctk.CTkLabel(
                answer_frame,
                text=current_problem.answer,
                font=("Trebuchet MS", 16, "bold"),
                text_color="#90EE90",
                wraplength=600,
                justify="center"
            )
            answer_text.pack(pady=(0, 15), padx=20)
            
            # Botões de ação
            buttons_frame = ctk.CTkFrame(detail_container, fg_color="transparent")
            buttons_frame.pack(pady=20, fill="x")
            
            # Botão para mostrar/ocultar resposta
            show_answer_button = ctk.CTkButton(
                buttons_frame,
                text="🔍 Mostrar Resposta",
                command=lambda: self.toggle_answer(answer_frame, show_answer_button),
                font=("Trebuchet MS", 14, "bold"),
                fg_color="#B0E0E6",
                hover_color="#8B008B",
                text_color="#000080",
                corner_radius=25,
                height=45,
                width=200,
                border_width=2,
                border_color="#708090"
            )
            show_answer_button.pack(side="left", padx=20)

            back_to_list_button = ctk.CTkButton(
                buttons_frame,
                text="📋 Voltar à Lista",
                command=lambda: self.back_to_problems_list(parent_container, voltar_para, principal),
                font=("Trebuchet MS", 14, "bold"),
                fg_color="#DAA520",
                hover_color="#B8860B",
                corner_radius=25,
                height=45,
                width=200,
                border_width=2,
                border_color="#708090"
            )
            back_to_list_button.pack(side="right", padx=20)
            

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
                answer_frame.pack(pady=(0, 20), padx=20, fill="x")
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