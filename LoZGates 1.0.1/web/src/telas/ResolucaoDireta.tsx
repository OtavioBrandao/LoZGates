import { useEffect, useState } from 'react';
import { TopoTela } from '../componentes/TopoTela';
import { useAplicacao, type Resolucao } from '../estado/Aplicacao';

/** frame_resolucao_direta — "Solução da expressão:" + StepView */
export function ResolucaoDireta() {
  const app = useAplicacao();
  return (
    <main className="tela tela--media">
      <TopoTela voltar={{ acao: app.voltarParaAbas }} titulo="Solução da expressão:" />
      {app.resolucao ? (
        <VistaPassos resolucao={app.resolucao} />
      ) : (
        app.ocupado && <p className="texto-secundario carregando-texto">Simplificando…</p>
      )}
    </main>
  );
}

/**
 * StepView (FrontEnd/step_view.py). No desktop os cartões apareciam conforme o
 * simplificador imprimia (com time.sleep(1) entre as iterações); aqui revelamos cada
 * cartão no mesmo instante em que ele apareceria.
 */
function VistaPassos({ resolucao }: { resolucao: Resolucao }) {
  const [agora, setAgora] = useState(() => performance.now());
  const decorrido = (agora - resolucao.iniciadoEm) / 1000;
  const fim = Math.max(resolucao.final?.t ?? 0, resolucao.passos.at(-1)?.t ?? 0);
  const concluido = decorrido >= fim;

  useEffect(() => {
    if (concluido) return;
    const id = setInterval(() => setAgora(performance.now()), 100);
    return () => clearInterval(id);
  }, [concluido]);

  const visiveis = resolucao.passos.filter((p) => p.t <= decorrido);
  const final = resolucao.final && resolucao.final.t <= decorrido ? resolucao.final : null;

  return (
    <section className="vista-passos" aria-labelledby="titulo-progresso">
      <h2 id="titulo-progresso" className="titulo-secao">
        Progresso da Simplificação
      </h2>
      <ol className="lista-passos" aria-live="polite">
        <li className="cartao-passo cartao-passo--inicial">
          <p className="cartao-passo__titulo">Expressão Inicial</p>
          <p className="mono cartao-passo__expressao">{resolucao.expressao_inicial}</p>
        </li>
        {visiveis.map((passo) => (
          <li key={passo.iteration} className="cartao-passo cartao-passo--entrada">
            <p className="cartao-passo__titulo">
              Iteração {passo.iteration} — {passo.law}
            </p>
            {passo.subexpression && <p className="texto-secundario mono">Subexpressão: {passo.subexpression}</p>}
            <p className="cartao-passo__transformacao mono">
              {passo.before} → {passo.after}
            </p>
            <p className={`cartao-passo__status ${passo.success ? 'cor-sucesso' : 'cor-erro'}`}>
              <span className="mono">
                {passo.success ? '✔' : '✖'} {passo.result_expression}
              </span>
              {passo.note && <small className="texto-secundario"> {passo.note}</small>}
            </p>
          </li>
        ))}
      </ol>

      {!concluido && <p className="texto-secundario carregando-texto">Simplificando…</p>}

      {final && (
        <footer className="resultado-final">
          <p className="cartao-passo__titulo">Expressão Resultante</p>
          <p className="mono resultado-final__expressao">{final.expressao}</p>
          {(!final.sucesso || resolucao.passos.length === 0) && (
            <p className="texto-secundario">Nenhuma simplificação adicional foi identificada.</p>
          )}
          {resolucao.passos.length > 0 && <p className="texto-secundario pequeno">Iterações: {resolucao.passos.length}</p>}
        </footer>
      )}
    </section>
  );
}
