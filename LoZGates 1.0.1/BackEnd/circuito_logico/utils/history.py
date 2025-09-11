"""
Módulo para gerenciamento de histórico de ações no circuito interativo.
Implementa funcionalidades de undo/redo com serialização de estados.
"""

import copy

class CircuitHistory:
    """Gerencia o histórico de estados do circuito para undo/redo."""
    
    def __init__(self, max_history=50):
        self.history = []  # Lista de estados
        self.current_index = -1  # Índice do estado atual
        self.max_history = max_history
        self.components_ref = None
    
    def save_state(self, components, wires):
        """Salva o estado atual do circuito."""
        # Remove estados futuros se estivermos no meio do histórico
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Cria uma cópia profunda do estado
        state = {
            'components': self._serialize_components(components),
            'wires': self._serialize_wires(wires, components)
        }
        
        self.history.append(state)
        self.current_index += 1
        
        # Limita o tamanho do histórico
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def can_undo(self):
        """Verifica se é possível fazer undo."""
        return self.current_index > 0
    
    def can_redo(self):
        """Verifica se é possível fazer redo."""
        return self.current_index < len(self.history) - 1
    
    def undo(self):
        """Retorna ao estado anterior."""
        if self.can_undo():
            self.current_index -= 1
            return self._deserialize_state(self.history[self.current_index])
        return None
    
    def redo(self):
        """Avança para o próximo estado."""
        if self.can_redo():
            self.current_index += 1
            return self._deserialize_state(self.history[self.current_index])
        return None
    
    def _serialize_components(self, components):
        """Serializa componentes para salvar no histórico."""
        serialized = []
        for comp in components:
            comp_data = {
                'x': comp.x,
                'y': comp.y,
                'type': comp.type,
                'name': comp.name,
                'width': comp.width,
                'height': comp.height,
                'selected': comp.selected
            }
            serialized.append(comp_data)
        return serialized
    
    def _serialize_wires(self, wires, components):
        """Serializa fios para salvar no histórico."""
        serialized = []
        for wire in wires:
            # Encontra os índices dos componentes
            start_comp_index = -1
            end_comp_index = -1
            
            for i, comp in enumerate(components):
                if comp == wire.start_comp:
                    start_comp_index = i
                elif comp == wire.end_comp:
                    end_comp_index = i
            
            if start_comp_index >= 0 and end_comp_index >= 0:
                wire_data = {
                    'start_comp_index': start_comp_index,
                    'start_output': wire.start_output,
                    'end_comp_index': end_comp_index,
                    'end_input': wire.end_input,
                    'selected': wire.selected
                }
                serialized.append(wire_data)
        return serialized
    
    def _deserialize_state(self, state):
        """Deserializa estado do histórico."""
        return {
            'components': state['components'],
            'wires': state['wires']
        }
    
    def set_components_reference(self, components):
        """Define referência aos componentes para serialização de wires."""
        self.components_ref = components