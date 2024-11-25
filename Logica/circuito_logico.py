import pygame
import sys
from converter import converter_para_algebra_booleana

# Lê a expressão do arquivo
try:
    with open(r"C:\Users\laris\Desktop\Logica\entrada.txt", "r") as file:
        expressao = file.read().strip()
except FileNotFoundError:
    print("O arquivo com a expressão não foi encontrado.")
    sys.exit()
    
# Inicializa o pygame
pygame.init()

# Configurações da tela
screen_width, screen_height = 850, 550
screen = pygame.display.set_mode((screen_width, screen_height))

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
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
    # Para uma curva suave, usamos pygame.draw.lines
    points = [
        (x1, y1),
        control_point1,
        control_point2,
        (x2, y2)
    ]
    pygame.draw.lines(screen, WHITE, False, points, 2)

draws = {
    '&': draw_and_gate,
    '|': draw_or_gate,
    '~': draw_not_gate,
    'L': draw_label}

#Função para conexão da NOT
def porta_nao(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp):
    # Verifique o próximo símbolo na expressão para aplicar a porta NOT a ele
    # Linha antes do not
    if i + 1 < len(expressao_booleana):  # Confirma que há um próximo símbolo
        proximo_simbolo = expressao_booleana[i + 1]

        if proximo_simbolo == "P":
            draw_not_gate(100, y_pos - 90)
            draw_curve(posicoes_variaveis["P"][0] + 10, posicoes_variaveis["P"][1], 100, y_pos - 50)
            Ptemp += 1
            
        elif proximo_simbolo == "Q":
            draw_not_gate(100, y_pos)
            draw_curve(posicoes_variaveis["Q"][0] + 10, posicoes_variaveis["Q"][1], 100, y_pos + 40)
            Qtemp += 1
    
        elif proximo_simbolo == "R":
            draw_not_gate(100, y_pos + 90)
            draw_curve(posicoes_variaveis["R"][0] + 10, posicoes_variaveis["R"][1], 100, y_pos + 120)
            Rtemp += 1
            
        elif proximo_simbolo == "S":
            draw_not_gate(100, y_pos + 180)
            draw_curve(posicoes_variaveis["S"][0] + 10, posicoes_variaveis["S"][1], 100, y_pos + 220)
            Stemp += 1
            
        elif proximo_simbolo == "T":
            draw_not_gate(100, y_pos + 270)
            draw_curve(posicoes_variaveis["T"][0] + 10, posicoes_variaveis["T"][1], 100, y_pos + 310)
            Ttemp += 1
            
    return Ptemp, Qtemp, Rtemp, Stemp, Ttemp
  
#Função para conexão da AND    
def porta_AND(i, simbolo, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp):
    proximo_simbolo = expressao_booleana[i + 1]
    simbolo_anterior = expressao_booleana[i - 1]
   
    if proximo_simbolo == "~" or simbolo_anterior == "~" or simbolo == "~":  
        Ptemp, Qtemp, Rtemp, Stemp, Ttemp = porta_nao(i+1, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
        proximo_simbolo = expressao_booleana[i + 2]
       
    if proximo_simbolo == "P" or simbolo_anterior == "P":
        if Ptemp > 0:
            draw_curve(x_pos - 30, y_pos - 50, x_pos, y_pos + 20)
            Ptemp = 0
        else:   
            draw_curve(posicoes_variaveis["P"][0] + 10, posicoes_variaveis["P"][1], x_pos, y_pos + 20)
        
    if proximo_simbolo == "Q" or simbolo_anterior == "Q":
        if Qtemp > 0:
            draw_curve(x_pos - 30, y_pos + 40, x_pos, y_pos + 30)
            Qtemp = 0                    
        else:
            draw_curve(posicoes_variaveis["Q"][0] + 10, posicoes_variaveis["Q"][1], x_pos, y_pos + 30)
            
    if proximo_simbolo == "R" or simbolo_anterior == "R":
        if Rtemp > 0:
            draw_curve(x_pos - 30, y_pos + 130, x_pos, y_pos + 45)
            Rtemp = 0                    
        else:
            draw_curve(posicoes_variaveis["R"][0] + 10, posicoes_variaveis["R"][1], x_pos, y_pos + 45)
    
    if proximo_simbolo == "S" or simbolo_anterior == "S":
        if Stemp > 0:
            draw_curve(x_pos - 30, y_pos + 220, x_pos, y_pos + 50)
            Stemp = 0                    
        else:
            draw_curve(posicoes_variaveis["S"][0] + 10, posicoes_variaveis["S"][1], x_pos, y_pos + 50)
            
    if proximo_simbolo == "T" or simbolo_anterior == "T":
        if Ttemp > 0:
            draw_curve(x_pos - 30, y_pos + 310, x_pos, y_pos + 60)
            Ttemp = 0                    
        else:
            draw_curve(posicoes_variaveis["T"][0] + 10, posicoes_variaveis["T"][1], x_pos, y_pos + 60)

#Função para conexão da OR
def porta_OR(i, simbolo, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp):
    proximo_simbolo = expressao_booleana[i + 1]
    simbolo_anterior = expressao_booleana[i - 1]
    
    if proximo_simbolo == "~" or simbolo_anterior == "~" or simbolo == "~":  
        Ptemp, Qtemp, Rtemp, Stemp, Ttemp = porta_nao(i+1, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
        proximo_simbolo = expressao_booleana[i + 2]
        
    if proximo_simbolo == "P" or simbolo_anterior == "P":
        if Ptemp > 0:
            draw_curve(x_pos - 30, y_pos - 50, x_pos + 10, y_pos + 20)
            Ptemp = 0
        else:   
            draw_curve(posicoes_variaveis["P"][0] + 10, posicoes_variaveis["P"][1], x_pos + 10, y_pos + 20)
 
    if proximo_simbolo == "Q" or simbolo_anterior == "Q":
        if Qtemp > 0:
            draw_curve(x_pos - 30, y_pos + 40, x_pos + 10, y_pos + 30)
            Qtemp = 0                    
        else:
            draw_curve(posicoes_variaveis["Q"][0] + 10, posicoes_variaveis["Q"][1], x_pos + 10, y_pos + 30)

    if proximo_simbolo == "R" or simbolo_anterior == "R":
        if Rtemp > 0:
            draw_curve(x_pos - 30, y_pos + 120, x_pos + 10, y_pos + 45)
            Rtemp = 0                    
        else:
            draw_curve(posicoes_variaveis["R"][0] + 10, posicoes_variaveis["R"][1], x_pos + 10, y_pos + 45)
    
    if proximo_simbolo == "S" or simbolo_anterior == "S":
        if Stemp > 0:
            draw_curve(x_pos - 30, y_pos + 220, x_pos + 10, y_pos + 50)
            Stemp = 0                    
        else:
            draw_curve(posicoes_variaveis["S"][0] + 10, posicoes_variaveis["S"][1], x_pos + 10, y_pos + 50)
            
    if proximo_simbolo == "T" or simbolo_anterior == "T":
        if Ttemp > 0:
            draw_curve(x_pos - 30, y_pos + 310, x_pos + 10, y_pos + 60)
            Ttemp = 0                    
        else:
            draw_curve(posicoes_variaveis["T"][0] + 10, posicoes_variaveis["T"][1], x_pos + 10, y_pos + 60)

#Função para parenteses
def processa_subexpressao(simbolo, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp):
     
    i = 0

    for index, simbolo in enumerate(expressao_booleana):
        if simbolo == ")":
            #Implementar a logica para ligação das portas lógicas
            draw_curve(x_pos - 90, y_pos + 40, x_pos, y_pos + 40)
            i += 1
            continue #simbolo
            
        elif simbolo == "*":  # Porta AND
            draw_and_gate(x_pos, y_pos)
            porta_AND(i, simbolo, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
            x_pos += 150

        elif simbolo == "+":  # Porta OR
            draw_or_gate(x_pos, y_pos)
            porta_OR(i, simbolo, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
            x_pos += 150

        elif simbolo == "~":  # Porta NOT
            Ptemp, Qtemp, Rtemp, Stemp, Ttemp = porta_nao(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
 
        i += 1


def plotar_circuito_logico(expressao_booleana):
    x_pos = 200  # Posição inicial no eixo X
    y_pos = 150  # Posição base no eixo Y
    posicoes_variaveis = {}  # Dicionário para armazenar posições de P, Q e R
    pilha = []  # Pilha para guardar as variáveis e operadores

    # Desenha variáveis P, Q, R
    font = pygame.font.Font(None, 36)
    for char in expressao_booleana:
        if char == "P" and "P" not in posicoes_variaveis:
            posicoes_variaveis["P"] = (50, 80)
            draw_circle_label(50, 80, "P")
        
        elif char == "Q" and "Q" not in posicoes_variaveis:
            posicoes_variaveis["Q"] = (50, 180)
            draw_circle_label(50, 180, "Q")
    
        elif char == "R" and "R" not in posicoes_variaveis:
            posicoes_variaveis["R"] = (50, 280)
            draw_circle_label(50, 280, "R")
            
        elif char == "S" and "S" not in posicoes_variaveis:
            posicoes_variaveis["S"] = (50, 380)
            draw_circle_label(50, 380, "S")
            
        elif char == "T" and "T" not in posicoes_variaveis:
            posicoes_variaveis["T"] = (50, 480)
            draw_circle_label(50, 480, "T")
            
    Ptemp = 0
    Qtemp = 0
    Rtemp = 0
    Stemp = 0
    Ttemp = 0

    for i, simbolo in enumerate(expressao_booleana):
        
        if "(" in expressao_booleana:
            # Chama a função para processar a subexpressão
            processa_subexpressao(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
            continue
        if simbolo == ")":
            simbolo = expressao_booleana[i+1]
            
        if simbolo == "~":  # Porta NOT
            Ptemp, Qtemp, Rtemp, Stemp, Ttemp = porta_nao(i, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)  
            # Avance o índice para pular o próximo símbolo já processado
            continue  # Pula para a próxima iteração para não processar `proximo_simbolo` novamente
        # Linha dps do NOT
        
        elif simbolo == "*":  # Porta AND
            draw_and_gate(x_pos, y_pos)
            porta_AND(i, simbolo, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
            x_pos += 150
            
        elif simbolo == "+":  # Porta OR
            draw_or_gate(x_pos, y_pos)
            #armazenar = draw_and_gate(x_pos, y_pos)
            #voltar na posiçao_porta -> porta_OR
            porta_OR(i, simbolo, expressao_booleana, x_pos, y_pos, posicoes_variaveis, Ptemp, Qtemp, Rtemp, Stemp, Ttemp)
            x_pos += 150
            

# Loop principal
expressao_booleana = converter_para_algebra_booleana(expressao)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)  # Limpa a tela
    plotar_circuito_logico(expressao_booleana)  # Desenha o circuito com base na expressão
    pygame.display.flip()  # Atualiza a tela
            #Para printar o resultado no nome do programa
    titulo = f"Circuito Lógico"
    #print(resultado)
    pygame.display.set_caption(titulo.center(50))
    icon = pygame.image.load(r"C:\Users\laris\Desktop\Logica\icon.png")

    # Define o ícone da janela
    pygame.display.set_icon(icon)

pygame.quit()
sys.exit()