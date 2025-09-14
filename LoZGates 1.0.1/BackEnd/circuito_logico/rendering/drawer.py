"""
    Módulo responsável pela renderização visual dos circuitos lógicos,
    incluindo desenho de componentes, fios e as portas lógicas.
"""

import pygame
import math

class CircuitDrawer:
    """Responsável por desenhar elementos escaláveis do circuito lógico."""
    
    def __init__(self, screen, camera):
        self.screen = screen
        self.camera = camera
        
        #Cores do tema
        self.BACKGROUND = (0, 0, 0)
        self.WHITE = (230, 230, 230)
        self.BLUE = (60, 120, 220)
        self.GREEN = (50, 200, 130)
        self.ORANGE = (250, 170, 70)
        self.RED = (220, 60, 60)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (120, 60, 220)
        self.PINK = (200, 50, 130)
        self.BROWN = (220, 120, 60)
        self.TEAL = (60, 220, 120)
        self.LABEL_COLOR = (255, 255, 255)
        self.WIRE_COLOR = (200, 200, 200)
        self.SELECTED_COLOR = (255, 255, 0)
        self.CONNECTION_POINT_COLOR = (100, 255, 100)
        
        #Dimensões padrão
        self.GATE_WIDTH = 60
        self.GATE_HEIGHT = 80
        self.NODE_H_SPACING = 180
    
    def draw_line(self, start_world, end_world, color, width=2):
        """Desenha uma linha em coordenadas do mundo."""
        start_screen = self.camera.world_to_screen(start_world)
        end_screen = self.camera.world_to_screen(end_world)
        scaled_width = max(1, int(width * self.camera.zoom))
        pygame.draw.line(self.screen, color, start_screen, end_screen, scaled_width)
    
    def draw_circle(self, center_world, radius, color, width=0):
        """Desenha um círculo em coordenadas do mundo."""
        center_screen = self.camera.world_to_screen(center_world)
        scaled_radius = max(1, int(radius * self.camera.zoom))
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.circle(self.screen, color, center_screen, scaled_radius, scaled_width)
    
    def draw_polygon(self, points_world, color, width=0):
        """Desenha um polígono em coordenadas do mundo."""
        points_screen = [self.camera.world_to_screen(p) for p in points_world]
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.polygon(self.screen, color, points_screen, scaled_width)
    
    def draw_rect(self, rect_world, color, width=0):
        """Desenha um retângulo em coordenadas do mundo."""
        x, y, w, h = rect_world
        corners = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
        corners_screen = [self.camera.world_to_screen(corner) for corner in corners]
        scaled_width = max(1, int(width * self.camera.zoom)) if width > 0 else 0
        pygame.draw.polygon(self.screen, color, corners_screen, scaled_width)
    
    def draw_text(self, text, pos_world, font_size=36, color=None):
        """Desenha texto em coordenadas do mundo."""
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
        """Desenha as formas das portas lógicas."""
        w, h = self.GATE_WIDTH - 20, self.GATE_HEIGHT
        
        if name == 'AND':
            #Porta AND - retângulo com semicírculo à direita
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
            #Porta OR - forma curva 
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
            #Porta NOT - triângulo com círculo
            center_y = world_y + h/2
            points = [(world_x, world_y + 15), (world_x, world_y + h - 15), (world_x + 30, center_y)]
            self.draw_polygon(points, self.ORANGE, 3)
            self.draw_circle((world_x + 38, center_y), 8, self.ORANGE, 3)
            return (world_x + 46, center_y)
        
        elif name == 'NAND':
            #Porta NAND - AND com círculo de negação
            self._draw_and_shape(world_x, world_y, w, h, self.PURPLE)
            #Adiciona círculo de negação
            self.draw_circle((world_x + w + 8, world_y + h/2), 8, self.PURPLE, 3)
            return (world_x + w + 16, world_y + h/2)
        
        elif name == 'NOR':
            #Porta NOR - OR com círculo de negação
            self._draw_or_shape(world_x, world_y, w, h, self.PINK)
            #Adiciona círculo de negação
            self.draw_circle((world_x + w + 8, world_y + h/2), 8, self.PINK, 3)
            return (world_x + w + 16, world_y + h/2)
        
        elif name == 'XOR':
            #Porta XOR - OR com linha adicional
            self._draw_xor_shape(world_x, world_y, w, h, self.BROWN)
            return (world_x + w, world_y + h/2)
        
        elif name == 'XNOR':
            #Porta XNOR - XOR com círculo de negação
            self._draw_xor_shape(world_x, world_y, w, h, self.TEAL)
            #Adiciona círculo de negação
            self.draw_circle((world_x + w + 8, world_y + h/2), 8, self.TEAL, 3)
            return (world_x + w + 16, world_y + h/2)
    
    def _draw_and_shape(self, world_x, world_y, w, h, color):
        """Desenha forma AND com cor específica."""
        self.draw_line((world_x, world_y), (world_x, world_y + h), color, 3)
        self.draw_line((world_x, world_y), (world_x + w/2, world_y), color, 3)
        self.draw_line((world_x, world_y + h), (world_x + w/2, world_y + h), color, 3)
        center = (world_x + w/2, world_y + h/2)
        for i in range(16):
            a1 = -math.pi/2 + (i * math.pi/16)
            a2 = -math.pi/2 + ((i+1) * math.pi/16)
            p1 = (center[0] + (w/2) * math.cos(a1), center[1] + (h/2) * math.sin(a1))
            p2 = (center[0] + (w/2) * math.cos(a2), center[1] + (h/2) * math.sin(a2))
            self.draw_line(p1, p2, color, 3)
    
    def _draw_or_shape(self, world_x, world_y, w, h, color):
        """Desenha forma OR com cor específica."""
        back_center = (world_x - 7.5, world_y + h/2)
        front_center = (world_x + w/2, world_y + h/2)
        for i in range(16):
            a1 = -math.pi/2 + (i * math.pi/16)
            a2 = -math.pi/2 + ((i+1) * math.pi/16)
            p1_b = (back_center[0] + 10 * math.cos(a1), back_center[1] + (h/2) * math.sin(a1))
            p2_b = (back_center[0] + 10 * math.cos(a2), back_center[1] + (h/2) * math.sin(a2))
            self.draw_line(p1_b, p2_b, color, 3)
            p1_f = (front_center[0] + (w/2) * math.cos(a1), front_center[1] + (h/2) * math.sin(a1))
            p2_f = (front_center[0] + (w/2) * math.cos(a2), front_center[1] + (h/2) * math.sin(a2))
            self.draw_line(p1_f, p2_f, color, 3)
        self.draw_line((back_center[0], back_center[1] - h/2), (front_center[0], front_center[1] - h/2), color, 3)
        self.draw_line((back_center[0], back_center[1] + h/2), (front_center[0], front_center[1] + h/2), color, 3)
    
    def _draw_xor_shape(self, world_x, world_y, w, h, color):
        """Desenha forma XOR com cor específica."""
        #Linha extra 
        extra_back_center = (world_x - 15, world_y + h/2)
        for i in range(16):
            a1 = -math.pi/2 + (i * math.pi/16)
            a2 = -math.pi/2 + ((i+1) * math.pi/16)
            p1_extra = (extra_back_center[0] + 8 * math.cos(a1), extra_back_center[1] + (h/2 - 5) * math.sin(a1))
            p2_extra = (extra_back_center[0] + 8 * math.cos(a2), extra_back_center[1] + (h/2 - 5) * math.sin(a2))
            self.draw_line(p1_extra, p2_extra, color, 3)
        
        #Forma OR principal
        self._draw_or_shape(world_x, world_y, w, h, color)
    
    def draw_smart_wire(self, start_world, end_world):
        """Desenha um fio com curvas inteligentes."""
        x1, y1 = start_world
        x2, y2 = end_world
        mid_x = x1 + (x2 - x1) * 0.5
        self.draw_line((x1, y1), (mid_x, y1), self.WIRE_COLOR, 2)
        self.draw_line((mid_x, y1), (mid_x, y2), self.WIRE_COLOR, 2)
        self.draw_line((mid_x, y2), (x2, y2), self.WIRE_COLOR, 2)
    
    def draw_connection_dot(self, pos_world, color=None, radius=5):
        """Desenha um ponto de conexão."""
        if color is None: 
            color = self.WIRE_COLOR
        self.draw_circle(pos_world, radius, color)
    
    def draw_component(self, component):
        """Desenha componente interativo usando o estilo das portas."""
        color = self.SELECTED_COLOR if component.selected else self.WHITE
        
        if component.type == 'variable':
            #Desenha retângulo para variável
            self.draw_rect((component.x, component.y, component.width, component.height), color, 2)
            self.draw_text(component.name, (component.x + component.width//2, component.y + component.height//2), 20)
        
        elif component.type in ['and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor']:
            #Mapeia tipos para nomes
            gate_names = {
                'and': 'AND', 'or': 'OR', 'not': 'NOT', 
                'nand': 'NAND', 'nor': 'NOR', 'xor': 'XOR', 'xnor': 'XNOR'
            }
            
            #Usa o desenho original da porta
            gate_y = component.y + (component.height - self.GATE_HEIGHT)//2
            gate_output_pos = self.draw_gate_shape(gate_names[component.type], component.x, gate_y)
            
            #Ajusta as saídas baseado no desenho real
            component.outputs = [gate_output_pos]
            
            #Recalcula as posições de entrada baseado no desenho da porta
            gate_center_y = gate_y + self.GATE_HEIGHT//2
            
            if component.type == 'not':
                #NOT tem apenas 1 entrada
                component.inputs = [(component.x, gate_center_y)]
            else:
                #Outras portas têm 2 entradas
                component.inputs = [
                    (component.x, gate_center_y - 20),  #Entrada superior
                    (component.x, gate_center_y + 20)   #Entrada inferior
                ]
        
        elif component.type == 'output':
            #Desenha saída
            self.draw_rect((component.x, component.y, component.width, component.height), self.RED, 2)
            self.draw_text("SAÍDA", (component.x + component.width//2, component.y + component.height//2), 16)
        
        #Desenha pontos de conexão de entrada
        for i, input_pos in enumerate(component.inputs):
            color = self.CONNECTION_POINT_COLOR
            if i in component.input_connections:
                color = self.YELLOW                 #Conectado
            self.draw_circle(input_pos, 4, color)
        
        #Desenha pontos de saída
        for output_pos in component.outputs:
            color = self.CONNECTION_POINT_COLOR
            if component.output_connections:
                color = self.YELLOW                 #Conectado
            self.draw_circle(output_pos, 4, color)
            
    def draw_wire(self, wire):
        """Desenha um fio conectando dois componentes."""
        start_pos = wire.get_start_pos()
        end_pos = wire.get_end_pos()
        
        color = self.SELECTED_COLOR if wire.selected else self.WIRE_COLOR
        
        #Desenha fio com curvas suaves
        mid_x = start_pos[0] + (end_pos[0] - start_pos[0]) * 0.7
        self.draw_line(start_pos, (mid_x, start_pos[1]), color, 3)
        self.draw_line((mid_x, start_pos[1]), (mid_x, end_pos[1]), color, 3)
        self.draw_line((mid_x, end_pos[1]), end_pos, color, 3)
    
    def draw_grid(self, screen_width, screen_height):
        """Desenha uma grade de fundo para facilitar o posicionamento."""
        grid_size = 50
        color = (30, 30, 30)
        
        #Calcula limites visíveis com margem extra para evitar bugs
        top_left = self.camera.screen_to_world((0, 0))
        bottom_right = self.camera.screen_to_world((screen_width, screen_height))
        
        #Adiciona margem extra para garantir cobertura completa
        margin = grid_size * 2
        top_left = (top_left[0] - margin, top_left[1] - margin)
        bottom_right = (bottom_right[0] + margin, bottom_right[1] + margin)
        
        #Desenha linhas verticais
        start_x = int(top_left[0] / grid_size) * grid_size
        end_x = int(bottom_right[0] / grid_size) * grid_size + grid_size
        
        for x in range(start_x, end_x + grid_size, grid_size):
            self.draw_line((x, top_left[1]), (x, bottom_right[1]), color, 1)
        
        #Desenha linhas horizontais
        start_y = int(top_left[1] / grid_size) * grid_size
        end_y = int(bottom_right[1] / grid_size) * grid_size + grid_size
        
        for y in range(start_y, end_y + grid_size, grid_size):
            self.draw_line((top_left[0], y), (bottom_right[0], y), color, 1)