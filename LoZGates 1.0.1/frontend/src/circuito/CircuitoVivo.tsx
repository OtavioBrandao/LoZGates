import {
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
  type PointerEvent,
  type ReactNode,
  type Ref,
} from 'react';
import { flushSync } from 'react-dom';
import type { LayoutCircuito, PortaDoLayout } from '../api/tipos';
import { calcularPropagacao, DURACAO_DO_TRECHO, EVENTO_ESTADO_FINAL, movimentoReduzido, type Propagacao } from './propagacao';
import { escalaInicial, escalaQueCabe, limitarEscala, rolagemAncorada, ZOOM_MAXIMO, type Janela, type Ponto } from './visao';

const MARGEM = 16;
const PASSO_DO_ZOOM = 1.25;
/** Borda da área (1 px de cada lado): o desenho a 100% cabe por dentro dela. */
const BORDA = 2;

const nivel = (v: boolean | null) => (v === null ? 'indefinido' : v ? '1' : '0');
const NOMES_DAS_PORTAS: Record<string, string> = { AND: 'E (AND)', OR: 'OU (OR)', NOT: 'NÃO (NOT)' };

/** Retângulo do que é de fato desenhado (rótulos, portas, LED e o "S"), com uma margem pequena. */
export function enquadramento(layout: LayoutCircuito): Janela {
  const xs: number[] = [];
  const ys: number[] = [];
  const incluir = (x: number, y: number) => {
    xs.push(x);
    ys.push(y);
  };
  for (const b of layout.barramentos) {
    incluir(b.x - 18, b.y_rotulo - 28); // nome em cima (24 u)
    incluir(b.x + 18, b.y_fim);
  }
  for (const p of layout.portas) {
    incluir(p.x - 8, p.y);
    incluir(p.x + 48, p.y + 80); // a bolinha do NÃO passa da largura útil
  }
  for (const f of layout.fios) for (const [x, y] of f.pontos) incluir(x, y);
  if (layout.saida) {
    const [x, y] = layout.saida.ate;
    incluir(layout.saida.de[0], layout.saida.de[1]);
    incluir(x + 34, y - 16); // LED
    incluir(x + 34, y + 46); // "S" embaixo do LED
  }
  if (!xs.length) {
    const { x_min, y_min, x_max, y_max } = layout.limites;
    incluir(x_min, y_min);
    incluir(x_max, y_max);
  }
  const x = Math.min(...xs) - MARGEM;
  const y = Math.min(...ys) - MARGEM;
  return { x, y, w: Math.max(...xs) + MARGEM - x, h: Math.max(...ys) + MARGEM - y };
}

/** Formas ANSI das portas, nas medidas do desenho original (largura útil 40, altura 80). */
function caminhoDaPorta(porta: PortaDoLayout): { corpo: string; bolha?: [number, number] } {
  const { x, y } = porta;
  if (porta.tipo === 'AND') return { corpo: `M${x} ${y} H${x + 20} A20 40 0 0 1 ${x + 20} ${y + 80} H${x} Z` };
  if (porta.tipo === 'OR') {
    return { corpo: `M${x - 7.5} ${y} H${x + 20} A20 40 0 0 1 ${x + 20} ${y + 80} H${x - 7.5} A10 40 0 0 0 ${x - 7.5} ${y} Z` };
  }
  return { corpo: `M${x} ${y + 15} L${x} ${y + 65} L${x + 30} ${y + 40} Z`, bolha: [x + 38, y + 40] };
}

const pontosSvg = (pontos: [number, number][]) => pontos.map(([x, y]) => `${x},${y}`).join(' ');

interface Dica {
  porta: PortaDoLayout;
  esquerda: number;
  topo: number;
}

interface Props {
  layout: LayoutCircuito;
  rotulo: string;
  ref?: Ref<SVGSVGElement>;
  /** Título da figura, à esquerda das ferramentas de zoom */
  titulo?: ReactNode;
  /** Botões extras, à direita das ferramentas de zoom */
  acoes?: ReactNode;
  /** Logo abaixo do desenho (as entradas, nas telas estreitas) */
  abaixo?: ReactNode;
}

/**
 * O circuito da expressão em SVG, com os sinais atuais: fios em 1 acendem e,
 * quando uma entrada muda, o novo nível percorre o circuito até o LED.
 * O desenho abre numa escala legível e a área rola; Ctrl + roda, a pinça e os
 * botões aproximam; apontar uma porta (mouse ou teclado) mostra o que ela calcula.
 */
export function CircuitoVivo({ layout, rotulo, ref, titulo, acoes, abaixo }: Props) {
  // Trocar só os valores das entradas mantém o desenho: o zoom do aluno continua
  const chaveDoDesenho = `${layout.expressao_booleana}|${JSON.stringify(layout.limites)}`;
  const base = useMemo(() => enquadramento(layout), [chaveDoDesenho]);
  const moldura = useRef<HTMLDivElement>(null);
  const area = useRef<HTMLDivElement>(null);
  const svg = useRef<SVGSVGElement | null>(null);
  const [largura, setLargura] = useState(0);
  const [alturaDaJanela, setAlturaDaJanela] = useState(() => (typeof window === 'undefined' ? 800 : window.innerHeight));
  const [escalaEscolhida, setEscalaEscolhida] = useState<number | null>(null); // null = 100%
  const [ativa, setAtiva] = useState<string | null>(null);
  const [dica, setDica] = useState<Dica | null>(null);
  const [propagacao, setPropagacao] = useState<(Propagacao & { onda: number }) | null>(null);
  const layoutAnterior = useRef<LayoutCircuito | null>(null);
  const idGrade = useId().replace(/:/g, '');

  // Largura disponível medida antes de pintar (sem "pulo" na primeira tela)
  useLayoutEffect(() => {
    const elemento = moldura.current;
    if (!elemento) return;
    setLargura(elemento.clientWidth);
    const observador = new ResizeObserver(([entrada]) => setLargura(Math.floor(entrada.contentRect.width)));
    observador.observe(elemento);
    return () => observador.disconnect();
  }, []);

  useEffect(() => {
    const aoRedimensionar = () => setAlturaDaJanela(window.innerHeight);
    window.addEventListener('resize', aoRedimensionar);
    return () => window.removeEventListener('resize', aoRedimensionar);
  }, []);

  // Outro circuito: volta aos 100%
  useEffect(() => setEscalaEscolhida(null), [base]);

  // O novo nível percorre o circuito (antes de pintar, para não piscar o estado final)
  useLayoutEffect(() => {
    const antes = layoutAnterior.current;
    layoutAnterior.current = layout;
    const nova = antes && !movimentoReduzido() ? calcularPropagacao(antes, layout) : null;
    setPropagacao(nova ? { ...nova, onda: Date.now() } : null);
    if (!nova) return;
    const relogio = window.setTimeout(() => setPropagacao(null), nova.duracao + 80);
    return () => window.clearTimeout(relogio);
  }, [layout]);

  // Exportar PNG pede o desenho já no estado final
  useEffect(() => {
    const elemento = svg.current;
    if (!elemento) return;
    const finalizar = () => flushSync(() => setPropagacao(null));
    elemento.addEventListener(EVENTO_ESTADO_FINAL, finalizar);
    return () => elemento.removeEventListener(EVENTO_ESTADO_FINAL, finalizar);
  }, []);

  const alturaMaxima = Math.max(200, alturaDaJanela * 0.6);
  const larguraUtil = Math.max(0, largura - BORDA);
  const inicial = larguraUtil > 0 ? escalaInicial(base, larguraUtil, alturaMaxima) : 0;
  const alturaDaArea = Math.ceil(Math.min(base.h * inicial, alturaMaxima));
  const minima = Math.min(inicial, escalaQueCabe(base, { largura: larguraUtil, altura: alturaDaArea }));
  const maxima = inicial * ZOOM_MAXIMO;
  const escala = inicial > 0 ? limitarEscala(escalaEscolhida ?? inicial, minima, maxima) : 0;
  const zoom = inicial > 0 ? Math.round((escala / inicial) * 100) : 100;

  // Valores atuais para os ouvintes nativos (roda do mouse)
  const atual = useRef({ base, escala, minima, maxima });
  atual.current = { base, escala, minima, maxima };

  /** Troca a escala mantendo parado o ponto indicado da área (o centro, se nenhum). */
  const aplicarEscala = useCallback((nova: number, ponto?: Ponto) => {
    const elemento = area.current;
    const { base: b, escala: antes, minima: min, maxima: max } = atual.current;
    if (!elemento || antes <= 0) return;
    const depois = limitarEscala(nova, min, max);
    if (Math.abs(depois - antes) < 1e-6) return;
    const tamanho = { largura: elemento.clientWidth, altura: elemento.clientHeight };
    const alvo = ponto ?? { x: tamanho.largura / 2, y: tamanho.altura / 2 };
    const rolagem = rolagemAncorada(b, tamanho, { x: elemento.scrollLeft, y: elemento.scrollTop }, alvo, antes, depois);
    flushSync(() => setEscalaEscolhida(depois));
    elemento.scrollLeft = rolagem.x;
    elemento.scrollTop = rolagem.y;
  }, []);

  // Ctrl/⌘ + roda aproxima no cursor; a roda sozinha rola a área (ou a página)
  useEffect(() => {
    const elemento = area.current;
    if (!elemento) return;
    const aoRolar = (e: WheelEvent) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const caixa = elemento.getBoundingClientRect();
      aplicarEscala(atual.current.escala * Math.exp(-e.deltaY * 0.0018), { x: e.clientX - caixa.left, y: e.clientY - caixa.top });
    };
    elemento.addEventListener('wheel', aoRolar, { passive: false });
    return () => elemento.removeEventListener('wheel', aoRolar);
  }, [aplicarEscala]);

  // Mouse arrasta a área; no toque a rolagem é do navegador e só a pinça é nossa
  const arrasto = useRef<Ponto | null>(null);
  const dedos = useRef(new Map<number, Ponto>());
  const pinca = useRef<{ distancia: number; escala: number } | null>(null);

  const aoPressionar = (e: PointerEvent<HTMLDivElement>) => {
    if (e.pointerType === 'mouse') {
      if (e.button !== 0 || (e.target as Element).closest('.porta-viva')) return;
      arrasto.current = { x: e.clientX, y: e.clientY };
      e.currentTarget.setPointerCapture(e.pointerId);
      return;
    }
    dedos.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (dedos.current.size === 2) {
      const [a, b] = [...dedos.current.values()];
      pinca.current = { distancia: Math.hypot(a.x - b.x, a.y - b.y), escala: atual.current.escala };
    }
  };

  const aoMover = (e: PointerEvent<HTMLDivElement>) => {
    const elemento = area.current;
    if (!elemento) return;
    if (e.pointerType === 'mouse') {
      const inicio = arrasto.current;
      if (!inicio) return;
      elemento.scrollLeft -= e.clientX - inicio.x;
      elemento.scrollTop -= e.clientY - inicio.y;
      arrasto.current = { x: e.clientX, y: e.clientY };
      return;
    }
    if (!dedos.current.has(e.pointerId)) return;
    dedos.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    const comeco = pinca.current;
    if (!comeco || dedos.current.size !== 2 || comeco.distancia <= 0) return;
    const [a, b] = [...dedos.current.values()];
    const caixa = elemento.getBoundingClientRect();
    const meio = { x: (a.x + b.x) / 2 - caixa.left, y: (a.y + b.y) / 2 - caixa.top };
    aplicarEscala((comeco.escala * Math.hypot(a.x - b.x, a.y - b.y)) / comeco.distancia, meio);
  };

  const aoSoltar = (e: PointerEvent<HTMLDivElement>) => {
    if (e.pointerType === 'mouse') arrasto.current = null;
    dedos.current.delete(e.pointerId);
    if (dedos.current.size < 2) pinca.current = null;
  };

  const aoTeclar = (e: KeyboardEvent<HTMLDivElement>) => {
    const acoes: Record<string, () => void> = {
      '+': () => aplicarEscala(escala * PASSO_DO_ZOOM),
      '=': () => aplicarEscala(escala * PASSO_DO_ZOOM),
      '-': () => aplicarEscala(escala / PASSO_DO_ZOOM),
      '0': () => aplicarEscala(inicial),
    };
    const acao = acoes[e.key];
    if (!acao || e.target !== e.currentTarget) return; // as setas rolam a área (navegador)
    e.preventDefault();
    acao();
  };

  const mostrarDica = (porta: PortaDoLayout, elemento: Element) => {
    const caixa = elemento.getBoundingClientRect();
    const quadro = moldura.current?.getBoundingClientRect();
    if (!quadro) return;
    setAtiva(porta.id);
    setDica({ porta, esquerda: caixa.left - quadro.left + caixa.width / 2, topo: caixa.top - quadro.top });
  };

  const esconderDica = () => {
    setAtiva(null);
    setDica(null);
  };

  // Fios ligados à porta em destaque (entradas e saída)
  const fiosAtivos = useMemo(() => {
    if (!ativa) return new Set<string>();
    return new Set(layout.fios.filter((f) => f.destino.porta === ativa || (f.origem.tipo === 'porta' && f.origem.id === ativa)).map((f) => f.id));
  }, [ativa, layout.fios]);
  const raiz = layout.portas[0]?.id;

  // Enquanto o sinal não chega, o trecho que vai acender continua apagado
  const exibido = (id: string, valor: boolean | null) => (propagacao?.sobem.has(id) ? false : valor);
  const estiloDoTrecho = (comprimento: number, ordem: number) =>
    ({ '--comprimento': comprimento, '--atraso': `${ordem * DURACAO_DO_TRECHO}ms`, '--duracao': `${DURACAO_DO_TRECHO}ms` }) as CSSProperties;

  const ligarSvg = (elemento: SVGSVGElement | null) => {
    svg.current = elemento;
    if (typeof ref === 'function') ref(elemento);
    else if (ref) (ref as { current: SVGSVGElement | null }).current = elemento;
  };

  const led = layout.saida && propagacao?.led;
  const classeDoLed = led ? (led.acende ? 'led--acendendo' : 'led--apagando') : '';

  return (
    <div className="circuito-vivo">
      <div className="circuito-vivo__topo">
        {titulo}
        <div className="circuito-vivo__ferramentas" role="toolbar" aria-label="Zoom do circuito">
          <button type="button" className="botao botao--fantasma botao--icone" onClick={() => aplicarEscala(escala / PASSO_DO_ZOOM)} aria-label="Afastar">
            −
          </button>
          <button
            type="button"
            className="botao botao--fantasma botao--pequeno circuito-vivo__zoom mono"
            onClick={() => aplicarEscala(inicial)}
            title="Voltar ao tamanho inicial"
            aria-label={`Zoom ${zoom}%. Voltar ao tamanho inicial`}
          >
            {zoom}%
          </button>
          <button type="button" className="botao botao--fantasma botao--icone" onClick={() => aplicarEscala(escala * PASSO_DO_ZOOM)} aria-label="Aproximar">
            +
          </button>
          <button type="button" className="botao botao--fantasma botao--pequeno" onClick={() => aplicarEscala(minima)}>
            Ver inteiro
          </button>
        </div>
        {acoes && <div className="circuito-vivo__acoes">{acoes}</div>}
      </div>

      <div ref={moldura} className="circuito-vivo__moldura">
        <div
          ref={area}
          className="circuito-vivo__area"
          style={{ height: alturaDaArea ? alturaDaArea + BORDA : undefined }}
          tabIndex={0}
          role="group"
          aria-label={`${rotulo}. Zoom ${zoom}%: use + e − para aproximar e as setas para mover.`}
          onPointerDown={aoPressionar}
          onPointerMove={aoMover}
          onPointerUp={aoSoltar}
          onPointerCancel={aoSoltar}
          onKeyDown={aoTeclar}
          onScroll={() => dica && esconderDica()}
        >
          <div className="circuito-vivo__folha">
            <svg
              ref={ligarSvg}
              className="circuito-vivo__svg"
              width={base.w * escala}
              height={base.h * escala}
              viewBox={`${base.x} ${base.y} ${base.w} ${base.h}`}
            >
              <defs>
                <pattern id={`${idGrade}-fina`} width="20" height="20" patternUnits="userSpaceOnUse">
                  <path className="grade grade--fina" d="M20 0 H0 V20" />
                </pattern>
                <pattern id={`${idGrade}-grossa`} width="100" height="100" patternUnits="userSpaceOnUse">
                  <rect width="100" height="100" fill={`url(#${idGrade}-fina)`} />
                  <path className="grade grade--grossa" d="M100 0 H0 V100" />
                </pattern>
              </defs>
              <rect className="circuito-vivo__papel" x={base.x} y={base.y} width={base.w} height={base.h} fill={`url(#${idGrade}-grossa)`} />

              <g className="circuito-vivo__desenho">
                {layout.barramentos.map((b) => (
                  <g key={b.id} className={`barramento fio--${nivel(exibido(`barramento:${b.id}`, b.valor))}`}>
                    <line className="fio" x1={b.x} y1={b.y_inicio} x2={b.x} y2={b.y_fim} />
                    <text className="barramento__nome" x={b.x} y={b.y_rotulo - 8}>
                      {b.rotulo}
                    </text>
                    <text className={`barramento__valor fio--${nivel(b.valor)}`} x={b.x} y={b.y_rotulo + 12}>
                      {b.valor === null ? '' : b.valor ? '1' : '0'}
                    </text>
                  </g>
                ))}

                {layout.fios.map((f) => (
                  <polyline
                    key={f.id}
                    className={`fio fio--${nivel(exibido(f.id, f.valor))} ${fiosAtivos.has(f.id) ? 'fio--destaque' : ''}`}
                    points={pontosSvg(f.pontos)}
                  />
                ))}

                {layout.conexoes.map((c, i) => {
                  const barramento = layout.barramentos.find((b) => b.id === c.barramento);
                  return <circle key={i} className={`juncao fio--${nivel(barramento?.valor ?? null)}`} cx={c.ponto[0]} cy={c.ponto[1]} r={4.5} />;
                })}

                {layout.saida && (
                  <line
                    className={`fio fio--${nivel(exibido('saida', layout.saida.valor))} ${ativa === raiz ? 'fio--destaque' : ''}`}
                    x1={layout.saida.de[0]}
                    y1={layout.saida.de[1]}
                    x2={layout.saida.ate[0]}
                    y2={layout.saida.ate[1]}
                  />
                )}

                {propagacao && (
                  <g key={propagacao.onda} className="propagacao" aria-hidden="true">
                    {propagacao.trechos.map((t) => {
                      const estilo = estiloDoTrecho(t.comprimento, t.ordem);
                      const pontos = pontosSvg(t.pontos);
                      return t.sobe ? (
                        <g key={t.id}>
                          <polyline className="frente frente--acende" points={pontos} style={estilo} />
                          <polyline className="pulso" points={pontos} style={estilo} />
                        </g>
                      ) : (
                        <polyline key={t.id} className="frente frente--apaga" points={pontos} style={estilo} />
                      );
                    })}
                  </g>
                )}

                {layout.portas.map((porta) => {
                  const { corpo, bolha } = caminhoDaPorta(porta);
                  return (
                    <g
                      key={porta.id}
                      className={`porta-viva ${ativa === porta.id ? 'porta-viva--ativa' : ''}`}
                      tabIndex={0}
                      role="img"
                      aria-label={`Porta ${NOMES_DAS_PORTAS[porta.tipo] ?? porta.tipo}: ${porta.subexpressao} = ${porta.valor === null ? '?' : porta.valor ? '1' : '0'}`}
                      onPointerEnter={(e) => mostrarDica(porta, e.currentTarget)}
                      onPointerLeave={esconderDica}
                      onFocus={(e) => mostrarDica(porta, e.currentTarget)}
                      onBlur={esconderDica}
                    >
                      <path className="porta-viva__corpo" d={corpo} />
                      {bolha && <circle className="porta-viva__corpo" cx={bolha[0]} cy={bolha[1]} r={8} />}
                    </g>
                  );
                })}

                {layout.saida && (
                  <g className={`saida-viva fio--${nivel(layout.saida.valor)}`}>
                    <circle
                      key={propagacao?.onda ?? 'parado'}
                      className={`led led--${nivel(layout.saida.valor)} ${classeDoLed}`}
                      style={led ? ({ '--atraso': `${led.ordem * DURACAO_DO_TRECHO}ms` } as CSSProperties) : undefined}
                      cx={layout.saida.ate[0] + 18}
                      cy={layout.saida.ate[1]}
                      r={14}
                    />
                    <text className="saida-viva__nome" x={layout.saida.ate[0] + 18} y={layout.saida.ate[1] + 40}>
                      S
                    </text>
                  </g>
                )}
              </g>
            </svg>
          </div>
        </div>

        {dica && (
          <div className="dica-porta" role="tooltip" style={{ left: dica.esquerda, top: dica.topo }}>
            <span className="dica-porta__tipo">{NOMES_DAS_PORTAS[dica.porta.tipo] ?? dica.porta.tipo}</span>
            <span className="mono">
              {dica.porta.subexpressao} = <strong className={dica.porta.valor ? 'cor-sinal-1' : 'cor-sinal-0'}>{dica.porta.valor === null ? '?' : dica.porta.valor ? '1' : '0'}</strong>
            </span>
          </div>
        )}
      </div>

      {abaixo}

      <p className="circuito-vivo__ajuda">
        <span className="so-mouse">Arraste para mover · Ctrl + roda do mouse para aproximar · aponte para uma porta para ver o que ela calcula</span>
        <span className="so-toque">Deslize para mover · pinça para aproximar · toque numa porta para ver o que ela calcula</span>
      </p>
    </div>
  );
}
