#Módulo para gerenciamento da câmera/viewport do circuito lógico, incluindo zoom, pan e conversões de coordenadas.

import pygame

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
        self.x = 0
        self.y = 0
        self.zoom = 1.0
    
    def handle_event(self, event, interactive_mode=False):
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