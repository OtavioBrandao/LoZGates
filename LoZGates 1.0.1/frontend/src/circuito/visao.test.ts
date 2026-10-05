import { describe, expect, it } from 'vitest';
import { deslocamentoDoDesenho, ESCALA_LEGIVEL, ESCALA_MAXIMA_INICIAL, escalaInicial, escalaQueCabe, rolagemAncorada } from './visao';

// O circuito de (A&B)>C: largo e baixo, como quase todos
const BASE = { x: 64, y: -15, w: 1150, h: 430 };

describe('escala inicial', () => {
  it('no computador, o circuito cabe na largura do painel', () => {
    const escala = escalaInicial(BASE, 860, 600);
    expect(escala).toBeCloseTo(860 / 1150);
    expect(BASE.w * escala).toBeCloseTo(860);
  });

  it('no celular, nunca fica abaixo da escala legível: o desenho passa da largura e rola para o lado', () => {
    const escala = escalaInicial(BASE, 300, 470);
    expect(escala).toBe(ESCALA_LEGIVEL);
    expect(BASE.w * escala).toBeGreaterThan(300);
  });

  it('um circuito pequeno não vira um desenho gigante', () => {
    expect(escalaInicial({ x: 0, y: 0, w: 300, h: 200 }, 1800, 900)).toBe(ESCALA_MAXIMA_INICIAL);
  });

  it('"ver inteiro" cabe nas duas direções', () => {
    const escala = escalaQueCabe(BASE, { largura: 300, altura: 258 });
    expect(BASE.w * escala).toBeLessThanOrEqual(300 + 1e-9);
    expect(BASE.h * escala).toBeLessThanOrEqual(258 + 1e-9);
  });
});

describe('zoom ancorado', () => {
  const area = { largura: 300, altura: 258 };

  it('o ponto sob os dedos fica parado ao aproximar', () => {
    const rolagem = { x: 120, y: 0 };
    const ponto = { x: 90, y: 100 };
    const nova = rolagemAncorada(BASE, area, rolagem, ponto, 0.6, 1.2);
    // mesma coordenada do circuito antes e depois, medida a partir do canto visível
    const mundoAntes = (rolagem.x + ponto.x - deslocamentoDoDesenho(BASE, area, 0.6).x) / 0.6;
    const mundoDepois = (nova.x + ponto.x - deslocamentoDoDesenho(BASE, area, 1.2).x) / 1.2;
    expect(mundoDepois).toBeCloseTo(mundoAntes);
    expect((nova.y + ponto.y) / 1.2).toBeCloseTo((rolagem.y + ponto.y) / 0.6);
  });

  it('afastando além da área, o desenho fica centralizado', () => {
    const escala = escalaQueCabe(BASE, area) / 2;
    const deslocamento = deslocamentoDoDesenho(BASE, area, escala);
    expect(deslocamento.x).toBeCloseTo((area.largura - BASE.w * escala) / 2);
    expect(deslocamento.x).toBeGreaterThan(0);
  });
});
