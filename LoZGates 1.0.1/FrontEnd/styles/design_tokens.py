# Design Tokens - Sistema de Design Unificado para LoZ Gates
# Etapa 8: Redesign Visual & UX — paleta educacional moderna
# Centraliza cores, fontes, espaçamentos e outros valores visuais

# PALETA DE CORES
class Colors:
    # --- Backgrounds ---
    PRIMARY_BG     = "#0E0F14"      # Preto azulado profundo
    SECONDARY_BG   = "#151720"      # Levemente mais claro
    SURFACE_DARK   = "#1C1E2B"      # Card principal / surface base
    SURFACE_MEDIUM = "#232638"      # Surface elevada
    SURFACE_LIGHT  = "#2A2D3E"      # Inputs, surface mais alta
    SURFACE_INPUT  = "#2A2D3E"      # Campos de entrada (alias semântico)

    # --- Cor Primária (ações principais) ---
    PRIMARY        = "#5B8AF0"      # Azul elétrico suave
    PRIMARY_HOVER  = "#7BA0F5"      # Hover mais claro
    PRIMARY_MUTED  = "#1E2D5A"      # Fundo de chips/badges primários

    # --- Legado: alias de compatibilidade (não remover até migração completa) ---
    BUTTON_PRIMARY       = PRIMARY
    BUTTON_PRIMARY_HOVER = PRIMARY_HOVER
    BUTTON_TEXT          = "#000000"      # Preto para texto em botões claros

    # --- Accent (elementos lógicos / interativos) ---
    ACCENT_CYAN        = "#5B8AF0"   # Agora aponta para Primary (migração gradual)
    ACCENT_LOGIC       = "#C678DD"   # Roxo para elementos de lógica
    ACCENT_PURPLE      = "#C678DD"   # Alias semântico
    HEHEHE             = ACCENT_PURPLE  # Alias legado — use ACCENT_PURPLE em código novo

    # --- Legado: gold (ainda usado em places que serão migrados na Fase B) ---
    ACCENT_GOLD        = "#4A7EE8"   # Migrado para azul para consistência visual
    ACCENT_GOLD_HOVER  = "#3A6DD0"   # Hover correspondente

    # --- Estado: Sucesso ---
    SUCCESS       = "#3EAE6E"       # Verde esmeralda
    SUCCESS_MUTED = "#1A3D2E"       # Fundo de badge sucesso
    SUCCESS_HOVER = "#35A062"       # Hover de botão sucesso

    # --- Estado: Aviso ---
    WARNING       = "#E8A838"       # Âmbar educacional
    WARNING_MUTED = "#3D2F10"       # Fundo de badge aviso

    # --- Estado: Erro / Perigo ---
    ERROR         = "#E05252"       # Vermelho suave
    ERROR_MUTED   = "#3D1515"       # Fundo de badge erro
    ERROR_HOVER   = "#C84444"       # Hover de botão erro

    # --- Info ---
    INFO          = "#5B8AF0"       # Migrado para Primary (consistência)
    INFO_MUTED    = "#1E2D5A"       # Fundo de badge info

    # --- Texto ---
    TEXT_PRIMARY   = "#EAEDF5"      # Quase branco, não saturado
    TEXT_SECONDARY = "#8A90A8"      # Cinza azulado
    TEXT_MUTED     = "#565A72"      # Placeholders
    TEXT_ACCENT    = "#7AABFF"      # Azul claro — expressões / destaque
    TEXT_CODE      = "#A8D5FF"      # Para código e expressões lógicas
    TEXT_SUCCESS   = "#5DD68A"      # Verde claro — texto de sucesso
    TEXT_ERROR     = "#F08080"      # Vermelho claro — texto de erro
    TEXT_WARNING   = "#F0C060"      # Âmbar claro — texto de aviso

    # --- Bordas ---
    BORDER_DEFAULT = "#2C2F42"      # Borda sutil (antes era azul, agora mais discreta)
    BORDER_ACTIVE  = "#5B8AF0"      # Borda de foco / seleção ativa
    BORDER_ACCENT  = "#3A4A7A"      # Borda com destaque suave

    # --- Help dialog (mantido para compatibilidade) ---
    HOVER_COLOR_HELP = "#3A6DD0"
    FG_COLOR_HELP    = "#2A5CC0"


# TIPOGRAFIA
class Typography:
    FONT_FAMILY      = "Segoe UI"
    FONT_CODE        = "Consolas"   # Para expressões lógicas

    # Tamanhos
    SIZE_DISPLAY         = 32   # Logo "LoZ Gates"
    SIZE_TITLE_LARGE     = 22   # Título de tela
    SIZE_TITLE_MEDIUM    = 20   # Título de seção
    SIZE_TITLE_SMALL     = 18   # Subtítulo de card / seção
    SIZE_SUBTITLE        = 16   # Subtítulo
    SIZE_BODY            = 14   # Texto padrão
    SIZE_BODY_SMALL      = 13   # Texto auxiliar
    SIZE_CAPTION         = 12   # Caption / label pequeno
    SIZE_CODE            = 14   # Expressões lógicas
    SIZE_CODE_LARGE      = 18   # Expressão principal em destaque

    # Pesos (apenas os que CustomTkinter suporta)
    WEIGHT_BOLD   = "bold"
    WEIGHT_NORMAL = "normal"


# ESPAÇAMENTOS
class Spacing:
    XS   = 4    # Micro-espaçamentos
    SM   = 8    # Entre elementos relacionados
    MD   = 12   # Padding interno de componentes
    LG   = 16   # Entre seções menores
    XL   = 24   # Padding de cards
    XXL  = 32   # Entre seções maiores
    XXXL = 48   # Margens de telas

    # Espaçamentos específicos (mantidos para compatibilidade)
    BUTTON_PADDING_X = 12
    BUTTON_PADDING_Y = 14
    FRAME_PADDING    = 16
    SECTION_SPACING  = 24


# DIMENSÕES
class Dimensions:
    # Botões
    BUTTON_WIDTH_STANDARD = 200
    BUTTON_WIDTH_SMALL    = 120
    BUTTON_WIDTH_LARGE    = 260
    BUTTON_HEIGHT_STANDARD = 44
    BUTTON_HEIGHT_SMALL    = 38

    # Bordas arredondadas
    CORNER_RADIUS_SMALL  = 6
    CORNER_RADIUS_MEDIUM = 10
    CORNER_RADIUS_LARGE  = 14
    CORNER_RADIUS_XL     = 20

    # Bordas
    BORDER_WIDTH_THIN     = 1
    BORDER_WIDTH_STANDARD = 2
    BORDER_WIDTH_THICK    = 3


# CONFIGURAÇÕES DE ABAS
class TabConfig:
    # Cores em tema dark (corrigido: antes usava fundo branco #FFFFFF)
    SELECTED_COLOR        = "#5B8AF0"   # Aba ativa: Primary
    SELECTED_HOVER        = "#3A6DD0"   # Hover da aba ativa
    UNSELECTED_COLOR      = "#1C1E2B"   # Aba inativa: Surface Dark
    UNSELECTED_HOVER      = "#232638"   # Hover da aba inativa
    BACKGROUND_COLOR      = "#151720"   # Fundo da barra de abas (dark)


# UTILITÁRIOS
def get_font(size=Typography.SIZE_BODY, weight=Typography.WEIGHT_NORMAL):
    return (Typography.FONT_FAMILY, size, weight)

def get_title_font(size=Typography.SIZE_TITLE_MEDIUM):
    return get_font(size, Typography.WEIGHT_BOLD)

def get_code_font(size=Typography.SIZE_CODE, weight=Typography.WEIGHT_NORMAL):
    """Fonte monoespaçada para expressões lógicas."""
    return (Typography.FONT_CODE, size, weight)

def get_button_style():
    return {
        "font": get_font(Typography.SIZE_BODY),
        "corner_radius": Dimensions.CORNER_RADIUS_MEDIUM,
        "border_width": Dimensions.BORDER_WIDTH_STANDARD,
        "border_color": Colors.BORDER_DEFAULT,
        "width": Dimensions.BUTTON_WIDTH_STANDARD,
        "height": Dimensions.BUTTON_HEIGHT_STANDARD
    }