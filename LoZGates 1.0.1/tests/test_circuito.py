"""Circuito como dados: layout do circuito gerado e correção do circuito montado."""
import pytest

from BackEnd.circuito_logico.logic.componentes import componentes_iniciais, definicoes, pinos
from BackEnd.circuito_logico.logic.layout import montar_layout
from BackEnd.circuito_logico.logic.validacao import (
    CircuitoInvalido,
    montar_netlist,
    simular,
    validar_circuito,
)
from BackEnd.circuito_logico.modos import MODOS, dicas_do_modo, info_do_modo
from BackEnd.core.expression_ast import ExpressaoInvalida


# ------------------------------ layout do circuito gerado ------------------------------

def test_layout_de_a_e_b_com_as_coordenadas_do_desenho_original():
    layout = montar_layout("A*B")
    assert [(b['rotulo'], b['x']) for b in layout['barramentos']] == [("A", 100), ("~A", 140), ("B", 200), ("~B", 240)]
    (porta,) = layout['portas']
    assert (porta['tipo'], porta['x'], porta['y']) == ("AND", 570, 150)
    assert porta['entradas'] == [(570, 165), (570, 215)]
    assert porta['saida'] == (610, 190)
    assert porta['subexpressao'] == "A*B"
    assert [f['pontos'] for f in layout['fios']] == [
        [(100, 140), (335.0, 140), (335.0, 165), (570, 165)],
        [(200, 240), (385.0, 240), (385.0, 215), (570, 215)],
    ]
    assert [c['ponto'] for c in layout['conexoes']] == [(100, 140), (200, 240)]
    assert layout['saida'] == {'de': (610, 190), 'ate': (690, 190), 'rotulo': (730, 190), 'valor': None}


def test_layout_converte_implicacao_e_usa_barramento_negado():
    layout = montar_layout("A>B")
    assert layout['expressao_booleana'] == "~A+B"
    (porta,) = layout['portas']
    assert porta['tipo'] == "OR"
    assert [f['origem'] for f in layout['fios']] == [{'tipo': 'barramento', 'id': '~A'}, {'tipo': 'barramento', 'id': 'B'}]


def test_valores_acendem_barramentos_portas_e_fios():
    layout = montar_layout("A*B", valores={"A": True, "B": False})
    assert [b['valor'] for b in layout['barramentos']] == [True, False, False, True]
    assert layout['portas'][0]['valor'] is False
    assert [f['valor'] for f in layout['fios']] == [True, False]
    assert layout['saida']['valor'] is False and layout['valor'] is False


def test_porta_not_de_subexpressao_e_caminhos():
    layout = montar_layout("~(A*B)+C")
    assert [p['tipo'] for p in layout['portas']] == ["OR", "NOT", "AND"]
    assert [p['caminho'] for p in layout['portas']] == [[], [0], [0, 0]]
    assert layout['portas'][1]['subexpressao'] == "~(A*B)"


def test_constantes_viram_entradas_fixas():
    layout = montar_layout("A*1")
    assert [(b['rotulo'], b['tipo']) for b in layout['barramentos']] == [("A", "variavel"), ("~A", "negado"), ("1", "constante")]
    assert layout['fios'][1]['origem'] == {'tipo': 'barramento', 'id': '1'}


def test_variavel_sozinha_nao_tem_portas_nem_saida_como_no_original():
    layout = montar_layout("A")
    assert layout['portas'] == [] and layout['fios'] == [] and layout['saida'] is None


def test_expressao_invalida():
    with pytest.raises(ExpressaoInvalida):
        montar_layout("A*")


# ------------------------------ componentes e modos ------------------------------

def test_pinos_e_componentes_iniciais():
    assert pinos('and') == {'entradas': [(0, 20), (0, 60)], 'saida': (40, 40)}
    assert pinos('nand')['saida'] == (56, 40)
    assert pinos('not') == {'entradas': [(0, 40)], 'saida': (46, 40)}
    iniciais = componentes_iniciais(["A", "B"])
    assert [(c['id'], c['x'], c['y']) for c in iniciais] == [("var-A", -300, -100), ("var-B", -300, 0), ("saida", 300, 0)]
    assert set(definicoes()['tipos']) == {'variable', 'and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor', 'output'}


def test_modos():
    assert info_do_modo('nand_only')['restrictions'] == ['nand']
    assert info_do_modo('nao_existe') is MODOS['livre']
    assert dicas_do_modo(None) == ["Selecione um modo primeiro para ver dicas específicas."]


# ------------------------------ correção do circuito montado ------------------------------

def netlist(*portas, fios=(), variaveis=("A", "B")):
    componentes = [{'id': f'var-{v}', 'tipo': 'variable', 'nome': v} for v in variaveis]
    componentes.append({'id': 'saida', 'tipo': 'output'})
    componentes += [{'id': pid, 'tipo': tipo} for pid, tipo in portas]
    return montar_netlist({'componentes': componentes, 'fios': [
        {'origem': o, 'destino': d, 'entrada': e} for o, d, e in fios
    ]})


E_CORRETO = netlist(("g1", "and"), fios=[("var-A", "g1", 0), ("var-B", "g1", 1), ("g1", "saida", 0)])


def test_circuito_correto():
    resultado = validar_circuito("A*B", E_CORRETO)
    assert resultado.correto and resultado.motivo == "correto" and resultado.combinacoes == 4


def test_tabela_diferente_mostra_onde_falha():
    resultado = validar_circuito("A+B", E_CORRETO)
    assert not resultado.correto and resultado.motivo == "tabela_diferente"
    assert resultado.falhas[0] == {'entradas': {'A': False, 'B': True}, 'esperado': True, 'obtido': False}


def test_saida_desconectada_e_variavel_faltando():
    sem_saida = netlist(("g1", "and"), fios=[("var-A", "g1", 0), ("var-B", "g1", 1)])
    assert validar_circuito("A*B", sem_saida).motivo == "saida_desconectada"
    so_a = netlist(("g1", "not"), fios=[("var-A", "g1", 0), ("g1", "saida", 0)])
    resultado = validar_circuito("A*B", so_a)
    assert resultado.motivo == "variaveis_desconectadas" and resultado.variaveis_faltando == ["B"]


def test_precisa_de_porta_exceto_no_modo_minimo():
    direto = netlist(fios=[("var-A", "saida", 0)], variaveis=("A",))
    assert validar_circuito("A", direto).motivo == "sem_portas"
    assert validar_circuito("A", direto, modo="minimal").correto


def test_portas_do_modo_sao_conferidas():
    resultado = validar_circuito("A*B", E_CORRETO, modo="nand_only")
    assert resultado.motivo == "porta_nao_permitida" and resultado.portas_nao_permitidas == ["and"]


def test_porta_com_entrada_solta_nao_simula():
    meia = netlist(("g1", "and"), fios=[("var-A", "g1", 0), ("g1", "saida", 0)], variaveis=("A",))
    assert validar_circuito("A", meia).motivo == "simulacao_incompleta"


def test_simulacao_porta_a_porta():
    saidas = simular(E_CORRETO, {"A": True, "B": True})
    assert saidas == {'var-A': True, 'var-B': True, 'saida': True, 'g1': True}


@pytest.mark.parametrize("dados, trecho", [
    ({'componentes': [{'id': 'x', 'tipo': 'flipflop'}]}, "desconhecido"),
    ({'componentes': [{'id': 'x', 'tipo': 'and'}, {'id': 'x', 'tipo': 'or'}]}, "repetido"),
    ({'componentes': [{'id': 'x', 'tipo': 'and'}], 'fios': [{'origem': 'x', 'destino': 'x', 'entrada': 0}]}, "si mesmo"),
    ({'componentes': [{'id': 'x', 'tipo': 'not'}], 'fios': [{'origem': 'y', 'destino': 'x', 'entrada': 0}]}, "não existe"),
    ({'componentes': [{'id': 'a', 'tipo': 'variable', 'nome': 'A'}, {'id': 'x', 'tipo': 'not'}],
      'fios': [{'origem': 'a', 'destino': 'x', 'entrada': 1}]}, "não tem a entrada"),
    ({'componentes': [{'id': 'a', 'tipo': 'variable', 'nome': 'A'}, {'id': 'b', 'tipo': 'variable', 'nome': 'B'},
                      {'id': 'x', 'tipo': 'not'}],
      'fios': [{'origem': 'a', 'destino': 'x', 'entrada': 0}, {'origem': 'b', 'destino': 'x', 'entrada': 0}]}, "só pode receber"),
    ({'fios': []}, "incompleta"),
])
def test_netlist_malformada(dados, trecho):
    with pytest.raises(CircuitoInvalido, match=trecho):
        montar_netlist(dados)
