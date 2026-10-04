"""
Modos de desafio do circuito interativo (dados puros, sem interface).

Mesmo conteúdo do CircuitModeManager do interface_update: nomes, descrições,
portas permitidas, cores, ícones, dificuldade e dicas de cada modo.
"""
from typing import Any, Dict, List, Optional

MODOS: Dict[str, Dict[str, Any]] = {
    'livre': {
        'name': 'Modo Livre',
        'description': 'Use qualquer tipo de porta lógica',
        'restrictions': None,
        'color': '#4441F7',
        'icon': '🆓',
        'difficulty': 'Iniciante'
    },
    'basic_gates': {
        'name': 'Portas Básicas',
        'description': 'Use apenas AND, OR, NOT',
        'restrictions': ['and', 'or', 'not'],
        'color': '#4A597C',
        'icon': '📚',
        'difficulty': 'Iniciante'
    },
    'nand_only': {
        'name': 'Desafio NAND',
        'description': 'Implemente usando apenas portas NAND',
        'restrictions': ['nand'],
        'color': '#7A2020',
        'icon': '🎯',
        'difficulty': 'Intermediário'
    },
    'nor_only': {
        'name': 'Desafio NOR',
        'description': 'Implemente usando apenas portas NOR',
        'restrictions': ['nor'],
        'color': '#2D5A27',
        'icon': '🔥',
        'difficulty': 'Intermediário'
    },
    'advanced_gates': {
        'name': 'Portas Avançadas',
        'description': 'Use XOR e XNOR',
        'restrictions': ['xor', 'xnor'],
        'color': '#8B4513',
        'icon': '⚡',
        'difficulty': 'Avançado'
    },
    'minimal': {
        'name': 'Desafio Mínimo',
        'description': 'Use o menor número possível de portas',
        'restrictions': None,
        'color': '#800080',
        'icon': '🏆',
        'difficulty': 'Expert'
    }
}

DICAS: Dict[str, List[str]] = {
    'livre': [
        "Experimente diferentes combinações de portas"
    ],
    'nand_only': [
        "OR pode ser implementado usando as leis de De Morgan",
        "Pense em como ~(A*B) = ~A + ~B"
    ],
    'nor_only': [
        "AND pode ser implementado usando as leis de De Morgan",
        "Pense em como ~(A+B) = ~A * ~B"
    ],
    'basic_gates': [
        "Foque na clareza da implementação",
        "Use as leis básicas: distributiva, associativa, comutativa",
        "Minimize o uso desnecessário de NOTs"
    ],
    'advanced_gates': [
        "XOR é útil para funções de paridade",
        "XNOR é o complemento do XOR"
    ],
    'minimal': [
        "Aplique simplificações algébricas primeiro",
        "Considere usar portas que implementem múltiplas funções"
    ]
}

DICA_SEM_MODO = ["Selecione um modo primeiro para ver dicas específicas."]


def info_do_modo(chave: str) -> Dict[str, Any]:
    """Como get_mode_info: modo desconhecido cai no Modo Livre."""
    return MODOS.get(chave, MODOS['livre'])


def dicas_do_modo(chave: Optional[str]) -> List[str]:
    if chave is None:
        return list(DICA_SEM_MODO)
    return list(DICAS.get(chave, DICAS['livre']))


def portas_permitidas(chave: str) -> Optional[List[str]]:
    """Tipos de porta liberados no modo, ou None se todos forem."""
    return info_do_modo(chave)['restrictions']
