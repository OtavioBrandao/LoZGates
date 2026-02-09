#Módulo para gerenciar diferentes modos de circuito interativo.

import tkinter as tk
from typing import List, Optional, Dict, Any
from .interactive.interactive_circuit import CircuitoInterativoManual

class CircuitModeManager:
    MODES = {
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
    
    ''' NÃO TO USANDO ISSO POR ENQUANTO
    #Expressões sugeridas por dificuldade
    SUGGESTED_EXPRESSIONS = {
        'iniciante': [
            'A*B',
            'A+B', 
            '~A',
            'A*B + C',
            '~(A*B)'
        ],
        'intermediario': [
            'A*B + ~C',
            '(A+B)*C',
            '~A*B + A*~B',
            '(A*B) + (~A*~B)',
            'A*B + C*D'
        ],
        'avancado': [
            '(A*B) + (~C*D)',
            '~(A+B) * ~(C+D)',
            'A*B*C + ~A*~B*~C',
            '(A+B)*(C+D)*~E',
            'A*B + C*D + E*F'
        ]
    }'''
    
    def __init__(self):
        self.current_mode = None  #Inicializa como None
        self.current_circuit = None
        self.circuit_frame = None
        
    def get_mode_info(self, mode_key: str) -> Dict[str, Any]: #Retorna informações sobre um modo específico.
        return self.MODES.get(mode_key, self.MODES['livre'])
    
    def get_all_modes(self) -> Dict[str, Dict[str, Any]]: #Retorna todos os modos disponíveis.
        return self.MODES
    
    def set_mode(self, mode_key: str): #Define o modo atual.
        if mode_key in self.MODES:
            self.current_mode = mode_key
            print(f"Modo definido para: {mode_key}")
        else:
            print(f"Modo inválido: {mode_key}")
            self.current_mode = None
    
    def get_current_mode(self) -> str: #Retorna o modo atual.
        return self.current_mode
    
    def has_mode_selected(self) -> bool: #Verifica se um modo foi selecionado.
        return self.current_mode is not None
    
    ''' NÃO TO USANDO ISSO POR ENQUANTO
    def get_suggested_expressions(self, difficulty: str = None) -> List[str]:
        """Retorna expressões sugeridas baseadas na dificuldade."""
        if difficulty is None and self.current_mode:
            mode_info = self.get_mode_info(self.current_mode)
            difficulty = mode_info['difficulty'].lower()
        
        difficulty_map = {
            'iniciante': 'iniciante',
            'intermediário': 'intermediario',
            'avançado': 'avancado',
            'expert': 'avancado'  #Expert usa expressões avançadas
        }
        
        mapped_difficulty = difficulty_map.get(difficulty, 'iniciante')
        return self.SUGGESTED_EXPRESSIONS.get(mapped_difficulty, self.SUGGESTED_EXPRESSIONS['iniciante'])
    '''
    
    def create_circuit(self, parent_frame: tk.Widget, expression: str, logger=None) -> CircuitoInterativoManual: #Cria um circuito com as restrições do modo atual.
        #Para instância anterior se existir
        if self.current_circuit:
            try:
                self.current_circuit.stop()
                print("Circuito anterior parado")
            except Exception as e:
                print(f"Erro ao parar circuito anterior: {e}")
        
        #Limpa o frame
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        #Verifica se um modo foi selecionado
        if not self.has_mode_selected():
            raise ValueError("Nenhum modo foi selecionado. Selecione um modo antes de iniciar o circuito.")
        
        #Obtém restrições do modo atual
        mode_info = self.get_mode_info(self.current_mode)
        restrictions = mode_info['restrictions']
        
        print(f"Criando circuito no modo: {mode_info['name']}")
        if restrictions:
            print(f"Restrições ativas: {restrictions}")
        
        #Cria novo circuito
        try:
            self.current_circuit = CircuitoInterativoManual(
                parent_frame, 
                expression, 
                gate_restrictions=restrictions,
                logger=logger,
                mode_key = self.current_mode
            )
            self.circuit_frame = parent_frame
            print("Circuito criado com sucesso!")
            
            return self.current_circuit
            
        except Exception as e:
            print(f"Erro ao criar circuito: {e}")
            raise e
    
    def stop_current_circuit(self): #Para o circuito atual.
        if self.current_circuit:
            try:
                self.current_circuit.stop()
                print("Circuito parado com sucesso")
            except Exception as e:
                print(f"Erro ao parar circuito: {e}")
            finally:
                self.current_circuit = None
    
    def get_mode_tips(self, mode_key: str = None) -> List[str]: #Retorna dicas específicas para o modo.
        if mode_key is None:
            mode_key = self.current_mode
            
        if mode_key is None:
            return ["Selecione um modo primeiro para ver dicas específicas."]
        #MODIFICAR DICAS AQUI    
        tips = {
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
        
        return tips.get(mode_key, tips['livre'])
    
    def validate_expression_for_mode(self, expression: str, mode_key: str = None) -> tuple[bool, str]: #Valida se uma expressão é adequada para o modo.
        if mode_key is None:
            mode_key = self.current_mode
            
        if mode_key is None:
            return False, "Nenhum modo selecionado"
        
        #Validações básicas
        if not expression or not expression.strip():
            return False, "Expressão não pode estar vazia"
        
        #Remove espaços e converte para maiúscula
        expr = expression.strip().upper().replace(" ", "")
        
        #Verifica caracteres válidos
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ()~*+')
        if not all(c in valid_chars for c in expr):
            return False, "Expressão contém caracteres inválidos"
        
        #Validações específicas por modo
        mode_info = self.get_mode_info(mode_key)
        difficulty = mode_info['difficulty']
        
        #Para modos de desafio, sugere complexidade mínima
        if mode_key in ['nand_only', 'nor_only'] and len(expr) < 5:
            return False, f"Para o {mode_info['name']}, use uma expressão mais complexa"
        
        #Para modo expert, sugere expressões mais complexas
        if difficulty == 'Expert' and expr.count('*') + expr.count('+') < 2:
            return False, "Modo Expert requer expressões mais complexas"
        
        return True, "Expressão válida"
    
    def get_completion_message(self, mode_key: str = None) -> str: #Retorna mensagem de conclusão específica do modo.
        #NÂO TO USANDO ESSA FUNÇÃO POR ENQUANTO
        if mode_key is None:
            mode_key = self.current_mode
            
        if mode_key is None:
            return "Parabéns! Você completou o desafio!"
            
        mode_info = self.get_mode_info(mode_key)
        messages = {
            'livre': f"Parabéns! Você implementou o circuito corretamente!",
            'nand_only': f"Excelente! Você dominou a completude funcional do NAND!",
            'nor_only': f"Fantástico! Você provou que NOR é funcionalmente completa!",
            'basic_gates': f"Muito bem! Implementação clara com portas básicas!",
            'advanced_gates': f"Impressionante! Ótimo uso das portas avançadas!",
            'minimal': f"Perfeito! Solução elegante e minimalista!"
        }
        
        base_message = messages.get(mode_key, messages['livre'])
        return f"{mode_info['icon']} {base_message} {mode_info['icon']}"

circuit_mode_manager = CircuitModeManager()