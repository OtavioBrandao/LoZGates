import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")

#Texto curto para dúvidas rápidas sobre circuitos
duvida_circuitos = """
═══════════════════════════════════════════════════════════════════════════
🔧 GUIA RÁPIDO - CIRCUITOS INTERATIVOS
═══════════════════════════════════════════════════════════════════════════

🎮 CONTROLES ESSENCIAIS:
• TAB: Abrir/fechar painel de componentes
• ESPAÇO: Testar o circuito
• Clique: Selecionar componentes
• Arrastar: Mover componentes  
• DELETE: Remover selecionado

🔌 FAZENDO CONEXÕES:
1. Clique em uma SAÍDA (lado direito dos componentes)
2. Arraste até uma ENTRADA (lado esquerdo)
3. A conexão aparecerá automaticamente

🧪 TESTANDO:
• ✅ Verde = Circuito correto!
• ❌ Vermelho = Precisa ajustes

💡 DICA: Para manual completo, clique em "❓ Ajuda" na tela inicial!
═══════════════════════════════════════════════════════════════════════════
"""

#Mensagem de boas-vindas mais concisa
welcome_message = """
🚀 Bem-vindo ao LoZ Gates!

Ferramenta educacional para Lógica Proposicional & Circuitos Digitais.

✨ Funcionalidades principais:
• 📊 Visualização automática de circuitos
• 🎮 Construção interativa
• 🧮 Simplificação passo a passo
• 📋 Tabela verdade inteligente
• 🧪 20+ problemas do mundo real

Para o manual completo, clique em "❓ Ajuda"!
"""
#---------------------- dados para o sistema interativo ---------------------------s

#Exemplos práticos organizados por categoria (para a aba de exemplos)
INTERACTIVE_EXAMPLES = {
    "basic": [
        ("A & B", "Conjunção simples", "Verdadeiro apenas se A E B forem verdadeiros"),
        ("A | B", "Disjunção simples", "Verdadeiro se A OU B for verdadeiro"),
        ("!A", "Negação simples", "Inverte o valor de A"),
        ("A & B | C", "Precedência básica", "Primeiro A & B, depois OR com C")
    ],
    "intermediate": [
        ("(A | B) & C", "Parênteses prioritários", "Primeiro A | B, depois AND com C"),
        ("A > B", "Implicação", "Se A então B: equivale a !A | B"),
        ("!(A & B)", "Lei de De Morgan", "Equivale a !A | !B"),
        ("A <> B", "Bi-implicação", "A se e somente se B")
    ],
    "advanced": [
        ("(A & B) | (!C & D)", "Combinação complexa", "Múltiplos operadores e negações"),
        ("(A > B) & (B > A)", "Equivalente à bi-implicação", "Duas implicações formam bi-implicação"),
        ("(A | B) & !(A & B)", "XOR lógico", "OU exclusivo: um ou outro, mas não ambos"),
        ("((A & B) | C) > (D <> E)", "Expressão hierárquica", "Múltiplos níveis de precedência")
    ]
}

#Dicas contextuais para diferentes seções
CONTEXTUAL_TIPS = {
    "circuit_mode": [
        "💡 Use TAB para abrir o painel de componentes rapidamente",
        "🔌 Conecte sempre as saídas (direita) às entradas (esquerda)",
        "⚡ Pressione ESPAÇO para testar seu circuito a qualquer momento",
        "🎯 Comece com o modo 'Portas Básicas' antes dos desafios",
        "🔄 Use CTRL+Z para desfazer se cometer um erro"
    ],
    "simplification": [
        "🧮 Procure primeiro por padrões como (A & !A) = 0",
        "📐 Use parênteses para deixar a precedência clara", 
        "🔄 Aplique De Morgan para simplificar negações complexas",
        "✨ Leis de absorção frequentemente simplificam muito",
        "↩️ Use 'Desfazer' se aplicar uma lei por engano"
    ],
    "expression_entry": [
        "📝 Use & para AND, | para OR, ! para NOT",
        "⚠️ Precedência: '!' -> '&' -> '|' -> '>' -> '<>'",
        "🔍 Teste com tabela verdade se não tem certeza",
        "💭 Pense na expressão em linguagem natural primeiro",
        "🔤 Use letras A-Z para variáveis"
    ]
}

#FAQ mais comum (para seção de ajuda rápida)
COMMON_FAQ = {
    "circuit_not_working": {
        "question": "Por que meu circuito não funciona?",
        "answer": """Verifique se:
• Todas as variáveis da expressão estão conectadas
• A saída tem exatamente uma conexão  
• Não há loops no circuito
• Todos os componentes têm suas entradas conectadas
• Pelo menos uma porta lógica foi usada"""
    },
    "expression_syntax": {
        "question": "Qual a sintaxe correta das expressões?",
        "answer": """Use:
• & ou * para AND (E)
• | ou + para OR (OU)  
• ! ou ~ para NOT (NÃO)
• > para implicação
• <> para bi-implicação
• Parênteses () para precedência"""
    },
    "simplification_stuck": {
        "question": "Estou travado na simplificação, e agora?",
        "answer": """Tente:
• Procurar padrões como A & !A = 0
• Aplicar De Morgan em negações complexas
• Usar absorção: A & (A | B) = A
• Pular subexpressão atual e voltar depois
• Usar o botão 'Desfazer' se errar"""
    }
}

#Mantém a variável 'informacoes' para compatibilidade, mas agora aponta para o novo sistema
informacoes = """
📚 MANUAL INTERATIVO DISPONÍVEL!

O LoZ Gates agora possui um manual completamente renovado com:

✨ Interface organizada em abas
🎨 Design moderno e atrativo  
📖 Conteúdo estruturado e didático
🔗 Links e exemplos interativos
🎮 Guias passo a passo

Para acessar o manual completo, use o botão "❓ Ajuda" na tela inicial.

Este popup mostra apenas informações básicas para consulta rápida.
"""

#função para as coisas aparecerem na frente
def make_window_visible_robust(window, parent=None, modal=False):
    if parent:
        try:
            window.transient(parent)
        except:
            pass
    
    window.update_idletasks()
    
    def force_visibility():
        try:
            window.deiconify()          
            window.lift()               
            window.attributes('-topmost', 1) 
            window.focus_force()
            if modal:
                window.grab_set()
        except:
            pass
    
    def normalize():
        try:
            window.attributes('-topmost', 0) 
            if modal:
                window.grab_release()
        except:
            pass
    
    window.after(10, force_visibility) 
    window.after(250, normalize)         
    return window