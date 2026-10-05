import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from 'react';
import { api } from '../api/cliente';
import type { Netlist, Ponto } from '../api/tipos';
import { ChaveDeEntrada } from '../componentes/ChaveDeEntrada';
import { comprimento, DURACAO_DO_TRECHO, movimentoReduzido } from '../circuito/propagacao';

type Porta = 'and' | 'or';
type Fio = 'A' | 'B' | 'S';

const NOMES: Record<Porta, { simbolo: string; legenda: string }> = {
  and: { simbolo: '&', legenda: 'Porta E (AND)' },
  or: { simbolo: '|', legenda: 'Porta OU (OR)' },
};

// Os fios começam embaixo das chaves (que ficam a partir de x = 2%) e terminam nas entradas da porta
const FIOS: Record<Fio, Ponto[]> = {
  A: [[20, 60], [150, 60], [150, 100], [190, 100]],
  B: [[20, 180], [150, 180], [150, 140], [190, 140]],
  S: [[247, 120], [320, 120]],
};
const pontosSvg = (pontos: Ponto[]) => pontos.map(([x, y]) => `${x},${y}`).join(' ');

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

interface Onda {
  chave: number;
  trechos: { fio: Fio; sobe: boolean; atraso: number }[];
  led: { acende: boolean; atraso: number } | null;
}

const nivel = (v: boolean | null) => (v === null ? '·' : v ? '1' : '0');

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
  const [onda, setOnda] = useState<Onda | null>(null);
  const pedido = useRef(0);
  const inicioDaOnda = useRef(0);
  const saidaAnterior = useRef<boolean | null>(null);

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

  // A mudança percorre o fio da entrada; quando a resposta do servidor chega, segue pela saída até o LED
  const alternar = (fio: 'A' | 'B', valor: boolean) => {
    (fio === 'A' ? setA : setB)(!valor);
    if (movimentoReduzido()) return;
    inicioDaOnda.current = performance.now();
    setOnda((anterior) => ({ chave: (anterior?.chave ?? 0) + 1, trechos: [{ fio, sobe: !valor, atraso: 0 }], led: null }));
  };

  const trocarPorta = (nova: Porta) => {
    setPorta(nova);
    inicioDaOnda.current = performance.now() - DURACAO_DO_TRECHO; // não há fio de entrada para percorrer
  };

  useLayoutEffect(() => {
    const antes = saidaAnterior.current;
    saidaAnterior.current = saida;
    if (antes === null || saida === null || antes === saida || movimentoReduzido()) return;
    const atraso = Math.max(0, DURACAO_DO_TRECHO - (performance.now() - inicioDaOnda.current));
    setOnda((anterior) => ({
      chave: anterior?.chave ?? 0,
      trechos: [...(anterior?.trechos.filter((t) => t.fio !== 'S') ?? []), { fio: 'S', sobe: saida, atraso }],
      led: { acende: saida, atraso: atraso + DURACAO_DO_TRECHO },
    }));
  }, [saida]);

  // Terminada a onda, os fios voltam a ser desenhados só pelo estado atual
  useEffect(() => {
    if (!onda) return;
    const fim = Math.max(...onda.trechos.map((t) => t.atraso), onda.led?.atraso ?? 0) + DURACAO_DO_TRECHO + 80;
    const relogio = window.setTimeout(() => setOnda(null), fim);
    return () => window.clearTimeout(relogio);
  }, [onda]);

  // Enquanto o sinal não chega, o fio que vai acender continua apagado
  const exibido = (fio: Fio, valor: boolean | null) => (onda?.trechos.some((t) => t.fio === fio && t.sobe) ? false : valor);
  const classeDoFio = (fio: Fio, valor: boolean | null) => `mini__fio ${exibido(fio, valor) ? 'fio--1' : 'fio--0'}`;
  const estilo = (fio: Fio, atraso: number) =>
    ({ '--comprimento': comprimento(FIOS[fio]), '--atraso': `${atraso}ms`, '--duracao': `${DURACAO_DO_TRECHO}ms` }) as CSSProperties;

  return (
    <figure className="mini" aria-label="Minicircuito de exemplo">
      <div className="mini__quadro">
        <svg className="mini__svg" viewBox="0 0 400 240" aria-hidden="true" focusable="false">
          <polyline className={classeDoFio('A', a)} points={pontosSvg(FIOS.A)} />
          <polyline className={classeDoFio('B', b)} points={pontosSvg(FIOS.B)} />
          <polyline className={classeDoFio('S', saida)} points={pontosSvg(FIOS.S)} />
          {onda && (
            <g key={onda.chave}>
              {onda.trechos.map((t) =>
                t.sobe ? (
                  <g key={t.fio}>
                    <polyline className="frente frente--acende mini__frente" points={pontosSvg(FIOS[t.fio])} style={estilo(t.fio, t.atraso)} />
                    <polyline className="pulso mini__pulso" points={pontosSvg(FIOS[t.fio])} style={estilo(t.fio, t.atraso)} />
                  </g>
                ) : (
                  <polyline key={t.fio} className="frente frente--apaga mini__frente" points={pontosSvg(FIOS[t.fio])} style={estilo(t.fio, t.atraso)} />
                ),
              )}
            </g>
          )}
          {porta === 'and' ? (
            <path className="mini__porta" d="M190 88 H214 A32 32 0 0 1 214 152 H190 Z" />
          ) : (
            <path className="mini__porta" d="M182 88 Q218 88 248 120 Q218 152 182 152 Q197 120 182 88 Z" />
          )}
          <circle
            key={onda?.led ? `led-${onda.chave}-${onda.led.atraso}` : 'led'}
            className={`mini__led ${saida ? 'led--1' : 'led--0'} ${onda?.led ? (onda.led.acende ? 'led--acendendo' : 'led--apagando') : ''}`}
            style={onda?.led ? ({ '--atraso': `${onda.led.atraso}ms` } as CSSProperties) : undefined}
            cx="340"
            cy="120"
            r="17"
          />
          <text className="mini__rotulo" x="340" y="166">
            S
          </text>
        </svg>
        <ChaveDeEntrada className="mini__chave mini__chave--a" nome="A" ligada={a} aoAlternar={() => alternar('A', a)} />
        <ChaveDeEntrada className="mini__chave mini__chave--b" nome="B" ligada={b} aoAlternar={() => alternar('B', b)} />
      </div>
      <figcaption className="mini__legenda">
        <span>
          <span className="rotulo-secao">Figura 1</span> {NOMES[porta].legenda}
        </span>
        <span className="mini__seletor" role="group" aria-label="Porta lógica">
          {(['and', 'or'] as Porta[]).map((p) => (
            <button key={p} type="button" aria-pressed={porta === p} onClick={() => trocarPorta(p)}>
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
