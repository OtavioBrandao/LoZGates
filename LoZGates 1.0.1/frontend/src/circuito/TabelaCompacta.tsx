import { useEffect, useRef } from 'react';

interface Props {
  variaveis: string[];
  tabela: number[][];
  resultados: number[];
  atual: number;
  aoEscolher: (indice: number) => void;
}

/** Tabela-verdade resumida (entradas e S); a linha das entradas atuais fica marcada. */
export function TabelaCompacta({ variaveis, tabela, resultados, atual, aoEscolher }: Props) {
  const linhaAtual = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    // Rola só a caixa da tabela, sem mexer na página
    const botao = linhaAtual.current;
    const caixa = botao?.closest('.tabela-compacta__corpo') as HTMLElement | null;
    if (!botao || !caixa) return;
    const topo = botao.offsetTop; // a caixa é position: relative
    if (topo < caixa.scrollTop || topo + botao.offsetHeight > caixa.scrollTop + caixa.clientHeight) {
      caixa.scrollTop = topo - caixa.clientHeight / 2 + botao.offsetHeight / 2;
    }
  }, [atual]);

  const colunas = { gridTemplateColumns: `1.25rem repeat(${variaveis.length + 1}, minmax(1.75rem, 1fr))` };

  return (
    <div className="tabela-compacta">
      <div className="tabela-compacta__cabecalho mono" style={colunas} aria-hidden="true">
        <span />
        {variaveis.map((v) => (
          <span key={v}>{v}</span>
        ))}
        <span className="tabela-compacta__s">S</span>
      </div>
      <ol className="tabela-compacta__corpo">
        {tabela.map((linha, i) => {
          const entradas = linha.slice(0, variaveis.length);
          const descricao = `${variaveis.map((v, j) => `${v}=${entradas[j]}`).join(', ')}; S=${resultados[i]}`;
          return (
            <li key={i}>
              <button
                ref={i === atual ? linhaAtual : undefined}
                type="button"
                className={`tabela-compacta__linha mono ${i === atual ? 'tabela-compacta__linha--atual' : ''}`}
                style={colunas}
                aria-pressed={i === atual}
                aria-label={descricao}
                onClick={() => aoEscolher(i)}
              >
                <span className="tabela-compacta__marca" aria-hidden="true">
                  {i === atual ? '▸' : ''}
                </span>
                {entradas.map((valor, j) => (
                  <span key={j} className={valor ? 'nivel-1' : 'nivel-0'}>
                    {valor}
                  </span>
                ))}
                <span className={`tabela-compacta__s ${resultados[i] ? 'nivel-1' : 'nivel-0'}`}>{resultados[i]}</span>
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
