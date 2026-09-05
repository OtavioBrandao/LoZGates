import unittest
import sys
import os

# Adiciona o diretório principal ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BackEnd.equivalencia import check_universal_equivalence

class TestUniversalEquivalence(unittest.TestCase):
    def test_implicacao_inversa(self):
        # Teste 1: P -> Q vs Q -> P
        # NÃO devem ser equivalentes
        self.assertFalse(check_universal_equivalence("P>Q", "Q>P"))

    def test_implicacao_definicao(self):
        # Teste 2: P -> Q vs ~P | Q
        # Devem ser equivalentes
        self.assertTrue(check_universal_equivalence("P>Q", "!P|Q"))
        self.assertTrue(check_universal_equivalence("P>Q", "~P|Q")) # Suporte a notações variadas

    def test_comutatividade_and(self):
        # Teste 3: P & Q vs Q & P
        # Devem ser equivalentes
        self.assertTrue(check_universal_equivalence("P&Q", "Q&P"))
        self.assertTrue(check_universal_equivalence("P*Q", "Q*P"))

    def test_comutatividade_or(self):
        # Teste 4: P | Q vs Q | P
        # Devem ser equivalentes
        self.assertTrue(check_universal_equivalence("P|Q", "Q|P"))
        self.assertTrue(check_universal_equivalence("P+Q", "Q+P"))

    def test_negacao_simples(self):
        # Teste 5: P vs ~P
        # NÃO devem ser equivalentes
        self.assertFalse(check_universal_equivalence("P", "!P"))

    def test_contradicao(self):
        # Teste 6: P & ~P vs 0
        # Devem ser equivalentes
        self.assertTrue(check_universal_equivalence("P&!P", "0"))

    def test_compostas_equivalentes(self):
        # Teste 8 (Compostas equivalentes): P -> (Q | R) vs ~P | (Q | R)
        self.assertTrue(check_universal_equivalence("P>(Q|R)", "!P|(Q|R)"))
        
    def test_compostas_nao_equivalentes(self):
        # Teste 8 (Compostas não equivalentes): P -> Q vs Q -> P
        self.assertFalse(check_universal_equivalence("P>Q", "Q>P"))
        
    def test_bateria_regressao(self):
        # Teste 11: Bateria de regressão
        self.assertTrue(check_universal_equivalence("P&Q", "Q&P"))
        self.assertTrue(check_universal_equivalence("P|Q", "Q|P"))
        self.assertFalse(check_universal_equivalence("P>Q", "Q>P"))
        self.assertTrue(check_universal_equivalence("P>Q", "!P|Q"))
        self.assertTrue(check_universal_equivalence("!(P&Q)", "!P|!Q"))
        self.assertTrue(check_universal_equivalence("!(P|Q)", "!P&!Q"))

if __name__ == '__main__':
    unittest.main(verbosity=2)
