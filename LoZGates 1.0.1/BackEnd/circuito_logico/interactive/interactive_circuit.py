#Módulo para o circuito interativo manual atualizado com painel de seleção de componentes.

import pygame
import tkinter as tk
import logging
import math
import time

from .components import Wire, ComponentFactory
from .palette import ComponentPalette
from ..rendering.camera import Camera
from ..rendering.drawer import CircuitDrawer
from ..logic.parser import criar_ast_de_expressao, _coletar_variaveis
from ..utils.history import CircuitHistory
from ..platform_support import configure_sdl_embedding, fit_surface_size
from BackEnd.equivalencia import UniversalLogicAnalyzer


logger = logging.getLogger(__name__)

class CircuitoInterativoManual:    
    def __init__(self, parent_frame, expressao, gate_restrictions=None, logger=None, mode_key=None):
        self.parent_frame = parent_frame
        self.expressao = expressao
        self.gate_restrictions = gate_restrictions  #Lista de portas permitidas ou None
        self.logger = logger # Add logger
        self.mode_key = mode_key
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

        #Variáveis para mensagem de sucesso/erro
        self.show_success_message = False
        self.success_message_timer = 0
        self.show_error_message = False
        self.error_message_timer = 0
        self.error_message_text = ""

        #Estado da interface
        self._move = {'up': False, 'down': False, 'left': False, 'right': False}

        #Inicialização com delay para garantir que o frame esteja pronto
        self.parent_frame.after(100, self.init_pygame)
        
        #Para selecionar e posicionar componentes de acordo com o mouse
        self.ghost_component = None  #Componente sendo posicionado
        self.ghost_component_type = None  #Tipo do componente fantasma
        self.placing_component = False  #Se está no modo de colocação
        
        #Sistema de colisão
        self.collision_margin = 10  #Margem mínima entre componentes

        #referencia logger
        self.logger = logger
        
        #Callback para controle de scroll externo
        self.scroll_control_callback = None
        self._resize_after_id = None
        self._configure_binding_id = None

    def _create_display_surface(self, size):
        try:
            return pygame.display.set_mode(size, self.display_flags, vsync=1)
        except (TypeError, pygame.error):
            return pygame.display.set_mode(size, self.display_flags)

    def _on_parent_configure(self, event):
        if not self.running or event.widget is not self.parent_frame:
            return
        if event.width <= 1 or event.height <= 1:
            return
        if self._resize_after_id:
            try:
                self.parent_frame.after_cancel(self._resize_after_id)
            except (tk.TclError, ValueError):
                pass
        self._resize_after_id = self.parent_frame.after(
            100,
            lambda width=event.width, height=event.height: self._resize_surface(
                width, height
            ),
        )

    def _resize_surface(self, width, height):
        self._resize_after_id = None
        if not self.running:
            return
        new_size = fit_surface_size(width, height)
        if new_size == (self.screen_width, self.screen_height):
            return
        self.screen_width, self.screen_height = new_size
        self.screen = self._create_display_surface(new_size)
        self.camera.update_viewport(*new_size)
        self.drawer.screen = self.screen
        if self.component_palette:
            self.component_palette.resize(*new_size)
        logger.debug("Superficie Pygame redimensionada para %sx%s", *new_size)
    
    def init_pygame(self): #Inicializa o Pygame e configura a interface.
        try:
            #Garante que o frame esteja visível e com tamanho definido
            self.parent_frame.update_idletasks()
            
            #Espera o frame estar pronto
            if self.parent_frame.winfo_width() <= 1 or self.parent_frame.winfo_height() <= 1:
                self.parent_frame.after(200, self.init_pygame) 
                return
            
            #Configurações do Pygame
            configure_sdl_embedding(self.parent_frame.winfo_id())

            pygame.init()
            pygame.font.init()
            self.parent_frame.update()

            self.screen_width, self.screen_height = fit_surface_size(
                self.parent_frame.winfo_width(), self.parent_frame.winfo_height()
            )

            self.display_flags = pygame.DOUBLEBUF
            self.screen = self._create_display_surface(
                (self.screen_width, self.screen_height)
            )

            self.camera = Camera(self.screen_width, self.screen_height)
            self.camera.on_mouse_enter = self._on_pygame_mouse_enter
            self.camera.on_mouse_leave = self._on_pygame_mouse_leave
            self.drawer = CircuitDrawer(self.screen, self.camera)

            #Inicializa painel de componentes
            self.component_palette = ComponentPalette(self.screen_width, self.screen_height)
            if self.gate_restrictions:
                self.component_palette.set_gate_limitations(self.gate_restrictions)

            try:    
                self.font = pygame.font.Font(None, 24)
            except pygame.error:
                self.font = None

            #Configuração do frame Tkinter
            self.parent_frame.configure(bg="#000000", highlightthickness=0)
            self.parent_frame.focus_set()
            self.parent_frame.bind("<Enter>", lambda e: self.parent_frame.focus_set())
            self.parent_frame.bind("<KeyPress>", self._on_key_press)
            self.parent_frame.bind("<KeyRelease>", self._on_key_release)
            self._configure_binding_id = self.parent_frame.bind(
                "<Configure>", self._on_parent_configure, add="+"
            )

            #Inicializa componentes baseado na expressão (apenas variáveis e saída)
            self.init_basic_components()
            
            #Configura referência para serialização e salva estado inicial
            self.history.set_components_reference(self.components)
            self.save_state("Initial state")

            self.running = True
            logger.info(
                "Pygame interativo inicializado em %sx%s",
                self.screen_width,
                self.screen_height,
            )
            self._tick()

        except Exception as e:
            logger.exception("Erro ao inicializar Pygame interativo")
            tk.Label(self.parent_frame, text=f"Erro Pygame: {e}", fg="red", bg="black").pack()
    
    def init_basic_components(self): #Inicializa apenas variáveis e saída - usuário adiciona as portas.
        try:
            #Analisa a expressão para determinar variáveis necessárias
            ast_root = criar_ast_de_expressao(self.expressao)
            variables = sorted(list(_coletar_variaveis(ast_root)))
        except ValueError:
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
    
    def extract_variables(self, expressao): #Extrai variáveis únicas da expressão.
        variables = set()
        for char in expressao:
            if char.isalpha() and char.upper() not in ['AND', 'OR', 'NOT']:
                variables.add(char.upper())
        return sorted(list(variables))
    
    def check_collision(self, component, x, y, exclude_component=None): #"Verifica se há colisão entre componentes na posição especificada.
        temp_rect = pygame.Rect(
            x - self.collision_margin, 
            y - self.collision_margin,
            component.width + 2 * self.collision_margin, 
            component.height + 2 * self.collision_margin
        )
        
        #Verifica colisão com outros componentes
        for other_comp in self.components:
            #Ignora o próprio componente e componente excluído
            if other_comp == component or other_comp == exclude_component:
                continue
            
            #Ignora componente fantasma se estiver sendo colocado
            if other_comp == self.ghost_component:
                continue
            
            #Cria retângulo do outro componente com margem
            other_rect = pygame.Rect(
                other_comp.x - self.collision_margin,
                other_comp.y - self.collision_margin, 
                other_comp.width + 2 * self.collision_margin,
                other_comp.height + 2 * self.collision_margin
            )
            
            #Verifica sobreposição
            if temp_rect.colliderect(other_rect):
                return True
        
        return False
    
    def find_valid_position(self, component, preferred_x, preferred_y): #Encontra uma posição válida próxima à posição preferida (sem colisão).
        if not self.check_collision(component, preferred_x, preferred_y):
            return preferred_x, preferred_y
        
        #Busca em espiral a partir da posição preferida
        max_offset = 200  #Máximo de deslocamento para buscar
        step = 30  #Tamanho do passo
        
        for radius in range(step, max_offset, step):
            #Testa posições em círculo ao redor da posição preferida
            for angle in range(0, 360, 30):  #A cada 30 graus
                offset_x = radius * math.cos(math.radians(angle))
                offset_y = radius * math.sin(math.radians(angle))
                
                test_x = preferred_x + offset_x
                test_y = preferred_y + offset_y
                
                if not self.check_collision(component, test_x, test_y):
                    return test_x, test_y
        
        #Se não encontrou posição válida, retorna a preferida mesmo com colisão
        logger.warning("Nao foi encontrada posicao sem colisao para %s", component.type)
        return preferred_x, preferred_y
    
    def add_component_at_position(self, comp_type, world_pos): #Adiciona um componente na posição especificada, verificando colisão.
        if self.logger:
            self.logger.log_component_action("add", comp_type)
            
        x, y = world_pos
        #Centraliza o componente na posição do mouse
        x -= 40  #metade da largura padrão
        y -= 30  #metade da altura padrão
        
        new_component = ComponentFactory.create_component(comp_type, x, y)
        
        #Verifica e ajusta posição para evitar colisão
        valid_x, valid_y = self.find_valid_position(new_component, x, y)
        new_component.x = valid_x
        new_component.y = valid_y
        new_component.update_connection_points()
        
        self.components.append(new_component)
        self.save_state(f"Add {comp_type} component")
        
        #Feedback visual se houve ajuste de posição
        if abs(valid_x - x) > 5 or abs(valid_y - y) > 5:
            logger.debug("Posicao de %s ajustada para evitar colisao", comp_type)
        
        return new_component
    
    def save_state(self, action_description=""): #Salva o estado atual no histórico.
        current_time = time.time()
        
        if current_time - self.last_action_time > 0.5:
            self.history.save_state(self.components, self.wires)
            self.last_action_time = current_time
            if action_description:
                logger.debug("Estado do circuito salvo: %s", action_description)
    
    def restore_state(self, state_data): #Restaura um estado do histórico.
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
        if self.history.can_undo():
            #Log do undo
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_component_action("undo")
            
            state = self.history.undo()
            self.restore_state(state)
            logger.info("Undo do circuito executado")
            return True
        return False
    
    def redo(self):
        if self.history.can_redo():
            state = self.history.redo()
            self.restore_state(state)
            logger.info("Redo do circuito executado")
            return True
        return False
    
    def _on_key_press(self, e): #Processa teclas pressionadas.
        k = (e.keysym or "").lower()
        ctrl_pressed = (e.state & 0x4) != 0
        
        #Controles de undo/redo
        if ctrl_pressed:
            if k == 'z':
                if not self.undo():
                    logger.debug("Nao ha acao do circuito para desfazer")
                return
            elif k == 'y':
                if not self.redo():
                    logger.debug("Nao ha acao do circuito para refazer")
                return
        
        #Cancelar colocação de componente
        if k == 'escape':
            if self.placing_component:
                self.cancel_component_placement()
            else:
                self.cancel_connection()
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
        if k == 'space':        #Testar circuito
            self.test_circuit_manual()
            
    def _on_key_release(self, e): #Processa teclas liberadas.
        k = (e.keysym or "").lower()
        if k in ('w', 'up'):    self._move['up'] = False
        if k in ('s', 'down'):  self._move['down'] = False
        if k in ('a', 'left'):  self._move['left'] = False
        if k in ('d', 'right'): self._move['right'] = False
    
    def delete_selected(self):
        deleted_something = False
        
        if self.selected_component:
            #Log da deleção
            if self.logger:
                self.logger.log_component_action("delete", self.selected_component.type)
            
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
                if self.logger:
                    self.logger.log_component_action("delete_connection")
                if wire in wire.start_comp.output_connections:
                    wire.start_comp.output_connections.remove(wire)
                if wire.end_input in wire.end_comp.input_connections:
                    del wire.end_comp.input_connections[wire.end_input]
                
                self.wires.remove(wire)
                deleted_something = True
        
        return deleted_something
    
    def cancel_connection(self):
        self.connecting = False
        self.connection_start = None
    
    def find_connection_point(self, component, world_pos): #Encontra qual ponto de conexão foi clicado.
        detection_radius = 15
        
        #Verifica pontos de saída 
        for i, output_pos in enumerate(component.outputs):
            distance = math.sqrt((world_pos[0] - output_pos[0])**2 + (world_pos[1] - output_pos[1])**2)
            if distance <= detection_radius:
                return ('output', i)
        
        #Verifica pontos de entrada 
        for i, input_pos in enumerate(component.inputs):
            distance = math.sqrt((world_pos[0] - input_pos[0])**2 + (world_pos[1] - input_pos[1])**2)
            if distance <= detection_radius:
                return ('input', i)
        
        return None
    
    def handle_mouse_click(self, pos): #"Gerencia cliques do mouse
        #Se está colocando componente, finaliza a colocação
        if self.placing_component and self.ghost_component:
            self.place_ghost_component(pos)
            return
        
        #Verifica se clicou no painel de componentes
        if self.component_palette and self.component_palette.visible:
            clicked_component_type = self.component_palette.handle_click(pos)
            if clicked_component_type:
                if clicked_component_type != 'palette_click':
                    #Inicia modo de colocação ao invés de colocar diretamente
                    self.start_component_placement(clicked_component_type)
                return  #Consumiu o clique
        
        world_pos = self.camera.screen_to_world(pos)
        
        #Verifica clique em componentes E em pontos de conexão
        clicked_component = None
        connection_point = None
        
        #Procura por componentes clicados (ignora o componente fantasma)
        for component in self.components:
            if component != self.ghost_component and component.contains_point(world_pos):
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

    def start_component_placement(self, component_type): #Inicia o modo de colocação de componente.
        self.placing_component = True
        self.ghost_component_type = component_type
        
        #Cria componente fantasma na posição do mouse
        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.camera.screen_to_world(mouse_pos)
        
        self.ghost_component = ComponentFactory.create_component(
            component_type, 
            world_pos[0] - 40, 
            world_pos[1] - 30
        )
        
        #Adiciona temporariamente à lista para renderização
        self.components.append(self.ghost_component)
        
        logger.debug("Modo de colocacao ativado: %s", component_type)

    def place_ghost_component(self, screen_pos): #Finaliza a colocação do componente fantasma com verificação de colisão.
        if not self.ghost_component:
            return
        
        world_pos = self.camera.screen_to_world(screen_pos)
        
        #Calcula posição centralizada
        preferred_x = world_pos[0] - 40
        preferred_y = world_pos[1] - 30
        
        #Encontra posição válida sem colisão
        valid_x, valid_y = self.find_valid_position(self.ghost_component, preferred_x, preferred_y)
        
        #Atualiza posição final
        self.ghost_component.x = valid_x
        self.ghost_component.y = valid_y
        self.ghost_component.update_connection_points()
        
        #Feedback visual se houve ajuste
        if abs(valid_x - preferred_x) > 5 or abs(valid_y - preferred_y) > 5:
            logger.debug("Componente reposicionado para evitar colisao")
        
        #Finaliza colocação
        self.placing_component = False
        self.save_state(f"Place {self.ghost_component_type} component")
        
        logger.info("Componente %s colocado", self.ghost_component_type)
        if hasattr(self, 'logger') and self.logger:
            self.logger.log_component_action("add", self.ghost_component_type)
        
        #Limpa referências
        self.ghost_component = None
        self.ghost_component_type = None

    def cancel_component_placement(self): #Cancela a colocação de componente.
        if self.ghost_component and self.ghost_component in self.components:
            self.components.remove(self.ghost_component)
        
        self.ghost_component = None
        self.ghost_component_type = None
        self.placing_component = False
        
        logger.debug("Colocacao de componente cancelada")

    def update_ghost_component_position(self): #Atualiza posição do componente fantasma para seguir o mouse.
        if self.placing_component and self.ghost_component:
            mouse_pos = pygame.mouse.get_pos()
            world_pos = self.camera.screen_to_world(mouse_pos)
            
            self.ghost_component.x = world_pos[0] - 40
            self.ghost_component.y = world_pos[1] - 30
            self.ghost_component.update_connection_points()
        
    def select_component(self, component): #Seleciona um componente.
        #Deseleciona outros
        for comp in self.components:
            comp.selected = False
        for wire in self.wires:
            wire.selected = False
        
        component.selected = True
        self.selected_component = component
    
    def deselect_all(self): #Deseleciona todos os componentes e fios.
        for comp in self.components:
            comp.selected = False
        for wire in self.wires:
            wire.selected = False
        self.selected_component = None
    
    def start_connection(self, component, conn_type, index): #Inicia uma conexão a partir de um ponto de saída.
        if conn_type == 'output':
            self.connecting = True
            self.connection_start = {
                'component': component,
                'type': conn_type,
                'index': index
            }
            logger.debug("Iniciando conexao da saida %s de %s", index, component.type)

    def try_connect_to_input(self, target_component, input_index): #Tenta conectar à entrada especificada do componente alvo.
        if not self.connection_start:
            return
        
        #Verifica se a entrada já está conectada
        if input_index in target_component.input_connections:
            logger.warning("Entrada %s ja esta conectada", input_index)
            self.cancel_connection()
            return
        
        #Verifica se não está tentando conectar componente a si mesmo
        if self.connection_start['component'] == target_component:
            logger.warning("Tentativa de conectar um componente a si mesmo")
            self.cancel_connection()
            return
        
        if hasattr(self, 'logger') and self.logger:
            self.logger.log_component_action("connect")
        
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
        
        logger.info(
            "Conexao criada: %s -> %s",
            self.connection_start['component'].type,
            target_component.type,
        )
        
        #Salva estado após conexão
        self.save_state("Connect components")
        
        #Remove validação automática - usuário testará manualmente
        #self.check_circuit_completion()
        
        self.cancel_connection()
    
    def handle_mouse_drag(self, pos): #Gerencia arraste do mouse com verificação de colisão.
        if self.selected_component and not self.connecting:
            world_pos = self.camera.screen_to_world(pos)
            
            #Move o componente
            if self.selected_component.type not in ['']: #caso queira adicionar alguma porta que precisa ser fixa, basta adicionar nessa lista
                old_x, old_y = self.selected_component.x, self.selected_component.y
                new_x = world_pos[0] - self.selected_component.width // 2
                new_y = world_pos[1] - self.selected_component.height // 2
                
                #Verifica colisão na nova posição
                if not self.check_collision(self.selected_component, new_x, new_y, exclude_component=self.selected_component):
                    #Posição válida - move o componente
                    self.selected_component.x = new_x
                    self.selected_component.y = new_y
                    self.selected_component.update_connection_points()
                    
                    #Salva estado apenas se houve movimento significativo
                    if abs(old_x - self.selected_component.x) > 10 or abs(old_y - self.selected_component.y) > 10:
                        self.save_state("Move component")
                else:
                    #Posição inválida - tenta encontrar posição próxima válida
                    valid_x, valid_y = self.find_valid_position(self.selected_component, new_x, new_y)
                    
                    #Se a posição válida encontrada está relativamente próxima, usa ela
                    distance_to_valid = math.sqrt((valid_x - new_x)**2 + (valid_y - new_y)**2)
                    if distance_to_valid < 50:  #Threshold de proximidade
                        self.selected_component.x = valid_x
                        self.selected_component.y = valid_y
                        self.selected_component.update_connection_points()
                        
                        if abs(old_x - self.selected_component.x) > 10 or abs(old_y - self.selected_component.y) > 10:
                            self.save_state("Move component")
                    #Senão, mantém na posição anterior (não move)
    
    def _tick(self): #Loop principal de renderização.
        if not self.running:
            try:
                pygame.quit()
            except pygame.error:
                logger.debug("Pygame ja estava finalizado", exc_info=True)
            return

        #Atualiza posição do componente fantasma
        if self.placing_component:
            self.update_ghost_component_position()

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
                    if pygame.mouse.get_pressed()[0] and not self.placing_component:  #Só arrasta se não está colocando
                        self.handle_mouse_drag(event.pos)

        #Movimento contínuo via teclado (desabilitado durante colocação)
        if not self.placing_component:
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
        
        #Desenha componentes (incluindo fantasma)
        for component in self.components:
            if component == self.ghost_component:
                #Desenha componente fantasma com transparência
                self.drawer.draw_component(component)
                
                #Desenha indicador de colisão se houver
                if self.check_collision(component, component.x, component.y):
                    self.draw_collision_warning(component)
            else:
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
        
        #Desenha mensagem de sucesso se ativa
        if self.show_success_message and self.success_message_timer > 0:
            self.draw_success_message()
            self.success_message_timer -= 1
            if self.success_message_timer <= 0:
                self.show_success_message = False

        #Desenha mensagem de erro se ativa
        if self.show_error_message and self.error_message_timer > 0:
            self.draw_error_message()
            self.error_message_timer -= 1
            if self.error_message_timer <= 0:
                self.show_error_message = False

        pygame.display.flip()
        
        #Continua o loop se ainda estiver rodando
        if self.running:
            self.parent_frame.after(16, self._tick)
    
    def draw_collision_warning(self, component): #Desenha aviso visual de colisão.
        #Desenha X vermelho no centro se houver colisão
        center_x = component.x + component.width // 2
        center_y = component.y + component.height // 2
        
        #Converte para coordenadas de tela
        screen_center = self.camera.world_to_screen((center_x, center_y))
        
        #Desenha X
        size = 15
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (screen_center[0] - size, screen_center[1] - size),
                        (screen_center[0] + size, screen_center[1] + size), 3)
        pygame.draw.line(self.screen, (255, 0, 0),
                        (screen_center[0] + size, screen_center[1] - size), 
                        (screen_center[0] - size, screen_center[1] + size), 3)
            
    def _on_pygame_mouse_enter(self):
        if self.scroll_control_callback:
            self.scroll_control_callback(False)  # Desabilita scroll externo
    
    def _on_pygame_mouse_leave(self):
        if self.scroll_control_callback:
            self.scroll_control_callback(True)  # Habilita scroll externo
    
    def stop(self):
        self.running = False
        if self._resize_after_id:
            try:
                self.parent_frame.after_cancel(self._resize_after_id)
            except (tk.TclError, ValueError):
                pass
            self._resize_after_id = None
        if self._configure_binding_id:
            try:
                self.parent_frame.unbind("<Configure>", self._configure_binding_id)
            except tk.TclError:
                pass
            self._configure_binding_id = None
        logger.info("Circuito Pygame interativo parado")
    
    def test_circuit_manual(self): #Testa o circuito manualmente quando o usuário pressiona ESPAÇO.
        logger.info("Testando circuito manualmente")
        
        try:
            is_correct = self.is_circuit_correct()
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_circuit_test(is_correct)

            if is_correct:
                self.show_success_message = True
                self.success_message_timer = 300
                self.show_error_message = False
                logger.info("Circuito validado com sucesso")
            else:
                self.show_error_message = True
                self.error_message_timer = 300
                self.show_success_message = False
                logger.warning("Circuito validado como incorreto")
                
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_error("interactive_circuit_exception", str(e), "circuit_test")

            self.show_error_message = True
            self.error_message_timer = 300
            self.error_message_text = f"Erro na validação: {str(e)}"
            self.show_success_message = False
            logger.exception("Erro ao testar circuito")
            
    def check_circuit_completion(self):
        #Removido - agora só testamos manualmente - continua aqui para compatibilidade
        pass

    def is_circuit_correct(self): #Verifica se o circuito implementa a expressão através de simulação com tabela verdade.
        try:
            #Extrai variáveis da expressão
            variables = self.extract_variables(self.expressao)
            
            #Encontra componente de saída
            output_component = self.find_output_component()
            if not output_component:
                logger.warning("Componente de saida ausente ou desconectado")
                return False
            
            is_minimal_mode = False
            if hasattr(self, 'mode_key'):
                is_minimal_mode = (self.mode_key == 'minimal')
            
            #VALIDAÇÃO CRÍTICA: Verifica se TODAS as variáveis da expressão estão sendo usadas
            if not is_minimal_mode:
                if not self.all_variables_connected(variables, output_component):
                    logger.warning("Nem todas as variaveis estao conectadas ao circuito")
                    return False
                
                #Verifica se o circuito tem pelo menos uma porta lógica
                if not self.has_logic_gates_connected():
                    logger.warning("Circuito nao possui portas logicas conectadas")
                    return False
                
            else: #MODO MINIMAL
                connected_variables = set()
                visited = set()
                self._collect_connected_variables(output_component, visited, connected_variables)
                
                if len(connected_variables) == 0:
                    logger.warning("Nenhuma variavel esta conectada ao circuito")
                    return False
                
                logger.info(
                    "Modo Minimal: %s de %s variaveis conectadas (%s)",
                    len(connected_variables),
                    len(variables),
                    connected_variables,
                )
            
            #Simula todas as combinações possíveis
            return self.validate_truth_table(variables, output_component)
            
        except Exception:
            logger.exception("Erro na validacao estrutural do circuito")
            return False
        
    def all_variables_connected(self, required_variables, output_component): #Verifica se TODAS as variáveis da expressão estão conectadas no caminho até a saída.
        connected_variables = set()
        visited = set()
        
        self._collect_connected_variables(output_component, visited, connected_variables)
        
        #Converte para sets para comparação
        required_set = set(required_variables)
        connected_set = connected_variables
        
        logger.debug("Variaveis necessarias: %s", required_set)
        logger.debug("Variaveis conectadas: %s", connected_set)
        
        #Verifica se todas as variáveis necessárias estão conectadas
        missing_variables = required_set - connected_set
        if missing_variables:
            logger.warning("Variaveis nao conectadas: %s", missing_variables)
            return False
        
        return True
    
    def has_logic_gates_connected(self): #Verifica se o circuito tem pelo menos uma porta lógica conectada ao caminho da saída.
        output_component = None
        for comp in self.components:
            if comp.type == 'output':
                output_component = comp
                break
        
        if not output_component or len(output_component.input_connections) == 0:
            return False
        
        #Verifica se há pelo menos uma porta lógica no caminho até a saída
        visited = set()
        return self._has_logic_gate_in_path(output_component, visited)

    def _has_logic_gate_in_path(self, component, visited): #Recursivamente verifica se há portas lógicas no caminho até as variáveis.
        if component in visited:
            return False
        
        visited.add(component)
        
        #Se é uma porta lógica, encontrou o que procura
        if component.type in ['and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor']:
            return True
        
        #Se é uma variável, chegou ao fim sem encontrar porta lógica
        if component.type == 'variable':
            return False
        
        #Para outros tipos (output), verifica as conexões de entrada
        for input_idx, wire in component.input_connections.items():
            if self._has_logic_gate_in_path(wire.start_comp, visited):
                return True
        
        return False
    
    def _collect_connected_variables(self, component, visited, connected_variables): #Recursivamente coleta todas as variáveis conectadas no caminho.
        if component in visited:
            return
        
        visited.add(component)
        
        #Se é uma variável, adiciona ao conjunto
        if component.type == 'variable':
            connected_variables.add(component.name)
            return
        
        #Para outros tipos, verifica as conexões de entrada
        for input_idx, wire in component.input_connections.items():
            self._collect_connected_variables(wire.start_comp, visited, connected_variables)
                
    def find_output_component(self): #Encontra e valida o componente de saída
        output_component = None
        for comp in self.components:
            if comp.type == 'output':
                output_component = comp
                break
        
        #Verifica se a saída tem exatamente uma conexão
        if not output_component or len(output_component.input_connections) != 1:
            return None
        
        return output_component

    def validate_truth_table(self, variables, output_component): #Valida o circuito comparando com a expressão original
        import itertools
        
        total_combinations = 2 ** len(variables)
        correct_results = 0
        failed_combinations = []
        
        logger.debug("Testando %s combinacoes do circuito", total_combinations)
        
        for combination in itertools.product([False, True], repeat=len(variables)):
            var_values = dict(zip(variables, combination))
            
            #Resultado esperado da expressão
            expected = self.evaluate_expression(self.expressao, var_values)
            
            #Resultado do circuito
            actual = self.simulate_circuit_simple(var_values)
            
            #Se não conseguiu simular o circuito, é erro
            if actual is None:
                logger.warning("Nao foi possivel simular o circuito para %s", var_values)
                return False
            
            if expected == actual:
                correct_results += 1
            else:
                failed_combinations.append({
                    'inputs': var_values,
                    'expected': expected,
                    'actual': actual
                })
        
        #Se houve falhas, mostra detalhes
        if failed_combinations:
            logger.warning("%s combinacoes incorretas", len(failed_combinations))
            for fail in failed_combinations[:3]:  #Mostra só as 3 primeiras
                logger.debug(
                    "Falha %s: esperado=%s obtido=%s",
                    fail['inputs'],
                    fail['expected'],
                    fail['actual'],
                )
            if len(failed_combinations) > 3:
                logger.debug("Mais %s falhas omitidas", len(failed_combinations) - 3)
            return False
        
        success_rate = (correct_results / total_combinations) * 100
        logger.info(
            "Todas as %s combinacoes corretas (%.1f%%)",
            total_combinations,
            success_rate,
        )
        
        return True

    def evaluate_expression(self, expression, var_values): #Avalia a expressão booleana com os valores fornecidos
        try:
            safe_expression = (
                expression.upper()
                .replace("*", "&")
                .replace("+", "|")
                .replace("~", "!")
            )
            return bool(
                UniversalLogicAnalyzer().analyze_expression(safe_expression, var_values)
            )
        except Exception:
            logger.exception("Erro ao avaliar expressao do circuito")
            return False

    def simulate_circuit_simple(self, var_values): #Simulação simplificada do circuito.
        component_outputs = {}
        
        #Define valores das variáveis de entrada
        variables_set = False
        for comp in self.components:
            if comp.type == 'variable' and comp.name in var_values:
                component_outputs[comp] = var_values[comp.name]
                variables_set = True
        
        if not variables_set:
            logger.warning("Nenhuma variavel foi definida no circuito")
            return None
        
        #Propaga valores através do circuito (máximo 15 iterações)
        for iteration in range(15):
            changes_made = False
            
            for comp in self.components:
                #Pula se já tem valor calculado
                if comp in component_outputs:
                    continue
                    
                #Verifica se é uma porta lógica ou saída
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
        
        #Se chegou aqui, não conseguiu simular completamente
        logger.warning("Simulacao incompleta; circuito pode estar desconectado")
        return None


    def get_component_inputs(self, component, component_outputs): #Obtém valores de entrada de um componente
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
                logger.warning("%s entrada %s nao conectada", component.type, input_idx)
                return None  #Entrada não conectada
        
        return input_values

    def get_expected_input_count(self, gate_type): #Retorna o número esperado de entradas para cada tipo de porta.
        input_counts = {
            'and': 2, 'or': 2, 'not': 1, 'nand': 2, 
            'nor': 2, 'xor': 2, 'xnor': 2, 'output': 1
        }
        return input_counts.get(gate_type, 0)

    def calculate_gate_output_simple(self, gate_type, inputs): #Calcula saída da porta lógica - versão simplificada
        if not inputs and gate_type != 'not':
            return False
        
        try:
            if gate_type == 'and':
                return all(inputs)
            elif gate_type == 'or':
                return any(inputs)
            elif gate_type == 'not':
                return not inputs[0] if len(inputs) >= 1 else True
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
        except Exception:
            logger.exception("Erro ao calcular saida da porta %s", gate_type)
            return None

    
    def draw_success_message(self): #Desenha mensagem de parabéns quando o circuito está correto
        if not self.font:
            return
        
        #Fundo semi-transparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 50, 0))  #Verde escuro
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        #Mensagem principal
        messages = [
            "🎉 PARABÉNS! 🎉",
            "Circuito montado corretamente!",
            f"Expressão: {self.expressao}",
            ""
        ]
        
        if self.gate_restrictions:
            messages.insert(-2, f"Usando apenas: {', '.join(self.gate_restrictions).upper()}")
        
        start_y = self.screen_height // 2 - 120
        for i, message in enumerate(messages):
            if message.startswith("🎉"):
                color = (255, 255, 0)  #Amarelo
                font_size = 48
            elif message.startswith("Circuito"):
                color = (0, 255, 0)   #Verde
                font_size = 36
            elif message.startswith("Expressão") or message.startswith("Usando"):
                color = (255, 255, 255)  #Branco
                font_size = 24
            elif message.startswith("Pressione"):
                color = (200, 200, 200)  #Cinza claro
                font_size = 18
            else:
                color = (200, 200, 200)  #Cinza claro
                font_size = 20
            
            try:
                font = pygame.font.Font(None, font_size)
                surface = font.render(message, True, color)
                rect = surface.get_rect(center=(self.screen_width//2, start_y + i * 40))
                self.screen.blit(surface, rect)
            except pygame.error:
                logger.debug("Falha ao desenhar mensagem de sucesso", exc_info=True)

    def draw_error_message(self): #Desenha mensagem de erro quando o circuito está incorreto
        if not self.font:
            return
        
        #Fundo semi-transparente vermelho
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((50, 0, 0))  #Vermelho escuro
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        #Mensagem principal
        messages = [
            "❌ CIRCUITO INCORRETO ❌",
            "Tente novamente!",
            "",
            "Possíveis problemas:",
            "• Verifique todas as conexões",
            "• Confira se implementou a expressão correta",
            "• Todas as variáveis devem estar conectadas",
            "• O circuito deve ter pelo menos uma porta lógica",
            ""
        ]
        
        start_y = self.screen_height // 2 - 160
        for i, message in enumerate(messages):
            if message.startswith("❌"):
                color = (255, 100, 100)  #Vermelho claro
                font_size = 42
            elif message.startswith("Tente"):
                color = (255, 150, 150)   #Rosa
                font_size = 32
            elif message.startswith("Possíveis"):
                color = (255, 255, 255)  #Branco
                font_size = 24
            elif message.startswith("•"):
                color = (255, 200, 200)  #Rosa claro
                font_size = 18
            elif message.startswith("Pressione"):
                color = (200, 200, 200)  #Cinza
                font_size = 18
            else:
                color = (200, 200, 200)  #Cinza
                font_size = 18
            
            try:
                font = pygame.font.Font(None, font_size)
                surface = font.render(message, True, color)
                rect = surface.get_rect(center=(self.screen_width//2, start_y + i * 30))
                self.screen.blit(surface, rect)
            except pygame.error:
                logger.debug("Falha ao desenhar mensagem de erro", exc_info=True)
