"""
Módulo contendo as classes para componentes interativos do circuito lógico,
incluindo portas lógicas, variáveis e conectores.
"""

import pygame

class Component:
    """Classe base para componentes interativos do circuito."""
    
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
        """Define os pontos de conexão baseado no tipo do componente."""
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
        """Atualiza as posições dos pontos de conexão quando o componente é movido."""
        self._setup_connection_points()
    
    def get_rect(self):
        """Retorna o retângulo do componente para detecção de colisão."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, point):
        """Verifica se um ponto está dentro do componente."""
        x, y = point
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)


class Wire:
    """Classe representando uma conexão entre dois componentes."""
    
    def __init__(self, start_comp, start_output, end_comp, end_input):
        self.start_comp = start_comp
        self.start_output = start_output  # índice da saída
        self.end_comp = end_comp
        self.end_input = end_input  # índice da entrada
        self.selected = False
    
    def get_start_pos(self):
        """Retorna a posição inicial do fio."""
        return self.start_comp.outputs[self.start_output]
    
    def get_end_pos(self):
        """Retorna a posição final do fio."""
        return self.end_comp.inputs[self.end_input]