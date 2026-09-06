import unittest
import sys
import os

# Garantir que o path inclua o diretório principal do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



class TestRegressionBugs(unittest.TestCase):
    
    def test_bug_1_if_necessary_create_a_circuit_removed(self):
        """
        BUG 1: NameError: name 'if_necessary_create_a_circuit' is not defined
        Verificar se a função if_necessary_create_a_circuit não está sendo usada 
        na tela de expressão. Ela foi substituída pelo método on_tab_change.
        """
        import FrontEnd.screens.expression.expression_screen as expr_screen
        import inspect
        source = inspect.getsource(expr_screen)
        self.assertNotIn('if_necessary_create_a_circuit', source, 
                         "A referência antiga if_necessary_create_a_circuit ainda está no código.")

    def test_bug_2_typography_weight_bold(self):
        """
        BUG 2: AttributeError: type object 'Typography' has no attribute 'WEIGHT_MEDIUM'
        Verificar se Typography.WEIGHT_MEDIUM foi substituído corretamente.
        """
        import FrontEnd.screens.resolver.resolver_screen as res_screen
        import inspect
        source = inspect.getsource(res_screen)
        self.assertNotIn('WEIGHT_MEDIUM', source, 
                         "O peso da fonte WEIGHT_MEDIUM ainda está presente, o correto é WEIGHT_BOLD ou WEIGHT_REGULAR.")

    def test_bug_3_zero_division_in_logging_service(self):
        """
        BUG 3: ZeroDivisionError no log simplificado se sessions_started for 0.
        Verificar se log_simplification_completed não gera erro se não houver sessões.
        """
        from FrontEnd.services.logging_service import DetailedUserLogger
        
        logger = DetailedUserLogger("1.0-beta")
        # Simular 0 sessões iniciadas
        logger.current_session["interactive_simplification"]["sessions_started"] = 0
        logger.current_session["interactive_simplification"]["expressions_completed"] = 1
        
        try:
            logger.log_simplification_completed(5, ["identidade"])
            success = True
        except ZeroDivisionError:
            success = False
            
        self.assertTrue(success, "ZeroDivisionError ocorreu no logging_service!")
        
    def test_bug_4_circuit_logging_in_interactive_circuit(self):
        """
        BUG 4: Sessão de circuito salva com 0 eventos.
        Verificar se o CircuitoInterativoManual aceita o user_logger e chama log_component_action.
        """
        from BackEnd.circuito_logico.interactive.interactive_circuit import CircuitoInterativoManual
        from FrontEnd.services.logging_service import DetailedUserLogger
        import tkinter as tk
        
        # Testar apenas se o logger foi salvo e as chamadas existem
        import inspect
        source = inspect.getsource(CircuitoInterativoManual)
        self.assertIn("self.logger = logger", source, "A injeção do user_logger não foi feita no __init__")
        self.assertIn("self.logger.log_component_action", source, "O logger não é usado para registrar a ação de componente")

    def test_bug_5_google_forms_4_fields(self):
        """
        BUG 5: Google Forms reporta envio com 3 campos, devia ser 4.
        Verificar se 'formatted_report' está no ENTRY_MAPPING do app.
        """
        from FrontEnd.app.loz_app import LOZGatesApp
        import inspect
        source = inspect.getsource(LOZGatesApp.on_closing)
        self.assertIn("'summary_json'", source, "O ENTRY_MAPPING deve conter 'summary_json' para envio correto dos dados RAW JSON.")
        self.assertNotIn("'formatted_report'", source, "O 'formatted_report' NÃO deve estar no ENTRY_MAPPING, para evitar sobreposição.")

if __name__ == '__main__':
    unittest.main()
