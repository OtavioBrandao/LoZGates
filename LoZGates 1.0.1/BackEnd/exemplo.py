import pygame
import sys
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.imagem import converte_matrix_para_pygame_imagem_endeota
import os
from config import ASSETS_PATH
import math

# --- Classes de Nó da AST ---
class Node:
    pass

class VariableNode(Node):
    def _init_(self, name):
        self.name = name

class OperatorNode(Node):
    def _init_(self, op, children):
        self.op = op
        self.children = children

# --- Classe para gerenciar a câmera/viewport ---
class Camera:
    def _init_(self, screen_width, screen_height):
        self.x = 0  # Posição da câmera no mundo
        self.y = 0
        self.zoom = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 3.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Velocidade de movimento
        self.move_speed = 5
        self.zoom_speed = 0.1
        
        # Para arrastar com mouse
        self.dragging = False
        self.last_mouse_pos = (0, 0)
    
    def world_to_screen(self, world_pos):
        """Converte coordenadas do mundo para coordenadas da tela"""
        world_x, world_y = world_pos
        screen_x = (world_x - self.x) * self.zoom + self.screen_width / 2
        screen_y = (world_y - self.y) * self.zoom + self.screen_height / 2
        return (int(screen_x), int(screen_y))
    
    def screen_to_world(self, screen_pos):
        """Converte coordenadas da tela para coordenadas do mundo"""
        screen_x, screen_y = screen_pos
        world_x = (screen_x - self.screen_width / 2) / self.zoom + self.x
        world_y = (screen_y - self.screen_height / 2) / self.zoom + self.y
        return (world_x, world_y)
    
    def move(self, dx, dy):
        """Move a câmera"""
        self.x += dx / self.zoom
        self.y += dy / self.zoom
    
    def zoom_at(self, screen_pos, zoom_delta):
        """Faz zoom mantendo o ponto da tela fixo"""
        world_pos = self.screen_to_world(screen_pos)
        
        old_zoom = self.zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom + zoom_delta))
        
        # Ajusta a posição da câmera para manter o ponto fixo
        zoom_ratio = self.zoom / old_zoom
        self.x = world_pos[0] - (world_pos[0] - self.x) * zoom_ratio
        self.y = world_pos[1] - (world_pos[1] - self.y) * zoom_ratio
    
    def handle_event(self, event):
        """Processa eventos relacionados à navegação"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo
                self.dragging = True
                self.last_mouse_pos = event.pos
            elif event.button == 4:  # Scroll up
                self.zoom_at(event.pos, self.zoom_speed)
            elif event.button == 5:  # Scroll down
                self.zoom_at(event.pos, -self.zoom_speed)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.move(-dx, -dy)  # Invertido para movimento natural
                self.last_mouse_pos = event.pos

# --- Classe para desenhar elementos escaláveis ---
class CircuitDrawer:
    def _init_(self, screen, camera):
        self.screen = screen
        self.camera = camera
        
        # Cores
        self.BACKGROUND = (0, 0, 0)
        self.WHITE = (230, 230, 230)
        self.BLUE = (60, 120, 220)
        self.GREEN = (50, 200, 130)
        self.ORANGE = (250, 170, 70)
        self.LABEL_COLOR = (255, 255, 255)
        self.WIRE_COLOR = (200, 200, 200)
        
        # Dimensões base (no mundo)
        self.GATE_WIDTH = 60
        self.GATE_HEIGHT = 80
        self.NODE_H_SPACING = 180
        self.NODE_V_SPACING = 100
    
    def draw_line(self, start_world, end_world, color, width=2):
        """Desenha uma linha do mundo para a tela"""
        start_screen = self.camera.world_to_screen(start_world)
        end_screen = self.camera.world_to_screen(end_world)
        scaled_width = max(1, int(width * self.camera.zoom))
        pygame.draw.line(self.screen, color, start_screen, end_screen, scaled_width)
    
    def draw_circle(self, center_world, radius, color, width=0):
        """Desenha um círculo do mundo para a tela"""
        center_screen = self.camera.world_to_screen(center_world)
        scaled_radius = max(1, int(radius * self.camera.zoom))
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.circle(self.screen, color, center_screen, scaled_radius, scaled_width)
    
    def draw_polygon(self, points_world, color, width=0):
        """Desenha um polígono do mundo para a tela"""
        points_screen = [self.camera.world_to_screen(p) for p in points_world]
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.polygon(self.screen, color, points_screen, scaled_width)
    
    def draw_text(self, text, pos_world, font_size=36, color=None):
        """Desenha texto escalável"""
        if color is None:
            color = self.LABEL_COLOR
        
        scaled_font_size = max(8, int(font_size * self.camera.zoom))
        font = pygame.font.Font(None, scaled_font_size)
        text_surface = font.render(text, True, color)
        
        pos_screen = self.camera.world_to_screen(pos_world)
        text_rect = text_surface.get_rect(center=pos_screen)
        self.screen.blit(text_surface, text_rect)
    
    def draw_and_gate(self, world_x, world_y):
        """Desenha porta AND"""
        w, h = self.GATE_WIDTH - 20, self.GATE_HEIGHT
        
        # Desenha as linhas da porta AND
        self.draw_line((world_x, world_y), (world_x, world_y + h), self.BLUE, 3)
        self.draw_line((world_x, world_y), (world_x + w/2, world_y), self.BLUE, 3)
        self.draw_line((world_x, world_y + h), (world_x + w/2, world_y + h), self.BLUE, 3)
        
        # Arco da direita
        center = (world_x + w/2, world_y + h/2)
        # Aproximação do arco com linhas
        for i in range(16):
            angle1 = -math.pi/2 + (i * math.pi/16)
            angle2 = -math.pi/2 + ((i+1) * math.pi/16)
            x1 = center[0] + (w/2) * math.cos(angle1)
            y1 = center[1] + (h/2) * math.sin(angle1)
            x2 = center[0] + (w/2) * math.cos(angle2)
            y2 = center[1] + (h/2) * math.sin(angle2)
            self.draw_line((x1, y1), (x2, y2), self.BLUE, 3)
        
        return (world_x + w, world_y + h/2)
    
    def draw_or_gate(self, world_x, world_y):
        """Desenha porta OR"""
        w, h = self.GATE_WIDTH - 20, self.GATE_HEIGHT
        
        # Arco traseiro
        back_center = (world_x - 7.5, world_y + h/2)
        for i in range(16):
            angle1 = -math.pi/2 + (i * math.pi/16)
            angle2 = -math.pi/2 + ((i+1) * math.pi/16)
            x1 = back_center[0] + 10 * math.cos(angle1)
            y1 = back_center[1] + (h/2) * math.sin(angle1)
            x2 = back_center[0] + 10 * math.cos(angle2)
            y2 = back_center[1] + (h/2) * math.sin(angle2)
            self.draw_line((x1, y1), (x2, y2), self.GREEN, 3)
        
        # Arco frontal
        front_center = (world_x + w/2, world_y + h/2)
        for i in range(16):
            angle1 = -math.pi/2 + (i * math.pi/16)
            angle2 = -math.pi/2 + ((i+1) * math.pi/16)
            x1 = front_center[0] + (w/2) * math.cos(angle1)
            y1 = front_center[1] + (h/2) * math.sin(angle1)
            x2 = front_center[0] + (w/2) * math.cos(angle2)
            y2 = front_center[1] + (h/2) * math.sin(angle2)
            self.draw_line((x1, y1), (x2, y2), self.GREEN, 3)
        
        # Linhas conectoras
        self.draw_line((back_center[0], back_center[1] - h/2), 
                      (front_center[0], front_center[1] - h/2), self.GREEN, 3)
        self.draw_line((back_center[0], back_center[1] + h/2), 
                      (front_center[0], front_center[1] + h/2), self.GREEN, 3)
        
        return (world_x + w, world_y + h/2)
    
    def draw_not_gate(self, world_x, world_y):
        """Desenha porta NOT"""
        h = self.GATE_HEIGHT
        center_y = world_y + h/2
        
        # Triângulo
        points = [
            (world_x, world_y + 15),
            (world_x, world_y + h - 15),
            (world_x + 30, center_y)
        ]
        self.draw_polygon(points, self.ORANGE, 3)
        
        # Círculo
        self.draw_circle((world_x + 38, center_y), 8, self.ORANGE, 3)
        
        return (world_x + 46, center_y)
    
    def draw_routed_wire(self, start_world, end_world, routing_x_world):
        """Desenha fio roteado"""
        x1, y1 = start_world
        x2, y2 = end_world
        
        self.draw_line((x1, y1), (routing_x_world, y1), self.WIRE_COLOR, 2)
        self.draw_line((routing_x_world, y1), (routing_x_world, y2), self.WIRE_COLOR, 2)
        self.draw_line((routing_x_world, y2), (x2, y2), self.WIRE_COLOR, 2)
    
    def draw_connection_dot(self, pos_world, color=None, radius=5):
        """Desenha ponto de conexão"""
        if color is None:
            color = self.WIRE_COLOR
        self.draw_circle(pos_world, radius, color)

# Mantém as funções originais de parsing
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

def calcular_layout(node, y_start=0):
    """Calcula layout da AST"""
    if isinstance(node, VariableNode) or \
       (isinstance(node, OperatorNode) and node.op == '~' and isinstance(node.children[0], VariableNode)):
        
        bus_name = node.name if isinstance(node, VariableNode) else f"~{node.children[0].name}"

        return {
            'type': 'leaf',
            'bus_name': bus_name,
            'y_pos': y_start + 50,  # NODE_V_SPACING / 2 
            'height': 100           # NODE_V_SPACING
        }

    if isinstance(node, OperatorNode):
        child_layouts = []
        current_y_offset = 0
        for child_node in node.children:
            child_layout = calcular_layout(child_node, y_start + current_y_offset)
            child_layouts.append(child_layout)
            current_y_offset += child_layout['height']

        total_height = current_y_offset
        gate_y_pos = y_start + total_height / 2

        return {
            'type': 'gate',
            'op': node.op,
            'y_pos': gate_y_pos,
            'height': total_height,
            'children': child_layouts
        }
    return {}

def desenhar_circuito_recursivo(layout, x_pos, bus_x_coords, drawer):
    """Desenha circuito usando o drawer escalável"""
    if layout.get('type') == 'leaf':
        return ('bus', layout['bus_name'], layout['y_pos'])

    if layout.get('type') == 'gate':
        gate_center_y = layout['y_pos']
        gate_top_y = gate_center_y - drawer.GATE_HEIGHT / 2
        
        output_pos = None
        if layout['op'] == '*':
            output_pos = drawer.draw_and_gate(x_pos, gate_top_y)
        elif layout['op'] == '+':
            output_pos = drawer.draw_or_gate(x_pos, gate_top_y)
        elif layout['op'] == '~':
            output_pos = drawer.draw_not_gate(x_pos, gate_top_y)

        num_children = len(layout['children'])
        gate_inputs_y = [gate_center_y]
        if num_children > 1:
            gate_inputs_y = [gate_top_y + 20, gate_top_y + drawer.GATE_HEIGHT - 20]

        routing_x = x_pos - (drawer.NODE_H_SPACING / 2)

        for i, child_layout in enumerate(layout['children']):
            child_output = desenhar_circuito_recursivo(child_layout, x_pos - drawer.NODE_H_SPACING, bus_x_coords, drawer)
            
            input_pos = (x_pos, gate_inputs_y[i])

            if isinstance(child_output, tuple) and child_output[0] == 'bus':
                bus_name = child_output[1]
                bus_x = bus_x_coords[bus_name]
                wire_y = child_output[2]
                start_pos = (bus_x, wire_y)

                drawer.draw_routed_wire(start_pos, input_pos, routing_x)
                drawer.draw_connection_dot(start_pos)
            else:
                start_pos = child_output
                drawer.draw_routed_wire(start_pos, input_pos, routing_x)
        
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

def plotar_circuito_logico(expressao_booleana, drawer, screen_width, screen_height):
    """Função principal do desenho com navegação"""
    try:
        ast_root = criar_ast_de_expressao(expressao_booleana)
    except ValueError as e:
        print(f"Erro ao analisar a expressão: {e}")
        drawer.draw_text(f"Erro: {e}", (screen_width/2, screen_height/2), 40, (255, 80, 80))
        return

    # Desenha barramentos
    variaveis = sorted(list(_coletar_variaveis(ast_root)))
    bus_x_coords = {}

    bus_x_start = 30
    bus_pair_spacing = 80
    negated_line_offset = 50

    for i, var_name in enumerate(variaveis):
        true_bus_x = bus_x_start
        drawer.draw_line((true_bus_x, 40), (true_bus_x, screen_height - 40), drawer.WHITE, 2)
        drawer.draw_text(var_name, (true_bus_x, 25))
        bus_x_coords[var_name] = true_bus_x

        negated_bus_x = true_bus_x + negated_line_offset
        drawer.draw_line((negated_bus_x, 40), (negated_bus_x, screen_height - 40), drawer.WHITE, 2)
        drawer.draw_text(f"~{var_name}", (negated_bus_x, 25))
        bus_x_coords[f"~{var_name}"] = negated_bus_x

        bus_x_start = negated_bus_x + bus_pair_spacing

    layout_final = calcular_layout(ast_root, y_start=60)
    x_final_gate = screen_width - drawer.NODE_H_SPACING
    final_output_pos = desenhar_circuito_recursivo(layout_final, x_final_gate, bus_x_coords, drawer)

    # Desenha fio de saída final
    if final_output_pos:
        if isinstance(final_output_pos, tuple) and final_output_pos[0] == 'bus':
            bus_name = final_output_pos[1]
            bus_x = bus_x_coords[bus_name]
            y_final_gate = final_output_pos[2]
            start_pos = (bus_x, y_final_gate)
            drawer.draw_line(start_pos, (screen_width - 20, y_final_gate), drawer.WHITE, 3)
            drawer.draw_connection_dot(start_pos, color=drawer.WHITE)
        else:
            drawer.draw_line(final_output_pos, (final_output_pos[0] + 50, final_output_pos[1]), drawer.WHITE, 3)

def draw_ui(screen, camera, font):
    """Desenha interface de controle"""
    ui_texts = [
        "Controles:",
        "- Arrastar: Botão esquerdo do mouse",
        "- Zoom: Roda do mouse",
        "- WASD: Mover câmera",
        "- R: Resetar vista",
        f"Zoom: {camera.zoom:.2f}x",
        f"Posição: ({camera.x:.0f}, {camera.y:.0f})"
    ]
    
    y = 10
    for text in ui_texts:
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (10, y))
        y += 25

# --- EXECUÇÃO PRINCIPAL ---
# Carrega expressão
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

# Configurações
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gerador de Circuitos Lógicos - Navegável")

camera = Camera(screen_width, screen_height)
drawer = CircuitDrawer(screen, camera)
font = pygame.font.Font(None, 24)

# Converte expressão
expressao_booleana = converter_para_algebra_booleana(expressao)

clock = pygame.time.Clock()
running = True

while running:
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reset câmera
                camera.x = 0
                camera.y = 0
                camera.zoom = 1.0
            elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                # Salva imagem (Ctrl+S)
                caminho_imagem = os.path.join(ASSETS_PATH, "circuito_navegavel.png")
                pygame.image.save(screen, caminho_imagem)
                print(f"Imagem salva em: {caminho_imagem}")
        
        camera.handle_event(event)
    
    # Controles de teclado
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        camera.move(0, -camera.move_speed)
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        camera.move(0, camera.move_speed)
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        camera.move(-camera.move_speed, 0)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        camera.move(camera.move_speed, 0)
    
    # Desenho
    screen.fill(drawer.BACKGROUND)
    plotar_circuito_logico(expressao_booleana, drawer, screen_width, screen_height)
    draw_ui(screen, camera, font)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()