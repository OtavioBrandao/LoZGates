import customtkinter as ctk
from BackEnd.problems_bank import Problems_bank, ProblemsToFrame
from .design_tokens import Colors, Typography, Dimensions, Spacing, get_font, get_title_font
from .buttons import Button

class IntegratedProblemsInterface:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.problems_handler = ProblemsToFrame(Problems_bank)
        self.current_frame = None
    
    def create_problems_main_screen(self, scroll_problemas_reais, voltar_para, principal):
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
        
        main_container = ctk.CTkFrame(
            scroll_problemas_reais, 
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_ACCENT
        )
        main_container.pack(pady=Spacing.LG, padx=Spacing.LG, fill="both", expand=True)
        
        problems_frame = ctk.CTkScrollableFrame(
            main_container, 
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=400,
            width=850
        )
        problems_frame.pack(padx=Spacing.SM, pady=Spacing.SM, fill="both", expand=True)
  
        for i in range(4):
            problems_frame.grid_columnconfigure(i, weight=1)
        
        self.create_problem_buttons(problems_frame, scroll_problemas_reais, voltar_para, principal)
        
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
        difficulty_colors = {
            "Fácil": (Colors.SUCCESS, "#09BB62"),
            "Médio": (Colors.WARNING, "#F38D08"),
            "Difícil": (Colors.ERROR, "#D32F2F"),
            "Supremo": (Colors.HEHEHE, "#B019AB")
        }
        
        for idx, problem in enumerate(Problems_bank):
            difficulty = getattr(problem, 'difficulty', 'Fácil')
            fg_color, hover_color = difficulty_colors.get(difficulty, difficulty_colors["Fácil"])
            
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
            
            row = idx // 4
            col = idx % 4
            problem_button.grid(row=row, column=col, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
    
    def toggle_answer(self, answer_frame, button):
        if self.answer_visible:
            answer_frame.pack_forget()
            button.configure(text="🔍 Mostrar Resposta")
            self.answer_visible = False
        else:
            answer_frame.pack(pady=(0, Spacing.LG), padx=Spacing.LG, fill="x")
            button.configure(text="🙈 Ocultar Resposta")
            self.answer_visible = True
    
    def back_to_problems_list(self, parent_container, voltar_para, principal):
        for widget in parent_container.winfo_children():
            widget.destroy()
        
        self.create_problems_main_screen(parent_container, voltar_para, principal)

    def show_problem_detail(self, problem_index, parent_container, voltar_para, principal):
        
        for widget in parent_container.winfo_children():
            widget.destroy()
        
        current_problem = Problems_bank[problem_index]
        
        detail_container = ctk.CTkFrame(
            parent_container, 
            fg_color=Colors.SURFACE_LIGHT,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            border_width=Dimensions.BORDER_WIDTH_STANDARD,
            border_color=Colors.BORDER_ACCENT
        )
        detail_container.pack(pady=Spacing.XXL, padx=Spacing.XXL, fill="both", expand=True)
        
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
        
        content_frame = ctk.CTkScrollableFrame(
            detail_container,
            fg_color=Colors.SURFACE_MEDIUM,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL,
            height=300
        )
        content_frame.pack(pady=Spacing.LG, padx=Spacing.LG, fill="both", expand=True)
        
        question_label = ctk.CTkLabel(
            content_frame,
            text="📖 Problema:",
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
        
        answer_input_frame = ctk.CTkFrame(
            content_frame,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        answer_input_frame.pack(pady=(0, Spacing.LG), padx=Spacing.LG, fill="x")
        
        answer_input_title = ctk.CTkLabel(
            answer_input_frame,
            text="✍️ Sua Resposta:",
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=Colors.ACCENT_CYAN,
            anchor="w"
        )
        answer_input_title.pack(pady=(Spacing.MD, Spacing.SM), padx=Spacing.LG, fill="x")
        
        answer_entry = ctk.CTkEntry(
            answer_input_frame,
            placeholder_text="Digite sua expressão lógica aqui (ex: A & B | C)",
            font=get_font(Typography.SIZE_BODY),
            height=40
        )
        answer_entry.pack(pady=(0, Spacing.MD), padx=Spacing.LG, fill="x")
        
        feedback_frame = ctk.CTkFrame(
            answer_input_frame,
            fg_color="transparent"
        )
        feedback_frame.pack(pady=(0, Spacing.MD), padx=Spacing.LG, fill="x")
        
        feedback_label = ctk.CTkLabel(
            feedback_frame,
            text="",
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        feedback_label.pack()
        
        answer_frame = ctk.CTkFrame(
            content_frame, 
            fg_color=Colors.SURFACE_DARK, 
            corner_radius=Dimensions.CORNER_RADIUS_SMALL
        )
        
        answer_title = ctk.CTkLabel(
            answer_frame,
            text="💡 Resposta Correta:",
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
        
        buttons_frame = ctk.CTkFrame(detail_container, fg_color="transparent")
        buttons_frame.pack(pady=Spacing.LG, padx=Spacing.LG, fill="x")
        
        #Configura grid para distribuição uniforme dos botões
        for i in range(6):
            buttons_frame.grid_columnconfigure(i, weight=1, uniform="button")

        def verify_answer():
            user_answer = answer_entry.get().strip()
            
            if not user_answer:
                feedback_label.configure(
                    text="⚠️ Por favor, digite uma resposta",
                    text_color=Colors.WARNING
                )
                return
            
            #✅ HABILITA botão "Mostrar Resposta" após PRIMEIRA tentativa
            show_answer_button.configure(state="normal")
            
            is_correct, message = self.validate_answer_with_equivalence(user_answer, current_problem.answer)
            
            if is_correct:
                feedback_label.configure(
                    text=message,
                    text_color=Colors.SUCCESS
                )
                #✅ HABILITA botões de análise APENAS se resposta correta
                analyze_circuit_btn.configure(state="normal")
                analyze_simplify_btn.configure(state="normal")
                analyze_table_btn.configure(state="normal")
                
                if hasattr(self, 'user_logger'):
                    self.user_logger.log_feature_used("problem_solved", 0)
            else:
                feedback_label.configure(
                    text=message,
                    text_color=Colors.ERROR
                )
                #❌ MANTÉM botões de análise desabilitados se resposta incorreta
                analyze_circuit_btn.configure(state="disabled")
                analyze_simplify_btn.configure(state="disabled")
                analyze_table_btn.configure(state="disabled")

        def analyze_in_circuit():
            user_answer = answer_entry.get().strip()
            if user_answer:
                self.back_to_problems_list(parent_container, voltar_para, principal)
                voltar_para(principal)
                self.fill_main_expression_and_navigate(user_answer, "circuit")
        
        def analyze_in_simplifier():
            user_answer = answer_entry.get().strip()
            if user_answer:
                self.back_to_problems_list(parent_container, voltar_para, principal)
                voltar_para(principal)
                self.fill_main_expression_and_navigate(user_answer, "simplifier")
        
        def analyze_in_table():
            user_answer = answer_entry.get().strip()
            if user_answer:
                self.back_to_problems_list(parent_container, voltar_para, principal)
                voltar_para(principal)
                self.fill_main_expression_and_navigate(user_answer, "table")
        
        verify_button = Button.botao_padrao("🔍 Verificar Resposta", buttons_frame)
        verify_button.configure(command=verify_answer)
        verify_button.grid(row=0, column=0, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
        
        analyze_circuit_btn = Button.botao_padrao("🔌 Analisar no Circuito", buttons_frame)
        analyze_circuit_btn.configure(command=analyze_in_circuit, state="disabled")
        analyze_circuit_btn.grid(row=0, column=1, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
        
        analyze_simplify_btn = Button.botao_padrao("🔎 Simplificar", buttons_frame)
        analyze_simplify_btn.configure(command=analyze_in_simplifier, state="disabled")
        analyze_simplify_btn.grid(row=0, column=2, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
        
        analyze_table_btn = Button.botao_padrao("📊 Tabela Verdade", buttons_frame)
        analyze_table_btn.configure(command=analyze_in_table, state="disabled")
        analyze_table_btn.grid(row=0, column=3, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
        
        show_answer_button = Button.botao_padrao("👁️ Mostrar Resposta", buttons_frame)
        show_answer_button.configure(command=lambda: self.toggle_answer(answer_frame, show_answer_button), state="disabled")
        show_answer_button.grid(row=0, column=4, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
        
        back_to_list_button = Button.botao_voltar("📋 Voltar à Lista", buttons_frame)
        back_to_list_button.configure(command=lambda: self.back_to_problems_list(parent_container, voltar_para, principal))
        back_to_list_button.grid(row=0, column=5, padx=Spacing.XS, pady=Spacing.XS, sticky="ew")
        
        self.answer_frame = answer_frame
        self.show_answer_button = show_answer_button
        self.answer_visible = False

    def fill_main_expression_and_navigate(self, expression, destination):
        if hasattr(self, 'main_entry_callback'):
            self.main_entry_callback(expression, destination)
        else:
            print(f"⚠️ Callback não configurado. Expressão: {expression}, Destino: {destination}")
            
    def validate_answer_with_equivalence(self, user_answer, correct_answer):
        from BackEnd.equivalencia import check_universal_equivalence
        from BackEnd.normalizer import normalize_for_comparison, expressions_are_structurally_equivalent
        
        try:
            user_answer_clean = user_answer.strip().upper().replace(" ", "")
            correct_answer_clean = correct_answer.strip().upper().replace(" ", "")
            
            print(f"\n{'='*60}")
            print(f"🔍 VALIDAÇÃO DE RESPOSTA")
            print(f"{'='*60}")
            print(f"📝 Resposta do usuário: {user_answer_clean}")
            print(f"✅ Resposta correta: {correct_answer_clean}")
            
            #PRIMEIRA VERIFICAÇÃO: Equivalência lógica direta
            print(f"\n🧮 Verificando equivalência lógica direta...")
            is_logically_equivalent = check_universal_equivalence(user_answer_clean, correct_answer_clean, debug=True)
            
            if is_logically_equivalent:
                print(f"✅ RESULTADO: Expressões são logicamente equivalentes!")
                print(f"{'='*60}\n")
                return True, "✅ Resposta correta! Parabéns!"
            
            #SEGUNDA VERIFICAÇÃO: Equivalência estrutural (variáveis diferentes)
            print(f"\n🔄 Verificando equivalência estrutural (ignorando nomes de variáveis)...")
            
            user_normalized = normalize_for_comparison(user_answer_clean)
            correct_normalized = normalize_for_comparison(correct_answer_clean)
            
            print(f"   Usuário normalizado: {user_normalized}")
            print(f"   Correto normalizado: {correct_normalized}")
            
            is_structurally_equivalent = expressions_are_structurally_equivalent(user_answer_clean, correct_answer_clean)
            
            if is_structurally_equivalent:
                #Verifica se são logicamente equivalentes após normalização
                is_equiv_normalized = check_universal_equivalence(user_normalized, correct_normalized, debug=False)
                
                if is_equiv_normalized:
                    print(f"✅ RESULTADO: Expressões são estruturalmente equivalentes!")
                    print(f"{'='*60}\n")
                    return True, "✅ Resposta correta! Sua expressão tem a mesma estrutura lógica (apenas os nomes das variáveis diferem)."
            
            #NÃO É EQUIVALENTE
            print(f"❌ RESULTADO: Expressões NÃO são equivalentes")
            print(f"{'='*60}\n")
            return False, "❌ Resposta incorreta. Sua expressão não é logicamente equivalente à resposta esperada."
        
        except Exception as e:
            print(f"❌ Erro geral na validação: {e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            return False, f"❌ Erro na validação: {str(e)}"

def setup_problems_interface(scroll_problemas_reais, voltar_para, principal, Button):
    interface = IntegratedProblemsInterface(scroll_problemas_reais)
    interface.create_problems_main_screen(scroll_problemas_reais, voltar_para, principal)