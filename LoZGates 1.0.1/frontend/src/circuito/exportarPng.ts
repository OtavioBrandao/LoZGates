/**
 * "💾 Salvar circuito como PNG": rasteriza o desenho do circuito numa imagem de
 * 1200×800 com fundo preto, enquadrada como plotar_circuito_logico fazia
 * (centro do circuito e zoom = min(1200/largura, 800/altura, 1,5) × 0,8).
 */
import type { LayoutCircuito } from '../api/tipos';

const LARGURA = 1200;
const ALTURA = 800;

export function enquadramento(layout: LayoutCircuito) {
  const { x_min, y_min, x_max, y_max } = layout.limites;
  const largura = Math.max(1, x_max - x_min);
  const altura = Math.max(1, y_max - y_min + 120);
  const zoom = Math.max(0.2, Math.min(3, Math.min(LARGURA / largura, ALTURA / altura, 1.5) * 0.8));
  const centroX = (x_min + x_max) / 2;
  const centroY = (y_min + y_max) / 2;
  return {
    x: centroX - LARGURA / 2 / zoom,
    y: centroY - ALTURA / 2 / zoom,
    largura: LARGURA / zoom,
    altura: ALTURA / zoom,
  };
}

function carregarImagem(url: string): Promise<HTMLImageElement> {
  return new Promise((resolver, rejeitar) => {
    const imagem = new Image();
    imagem.onload = () => resolver(imagem);
    imagem.onerror = () => rejeitar(new Error('não foi possível desenhar o circuito'));
    imagem.src = url;
  });
}

export async function exportarPng(svg: SVGSVGElement, layout: LayoutCircuito, nomeDoArquivo: string): Promise<void> {
  const desenho = svg.querySelector(':scope > g');
  if (!desenho) throw new Error('circuito vazio');
  const caixa = enquadramento(layout);
  const fonte =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${LARGURA}" height="${ALTURA}" ` +
    `viewBox="${caixa.x} ${caixa.y} ${caixa.largura} ${caixa.altura}">` +
    `<rect x="${caixa.x}" y="${caixa.y}" width="${caixa.largura}" height="${caixa.altura}" fill="#000000"/>` +
    `${desenho.outerHTML}</svg>`;

  const url = URL.createObjectURL(new Blob([fonte], { type: 'image/svg+xml;charset=utf-8' }));
  try {
    const imagem = await carregarImagem(url);
    const canvas = document.createElement('canvas');
    canvas.width = LARGURA;
    canvas.height = ALTURA;
    const contexto = canvas.getContext('2d');
    if (!contexto) throw new Error('o navegador não permite desenhar a imagem');
    contexto.drawImage(imagem, 0, 0, LARGURA, ALTURA);
    const png = await new Promise<Blob>((resolver, rejeitar) =>
      canvas.toBlob((blob) => (blob ? resolver(blob) : rejeitar(new Error('falha ao gerar o PNG'))), 'image/png'),
    );
    const link = document.createElement('a');
    link.href = URL.createObjectURL(png);
    link.download = nomeDoArquivo;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(link.href), 10_000);
  } finally {
    URL.revokeObjectURL(url);
  }
}
