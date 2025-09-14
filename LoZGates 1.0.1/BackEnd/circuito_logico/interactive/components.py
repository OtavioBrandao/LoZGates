"""
    Módulo contendo as classes para componentes interativos do circuito lógico. 
"""
import pygame
import math

class Component:
    """Classe base para componentes interativos do circuito."""
    
    def __init__(self, x, y, comp_type, name=""):
        self.x = x
        self.y = y
        self.type = comp_type  #'variable', 'and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor', 'output'
        self.name = name
        
        #Área de seleção expandida para facilitar arraste
        if comp_type == 'variable':
            self.width = 80
            self.height = 60
            self.selection_padding = 10  #Área extra para seleção
        elif comp_type == 'output':
            self.width = 80
            self.height = 60  
            self.selection_padding = 10
        else:
            #Portas lógicas têm área de seleção maior
            self.width = 80
            self.height = 80            #Aumentado para facilitar seleção
            self.selection_padding = 15 #Área extra generosa para portas
        
        self.inputs = []                #Lista de pontos de entrada
        self.outputs = []               #Lista de pontos de saída
        self.input_connections = {}     #Dicionário de wires conectados às entradas
        self.output_connections = []    #Lista de wires conectados à saída
        self.dragging = False
        self.selected = False
        
        #Raio de tolerância para conexões - exatamente sobre as bolinhas
        self.connection_radius = 4      #Mesmo tamanho da bolinha verde
        
        self._setup_connection_points()
    
    def _setup_connection_points(self):
        """Define os pontos de conexão baseado no tipo do componente."""
        if self.type == 'variable':
            #Variável tem apenas saída
            self.outputs = [(self.x + self.width, self.y + self.height//2)]
        elif self.type == 'not':
            #NOT tem 1 entrada e 1 saída
            self.inputs = [(self.x, self.y + self.height//2)]
            self.outputs = [(self.x + self.width, self.y + self.height//2)]
        elif self.type in ['and', 'or', 'nand', 'nor', 'xor', 'xnor']:
            #Portas binárias têm 2 entradas e 1 saída
            self.inputs = [
                (self.x, self.y + self.height//3),
                (self.x, self.y + 2*self.height//3)
            ]
            self.outputs = [(self.x + self.width, self.y + self.height//2)]
        elif self.type == 'output':
            #Saída tem apenas entrada
            self.inputs = [(self.x, self.y + self.height//2)]
    
    def update_connection_points(self):
        """Atualiza as posições dos pontos de conexão quando o componente é movido."""
        self._setup_connection_points()
    
    def get_rect(self):
        """Retorna o retângulo do componente para detecção de colisão."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_selection_rect(self):
        """Retorna o retângulo expandido para seleção/arraste."""
        return pygame.Rect(
            self.x - self.selection_padding, 
            self.y - self.selection_padding,
            self.width + 2 * self.selection_padding, 
            self.height + 2 * self.selection_padding
        )
    
    def contains_point(self, point):
        """Verifica se um ponto está dentro da área de seleção expandida do componente."""
        x, y = point
        rect = self.get_selection_rect()
        return rect.collidepoint(x, y)
    
    def get_connection_point_at(self, point, connection_type='both'):
        """Verifica se um ponto está próximo de um ponto de conexão."""
        x, y = point
        
        #Verifica pontos de entrada
        if connection_type in ['input', 'both']:
            for i, input_pos in enumerate(self.inputs):
                dist = math.sqrt((x - input_pos[0])**2 + (y - input_pos[1])**2)
                if dist <= self.connection_radius:
                    return ('input', i)
        
        #Verifica pontos de saída
        if connection_type in ['output', 'both']:
            for i, output_pos in enumerate(self.outputs):
                dist = math.sqrt((x - output_pos[0])**2 + (y - output_pos[1])**2)
                if dist <= self.connection_radius:
                    return ('output', i)
        
        return None

class Wire:
    """Classe representando uma conexão entre dois componentes."""
    def __init__(self, start_comp, start_output, end_comp, end_input):
        self.start_comp = start_comp
        self.start_output = start_output    #Índice da saída
        self.end_comp = end_comp
        self.end_input = end_input          #Índice da entrada
        self.selected = False
        self.signal_state = False           #Para simulação futura
    
    def get_start_pos(self):
        """Retorna a posição inicial do fio."""
        return self.start_comp.outputs[self.start_output]
    
    def get_end_pos(self):
        """Retorna a posição final do fio."""
        return self.end_comp.inputs[self.end_input]


class ComponentFactory:
    """Factory para criar componentes com configurações padrão."""
    
    @staticmethod
    def create_component(comp_type, x, y, name=""):
        """Cria um componente do tipo especificado."""
        if comp_type == 'variable':
            return Component(x, y, comp_type, name or "VAR")
        elif comp_type == 'and':
            return Component(x, y, comp_type, "AND")
        elif comp_type == 'or':
            return Component(x, y, comp_type, "OR")
        elif comp_type == 'not':
            return Component(x, y, comp_type, "NOT")
        elif comp_type == 'nand':
            return Component(x, y, comp_type, "NAND")
        elif comp_type == 'nor':
            return Component(x, y, comp_type, "NOR")
        elif comp_type == 'xor':
            return Component(x, y, comp_type, "XOR")
        elif comp_type == 'xnor':
            return Component(x, y, comp_type, "XNOR")
        elif comp_type == 'output':
            return Component(x, y, comp_type, "SAÍDA")
        else:
            raise ValueError(f"Tipo de componente desconhecido: {comp_type}")
    
    @staticmethod
    def get_component_info():
        """Retorna informações sobre todos os tipos de componentes."""
        return {
            'variable': {'name': 'Variável', 'inputs': 0, 'outputs': 1, 'color': (255, 255, 255)},
            'and': {'name': 'AND', 'inputs': 2, 'outputs': 1, 'color': (60, 120, 220)},
            'or': {'name': 'OR', 'inputs': 2, 'outputs': 1, 'color': (50, 200, 130)},
            'not': {'name': 'NOT', 'inputs': 1, 'outputs': 1, 'color': (250, 170, 70)},
            'nand': {'name': 'NAND', 'inputs': 2, 'outputs': 1, 'color': (120, 60, 220)},
            'nor': {'name': 'NOR', 'inputs': 2, 'outputs': 1, 'color': (200, 50, 130)},
            'xor': {'name': 'XOR', 'inputs': 2, 'outputs': 1, 'color': (220, 120, 60)},
            'xnor': {'name': 'XNOR', 'inputs': 2, 'outputs': 1, 'color': (60, 220, 120)},
            'output': {'name': 'Saída', 'inputs': 1, 'outputs': 0, 'color': (220, 60, 60)}
        }