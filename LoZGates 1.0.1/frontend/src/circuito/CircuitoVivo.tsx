import { useCallback, useEffect, useId, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent, type Ref } from 'react';
import type { LayoutCircuito, PortaDoLayout } from '../api/tipos';
import { deslocar, nivelDeZoom, zoomEm, zoomNoCentro, type Janela } from './visao';

const MARGEM = 40;
const PASSO_DO_ZOOM = 1.25;

const nivel = (v: boolean | null) => (v === null ? 'indefinido' : v ? '1' : '0');
const NOMES_DAS_PORTAS: Record<string, string> = { AND: 'E (AND)', OR: 'OU (OR)', NOT: 'NÃO (NOT)' };

export function enquadramento(layout: LayoutCircuito): Janela {
  const { x_min, y_min, x_max, y_max } = layout.limites;
  return { x: x_min - MARGEM, y: y_min - MARGEM, w: x_max - x_min + 2 * MARGEM, h: y_max - y_min + 2 * MARGEM };
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

interface Dica {
  porta: PortaDoLayout;
  esquerda: number;
  topo: number;
}

interface Props {
  layout: LayoutCircuito;
  rotulo: string;
  ref?: Ref<SVGSVGElement>;
}

/**
 * O circuito da expressão em SVG, com os sinais atuais: fios em 1 acendem.
 * Arrastar desloca; Ctrl + roda (ou os botões) aproxima; passar o mouse ou o
 * foco do teclado numa porta mostra a subexpressão que ela calcula.
 */
export function CircuitoVivo({ layout, rotulo, ref }: Props) {
  // Ao trocar só os valores das entradas o enquadramento é o mesmo: o zoom do aluno continua
  const chaveDoEnquadramento = JSON.stringify(layout.limites);
  const base = useMemo(() => enquadramento(layout), [chaveDoEnquadramento]);
  const [janela, setJanela] = useState<Janela>(base);
  const [ativa, setAtiva] = useState<string | null>(null);
  const [dica, setDica] = useState<Dica | null>(null);
  const area = useRef<HTMLDivElement>(null);
  const svg = useRef<SVGSVGElement | null>(null);
  // Dedos/mouse pressionados: um desloca, dois fazem pinça
  const ponteiros = useRef(new Map<number, { x: number; y: number }>());
  const idGrade = useId().replace(/:/g, '');

  // Outro circuito: volta ao enquadramento inteiro
  useEffect(() => setJanela(base), [base]);

  const pontoNoMundo = useCallback((clienteX: number, clienteY: number): [number, number] | null => {
    const elemento = svg.current;
    const matriz = elemento?.getScreenCTM();
    if (!elemento || !matriz) return null;
    const ponto = new DOMPoint(clienteX, clienteY).matrixTransform(matriz.inverse());
    return [ponto.x, ponto.y];
  }, []);

  // Ctrl/⌘ + roda aproxima no cursor; a roda sozinha continua rolando a página
  useEffect(() => {
    const elemento = svg.current;
    if (!elemento) return;
    const aoRolar = (e: WheelEvent) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      const ponto = pontoNoMundo(e.clientX, e.clientY);
      if (!ponto) return;
      setJanela((j) => zoomEm(base, j, Math.exp(-e.deltaY * 0.0018), ponto[0], ponto[1]));
    };
    elemento.addEventListener('wheel', aoRolar, { passive: false });
    return () => elemento.removeEventListener('wheel', aoRolar);
  }, [base, pontoNoMundo]);

  const aoPressionar = (e: PointerEvent<SVGSVGElement>) => {
    if (e.button !== 0) return;
    // com o mouse, clicar numa porta não arrasta (a dica fica parada)
    if (e.pointerType === 'mouse' && (e.target as Element).closest('.porta-viva')) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    ponteiros.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
  };

  const aoMover = (e: PointerEvent<SVGSVGElement>) => {
    const anterior = ponteiros.current.get(e.pointerId);
    if (!anterior) return;
    const atual = { x: e.clientX, y: e.clientY };
    const outro = [...ponteiros.current].find(([id]) => id !== e.pointerId)?.[1];
    ponteiros.current.set(e.pointerId, atual);
    if (!outro) {
      const de = pontoNoMundo(anterior.x, anterior.y);
      const ate = pontoNoMundo(atual.x, atual.y);
      if (de && ate) setJanela((j) => deslocar(base, j, de[0] - ate[0], de[1] - ate[1]));
      return;
    }
    // pinça: aproxima na razão entre as distâncias dos dois dedos, em volta do ponto médio
    const antes = Math.hypot(anterior.x - outro.x, anterior.y - outro.y);
    const depois = Math.hypot(atual.x - outro.x, atual.y - outro.y);
    const meio = pontoNoMundo((atual.x + outro.x) / 2, (atual.y + outro.y) / 2);
    if (antes > 0 && meio) setJanela((j) => zoomEm(base, j, depois / antes, meio[0], meio[1]));
  };

  const aoSoltar = (e: PointerEvent<SVGSVGElement>) => {
    ponteiros.current.delete(e.pointerId);
  };

  const aoTeclar = (e: KeyboardEvent<SVGSVGElement>) => {
    const passo = 0.12;
    const acoes: Record<string, () => Janela> = {
      '+': () => zoomNoCentro(base, janela, PASSO_DO_ZOOM),
      '=': () => zoomNoCentro(base, janela, PASSO_DO_ZOOM),
      '-': () => zoomNoCentro(base, janela, 1 / PASSO_DO_ZOOM),
      '0': () => base,
      ArrowLeft: () => deslocar(base, janela, -janela.w * passo, 0),
      ArrowRight: () => deslocar(base, janela, janela.w * passo, 0),
      ArrowUp: () => deslocar(base, janela, 0, -janela.h * passo),
      ArrowDown: () => deslocar(base, janela, 0, janela.h * passo),
    };
    const acao = acoes[e.key];
    if (!acao || e.target !== e.currentTarget) return;
    e.preventDefault();
    setJanela(acao());
  };

  const mostrarDica = (porta: PortaDoLayout, elemento: Element) => {
    const caixa = elemento.getBoundingClientRect();
    const quadro = area.current?.getBoundingClientRect();
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
  const zoom = Math.round(nivelDeZoom(base, janela) * 100);

  const ligarSvg = (elemento: SVGSVGElement | null) => {
    svg.current = elemento;
    if (typeof ref === 'function') ref(elemento);
    else if (ref) (ref as { current: SVGSVGElement | null }).current = elemento;
  };

  return (
    <div className="circuito-vivo">
      <div className="circuito-vivo__ferramentas" role="toolbar" aria-label="Zoom do circuito">
        <button type="button" className="botao botao--fantasma botao--icone" onClick={() => setJanela((j) => zoomNoCentro(base, j, 1 / PASSO_DO_ZOOM))} aria-label="Afastar">
          −
        </button>
        <output className="circuito-vivo__zoom mono" aria-live="polite" aria-label="Zoom atual">
          {zoom}%
        </output>
        <button type="button" className="botao botao--fantasma botao--icone" onClick={() => setJanela((j) => zoomNoCentro(base, j, PASSO_DO_ZOOM))} aria-label="Aproximar">
          +
        </button>
        <button type="button" className="botao botao--fantasma botao--pequeno" onClick={() => setJanela(base)}>
          Ajustar
        </button>
      </div>

      <div ref={area} className="circuito-vivo__area">
        <svg
          ref={ligarSvg}
          className="circuito-vivo__svg"
          viewBox={`${janela.x} ${janela.y} ${janela.w} ${janela.h}`}
          preserveAspectRatio="xMidYMid meet"
          // Sem zoom o circuito inteiro já está à vista: deslizar o dedo na vertical rola a página
          style={{ aspectRatio: `${base.w} / ${base.h}`, touchAction: zoom > 100 ? 'none' : 'pan-y' }}
          role="group"
          aria-label={rotulo}
          tabIndex={0}
          onPointerDown={aoPressionar}
          onPointerMove={aoMover}
          onPointerUp={aoSoltar}
          onPointerCancel={aoSoltar}
          onKeyDown={aoTeclar}
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
          <rect
            className="circuito-vivo__papel"
            x={base.x - base.w * 2}
            y={base.y - base.h * 2}
            width={base.w * 5}
            height={base.h * 5}
            fill={`url(#${idGrade}-grossa)`}
          />

          <g className="circuito-vivo__desenho">
            {layout.barramentos.map((b) => (
              <g key={b.id} className={`barramento fio--${nivel(b.valor)}`}>
                <line className="fio" x1={b.x} y1={b.y_inicio} x2={b.x} y2={b.y_fim} />
                <text className="barramento__nome" x={b.x} y={b.y_rotulo - 5}>
                  {b.rotulo}
                </text>
                <text className="barramento__valor" x={b.x} y={b.y_rotulo + 11}>
                  {b.valor === null ? '' : b.valor ? '1' : '0'}
                </text>
              </g>
            ))}

            {layout.fios.map((f) => (
              <polyline
                key={f.id}
                className={`fio fio--${nivel(f.valor)} ${fiosAtivos.has(f.id) ? 'fio--destaque' : ''}`}
                points={f.pontos.map(([x, y]) => `${x},${y}`).join(' ')}
              />
            ))}

            {layout.conexoes.map((c, i) => {
              const barramento = layout.barramentos.find((b) => b.id === c.barramento);
              return <circle key={i} className={`juncao fio--${nivel(barramento?.valor ?? null)}`} cx={c.ponto[0]} cy={c.ponto[1]} r={4.5} />;
            })}

            {layout.saida && (
              <g className={`saida-viva fio--${nivel(layout.saida.valor)}`}>
                <line
                  className={`fio ${ativa === raiz ? 'fio--destaque' : ''}`}
                  x1={layout.saida.de[0]}
                  y1={layout.saida.de[1]}
                  x2={layout.saida.ate[0]}
                  y2={layout.saida.ate[1]}
                />
                <circle className={`led led--${nivel(layout.saida.valor)}`} cx={layout.saida.ate[0] + 18} cy={layout.saida.ate[1]} r={14} />
                <text className="saida-viva__nome" x={layout.saida.ate[0] + 18} y={layout.saida.ate[1] + 36}>
                  S
                </text>
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
          </g>
        </svg>

        {dica && (
          <div className="dica-porta" role="tooltip" style={{ left: dica.esquerda, top: dica.topo }}>
            <span className="dica-porta__tipo">{NOMES_DAS_PORTAS[dica.porta.tipo] ?? dica.porta.tipo}</span>
            <span className="mono">
              {dica.porta.subexpressao} = <strong className={dica.porta.valor ? 'cor-sinal-1' : 'cor-sinal-0'}>{dica.porta.valor === null ? '?' : dica.porta.valor ? '1' : '0'}</strong>
            </span>
          </div>
        )}
      </div>
      <p className="circuito-vivo__ajuda">
        Arraste para mover · Ctrl + roda do mouse (ou pinça, no toque) para aproximar · aponte para uma porta para ver o que ela calcula
      </p>
    </div>
  );
}
