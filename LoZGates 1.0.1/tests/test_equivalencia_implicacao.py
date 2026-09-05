import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from BackEnd.equivalencia import check_universal_equivalence, UniversalLogicAnalyzer

class TestEquivalenceFinal(unittest.TestCase):
    def test_1_implication_order(self):
        self.assertFalse(check_universal_equivalence("P > Q", "Q > P"))

    def test_2_implication_definition(self):
        self.assertTrue(check_universal_equivalence("P > Q", "!P | Q"))

    def test_3_and_commutative(self):
        self.assertTrue(check_universal_equivalence("P & Q", "Q & P"))

    def test_4_or_commutative(self):
        self.assertTrue(check_universal_equivalence("P | Q", "Q | P"))

    def test_5_not_equivalent(self):
        self.assertFalse(check_universal_equivalence("P", "!P"))

    def test_6_de_morgan(self):
        self.assertTrue(check_universal_equivalence("!(P & Q)", "!P | !Q"))

    def test_7_implication_vs_or(self):
        self.assertFalse(check_universal_equivalence("P > Q", "P | Q"))

if __name__ == '__main__':
    analyzer = UniversalLogicAnalyzer()
    
    print("--- PARSER (TOKENIZATION) ---")
    tokens_pq = analyzer.tokenize("P > Q")
    tokens_qp = analyzer.tokenize("Q > P")
    print("P > Q  ->", tokens_pq)
    print("Q > P  ->", tokens_qp)
    
    print("\n--- AVALIAÇÃO (TODAS AS COMBINAÇÕES) ---")
    variables = ['P', 'Q']
    combinations = [(False, False), (False, True), (True, False), (True, True)]
    
    res_pq = []
    res_qp = []
    for c in combinations:
        val = {'P': c[0], 'Q': c[1]}
        r1 = analyzer.evaluate_expression(list(tokens_pq), val)
        r2 = analyzer.evaluate_expression(list(tokens_qp), val)
        res_pq.append(int(r1))
        res_qp.append(int(r2))
        print(f"P={int(c[0])}, Q={int(c[1])} | P>Q = {int(r1)} | Q>P = {int(r2)}")
        
    print(f"\nResultados P>Q: {res_pq}")
    print(f"Resultados Q>P: {res_qp}")
    
    print("\n--- RODANDO TESTES UNITÁRIOS ---")
    unittest.main()
