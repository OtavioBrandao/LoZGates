import contextlib
import io
import unittest

from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.identificar_lei import construir_arvore, principal_simplificar, simplificar


def simplify(expression):
    algebraic = converter_para_algebra_booleana(expression)
    with contextlib.redirect_stdout(io.StringIO()):
        return principal_simplificar(algebraic)


class AutomaticSimplifierTests(unittest.TestCase):
    def test_large_reduction_finishes_at_a(self):
        result = simplify(
            "((A & B) | (A & !B)) | ((A & C) | (A & !C)) | (A & D)"
        )
        self.assertEqual(str(result), "A")

    def test_complement_absorption_and_already_reduced_cases(self):
        cases = (
            ("A | !A", "1"),
            ("A | (A & B)", "A"),
            ("A & B", "(A&B)"),
        )
        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertEqual(str(simplify(expression)), expected)

    def test_complex_expression_stops_without_cycle(self):
        result = simplify("((A | B) & 1) | ((A | B) & 0)")
        self.assertEqual(str(result), "(A|B)")

    def test_maximum_step_limit_preserves_last_valid_expression(self):
        tree = construir_arvore("(A&1)&1")
        with self.assertLogs("BackEnd.identificar_lei", level="WARNING") as logs:
            with contextlib.redirect_stdout(io.StringIO()):
                result = simplificar(tree, max_steps=1)
        self.assertEqual(str(result), "(A&1)")
        self.assertTrue(any("maximum steps reached" in line for line in logs.output))


if __name__ == "__main__":
    unittest.main()
