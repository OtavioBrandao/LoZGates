/**
 * "Salvar circuito como PNG": rasteriza o circuito inteiro (o enquadramento
 * completo, não o zoom atual) com as cores do tema que está na tela.
 *
 * O SVG da tela pinta tudo por CSS (classes e variáveis do tema); uma imagem
 * isolada não enxerga esse CSS, então copiamos para cada elemento as
 * propriedades de pintura já calculadas pelo navegador.
 */
const PROPRIEDADES = [
  'fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-opacity', 'stroke-dasharray', 'stroke-linejoin',
  'stroke-linecap', 'opacity', 'font-family', 'font-size', 'font-weight', 'text-anchor', 'dominant-baseline', 'filter',
];
const ESCALA = 2;
const LADO_MAXIMO = 4000;

function copiarPintura(original: Element, copia: Element) {
  const estilo = getComputedStyle(original);
  const declaracoes = PROPRIEDADES.map((p) => `${p}:${estilo.getPropertyValue(p)}`).join(';');
  copia.setAttribute('style', declaracoes);
  copia.removeAttribute('class');
  for (let i = 0; i < original.children.length; i += 1) copiarPintura(original.children[i], copia.children[i]);
}

function carregarImagem(url: string): Promise<HTMLImageElement> {
  return new Promise((resolver, rejeitar) => {
    const imagem = new Image();
    imagem.onload = () => resolver(imagem);
    imagem.onerror = () => rejeitar(new Error('não foi possível desenhar o circuito'));
    imagem.src = url;
  });
}

export async function exportarPng(svg: SVGSVGElement, nomeDoArquivo: string): Promise<void> {
  const desenho = svg.querySelector('.circuito-vivo__desenho');
  if (!desenho) throw new Error('circuito vazio');
  const caixa = (desenho as SVGGraphicsElement).getBBox();
  const margem = 24;
  const x = caixa.x - margem;
  const y = caixa.y - margem;
  const w = caixa.width + 2 * margem;
  const h = caixa.height + 2 * margem;
  const escala = Math.min(ESCALA, LADO_MAXIMO / Math.max(w, h));
  const largura = Math.round(w * escala);
  const altura = Math.round(h * escala);

  // Transições em andamento (um fio que acabou de mudar de nível, o destaque de uma porta
  // que acabou de perder o mouse) vão direto para o estado final antes de lermos as cores
  for (const animacao of svg.getAnimations({ subtree: true })) {
    try {
      animacao.finish();
    } catch {
      /* animação infinita: não há estado final */
    }
  }
  const copia = desenho.cloneNode(true) as Element;
  copiarPintura(desenho, copia);
  const fundo = getComputedStyle(document.documentElement).getPropertyValue('--painel').trim() || '#ffffff';
  const fonte =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${largura}" height="${altura}" viewBox="${x} ${y} ${w} ${h}">` +
    `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fundo}"/>${new XMLSerializer().serializeToString(copia)}</svg>`;

  const url = URL.createObjectURL(new Blob([fonte], { type: 'image/svg+xml;charset=utf-8' }));
  try {
    const imagem = await carregarImagem(url);
    const canvas = document.createElement('canvas');
    canvas.width = largura;
    canvas.height = altura;
    const contexto = canvas.getContext('2d');
    if (!contexto) throw new Error('o navegador não permite desenhar a imagem');
    contexto.drawImage(imagem, 0, 0, largura, altura);
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
