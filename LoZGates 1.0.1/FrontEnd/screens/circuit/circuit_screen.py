import customtkinter as ctk
import logging

from FrontEnd.styles.design_tokens import Colors
from FrontEnd.components.buttons import Button

logger = logging.getLogger(__name__)

class CircuitScreen(ctk.CTkFrame):
    def __init__(self, parent, navigation_controller, controller, get_global_expression_cb):
        super().__init__(parent, fg_color=Colors.PRIMARY_BG)
        
        self.navigation = navigation_controller
        self.controller = controller
        self.get_global_expression_cb = get_global_expression_cb
        self.is_initialized = False
        
        self.grid(row=0, column=0, sticky="nsew")

    def initialize_if_needed(self):
        # Garante que a expressão existe antes de criar o circuito
        expressao = self.get_global_expression_cb()
        if not expressao:
            logger.warning("Nenhuma expressao disponivel para criar circuito")
            return
            
        if not self.is_initialized or not self.controller.mode_selector_instance:
            self.controller.start_interaction()
            self.controller.initialize_circuit(self, Button, self.get_global_expression_cb)
            self.is_initialized = True
        else:
            self.controller.update_expression_display()

    def cleanup(self):
        self.controller.cleanup()
        self.is_initialized = False
