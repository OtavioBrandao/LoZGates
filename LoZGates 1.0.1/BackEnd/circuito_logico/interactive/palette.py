"""
    Módulo para o painel de seleção de componentes (paleta de ferramentas)
    onde o usuário pode escolher quais portas lógicas adicionar ao circuito.
"""

import pygame
import math

class ComponentPalette:
    """Painel de seleção de componentes para o circuito interativo."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = True
        self.x = 10
        self.y = 200
        self.width = 120
        self.height = 400
        
        #Componentes disponíveis
        self.components = [
            {'type': 'and', 'name': 'AND', 'color': (60, 120, 220)},
            {'type': 'or', 'name': 'OR', 'color': (50, 200, 130)},
            {'type': 'not', 'name': 'NOT', 'color': (250, 170, 70)},
            {'type': 'nand', 'name': 'NAND', 'color': (120, 60, 220)},
            {'type': 'nor', 'name': 'NOR', 'color': (200, 50, 130)},
            {'type': 'xor', 'name': 'XOR', 'color': (220, 120, 60)},
            {'type': 'xnor', 'name': 'XNOR', 'color': (60, 220, 120)}
        ]
        
        #Limitações ativas (None = sem limitações)
        self.allowed_gates = None
        self.button_height = 45
        self.button_margin = 5
        
        self.dragging_component = None
        self.drag_offset = (0, 0)
    
    def set_gate_limitations(self, allowed_gates):
        """Define quais portas são permitidas."""
        self.allowed_gates = allowed_gates
    
    def is_component_allowed(self, comp_type):
        """Verifica se um componente é permitido pelas limitações atuais."""
        if self.allowed_gates is None:
            return True
        return comp_type in self.allowed_gates
    
    def get_button_rect(self, index):
        """Retorna o retângulo de um botão específico."""
        y_pos = self.y + 30 + index * (self.button_height + self.button_margin)
        return pygame.Rect(self.x + 5, y_pos, self.width - 10, self.button_height)
    
    def handle_click(self, pos):
        """Processa cliques no painel."""
        if not self.visible or not self.point_in_palette(pos):
            return None
        
        #Verifica clique nos botões de componentes
        for i, component in enumerate(self.components):
            if not self.is_component_allowed(component['type']):
                continue
                
            button_rect = self.get_button_rect(i)
            if button_rect.collidepoint(pos):
                return component['type']
        
        return 'palette_click'  #Clicou no painel mas não em um botão
    
    def point_in_palette(self, pos):
        """Verifica se um ponto está dentro do painel."""
        palette_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return palette_rect.collidepoint(pos)
    
    def draw(self, screen, font=None):
        """Desenha o painel de componentes."""
        if not self.visible:
            return
        
        #Fundo do painel
        palette_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (40, 40, 40), palette_rect)
        pygame.draw.rect(screen, (100, 100, 100), palette_rect, 2)
        
        #Título
        if font:
            title_text = font.render("componentes", True, (255, 255, 255))
            title_rect = title_text.get_rect(centerx=self.x + self.width//2, y=self.y + 5)
            screen.blit(title_text, title_rect)
        
        #Botões dos componentes
        button_index = 0
        for i, component in enumerate(self.components):
            is_allowed = self.is_component_allowed(component['type'])
            
            button_rect = self.get_button_rect(button_index)
            
            #Cor do botão baseada na permissão
            if is_allowed:
                button_color = component['color']
                text_color = (255, 255, 255)
                border_color = (150, 150, 150)
            else:
                button_color = (60, 60, 60)
                text_color = (120, 120, 120)
                border_color = (80, 80, 80)
            
            #Desenha botão
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            #Desenha texto do componente
            if font:
                button_text = font.render(component['name'], True, text_color)
                text_rect = button_text.get_rect(center=button_rect.center)
                screen.blit(button_text, text_rect)
            
            #Desenha ícone pequeno da porta (simplificado)
            self._draw_gate_icon(screen, component['type'], button_rect, is_allowed)
            
            button_index += 1
        
        #Informações sobre limitações
        if self.allowed_gates and font:
            limit_y = self.y + self.height - 60
            limit_text = "LIMITADO A:"
            limit_surface = font.render(limit_text, True, (255, 255, 0))
            limit_rect = limit_surface.get_rect(centerx=self.x + self.width//2, y=limit_y)
            screen.blit(limit_surface, limit_rect)
            
            gates_text = ", ".join(self.allowed_gates).upper()
            gates_surface = font.render(gates_text, True, (255, 255, 0))
            gates_rect = gates_surface.get_rect(centerx=self.x + self.width//2, y=limit_y + 20)
            screen.blit(gates_surface, gates_rect)
    
    def _draw_gate_icon(self, screen, gate_type, button_rect, is_enabled):
        """Desenha ícone simplificado da porta lógica."""
        if not is_enabled:
            return
            
        #Posição do ícone (canto direito do botão)
        icon_x = button_rect.right - 25
        icon_y = button_rect.centery
        icon_size = 8
        
        color = (255, 255, 255) if is_enabled else (120, 120, 120)
        
        if gate_type in ['and', 'nand']:
            #Forma retangular com arco
            rect_points = [
                (icon_x - icon_size, icon_y - icon_size//2),
                (icon_x - 2, icon_y - icon_size//2),
                (icon_x - 2, icon_y + icon_size//2),
                (icon_x - icon_size, icon_y + icon_size//2)
            ]
            pygame.draw.polygon(screen, color, rect_points, 1)
            pygame.draw.arc(screen, color, 
                          (icon_x - 4, icon_y - icon_size//2, icon_size, icon_size), 
                          -math.pi/2, math.pi/2, 1)
            
            #Bolinha para NAND
            if gate_type == 'nand':
                pygame.draw.circle(screen, color, (icon_x + 6, icon_y), 2, 1)
        
        elif gate_type in ['or', 'nor']:
            #Forma curva para OR
            points = []
            for i in range(5):
                angle = -math.pi/4 + (i * math.pi/8)
                x = icon_x + icon_size//2 * math.cos(angle)
                y = icon_y + icon_size//2 * math.sin(angle)
                points.append((x, y))
            pygame.draw.lines(screen, color, False, points, 1)
            
            #Bolinha para NOR
            if gate_type == 'nor':
                pygame.draw.circle(screen, color, (icon_x + 6, icon_y), 2, 1)
        
        elif gate_type == 'not':
            #Triângulo com bolinha
            triangle_points = [
                (icon_x - icon_size, icon_y - icon_size//2),
                (icon_x - icon_size, icon_y + icon_size//2),
                (icon_x, icon_y)
            ]
            pygame.draw.polygon(screen, color, triangle_points, 1)
            pygame.draw.circle(screen, color, (icon_x + 4, icon_y), 2, 1)
        
        elif gate_type in ['xor', 'xnor']:
            #Duas curvas para XOR
            for offset in [-2, 0]:
                points = []
                for i in range(5):
                    angle = -math.pi/4 + (i * math.pi/8)
                    x = icon_x + offset + icon_size//3 * math.cos(angle)
                    y = icon_y + icon_size//2 * math.sin(angle)
                    points.append((x, y))
                pygame.draw.lines(screen, color, False, points, 1)
            
            #Bolinha para XNOR
            if gate_type == 'xnor':
                pygame.draw.circle(screen, color, (icon_x + 6, icon_y), 2, 1)
    
    def toggle_visibility(self):
        """Alterna a visibilidade do painel."""
        self.visible = not self.visible