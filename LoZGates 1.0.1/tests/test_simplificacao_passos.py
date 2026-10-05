"""Passos estruturados do "Simplificar — Resultado" (identificar_lei.simplificar_expressao)."""
import contextlib
import io
import threading

import pytest

from BackEnd.core.expression_ast import ExpressaoInvalida
from BackEnd.identificar_lei import principal_simplificar, simplificar_expressao
from BackEnd.converter import converter_para_algebra_booleana


def test_resultado_igual_ao_fluxo_antigo_da_interface():
    expressao = "((A & B) | (A & !B)) | ((A & C) | (A & !C)) | (A & D)"
    with contextlib.redirect_stdout(io.StringIO()):
        antigo = principal_simplificar(converter_para_algebra_booleana(expressao))
    resultado = simplificar_expressao(expressao)
    assert resultado.expressao_final == str(antigo) == "A"
    assert resultado.motivo_parada == "completed"


def test_cada_passo_tem_lei_e_trechos_coerentes():
    resultado = simplificar_expressao("(A&1)|(B&!B)")
    assert [p.lei for p in resultado.passos] == ["Identidade", "Inversa", "Identidade"]
    for passo in resultado.passos:
        inicio, fim = passo.trecho_antes
        assert passo.expressao_antes[inicio:fim] == passo.subexpressao_antes
        inicio, fim = passo.trecho_depois
        assert passo.expressao_depois[inicio:fim] == passo.subexpressao_depois
    for anterior, seguinte in zip(resultado.passos, resultado.passos[1:]):
        assert anterior.expressao_depois == seguinte.expressao_antes
    assert resultado.passos[-1].expressao_depois == resultado.expressao_final == "A"


def test_expressao_ja_simplificada_nao_tem_passos():
    resultado = simplificar_expressao("A & B")
    assert resultado.passos == []
    assert resultado.expressao_final == "A&B"
    assert resultado.motivo_parada == "no_further_simplification"


def test_converte_implicacao_antes_de_simplificar():
    resultado = simplificar_expressao("A > A")
    assert resultado.expressao_booleana == "~A+A"
    assert resultado.expressao_final == "1"


def test_erro_de_sintaxe_sobe_com_mensagem_clara():
    with pytest.raises(ExpressaoInvalida, match="Falta um operador"):
        simplificar_expressao("AB")


def test_simplificacoes_em_paralelo_nao_corrompem_a_saida():
    erros = []

    def trabalho():
        try:
            for _ in range(20):
                assert simplificar_expressao("(A&1)|(B&!B)").expressao_final == "A"
        except Exception as erro:  # noqa: BLE001 - o teste coleta qualquer falha das threads
            erros.append(erro)

    threads = [threading.Thread(target=trabalho, daemon=True) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not erros
    import sys
    assert sys.stdout is sys.__stdout__ or not isinstance(sys.stdout, io.StringIO)
