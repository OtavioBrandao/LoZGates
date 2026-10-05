import { describe, expect, it } from 'vitest';
import { combinacaoDoIndice, indiceDaCombinacao, montarDiagrama } from './diagrama';

// Tabela-verdade de A&B>C como o servidor devolve (variáveis primeiro, linhas em ordem binária)
const TABELA = [
  [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
  [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1],
];
const S = [1, 1, 1, 1, 1, 1, 0, 1];

describe('diagrama de tempo', () => {
  const d = montarDiagrama(['A', 'B', 'C'], TABELA, S);

  it('tem uma onda por variável e uma para a saída', () => {
    expect(d.linhas.map((l) => l.nome)).toEqual(['A', 'B', 'C', 'S']);
    expect(d.linhas[3].saida).toBe(true);
    expect(d.rotulos.map((r) => r.texto)).toEqual(['000', '001', '010', '011', '100', '101', '110', '111']);
  });

  it('desenha a onda de A: quatro fatias em 0 e quatro em 1', () => {
    const a = d.linhas[0];
    const fatia = d.larguraFatia;
    expect(a.niveis).toEqual([0, 0, 0, 0, 1, 1, 1, 1]);
    expect(a.altos).toEqual([{ x: d.inicioX + 4 * fatia, largura: 4 * fatia }]);
    // começa em 0 (embaixo), sobe uma vez e termina em 1 (em cima)
    expect(a.onda.startsWith(`M${d.inicioX} ${a.topo + 26}`)).toBe(true);
    const niveis = [...a.onda.matchAll(/V(\d+)/g)].map((m) => Number(m[1]));
    expect(niveis.filter((y, i) => i > 0 && y !== niveis[i - 1])).toEqual([a.topo + 6]);
    expect(a.onda.endsWith(`H${d.inicioX + 8 * fatia}`)).toBe(true);
  });

  it('junta trechos seguidos em 1 e separa os que têm um 0 no meio', () => {
    const s = d.linhas[3];
    expect(s.altos).toHaveLength(2);
    expect(s.altos[0].largura).toBe(6 * d.larguraFatia);
    expect(s.altos[1].largura).toBe(d.larguraFatia);
  });

  it('estica as fatias para ocupar a largura disponível, sem passar do limite nem do mínimo', () => {
    const minima = d.larguraFatia;
    const esticado = montarDiagrama(['A', 'B', 'C'], TABELA, S, 600);
    expect(esticado.larguraFatia).toBe(68);
    expect(esticado.largura).toBeLessThanOrEqual(600);
    expect(montarDiagrama(['A', 'B', 'C'], TABELA, S, 5000).larguraFatia).toBe(96);
    expect(montarDiagrama(['A', 'B', 'C'], TABELA, S, 200).larguraFatia).toBe(minima);
  });

  it('converte entre valores e linha da tabela', () => {
    expect(indiceDaCombinacao(['A', 'B', 'C'], { A: true, B: true, C: false })).toBe(6);
    expect(combinacaoDoIndice(['A', 'B', 'C'], 5)).toEqual({ A: true, B: false, C: true });
    for (let i = 0; i < 8; i += 1) expect(indiceDaCombinacao(['A', 'B', 'C'], combinacaoDoIndice(['A', 'B', 'C'], i))).toBe(i);
  });
});
