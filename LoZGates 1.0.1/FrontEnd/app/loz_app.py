import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)

class LOZGatesApp:
    """
    Classe base da aplicação LOZGates.
    Esta classe será o novo ponto de entrada para o FrontEnd,
    substituindo o antigo 'interface.py' gradualmente.
    """
    def __init__(self):
        # Configurações iniciais
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.janela = ctk.CTk()
        self.janela.title("LOZGates")
        self.janela.geometry("1100x650")
        self.janela.minsize(800, 500)
        
        # O container principal onde as telas serão injetadas
        self.main_container = ctk.CTkFrame(self.janela, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both")
        
        # A navegação (inserida na etapa posterior)
        # self.navigation = NavigationController()

    def run(self):
        """Inicia o loop principal do Tkinter."""
        logger.info("LOZGates UI iniciada (Base class).")
        self.janela.mainloop()
