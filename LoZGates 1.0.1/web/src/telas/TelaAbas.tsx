import { useEffect, useId } from 'react';
import { Abas } from '../componentes/Abas';
import { TopoTela } from '../componentes/TopoTela';
import { useAplicacao, type Aba } from '../estado/Aplicacao';
import { AbaCircuito } from './AbaCircuito';
import { AbaCircuitoInterativo } from './AbaCircuitoInterativo';
import { AbaExpressao } from './AbaExpressao';

const ABAS: { id: Aba; rotulo: string }[] = [
  { id: 'circuito', rotulo: 'Circuito' },
  { id: 'interativo', rotulo: 'Circuito Interativo' },
  { id: 'expressao', rotulo: 'Expressão' },
];

const PREFIXO = 'Expressão Lógica Proposicional: ';

/** label_circuito_expressao: "Expressão Lógica Proposicional: <expressão>" */
function RotuloExpressao({ texto }: { texto: string }) {
  if (!texto.startsWith(PREFIXO)) return <>{texto}</>;
  return (
    <>
      <span className="topo-tela__rotulo">Expressão Lógica Proposicional:</span>{' '}
      <span className="mono destaque">{texto.slice(PREFIXO.length)}</span>
    </>
  );
}

/**
 * frame_abas — as três abas ficam montadas o tempo todo (como no CTkTabview), assim o
 * circuito interativo continua existindo ao trocar de aba ou ir para a simplificação.
 */
export function TelaAbas({ oculta }: { oculta: boolean }) {
  const app = useAplicacao();
  const idBase = useId();
  const { aba, seletor, garantirSeletor } = app;

  // A aba "Circuito Interativo" visível sempre tem a tela de modos (if_necessary_create_a_circuit)
  useEffect(() => {
    if (!oculta && aba === 'interativo' && !seletor) garantirSeletor();
  }, [oculta, aba, seletor, garantirSeletor]);

  return (
    <main className="tela tela--larga" hidden={oculta}>
      <TopoTela voltar={{ acao: () => app.voltarPara('principal') }} titulo={<RotuloExpressao texto={app.labelCircuito} />} />
      <Abas idBase={idBase} rotulo="Ferramentas da expressão" abas={ABAS} atual={aba} aoMudar={app.mudarAba} />
      {ABAS.map((item) => (
        <section
          key={item.id}
          role="tabpanel"
          id={`${idBase}-painel-${item.id}`}
          aria-labelledby={`${idBase}-aba-${item.id}`}
          hidden={aba !== item.id}
          className="painel-aba"
        >
          {item.id === 'circuito' && <AbaCircuito />}
          {item.id === 'interativo' && (seletor ? <AbaCircuitoInterativo key={seletor} /> : null)}
          {item.id === 'expressao' && <AbaExpressao />}
        </section>
      ))}
    </main>
  );
}
