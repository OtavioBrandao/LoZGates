"""
    Módulo para o circuito interativo manual atualizado com painel de seleção de componentes.
"""

import pygame
import tkinter as tk
import os
import math
import time
import itertools

from .components import Component, Wire, ComponentFactory
from .palette import ComponentPalette
from ..rendering.camera import Camera
from ..rendering.drawer import CircuitDrawer
from ..logic.parser import criar_ast_de_expressao, _coletar_variaveis, _coletar_operadores
from ..utils.history import CircuitHistory

class CircuitoInterativoManual:
    """Classe principal para o circuito interativo manual com painel de componentes."""
    
    def __init__(self, parent_frame, expressao, gate_restrictions=None):
        self.parent_frame = parent_frame
        self.expressao = expressao
        self.gate_restrictions = gate_restrictions  #Lista de portas permitidas ou None
        self.running = False
        self.interactive_mode = True

        #Componentes do circuito
        self.components = []
        self.wires = []
        self.selected_component = None
        self.connecting = False
        self.connection_start = None
        self.dragging_component = None

        #Painel de componentes
        self.component_palette = None

        #Sistema de histórico para undo/redo
        self.history = CircuitHistory()
        self.last_action_time = 0

        #Variáveis para mensagem de sucesso
        self.show_success_message = False
        self.success_message_timer = 0

        #Estado da interface
        self._move = {'up': False, 'down': False, 'left': False, 'right': False}

        #Inicialização com delay para garantir que o frame esteja pronto
        self.parent_frame.after(100, self.init_pygame)
    
    def init_pygame(self):
        """Inicializa o Pygame e configura a interface."""
        try:
            #Garante que o frame esteja visível e com tamanho definido
            self.parent_frame.update_idletasks()
            
            #Espera o frame estar pronto
            if self.parent_frame.winfo_width() <= 1 or self.parent_frame.winfo_height() <= 1:
                self.parent_frame.after(200, self.init_pygame)  #Tenta novamente
                return
            
            #Configurações do Pygame
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

            #Inicializa painel de componentes
            self.component_palette = ComponentPalette(self.screen_width, self.screen_height)
            if self.gate_restrictions:
                self.component_palette.set_gate_limitations(self.gate_restrictions)

            try:    
                self.font = pygame.font.Font(None, 24)
            except: 
                self.font = None

            #Configuração do frame Tkinter
            self.parent_frame.configure(bg="#000000", highlightthickness=0)
            self.parent_frame.focus_set()
            self.parent_frame.bind("<Enter>", lambda e: self.parent_frame.focus_set())
            self.parent_frame.bind("<KeyPress>", self._on_key_press)
            self.parent_frame.bind("<KeyRelease>", self._on_key_release)

            #Inicializa componentes baseado na expressão (apenas variáveis e saída)
            self.init_basic_components()
            
            #Configura referência para serialização e salva estado inicial
            self.history.set_components_reference(self.components)
            self.save_state("Initial state")

            self.running = True
            print(f"✅ Pygame inicializado com sucesso - {self.screen_width}x{self.screen_height}")
            self._tick()

        except Exception as e:
            print(f"❌ Erro ao inicializar Pygame: {e}")
            tk.Label(self.parent_frame, text=f"Erro Pygame: {e}", fg="red", bg="black").pack()
    
    def init_basic_components(self):
        """Inicializa apenas variáveis e saída - usuário adiciona as portas."""
        try:
            #Analisa a expressão para determinar variáveis necessárias
            ast_root = criar_ast_de_expressao(self.expressao)
            variables = sorted(list(_coletar_variaveis(ast_root)))
        except:
            #Fallback se houver erro no parsing
            variables = self.extract_variables(self.expressao)
        
        #Cria barramentos de variáveis na esquerda
        y_start = -100
        for i, var in enumerate(variables):
            comp = ComponentFactory.create_component('variable', -300, y_start + i * 100, var)
            self.components.append(comp)
            
        #Adiciona saída
        output_comp = ComponentFactory.create_component('output', 300, 0, 'SAÍDA')
        self.components.append(output_comp)
    
    def extract_variables(self, expressao):
        """Extrai variáveis únicas da expressão."""
        variables = set()
        for char in expressao:
            if char.isalpha() and char.upper() not in ['AND', 'OR', 'NOT']:
                variables.add(char.upper())
        return sorted(list(variables))
    
    def add_component_at_position(self, comp_type, world_pos):
        """Adiciona um componente na posição especificada."""
        x, y = world_pos
        #Centraliza o componente na posição do mouse
        x -= 40  #metade da largura padrão
        y -= 30  #metade da altura padrão
        
        new_component = ComponentFactory.create_component(comp_type, x, y)
        self.components.append(new_component)
        self.save_state(f"Add {comp_type} component")
        return new_component
    
    def save_state(self, action_description=""):
        """Salva o estado atual no histórico."""
        current_time = time.time()
        
        if current_time - self.last_action_time > 0.5:
            self.history.save_state(self.components, self.wires)
            self.last_action_time = current_time
            if action_description:
                print(f"Estado salvo: {action_description}")
    
    def restore_state(self, state_data):
        """Restaura um estado do histórico."""
        if not state_data:
            return
        
        #Limpa conexões atuais
        for comp in self.components:
            comp.input_connections.clear()
            comp.output_connections.clear()
        
        #Restaura componentes
        for i, comp_data in enumerate(state_data['components']):
            if i < len(self.components):
                comp = self.components[i]
                comp.x = comp_data['x']
                comp.y = comp_data['y']
                comp.selected = comp_data['selected']
                comp.update_connection_points()
        
        #Limpa fios existentes
        self.wires.clear()
        
        #Restaura fios
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
            
            #Reconecta as referências
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
        ctrl_pressed = (e.state & 0x4) != 0
        
        #Controles de undo/redo
        if ctrl_pressed:
            if k == 'z':
                if not self.undo():
                    print("Nada para desfazer")
                return
            elif k == 'y':
                if not self.redo():
                    print("Nada para refazer")
                return
        
        #Controles existentes
        if k in ('w', 'up'):    self._move['up'] = True
        if k in ('s', 'down'):  self._move['down'] = True
        if k in ('a', 'left'):  self._move['left'] = True
        if k in ('d', 'right'): self._move['right'] = True
        if k == 'r':            self.camera.reset_view()
        if k == 'delete':       
            self.delete_selected()
            self.save_state("Delete component")
        if k == 'escape':       self.cancel_connection()
        if k == 'tab':          #Toggle painel de componentes
            if self.component_palette:
                self.component_palette.toggle_visibility()
    
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
            #Remove conexões do componente
            for wire in self.wires[:]:
                if wire.start_comp == self.selected_component or wire.end_comp == self.selected_component:
                    if wire in wire.start_comp.output_connections:
                        wire.start_comp.output_connections.remove(wire)
                    if wire.end_input in wire.end_comp.input_connections:
                        del wire.end_comp.input_connections[wire.end_input]
                    
                    self.wires.remove(wire)
                    deleted_something = True
            
            #Remove componente (exceto variáveis e saída)
            if self.selected_component.type not in ['variable', 'output']:
                self.components.remove(self.selected_component)
                deleted_something = True
            
            self.selected_component = None
        
        #Remove fios selecionados
        for wire in self.wires[:]:
            if wire.selected:
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
    
    def find_connection_point(self, component, world_pos):
        """Encontra qual ponto de conexão foi clicado."""
        #Raio de detecção para as bolinhas
        detection_radius = 15
        
        #Verifica pontos de saída (bolinhas verdes)
        for i, output_pos in enumerate(component.outputs):
            distance = math.sqrt((world_pos[0] - output_pos[0])**2 + (world_pos[1] - output_pos[1])**2)
            if distance <= detection_radius:
                return ('output', i)
        
        #Verifica pontos de entrada (bolinhas azuis/vermelhas)
        for i, input_pos in enumerate(component.inputs):
            distance = math.sqrt((world_pos[0] - input_pos[0])**2 + (world_pos[1] - input_pos[1])**2)
            if distance <= detection_radius:
                return ('input', i)
        
        return None
    
    def handle_mouse_click(self, pos):
        """Gerencia cliques do mouse"""
        #Primeiro verifica se clicou no painel de componentes
        if self.component_palette and self.component_palette.visible:
            clicked_component_type = self.component_palette.handle_click(pos)
            if clicked_component_type:
                if clicked_component_type != 'palette_click':
                    #Adiciona componente na posição do mouse (convertida para mundo)
                    world_pos = self.camera.screen_to_world(pos)
                    self.add_component_at_position(clicked_component_type, world_pos)
                return  #Consumiu o clique
        
        world_pos = self.camera.screen_to_world(pos)
        
        #Verifica clique em componentes E em pontos de conexão
        clicked_component = None
        connection_point = None
        
        #Procura por componentes clicados
        for component in self.components:
            if component.contains_point(world_pos):
                clicked_component = component
                #Verifica se clicou especificamente em um ponto de conexão
                connection_point = self.find_connection_point(component, world_pos)
                break
        
        if clicked_component:
            #Se clicou em um ponto de conexão específico
            if connection_point:
                conn_type, conn_index = connection_point
                
                if self.connecting:
                    #Tentativa de finalizar conexão
                    if conn_type == 'input':
                        self.try_connect_to_input(clicked_component, conn_index)
                    else:
                        #Clicou em outra saída - cancela conexão atual e inicia nova
                        self.cancel_connection()
                        self.start_connection(clicked_component, conn_type, conn_index)
                else:
                    #Inicia nova conexão se clicou em saída
                    if conn_type == 'output':
                        self.start_connection(clicked_component, conn_type, conn_index)
                    else:
                        #Clicou em entrada sem estar conectando - seleciona componente
                        self.select_component(clicked_component)
            else:
                #Clicou no componente mas não em ponto de conexão - seleciona
                self.select_component(clicked_component)
        else:
            #Clicou no vazio - deseleciona tudo e cancela conexão
            self.deselect_all()
            self.cancel_connection()
    
    def select_component(self, component):
        """Seleciona um componente."""
        #Deseleciona outros
        for comp in self.components:
            comp.selected = False
        for wire in self.wires:
            wire.selected = False
        
        component.selected = True
        self.selected_component = component
    
    def deselect_all(self):
        """Deseleciona todos os componentes e fios."""
        for comp in self.components:
            comp.selected = False
        for wire in self.wires:
            wire.selected = False
        self.selected_component = None
    
    def start_connection(self, component, conn_type, index):
        """Inicia uma conexão a partir de um ponto de saída."""
        if conn_type == 'output':
            self.connecting = True
            self.connection_start = {
                'component': component,
                'type': conn_type,
                'index': index
            }
            print(f"🔗 Iniciando conexão de {component.type} saída {index}")
    
    def try_connect_to_input(self, target_component, input_index):
        """Tenta conectar à entrada especificada do componente alvo."""
        if not self.connection_start:
            return
        
        #Verifica se a entrada já está conectada
        if input_index in target_component.input_connections:
            print(f"❌ Entrada {input_index} já está conectada!")
            self.cancel_connection()
            return
        
        #Verifica se não está tentando conectar componente a si mesmo
        if self.connection_start['component'] == target_component:
            print("❌ Não é possível conectar componente a si mesmo!")
            self.cancel_connection()
            return
        
        #Cria o fio
        wire = Wire(
            self.connection_start['component'],
            self.connection_start['index'],
            target_component,
            input_index
        )
        self.wires.append(wire)
        
        #Registra as conexões
        self.connection_start['component'].output_connections.append(wire)
        target_component.input_connections[input_index] = wire
        
        print(f"✅ Conexão criada: {self.connection_start['component'].type} → {target_component.type}")
        
        #Salva estado após conexão
        self.save_state("Connect components")
        
        #Verifica se o circuito está correto
        self.check_circuit_completion()
        
        self.cancel_connection()
    
    def handle_mouse_drag(self, pos):
        """Gerencia arraste do mouse."""
        if self.selected_component and not self.connecting:
            world_pos = self.camera.screen_to_world(pos)
            
            #Move o componente (exceto variáveis)
            if self.selected_component.type not in ['variable']:
                old_x, old_y = self.selected_component.x, self.selected_component.y
                self.selected_component.x = world_pos[0] - self.selected_component.width // 2
                self.selected_component.y = world_pos[1] - self.selected_component.height // 2
                self.selected_component.update_connection_points()
                
                #Salva estado apenas se houve movimento significativo
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

        #Processa eventos do Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            
            #Primeiro verifica se a câmera consome o evento
            if not self.camera.handle_event(event, self.interactive_mode):
                #Se não foi consumido pela câmera, processa outros eventos
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_mouse_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:  #Botão esquerdo pressionado
                        self.handle_mouse_drag(event.pos)

        #Movimento contínuo via teclado
        if self._move['up']:    self.camera.move(0, -self.camera.move_speed)
        if self._move['down']:  self.camera.move(0,  self.camera.move_speed)
        if self._move['left']:  self.camera.move(-self.camera.move_speed, 0)
        if self._move['right']: self.camera.move( self.camera.move_speed, 0)

        #Desenha frame
        self.screen.fill(self.drawer.BACKGROUND)
        
        #Desenha grade de fundo
        self.drawer.draw_grid(self.screen_width, self.screen_height)
        
        #Desenha fios
        for wire in self.wires:
            self.drawer.draw_wire(wire)
        
        #Desenha componentes
        for component in self.components:
            self.drawer.draw_component(component)
        
        #Desenha linha de conexão temporária
        if self.connecting and self.connection_start:
            mouse_pos = pygame.mouse.get_pos()
            start_pos = self.connection_start['component'].outputs[self.connection_start['index']]
            start_screen = self.camera.world_to_screen(start_pos)
            pygame.draw.line(self.screen, self.drawer.YELLOW, start_screen, mouse_pos, 2)
        
        #Desenha painel de componentes
        if self.component_palette:
            self.component_palette.draw(self.screen, self.font)
        
        #Desenha informações
        if self.font:
            self.draw_ui_info()
        
        #Desenha mensagem de sucesso se ativa
        if self.show_success_message and self.success_message_timer > 0:
            self.draw_success_message()
            self.success_message_timer -= 1
            if self.success_message_timer <= 0:
                self.show_success_message = False

        pygame.display.flip()
        
        #Continua o loop se ainda estiver rodando
        if self.running:
            self.parent_frame.after(16, self._tick)
    
    def draw_ui_info(self):
        """Desenha informações de controle na tela"""
        '''#Ajusta posição se o painel está visível
        start_x = 150 if (self.component_palette and self.component_palette.visible) else 10
        
        ui_texts = [
            "=== MODO CONSTRUÇÃO INTERATIVA ===",
            f"Expressão: {self.expressao[:30]}{'...' if len(self.expressao) > 30 else ''}",
            "Status: " + ("Conectando..." if self.connecting else "Clique nas bolinhas verdes para conectar")
        ]
        
        #Adiciona informação sobre restrições se ativas
        if self.gate_restrictions:
            ui_texts.insert(-2, f"LIMITADO A: {', '.join(self.gate_restrictions).upper()}")
        
        y = 10
        for text in ui_texts:
            try:
                if text.startswith("==="):
                    color = (255, 255, 0)
                elif text.startswith("INSTRUÇÕES") or text.startswith("•"):
                    color = (0, 255, 255)
                elif text.startswith("LIMITADO"):
                    color = (255, 100, 100)  #Vermelho para restrições
                else:
                    color = (255, 255, 255)
                
                surface = self.font.render(text, True, color)
                self.screen.blit(surface, (start_x, y))
                y = y + 20 if not text.startswith("===") else y + 25
            except: 
                pass'''
        pass #Desativado por tempo indeterminado
    
    def stop(self):
        """Para o circuito."""
        self.running = False
        print("🛑 Circuito interativo parado")
    
    def check_circuit_completion(self):
        """Verifica se o circuito montado está correto conforme a expressão"""
        try:
            if self.is_circuit_correct():
                self.show_success_message = True
                self.success_message_timer = 300
                print("🎉 Circuito montado corretamente!")
        except Exception as e:
            print(f"Erro ao verificar circuito: {e}")

    def is_circuit_correct(self):
        """Verifica se o circuito implementa a expressão através de simulação com tabela verdade."""
        try:
            #Extrai variáveis da expressão
            variables = self.extract_variables(self.expressao)
            
            #Encontra componente de saída
            output_component = self.find_output_component()
            if not output_component:
                print("❌ Componente de saída não encontrado ou não conectado")
                return False
            
            #Simula todas as combinações possíveis
            return self.validate_truth_table(variables, output_component)
            
        except Exception as e:
            print(f"Erro na validação: {e}")
            return False

    def find_output_component(self):
        """Encontra e valida o componente de saída"""
        output_component = None
        for comp in self.components:
            if comp.type == 'output':
                output_component = comp
                break
        
        #Verifica se a saída tem exatamente uma conexão
        if not output_component or len(output_component.input_connections) != 1:
            return None
        
        return output_component

    def validate_truth_table(self, variables, output_component):
        """Valida o circuito comparando com a expressão original"""
        import itertools
        
        total_combinations = 2 ** len(variables)
        correct_results = 0
        
        print(f"🧪 Testando {total_combinations} combinações...")
        
        for combination in itertools.product([False, True], repeat=len(variables)):
            var_values = dict(zip(variables, combination))
            
            #Resultado esperado da expressão
            expected = self.evaluate_expression(self.expressao, var_values)
            
            #Resultado do circuito
            actual = self.simulate_circuit_simple(var_values)
            
            if expected == actual:
                correct_results += 1
            else:
                print(f"❌ Falha: {var_values} -> Esperado: {expected}, Obtido: {actual}")
                return False
        
        success_rate = (correct_results / total_combinations) * 100
        print(f"✅ Todas as {total_combinations} combinações corretas ({success_rate:.1f}%)")
        
        return correct_results == total_combinations

    def evaluate_expression(self, expression, var_values):
        """Avalia a expressão booleana com os valores fornecidos"""
        try:
            #Substitui variáveis pelos valores
            expr = expression.upper().replace(" ", "")
            
            #Substitui operadores para sintaxe Python
            expr = expr.replace("*", " and ").replace("+", " or ").replace("~", " not ")
            
            #Substitui variáveis pelos valores
            for var, value in var_values.items():
                expr = expr.replace(var, str(value))
            
            #Avalia a expressão
            result = eval(expr)
            return bool(result)
            
        except Exception as e:
            print(f"Erro ao avaliar expressão: {e}")
            return False

    def simulate_circuit_simple(self, var_values):
        """Simulação simplificada do circuito"""
        component_outputs = {}
        
        #Define valores das variáveis de entrada
        for comp in self.components:
            if comp.type == 'variable' and comp.name in var_values:
                component_outputs[comp] = var_values[comp.name]
        
        #Propaga valores através do circuito (máximo 10 iterações)
        for iteration in range(10):
            changes_made = False
            
            for comp in self.components:
                #Pula se já tem valor calculado
                if comp in component_outputs:
                    continue
                    
                #Verifica se é uma porta lógica
                if comp.type in ['and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor', 'output']:
                    input_values = self.get_component_inputs(comp, component_outputs)
                    
                    if input_values is not None:  #Todas as entradas estão prontas
                        output = self.calculate_gate_output_simple(comp.type, input_values)
                        if output is not None:
                            component_outputs[comp] = output
                            changes_made = True
            
            #Se nenhuma mudança foi feita, para a simulação
            if not changes_made:
                break
        
        #Retorna o valor da saída
        for comp in self.components:
            if comp.type == 'output' and comp in component_outputs:
                return component_outputs[comp]
        
        print("⚠️ Não foi possível determinar valor de saída")
        return False

    def get_component_inputs(self, component, component_outputs):
        """Obtém valores de entrada de um componente"""
        input_values = []
        
        #Determina quantas entradas o componente deveria ter
        expected_inputs = self.get_expected_input_count(component.type)
        if expected_inputs == 0:
            return []
        
        #Coleta valores das entradas conectadas
        for input_idx in range(expected_inputs):
            if input_idx in component.input_connections:
                wire = component.input_connections[input_idx]
                source_comp = wire.start_comp
                
                if source_comp in component_outputs:
                    input_values.append(component_outputs[source_comp])
                else:
                    return None  #Entrada não está pronta
            else:
                return None  #Entrada não conectada
        
        return input_values

    def get_expected_input_count(self, gate_type):
        """Retorna o número esperado de entradas para cada tipo de porta"""
        input_counts = {
            'and': 2, 'or': 2, 'not': 1, 'nand': 2, 
            'nor': 2, 'xor': 2, 'xnor': 2, 'output': 1
        }
        return input_counts.get(gate_type, 0)

    def calculate_gate_output_simple(self, gate_type, inputs):
        """Calcula saída da porta lógica - versão simplificada"""
        if not inputs:
            return False
        
        if gate_type == 'and':
            return all(inputs)
        elif gate_type == 'or':
            return any(inputs)
        elif gate_type == 'not':
            return not inputs[0] if len(inputs) >= 1 else False
        elif gate_type == 'nand':
            return not all(inputs)
        elif gate_type == 'nor':
            return not any(inputs)
        elif gate_type == 'xor':
            return sum(inputs) % 2 == 1
        elif gate_type == 'xnor':
            return sum(inputs) % 2 == 0
        elif gate_type == 'output':
            return inputs[0] if len(inputs) >= 1 else False
        
        return False

    
    def draw_success_message(self):
        """Desenha mensagem de parabéns quando o circuito está correto"""
        if not self.font:
            return
        
        #Fundo semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        #Mensagem principal
        messages = [
            " PARABÉNS! ",
            "Circuito montado corretamente!",
            ""
        ]
        
        "colocar aqui a mensagem de conclusão detalhada para cada limitação"
        
        if self.gate_restrictions:
            messages.append(f"Usando apenas: {', '.join(self.gate_restrictions).upper()}")
            messages.append("")
            
        messages.append("Pressione enter para continuar...")
        #tenho que colocar uma coisa para ver se clicou no enter
        
        
        start_y = self.screen_height // 2 - 120
        for i, message in enumerate(messages):
            if message.startswith("🎉"):
                color = (255, 215, 0)  #Dourado
                font_size = 48
            elif message.startswith("Circuito"):
                color = (0, 255, 0)   #Verde
                font_size = 36
            elif message.startswith("Expressão") or message.startswith("Usando"):
                color = (255, 255, 255)  #Branco
                font_size = 24
            else:
                color = (200, 200, 200)  #Cinza claro
                font_size = 20
            
            try:
                font = pygame.font.Font(None, font_size)
                surface = font.render(message, True, color)
                rect = surface.get_rect(center=(self.screen_width//2, start_y + i * 40))
                self.screen.blit(surface, rect)
            except:
                pass