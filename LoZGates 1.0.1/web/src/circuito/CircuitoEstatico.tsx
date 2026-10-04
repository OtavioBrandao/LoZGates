import type { Ref } from 'react';
import type { LayoutCircuito } from '../api/tipos';
import { CORES, FormaDaPorta } from './formas';

/** Folga em volta do circuito, em unidades do mundo. */
const MARGEM = 30;

export function caixaDoCircuito(layout: LayoutCircuito) {
  const { x_min, y_min, x_max, y_max } = layout.limites;
  return {
    x: x_min - MARGEM,
    y: y_min - MARGEM,
    largura: x_max - x_min + 2 * MARGEM,
    altura: y_max - y_min + 2 * MARGEM,
  };
}

const pontosDaLinha = (pontos: [number, number][]) => pontos.map(([x, y]) => `${x},${y}`).join(' ');

/** Só o desenho (sem o <svg>), para reaproveitar na exportação em PNG. */
export function DesenhoDoCircuito({ layout }: { layout: LayoutCircuito }) {
  return (
    <g fontFamily="sans-serif">
      {/* Barramentos das variáveis (e das negações) */}
      {layout.barramentos.map((b) => (
        <g key={b.id}>
          <line x1={b.x} y1={b.y_inicio} x2={b.x} y2={b.y_fim} stroke={CORES.branco} strokeWidth={2} />
          <text x={b.x} y={b.y_rotulo} fill={CORES.rotulo} fontSize={24} textAnchor="middle" dominantBaseline="middle">
            {b.rotulo}
          </text>
        </g>
      ))}

      {/* Fios: três segmentos pelo meio do caminho (draw_smart_wire) */}
      {layout.fios.map((f) => (
        <polyline key={f.id} points={pontosDaLinha(f.pontos)} fill="none" stroke={CORES.fio} strokeWidth={2} />
      ))}

      {/* Pontos onde os fios saem dos barramentos */}
      {layout.conexoes.map((c, i) => (
        <circle key={i} cx={c.ponto[0]} cy={c.ponto[1]} r={5} fill={CORES.fio} />
      ))}

      {/* Portas */}
      {layout.portas.map((p) => (
        <g key={p.id}>
          <title>{p.subexpressao}</title>
          <FormaDaPorta tipo={p.tipo.toLowerCase()} x={p.x} y={p.y} />
        </g>
      ))}

      {/* Saída final */}
      {layout.saida && (
        <g>
          <line
            x1={layout.saida.de[0]}
            y1={layout.saida.de[1]}
            x2={layout.saida.ate[0]}
            y2={layout.saida.ate[1]}
            stroke={CORES.branco}
            strokeWidth={4}
          />
          <text
            x={layout.saida.rotulo[0]}
            y={layout.saida.rotulo[1]}
            fill={CORES.branco}
            fontSize={21}
            textAnchor="middle"
            dominantBaseline="middle"
          >
            SAÍDA
          </text>
        </g>
      )}
    </g>
  );
}

/**
 * Circuito gerado da expressão (antes: circuito.png feito pelo pygame).
 * As coordenadas vêm prontas do servidor (BackEnd/circuito_logico/logic/layout.py).
 */
export function CircuitoEstatico({ layout, rotulo, ref }: { layout: LayoutCircuito; rotulo: string; ref?: Ref<SVGSVGElement> }) {
  const caixa = caixaDoCircuito(layout);
  return (
    <svg
      ref={ref}
      className="circuito-estatico"
      viewBox={`${caixa.x} ${caixa.y} ${caixa.largura} ${caixa.altura}`}
      style={{ maxWidth: `${Math.round(caixa.largura * 1.25)}px` }}
      role="img"
      aria-label={rotulo}
    >
      <rect x={caixa.x} y={caixa.y} width={caixa.largura} height={caixa.altura} fill={CORES.fundo} />
      <DesenhoDoCircuito layout={layout} />
    </svg>
  );
}
