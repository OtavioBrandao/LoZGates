"""Single source of truth for top-level frames and tab selection."""

CIRCUIT_TAB = "      Circuito      "
INTERACTIVE_CIRCUIT_TAB = "  Circuito Interativo  "
EXPRESSION_TAB = "      Expressão      "


class NavigationController:
    def __init__(self, tab_frame, tabview, frame_names=None):
        self.tab_frame = tab_frame
        self.tabview = tabview
        self.frame_names = frame_names or {}
        self.tabs = {
            "circuit": CIRCUIT_TAB,
            "interactive_circuit": INTERACTIVE_CIRCUIT_TAB,
            "expression": EXPRESSION_TAB,
        }
        self.current_view = None

    def show_frame(self, frame, view_name=None):
        frame.tkraise()
        if frame is self.tab_frame and self.current_view in self.tabs:
            return self.current_view
        self.current_view = view_name or self.frame_names.get(frame, "frame")
        return self.current_view

    def show_tab(self, view_name):
        if view_name not in self.tabs:
            raise ValueError(f"Aba desconhecida: {view_name}")
        self.tab_frame.tkraise()
        self.tabview.set(self.tabs[view_name])
        self.current_view = view_name
        return self.current_view

    def sync_tab(self, tab_label):
        for view_name, label in self.tabs.items():
            if tab_label == label:
                self.current_view = view_name
                return view_name
        return self.current_view
