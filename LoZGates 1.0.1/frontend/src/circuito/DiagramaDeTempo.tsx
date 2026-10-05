import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from 'react';
import { montarDiagrama } from './diagrama';

interface Props {
  variaveis: string[];
  tabela: number[][];
  resultados: number[];
  atual: number;
  aoEscolher: (indice: number) => void;
}

/**
 * Diagrama de tempo: as linhas da tabela-verdade lado a lado no tempo, como
 * num analisador lógico. O cursor marca a combinação das entradas atuais;
 * clicar numa fatia (ou usar ← e →) troca as entradas.
 */
export function DiagramaDeTempo({ variaveis, tabela, resultados, atual, aoEscolher }: Props) {
  const caixa = useRef<HTMLDivElement>(null);
  const [largura, setLargura] = useState(0);
  const d = useMemo(() => montarDiagrama(variaveis, tabela, resultados, largura), [variaveis, tabela, resultados, largura]);
  const total = tabela.length;

  // As fatias acompanham a largura do painel
  useEffect(() => {
    const elemento = caixa.current;
    if (!elemento) return;
    const observador = new ResizeObserver(([entrada]) => setLargura(Math.floor(entrada.contentRect.width)));
    observador.observe(elemento);
    return () => observador.disconnect();
  }, []);

  const aoTeclar = (e: KeyboardEvent<SVGSVGElement>) => {
    const destino = { ArrowLeft: atual - 1, ArrowRight: atual + 1, Home: 0, End: total - 1 }[e.key];
    if (destino === undefined) return;
    e.preventDefault();
    aoEscolher((destino + total) % total);
  };

  return (
    <div ref={caixa} className="diagrama-tempo__rolagem">
      <svg
        className="diagrama-tempo"
        width={d.largura}
        height={d.altura}
        viewBox={`0 0 ${d.largura} ${d.altura}`}
        role="group"
        aria-label={`Diagrama de tempo de ${variaveis.join(', ')} e S. Combinação atual: ${d.rotulos[atual]?.texto ?? ''}. Use as setas para mudar.`}
        tabIndex={0}
        onKeyDown={aoTeclar}
      >
        {d.rotulos.map((rotulo, k) => (
          <rect
            key={`fatia-${k}`}
            className={`diagrama-tempo__fatia ${k % 2 ? 'diagrama-tempo__fatia--par' : ''}`}
            x={d.inicioX + k * d.larguraFatia}
            y={0}
            width={d.larguraFatia}
            height={d.baseRotulos + 14}
            onClick={() => aoEscolher(k)}
          >
            <title>{`${variaveis.join('')} = ${rotulo.texto} → S = ${resultados[k]}`}</title>
          </rect>
        ))}
        <rect
          className="diagrama-tempo__cursor"
          x={d.inicioX + atual * d.larguraFatia}
          y={-1}
          width={d.larguraFatia}
          height={d.baseRotulos + 16}
        />
        {d.linhas.map((linha) => (
          <g key={linha.nome} className={`diagrama-tempo__linha ${linha.saida ? 'diagrama-tempo__linha--saida' : ''}`}>
            <text className="diagrama-tempo__nome" x={d.inicioX - 14} y={linha.topo + 21}>
              {linha.nome}
            </text>
            {linha.altos.map((alto, i) => (
              <rect key={i} className="diagrama-tempo__alto" x={alto.x} y={linha.topo + 6} width={alto.largura} height={20} />
            ))}
            <path className="diagrama-tempo__onda" d={linha.onda} />
          </g>
        ))}
        {d.rotulos.map((rotulo, k) => (
          <text key={`rotulo-${k}`} className={`diagrama-tempo__rotulo ${k === atual ? 'diagrama-tempo__rotulo--atual' : ''}`} x={rotulo.x} y={d.baseRotulos + 10}>
            {rotulo.texto}
          </text>
        ))}
      </svg>
    </div>
  );
}
