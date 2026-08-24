import copy
import unittest

from BackEnd.equivalencia import check_universal_equivalence
from BackEnd.simplificador_interativo import (
    LEIS_LOGICAS,
    SimplificationGuard,
    aplicar_lei_e_substituir,
    calcular_complexidade,
    construir_arvore,
    encontrar_proximo_passo,
    reiniciar_busca,
)


def propositional(expression):
    return expression.replace("*", "&").replace("+", "|").replace("~", "!")


def root_step(tree):
    return {"no_atual": tree, "pai": None, "ramo": None}


class InteractiveSimplifierTests(unittest.TestCase):
    def setUp(self):
        reiniciar_busca()

    def assert_equivalent(self, before, after):
        self.assertTrue(
            check_universal_equivalence(
                propositional(str(before)), propositional(str(after)), debug=False
            )
        )

    def test_parser_preserves_precedence_and_nested_negation(self):
        self.assertEqual(str(construir_arvore("~(A+B)*C")), "(~(A+B)*C)")
        self.assertEqual(str(construir_arvore("A+B*C")), "(A+(B*C))")
        self.assertEqual(str(construir_arvore("~~A")), "~~A")

    def test_parser_rejects_malformed_expressions(self):
        for expression in ("", "A+", "(A+B", "A+B)", "A**B"):
            with self.subTest(expression=expression):
                with self.assertRaises((TypeError, ValueError)):
                    construir_arvore(expression)

    def test_each_exposed_law_changes_an_applicable_root(self):
        cases = (
            (0, "A*~A", "0"),
            (1, "A*0", "0"),
            (2, "A*1", "A"),
            (3, "A*A", "A"),
            (4, "A*(A+B)", "A"),
            (5, "~(A*B)", "(~A+~B)"),
            (6, "(A*B)+(A*C)", "(A*(B+C))"),
            (7, "(A*B)*C", "(A*(B*C))"),
            (8, "B+A", "(A+B)"),
        )
        self.assertEqual(len(cases), len(LEIS_LOGICAS))
        for law_index, expression, expected in cases:
            with self.subTest(law=LEIS_LOGICAS[law_index]["nome"]):
                tree = construir_arvore(expression)
                original = copy.deepcopy(tree)
                result, success = aplicar_lei_e_substituir(
                    tree, root_step(tree), law_index
                )
                self.assertTrue(success)
                self.assertEqual(str(result), expected)
                self.assert_equivalent(original, result)

    def test_distributive_common_factor_simplifies(self):
        tree = construir_arvore("(A+B)*(A+C)")
        original = copy.deepcopy(tree)
        result, success = aplicar_lei_e_substituir(tree, root_step(tree), 6)
        self.assertTrue(success)
        self.assertEqual(str(result), "(A+(B*C))")
        self.assert_equivalent(original, result)

    def test_distributive_expansion_is_not_offered_as_simplification(self):
        tree = construir_arvore("A+(B*C)")
        self.assertFalse(LEIS_LOGICAS[6]["verifica"](tree))
        result, success = aplicar_lei_e_substituir(tree, root_step(tree), 6)
        self.assertFalse(success)
        self.assertIs(result, tree)

    def test_guard_rejects_repetition_non_progress_and_maximum(self):
        repeated_guard = SimplificationGuard(construir_arvore("A+B"))
        self.assertEqual(
            repeated_guard.consider(construir_arvore("B+A")).reason,
            "repeated_state",
        )

        progress_guard = SimplificationGuard(construir_arvore("A*1"), max_steps=1)
        accepted = progress_guard.consider(construir_arvore("A"))
        self.assertTrue(accepted.accepted)
        self.assertEqual(
            progress_guard.consider(construir_arvore("0")).reason,
            "maximum_steps",
        )

        no_progress_guard = SimplificationGuard(construir_arvore("A+B"))
        decision = no_progress_guard.consider(construir_arvore("(A+B)+C"))
        self.assertEqual(decision.reason, "no_progress")

    def test_every_accepted_law_reduces_weighted_complexity(self):
        expressions = (
            "A*~A",
            "A*0",
            "A*1",
            "A*A",
            "A*(A+B)",
            "~(A*B)",
            "(A*B)+(A*C)",
            "(A*B)*C",
            "B+A",
        )
        for index, expression in enumerate(expressions):
            with self.subTest(law=LEIS_LOGICAS[index]["nome"]):
                tree = construir_arvore(expression)
                before = calcular_complexidade(tree)
                result, success = aplicar_lei_e_substituir(
                    tree, root_step(tree), index
                )
                self.assertTrue(success)
                self.assertLess(calcular_complexidade(result), before)

    def test_child_change_invalidates_traversal_cache(self):
        tree = construir_arvore("(A*1)+C")
        first_step = encontrar_proximo_passo(tree)
        self.assertEqual(str(first_step["no_atual"]), "(A*1)")
        result, success = aplicar_lei_e_substituir(tree, first_step, 2)
        self.assertTrue(success)

        next_step = encontrar_proximo_passo(result)
        self.assertIs(next_step["no_atual"], result)
        self.assertEqual(str(next_step["no_atual"]), "(A+C)")

    def test_detached_undo_reference_cannot_report_false_success(self):
        tree = construir_arvore("(A*1)+C")
        step = encontrar_proximo_passo(tree)
        detached_step = copy.deepcopy(step)
        result, success = aplicar_lei_e_substituir(tree, detached_step, 2)
        self.assertFalse(success)
        self.assertIs(result, tree)
        self.assertEqual(str(result), "((A*1)+C)")


if __name__ == "__main__":
    unittest.main()
