import { describe, expect, it } from 'vitest';
import type { TabelaVerdade } from '../api/tipos';
import { compararTabelas } from './comparacao';

/** Tabela como o servidor devolve: as primeiras colunas são as variáveis, em ordem alfabética. */
function tabela(variaveis: string[], resultados: number[]): TabelaVerdade {
  return {
    colunas: [...variaveis, 'S'],
    tabela: resultados.map((r, i) => [...variaveis.map((_, j) => (i >> (variaveis.length - 1 - j)) & 1), r]),
    resultados_finais: resultados,
    total_combinacoes: resultados.length,
    total_variaveis: variaveis.length,
    conclusao: '',
    tipo_conclusao: null,
  };
}

describe('comparação de tabelas-verdade', () => {
  it('A>B e !A|B coincidem em todas as linhas', () => {
    const c = compararTabelas(['A', 'B'], tabela(['A', 'B'], [1, 1, 0, 1]), tabela(['A', 'B'], [1, 1, 0, 1]));
    expect(c.diferentes).toBe(0);
    expect(c.linhas.map((l) => l.valores.join(''))).toEqual(['00', '01', '10', '11']);
  });

  it('A&B e A|B diferem quando só uma das entradas é 1', () => {
    const c = compararTabelas(['A', 'B'], tabela(['A', 'B'], [0, 0, 0, 1]), tabela(['A', 'B'], [0, 1, 1, 1]));
    expect(c.linhas.filter((l) => !l.iguais).map((l) => l.valores.join(''))).toEqual(['01', '10']);
  });

  it('variáveis diferentes: cada expressão é lida nas suas próprias colunas', () => {
    // A&B contra X&Y: as variáveis juntas são A, B, X, Y
    const c = compararTabelas(['A', 'B', 'X', 'Y'], tabela(['A', 'B'], [0, 0, 0, 1]), tabela(['X', 'Y'], [0, 0, 0, 1]));
    const linha = (valores: string) => c.linhas.find((l) => l.valores.join('') === valores)!;
    expect(linha('1100')).toMatchObject({ primeira: 1, segunda: 0, iguais: false });
    expect(linha('0011')).toMatchObject({ primeira: 0, segunda: 1, iguais: false });
    expect(linha('1111')).toMatchObject({ primeira: 1, segunda: 1, iguais: true });
    expect(c.diferentes).toBe(6);
  });

  it('expressão constante (sem variáveis) vale o mesmo em toda linha', () => {
    const c = compararTabelas(['A'], tabela(['A'], [0, 1]), tabela([], [1]));
    expect(c.linhas.map((l) => `${l.primeira}${l.segunda}`)).toEqual(['01', '11']);
  });
});
