import logging
from BackEnd.equivalencia import check_universal_equivalence

logger = logging.getLogger(__name__)

class EquivalenceController:
    def __init__(self, user_logger):
        self.user_logger = user_logger

    def compare(self, expr1: str, expr2: str) -> bool:
        """
        Valida entradas, chama o motor de equivalência lógica, 
        e salva no logger de uso.
        
        Retorna:
            True se equivalentes, False caso contrário.
        Levanta:
            ValueError se as expressões forem inválidas.
            Exception para outros erros subjacentes.
        """
        expr1 = expr1.strip().upper()
        expr2 = expr2.strip().upper()
        
        if not expr1 or not expr2:
            raise ValueError("As expressões não podem estar vazias.")
            
        logger.debug("Comparando expressoes %s e %s", expr1, expr2)
        
        # VERIFICAÇÃO: Equivalência lógica semântica via Tabela Verdade Universal
        resultado = check_universal_equivalence(expr1, expr2, debug=False)
        
        if resultado:
            logger.info("Expressoes logicamente equivalentes")
        else:
            logger.info("Expressoes nao equivalentes")

        # LOG DETALHADO COM EXPRESSÕES REAIS
        self.user_logger.log_equivalence_check_with_expressions(
            expr1, expr2, resultado
        )
        
        return resultado
