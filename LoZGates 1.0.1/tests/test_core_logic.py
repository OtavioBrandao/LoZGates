import itertools
import unittest

from BackEnd.converter import Conversorlogical, converter_para_algebra_booleana
from BackEnd.equivalencia import UniversalLogicAnalyzer, check_universal_equivalence
from BackEnd.tabela import gerar_tabela_verdade


class ConverterTests(unittest.TestCase):
    def test_converts_supported_operator_notations(self):
        self.assertEqual(converter_para_algebra_booleana("A -> B"), "~A+B")
        self.assertEqual(converter_para_algebra_booleana("!A | B"), "~A+B")
        self.assertTrue(
            check_universal_equivalence(
                converter_para_algebra_booleana("A <-> B"),
                "(A&B)|(!A&!B)",
            )
        )

    def test_batch_rejects_unbalanced_parentheses(self):
        result = Conversorlogical().convert_batch(["A & B", "(A | B"])
        self.assertEqual(result["A & B"], "A*B")
        self.assertTrue(result["(A | B"].startswith("ERRO:"))


class LogicAnalyzerTests(unittest.TestCase):
    def test_algebraic_and_propositional_aliases_match(self):
        analyzer = UniversalLogicAnalyzer()
        for a, b, c in itertools.product([False, True], repeat=3):
            values = {"A": a, "B": b, "C": c}
            with self.subTest(values=values):
                self.assertEqual(
                    analyzer.analyze_expression("(A*B)+~C", values),
                    analyzer.analyze_expression("(A&B)|!C", values),
                )

    def test_operator_precedence_and_nested_negation(self):
        analyzer = UniversalLogicAnalyzer()
        values = {"A": True, "B": False, "C": False}
        self.assertFalse(analyzer.analyze_expression("A|B>C", values))
        self.assertTrue(analyzer.analyze_expression("!!A", values))

    def test_invalid_characters_and_syntax_are_rejected(self):
        analyzer = UniversalLogicAnalyzer()
        for expression in ("", "A_ B", "A&", "(A|B"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    analyzer.analyze_expression(expression, {"A": True, "B": False})

    def test_truth_table_has_every_combination(self):
        result = gerar_tabela_verdade("A*B")
        self.assertEqual(result["colunas"], ["A", "B", "A*B"])
        self.assertEqual(len(result["tabela"]), 4)
        self.assertEqual(result["resultados_finais"], [0, 0, 0, 1])


if __name__ == "__main__":
    unittest.main()
