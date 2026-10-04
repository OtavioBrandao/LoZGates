import { useId } from 'react';
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

/**
 * frame_abas — as três abas ficam montadas o tempo todo (como no CTkTabview), assim o
 * circuito interativo continua existindo ao trocar de aba ou ir para as simplificações.
 */
export function TelaAbas({ oculta }: { oculta: boolean }) {
  const app = useAplicacao();
  const idBase = useId();

  return (
    <main className="tela tela--larga" hidden={oculta}>
      <TopoTela voltar={{ acao: () => app.voltarPara('principal') }} />
      <Abas idBase={idBase} rotulo="Ferramentas da expressão" abas={ABAS} atual={app.aba} aoMudar={app.mudarAba} />
      {ABAS.map((item) => (
        <section
          key={item.id}
          role="tabpanel"
          id={`${idBase}-painel-${item.id}`}
          aria-labelledby={`${idBase}-aba-${item.id}`}
          hidden={app.aba !== item.id}
          className="painel-aba"
        >
          {item.id === 'circuito' && <AbaCircuito />}
          {item.id === 'interativo' && (app.seletor ? <AbaCircuitoInterativo key={app.seletor} /> : null)}
          {item.id === 'expressao' && <AbaExpressao />}
        </section>
      ))}
    </main>
  );
}
