import logging

logger = logging.getLogger(__name__)

class NavigationController:
    """
    Controlador central de navegação entre telas do aplicativo.
    Responsável por mostrar uma tela, esconder a atual, e fornecer uma forma simples de voltar.
    """
    def __init__(self):
        self.screens = {}
        self.history = []
        self.current_screen_name = None
        self.current_screen_frame = None

    def register_screen(self, name, frame):
        """Registra uma tela no controlador de navegação."""
        self.screens[name] = frame

    def show_screen(self, name):
        """
        Esconde a tela atual, guarda no histórico e exibe a nova tela.
        Assume que as telas (frames) foram criadas para preencher o container pai.
        """
        if name not in self.screens:
            logger.error(f"Tela '{name}' não registrada.")
            return

        # Se já estamos na tela, não faz nada
        if self.current_screen_name == name:
            return

        # Esconde a atual
        if self.current_screen_frame:
            # Em tkinter, pack_forget ou grid_forget pode ser usado. 
            # A maioria das telas do LoZGates usa grid no root.
            self.current_screen_frame.grid_forget()
            try:
                self.current_screen_frame.pack_forget()
            except Exception:
                pass

        # Mostra a nova
        self.current_screen_name = name
        self.current_screen_frame = self.screens[name]
        
        # Tenta usar grid, fallback para pack (depende da implementação específica)
        self.current_screen_frame.grid(row=0, column=0, sticky="nsew")
        
        # Adiciona ao histórico, se não for o último
        if not self.history or self.history[-1] != name:
            self.history.append(name)
            
        logger.debug(f"Navegou para: {name}")

    def go_back(self):
        """Retorna para a tela anterior do histórico."""
        if len(self.history) > 1:
            # Remove a atual
            self.history.pop()
            prev_name = self.history[-1]
            
            if self.current_screen_frame:
                self.current_screen_frame.grid_forget()
                try:
                    self.current_screen_frame.pack_forget()
                except Exception:
                    pass
                
            self.current_screen_name = prev_name
            self.current_screen_frame = self.screens[prev_name]
            self.current_screen_frame.grid(row=0, column=0, sticky="nsew")
            
            logger.debug(f"Voltou para: {prev_name}")
        else:
            logger.warning("Histórico vazio, não é possível voltar mais.")
