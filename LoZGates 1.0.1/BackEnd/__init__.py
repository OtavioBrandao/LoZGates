# BackEnd/circuito_logico/__init__.py
"""
Módulo de circuitos lógicos para LoZ Gates.
Fornece funcionalidades para visualização e criação interativa de circuitos.
"""

from .principal import (
    plotar_circuito_logico,
    criar_circuito_integrado,
    criar_circuito_estatico,
    ver_circuito_pygame
)

__all__ = [
    'plotar_circuito_logico',
    'criar_circuito_integrado', 
    'criar_circuito_estatico',
    'ver_circuito_pygame'
]

# BackEnd/circuito_logico/core/__init__.py
"""Módulo principal com estruturas de dados fundamentais."""

from BackEnd.circuito_logico.core.nodes import Node, VariableNode, OperatorNode

__all__ = ['Node', 'VariableNode', 'OperatorNode']

# BackEnd/circuito_logico/rendering/__init__.py
"""Módulo de renderização para circuitos lógicos."""

from BackEnd.circuito_logico.rendering.camera import Camera
from BackEnd.circuito_logico.rendering.drawer import CircuitDrawer
from BackEnd.circuito_logico.rendering.circuit_renderer import desenhar_circuito_logico_base, draw_ui_info

__all__ = ['Camera', 'CircuitDrawer', 'desenhar_circuito_logico_base', 'draw_ui_info']

# BackEnd/circuito_logico/interactive/__init__.py
"""Módulo para componentes e funcionalidades interativas."""

from BackEnd.circuito_logico.interactive.components import Component, Wire
from BackEnd.circuito_logico.interactive.interactive_circuit import CircuitoInterativoManual

__all__ = ['Component', 'Wire', 'CircuitoInterativoManual']

# BackEnd/circuito_logico/logic/__init__.py
"""Módulo para parsing e análise de expressões lógicas."""

from BackEnd.circuito_logico.logic.parser import (
    criar_ast_de_expressao,
    calcular_layout_dinamico,
    _coletar_variaveis,
    _coletar_operadores
)

__all__ = [
    'criar_ast_de_expressao',
    'calcular_layout_dinamico', 
    '_coletar_variaveis',
    '_coletar_operadores'
]

# BackEnd/circuito_logico/static/__init__.py
"""Módulo para visualização estática de circuitos."""

from BackEnd.circuito_logico.static.static_circuit import CircuitoInterativo

__all__ = ['CircuitoInterativo']

# BackEnd/circuito_logico/utils/__init__.py
"""Módulo de utilitários."""

from BackEnd.circuito_logico.utils.history import CircuitHistory

__all__ = ['CircuitHistory']