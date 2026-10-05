"""
O editor do circuito interativo mudou para o navegador (TypeScript). Os
cenários que o teste do frontend confere (frontend/src/circuito/editor/modelo.test.ts)
são gerados pelo código pygame ORIGINAL; aqui garantimos que o arquivo gravado
é exatamente o que o oráculo produz hoje.
"""
import pytest

pytest.importorskip("pygame")
pytest.importorskip("tkinter")

from tests.paridade import editor_circuito  # noqa: E402


def test_cenarios_do_editor_estao_atualizados():
    gravado = editor_circuito.ARQUIVO.read_text(encoding="utf-8")
    assert gravado == editor_circuito.texto(), (
        "Os cenários do editor estão desatualizados; rode: python -m tests.paridade.editor_circuito"
    )


def test_cenarios_cobrem_os_casos_interessantes():
    cenarios = editor_circuito.cenarios()
    posicoes = cenarios["posicao"]
    assert any(c["colide"] for c in posicoes) and any(not c["colide"] for c in posicoes)
    assert any(c["colide"] and c["valida"] != [c["x"], c["y"]] for c in posicoes)  # a espiral achou lugar
    cliques = cenarios["clique"]
    assert any(c["pino"] and c["pino"][0] == "saida" for c in cliques)
    assert any(c["pino"] and c["pino"][0] == "entrada" for c in cliques)
    assert any(c["componente"] is not None and c["pino"] is None for c in cliques)
    assert any(c["componente"] is None for c in cliques)
    arrastos = cenarios["arrasto"]
    parados = [a for a in arrastos if a["final"] == [a["layout"][a["selecionado"]]["x"], a["layout"][a["selecionado"]]["y"]]]
    assert parados and len(parados) < len(arrastos)
