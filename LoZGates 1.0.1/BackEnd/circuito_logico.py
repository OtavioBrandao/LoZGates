import pygame
import sys
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.imagem import converte_matrix_para_pygame_imagem_endeota
import os
from config import ASSETS_PATH

# --- Classes de Nó da AST ---
class Node:
    pass

class VariableNode(Node):
    def __init__(self, name):
        self.name = name

class OperatorNode(Node):
    def __init__(self, op, children):
        self.op = op
        self.children = children

# Essa função converte a expressão em uma estrutura de árvore.
def criar_ast_de_expressao(expressao):
    tokens = list(expressao.replace(" ", ""))
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def consume():
        nonlocal pos
        pos += 1
        return tokens[pos - 1]

    def parse_factor():
        token = peek()
        if token.isalpha():
            return VariableNode(consume())
        elif token == '~':
            consume()
            if peek() == '(':
                consume()
                expr = parse_expression()
                if peek() != ')': raise ValueError("Parêntese não fechado")
                consume()
                return OperatorNode('~', [expr])
            return OperatorNode('~', [parse_factor()])
        elif token == '(':
            consume()
            expr = parse_expression()
            if peek() != ')': raise ValueError("Parêntese não fechado")
            consume()
            return expr
        raise ValueError(f"Token inválido: {token}")

    def parse_term():
        node = parse_factor()
        while peek() == '*':
            op = consume()
            right = parse_factor()
            node = OperatorNode(op, [node, right])
        return node

    def parse_expression():
        node = parse_term()
        while peek() == '+':
            op = consume()
            right = parse_term()
            node = OperatorNode(op, [node, right])
        return node

    return parse_expression()


# --- CONFIGURAÇÃO DO PYGAME ---
try:
    caminho_entrada = os.path.join(ASSETS_PATH, "entrada.txt")
    with open(caminho_entrada, "r", encoding="utf-8") as file:
        expressao = file.read().strip()
    if not expressao:
        raise FileNotFoundError
except FileNotFoundError:
    expressao = "P*~(Q+R)"
    print(f"Arquivo 'entrada.txt' não encontrado ou vazio. Usando expressão de exemplo: {expressao}")

pygame.init()

# Configurações da tela
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gerador de Circuitos Lógicos")

# Cores e Constantes
BACKGROUND = (0, 0, 0)
WHITE = (230, 230, 230)
BLUE = (60, 120, 220)
GREEN = (50, 200, 130)
ORANGE = (250, 170, 70)
LABEL_COLOR = (255, 255, 255)
WIRE_COLOR = (200, 200, 200)

GATE_WIDTH = 60
GATE_HEIGHT = 80
NODE_H_SPACING = 180
NODE_V_SPACING = 100

def draw_and_gate(x, y):
    rect = pygame.Rect(x, y, GATE_WIDTH - 20, GATE_HEIGHT)
    pygame.draw.line(screen, BLUE, rect.topleft, rect.bottomleft, 3)
    pygame.draw.arc(screen, BLUE, rect, -1.57, 1.57, 3)
    pygame.draw.line(screen, BLUE, rect.topleft, (rect.centerx, rect.top), 3)
    pygame.draw.line(screen, BLUE, rect.bottomleft, (rect.centerx, rect.bottom), 3)
    return (rect.right, rect.centery)

def draw_or_gate(x, y):
    rect = pygame.Rect(x, y, GATE_WIDTH - 20, GATE_HEIGHT)
    back_rect = pygame.Rect(x - 15, y, 20, GATE_HEIGHT)
    pygame.draw.arc(screen, GREEN, back_rect, -1.57, 1.57, 3)
    pygame.draw.arc(screen, GREEN, rect, -1.57, 1.57, 3)
    pygame.draw.line(screen, GREEN, (back_rect.centerx, back_rect.top), (rect.centerx, rect.top), 3)
    pygame.draw.line(screen, GREEN, (back_rect.centerx, back_rect.bottom), (rect.centerx, rect.bottom), 3)
    return (rect.right, rect.centery)

def draw_not_gate(x, y):
    center_y = y + GATE_HEIGHT / 2
    p1 = (x, y + 15)
    p2 = (x, y + GATE_HEIGHT - 15)
    p3 = (x + 30, center_y)
    pygame.draw.polygon(screen, ORANGE, [p1, p2, p3], 3)
    pygame.draw.circle(screen, ORANGE, (x + 38, center_y), 8, 3)
    return (x + 46, center_y)

def draw_wire(start_pos, end_pos, color=WIRE_COLOR):
    (x1, y1), (x2, y2) = start_pos, end_pos
    mid_x = x1 + (x2 - x1) * 0.5
    pygame.draw.line(screen, color, (x1, y1), (mid_x, y1), 2)
    pygame.draw.line(screen, color, (mid_x, y1), (mid_x, y2), 2)
    pygame.draw.line(screen, color, (mid_x, y2), (x2, y2), 2)

def draw_connection_dot(pos, color=WIRE_COLOR, radius=5):
    pygame.draw.circle(screen, color, pos, radius)


# --- LÓGICA DE DESENHO RECURSIVO ---
def processa_subexpressao(node, x_pos, y_pos, bus_x_coords):
    """
    Processa recursivamente um nó da AST para desenhar o circuito.
    Retorna a coordenada (x, y) de sua conexão de saída.
    """
    # CASO BASE 1: Variável simples (ex: 'P')
    if isinstance(node, VariableNode):
        return ('bus', node.name)

    # CASO BASE 2: NOT em uma variável simples (ex: '~P')
    if isinstance(node, OperatorNode) and node.op == '~' and isinstance(node.children[0], VariableNode):
        var_name = node.children[0].name
        return ('bus', f"~{var_name}")

    # PASSO RECURSIVO: Nó de operador com sub-expressões
    if isinstance(node, OperatorNode):
        num_children = len(node.children)
        y_offset_start = y_pos - (num_children - 1) * NODE_V_SPACING / 2
        child_outputs = []
        for i, child_node in enumerate(node.children):
            y_child = y_offset_start + i * NODE_V_SPACING
            output = processa_subexpressao(child_node, x_pos - NODE_H_SPACING, y_child, bus_x_coords)
            child_outputs.append(output)

        gate_y_pos = y_pos - GATE_HEIGHT / 2
        output_pos = None
        if node.op == '*':
            output_pos = draw_and_gate(x_pos, gate_y_pos)
        elif node.op == '+':
            output_pos = draw_or_gate(x_pos, gate_y_pos)
        elif node.op == '~': # Para negações complexas como ~(P*Q)
            output_pos = draw_not_gate(x_pos, gate_y_pos)
        else:
            raise ValueError(f"Operador desconhecido: {node.op}")

        gate_inputs_y = [y_pos]
        if num_children > 1:
            gate_inputs_y = [gate_y_pos + 20, gate_y_pos + GATE_HEIGHT - 20]

        for i, child_out in enumerate(child_outputs):
            input_pos = (x_pos, gate_inputs_y[i])

            if isinstance(child_out, tuple) and child_out[0] == 'bus':
                bus_name = child_out[1]
                bus_x = bus_x_coords[bus_name]
                start_pos = (bus_x, input_pos[1])
                draw_wire(start_pos, input_pos)
                draw_connection_dot(start_pos)
            else: # A entrada vem de outra porta, não de um barramento
                start_pos = child_out
                draw_wire(start_pos, input_pos)

        return output_pos

def _coletar_variaveis(node):
    if isinstance(node, VariableNode):
        return {node.name}
    if isinstance(node, OperatorNode):
        vars = set()
        for child in node.children:
            vars.update(_coletar_variaveis(child))
        return vars
    return set()

def plotar_circuito_logico(expressao_booleana):
    """Função principal do desenho."""
    try:
        ast_root = criar_ast_de_expressao(expressao_booleana)
    except ValueError as e:
        print(f"Erro ao analisar a expressão: {e}")
        font = pygame.font.Font(None, 40)
        text = font.render(f"Erro: {e}", True, (255, 80, 80))
        text_rect = text.get_rect(center=(screen_width/2, screen_height/2))
        screen.blit(text, text_rect)
        return

    variaveis = sorted(list(_coletar_variaveis(ast_root)))
    bus_x_coords = {}
    font = pygame.font.Font(None, 36)

    bus_x_start = 80
    bus_pair_spacing = 100 # Espaço entre pares de variáveis (ex: entre 'A' e 'B')
    negated_line_offset = 50 # Espaço entre a linha 'A' e '~A'

    for i, var_name in enumerate(variaveis):
        # 1. Desenha o barramento principal (variável verdadeira)
        true_bus_x = bus_x_start
        pygame.draw.line(screen, WHITE, (true_bus_x, 40), (true_bus_x, screen_height - 40), 2)
        text = font.render(var_name, True, LABEL_COLOR)
        screen.blit(text, (true_bus_x - text.get_width() / 2, 10))
        bus_x_coords[var_name] = true_bus_x

        # 2. Desenha o barramento negado (sem a porta NOT)
        negated_bus_x = true_bus_x + negated_line_offset
        pygame.draw.line(screen, WHITE, (negated_bus_x, 40), (negated_bus_x, screen_height - 40), 2)
        text = font.render(f"~{var_name}", True, LABEL_COLOR)
        screen.blit(text, (negated_bus_x - text.get_width() / 2, 10))
        bus_x_coords[f"~{var_name}"] = negated_bus_x

        # 3. Ajusta a posição para o próximo par de barramentos
        bus_x_start = negated_bus_x + bus_pair_spacing

    # Inicia o processo de desenho recursivo
    x_final_gate = screen_width - NODE_H_SPACING
    y_final_gate = screen_height / 2
    final_output_pos = processa_subexpressao(ast_root, x_final_gate, y_final_gate, bus_x_coords)

    # Desenha o fio de saída final
    if final_output_pos:
        # Se a saída for apenas uma variável vinda de um barramento
        if isinstance(final_output_pos, tuple) and final_output_pos[0] == 'bus':
            bus_name = final_output_pos[1]
            bus_x = bus_x_coords[bus_name]
            start_pos = (bus_x, y_final_gate)
            # Desenha o fio de saída
            pygame.draw.line(screen, WHITE, start_pos, (screen_width - 20, y_final_gate), 3)
            # NOVA ALTERAÇÃO: Adiciona o ponto de conexão na saída final
            draw_connection_dot(start_pos, color=WHITE)
        else: # Se a saída vem de uma porta
            pygame.draw.line(screen, WHITE, final_output_pos, (final_output_pos[0] + 50, final_output_pos[1]), 3)


# --- EXECUÇÃO PRINCIPAL ---
expressao_booleana = converter_para_algebra_booleana(expressao)

screen.fill(BACKGROUND)
plotar_circuito_logico(expressao_booleana)

caminho_imagem = os.path.join(ASSETS_PATH, "circuito.png")
pygame.image.save(screen, caminho_imagem)
print(f"Circuito modificado salvo como imagem em: {caminho_imagem}")

pygame.quit()
sys.exit()