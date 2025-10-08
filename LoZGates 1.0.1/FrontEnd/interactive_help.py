import customtkinter as ctk
import webbrowser
from FrontEnd.design_tokens import Colors, Typography, Dimensions, get_font, get_title_font
from config import make_window_visible_robust

class InteractiveHelpSystem:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.help_window = None
        
    def show_help(self):
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.lift()
            self.help_window.focus()
            return
            
        self.create_help_window()
        
    def create_help_window(self):
        self.help_window = ctk.CTkToplevel(self.parent)
        make_window_visible_robust(self.help_window, parent=self.parent)
        self.help_window.title("📚 LoZ Gates - manual interativo")
        self.help_window.geometry("1000x700")
        self.help_window.resizable(True, True)
        
        #Centralizar na tela
        self.help_window.update_idletasks()
        x = (self.help_window.winfo_screenwidth() // 2) - 500
        y = (self.help_window.winfo_screenheight() // 2) - 350
        self.help_window.geometry(f"1000x700+{x}+{y}")
        
        self.help_window.configure(fg_color=Colors.PRIMARY_BG)
        self.create_header()
        self.create_tabbed_interface()
        self.help_window.focus()
        
    def create_header(self):
        header_frame = ctk.CTkFrame(
            self.help_window,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM,
            height=100
        )
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        #Título principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="🚀 LoZ Gates - manual completo",
            font=get_title_font(32),
            text_color=Colors.TEXT_ACCENT
        )
        title_label.pack(pady=10)
        
        #Subtítulo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Ferramenta educacional para Lógica Proposicional & Circuitos Digitais",
            font=get_font(14),
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle_label.pack()
        
    def create_tabbed_interface(self):
        main_frame = ctk.CTkFrame(self.help_window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_view = ctk.CTkTabview(
            main_frame,
            fg_color=Colors.SURFACE_LIGHT,
            segmented_button_fg_color=Colors.SURFACE_MEDIUM,
            segmented_button_selected_color=Colors.INFO,
            segmented_button_selected_hover_color="#1976D2",
            segmented_button_unselected_color=Colors.SURFACE_DARK,
            segmented_button_unselected_hover_color=Colors.SURFACE_MEDIUM
        )
        self.tab_view.pack(fill="both", expand=True)
        
        self.create_about_tab()
        self.create_features_tab()
        self.create_syntax_tab()
        self.create_examples_tab()
        self.create_laws_tab()
        self.create_controls_tab()
        self.create_tips_tab()
        self.create_credits_tab()
        
    def create_about_tab(self):
        tab = self.tab_view.add("📘 Sobre")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        #Conteúdo da aba Sobre
        self.add_section_title(scroll_frame, "🎯 Objetivo do projeto")
        self.add_paragraph(scroll_frame, 
            "O LoZ Gates é uma ferramenta educacional interativa que conecta os conceitos "
            "de Lógica Proposicional com Circuitos Digitais, proporcionando uma experiência "
            "de aprendizado visual e prática para estudantes e educadores.")
        
        self.add_section_title(scroll_frame, "👥 Equipe de desenvolvimento")
        team_info = [
            "• Larissa Ferreira Dias de Souza - Sistemas interativos & Backend - lfds@ic.ufal.br",
            "• Otávio Joshua Costa Brandão Menezes - UI & UX - ojcbm@ic.ufal.br", 
            "• Zilderlan Naty dos Santos - IA - zns@ic.ufal.br",
            "• David Kelve Oliveira Barbosa - Simplificação & Banco de problemas - dkob@ic.ufal.br",
            "👨‍🏫 Orientador: Prof. Dr. Evandro de Barros Costa"
        ]
        self.add_bullet_list(scroll_frame, team_info)
        
        self.add_section_title(scroll_frame, "🏛️ Instituição")
        self.add_paragraph(scroll_frame,
            "Universidade Federal de Alagoas (UFAL)\n"
            "Instituto de Computação (IC)\n")
        
        #Botão de ação
        self.add_action_button(scroll_frame, "🌐 Site da UFAL", 
            lambda: webbrowser.open("https://ufal.br"))
            
    def create_features_tab(self):
        tab = self.tab_view.add("🔧 Funcionalidades")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        features = [
            {
                "title": "📊 Visualização de circuitos",
                "description": "Geração automática de circuitos lógicos a partir de expressões",
                "details": [
                    "• Visualização em tempo real das conexões",
                    "• Export de imagens PNG dos circuitos",
                    "• Interface intuitiva e didática"
                ]
            },
            {
                "title": "🎮 Circuito interativo",
                "description": "Construção manual de circuitos",
                "details": [
                    "• 6 modos de desafio diferentes",
                    "• Sistema de validação automática", 
                    "• Feedback visual em tempo real",
                    "• Suporte a componentes básicos e avançados"
                ]
            },
            {
                "title": "🧮 Simplificação interativa",
                "description": "Aplicação passo a passo das leis de simplificação",
                "details": [
                    "• Interface guiada com explicações",
                    "• Sistema de undo/redo",
                    "• Histórico completo das transformações",
                    "• Aplicação de 9 leis lógicas diferentes"
                ]
            },
            {
                "title": "📋 Tabela verdade inteligente",
                "description": "Geração automática para qualquer expressão",
                "details": [
                    "• Análise de tautologias e contradições",
                    "• Interface colorizada",
                    "• Suporte a expressões complexas"
                ]
            },
            {
                "title": "🧪 Problemas do mundo real",
                "description": "Mais de 30 problemas práticos categorizados",
                "details": [
                    "• 4 níveis de dificuldade",
                    "• Aplicações reais de lógica proposicional",
                    "• Sistema de dicas progressivas"
                ]
            }
        ]
        
        for feature in features:
            self.add_feature_card(scroll_frame, feature)
            
    def create_syntax_tab(self):
        tab = self.tab_view.add("📝 Sintaxe")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.add_section_title(scroll_frame, "🔤 Variáveis aceitas")
        self.add_code_block(scroll_frame, "Qualquer letra de A-Z (maiúscula ou minúscula)\nExemplo: A, B, C, p, Q, R, x, y, Z")
        
        self.add_section_title(scroll_frame, "🔣 Operadores lógicos")
        
        operators = [
            ("CONJUNÇÃO (E)", "& ou *", "A & B  ou  A * B", '"A e B"'),
            ("DISJUNÇÃO (OU)", "| ou +", "A | B  ou  A + B", '"A ou B"'),
            ("NEGAÇÃO (NÃO)", "! ou ~", "!A  ou  ~A", '"não A"'),
            ("IMPLICAÇÃO", ">", "A > B", '"se A então B"'),
            ("BI-IMPLICAÇÃO", "<>", "A <> B", '"A se e somente se B"')
        ]
        
        for op_name, symbol, example, meaning in operators:
            self.add_operator_card(scroll_frame, op_name, symbol, example, meaning)
            
        self.add_section_title(scroll_frame, "⚠️ Precedência dos operadores")
        precedence = [
            "1. ! ou ~ (Negação) - MAIOR precedência",
            "2. & ou * (Conjunção)",
            "3. | ou + (Disjunção)", 
            "4. > (Implicação)",
            "5. <> (Bi-implicação) - MENOR precedência"
        ]
        self.add_bullet_list(scroll_frame, precedence)
        
    def create_examples_tab(self):
        tab = self.tab_view.add("💡 Exemplos")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        example_categories = [
            {
                "level": "🟢 Básicas",
                "color": Colors.SUCCESS,
                "examples": [
                    ("A & B", "Conjunção simples"),
                    ("A | B", "Disjunção simples"),
                    ("!A", "Negação simples"),
                    ("A & B | C", "Conjunção seguida de disjunção")
                ]
            },
            {
                "level": "🟡 Intermediárias", 
                "color": Colors.WARNING,
                "examples": [
                    ("(A | B) & C", "Disjunção prioritária"),
                    ("A > B", "Implicação"),
                    ("!(A & B)", "Negação de conjunção"),
                    ("A <> B", "Bi-implicação")
                ]
            },
            {
                "level": "🔴 Avançadas",
                "color": Colors.ERROR,
                "examples": [
                    ("(A & B) | (!C & D)", "Combinação complexa"),
                    ("(A > B) & (B > A)", "Equivalente à bi-implicação"),
                    ("(A | B) & !(A & B)", "XOR lógico"),
                    ("((A & B) | C) > (D <> E)", "Expressão hierárquica")
                ]
            }
        ]
        
        for category in example_categories:
            self.add_example_category(scroll_frame, category)
            
        #Botão para testar exemplos (AINDA NÃP FUNCIONA)
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        test_button = ctk.CTkButton(
            button_frame,
            text="🧪 Testar exemplos no LoZ Gates",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            fg_color=Colors.INFO,
            hover_color="#1976D2",
            height=40,
            command=self.close_and_test_example
        )
        test_button.pack()
        
    def create_laws_tab(self):
        tab = self.tab_view.add("⚖️ Leis")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.add_section_title(scroll_frame, "📚 Leis fundamentais da lógica")
        
        laws = [
            {
                "name": "🔶 Lei da identidade",
                "rules": ["A & 1 = A", "A | 0 = A"],
                "explanation": '"E com verdadeiro é a própria variável"\n"Ou com falso é a própria variável"'
            },
            {
                "name": "🔶 Lei nula (absorção total)",
                "rules": ["A & 0 = 0", "A | 1 = 1"],
                "explanation": '"E com falso é sempre falso"\n"Ou com verdadeiro é sempre verdadeiro"'
            },
            {
                "name": "🔶 Lei idempotente", 
                "rules": ["A & A = A", "A | A = A"],
                "explanation": '"Variável consigo mesma não muda"'
            },
            {
                "name": "🔶 Lei inversa (complemento)",
                "rules": ["A & !A = 0", "A | !A = 1"],
                "explanation": '"Variável com sua negação dá resultado fixo"'
            },
            {
                "name": "🔶 Lei de De Morgan",
                "rules": ["!(A & B) = !A | !B", "!(A | B) = !A & !B"],
                "explanation": '"Negação distribui trocando o operador"'
            },
            {
                "name": "🔶 Lei de absorção",
                "rules": ["A & (A | B) = A", "A | (A & B) = A"],
                "explanation": '"Variável absorve expressões que a contêm"'
            },
            {
                "name": "🔶 Lei distributiva",
                "rules": ["A & (B | C) = (A & B) | (A & C)", "A | (B & C) = (A | B) & (A | C)"],
                "explanation": '"Distribui um operador sobre o outro"'
            },
            {
                "name": "🔶 Lei associativa",
                "rules": ["(A & B) & C = A & (B & C)", "(A | B) | C = A | (B | C)"],
                "explanation": '"Reagrupa operações do mesmo tipo"'
            },
            {
                "name": "🔶 Lei comutativa",
                "rules": ["A & B = B & A", "A | B = B | A"],
                "explanation": '"Ordem das variáveis não importa"'
            }
        ]
        
        for law in laws:
            self.add_law_card(scroll_frame, law)
            
    def create_controls_tab(self):
        tab = self.tab_view.add("🎮 Controles")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        control_sections = [
            {
                "title": "🔧 Controles básicos - circuito interativo",
                "controls": [
                    ("TAB", "Mostrar/esconder painel de componentes"),
                    ("ESPAÇO", "Testar circuito"),
                    ("Clique", "Selecionar componente"),
                    ("Arrastar", "Mover componente"),
                    ("DELETE", "Remover selecionado"),
                    ("ESC", "Cancelar ação atual")
                ]
            },
            {
                "title": "📐 Navegação da câmera",
                "controls": [
                    ("W / ↑", "Mover câmera para cima"),
                    ("S / ↓", "Mover câmera para baixo"),
                    ("A / ←", "Mover câmera para esquerda"),
                    ("D / →", "Mover câmera para direita"),
                    ("Scroll", "Zoom in/out"),
                    ("R", "Resetar vista")
                ]
            },
            {
                "title": "✏️ Edição avançada",
                "controls": [
                    ("CTRL+Z", "Desfazer última ação"),
                    ("CTRL+Y", "Refazer ação desfeita"),
                    ("Bolinhas verdes", "Pontos de conexão"),
                    ("Clique duplo", "Focar em componente")
                ]
            }
        ]
        
        for section in control_sections:
            self.add_controls_section(scroll_frame, section)
            
        #Seção especial: Como jogar
        self.add_section_title(scroll_frame, "📋 Como jogar - passo a passo")
        steps = [
            "1. 🎯 Selecione um modo de desafio",
            "2. ▶️ Clique em 'Iniciar desafio'", 
            "3. 📱 Use TAB para abrir o painel",
            "4. 🔧 Adicione componentes clicando no painel",
            "5. 🔗 Conecte os pontos verdes",
            "6. 🧪 Pressione ESPAÇO para testar!",
            "7. ✅ Implemente a expressão corretamente!"
        ]
        self.add_bullet_list(scroll_frame, steps)
        
    def create_tips_tab(self):
        tab = self.tab_view.add("💭 Dicas")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tip_sections = [
            {
                "title": "🔰 Para iniciantes",
                "icon": "🟢",
                "tips": [
                    "Comece com expressões simples (2-3 variáveis)",
                    "Use parênteses quando em dúvida sobre precedência",
                    "Teste suas expressões com a tabela verdade primeiro",
                    "Explore o modo 'Portas básicas' no circuito interativo"
                ]
            },
            {
                "title": "🎯 Para intermediários",
                "icon": "🟡",
                "tips": [
                    "Pratique simplificação manual antes do modo interativo",
                    "Tente os desafios NAND e NOR",
                    "Compare diferentes formas da mesma expressão",
                    "Explore os problemas do mundo real"
                ]
            },
            {
                "title": "🚀 Para avançados",
                "icon": "🔴",
                "tips": [
                    "Use o modo 'Desafio mínimo' para otimizar",
                    "Experimente com expressões de 4+ variáveis",
                    "Crie seus próprios problemas complexos",
                    "Explore as nuances das leis distributivas"
                ]
            }
        ]
        
        for section in tip_sections:
            self.add_tips_section(scroll_frame, section)
            
        self.add_section_title(scroll_frame, "🎯 Estratégias de Simplificação")
        strategy_text = """
✅ Ordem Recomendada:
    1️ Leis nula
    2️ Leis inversas  
    3️ Identidade e idempotente
    4️ Absorção
    5️ De Morgan e distributiva

🔍 Reconhecimento de padrões:
  • Procure por (A & !A) ou (A | !A) primeiro
  • Identifique oportunidades de absorção
  • Use De Morgan para simplificar negações complexas
        """
        self.add_paragraph(scroll_frame, strategy_text)
        
    def create_credits_tab(self):
        tab = self.tab_view.add("🏆 Créditos")
        
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.add_section_title(scroll_frame, "🎓 Sobre o LoZ Gates")
        self.add_paragraph(scroll_frame,
            "Versão 1.0-Beta\n"
            "Projeto educacional desenvolvido na Universidade Federal de Alagoas (UFAL)\n"
            "Instituto de Computação - 2024")
        
        '''self.add_section_title(scroll_frame, "🙏 Agradecimentos")
        thanks = [
        ]
        self.add_bullet_list(scroll_frame, thanks)'''
        
        self.add_section_title(scroll_frame, "💡 Tecnologias Utilizadas")
        tech = [
            "• Python 3.8+ (Linguagem principal)",
            "• CustomTkinter (Interface moderna)",
            "• Pygame (Circuitos interativos)",
            "• PIL/Pillow (Processamento de imagens)",
            "• Requests (Comunicação web)"
        ]
        self.add_bullet_list(scroll_frame, tech)
        
        #Botões de ação
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        github_button = ctk.CTkButton(
            button_frame,
            text="🐙 Repositório GitHub",
            fg_color="#333333",
            hover_color="#555555",
            command=lambda: webbrowser.open("https://github.com/LarissaFDS/LoZGates/tree/main")
        )
        github_button.pack(side="left", padx=10)
        
        ufal_button = ctk.CTkButton(
            button_frame, 
            text="🏛️ IC-UFAL",
            fg_color=Colors.INFO,
            hover_color="#1976D2",
            command=lambda: webbrowser.open("https://ic.ufal.br")
        )
        ufal_button.pack(side="left", padx=10)
        
        #Mensagem final
        final_frame = ctk.CTkFrame(scroll_frame, fg_color=Colors.SURFACE_DARK, corner_radius=15)
        final_frame.pack(fill="x", pady=20)
        
        final_label = ctk.CTkLabel(
            final_frame,
            text='"É importante extrair sabedoria de diferentes lugares.\nSe você a extrai de um lugar só, ela se torna rígida e obsoleta."\n- Iroh\n\n🚀 Obrigado por usar o LoZ Gates!',
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
            justify="center"
        )
        final_label.pack(pady=20)
        
    #============ MÉTODOS AUXILIARES PARA CRIAÇÃO DE COMPONENTES ============
    
    def add_section_title(self, parent, title):
        title_label = ctk.CTkLabel(
            parent,
            text=title,
            font=get_title_font(Typography.SIZE_TITLE_SMALL),
            text_color=Colors.TEXT_ACCENT,
            anchor="w"
        )
        title_label.pack(fill="x", pady=(20, 10))
        return title_label
        
    def add_paragraph(self, parent, text):
        para_label = ctk.CTkLabel(
            parent,
            text=text,
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
            justify="left",
            wraplength=800
        )
        para_label.pack(fill="x", pady=(0, 10))
        return para_label
        
    def add_bullet_list(self, parent, items):
        for item in items:
            item_label = ctk.CTkLabel(
                parent,
                text=item,
                font=get_font(Typography.SIZE_BODY),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w",
                justify="left"
            )
            item_label.pack(fill="x", pady=2)
        return
        
    def add_code_block(self, parent, code):
        code_frame = ctk.CTkFrame(parent, fg_color=Colors.SURFACE_DARK, corner_radius=8)
        code_frame.pack(fill="x", pady=10)
        
        code_label = ctk.CTkLabel(
            code_frame,
            text=code,
            font=("Consolas", 12),
            text_color=Colors.TEXT_ACCENT,
            anchor="w",
            justify="left"
        )
        code_label.pack(padx=15, pady=10, fill="x")
        return code_frame
        
    def add_operator_card(self, parent, op_name, symbol, example, meaning):
        card_frame = ctk.CTkFrame(parent, fg_color=Colors.SURFACE_LIGHT, corner_radius=10)
        card_frame.pack(fill="x", pady=5)
        
        #Nome do operador
        name_label = ctk.CTkLabel(
            card_frame,
            text=op_name,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
            anchor="w"
        )
        name_label.pack(fill="x", padx=15, pady=(10, 5))
        
        #Símbolo e exemplo
        details_text = f"Símbolo: {symbol}\nExemplo: {example}\nSignificado: {meaning}"
        details_label = ctk.CTkLabel(
            card_frame,
            text=details_text,
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
            justify="left"
        )
        details_label.pack(fill="x", padx=15, pady=(0, 10))
        
        return card_frame
        
    def add_feature_card(self, parent, feature):
        card_frame = ctk.CTkFrame(parent, fg_color=Colors.SURFACE_LIGHT, corner_radius=10)
        card_frame.pack(fill="x", pady=10)
        
        #Título da funcionalidade
        title_label = ctk.CTkLabel(
            card_frame,
            text=feature["title"],
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(15, 5))
        
        #Descrição
        desc_label = ctk.CTkLabel(
            card_frame,
            text=feature["description"],
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            wraplength=750
        )
        desc_label.pack(fill="x", padx=15, pady=(0, 10))
        
        #Detalhes
        for detail in feature["details"]:
            detail_label = ctk.CTkLabel(
                card_frame,
                text=detail,
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            detail_label.pack(fill="x", padx=25, pady=2)
        
        #Espaçamento final
        spacer = ctk.CTkLabel(card_frame, text="", height=5)
        spacer.pack()
        
        return card_frame
        
    def add_example_category(self, parent, category):
        #Frame da categoria
        cat_frame = ctk.CTkFrame(parent, fg_color=Colors.SURFACE_LIGHT, corner_radius=10)
        cat_frame.pack(fill="x", pady=10)
        
        #Título da categoria
        title_label = ctk.CTkLabel(
            cat_frame,
            text=category["level"],
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=category["color"],
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(15, 10))
        
        #Exemplos
        for expression, description in category["examples"]:
            example_frame = ctk.CTkFrame(cat_frame, fg_color=Colors.SURFACE_DARK, corner_radius=5)
            example_frame.pack(fill="x", padx=15, pady=5)
            
            #Expressão
            expr_label = ctk.CTkLabel(
                example_frame,
                text=expression,
                font=("Consolas", 14, "bold"),
                text_color=Colors.TEXT_ACCENT,
                anchor="w"
            )
            expr_label.pack(side="left", padx=15, pady=10)
            
            #Descrição
            desc_label = ctk.CTkLabel(
                example_frame,
                text=f"→ {description}",
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w"
            )
            desc_label.pack(side="left", padx=(0, 15), pady=10)
        
        #Espaçamento final
        spacer = ctk.CTkLabel(cat_frame, text="", height=10)
        spacer.pack()
        
        return cat_frame
        
    def add_law_card(self, parent, law):
        card_frame = ctk.CTkFrame(parent, fg_color=Colors.SURFACE_LIGHT, corner_radius=10)
        card_frame.pack(fill="x", pady=8)
        
        #Nome da lei
        name_label = ctk.CTkLabel(
            card_frame,
            text=law["name"],
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
            anchor="w"
        )
        name_label.pack(fill="x", padx=15, pady=(15, 10))
        
        #Regras
        rules_frame = ctk.CTkFrame(card_frame, fg_color=Colors.SURFACE_DARK, corner_radius=5)
        rules_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        for rule in law["rules"]:
            rule_label = ctk.CTkLabel(
                rules_frame,
                text=f"• {rule}",
                font=("Consolas", 12),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            rule_label.pack(fill="x", padx=15, pady=5)
        
        #Explicação
        expl_label = ctk.CTkLabel(
            card_frame,
            text=law["explanation"],
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            justify="left"
        )
        expl_label.pack(fill="x", padx=15, pady=(0, 15))
        
        return card_frame
        
    def add_controls_section(self, parent, section):
        self.add_section_title(parent, section["title"])
        
        #Frame para os controles
        controls_frame = ctk.CTkFrame(parent, fg_color=Colors.SURFACE_LIGHT, corner_radius=10)
        controls_frame.pack(fill="x", pady=10)
        
        for key, description in section["controls"]:
            control_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
            control_frame.pack(fill="x", padx=15, pady=5)
            
            #Tecla/botão
            key_label = ctk.CTkLabel(
                control_frame,
                text=key,
                font=("Consolas", 12, "bold"),
                text_color=Colors.TEXT_ACCENT,
                width=100,
                anchor="w"
            )
            key_label.pack(side="left", padx=(0, 20))
            
            #Descrição
            desc_label = ctk.CTkLabel(
                control_frame,
                text=description,
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            desc_label.pack(side="left", fill="x", expand=True)
        
        #Espaçamento
        spacer = ctk.CTkLabel(controls_frame, text="", height=10)
        spacer.pack()
        
        return controls_frame
        
    def add_tips_section(self, parent, section):
        #Frame da seção
        section_frame = ctk.CTkFrame(parent, fg_color=Colors.SURFACE_LIGHT, corner_radius=10)
        section_frame.pack(fill="x", pady=10)
        
        #Título com ícone
        title_text = f'{section["icon"]} {section["title"]}'
        title_label = ctk.CTkLabel(
            section_frame,
            text=title_text,
            font=get_font(Typography.SIZE_SUBTITLE, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT,
            anchor="w"
        )
        title_label.pack(fill="x", padx=15, pady=(15, 10))
        
        #Dicas
        for tip in section["tips"]:
            tip_frame = ctk.CTkFrame(section_frame, fg_color=Colors.SURFACE_DARK, corner_radius=5)
            tip_frame.pack(fill="x", padx=15, pady=5)
            
            tip_label = ctk.CTkLabel(
                tip_frame,
                text=f"💡 {tip}",
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w",
                wraplength=700,
                justify="left"
            )
            tip_label.pack(fill="x", padx=15, pady=10)
        
        #Espaçamento
        spacer = ctk.CTkLabel(section_frame, text="", height=10)
        spacer.pack()
        
        return section_frame
        
    def add_action_button(self, parent, text, command):
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=15)
        
        button = ctk.CTkButton(
            button_frame,
            text=text,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            fg_color=Colors.INFO,
            hover_color="#1976D2",
            height=40,
            command=command
        )
        button.pack()
        
        return button
        
    def close_and_test_example(self):
        if self.help_window:
            self.help_window.destroy()
        
    def close_help(self):
        if self.help_window:
            self.help_window.destroy()
            self.help_window = None

#FUNÇÃO PARA INTEGRAR COM O SISTEMA EXISTENTE
def show_interactive_help(parent_window):
    help_system = InteractiveHelpSystem(parent_window)
    help_system.show_help()