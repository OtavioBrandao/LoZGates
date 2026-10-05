"""
Parser canônico das expressões lógicas do LoZ Gates.

É o ÚNICO lugar do projeto que transforma texto em árvore. Simplificadores,
equivalência, tabela-verdade, conversor, normalizador e circuito usam este
parser e estas classes de nó.

Gramática, da menor para a maior precedência:

    expressão   := implicação ( '<>' implicação )*   bi-implicação, associa à esquerda
    implicação  := disjunção ( '>' implicação )?     associa à DIREITA: A>B>C = A>(B>C)
    disjunção   := conjunção ( '|' conjunção )*
    conjunção   := negação ( '&' negação )*
    negação     := '!' negação | primário
    primário    := VARIÁVEL | CONSTANTE | '(' expressão ')'

Variáveis têm uma única letra de A a Z (minúsculas viram maiúsculas) e as
constantes são 0 e 1. Também são aceitos os sinônimos * + ~ -> <->.
Espaços são ignorados. Qualquer outra entrada gera ExpressaoInvalida, com a
posição do problema e uma mensagem pensada para o aluno.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Set, Tuple

# Operadores canônicos internos
AND, OR, NOT, IMPLIES, IFF = '&', '|', '!', '>', '<>'
CONSTANTES = ('0', '1')

Caminho = Tuple[int, ...]


class ExpressaoInvalida(ValueError):
    """Erro de sintaxe. `posicao` é o índice (a partir de 0) no texto original."""

    def __init__(self, mensagem: str, posicao: Optional[int] = None, expressao: Optional[str] = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.posicao = posicao
        self.expressao = expressao


class Node:
    """
    Classe base. Não instanciar diretamente.

    A igualdade entre nós é ESTRUTURAL: dois nós podem ser iguais sem serem o
    mesmo objeto. Por isso os nós não são hasheáveis. Para rastrear uma
    instância específica (por exemplo, nós ignorados), use id(no) num
    set[int], nunca o próprio nó como chave.
    """
    __slots__ = ('parenteses',)
    __hash__ = None

    def __init__(self):
        # Pares de parênteses que o usuário escreveu em volta deste nó, como
        # (início, fim) no texto original, do mais externo para o mais interno.
        # É metadado de origem: não entra na igualdade e as leis não o copiam.
        self.parenteses: Tuple[Tuple[int, int], ...] = ()


class VariableNode(Node):
    """Variável (uma letra) ou constante ('0' ou '1')."""
    __slots__ = ('name',)

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __eq__(self, other):
        return isinstance(other, VariableNode) and self.name == other.name

    @property
    def eh_constante(self) -> bool:
        return self.name in CONSTANTES

    # ---- ponte de compatibilidade com o código legado (valor/esquerda/direita) ----
    @property
    def valor(self):
        return self.name

    @property
    def esquerda(self):
        return None

    @property
    def direita(self):
        return None

    def __str__(self):
        return to_string(self, style="logic")

    def __repr__(self):
        return f"VariableNode({self.name!r})"


class OperatorNode(Node):
    __slots__ = ('op', 'children')

    def __init__(self, op: str, children: List[Node]):
        super().__init__()
        self.op = op
        self.children = list(children)

    def __eq__(self, other):
        return (isinstance(other, OperatorNode)
                and self.op == other.op
                and self.children == other.children)

    # ---- ponte de compatibilidade com o código legado (esquerda/direita) ----
    @property
    def valor(self):
        return self.op

    @property
    def esquerda(self) -> Optional[Node]:
        return self.children[0] if self.children else None

    @esquerda.setter
    def esquerda(self, value: Node):
        if not self.children:
            self.children = [value]
        else:
            self.children[0] = value

    @property
    def direita(self) -> Optional[Node]:
        return self.children[1] if len(self.children) > 1 else None

    @direita.setter
    def direita(self, value: Node):
        if len(self.children) < 2:
            self.children.append(value)
        else:
            self.children[1] = value

    def __str__(self):
        return to_string(self, style="logic")

    def __repr__(self):
        return f"OperatorNode({self.op!r}, {self.children!r})"


# --------------------------- TOKENIZAÇÃO ---------------------------

@dataclass(frozen=True)
class _Token:
    tipo: str      # 'operando', 'operador', 'abre' ou 'fecha'
    valor: str     # forma canônica: 'A', '1', '&', '|', '!', '>', '<>', '(', ')'
    inicio: int    # posição no texto original
    fim: int

    def texto(self, fonte: str) -> str:
        return fonte[self.inicio:self.fim]


_OPERADORES_DE_1_CARACTERE = {
    '&': AND, '*': AND,
    '|': OR, '+': OR,
    '!': NOT, '~': NOT,
    '>': IMPLIES,
}


def _tokenizar(fonte: str) -> List[_Token]:
    tokens: List[_Token] = []
    i = 0
    while i < len(fonte):
        c = fonte[i]
        if c.isspace():
            i += 1
            continue
        if fonte.startswith('<->', i):
            tokens.append(_Token('operador', IFF, i, i + 3))
            i += 3
        elif fonte.startswith('<>', i):
            tokens.append(_Token('operador', IFF, i, i + 2))
            i += 2
        elif fonte.startswith('->', i):
            tokens.append(_Token('operador', IMPLIES, i, i + 2))
            i += 2
        elif c in _OPERADORES_DE_1_CARACTERE:
            tokens.append(_Token('operador', _OPERADORES_DE_1_CARACTERE[c], i, i + 1))
            i += 1
        elif c == '(':
            tokens.append(_Token('abre', '(', i, i + 1))
            i += 1
        elif c == ')':
            tokens.append(_Token('fecha', ')', i, i + 1))
            i += 1
        elif c.isascii() and c.isalpha():
            tokens.append(_Token('operando', c.upper(), i, i + 1))
            i += 1
        elif c in CONSTANTES:
            tokens.append(_Token('operando', c, i, i + 1))
            i += 1
        elif c.isdigit():
            raise ExpressaoInvalida(
                f"Número '{c}' na posição {i + 1}: só as constantes 0 e 1 são aceitas.", i, fonte)
        elif c == '<':
            raise ExpressaoInvalida(
                f"Operador incompleto na posição {i + 1}: use '<>' (ou '<->') para a bi-implicação.", i, fonte)
        elif c == '-':
            raise ExpressaoInvalida(
                f"Operador incompleto na posição {i + 1}: use '>' (ou '->') para a implicação.", i, fonte)
        elif c.isalpha():
            raise ExpressaoInvalida(
                f"Letra '{c}' na posição {i + 1}: use só letras de A a Z, sem acento.", i, fonte)
        else:
            raise ExpressaoInvalida(f"Caractere inválido '{c}' na posição {i + 1}.", i, fonte)
    return tokens


# --------------------------- PARSER ---------------------------

class _Analisador:
    def __init__(self, fonte: str):
        self.fonte = fonte
        self.tokens = _tokenizar(fonte)
        self.pos = 0

    def _olhar(self) -> Optional[_Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _consumir(self) -> _Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def _erro(self, mensagem: str, posicao: Optional[int]) -> ExpressaoInvalida:
        return ExpressaoInvalida(mensagem, posicao, self.fonte)

    def _eh_operador(self, valor: str) -> bool:
        token = self._olhar()
        return token is not None and token.tipo == 'operador' and token.valor == valor

    def analisar(self) -> Node:
        if not self.tokens:
            raise self._erro("A expressão está vazia.", 0)
        raiz = self._bi_implicacao()
        sobra = self._olhar()
        if sobra is not None:
            if sobra.tipo == 'fecha':
                raise self._erro(
                    f"Parêntese ')' na posição {sobra.inicio + 1} sem abertura correspondente.", sobra.inicio)
            anterior = self.tokens[self.pos - 1]
            a, b = anterior.texto(self.fonte), sobra.texto(self.fonte)
            dica = " (cada variável é uma única letra)" if anterior.tipo == sobra.tipo == 'operando' else ""
            raise self._erro(
                f"Falta um operador entre '{a}' e '{b}' na posição {sobra.inicio + 1}{dica}.", sobra.inicio)
        return raiz

    def _bi_implicacao(self) -> Node:
        no = self._implicacao()
        while self._eh_operador(IFF):
            self._consumir()
            no = OperatorNode(IFF, [no, self._implicacao()])
        return no

    def _implicacao(self) -> Node:
        no = self._disjuncao()
        if self._eh_operador(IMPLIES):
            self._consumir()
            # Recursão à direita: A>B>C vira A>(B>C)
            return OperatorNode(IMPLIES, [no, self._implicacao()])
        return no

    def _disjuncao(self) -> Node:
        no = self._conjuncao()
        while self._eh_operador(OR):
            self._consumir()
            no = OperatorNode(OR, [no, self._conjuncao()])
        return no

    def _conjuncao(self) -> Node:
        no = self._negacao()
        while self._eh_operador(AND):
            self._consumir()
            no = OperatorNode(AND, [no, self._negacao()])
        return no

    def _negacao(self) -> Node:
        if self._eh_operador(NOT):
            self._consumir()
            return OperatorNode(NOT, [self._negacao()])
        return self._primario()

    def _primario(self) -> Node:
        token = self._olhar()
        if token is None:
            raise self._erro("A expressão termina sem o último operando.", len(self.fonte))
        if token.tipo == 'operando':
            self._consumir()
            return VariableNode(token.valor)
        if token.tipo == 'abre':
            abre = self._consumir()
            if self._olhar() is not None and self._olhar().tipo == 'fecha':
                raise self._erro(f"Parênteses vazios na posição {abre.inicio + 1}.", abre.inicio)
            no = self._bi_implicacao()
            fecha = self._olhar()
            if fecha is None or fecha.tipo != 'fecha':
                raise self._erro(
                    f"O parêntese aberto na posição {abre.inicio + 1} não foi fechado.", abre.inicio)
            self._consumir()
            no.parenteses = ((abre.inicio, fecha.fim),) + no.parenteses
            return no
        texto = token.texto(self.fonte)
        raise self._erro(f"Falta um operando antes de '{texto}' na posição {token.inicio + 1}.", token.inicio)


def parse(expressao: str) -> Node:
    """Ponto de entrada único: texto → árvore canônica."""
    if not isinstance(expressao, str):
        raise TypeError("A expressão deve ser uma string.")
    try:
        return _Analisador(expressao).analisar()
    except RecursionError:
        raise ExpressaoInvalida("A expressão tem parênteses ou negações aninhados demais.", None, expressao)


# ----------------------- IMPRESSÃO (compatível com o texto legado) -----------------------

_SIMBOLOS = {
    "logic": {AND: '&', OR: '|', NOT: '!', IMPLIES: '>', IFF: '<>'},
    "boolean": {AND: '*', OR: '+', NOT: '~', IMPLIES: '>', IFF: '<>'},
}


def _imprimir(node: Node, style: str, trechos: Optional[Dict[int, Tuple[int, int]]]) -> str:
    if style not in _SIMBOLOS:
        raise ValueError(f"Estilo de impressão desconhecido: {style}")
    simbolos = _SIMBOLOS[style]

    def visitar(n: Node, base: int) -> str:
        if isinstance(n, VariableNode):
            texto = n.name
        elif n.op == NOT:
            texto = simbolos[NOT]
            texto += visitar(n.children[0], base + len(texto))
        elif n.op in (AND, OR, IMPLIES, IFF):
            texto = "("
            texto += visitar(n.children[0], base + len(texto))
            texto += simbolos[n.op]
            texto += visitar(n.children[1], base + len(texto))
            texto += ")"
        else:
            raise ValueError(f"Operador desconhecido: {n.op}")
        if trechos is not None:
            trechos[id(n)] = (base, base + len(texto))
        return texto

    return visitar(node, 0)


def to_string(node: Node, style: str = "logic") -> str:
    """
    style='logic'   -> usa & | !   (formato de identificar_lei.py)
    style='boolean' -> usa * + ~   (formato de simplificador_interativo.py)
    Toda operação binária sai entre parênteses, então reler o texto
    reproduz exatamente a mesma árvore.
    """
    return _imprimir(node, style, None)


def to_string_com_trechos(node: Node, style: str = "logic") -> Tuple[str, Dict[int, Tuple[int, int]]]:
    """Como to_string, mas também diz onde cada nó aparece: {id(no): (início, fim)}."""
    trechos: Dict[int, Tuple[int, int]] = {}
    return _imprimir(node, style, trechos), trechos


# Precedência na gramática acima (maior = liga mais forte): <> < > < | < & < ! < operando
_PRECEDENCIA = {IFF: 1, IMPLIES: 2, OR: 3, AND: 4, NOT: 5}
_OPERANDO = 6


def _precedencia(no: Node) -> int:
    return _OPERANDO if isinstance(no, VariableNode) else _PRECEDENCIA[no.op]


def _imprimir_minimo(node: Node, style: str, trechos: Optional[Dict[int, Tuple[int, int]]]) -> str:
    if style not in _SIMBOLOS:
        raise ValueError(f"Estilo de impressão desconhecido: {style}")
    simbolos = _SIMBOLOS[style]

    def filho(n: Node, base: int, precisa: bool) -> str:
        """Texto do filho que começa em `base`, entre parênteses só se precisar."""
        if not precisa:
            return visitar(n, base)
        return "(" + visitar(n, base + 1) + ")"

    def visitar(n: Node, base: int) -> str:
        if isinstance(n, VariableNode):
            texto = n.name
        elif n.op == NOT:
            unico = n.children[0]
            texto = simbolos[NOT]
            texto += filho(unico, base + len(texto), _precedencia(unico) < _PRECEDENCIA[NOT])
        elif n.op in (AND, OR, IMPLIES, IFF):
            propria = _PRECEDENCIA[n.op]
            a_direita = n.op == IMPLIES  # a única que associa à direita
            esquerda, direita = n.children
            texto = filho(esquerda, base,
                          _precedencia(esquerda) < propria or (_precedencia(esquerda) == propria and a_direita))
            texto += simbolos[n.op]
            texto += filho(direita, base + len(texto),
                           _precedencia(direita) < propria or (_precedencia(direita) == propria and not a_direita))
        else:
            raise ValueError(f"Operador desconhecido: {n.op}")
        if trechos is not None:
            trechos[id(n)] = (base, base + len(texto))
        return texto

    return visitar(node, 0)


def to_string_minimo(node: Node, style: str = "logic") -> str:
    """
    Como to_string, mas só com os parênteses necessários para reler a MESMA
    árvore; a precedência e a associatividade da gramática decidem o resto.
    "(A+B)*((~C+D))" sai "(A+B)*(~C+D)". Já "A*(B*C)" fica como está: sem os
    parênteses o texto seria lido como (A*B)*C, outra árvore e outro circuito.
    """
    return _imprimir_minimo(node, style, None)


def to_string_minimo_com_trechos(node: Node, style: str = "logic") -> Tuple[str, Dict[int, Tuple[int, int]]]:
    """
    Como to_string_minimo, mas também diz onde cada nó aparece: {id(no): (início, fim)}.
    O trecho de um nó não inclui os parênteses que o pai pôs em volta dele.
    """
    trechos: Dict[int, Tuple[int, int]] = {}
    return _imprimir_minimo(node, style, trechos), trechos


# ----------------------- HELPERS usados em vários módulos -----------------------

def collect_variables(node: Node) -> Set[str]:
    """Nomes das variáveis da árvore. As constantes 0 e 1 não entram."""
    if isinstance(node, VariableNode):
        return set() if node.eh_constante else {node.name}
    return set().union(*(collect_variables(c) for c in node.children))


def tree_size(node: Node) -> int:
    if isinstance(node, VariableNode):
        return 1
    return 1 + sum(tree_size(c) for c in node.children)


def avaliar(node: Node, valores: Dict[str, bool]) -> bool:
    """Valor lógico da árvore. Variável ausente em `valores` conta como falsa."""
    if isinstance(node, VariableNode):
        if node.eh_constante:
            return node.name == '1'
        return valores.get(node.name, False)
    if node.op == NOT:
        return not avaliar(node.children[0], valores)
    a = avaliar(node.children[0], valores)
    b = avaliar(node.children[1], valores)
    if node.op == AND:
        return a and b
    if node.op == OR:
        return a or b
    if node.op == IMPLIES:
        return (not a) or b
    if node.op == IFF:
        return a == b
    raise ValueError(f"Operador desconhecido: {node.op}")


def percorrer(raiz: Node) -> Iterator[Tuple[Caminho, Node]]:
    """Todos os nós em pré-ordem, com o caminho (índices em `children`) de cada um."""
    pilha: List[Tuple[Caminho, Node]] = [((), raiz)]
    while pilha:
        caminho, no = pilha.pop()
        yield caminho, no
        if isinstance(no, OperatorNode):
            for indice in reversed(range(len(no.children))):
                pilha.append((caminho + (indice,), no.children[indice]))


def caminho_ate(raiz: Node, alvo: Node) -> Optional[Caminho]:
    """Caminho até a INSTÂNCIA `alvo` (comparação por identidade), ou None."""
    for caminho, no in percorrer(raiz):
        if no is alvo:
            return caminho
    return None


def no_no_caminho(raiz: Node, caminho: Caminho) -> Node:
    """O nó alcançado seguindo `caminho` a partir da raiz."""
    no = raiz
    for indice in caminho:
        if not isinstance(no, OperatorNode) or not 0 <= indice < len(no.children):
            raise ValueError(f"Caminho inválido na árvore: {list(caminho)}")
        no = no.children[indice]
    return no
