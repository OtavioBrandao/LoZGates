import { describe, expect, it } from 'vitest';
import type { Barramento, LayoutCircuito } from '../api/tipos';
import { calcularPropagacao, comprimento, DURACAO_DO_TRECHO } from './propagacao';

const barramento = (id: string, x: number, valor: boolean): Barramento => ({
  id,
  rotulo: id,
  x,
  tipo: id.startsWith('~') ? 'negado' : 'variavel',
  valor,
  y_inicio: 40,
  y_fim: 400,
  y_rotulo: 25,
});

/** (A*B)+C desenhado como o layout.py devolve: E em p1, OU em p0 (a raiz). */
function layout(A: boolean, B: boolean, C: boolean): LayoutCircuito {
  const e = A && B;
  const s = e || C;
  return {
    expressao: '(A&B)|C',
    expressao_booleana: 'A*B+C',
    variaveis: ['A', 'B', 'C'],
    barramentos: [
      barramento('A', 100, A),
      barramento('~A', 140, !A),
      barramento('B', 200, B),
      barramento('~B', 240, !B),
      barramento('C', 300, C),
      barramento('~C', 340, !C),
    ],
    portas: [
      { id: 'p0', tipo: 'OR', x: 850, y: 200, largura: 40, altura: 80, entradas: [[850, 215], [850, 265]], saida: [890, 240], subexpressao: 'A*B+C', caminho: [], valor: s },
      { id: 'p1', tipo: 'AND', x: 670, y: 150, largura: 40, altura: 80, entradas: [[670, 165], [670, 215]], saida: [710, 190], subexpressao: 'A*B', caminho: [0], valor: e },
    ],
    fios: [
      { id: 'f0', origem: { tipo: 'barramento', id: 'A' }, destino: { porta: 'p1', entrada: 0 }, pontos: [[100, 140], [670, 140], [670, 165]], valor: A },
      { id: 'f1', origem: { tipo: 'barramento', id: 'B' }, destino: { porta: 'p1', entrada: 1 }, pontos: [[200, 215], [670, 215]], valor: B },
      { id: 'f2', origem: { tipo: 'porta', id: 'p1' }, destino: { porta: 'p0', entrada: 0 }, pontos: [[710, 190], [780, 190], [780, 215], [850, 215]], valor: e },
      { id: 'f3', origem: { tipo: 'barramento', id: 'C' }, destino: { porta: 'p0', entrada: 1 }, pontos: [[300, 265], [850, 265]], valor: C },
    ],
    conexoes: [],
    saida: { de: [890, 240], ate: [970, 240], rotulo: [1010, 240], valor: s },
    valor: s,
    limites: { x_min: 70, y_min: 10, x_max: 1040, y_max: 400 },
  };
}

const resumo = (p: ReturnType<typeof calcularPropagacao>) =>
  p?.trechos.map((t) => `${t.id}:${t.sobe ? 'acende' : 'apaga'}@${t.ordem}`).sort();

describe('propagação do sinal', () => {
  it('ligar A com B=1 acende o caminho todo, na ordem em que o sinal passa, até o LED', () => {
    const p = calcularPropagacao(layout(false, true, false), layout(true, true, false));
    expect(resumo(p)).toEqual(['barramento:A:acende@0', 'barramento:~A:apaga@0', 'f0:acende@1', 'f2:acende@2', 'saida:acende@3'].sort());
    expect(p?.led).toEqual({ acende: true, ordem: 4 });
    expect(p?.duracao).toBe(5 * DURACAO_DO_TRECHO);
    // enquanto o sinal não chega, o que vai acender continua apagado
    expect([...(p?.sobem ?? [])].sort()).toEqual(['barramento:A', 'f0', 'f2', 'saida']);
  });

  it('com B=0 a porta E não muda: o sinal para nela e o LED fica como estava', () => {
    const p = calcularPropagacao(layout(false, false, false), layout(true, false, false));
    expect(resumo(p)).toEqual(['barramento:A:acende@0', 'barramento:~A:apaga@0', 'f0:acende@1'].sort());
    expect(p?.led).toBeNull();
  });

  it('desligar C apaga o fio e o LED', () => {
    const p = calcularPropagacao(layout(false, false, true), layout(false, false, false));
    expect(resumo(p)).toEqual(['barramento:C:apaga@0', 'barramento:~C:acende@0', 'f3:apaga@1', 'saida:apaga@2'].sort());
    expect(p?.led).toEqual({ acende: false, ordem: 3 });
  });

  it('nada muda, ou o circuito é outro: sem propagação', () => {
    expect(calcularPropagacao(layout(true, true, false), layout(true, true, false))).toBeNull();
    const outro = { ...layout(true, true, false), expressao_booleana: 'A*B' };
    expect(calcularPropagacao(layout(false, true, false), outro)).toBeNull();
  });

  it('mede o comprimento dos fios em L', () => {
    expect(comprimento([[0, 0], [30, 0], [30, 40]])).toBe(70);
  });
});
