"""
Layout do circuito gerado a partir da expressão, como dados (JSON).

É o mesmo raciocínio do desenho em pygame do interface_update
(circuit_renderer.desenhar_circuito_logico_base, desenhar_circuito_dinamico e
CircuitDrawer.draw_gate_shape), só que separado do desenho: barramentos,
portas, pinos, fios, pontos de conexão e saída com as MESMAS coordenadas de
"mundo" do circuito original. O frontend só desenha.

Novidades em relação ao desenho antigo (dados extras, sem mudar posições):
a subexpressão e o caminho de cada porta, para destacar no hover, e, se forem
passados valores das variáveis, o nível lógico de cada barramento, porta e fio.
"""
from typing import Dict, List, Optional, Tuple

from BackEnd.circuito_logico.logic.parser import calcular_layout_dinamico
from BackEnd.converter import converter_para_algebra_booleana
from BackEnd.core.expression_ast import (
    AND,
    NOT,
    OR,
    VariableNode,
    avaliar,
    collect_variables,
    parse,
    percorrer,
    to_string,
)

# Mesmas constantes do desenho original (CircuitDrawer e circuit_renderer)
LARGURA_PORTA = 60              # GATE_WIDTH
ALTURA_PORTA = 80               # GATE_HEIGHT
ESPACO_HORIZONTAL = 180         # NODE_H_SPACING
X_PRIMEIRO_BARRAMENTO = 100
ESPACO_ENTRE_BARRAMENTOS = 100
DESLOCAMENTO_DO_NEGADO = 40
Y_INICIO_BARRAMENTO = 40
Y_ROTULO_BARRAMENTO = 25
FOLGA_ATE_A_PRIMEIRA_PORTA = 150
Y_BASE = 100
COMPRIMENTO_DA_SAIDA = 80
DESLOCAMENTO_DO_ROTULO_DA_SAIDA = 120
# Constantes 0/1 não existiam no circuito antigo (dava erro): ganham um barramento próprio
ESPACO_DO_BARRAMENTO_CONSTANTE = 60

NOME_DA_PORTA = {AND: "AND", OR: "OR", NOT: "NOT"}

Ponto = Tuple[float, float]


def saida_da_porta(tipo: str, x: float, y: float) -> Ponto:
    """Posição da saída, como devolvida por CircuitDrawer.draw_gate_shape."""
    w = LARGURA_PORTA - 20
    if tipo == "NOT":
        return (x + 46, y + ALTURA_PORTA / 2)
    if tipo in ("NAND", "NOR", "XNOR"):
        return (x + w + 16, y + ALTURA_PORTA / 2)
    return (x + w, y + ALTURA_PORTA / 2)


def largura_da_porta(tipo: str) -> float:
    return saida_da_porta(tipo, 0, 0)[0]


def rota_do_fio(inicio: Ponto, fim: Ponto) -> List[Ponto]:
    """Fio em três segmentos pelo meio do caminho (CircuitDrawer.draw_smart_wire)."""
    (x1, y1), (x2, y2) = inicio, fim
    meio = x1 + (x2 - x1) * 0.5
    return [(x1, y1), (meio, y1), (meio, y2), (x2, y2)]


class _Montador:
    def __init__(self, arvore, valores: Optional[Dict[str, bool]]):
        self.arvore = arvore
        self.valores = valores
        self.barramentos: List[dict] = []
        self.posicao_dos_barramentos: Dict[str, float] = {}
        self.portas: List[dict] = []
        self.fios: List[dict] = []
        self.conexoes: List[dict] = []

    def _valor(self, no) -> Optional[bool]:
        return None if self.valores is None else avaliar(no, self.valores)

    def _barramento(self, nome: str, rotulo: str, x: float, tipo: str, valor: Optional[bool]):
        self.posicao_dos_barramentos[nome] = x
        self.barramentos.append({'id': nome, 'rotulo': rotulo, 'x': x, 'tipo': tipo, 'valor': valor})

    def montar_barramentos(self, variaveis: List[str], constantes: List[str]) -> float:
        ultimo_x = X_PRIMEIRO_BARRAMENTO
        for i, nome in enumerate(variaveis):
            x = X_PRIMEIRO_BARRAMENTO + i * ESPACO_ENTRE_BARRAMENTOS
            valor = None if self.valores is None else bool(self.valores.get(nome, False))
            self._barramento(nome, nome, x, 'variavel', valor)
            self._barramento(f"~{nome}", f"~{nome}", x + DESLOCAMENTO_DO_NEGADO, 'negado',
                             None if valor is None else not valor)
            ultimo_x = x + DESLOCAMENTO_DO_NEGADO
        for constante in constantes:
            ultimo_x += ESPACO_DO_BARRAMENTO_CONSTANTE
            self._barramento(constante, constante, ultimo_x, 'constante', constante == '1')
        return ultimo_x

    def montar(self, layout: dict, no, caminho: Tuple[int, ...], x_pos: float) -> dict:
        tipo = layout.get('type')
        if tipo in ('variable', 'negated_variable', 'constant'):
            nome = f"~{layout['name']}" if tipo == 'negated_variable' else layout['name']
            ponto = (self.posicao_dos_barramentos[nome], layout['y_pos'] + 40)
            return {'tipo': 'barramento', 'id': nome, 'ponto': ponto}

        nome_da_porta = NOME_DA_PORTA[layout['op']]
        centro_y = layout['y_pos']
        topo_y = centro_y - ALTURA_PORTA / 2
        saida = saida_da_porta(nome_da_porta, x_pos, topo_y)
        quantidade = len(layout['children'])
        if quantidade == 1:
            entradas = [(x_pos, centro_y)]
        else:
            espaco = (ALTURA_PORTA - 30) / (quantidade - 1)
            entradas = [(x_pos, (topo_y + 15) + espaco * i) for i in range(quantidade)]

        porta = {
            'id': f"p{len(self.portas)}",
            'tipo': nome_da_porta,
            'x': x_pos,
            'y': topo_y,
            'largura': largura_da_porta(nome_da_porta),
            'altura': ALTURA_PORTA,
            'entradas': entradas,
            'saida': saida,
            'subexpressao': to_string(no, style="boolean"),
            'caminho': list(caminho),
            'valor': self._valor(no),
        }
        self.portas.append(porta)

        for i, (filho_layout, filho) in enumerate(zip(layout['children'], no.children)):
            origem = self.montar(filho_layout, filho, caminho + (i,), x_pos - ESPACO_HORIZONTAL)
            if origem['tipo'] == 'barramento':
                inicio = origem['ponto']
                self.conexoes.append({'barramento': origem['id'], 'ponto': inicio})
                valor = next(b['valor'] for b in self.barramentos if b['id'] == origem['id'])
            else:
                inicio = origem['ponto']
                valor = origem['valor']
            self.fios.append({
                'id': f"f{len(self.fios)}",
                'origem': {'tipo': origem['tipo'], 'id': origem['id']},
                'destino': {'porta': porta['id'], 'entrada': i},
                'pontos': rota_do_fio(inicio, entradas[i]),
                'valor': valor,
            })

        return {'tipo': 'porta', 'id': porta['id'], 'ponto': saida, 'valor': porta['valor']}


def _limites(barramentos, portas, fios, saida, y_fim) -> Dict[str, float]:
    xs, ys = [], [Y_ROTULO_BARRAMENTO - 15, y_fim]
    xs += [b['x'] for b in barramentos]
    for porta in portas:
        xs += [porta['x'] - 20, porta['x'] + porta['largura']]
        ys += [porta['y'], porta['y'] + porta['altura']]
    for fio in fios:
        xs += [p[0] for p in fio['pontos']]
        ys += [p[1] for p in fio['pontos']]
    if saida:
        xs.append(saida['rotulo'][0] + 40)
    if not xs:
        xs = [X_PRIMEIRO_BARRAMENTO]
    return {'x_min': min(xs) - 30, 'y_min': min(ys), 'x_max': max(xs) + 30, 'y_max': max(ys)}


def montar_layout(expressao: str, valores: Optional[Dict[str, bool]] = None) -> dict:
    """
    Layout completo do circuito da expressão (em notação lógica ou booleana).
    Erros de sintaxe sobem como ExpressaoInvalida.
    """
    booleana = converter_para_algebra_booleana(expressao)
    arvore = parse(booleana)
    variaveis = sorted(collect_variables(arvore))
    constantes = sorted({no.name for _, no in percorrer(arvore) if isinstance(no, VariableNode) and no.eh_constante})

    montador = _Montador(arvore, valores)
    ultimo_barramento_x = montador.montar_barramentos(variaveis, constantes)

    layout = calcular_layout_dinamico(arvore, y_base=Y_BASE)
    primeira_porta_x = ultimo_barramento_x + FOLGA_ATE_A_PRIMEIRA_PORTA
    resultado = montador.montar(layout, arvore, (), primeira_porta_x + layout.get('width', 0))

    saida = None
    if resultado['tipo'] == 'porta':
        x, y = resultado['ponto']
        saida = {
            'de': (x, y),
            'ate': (x + COMPRIMENTO_DA_SAIDA, y),
            'rotulo': (x + DESLOCAMENTO_DO_ROTULO_DA_SAIDA, y),
            'valor': resultado['valor'],
        }

    y_mais_baixo = max(
        [Y_INICIO_BARRAMENTO + ALTURA_PORTA]
        + [p['y'] + p['altura'] for p in montador.portas]
        + [ponto[1] for fio in montador.fios for ponto in fio['pontos']]
    )
    y_fim = y_mais_baixo + 40
    for barramento in montador.barramentos:
        barramento['y_inicio'] = Y_INICIO_BARRAMENTO
        barramento['y_fim'] = y_fim
        barramento['y_rotulo'] = Y_ROTULO_BARRAMENTO

    return {
        'expressao': expressao,
        'expressao_booleana': booleana,
        'variaveis': variaveis,
        'barramentos': montador.barramentos,
        'portas': montador.portas,
        'fios': montador.fios,
        'conexoes': montador.conexoes,
        'saida': saida,
        'valor': None if valores is None else avaliar(arvore, valores),
        'limites': _limites(montador.barramentos, montador.portas, montador.fios, saida, y_fim),
    }
