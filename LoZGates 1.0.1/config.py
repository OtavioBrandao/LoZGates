import logging
import os
from dataclasses import dataclass
from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent
ROOT_DIR = str(ROOT_PATH)  # Compatibilidade com consumidores antigos.
ASSETS_DIR = ROOT_PATH / "assets"
ASSETS_PATH = str(ASSETS_DIR)


def load_environment_file(path=None):
    """Load a simple .env file without overriding the process environment."""
    env_path = Path(path or ROOT_PATH / ".env")
    if not env_path.is_file():
        return False

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name or not name.replace("_", "").isalnum():
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(name, value)
    return True


load_environment_file()


def _configured_path(variable_name, default):
    value = os.getenv(variable_name)
    path = Path(value).expanduser() if value else default
    if not path.is_absolute():
        path = ROOT_PATH / path
    return path.resolve()


def _env_float(variable_name, default, minimum=0.1):
    try:
        return max(minimum, float(os.getenv(variable_name, default)))
    except (TypeError, ValueError):
        return float(default)


DATA_DIR = _configured_path("LOZGATES_DATA_DIR", ROOT_PATH / "data")
LOG_DIR = _configured_path("LOZGATES_LOG_DIR", ROOT_PATH / "logs")
CIRCUIT_IMAGE_PATH = DATA_DIR / "circuito.png"
INPUT_CACHE_PATH = DATA_DIR / "entrada.txt"
ACTIVITY_LOG_PATH = DATA_DIR / "user_activity_detailed.json"
ACTIVITY_SETTINGS_PATH = DATA_DIR / "logging_settings.json"
LEGACY_ACTIVITY_LOG_PATH = ROOT_PATH / "user_activity_detailed.json"
LEGACY_ACTIVITY_SETTINGS_PATH = ROOT_PATH / "logging_settings.json"
WINDOW_ICON_PATH = ASSETS_DIR / "icon.ico"


def ensure_runtime_directories():
    """Cria somente os diretorios gravaveis usados em tempo de execucao."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class AISettings:
    api_key: str
    api_url: str
    model: str
    timeout_seconds: float
    service_url: str

    @classmethod
    def from_environment(cls):
        return cls(
            api_key=(
                os.getenv("LOZGATES_AI_API_KEY")
                or os.getenv("GROQ_API_KEY")
                or ""
            ).strip(),
            api_url=os.getenv(
                "LOZGATES_AI_API_URL",
                "https://api.groq.com/openai/v1/chat/completions",
            ).strip(),
            model=os.getenv("LOZGATES_AI_MODEL", "openai/gpt-oss-120b").strip(),
            timeout_seconds=_env_float("LOZGATES_AI_TIMEOUT", 15),
            service_url=os.getenv("LOZGATES_AI_SERVICE_URL", "").strip().rstrip("/"),
        )

#Texto curto para dúvidas rápidas sobre circuitos
duvida_circuitos = """
═══════════════════════════════════════════════════════════════════════════
🔧 GUIA RÁPIDO - CIRCUITOS INTERATIVOS
═══════════════════════════════════════════════════════════════════════════

🎮 CONTROLES ESSENCIAIS:
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
        except Exception:
            logging.getLogger(__name__).debug(
                "Nao foi possivel associar a janela ao parent", exc_info=True
            )
    
    window.update_idletasks()
    
    def force_visibility():
        try:
            window.deiconify()          
            window.lift()               
            window.attributes('-topmost', 1) 
            window.focus_force()
            if modal:
                window.grab_set()
        except Exception:
            logging.getLogger(__name__).debug(
                "Nao foi possivel forcar a visibilidade da janela", exc_info=True
            )
    
    def normalize():
        try:
            window.attributes('-topmost', 0) 
            if modal:
                window.grab_release()
        except Exception:
            logging.getLogger(__name__).debug(
                "Nao foi possivel normalizar a janela", exc_info=True
            )
    
    window.after(10, force_visibility) 
    window.after(250, normalize)
    return window


def apply_window_icon(window):
    """Aplica o icone quando suportado pelo backend Tk da plataforma."""
    if not WINDOW_ICON_PATH.exists():
        return False
    try:
        window.iconbitmap(str(WINDOW_ICON_PATH))
        return True
    except Exception:
        logging.getLogger(__name__).debug(
            "Backend Tk nao suporta o icone %s", WINDOW_ICON_PATH, exc_info=True
        )
        return False
