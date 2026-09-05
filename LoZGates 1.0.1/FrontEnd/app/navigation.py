import logging

logger = logging.getLogger(__name__)

CIRCUIT_TAB = "      Circuito      "
INTERACTIVE_CIRCUIT_TAB = "  Circuito Interativo  "
EXPRESSION_TAB = "      Expressão      "

class NavigationController:
    """
    Controlador central de navegação entre telas do aplicativo.
    Responsável por mostrar uma tela, esconder a atual, e fornecer uma forma simples de voltar.
    Também gerencia a navegação por abas.
    """
    def __init__(self, tab_frame=None, tabview=None, frame_names=None):
        self.screens = {}
        self.history = []
        self.current_screen_name = None
        self.current_screen_frame = None

        self.tab_frame = tab_frame
        self.tabview = tabview
        self.frame_names = frame_names or {}
        self.tabs = {
            "circuit": CIRCUIT_TAB,
            "interactive_circuit": INTERACTIVE_CIRCUIT_TAB,
            "expression": EXPRESSION_TAB,
        }

    def register_screen(self, name, frame):
        """Registra uma tela no controlador de navegação."""
        self.screens[name] = frame

    def show_screen(self, name):
        """
        Esconde a tela atual, guarda no histórico e exibe a nova tela.
        """
        if name not in self.screens:
            logger.error(f"Tela '{name}' não registrada.")
            return

        # Se já estamos na tela, não faz nada
        if self.current_screen_name == name:
            return

        # Mostra a nova
        self.current_screen_name = name
        self.current_screen_frame = self.screens[name]
        
        # Como o LoZGates original empilha as telas no mesmo grid e usa tkraise(),
        # preservamos esse comportamento para não quebrar as telas não-migradas.
        self.current_screen_frame.tkraise()
        
        # Adiciona ao histórico, se não for o último
        if not self.history or self.history[-1] != name:
            self.history.append(name)
            
        logger.debug(f"Navegou para: {name}")

    def go_back(self):
        """Retorna para a tela anterior do histórico."""
        if len(self.history) > 1:
            self.history.pop()
            prev_name = self.history[-1]
            
            self.current_screen_name = prev_name
            self.current_screen_frame = self.screens[prev_name]
            self.current_screen_frame.tkraise()
            
            logger.debug(f"Voltou para: {prev_name}")
        else:
            logger.warning("Histórico vazio, não é possível voltar mais.")

    def show_frame(self, frame, view_name=None):
        """Método compatível com a interface antiga"""
        frame.tkraise()
        if self.tab_frame and frame is self.tab_frame and self.current_screen_name in self.tabs:
            return self.current_screen_name
        self.current_screen_name = view_name or self.frame_names.get(frame, "frame")
        return self.current_screen_name

    def show_tab(self, view_name):
        """Método compatível com a interface antiga"""
        if view_name not in self.tabs:
            raise ValueError(f"Aba desconhecida: {view_name}")
        if self.tab_frame:
            self.tab_frame.tkraise()
        if self.tabview:
            self.tabview.set(self.tabs[view_name])
        self.current_screen_name = view_name
        return self.current_screen_name

    def sync_tab(self, tab_label):
        """Método compatível com a interface antiga"""
        for view_name, label in self.tabs.items():
            if tab_label == label:
                self.current_screen_name = view_name
                return view_name
        return self.current_screen_name
