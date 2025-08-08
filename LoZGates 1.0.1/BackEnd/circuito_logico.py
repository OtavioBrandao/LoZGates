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

def draw_routed_wire(start_pos, end_pos, routing_x, color=WIRE_COLOR):
    (x1, y1), (x2, y2) = start_pos, end_pos 
    pygame.draw.line(screen, color, (x1, y1), (routing_x, y1), 2)
    pygame.draw.line(screen, color, (routing_x, y1), (routing_x, y2), 2)
    pygame.draw.line(screen, color, (routing_x, y2), (x2, y2), 2)

def draw_connection_dot(pos, color=WIRE_COLOR, radius=5):
    pygame.draw.circle(screen, color, pos, radius)


# --- LÓGICA DE DESENHO RECURSIVO ---
def calcular_layout(node, y_start=0):
    """
    PASSAGEM 1: Percorre a AST para calcular a posição e o tamanho vertical de cada nó.
    Retorna um dicionário representando o layout da sub-árvore.
    """
    # CASO BASE: Uma variável é uma "folha" e ocupa uma única pista vertical.
    if isinstance(node, VariableNode) or \
       (isinstance(node, OperatorNode) and node.op == '~' and isinstance(node.children[0], VariableNode)):
        
        #Define o nome do barramento, ex: "P" ou "~P"
        bus_name = node.name if isinstance(node, VariableNode) else f"~{node.children[0].name}"

        return {
            'type': 'leaf',
            'bus_name': bus_name,
            'y_pos': y_start + NODE_V_SPACING / 2, 
            'height': NODE_V_SPACING           
        }

    # PASSO RECURSIVO: Um operador (porta lógica)
    if isinstance(node, OperatorNode):
        child_layouts = []
        current_y_offset = 0
        for child_node in node.children:
            # Calcula o layout para cada filho, um abaixo do outro
            child_layout = calcular_layout(child_node, y_start + current_y_offset)
            child_layouts.append(child_layout)
            current_y_offset += child_layout['height'] # Aumenta o deslocamento para o próximo filho

        total_height = current_y_offset
        # A porta fica no centro vertical do espaço ocupado por todos os seus filhos
        gate_y_pos = y_start + total_height / 2

        return {
            'type': 'gate',
            'op': node.op,
            'y_pos': gate_y_pos,
            'height': total_height,
            'children': child_layouts
        }
    return {}

def desenhar_circuito_recursivo(layout, x_pos, bus_x_coords):
    """
    PASSAGEM 2: Desenha o circuito usando layout pré-calculado e canais de roteamento.
    """
    if layout.get('type') == 'leaf':
        return ('bus', layout['bus_name'], layout['y_pos'])

    if layout.get('type') == 'gate':
        gate_center_y = layout['y_pos']
        gate_top_y = gate_center_y - GATE_HEIGHT / 2
        
        output_pos = None
        if layout['op'] == '*':
            output_pos = draw_and_gate(x_pos, gate_top_y)
        elif layout['op'] == '+':
            output_pos = draw_or_gate(x_pos, gate_top_y)
        elif layout['op'] == '~':
            output_pos = draw_not_gate(x_pos, gate_top_y)

        num_children = len(layout['children'])
        gate_inputs_y = [gate_center_y]
        if num_children > 1:
            gate_inputs_y = [gate_top_y + 20, gate_top_y + GATE_HEIGHT - 20]

        # --- LÓGICA DE ROTEAMENTO ---
        # Define um canal vertical único para TODOS os fios que chegam nesta porta.
        # Ele ficará exatamente no meio do caminho entre este estágio e o anterior.
        routing_x = x_pos - (NODE_H_SPACING / 2)

        for i, child_layout in enumerate(layout['children']):
            child_output = desenhar_circuito_recursivo(child_layout, x_pos - NODE_H_SPACING, bus_x_coords)
            
            input_pos = (x_pos, gate_inputs_y[i])

            if isinstance(child_output, tuple) and child_output[0] == 'bus':
                bus_name = child_output[1]
                bus_x = bus_x_coords[bus_name]
                wire_y = child_output[2]
                start_pos = (bus_x, wire_y)

                draw_routed_wire(start_pos, input_pos, routing_x)
                draw_connection_dot(start_pos)
            else:
                start_pos = child_output
                draw_routed_wire(start_pos, input_pos, routing_x)
        
        return output_pos
    return None
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

    # Parte de desenhar os barramentos
    variaveis = sorted(list(_coletar_variaveis(ast_root)))
    bus_x_coords = {}
    font = pygame.font.Font(None, 36)

    bus_x_start = 30
    bus_pair_spacing = 80
    negated_line_offset = 50

    for i, var_name in enumerate(variaveis):
        true_bus_x = bus_x_start
        pygame.draw.line(screen, WHITE, (true_bus_x, 40), (true_bus_x, screen_height - 40), 2)
        text = font.render(var_name, True, LABEL_COLOR)
        screen.blit(text, (true_bus_x - text.get_width() / 2, 10))
        bus_x_coords[var_name] = true_bus_x

        negated_bus_x = true_bus_x + negated_line_offset
        pygame.draw.line(screen, WHITE, (negated_bus_x, 40), (negated_bus_x, screen_height - 40), 2)
        text = font.render(f"~{var_name}", True, LABEL_COLOR)
        screen.blit(text, (negated_bus_x - text.get_width() / 2, 10))
        bus_x_coords[f"~{var_name}"] = negated_bus_x

        bus_x_start = negated_bus_x + bus_pair_spacing
    

    layout_final = calcular_layout(ast_root, y_start=60)
    x_final_gate = screen_width - NODE_H_SPACING
    final_output_pos = desenhar_circuito_recursivo(layout_final, x_final_gate, bus_x_coords)

    # Desenha o fio de saída final
    if final_output_pos:
        # Se a saída for apenas uma variável vinda de um barramento (ex: expressao = "P")
        if isinstance(final_output_pos, tuple) and final_output_pos[0] == 'bus':
            bus_name = final_output_pos[1]
            bus_x = bus_x_coords[bus_name]
            y_final_gate = final_output_pos[2] # Usar a coordenada Y do layout
            start_pos = (bus_x, y_final_gate)
            pygame.draw.line(screen, WHITE, start_pos, (screen_width - 20, y_final_gate), 3)
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