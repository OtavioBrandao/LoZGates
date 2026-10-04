"""
Geometria dos componentes do circuito interativo: tamanhos, pinos e as regras
de posicionamento do editor do interface_update.

Os pinos das portas são os que o desenho original usava de fato
(CircuitDrawer.draw_component recalculava a posição a cada quadro), e não os
provisórios de Component._setup_connection_points. O editor no navegador usa
estes valores para desenhar, detectar cliques e evitar sobreposição.
"""
from typing import Dict, List, Optional, Tuple

TIPOS_DE_PORTA = ('and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor')
TIPOS = ('variable',) + TIPOS_DE_PORTA + ('output',)

# Nomes exibidos (ComponentFactory) e rótulos desenhados dentro do componente
NOMES = {
    'variable': 'Variável', 'and': 'AND', 'or': 'OR', 'not': 'NOT', 'nand': 'NAND',
    'nor': 'NOR', 'xor': 'XOR', 'xnor': 'XNOR', 'output': 'Saída',
}
ROTULO_SAIDA = "SAÍDA"

LARGURA = 80
ALTURA = {'variable': 60, 'output': 60, **{tipo: 80 for tipo in TIPOS_DE_PORTA}}
# Área extra em volta do componente que ainda conta como clique nele
FOLGA_DE_SELECAO = {'variable': 10, 'output': 10, **{tipo: 15 for tipo in TIPOS_DE_PORTA}}

MARGEM_DE_COLISAO = 10
RAIO_DE_DETECCAO_DO_PINO = 15
# Ao posicionar, o componente fica com o canto em (cursor - deslocamento)
DESLOCAMENTO_AO_POSICIONAR = (40, 30)
# Busca em espiral por um lugar livre (find_valid_position)
BUSCA_ESPIRAL = {'passo': 30, 'raio_maximo': 200, 'passo_angulo': 30}
# Ao arrastar sobre outro componente, só aceita um lugar livre próximo
DISTANCIA_MAXIMA_DE_AJUSTE_NO_ARRASTO = 50
# Variáveis empilhadas à esquerda e a saída à direita (init_basic_components)
ORIGEM_DAS_VARIAVEIS = (-300, -100)
ESPACO_ENTRE_VARIAVEIS = 100
POSICAO_DA_SAIDA = (300, 0)
MAXIMO_DE_ESTADOS_NO_HISTORICO = 50


def pinos(tipo: str) -> Dict[str, object]:
    """Pinos relativos ao canto superior esquerdo do componente."""
    if tipo == 'variable':
        return {'entradas': [], 'saida': (80, 30)}
    if tipo == 'output':
        return {'entradas': [(0, 30)], 'saida': None}
    if tipo == 'not':
        return {'entradas': [(0, 40)], 'saida': (46, 40)}
    if tipo in ('nand', 'nor', 'xnor'):
        return {'entradas': [(0, 20), (0, 60)], 'saida': (56, 40)}
    if tipo in ('and', 'or', 'xor'):
        return {'entradas': [(0, 20), (0, 60)], 'saida': (40, 40)}
    raise ValueError(f"Tipo de componente desconhecido: {tipo}")


def definicoes() -> Dict[str, object]:
    return {
        'tipos': {
            tipo: {
                'nome': NOMES[tipo],
                'largura': LARGURA,
                'altura': ALTURA[tipo],
                'folga_de_selecao': FOLGA_DE_SELECAO[tipo],
                **pinos(tipo),
            }
            for tipo in TIPOS
        },
        'portas': list(TIPOS_DE_PORTA),
        'rotulo_saida': ROTULO_SAIDA,
        'margem_de_colisao': MARGEM_DE_COLISAO,
        'raio_de_deteccao_do_pino': RAIO_DE_DETECCAO_DO_PINO,
        'deslocamento_ao_posicionar': DESLOCAMENTO_AO_POSICIONAR,
        'busca_espiral': BUSCA_ESPIRAL,
        'distancia_maxima_de_ajuste_no_arrasto': DISTANCIA_MAXIMA_DE_AJUSTE_NO_ARRASTO,
        'maximo_de_estados_no_historico': MAXIMO_DE_ESTADOS_NO_HISTORICO,
    }


def componentes_iniciais(variaveis: List[str]) -> List[Dict[str, object]]:
    """Variáveis da expressão e a saída, nas posições do editor original."""
    x0, y0 = ORIGEM_DAS_VARIAVEIS
    componentes = [
        {'id': f'var-{nome}', 'tipo': 'variable', 'nome': nome, 'x': x0, 'y': y0 + i * ESPACO_ENTRE_VARIAVEIS}
        for i, nome in enumerate(variaveis)
    ]
    componentes.append({'id': 'saida', 'tipo': 'output', 'nome': ROTULO_SAIDA,
                        'x': POSICAO_DA_SAIDA[0], 'y': POSICAO_DA_SAIDA[1]})
    return componentes


def posicao_absoluta(pino: Optional[Tuple[int, int]], x: float, y: float) -> Optional[Tuple[float, float]]:
    return None if pino is None else (x + pino[0], y + pino[1])
