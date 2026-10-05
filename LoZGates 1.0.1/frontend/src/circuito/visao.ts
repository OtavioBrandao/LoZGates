/**
 * Zoom e deslocamento do circuito, como uma "janela" (viewBox) sobre as
 * coordenadas do mundo que o servidor calculou.
 */
export interface Janela {
  x: number;
  y: number;
  w: number;
  h: number;
}

export const ZOOM_MINIMO = 0.5;
export const ZOOM_MAXIMO = 6;

/** Nível de zoom em relação ao enquadramento inteiro (1 = circuito todo visível). */
export const nivelDeZoom = (base: Janela, janela: Janela) => base.w / janela.w;

/** Aproxima (fator > 1) ou afasta mantendo parado o ponto (px, py) do mundo. */
export function zoomEm(base: Janela, janela: Janela, fator: number, px: number, py: number): Janela {
  const nivel = Math.min(ZOOM_MAXIMO, Math.max(ZOOM_MINIMO, nivelDeZoom(base, janela) * fator));
  const real = nivel / nivelDeZoom(base, janela);
  const w = janela.w / real;
  const h = janela.h / real;
  return { x: px - (px - janela.x) / real, y: py - (py - janela.y) / real, w, h };
}

/** Zoom pelo centro da janela (botões + e −). */
export function zoomNoCentro(base: Janela, janela: Janela, fator: number): Janela {
  return zoomEm(base, janela, fator, janela.x + janela.w / 2, janela.y + janela.h / 2);
}

/** Desloca a janela em unidades do mundo, sem deixar o circuito sumir de vista. */
export function deslocar(base: Janela, janela: Janela, dx: number, dy: number): Janela {
  const folgaX = Math.max(base.w, janela.w) * 0.75;
  const folgaY = Math.max(base.h, janela.h) * 0.75;
  const x = Math.min(base.x + base.w - janela.w + folgaX, Math.max(base.x - folgaX, janela.x + dx));
  const y = Math.min(base.y + base.h - janela.h + folgaY, Math.max(base.y - folgaY, janela.y + dy));
  return { ...janela, x, y };
}
