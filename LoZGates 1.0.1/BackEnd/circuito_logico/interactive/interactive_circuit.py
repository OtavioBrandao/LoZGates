"""
Módulo para o circuito interativo manual onde o usuário pode construir
circuitos lógicos arrastando componentes e fazendo conexões.
"""

import pygame
import tkinter as tk
import os
import math
import time

from .components import Component, Wire
from ..rendering.camera import Camera
from ..rendering.drawer import CircuitDrawer
from ..logic.parser import criar_ast_de_expressao, _coletar_variaveis, _coletar_operadores
from ..utils.history import CircuitHistory

class CircuitoInterativoManual:
    """Classe principal para o circuito interativo manual."""
    
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
        """Inicializa o Pygame e configura a interface."""
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
        """Inicializa componentes baseado na expressão fornecida."""
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
        """Extrai variáveis únicas da expressão."""
        variables = set()
        for char in expressao:
            if char.isalpha() and char.upper() not in ['AND', 'OR', 'NOT']:
                variables.add(char.upper())
        return sorted(list(variables))
    
    def save_state(self, action_description=""):
        """Salva o estado atual no histórico."""
        current_time = time.time()
        
        # Evita salvar estados muito frequentemente (limita a 1 por 0.5 segundos)
        if current_time - self.last_action_time > 0.5:
            self.history.save_state(self.components, self.wires)
            self.last_action_time = current_time
            if action_description:
                print(f"Estado salvo: {action_description}")
    
    def restore_state(self, state_data):
        """Restaura um estado do histórico."""
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
        """Executa undo."""
        if self.history.can_undo():
            state = self.history.undo()
            self.restore_state(state)
            print("Undo executado")
            return True
        return False
    
    def redo(self):
        """Executa redo."""
        if self.history.can_redo():
            state = self.history.redo()
            self.restore_state(state)
            print("Redo executado")
            return True
        return False
    
    def _on_key_press(self, e):
        """Processa teclas pressionadas."""
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
        """Processa teclas liberadas."""
        k = (e.keysym or "").lower()
        if k in ('w', 'up'):    self._move['up'] = False
        if k in ('s', 'down'):  self._move['down'] = False
        if k in ('a', 'left'):  self._move['left'] = False
        if k in ('d', 'right'): self._move['right'] = False
    
    def delete_selected(self):
        """Deleta componente ou fio selecionado."""
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
        """Cancela conexão em andamento."""
        self.connecting = False
        self.connection_start = None
    
    def handle_mouse_click(self, pos):
        """Gerencia cliques do mouse."""
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
        """Inicia uma conexão a partir de um ponto."""
        if conn_type == 'output':
            self.connecting = True
            self.connection_start = {
                'component': component,
                'type': conn_type,
                'index': index
            }
    
    def try_connect(self, target_component, world_pos):
        """Tenta conectar ao componente alvo."""
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
        """Gerencia arraste do mouse."""
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
        """Loop principal de renderização."""
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
        self.drawer.draw_grid(self.screen_width, self.screen_height)
        
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