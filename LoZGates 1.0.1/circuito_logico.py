import pygame
import sys
from converter import converter_para_algebra_booleana
from imagem import converte_matrix_para_pygame_imagem_endeota

# Lê a expressão do arquivo
try:
    with open("entrada.txt", "r") as file:
        expressao = file.read().strip()
except FileNotFoundError:
    print("O arquivo com a expressão não foi encontrado no circuito_logico.")
    sys.exit()

# Inicializa o pygame
pygame.init()

# Configurações da tela
screen_width, screen_height = 850, 550
screen = pygame.display.set_mode((screen_width, screen_height))

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# Funções de desenho das portas lógicas
def draw_and_gate(x, y):
    pygame.draw.line(screen, BLUE, (x, y), (x, y + 80), 5)
    pygame.draw.line(screen, BLUE, (x, y), (x + 40, y), 5)
    pygame.draw.line(screen, BLUE, (x, y + 80), (x + 40, y + 80), 5)
    pygame.draw.arc(screen, BLUE, (x + 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.line(screen, WHITE, (x + 60, y + 40), (x + 80, y + 40), 2)

def draw_or_gate(x, y):
    pygame.draw.line(screen, GREEN, (x, y), (x + 40, y), 5)
    pygame.draw.line(screen, GREEN, (x, y + 80), (x + 40, y + 80), 5)
    pygame.draw.arc(screen, GREEN, (x + 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.arc(screen, GREEN, (x - 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.line(screen, WHITE, (x + 60, y + 40), (x + 80, y + 40), 2)

def draw_not_gate(x, y):
    pygame.draw.polygon(screen, ORANGE, [(x, y), (x, y + 80), (x + 50, y + 40)], 5)
    pygame.draw.circle(screen, ORANGE, (x + 60, y + 40), 10, 5)

# Função de desenho dos átomos
def draw_circle_label(x, y, label):
    pygame.draw.circle(screen, WHITE, (x, y), 10)
    font = pygame.font.Font(None, 36)
    text = font.render(label, True, WHITE)
    screen.blit(text, (x - 10, y + 10))

# Função para desenhar as linhas
def draw_line(x1, y1, x2, y2):
    pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2), 4)

def draw_label(x, y, text):
    font = pygame.font.Font(None, 36)
    text = font.render(text, True, BLACK)
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect.topleft)

# Função para desenhar uma curva suave entre dois pontos
def draw_curve(x1, y1, x2, y2):
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2
    control_point1 = (mid_x, y1)
    control_point2 = (mid_x, y2)
    points = [(x1, y1), control_point1, control_point2, (x2, y2)]
    pygame.draw.lines(screen, WHITE, False, points, 2)

# Função para aplicar a distributiva do NOT sobre parênteses
def aplicar_distributiva_not(expressao):
    i = 0
    resultado = ""
    while i < len(expressao):
        if expressao[i] == '~' and i + 1 < len(expressao) and expressao[i + 1] == '(':
            # Encontramos um NOT antes de um parêntese
            resultado += "~("
            i += 2
            nivel = 1
            while i < len(expressao) and nivel > 0:
                if expressao[i] == '(':
                    nivel += 1
                elif expressao[i] == ')':
                    nivel -= 1
                if nivel > 0:
                    resultado += expressao[i]
                i += 1
            resultado += ")"
        else:
            resultado += expressao[i]
            i += 1
    return resultado

# Função para conexão da NOT
def porta_nao(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts):
    if i + 1 < len(expressao_booleana):
        proximo_simbolo = expressao_booleana[i + 1]
        if proximo_simbolo in posicoes_variaveis:
            draw_not_gate(100, y_pos - 90 + (ord(proximo_simbolo) - ord('P')) * 90)
            draw_curve(posicoes_variaveis[proximo_simbolo][0] + 10, posicoes_variaveis[proximo_simbolo][1], 100, y_pos - 50 + (ord(proximo_simbolo) - ord('P')) * 90)
            temp_counts[proximo_simbolo] += 1
    return temp_counts

# Função para conexão da AND
def porta_AND(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts):
    simbolo_anterior = expressao_booleana[i - 1] if i > 0 else None
    proximo_simbolo = expressao_booleana[i + 1] if i + 1 < len(expressao_booleana) else None

    if proximo_simbolo == "~" or simbolo_anterior == "~":
        temp_counts = porta_nao(i + 1, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts)
        proximo_simbolo = expressao_booleana[i + 2] if i + 2 < len(expressao_booleana) else None

    for simbolo in [simbolo_anterior, proximo_simbolo]:
        if simbolo in posicoes_variaveis:
            if temp_counts[simbolo] > 0:
                draw_curve(x_pos - 30, y_pos - 50 + (ord(simbolo) - ord('P')) * 90, x_pos, y_pos + 20)
                temp_counts[simbolo] = 0
            else:
                draw_curve(posicoes_variaveis[simbolo][0] + 10, posicoes_variaveis[simbolo][1], x_pos, y_pos + 20)

# Função para conexão da OR
def porta_OR(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts):
    simbolo_anterior = expressao_booleana[i - 1] if i > 0 else None
    proximo_simbolo = expressao_booleana[i + 1] if i + 1 < len(expressao_booleana) else None

    if proximo_simbolo == "~" or simbolo_anterior == "~":
        temp_counts = porta_nao(i + 1, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts)
        proximo_simbolo = expressao_booleana[i + 2] if i + 2 < len(expressao_booleana) else None

    for simbolo in [simbolo_anterior, proximo_simbolo]:
        if simbolo in posicoes_variaveis:
            if temp_counts[simbolo] > 0:
                draw_curve(x_pos - 30, y_pos - 50 + (ord(simbolo) - ord('P')) * 90, x_pos + 10, y_pos + 20)
                temp_counts[simbolo] = 0
            else:
                draw_curve(posicoes_variaveis[simbolo][0] + 10, posicoes_variaveis[simbolo][1], x_pos + 10, y_pos + 20)

# Função para processar subexpressões
def processa_subexpressao(expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts):
    i = 0
    while i < len(expressao_booleana):
        simbolo = expressao_booleana[i]
        if simbolo == ")":
            draw_curve(x_pos - 90, y_pos + 40, x_pos, y_pos + 40)
        elif simbolo == "*":
            draw_and_gate(x_pos, y_pos)
            porta_AND(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts)
            x_pos += 150
        elif simbolo == "+":
            draw_or_gate(x_pos, y_pos)
            porta_OR(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts)
            x_pos += 150
        elif simbolo == "~":
            temp_counts = porta_nao(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts)
        i += 1

def plotar_circuito_logico(expressao_booleana):
    x_pos = 200
    y_pos = 150
    posicoes_variaveis = {}
    temp_counts = {"P": 0, "Q": 0, "R": 0, "S": 0, "T": 0}

    # Aplicar distributiva do NOT sobre parênteses
    expressao_booleana = aplicar_distributiva_not(expressao_booleana)

    # Desenha variáveis P, Q, R, S, T
    for char in expressao_booleana:
        if char in ["P", "Q", "R", "S", "T"] and char not in posicoes_variaveis:
            posicoes_variaveis[char] = (50, 80 + (ord(char) - ord('P')) * 100)
            draw_circle_label(50, 80 + (ord(char) - ord('P')) * 100, char)

    processa_subexpressao(expressao_booleana, x_pos, y_pos, posicoes_variaveis, temp_counts)

# Loop principal
expressao_booleana = converter_para_algebra_booleana(expressao)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    plotar_circuito_logico(expressao_booleana)
    pygame.display.flip()

    titulo = "Circuito Lógico"
    pygame.display.set_caption(titulo.center(50))

    bytes_per_row = 19
    icon = converte_matrix_para_pygame_imagem_endeota(bytes_per_row)
    pygame.display.set_icon(icon)

pygame.quit()
sys.exit()
