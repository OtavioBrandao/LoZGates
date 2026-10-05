import { useEffect, useRef, useState } from 'react';
import { api } from '../api/cliente';
import type { Netlist } from '../api/tipos';

type Porta = 'and' | 'or';

const NOMES: Record<Porta, { simbolo: string; legenda: string }> = {
  and: { simbolo: '&', legenda: 'Porta E (AND)' },
  or: { simbolo: '|', legenda: 'Porta OU (OR)' },
};

function netlist(porta: Porta): Netlist {
  return {
    componentes: [
      { id: 'var-A', tipo: 'variable', nome: 'A' },
      { id: 'var-B', tipo: 'variable', nome: 'B' },
      { id: 'porta', tipo: porta },
      { id: 'saida', tipo: 'output' },
    ],
    fios: [
      { origem: 'var-A', destino: 'porta', entrada: 0 },
      { origem: 'var-B', destino: 'porta', entrada: 1 },
      { origem: 'porta', destino: 'saida', entrada: 0 },
    ],
  };
}

const nivel = (v: boolean | null) => (v === null ? '·' : v ? '1' : '0');
const classeDoFio = (v: boolean | null) => `mini__fio ${v ? 'fio--1' : 'fio--0'}`;

/**
 * Minicircuito da tela inicial: as chaves A e B entram numa porta E ou OU e a
 * saída acende o LED. Quem calcula a saída é o simulador do servidor
 * (circuito_logico/logic/validacao.simular), como no resto do LoZ Gates.
 */
export function MiniCircuito() {
  const [a, setA] = useState(true);
  const [b, setB] = useState(false);
  const [porta, setPorta] = useState<Porta>('and');
  const [saida, setSaida] = useState<boolean | null>(null);
  const pedido = useRef(0);

  useEffect(() => {
    const atual = ++pedido.current;
    api
      .simularCircuito(netlist(porta), { A: a, B: b })
      .then(({ saidas }) => {
        if (atual === pedido.current) setSaida(saidas.saida ?? null);
      })
      .catch(() => {
        if (atual === pedido.current) setSaida(null);
      });
  }, [a, b, porta]);

  return (
    <figure className="mini" aria-label="Minicircuito de exemplo">
      <div className="mini__quadro">
        <svg className="mini__svg" viewBox="0 0 400 240" aria-hidden="true" focusable="false">
          <path className={classeDoFio(a)} d="M76 60 H150 V100 H190" />
          <path className={classeDoFio(b)} d="M76 180 H150 V140 H190" />
          {porta === 'and' ? (
            <path className="mini__porta" d="M190 88 H214 A32 32 0 0 1 214 152 H190 Z" />
          ) : (
            <path className="mini__porta" d="M182 88 Q218 88 248 120 Q218 152 182 152 Q197 120 182 88 Z" />
          )}
          <path className={classeDoFio(saida)} d="M247 120 H318" />
          <circle className={`mini__led ${saida ? 'led--1' : 'led--0'}`} cx="340" cy="120" r="17" />
          <text className="mini__rotulo" x="340" y="166">
            S
          </text>
        </svg>
        <button
          type="button"
          className={`mini__chave ${a ? 'chave--1' : 'chave--0'}`}
          style={{ top: '25%' }}
          aria-pressed={a}
          onClick={() => setA((v) => !v)}
        >
          A = {nivel(a)}
        </button>
        <button
          type="button"
          className={`mini__chave ${b ? 'chave--1' : 'chave--0'}`}
          style={{ top: '75%' }}
          aria-pressed={b}
          onClick={() => setB((v) => !v)}
        >
          B = {nivel(b)}
        </button>
      </div>
      <figcaption className="mini__legenda">
        <span>
          <span className="rotulo-secao">Figura 1</span> {NOMES[porta].legenda}
        </span>
        <span className="mini__seletor" role="group" aria-label="Porta lógica">
          {(['and', 'or'] as Porta[]).map((p) => (
            <button key={p} type="button" aria-pressed={porta === p} onClick={() => setPorta(p)}>
              {p === 'and' ? 'E' : 'OU'}
            </button>
          ))}
        </span>
      </figcaption>
      <p className="mini__expressao mono" aria-live="polite">
        S = A {NOMES[porta].simbolo} B = <strong className={saida ? 'cor-sinal-1' : 'cor-sinal-0'}>{nivel(saida)}</strong>
      </p>
    </figure>
  );
}
