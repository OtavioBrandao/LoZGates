# Design Tokens - Sistema de Design Unificado para LoZ Gates
# Centraliza cores, fontes, espaçamentos e outros valores visuais

# PALETA DE CORES
class Colors:
    PRIMARY_BG     = "#0D0D0F"      # Preto tech
    SURFACE_DARK   = "#24242E"      # Cinza escuro
    SURFACE_MEDIUM = "#26262E"      # Cinza médio
    SURFACE_LIGHT  = "#33333D"      # Cinza claro
    
    # Cores de destaque
    ACCENT_CYAN = "#65E6FD"         # Ciano elétrico
    ACCENT_GOLD = "#D3C724"         # Pink neon
    ACCENT_GOLD_HOVER = "#837215"   # Pink hover
    
    # Cores de texto
    TEXT_PRIMARY = "#FFFFFF"        # Branco
    TEXT_SECONDARY = "#CCCCCC"      # Cinza claro
    TEXT_ACCENT = "#00FFFF"         # Ciano brilhante
    
    # Cores de botões padrão
    BUTTON_PRIMARY = "#00D9FF"      # Ciano elétrico
    BUTTON_PRIMARY_HOVER = "#5CE2FA" # Ciano hover
    BUTTON_TEXT = "#000000"         # Preto para contraste
    
    # Cores de estado
    SUCCESS = "#09BB62"             # Verde neon
    WARNING = "#BBA424"             # Ouro neon
    ERROR = "#961730"               # Vermelho neon
    INFO = "#00D9FF"                # Ciano neon
    
    # Bordas
    BORDER_DEFAULT = "#444444"
    BORDER_ACCENT = "#00D9FF"

    # Bordas
    BORDER_DEFAULT = "#4682B4"
    BORDER_ACCENT = "#00BFFF"
# TIPOGRAFIA
class Typography:
    FONT_FAMILY = "Segoe UI"
    
    # Tamanhos
    SIZE_TITLE_LARGE = 28
    SIZE_TITLE_MEDIUM = 24
    SIZE_TITLE_SMALL = 20
    SIZE_SUBTITLE = 18
    SIZE_BODY = 16
    SIZE_BODY_SMALL = 14
    SIZE_CAPTION = 12
    
    # Pesos
    WEIGHT_BOLD = "bold"
    WEIGHT_NORMAL = "normal"

# ESPAÇAMENTOS
class Spacing:
    # Padding/Margin
    XS = 5
    SM = 10
    MD = 15
    LG = 20
    XL = 30
    XXL = 40
    
    # Espaçamentos específicos
    BUTTON_PADDING_X = 12
    BUTTON_PADDING_Y = 15
    FRAME_PADDING = 20
    SECTION_SPACING = 25

# DIMENSÕES
class Dimensions:
    # Botões
    BUTTON_WIDTH_STANDARD = 200
    BUTTON_WIDTH_SMALL = 120
    BUTTON_WIDTH_LARGE = 250
    BUTTON_HEIGHT_STANDARD = 50
    BUTTON_HEIGHT_SMALL = 45
    
    # Bordas arredondadas
    CORNER_RADIUS_SMALL = 10
    CORNER_RADIUS_MEDIUM = 15
    CORNER_RADIUS_LARGE = 25
    
    # Bordas
    BORDER_WIDTH_THIN = 1
    BORDER_WIDTH_STANDARD = 2
    BORDER_WIDTH_THICK = 3

# CONFIGURAÇÕES DE ABAS
class TabConfig:
    # Cores das abas
    SELECTED_COLOR = "#4441F7"
    SELECTED_HOVER = "#0B1658"
    UNSELECTED_COLOR = "#001E44"
    UNSELECTED_HOVER = "#4682B4"
    BACKGROUND_COLOR = "#FFFFFF"

# UTILITÁRIOS
def get_font(size=Typography.SIZE_BODY, weight=Typography.WEIGHT_NORMAL):
    """Retorna tupla de fonte padronizada"""
    return (Typography.FONT_FAMILY, size, weight)

def get_title_font(size=Typography.SIZE_TITLE_MEDIUM):
    """Retorna fonte para títulos"""
    return get_font(size, Typography.WEIGHT_BOLD)

def get_button_style():
    """Retorna estilo padrão para botões customizados"""
    return {
        "font": get_font(Typography.SIZE_BODY),
        "corner_radius": Dimensions.CORNER_RADIUS_MEDIUM,
        "border_width": Dimensions.BORDER_WIDTH_STANDARD,
        "border_color": Colors.BORDER_DEFAULT,
        "width": Dimensions.BUTTON_WIDTH_STANDARD,
        "height": Dimensions.BUTTON_HEIGHT_STANDARD
    }