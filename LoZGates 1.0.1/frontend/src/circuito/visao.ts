/**
 * Zoom do circuito por tamanho: o desenho tem `escala` pixels por unidade do
 * layout e fica numa área que rola (barras do navegador, dedo, roda do mouse).
 * A escala inicial faz o circuito caber na largura, mas nunca fica abaixo da
 * escala legível: no celular o circuito abre legível, com rolagem lateral.
 */
export interface Janela {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface Ponto {
  x: number;
  y: number;
}

export interface Tamanho {
  largura: number;
  altura: number;
}

/** Abaixo disso os rótulos (24 unidades) ficam menores que ~14 px. */
export const ESCALA_LEGIVEL = 0.6;
/** Circuitos pequenos não viram um desenho gigante. */
export const ESCALA_MAXIMA_INICIAL = 1.2;
/** Zoom máximo, em relação à escala inicial. */
export const ZOOM_MAXIMO = 4;

/** Escala em que o circuito inteiro cabe na área. */
export function escalaQueCabe(base: Janela, area: Tamanho): number {
  return Math.min(area.largura / base.w, area.altura / base.h);
}

/** Escala com que o circuito abre (o "100%"). */
export function escalaInicial(base: Janela, largura: number, alturaMaxima: number): number {
  const cabe = escalaQueCabe(base, { largura, altura: alturaMaxima });
  return Math.min(ESCALA_MAXIMA_INICIAL, Math.max(ESCALA_LEGIVEL, cabe));
}

export function limitarEscala(escala: number, minima: number, maxima: number): number {
  return Math.min(maxima, Math.max(minima, escala));
}

/** Onde o desenho começa dentro da área: centralizado quando é menor que ela. */
export function deslocamentoDoDesenho(base: Janela, area: Tamanho, escala: number): Ponto {
  return {
    x: Math.max(0, (area.largura - base.w * escala) / 2),
    y: Math.max(0, (area.altura - base.h * escala) / 2),
  };
}

/**
 * Rolagem que mantém parado o ponto da área sob o cursor (ou o centro dos dois
 * dedos) quando a escala muda. `ponto` é relativo ao canto visível da área.
 */
export function rolagemAncorada(
  base: Janela,
  area: Tamanho,
  rolagem: Ponto,
  ponto: Ponto,
  escalaAntes: number,
  escalaDepois: number,
): Ponto {
  const antes = deslocamentoDoDesenho(base, area, escalaAntes);
  const depois = deslocamentoDoDesenho(base, area, escalaDepois);
  const mundoX = (rolagem.x + ponto.x - antes.x) / escalaAntes;
  const mundoY = (rolagem.y + ponto.y - antes.y) / escalaAntes;
  return {
    x: mundoX * escalaDepois + depois.x - ponto.x,
    y: mundoY * escalaDepois + depois.y - ponto.y,
  };
}
