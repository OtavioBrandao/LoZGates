import customtkinter as ctk
import tkinter as tk
import logging
from config import apply_window_icon

from FrontEnd.styles.design_tokens import Colors
from FrontEnd.utils.responsive import calculate_window_layout
from FrontEnd.app.navigation import NavigationController

from FrontEnd.dialogs.data_sharing_dialog import DetailedDataSharingDialog
from FrontEnd.services.google_forms_service import ImprovedGoogleFormsSubmitter
from FrontEnd.services.logging_service import DetailedUserLogger

logger = logging.getLogger(__name__)

class LOZGatesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("LoZ Gates")
        self.configure(bg=Colors.PRIMARY_BG)
        
        window_layout = calculate_window_layout(
            self.winfo_screenwidth(), self.winfo_screenheight()
        )
        self.geometry(window_layout.geometry)
        self.minsize(window_layout.minimum_width, window_layout.minimum_height)
        
        try:
            self.state('zoomed')
        except (tk.TclError, AttributeError):
            logger.debug("Maximizacao automatica indisponivel nesta plataforma")
            
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        apply_window_icon(self)
        self.resizable(True, True)
        
        self.user_logger = DetailedUserLogger("1.0-beta")
        self.navigation = NavigationController()
        
    def setup_screens(self, legacy_setup_func):
        """
        Delega a configuração das telas legadas.
        Isto permite injetar todo o código antigo sem quebrar o app.
        """
        legacy_setup_func(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # A inicialização inicial realimenta o 'navigation', depois exibimos a home
        self.navigation.show_screen("home")

    def on_closing(self):
        self.user_logger.end_session()
        
        if self.user_logger.should_prompt_data_sharing():
            try:
                dialog = DetailedDataSharingDialog(self.user_logger)
                result = dialog.show_dialog()
                
                if result == True:
                    logger.info("Usuario autorizou o envio dos dados detalhados")
                    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd9QNzL1_1MpD0cy_PUA4b59Kpy998015HIsfIT60VC6nOHZA/formResponse"
                    ENTRY_MAPPING = {
                        'app_version': 'entry.695751574',
                        'platform': 'entry.2115172041',
                        'submission_date': 'entry.1953189469',
                        'summary_json': 'entry.415910834'
                    }
                    submitter = ImprovedGoogleFormsSubmitter(FORM_URL, ENTRY_MAPPING)
                    data_to_send = DetailedUserLogger.create_formatted_shareable_data(self.user_logger)
                    success = submitter.submit_data(data_to_send)
                    if success:
                        self.user_logger._save_settings() 
                    else:
                        logger.warning("O envio de dados de atividade falhou")
                elif result == "never":
                    self.user_logger.logging_enabled = False
                    self.user_logger._save_settings()
            except Exception:
                logger.exception("Erro no dialogo de compartilhamento")
        
        self.destroy()
