import pygame
import sys

# Inicializa o pygame
pygame.init()

# Configurações da tela
screen_width, screen_height = 800, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Circuito Lógico")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Funções de desenho das portas lógicas
def draw_and_gate(x, y):
    pygame.draw.line(screen, BLACK, (x, y), (x, y + 80), 5)
    pygame.draw.line(screen, BLACK, (x, y), (x + 40, y), 5)
    pygame.draw.line(screen, BLACK, (x, y + 80), (x + 40, y + 80), 5)
    pygame.draw.arc(screen, BLACK, (x + 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.line(screen, BLACK, (x + 60, y + 40), (x + 80, y + 40), 5)

def draw_or_gate(x, y):
    pygame.draw.line(screen, BLACK, (x, y), (x + 40, y), 5)
    pygame.draw.line(screen, BLACK, (x, y + 80), (x + 40, y + 80), 5)
    pygame.draw.arc(screen, BLACK, (x + 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.arc(screen, BLACK, (x - 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.line(screen, BLACK, (x + 60, y + 40), (x + 80, y + 40), 5)

def draw_not_gate(x, y):
    pygame.draw.polygon(screen, BLACK, [(x, y), (x, y + 80), (x + 50, y + 40)], 5)
    pygame.draw.circle(screen, BLACK, (x + 60, y + 40), 10, 5)

# Função de desenho dos átomos
def draw_circle_label(x, y, label):
    pygame.draw.circle(screen, BLACK, (x, y), 10)
    font = pygame.font.Font(None, 36)
    text = font.render(label, True, BLACK)
    screen.blit(text, (x - 10, y + 10))

# Função para desenhar as linhas
def draw_line(x1, y1, x2, y2):
    pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)

# Função de conversão para álgebra booleana
def converter_para_algebra_booleana(expressao):
    resultado = ""  # String para armazenar o resultado

    i = 0
    while i < len(expressao):
        caracter = expressao[i]

        if caracter in 'PQR':
            resultado += caracter  # Adiciona a variável diretamente
        elif caracter == '!':
            if i + 1 < len(expressao) and expressao[i + 1] == '(':
                resultado += "~("  # Negação de expressão complexa
            else:
                resultado += "~"  # Negação de variável
        elif caracter == '&':
            resultado += "*"
        elif caracter == '|':
            resultado += "+"
        elif caracter == '>':
            # Converter A > B para (~A + B)
            if i > 0 and expressao[i - 1] in 'PQR' and i + 1 < len(expressao) and expressao[i + 1] in 'PQR':
                # Remove o último caractere do resultado temporário (variável antes do >)
                resultado = resultado[:-1]
                resultado += f"(~{expressao[i - 1]}+{expressao[i + 1]})"
                i += 1  # Pula a variável após o >
            elif i + 1 < len(expressao) and expressao[i + 1] == '!':
                if i > 0 and expressao[i - 1] in 'PQR' and i + 2 < len(expressao) and expressao[i + 2] in 'PQR':
                    resultado = resultado[:-1]  # Remove o último caractere do resultado temporário
                    resultado += f"(~{expressao[i - 1]}+~{expressao[i + 2]})"
                    i += 2  # Pula a variável após o !
            elif i + 1 < len(expressao) and expressao[i + 1] == '(':
                if i + 2 < len(expressao) and expressao[i + 2] in 'PQR':
                    resultado = resultado[:-1]  # Remove o último caractere do resultado temporário
                    resultado += f"{expressao[i - 1]}+({expressao[i + 2]}"
                    i += 2  # Pula a variável após o >
        elif caracter in '()':
            resultado += caracter  # Adiciona parênteses diretamente

        i += 1

    print("Expressão em Álgebra Booleana:", resultado)
    return resultado

# Função para desenhar o circuito com base na expressão booleana
def plotar_circuito_logico(expressao_booleana):
    x_pos = 200  # Posição inicial no eixo X
    y_pos = 150  # Posição base no eixo Y
    posicoes_variaveis = {}  # Dicionário para armazenar posições de P, Q e R

    # Desenha variáveis P, Q, R
    font = pygame.font.Font(None, 36)
    for char in expressao_booleana:
        if char == "P" and "P" not in posicoes_variaveis:
            draw_circle_label(50, 150, "P")
            posicoes_variaveis["P"] = (50, 150)
        elif char == "Q" and "Q" not in posicoes_variaveis:
            draw_circle_label(50, 250, "Q")
            posicoes_variaveis["Q"] = (50, 250)
        elif char == "R" and "R" not in posicoes_variaveis:
            draw_circle_label(50, 350, "R")
            posicoes_variaveis["R"] = (50, 350)

    #PRECISA IMPLEMENTAR TODOS OS CENÁRIOS POSSÍVEIS, EXEMPLO: Generalizar os atomos, e seguir a ordem da expressão, (esquerda para direita), ou seja, tem que
    #atualizar a posição das linhas, que não usa apenas 
    for simbolo in expressao_booleana:
        if simbolo == "*":  # Porta AND
            draw_and_gate(x_pos, y_pos)
            draw_line(posicoes_variaveis["P"][0] + 10, posicoes_variaveis["P"][1], x_pos, y_pos + 20)
            draw_line(posicoes_variaveis["Q"][0] + 10, posicoes_variaveis["Q"][1], x_pos, y_pos + 60)
            x_pos += 150
            
        elif simbolo == "+":  # Porta OR
            draw_or_gate(x_pos, y_pos)
            draw_line(posicoes_variaveis["P"][0] + 10, posicoes_variaveis["P"][1], x_pos, y_pos + 20)
            draw_line(posicoes_variaveis["Q"][0] + 10, posicoes_variaveis["Q"][1], x_pos, y_pos + 60)
            x_pos += 150

        elif simbolo == "~":  # Porta NOT
            draw_not_gate(100, y_pos + 100)
            draw_line(posicoes_variaveis["R"][0] + 10, posicoes_variaveis["R"][1], x_pos, y_pos + 40)
            x_pos += 150

# Loop principal
expressao = input("Digite uma expressão proposicional (ex: P&Q|R):\n")
expressao_booleana = converter_para_algebra_booleana(expressao)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)  # Limpa a tela
    plotar_circuito_logico(expressao_booleana)  # Desenha o circuito com base na expressão
    pygame.display.flip()  # Atualiza a tela

pygame.quit()
sys.exit()
