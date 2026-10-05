import { useId } from 'react';
import { Abas } from '../componentes/Abas';
import { Botao } from '../componentes/Botao';
import { SeletorDeTema } from '../componentes/SeletorDeTema';
import { PREFIXO_LABEL_CIRCUITO, useAplicacao, type Aba } from '../estado/Aplicacao';
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
  const expressao = app.labelCircuito.startsWith(PREFIXO_LABEL_CIRCUITO)
    ? app.labelCircuito.slice(PREFIXO_LABEL_CIRCUITO.length)
    : app.labelCircuito;

  return (
    <main className="pagina pagina--abas" hidden={oculta}>
      <header className="cabecalho-expressao">
        <Botao estilo="voltar" tamanho="pequeno" onClick={() => app.voltarPara('principal')}>
          Voltar
        </Botao>
        <div className="cabecalho-expressao__texto">
          <span className="rotulo-secao">Expressão lógica proposicional</span>
          <p className="cabecalho-expressao__expressao mono">
            {expressao}
            {app.expressaoGlobal && (
              <span className="cabecalho-expressao__booleana" title="Em álgebra booleana">
                ≡ {app.expressaoGlobal}
              </span>
            )}
          </p>
        </div>
        <SeletorDeTema />
      </header>
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
