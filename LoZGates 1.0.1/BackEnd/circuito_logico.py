import pygame
import tkinter as tk
import os
import threading
import math
import copy
import json
import time
from .converter import converter_para_algebra_booleana

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

# --- Classes para componentes interativos ---
class Component:
    def __init__(self, x, y, comp_type, name=""):
        self.x = x
        self.y = y
        self.type = comp_type  # 'variable', 'and', 'or', 'not', 'output'
        self.name = name
        self.width = 80
        self.height = 60
        self.inputs = []  # Lista de pontos de entrada
        self.outputs = []  # Lista de pontos de saída
        self.input_connections = {}  # {input_index: wire}
        self.output_connections = []  # Lista de wires conectados à saída
        self.dragging = False
        self.selected = False
        
        self._setup_connection_points()
    
    def _setup_connection_points(self):
        if self.type == 'variable':
            # Variável tem apenas saída
            self.outputs = [(self.x + self.width, self.y + self.height//2)]
        elif self.type == 'not':
            # NOT tem 1 entrada e 1 saída
            self.inputs = [(self.x, self.y + self.height//2)]
            self.outputs = [(self.x + self.width, self.y + self.height//2)]
        elif self.type in ['and', 'or']:
            # AND/OR têm 2 entradas e 1 saída
            self.inputs = [
                (self.x, self.y + self.height//3),
                (self.x, self.y + 2*self.height//3)
            ]
            self.outputs = [(self.x + self.width, self.y + self.height//2)]
        elif self.type == 'output':
            # Saída tem apenas entrada
            self.inputs = [(self.x, self.y + self.height//2)]
    
    def update_connection_points(self):
        """Atualiza as posições dos pontos de conexão quando o componente é movido"""
        self._setup_connection_points()
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, point):
        x, y = point
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)

class Wire:
    def __init__(self, start_comp, start_output, end_comp, end_input):
        self.start_comp = start_comp
        self.start_output = start_output  # índice da saída
        self.end_comp = end_comp
        self.end_input = end_input  # índice da entrada
        self.selected = False
    
    def get_start_pos(self):
        return self.start_comp.outputs[self.start_output]
    
    def get_end_pos(self):
        return self.end_comp.inputs[self.end_input]

# --- Classe para gerenciar a câmera/viewport ---
class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 3.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.move_speed = 5
        self.zoom_speed = 0.1
        self.dragging = False
        self.last_mouse_pos = (0, 0)
    
    def world_to_screen(self, world_pos):
        world_x, world_y = world_pos
        screen_x = (world_x - self.x) * self.zoom + self.screen_width / 2
        screen_y = (world_y - self.y) * self.zoom + self.screen_height / 2
        return (int(screen_x), int(screen_y))
    
    def screen_to_world(self, screen_pos):
        screen_x, screen_y = screen_pos
        world_x = (screen_x - self.screen_width / 2) / self.zoom + self.x
        world_y = (screen_y - self.screen_height / 2) / self.zoom + self.y
        return (world_x, world_y)
    
    def move(self, dx, dy):
        self.x += dx / self.zoom
        self.y += dy / self.zoom
    
    def zoom_at(self, screen_pos, zoom_delta):
        world_pos = self.screen_to_world(screen_pos)
        old_zoom = self.zoom
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom + zoom_delta))
        zoom_ratio = self.zoom / old_zoom
        self.x = world_pos[0] - (world_pos[0] - self.x) * zoom_ratio
        self.y = world_pos[1] - (world_pos[1] - self.y) * zoom_ratio
    
    def reset_view(self):
        """Reseta a câmera para a posição inicial"""
        self.x = 0
        self.y = 0
        self.zoom = 1.0
    
    def handle_event(self, event, interactive_mode=False):
        """Retorna True se o evento foi consumido pela câmera"""
        if interactive_mode:
            # No modo interativo, só permite zoom
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.zoom_at(event.pos, self.zoom_speed)
                    return True
                elif event.button == 5:  # Scroll down
                    self.zoom_at(event.pos, -self.zoom_speed)
                    return True
        else:
            # Modo normal - permite drag e zoom
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    return True
                elif event.button == 4:
                    self.zoom_at(event.pos, self.zoom_speed)
                    return True
                elif event.button == 5:
                    self.zoom_at(event.pos, -self.zoom_speed)
                    return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
                return True
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.move(-dx, -dy)
                self.last_mouse_pos = event.pos
                return True
        
        return False

# --- Classe para desenhar elementos escaláveis ---
class CircuitDrawer:
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera
        self.BACKGROUND = (0, 0, 0)
        self.WHITE = (230, 230, 230)
        self.BLUE = (60, 120, 220)
        self.GREEN = (50, 200, 130)
        self.ORANGE = (250, 170, 70)
        self.RED = (220, 60, 60)
        self.YELLOW = (255, 255, 0)
        self.LABEL_COLOR = (255, 255, 255)
        self.WIRE_COLOR = (200, 200, 200)
        self.SELECTED_COLOR = (255, 255, 0)
        self.CONNECTION_POINT_COLOR = (100, 255, 100)
        self.GATE_WIDTH = 60
        self.GATE_HEIGHT = 80
        self.NODE_H_SPACING = 180
    
    def draw_line(self, start_world, end_world, color, width=2):
        start_screen = self.camera.world_to_screen(start_world)
        end_screen = self.camera.world_to_screen(end_world)
        scaled_width = max(1, int(width * self.camera.zoom))
        pygame.draw.line(self.screen, color, start_screen, end_screen, scaled_width)
    
    def draw_circle(self, center_world, radius, color, width=0):
        center_screen = self.camera.world_to_screen(center_world)
        scaled_radius = max(1, int(radius * self.camera.zoom))
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.circle(self.screen, color, center_screen, scaled_radius, scaled_width)
    
    def draw_polygon(self, points_world, color, width=0):
        points_screen = [self.camera.world_to_screen(p) for p in points_world]
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.polygon(self.screen, color, points_screen, scaled_width)
    
    def draw_rect(self, rect_world, color, width=0):
        x, y, w, h = rect_world
        corners = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
        corners_screen = [self.camera.world_to_screen(corner) for corner in corners]
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.polygon(self.screen, color, corners_screen, scaled_width)
    
    def draw_text(self, text, pos_world, font_size=36, color=None):
        if color is None: 
            color = self.LABEL_COLOR
        scaled_font_size = max(8, int(font_size * self.camera.zoom))
        try:
            font = pygame.font.Font(None, scaled_font_size)
            text_surface = font.render(text, True, color)
            pos_screen = self.camera.world_to_screen(pos_world)
            text_rect = text_surface.get_rect(center=pos_screen)
            self.screen.blit(text_surface, text_rect)
        except pygame.error: 
            pass

    def draw_gate_shape(self, name, world_x, world_y):
        """Desenho original das portas lógicas"""
        w, h = self.GATE_WIDTH - 20, self.GATE_HEIGHT
        if name == 'AND':
            self.draw_line((world_x, world_y), (world_x, world_y + h), self.BLUE, 3)
            self.draw_line((world_x, world_y), (world_x + w/2, world_y), self.BLUE, 3)
            self.draw_line((world_x, world_y + h), (world_x + w/2, world_y + h), self.BLUE, 3)
            center = (world_x + w/2, world_y + h/2)
            for i in range(16):
                a1 = -math.pi/2 + (i * math.pi/16)
                a2 = -math.pi/2 + ((i+1) * math.pi/16)
                p1 = (center[0] + (w/2) * math.cos(a1), center[1] + (h/2) * math.sin(a1))
                p2 = (center[0] + (w/2) * math.cos(a2), center[1] + (h/2) * math.sin(a2))
                self.draw_line(p1, p2, self.BLUE, 3)
            return (world_x + w, world_y + h/2)
        elif name == 'OR':
            back_center = (world_x - 7.5, world_y + h/2)
            front_center = (world_x + w/2, world_y + h/2)
            for i in range(16):
                a1 = -math.pi/2 + (i * math.pi/16)
                a2 = -math.pi/2 + ((i+1) * math.pi/16)
                p1_b = (back_center[0] + 10 * math.cos(a1), back_center[1] + (h/2) * math.sin(a1))
                p2_b = (back_center[0] + 10 * math.cos(a2), back_center[1] + (h/2) * math.sin(a2))
                self.draw_line(p1_b, p2_b, self.GREEN, 3)
                p1_f = (front_center[0] + (w/2) * math.cos(a1), front_center[1] + (h/2) * math.sin(a1))
                p2_f = (front_center[0] + (w/2) * math.cos(a2), front_center[1] + (h/2) * math.sin(a2))
                self.draw_line(p1_f, p2_f, self.GREEN, 3)
            self.draw_line((back_center[0], back_center[1] - h/2), (front_center[0], front_center[1] - h/2), self.GREEN, 3)
            self.draw_line((back_center[0], back_center[1] + h/2), (front_center[0], front_center[1] + h/2), self.GREEN, 3)
            return (world_x + w, world_y + h/2)
        elif name == 'NOT':
            center_y = world_y + h/2
            points = [(world_x, world_y + 15), (world_x, world_y + h - 15), (world_x + 30, center_y)]
            self.draw_polygon(points, self.ORANGE, 3)
            self.draw_circle((world_x + 38, center_y), 8, self.ORANGE, 3)
            return (world_x + 46, center_y)
    
    def draw_smart_wire(self, start_world, end_world):
        x1, y1 = start_world; x2, y2 = end_world
        mid_x = x1 + (x2 - x1) * 0.5
        self.draw_line((x1, y1), (mid_x, y1), self.WIRE_COLOR, 2)
        self.draw_line((mid_x, y1), (mid_x, y2), self.WIRE_COLOR, 2)
        self.draw_line((mid_x, y2), (x2, y2), self.WIRE_COLOR, 2)
    
    def draw_connection_dot(self, pos_world, color=None, radius=5):
        if color is None: 
            color = self.WIRE_COLOR
        self.draw_circle(pos_world, radius, color)
    
    def draw_component(self, component):
        """Desenha componente interativo usando o estilo original das portas"""
        color = self.SELECTED_COLOR if component.selected else self.WHITE
        
        if component.type == 'variable':
            # Desenha retângulo para variável
            self.draw_rect((component.x, component.y, component.width, component.height), color, 2)
            self.draw_text(component.name, (component.x + component.width//2, component.y + component.height//2), 20)
        
        elif component.type == 'and':
            # Usa o desenho original da porta AND
            gate_y = component.y + (component.height - self.GATE_HEIGHT)//2
            gate_output_pos = self.draw_gate_shape('AND', component.x, gate_y)
            
            # Ajusta TANTO as entradas quanto as saídas baseado no desenho real
            component.outputs = [gate_output_pos]
            # Recalcula as posições de entrada baseado no desenho da porta
            gate_center_y = gate_y + self.GATE_HEIGHT//2
            component.inputs = [
                (component.x, gate_center_y - 20),  # Entrada superior
                (component.x, gate_center_y + 20)   # Entrada inferior
            ]
        
        elif component.type == 'or':
            # Usa o desenho original da porta OR
            gate_y = component.y + (component.height - self.GATE_HEIGHT)//2
            gate_output_pos = self.draw_gate_shape('OR', component.x, gate_y)
            
            # Ajusta TANTO as entradas quanto as saídas baseado no desenho real
            component.outputs = [gate_output_pos]
            # Recalcula as posições de entrada baseado no desenho da porta
            gate_center_y = gate_y + self.GATE_HEIGHT//2
            component.inputs = [
                (component.x, gate_center_y - 20),  # Entrada superior
                (component.x, gate_center_y + 20)   # Entrada inferior
            ]
        
        elif component.type == 'not':
            # Usa o desenho original da porta NOT
            gate_y = component.y + (component.height - self.GATE_HEIGHT)//2
            gate_output_pos = self.draw_gate_shape('NOT', component.x, gate_y)
            
            # Ajusta TANTO as entradas quanto as saídas baseado no desenho real
            component.outputs = [gate_output_pos]
            # Recalcula a posição de entrada baseado no desenho da porta
            gate_center_y = gate_y + self.GATE_HEIGHT//2
            component.inputs = [(component.x, gate_center_y)]
        
        elif component.type == 'output':
            # Desenha saída
            self.draw_rect((component.x, component.y, component.width, component.height), self.RED, 2)
            self.draw_text("SAÍDA", (component.x + component.width//2, component.y + component.height//2), 16)
        
        # Desenha pontos de conexão
        for i, input_pos in enumerate(component.inputs):
            color = self.CONNECTION_POINT_COLOR
            if i in component.input_connections:
                color = self.YELLOW  # Conectado
            self.draw_circle(input_pos, 4, color)
        
        # Desenha pontos de saída - agora usando as posições atualizadas
        for output_pos in component.outputs:
            color = self.CONNECTION_POINT_COLOR
            if component.output_connections:
                color = self.YELLOW  # Conectado
            self.draw_circle(output_pos, 4, color)
            
    def draw_wire(self, wire):
            """Desenha um fio conectando dois componentes"""
            start_pos = wire.get_start_pos()
            end_pos = wire.get_end_pos()
            
            color = self.SELECTED_COLOR if wire.selected else self.WIRE_COLOR
            
            # Desenha fio com curvas suaves
            mid_x = start_pos[0] + (end_pos[0] - start_pos[0]) * 0.7
            self.draw_line(start_pos, (mid_x, start_pos[1]), color, 3)
            self.draw_line((mid_x, start_pos[1]), (mid_x, end_pos[1]), color, 3)
            self.draw_line((mid_x, end_pos[1]), end_pos, color, 3)

# -- - Classe para gerenciar histórico de ações (undo/redo) ---
class CircuitHistory:
    def __init__(self, max_history=50):
        self.history = []  # Lista de estados
        self.current_index = -1  # Índice do estado atual
        self.max_history = max_history
    
    def save_state(self, components, wires):
        """Salva o estado atual do circuito"""
        # Remove estados futuros se estivermos no meio do histórico
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Cria uma cópia profunda do estado
        state = {
            'components': self._serialize_components(components),
            'wires': self._serialize_wires(wires)
        }
        
        self.history.append(state)
        self.current_index += 1
        
        # Limita o tamanho do histórico
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def can_undo(self):
        """Verifica se é possível fazer undo"""
        return self.current_index > 0
    
    def can_redo(self):
        """Verifica se é possível fazer redo"""
        return self.current_index < len(self.history) - 1
    
    def undo(self):
        """Retorna ao estado anterior"""
        if self.can_undo():
            self.current_index -= 1
            return self._deserialize_state(self.history[self.current_index])
        return None
    
    def redo(self):
        """Avança para o próximo estado"""
        if self.can_redo():
            self.current_index += 1
            return self._deserialize_state(self.history[self.current_index])
        return None
    
    def _serialize_components(self, components):
        """Serializa componentes para salvar no histórico"""
        serialized = []
        for comp in components:
            comp_data = {
                'x': comp.x,
                'y': comp.y,
                'type': comp.type,
                'name': comp.name,
                'width': comp.width,
                'height': comp.height,
                'selected': comp.selected
            }
            serialized.append(comp_data)
        return serialized
    
    def _serialize_wires(self, wires):
        """Serializa fios para salvar no histórico"""
        serialized = []
        for wire in wires:
            # Encontra os índices dos componentes
            start_comp_index = -1
            end_comp_index = -1
            
            for i, comp in enumerate(self.components_ref):
                if comp == wire.start_comp:
                    start_comp_index = i
                elif comp == wire.end_comp:
                    end_comp_index = i
            
            if start_comp_index >= 0 and end_comp_index >= 0:
                wire_data = {
                    'start_comp_index': start_comp_index,
                    'start_output': wire.start_output,
                    'end_comp_index': end_comp_index,
                    'end_input': wire.end_input,
                    'selected': wire.selected
                }
                serialized.append(wire_data)
        return serialized
    
    def _deserialize_state(self, state):
        """Deserializa estado do histórico"""
        return {
            'components': state['components'],
            'wires': state['wires']
        }
    
    def set_components_reference(self, components):
        """Define referência aos componentes para serialização de wires"""
        self.components_ref = components

# --- Lógica de Parsing e Layout (para circuito automático) ---
def criar_ast_de_expressao(expressao):
    tokens = list(expressao.replace(" ", "")); pos = 0
    def peek(): return tokens[pos] if pos < len(tokens) else None
    def consume(): nonlocal pos; pos += 1; return tokens[pos - 1]
    def parse_factor():
        token = peek()
        if token and token.isalpha(): return VariableNode(consume())
        if token == '~':
            consume()
            if peek() == '(': consume(); expr = parse_expression(); consume(); return OperatorNode('~', [expr])
            return OperatorNode('~', [parse_factor()])
        if token == '(': consume(); expr = parse_expression(); consume(); return expr
        raise ValueError(f"Token inválido: {token}")
    def parse_term():
        node = parse_factor()
        while peek() == '*': op = consume(); right = parse_factor(); node = OperatorNode(op, [node, right])
        return node
    def parse_expression():
        node = parse_term()
        while peek() == '+': op = consume(); right = parse_term(); node = OperatorNode(op, [node, right])
        return node
    return parse_expression()

def calcular_layout_dinamico(node, y_base=0):
    if isinstance(node, VariableNode):
        return {'type': 'variable', 'name': node.name, 'y_pos': y_base, 'height': 80, 'width': 0}
    if isinstance(node, OperatorNode) and node.op == '~' and isinstance(node.children[0], VariableNode):
        return {'type': 'negated_variable', 'name': node.children[0].name, 'y_pos': y_base, 'height': 80, 'width': 0}
    if isinstance(node, OperatorNode):
        child_layouts, current_y, max_width = [], y_base, 0
        for child in node.children:
            child_layout = calcular_layout_dinamico(child, current_y)
            child_layouts.append(child_layout)
            current_y += child_layout['height'] + 20
            max_width = max(max_width, child_layout.get('width', 0))
        total_height = current_y - y_base - 20
        return {'type': 'gate', 'op': node.op, 'y_pos': y_base + total_height / 2, 'height': total_height, 'width': max_width + 180, 'children': child_layouts}
    return {}

def desenhar_circuito_dinamico(layout, x_pos, bus_positions, drawer):
    type = layout.get('type')
    if type in ['variable', 'negated_variable']:
        bus_name = layout['name'] if type == 'variable' else f"~{layout['name']}"
        return {'type': 'bus_connection', 'bus_x': bus_positions.get(bus_name, 50), 'y_pos': layout['y_pos'] + 40}
    if type == 'gate':
        gate_center_y = layout['y_pos']; gate_top_y = gate_center_y - drawer.GATE_HEIGHT / 2
        op_map = {'*': 'AND', '+': 'OR', '~': 'NOT'}
        output_pos = drawer.draw_gate_shape(op_map[layout['op']], x_pos, gate_top_y)
        num_inputs = len(layout['children'])
        spacing = (drawer.GATE_HEIGHT - 30) / (num_inputs - 1) if num_inputs > 1 else 0
        input_positions = [(x_pos, gate_center_y)] if num_inputs == 1 else [(x_pos, (gate_top_y + 15) + spacing * i) for i in range(num_inputs)]
        for i, child_layout in enumerate(layout['children']):
            child_output = desenhar_circuito_dinamico(child_layout, x_pos - drawer.NODE_H_SPACING, bus_positions, drawer)
            if child_output['type'] == 'bus_connection':
                bus_pos = (child_output['bus_x'], child_output['y_pos'])
                drawer.draw_smart_wire(bus_pos, input_positions[i])
                drawer.draw_connection_dot(bus_pos)
            else:
                drawer.draw_smart_wire((child_output['x'], child_output['y']), input_positions[i])
        return {'type': 'gate_output', 'x': output_pos[0], 'y': output_pos[1]}
    return {}

def _coletar_variaveis(node):
    if isinstance(node, VariableNode): return {node.name}
    if isinstance(node, OperatorNode):
        return set().union(*[_coletar_variaveis(child) for child in node.children])
    return set()

def _coletar_operadores(node, operators=None):
    """Coleta todos os operadores da AST"""
    if operators is None:
        operators = {'*': 0, '+': 0, '~': 0}
    
    if isinstance(node, OperatorNode):
        operators[node.op] += 1
        for child in node.children:
            _coletar_operadores(child, operators)
    
    return operators

# --- Função Principal de Desenho do Circuito Automático ---
def desenhar_circuito_logico_base(expressao_booleana, drawer, screen_width, screen_height):
    try:
        ast_root = criar_ast_de_expressao(expressao_booleana)
    except ValueError as e:
        drawer.draw_text(f"Erro: {e}", (screen_width/2, screen_height/2), 40, (255, 80, 80))
        return
    
    variaveis = sorted(list(_coletar_variaveis(ast_root)))
    bus_positions = {}
    bus_x_start = 100; bus_spacing = 100; last_bus_x = bus_x_start
    
    # Desenha os barramentos de variáveis
    for i, var_name in enumerate(variaveis):
        true_bus_x = bus_x_start + i * bus_spacing
        drawer.draw_line((true_bus_x, 40), (true_bus_x, screen_height * 3), drawer.WHITE, 2)
        drawer.draw_text(var_name, (true_bus_x, 25))
        bus_positions[var_name] = true_bus_x
        negated_bus_x = true_bus_x + 40
        drawer.draw_line((negated_bus_x, 40), (negated_bus_x, screen_height * 3), drawer.WHITE, 2)
        drawer.draw_text(f"~{var_name}", (negated_bus_x, 25))
        bus_positions[f"~{var_name}"] = negated_bus_x
        last_bus_x = negated_bus_x
        
    layout = calcular_layout_dinamico(ast_root, y_base=100)
    primeiro_gate_x = last_bus_x + 150
    final_output = desenhar_circuito_dinamico(layout, primeiro_gate_x + layout.get('width', 0), bus_positions, drawer)
    
    # Desenha a saída final
    if final_output and final_output.get('type') == 'gate_output':
        pos = (final_output['x'], final_output['y'])
        drawer.draw_line(pos, (pos[0] + 80, pos[1]), drawer.WHITE, 4)
        drawer.draw_text("SAÍDA", (pos[0] + 120, pos[1]), 30, drawer.WHITE)

def draw_ui_info(screen, camera, font):
    """Desenha informações de controle na tela"""
    ui_texts = [
        "Controles:",
        "- Arrastar: Mouse esquerdo",
        "- Zoom: Roda do mouse", 
        "- WASD: Mover câmera",
        "- R: Resetar vista",
        f"Zoom: {camera.zoom:.2f}x"
    ]
    
    y = 10
    for text in ui_texts:
        try:
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (10, y))
            y += 25
        except: pass

# --- Classe principal do circuito interativo ---

class CircuitHistory:
    def __init__(self, max_history=50):
        self.history = []  # Lista de estados
        self.current_index = -1  # Índice do estado atual
        self.max_history = max_history
        self.components_ref = None
    
    def save_state(self, components, wires):
        """Salva o estado atual do circuito"""
        # Remove estados futuros se estivermos no meio do histórico
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Cria uma cópia profunda do estado
        state = {
            'components': self._serialize_components(components),
            'wires': self._serialize_wires(wires, components)
        }
        
        self.history.append(state)
        self.current_index += 1
        
        # Limita o tamanho do histórico
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def can_undo(self):
        """Verifica se é possível fazer undo"""
        return self.current_index > 0
    
    def can_redo(self):
        """Verifica se é possível fazer redo"""
        return self.current_index < len(self.history) - 1
    
    def undo(self):
        """Retorna ao estado anterior"""
        if self.can_undo():
            self.current_index -= 1
            return self._deserialize_state(self.history[self.current_index])
        return None
    
    def redo(self):
        """Avança para o próximo estado"""
        if self.can_redo():
            self.current_index += 1
            return self._deserialize_state(self.history[self.current_index])
        return None
    
    def _serialize_components(self, components):
        """Serializa componentes para salvar no histórico"""
        serialized = []
        for comp in components:
            comp_data = {
                'x': comp.x,
                'y': comp.y,
                'type': comp.type,
                'name': comp.name,
                'width': comp.width,
                'height': comp.height,
                'selected': comp.selected
            }
            serialized.append(comp_data)
        return serialized
    
    def _serialize_wires(self, wires, components):
        """Serializa fios para salvar no histórico"""
        serialized = []
        for wire in wires:
            # Encontra os índices dos componentes
            start_comp_index = -1
            end_comp_index = -1
            
            for i, comp in enumerate(components):
                if comp == wire.start_comp:
                    start_comp_index = i
                elif comp == wire.end_comp:
                    end_comp_index = i
            
            if start_comp_index >= 0 and end_comp_index >= 0:
                wire_data = {
                    'start_comp_index': start_comp_index,
                    'start_output': wire.start_output,
                    'end_comp_index': end_comp_index,
                    'end_input': wire.end_input,
                    'selected': wire.selected
                }
                serialized.append(wire_data)
        return serialized
    
    def _deserialize_state(self, state):
        """Deserializa estado do histórico"""
        return {
            'components': state['components'],
            'wires': state['wires']
        }
    
    def set_components_reference(self, components):
        """Define referência aos componentes para serialização de wires"""
        self.components_ref = components

class CircuitoInterativoManual:
    def __init__(self, parent_frame, expressao):
        self.parent_frame = parent_frame
        self.expressao = expressao
        self.running = False
        self.interactive_mode = True

        # Componentes do circuito
        self.components = []
        self.wires = []
        self.selected_component = None
        self.connecting = False
        self.connection_start = None
        self.dragging_component = None

        # Sistema de histórico para undo/redo
        self.history = CircuitHistory()
        self.last_action_time = 0  # Para evitar salvar estados muito frequentemente

        # Variáveis para mensagem de sucesso
        self.show_success_message = False
        self.success_message_timer = 0

        # Estado da interface
        self._move = {'up': False, 'down': False, 'left': False, 'right': False}

        # Inicialização
        self.parent_frame.after(100, self.init_pygame)
    
    def init_pygame(self):
        try:
            os.environ['SDL_WINDOWID'] = str(self.parent_frame.winfo_id())
            os.environ['SDL_VIDEODRIVER'] = 'windows'

            pygame.init()
            pygame.font.init()
            self.parent_frame.update()

            self.screen_width = max(800, self.parent_frame.winfo_width())
            self.screen_height = max(600, self.parent_frame.winfo_height())

            flags = pygame.DOUBLEBUF
            try:
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags, vsync=1)
            except TypeError:
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags)

            self.camera = Camera(self.screen_width, self.screen_height)
            self.drawer = CircuitDrawer(self.screen, self.camera)

            try:    
                self.font = pygame.font.Font(None, 24)
            except: 
                self.font = None

            # Configuração do frame Tkinter
            self.parent_frame.configure(bg="#000000", highlightthickness=0)
            self.parent_frame.focus_set()
            self.parent_frame.bind("<Enter>", lambda e: self.parent_frame.focus_set())
            self.parent_frame.bind("<KeyPress>", self._on_key_press)
            self.parent_frame.bind("<KeyRelease>", self._on_key_release)

            # Inicializa componentes baseado na expressão
            self.init_components_from_expression()
            
            # Configura referência para serialização e salva estado inicial
            self.history.set_components_reference(self.components)
            self.save_state("Initial state")

            self.running = True
            self._tick()

        except Exception as e:
            tk.Label(self.parent_frame, text=f"Erro Pygame: {e}", fg="red", bg="black").pack()
    
    def init_components_from_expression(self):
        """Inicializa componentes baseado na expressão fornecida"""
        try:
            # Analisa a expressão para determinar componentes necessários
            ast_root = criar_ast_de_expressao(self.expressao)
            variables = sorted(list(_coletar_variaveis(ast_root)))
            operators = _coletar_operadores(ast_root)
        except:
            # Fallback se houver erro no parsing
            variables = self.extract_variables(self.expressao)
            operators = {'*': 2, '+': 2, '~': 1}
        
        # Cria barramentos de variáveis na esquerda
        y_start = -100
        for i, var in enumerate(variables):
            comp = Component(-300, y_start + i * 100, 'variable', var)
            self.components.append(comp)
            
        # Adiciona portas lógicas baseado na análise da expressão
        gate_y = -100
        
        # Adiciona portas AND baseado na necessidade
        for i in range(operators.get('*', 0)):
            comp = Component(-50, gate_y + i * 100, 'and')
            self.components.append(comp)
        
        # Adiciona portas OR baseado na necessidade
        for i in range(operators.get('+', 0)):
            comp = Component(50, gate_y + i * 100, 'or')
            self.components.append(comp)
        
        # Adiciona portas NOT baseado na necessidade
        for i in range(operators.get('~', 0)):
            comp = Component(150, gate_y + i * 80, 'not')
            self.components.append(comp)
        
        # Adiciona saída
        output_comp = Component(300, 0, 'output', 'SAÍDA')
        self.components.append(output_comp)
    
    def extract_variables(self, expressao):
        """Extrai variáveis únicas da expressão"""
        variables = set()
        for char in expressao:
            if char.isalpha() and char.upper() not in ['AND', 'OR', 'NOT']:
                variables.add(char.upper())
        return sorted(list(variables))
    
    def save_state(self, action_description=""):
        """Salva o estado atual no histórico"""
        current_time = time.time()
        
        # Evita salvar estados muito frequentemente (limita a 1 por 0.5 segundos)
        if current_time - self.last_action_time > 0.5:
            self.history.save_state(self.components, self.wires)
            self.last_action_time = current_time
            if action_description:
                print(f"Estado salvo: {action_description}")
    
    def restore_state(self, state_data):
        """Restaura um estado do histórico"""
        if not state_data:
            return
        
        # Limpa conexões atuais
        for comp in self.components:
            comp.input_connections.clear()
            comp.output_connections.clear()
        
        # Restaura componentes
        for i, comp_data in enumerate(state_data['components']):
            if i < len(self.components):
                comp = self.components[i]
                comp.x = comp_data['x']
                comp.y = comp_data['y']
                comp.selected = comp_data['selected']
                comp.update_connection_points()
        
        # Limpa fios existentes
        self.wires.clear()
        
        # Restaura fios
        for wire_data in state_data['wires']:
            start_comp = self.components[wire_data['start_comp_index']]
            end_comp = self.components[wire_data['end_comp_index']]
            
            wire = Wire(
                start_comp,
                wire_data['start_output'],
                end_comp,
                wire_data['end_input']
            )
            wire.selected = wire_data['selected']
            
            self.wires.append(wire)
            
            # Reconecta as referências
            start_comp.output_connections.append(wire)
            end_comp.input_connections[wire_data['end_input']] = wire
    
    def undo(self):
        """Executa undo"""
        if self.history.can_undo():
            state = self.history.undo()
            self.restore_state(state)
            print("Undo executado")
            return True
        return False
    
    def redo(self):
        """Executa redo"""
        if self.history.can_redo():
            state = self.history.redo()
            self.restore_state(state)
            print("Redo executado")
            return True
        return False
    
    def _on_key_press(self, e):
        k = (e.keysym or "").lower()
        ctrl_pressed = (e.state & 0x4) != 0  # Verifica se Ctrl está pressionado
        
        # Controles de undo/redo
        if ctrl_pressed:
            if k == 'z':
                if not self.undo():
                    print("Nada para desfazer")
                return
            elif k == 'y':
                if not self.redo():
                    print("Nada para refazer")
                return
        
        # Controles existentes
        if k in ('w', 'up'):    self._move['up'] = True
        if k in ('s', 'down'):  self._move['down'] = True
        if k in ('a', 'left'):  self._move['left'] = True
        if k in ('d', 'right'): self._move['right'] = True
        if k == 'r':            self.camera.reset_view()
        if k == 'delete':       
            self.delete_selected()
            self.save_state("Delete component")
        if k == 'escape':       self.cancel_connection()
    
    def _on_key_release(self, e):
        k = (e.keysym or "").lower()
        if k in ('w', 'up'):    self._move['up'] = False
        if k in ('s', 'down'):  self._move['down'] = False
        if k in ('a', 'left'):  self._move['left'] = False
        if k in ('d', 'right'): self._move['right'] = False
    
    def delete_selected(self):
        """Deleta componente ou fio selecionado"""
        deleted_something = False
        
        if self.selected_component:
            # Remove conexões do componente
            for wire in self.wires[:]:
                if wire.start_comp == self.selected_component or wire.end_comp == self.selected_component:
                    # Remove referências nas conexões dos componentes
                    if wire in wire.start_comp.output_connections:
                        wire.start_comp.output_connections.remove(wire)
                    if wire.end_input in wire.end_comp.input_connections:
                        del wire.end_comp.input_connections[wire.end_input]
                    
                    self.wires.remove(wire)
                    deleted_something = True
            
            # Remove componente (exceto variáveis e saída)
            if self.selected_component.type not in ['variable', 'output']:
                self.components.remove(self.selected_component)
                deleted_something = True
            
            self.selected_component = None
        
        # Remove fios selecionados
        for wire in self.wires[:]:
            if wire.selected:
                # Remove referências nas conexões dos componentes
                if wire in wire.start_comp.output_connections:
                    wire.start_comp.output_connections.remove(wire)
                if wire.end_input in wire.end_comp.input_connections:
                    del wire.end_comp.input_connections[wire.end_input]
                
                self.wires.remove(wire)
                deleted_something = True
        
        return deleted_something
    
    def cancel_connection(self):
        """Cancela conexão em andamento"""
        self.connecting = False
        self.connection_start = None
    
    def handle_mouse_click(self, pos):
        """Gerencia cliques do mouse"""
        world_pos = self.camera.screen_to_world(pos)
        
        # Verifica clique em componentes
        clicked_component = None
        for component in self.components:
            if component.contains_point(world_pos):
                clicked_component = component
                break
        
        if clicked_component:
            # Deseleciona outros
            for comp in self.components:
                comp.selected = False
            for wire in self.wires:
                wire.selected = False
            
            clicked_component.selected = True
            self.selected_component = clicked_component
            
            if self.connecting:
                # Tentativa de conexão
                self.try_connect(clicked_component, world_pos)
            else:
                # Verificar se clicou em ponto de conexão - tolerância aumentada
                for i, output_pos in enumerate(clicked_component.outputs):
                    dist = math.sqrt((world_pos[0] - output_pos[0])**2 + (world_pos[1] - output_pos[1])**2)
                    if dist < 35:  # Tolerância aumentada
                        self.start_connection(clicked_component, 'output', i)
                        return
        else:
            # Clicou no vazio - deseleciona tudo
            for comp in self.components:
                comp.selected = False
            for wire in self.wires:
                wire.selected = False
            self.selected_component = None
            self.cancel_connection()
    
    def start_connection(self, component, conn_type, index):
        """Inicia uma conexão a partir de um ponto"""
        if conn_type == 'output':
            self.connecting = True
            self.connection_start = {
                'component': component,
                'type': conn_type,
                'index': index
            }
    
    def try_connect(self, target_component, world_pos):
        """Tenta conectar ao componente alvo"""
        if not self.connection_start:
            return
        
        # Verifica se clicou em uma entrada - tolerância aumentada
        for i, input_pos in enumerate(target_component.inputs):
            dist = math.sqrt((world_pos[0] - input_pos[0])**2 + (world_pos[1] - input_pos[1])**2)
            if dist < 35:  # Tolerância aumentada
                # Verifica se a entrada já está conectada
                if i not in target_component.input_connections:
                    # Cria o fio
                    wire = Wire(
                        self.connection_start['component'],
                        self.connection_start['index'],
                        target_component,
                        i
                    )
                    self.wires.append(wire)
                    
                    # Registra as conexões
                    self.connection_start['component'].output_connections.append(wire)
                    target_component.input_connections[i] = wire
                    
                    # Salva estado após conexão
                    self.save_state("Connect components")
                    
                    # Verifica se o circuito está correto
                    self.check_circuit_completion()
                
                self.cancel_connection()
                return
    
    def handle_mouse_drag(self, pos):
        """Gerencia arraste do mouse"""
        if self.selected_component and not self.connecting:
            world_pos = self.camera.screen_to_world(pos)
            
            # Move o componente (exceto variáveis)
            if self.selected_component.type not in ['variable']:
                old_x, old_y = self.selected_component.x, self.selected_component.y
                self.selected_component.x = world_pos[0] - self.selected_component.width // 2
                self.selected_component.y = world_pos[1] - self.selected_component.height // 2
                self.selected_component.update_connection_points()
                
                # Salva estado apenas se houve movimento significativo
                if abs(old_x - self.selected_component.x) > 10 or abs(old_y - self.selected_component.y) > 10:
                    self.save_state("Move component")
    
    def _tick(self):
        if not self.running:
            try: 
                pygame.quit()
            except: 
                pass
            return

        # Processa eventos do Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            
            # Primeiro verifica se a câmera consome o evento
            if not self.camera.handle_event(event, self.interactive_mode):
                # Se não foi consumido pela câmera, processa outros eventos
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_mouse_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:  # Botão esquerdo pressionado
                        self.handle_mouse_drag(event.pos)

        # Movimento contínuo via teclado
        if self._move['up']:    self.camera.move(0, -self.camera.move_speed)
        if self._move['down']:  self.camera.move(0,  self.camera.move_speed)
        if self._move['left']:  self.camera.move(-self.camera.move_speed, 0)
        if self._move['right']: self.camera.move( self.camera.move_speed, 0)

        # Desenha frame
        self.screen.fill(self.drawer.BACKGROUND)
        
        # Desenha grade de fundo
        self.draw_grid()
        
        # Desenha fios
        for wire in self.wires:
            self.drawer.draw_wire(wire)
        
        # Desenha componentes
        for component in self.components:
            self.drawer.draw_component(component)
        
        # Desenha linha de conexão temporária
        if self.connecting and self.connection_start:
            mouse_pos = pygame.mouse.get_pos()
            start_pos = self.connection_start['component'].outputs[self.connection_start['index']]
            start_screen = self.camera.world_to_screen(start_pos)
            pygame.draw.line(self.screen, self.drawer.YELLOW, start_screen, mouse_pos, 2)
        
        # Desenha informações
        if self.font:
            self.draw_ui_info()
        
        # Desenha mensagem de sucesso se ativa
        if self.show_success_message and self.success_message_timer > 0:
            self.draw_success_message()
            self.success_message_timer -= 1
            if self.success_message_timer <= 0:
                self.show_success_message = False

        pygame.display.flip()
        self.parent_frame.after(16, self._tick)
    
    def draw_grid(self):
        """Desenha uma grade de fundo para facilitar o posicionamento"""
        grid_size = 50
        color = (30, 30, 30)
        
        # Calcula limites visíveis
        top_left = self.camera.screen_to_world((0, 0))
        bottom_right = self.camera.screen_to_world((self.screen_width, self.screen_height))
        
        # Desenha linhas verticais
        start_x = int(top_left[0] / grid_size) * grid_size
        end_x = int(bottom_right[0] / grid_size) * grid_size + grid_size
        
        for x in range(start_x, end_x, grid_size):
            self.drawer.draw_line((x, top_left[1] - 100), (x, bottom_right[1] + 100), color, 1)
        
        # Desenha linhas horizontais
        start_y = int(top_left[1] / grid_size) * grid_size
        end_y = int(bottom_right[1] / grid_size) * grid_size + grid_size
        
        for y in range(start_y, end_y, grid_size):
            self.drawer.draw_line((top_left[0] - 100, y), (bottom_right[0] + 100, y), color, 1)
    
    def draw_ui_info(self):
        """Desenha informações de controle na tela"""
        ui_texts = [
            "=== MODO CONSTRUÇÃO INTERATIVA ===",
            "• Clique nos pontos verdes para conectar",
            "• Arraste componentes para mover",
            "• Delete: Remove selecionado",
            "• Ctrl+Z: Desfazer",
            "• Ctrl+Y: Refazer", 
            "• Esc: Cancela conexão",
            "• WASD: Mover câmera",
            "• Scroll: Zoom",
            "• R: Reset vista",
            f"Zoom: {self.camera.zoom:.2f}x",
            f"Expressão: {self.expressao[:40]}{'...' if len(self.expressao) > 40 else ''}",
            "Status: " + ("Conectando..." if self.connecting else "Selecione componentes")
        ]
        
        '''f"Histórico: {len(self.history.history)} estados",
            f"Undo disponível: {'Sim' if self.history.can_undo() else 'Não'}",
            f"Redo disponível: {'Sim' if self.history.can_redo() else 'Não'}",
            "",'''
        
        y = 10
        for text in ui_texts:
            try:
                if text.startswith("==="):
                    color = (255, 255, 0)
                elif "Ctrl+" in text:
                    color = (0, 255, 255)  # Ciano para controles de undo/redo
                elif text.startswith("Histórico") or text.startswith("Undo") or text.startswith("Redo"):
                    color = (200, 200, 255)  # Azul claro para info do histórico
                else:
                    color = (255, 255, 255)
                
                surface = self.font.render(text, True, color)
                self.screen.blit(surface, (10, y))
                y = y + 20 if not text.startswith("===") else y + 25
            except: 
                pass
    
    def stop(self):
        self.running = False
        
    def check_circuit_completion(self):
        """Verifica se o circuito montado está correto conforme a expressão"""
        try:
            # Avalia se o circuito atual representa a expressão correta
            if self.is_circuit_correct():
                self.show_success_message = True
                self.success_message_timer = 300  # Mostra por 5 segundos (300 frames a 60fps)
        except Exception as e:
            print(f"Erro ao verificar circuito: {e}")

    def is_circuit_correct(self):
        """
        Verifica se o circuito conectado representa corretamente a expressão booleana
        Esta é uma verificação simplificada - em um sistema completo seria mais complexa
        """
        # Encontra a saída
        output_component = None
        for comp in self.components:
            if comp.type == 'output':
                output_component = comp
                break
        
        if not output_component or len(output_component.input_connections) != 1:
            return False
        
        # Analisa a expressão para ver que operadores são necessários
        ast_root = criar_ast_de_expressao(self.expressao)
        needed_operators = _coletar_operadores(ast_root)
        needed_variables = _coletar_variaveis(ast_root)
        
        # Conta operadores usados no circuito
        used_gates = {'*': 0, '+': 0, '~': 0}
        connected_variables = set()
        
        for wire in self.wires:
            if wire.start_comp.type == 'variable':
                connected_variables.add(wire.start_comp.name)
            elif wire.start_comp.type in ['and', 'or', 'not']:
                gate_type = {'and': '*', 'or': '+', 'not': '~'}[wire.start_comp.type]
                if wire.start_comp in [w.end_comp for w in self.wires]:  # Se a porta tem entrada
                    used_gates[gate_type] += 1
        
        # Verifica se tem pelo menos as variáveis e operadores necessários conectados
        variables_ok = len(connected_variables) >= len(needed_variables)
        operators_ok = (used_gates['*'] >= needed_operators.get('*', 0) and 
                    used_gates['+'] >= needed_operators.get('+', 0) and
                    used_gates['~'] >= needed_operators.get('~', 0))
        
        return variables_ok and operators_ok
    
    def draw_success_message(self):
        """Desenha mensagem de parabéns quando o circuito está correto"""
        if not self.font:
            return
        
        # Fundo semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        # Mensagem principal
        messages = [
            "🎉 PARABÉNS! 🎉",
            "Circuito montado corretamente!",
            f"Expressão: {self.expressao}",
            "",
            "Pressione qualquer tecla para continuar..."
        ]
        
        start_y = self.screen_height // 2 - 100
        for i, message in enumerate(messages):
            if message.startswith("🎉"):
                color = (255, 215, 0)  # Dourado
                font_size = 48
            elif message.startswith("Circuito"):
                color = (0, 255, 0)   # Verde
                font_size = 36
            elif message.startswith("Expressão"):
                color = (255, 255, 255)  # Branco
                font_size = 24
            else:
                color = (200, 200, 200)  # Cinza claro
                font_size = 20
            
            try:
                font = pygame.font.Font(None, font_size)
                surface = font.render(message, True, color)
                rect = surface.get_rect(center=(self.screen_width//2, start_y + i * 40))
                self.screen.blit(surface, rect)
            except:
                pass
            
# --- Classe para Integração com Tkinter (Circuito Automático Original) ---
class CircuitoInterativo:
    def __init__(self, parent_frame, expressao):
        self.parent_frame = parent_frame; self.expressao = expressao; self.running = False
        self.pygame_thread = None; self.info_label = None; self.status_label = None
        self.parent_frame.after(100, self.init_pygame)
        self._move = {'up': False, 'down': False, 'left': False, 'right': False}
        self.parent_frame.after(100, self.init_pygame)
    
    def init_pygame(self):
        try:
            os.environ['SDL_WINDOWID'] = str(self.parent_frame.winfo_id())
            os.environ['SDL_VIDEODRIVER'] = 'windows'

            pygame.init(); pygame.font.init()
            self.parent_frame.update()

            self.screen_width  = max(800, self.parent_frame.winfo_width())
            self.screen_height = max(600, self.parent_frame.winfo_height())

            flags = pygame.DOUBLEBUF
            try:
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height),
                                                    flags, vsync=1)
            except TypeError:
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), flags)

            self.camera = Camera(self.screen_width, self.screen_height)
            self.drawer = CircuitDrawer(self.screen, self.camera)

            try:    self.font = pygame.font.Font(None, 24)
            except: self.font = None

            self.parent_frame.configure(bg="black", highlightthickness=0)
            self.parent_frame.focus_set()
            self.parent_frame.bind("<Enter>",   lambda e: self.parent_frame.focus_set())
            self.parent_frame.bind("<KeyPress>",  self._on_key_press)
            self.parent_frame.bind("<KeyRelease>", self._on_key_release)

            self.running = True
            self._tick()

        except Exception as e:
            tk.Label(self.parent_frame, text=f"Erro Pygame: {e}", fg="red", bg="black").pack()

    def _on_key_press(self, e):
        k = (e.keysym or "").lower()
        if k in ('w', 'up'):    self._move['up'] = True
        if k in ('s', 'down'):  self._move['down'] = True
        if k in ('a', 'left'):  self._move['left'] = True
        if k in ('d', 'right'): self._move['right'] = True
        if k == 'r':            self.camera.reset_view()

    def _on_key_release(self, e):
        k = (e.keysym or "").lower()
        if k in ('w', 'up'):    self._move['up'] = False
        if k in ('s', 'down'):  self._move['down'] = False
        if k in ('a', 'left'):  self._move['left'] = False
        if k in ('d', 'right'): self._move['right'] = False

    def _tick(self):
        if not self.running:
            try: pygame.quit()
            except: pass
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            self.camera.handle_event(event)

        if self._move['up']:    self.camera.move(0, -self.camera.move_speed)
        if self._move['down']:  self.camera.move(0,  self.camera.move_speed)
        if self._move['left']:  self.camera.move(-self.camera.move_speed, 0)
        if self._move['right']: self.camera.move( self.camera.move_speed, 0)

        self.screen.fill(self.drawer.BACKGROUND)
        expressao_booleana = converter_para_algebra_booleana(self.expressao)
        desenhar_circuito_logico_base(expressao_booleana, self.drawer, self.screen_width, self.screen_height)
        if self.font:
            draw_ui_info(self.screen, self.camera, self.font)

        pygame.display.flip()
        self.parent_frame.after(16, self._tick)

    def stop(self):
        self.running = False

# =========================================================================================
# FUNÇÕES DE COMPATIBILIDADE PARA A INTERFACE GRÁFICA PRINCIPAL
# =========================================================================================

def plotar_circuito_logico(expressao, x_offset=0, width=1200, height=800):
    """
    Função para gerar um PNG ESTÁTICO do circuito.
    MODIFICADA: Agora centraliza automaticamente o circuito na imagem.
    """
    from config import ASSETS_PATH
    try:
        if not pygame.get_init():
            pygame.init()
            pygame.font.init()
        
        # Cria uma superfície temporária para calcular as dimensões do circuito
        temp_screen = pygame.Surface((width, height))
        temp_camera = Camera(width, height)
        temp_drawer = CircuitDrawer(temp_screen, temp_camera)
        
        expressao_booleana = converter_para_algebra_booleana(expressao)
        
        # Calcula o layout e as dimensões do circuito
        try:
            ast_root = criar_ast_de_expressao(expressao_booleana)
            variaveis = sorted(list(_coletar_variaveis(ast_root)))
            
            # Calcula posições dos barramentos
            bus_x_start = 100
            bus_spacing = 100
            last_bus_x = bus_x_start + (len(variaveis) - 1) * bus_spacing + 40
            
            layout = calcular_layout_dinamico(ast_root, y_base=100)
            primeiro_gate_x = last_bus_x + 150
            circuit_end_x = primeiro_gate_x + layout.get('width', 0) + 200  # +200 para saída
            
            # Calcula o centro do circuito
            circuit_center_x = (bus_x_start + circuit_end_x) / 2
            circuit_center_y = layout['y_pos']
            
            # Ajusta a câmera para centralizar o circuito
            temp_camera.x = circuit_center_x
            temp_camera.y = circuit_center_y
            
            # Calcula o zoom necessário para mostrar todo o circuito
            circuit_width = circuit_end_x - bus_x_start
            circuit_height = layout['height'] + 200  # margem extra
            
            zoom_x = width / circuit_width
            zoom_y = height / circuit_height
            optimal_zoom = min(zoom_x, zoom_y, 1.5) * 0.8  # 0.8 para margem
            
            temp_camera.zoom = max(0.2, min(3.0, optimal_zoom))
            
        except Exception as e:
            print(f"Erro ao calcular layout: {e}")
            # Usa valores padrão se houver erro
            temp_camera.x = 400
            temp_camera.y = 300
            temp_camera.zoom = 1.0
        
        # Cria a superfície final com a câmera ajustada
        screen = pygame.Surface((width, height))
        screen.fill((0, 0, 0))
        drawer = CircuitDrawer(screen, temp_camera)
        
        desenhar_circuito_logico_base(expressao_booleana, drawer, width, height)
        
        caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
        pygame.image.save(screen, caminho_img)
        
    except Exception as e:
        print(f"Erro ao plotar circuito estático: {e}")
        raise

def criar_circuito_integrado(parent_frame, expressao):
    """
    Função "fábrica" para criar um CIRCUITO INTERATIVO com construção manual.
    """
    expressao_booleana = converter_para_algebra_booleana(expressao)
    return CircuitoInterativoManual(parent_frame, expressao_booleana)