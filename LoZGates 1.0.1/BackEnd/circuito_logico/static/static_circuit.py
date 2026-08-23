#Módulo para o circuito estático (visualização automática) onde o circuito é gerado automaticamente baseado na expressão lógica fornecida.

import pygame
import tkinter as tk
import logging

from ..rendering.camera import Camera
from ..rendering.drawer import CircuitDrawer
from ..rendering.circuit_renderer import desenhar_circuito_logico_base, draw_ui_info
from ..platform_support import configure_sdl_embedding, fit_surface_size


logger = logging.getLogger(__name__)

class CircuitoInterativo:
    def __init__(self, parent_frame, expressao):
        self.parent_frame = parent_frame
        self.expressao = expressao
        self.running = False
        self.pygame_thread = None
        self.info_label = None
        self.status_label = None
        self._resize_after_id = None
        self._configure_binding_id = None
        
        # Estado da interface
        self._move = {'up': False, 'down': False, 'left': False, 'right': False}
        
        # Inicialização
        self.parent_frame.after(100, self.init_pygame)

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
        logger.debug("Superficie Pygame estatica redimensionada para %sx%s", *new_size)
    
    def init_pygame(self):
        try:
            self.parent_frame.update_idletasks()
            if self.parent_frame.winfo_width() <= 1 or self.parent_frame.winfo_height() <= 1:
                self.parent_frame.after(200, self.init_pygame)
                return

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
            self.drawer = CircuitDrawer(self.screen, self.camera)

            try:
                self.font = pygame.font.Font(None, 24)
            except pygame.error:
                self.font = None

            # Configuração do frame Tkinter
            self.parent_frame.configure(bg="black", highlightthickness=0)
            self.parent_frame.focus_set()
            self.parent_frame.bind("<Enter>", lambda e: self.parent_frame.focus_set())
            self.parent_frame.bind("<KeyPress>", self._on_key_press)
            self.parent_frame.bind("<KeyRelease>", self._on_key_release)
            self._configure_binding_id = self.parent_frame.bind(
                "<Configure>", self._on_parent_configure, add="+"
            )

            self.running = True
            logger.info(
                "Pygame estatico inicializado em %sx%s",
                self.screen_width,
                self.screen_height,
            )
            self._tick()

        except Exception as e:
            logger.exception("Erro ao inicializar Pygame estatico")
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
            except pygame.error:
                logger.debug("Pygame ja estava finalizado", exc_info=True)
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
        logger.info("Circuito Pygame estatico parado")
