import logging
import customtkinter as ctk

from FrontEnd.circuit_mode_interface import CircuitModeSelector
from BackEnd.circuito_logico.circuit_mode_selector import CircuitModeManager

logger = logging.getLogger(__name__)

class CircuitController:
    def __init__(self, user_logger):
        self.user_logger = user_logger
        self.mode_selector_instance = None
        self.does_it_have_interaction = False

    def initialize_circuit(self, parent_frame, button_class, get_global_expression_cb):
        if self.mode_selector_instance:
            try:
                self.mode_selector_instance.cleanup()
            except Exception:
                logger.exception("Erro ao limpar instancia anterior do circuito")
                
        for widget in parent_frame.winfo_children():
            widget.destroy()

        try:
            self.mode_selector_instance = CircuitModeSelector(
                parent_frame, 
                CircuitModeManager(),
                button_class,
                get_global_expression_cb,
                logger=self.user_logger 
            )
            self.does_it_have_interaction = False
            logger.info("Interface de circuito com modos criada (Controller)")
            
        except Exception as error:
            logger.exception("Erro ao criar interface de circuito")
            self.does_it_have_interaction = False
            
            error_label = ctk.CTkLabel(
                parent_frame,
                text=f"Erro ao criar circuito interativo: {error}",
                text_color="red"
            )
            error_label.pack(expand=True)
            
    def update_expression_display(self):
        if (self.mode_selector_instance and 
            hasattr(self.mode_selector_instance, 'update_expression_display')):
            self.mode_selector_instance.update_expression_display()

    def start_interaction(self):
        self.user_logger.log_circuit_interaction_start()

    def cleanup(self):
        if self.mode_selector_instance:
            try:
                self.mode_selector_instance.cleanup()
                self.mode_selector_instance = None
                self.does_it_have_interaction = False
                logger.info("Circuito interativo limpo (Controller)")
            except Exception:
                logger.exception("Erro ao limpar circuito interativo")
