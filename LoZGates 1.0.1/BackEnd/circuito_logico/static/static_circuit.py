#Módulo para o circuito estático (visualização automática) onde o circuito é gerado automaticamente baseado na expressão lógica fornecida.

import pygame
import tkinter as tk
import os

from ..rendering.camera import Camera
from ..rendering.drawer import CircuitDrawer
from ..rendering.circuit_renderer import desenhar_circuito_logico_base, draw_ui_info

class CircuitoInterativo:
    def __init__(self, parent_frame, expressao):
        self.parent_frame = parent_frame
        self.expressao = expressao
        self.running = False
        self.pygame_thread = None
        self.info_label = None
        self.status_label = None
        
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
            self.parent_frame.configure(bg="black", highlightthickness=0)
            self.parent_frame.focus_set()
            self.parent_frame.bind("<Enter>", lambda e: self.parent_frame.focus_set())
            self.parent_frame.bind("<KeyPress>", self._on_key_press)
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
            self.camera.handle_event(event)

        # Movimento contínuo via teclado
        if self._move['up']:    self.camera.move(0, -self.camera.move_speed)
        if self._move['down']:  self.camera.move(0,  self.camera.move_speed)
        if self._move['left']:  self.camera.move(-self.camera.move_speed, 0)
        if self._move['right']: self.camera.move( self.camera.move_speed, 0)

        # Desenha frame
        self.screen.fill(self.drawer.BACKGROUND)
        
        # Desenha o circuito automático
        desenhar_circuito_logico_base(self.expressao, self.drawer, self.screen_width, self.screen_height)
        
        # Desenha informações de controle
        if self.font:
            draw_ui_info(self.screen, self.camera, self.font)

        pygame.display.flip()
        self.parent_frame.after(16, self._tick)

    def stop(self):
        self.running = False