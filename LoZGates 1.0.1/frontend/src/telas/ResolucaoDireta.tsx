import type { ResultadoSimplificacao } from '../api/tipos';
import { CabecalhoDaTela } from '../componentes/CabecalhoDaTela';
import { TextoComTrecho } from '../componentes/TextoComTrecho';
import { useAplicacao } from '../estado/Aplicacao';

/** Por que a simplificação parou (motivos de identificar_lei._simplificar e do SimplificationGuard). */
const MOTIVOS: Record<string, string> = {
  completed: 'A expressão ficou reduzida a uma só variável ou constante.',
  no_further_simplification: 'Nenhuma lei reduz mais a expressão.',
  no_progress: 'A próxima transformação não reduziria a expressão.',
  maximum_steps: 'Limite máximo de transformações atingido.',
  repeated_state: 'A próxima transformação repetiria um estado anterior.',
};

/** frame_resolucao_direta — "Solução da expressão:" + StepView. */
export function ResolucaoDireta() {
  const app = useAplicacao();
  return (
    <main className="pagina pagina--formulario">
      <CabecalhoDaTela
        secao="3.2 · Simplificação · Resultado"
        titulo="Solução da expressão"
        aoVoltar={app.voltarParaAbas}
        voltarDesabilitado={app.simplificando}
      />
      <VistaPassos resolucao={app.resolucao} processando={app.simplificando} />
    </main>
  );
}

/**
 * StepView (FrontEnd/components/step_view.py). Os passos chegam prontos da API
 * (antes vinham do texto impresso pelo simplificador, lido pelo StepParser),
 * já com o trecho onde cada lei agiu.
 */
function VistaPassos({ resolucao, processando }: { resolucao: ResultadoSimplificacao | null; processando: boolean }) {
  return (
    <section className="painel vista-passos" aria-labelledby="titulo-progresso" aria-busy={processando}>
      <h2 id="titulo-progresso" className="titulo-painel">
        <span className="rotulo-secao">Tabela 1</span> {processando ? 'Simplificando expressão...' : 'Progresso da Simplificação'}
      </h2>
      {processando && !resolucao && <p className="texto-secundario carregando-texto">Aplicando as leis…</p>}
      {resolucao && (
        <>
          <ol className="registro-passos" aria-live="polite">
            <li className="registro-passos__item registro-passos__item--inicial">
              <span className="registro-passos__marca mono" aria-hidden="true">
                0
              </span>
              <div className="registro-passos__corpo">
                <p className="registro-passos__titulo">Expressão Inicial</p>
                <p className="mono registro-passos__expressao">{resolucao.expressao_inicial}</p>
                <p className="texto-secundario pequeno">
                  em álgebra booleana: <span className="mono">{resolucao.expressao_booleana}</span>
                </p>
              </div>
            </li>
            {resolucao.passos.map((passo, i) => (
              <li key={passo.iteracao} className="registro-passos__item">
                <span className="registro-passos__marca mono" aria-hidden="true">
                  {i + 1}
                </span>
                <div className="registro-passos__corpo">
                  <p className="registro-passos__titulo">
                    Iteração {i + 1} <span className="registro-passos__lei">{passo.lei}</span>
                  </p>
                  <p className="registro-passos__transformacao mono">
                    <span>{passo.subexpressao_antes}</span>
                    <span className="registro-passos__seta" aria-label="vira">
                      →
                    </span>
                    <span className="cor-sucesso">{passo.subexpressao_depois}</span>
                  </p>
                  <dl className="registro-passos__contexto mono">
                    <div>
                      <dt>antes</dt>
                      <dd>
                        <TextoComTrecho texto={passo.expressao_antes} trecho={passo.trecho_antes} />
                      </dd>
                    </div>
                    <div>
                      <dt>depois</dt>
                      <dd>
                        <TextoComTrecho texto={passo.expressao_depois} trecho={passo.trecho_depois} classe="trecho trecho--resultado" />
                      </dd>
                    </div>
                  </dl>
                </div>
              </li>
            ))}
          </ol>

          <footer className="resultado-final">
            <p className="rotulo-campo">Expressão Resultante</p>
            <p className="mono resultado-final__expressao">{resolucao.expressao_final}</p>
            {resolucao.passos.length === 0 ? (
              <p className="texto-secundario">Nenhuma simplificação adicional foi identificada.</p>
            ) : (
              <p className="texto-secundario pequeno">
                Iterações: {resolucao.passos.length} · {MOTIVOS[resolucao.motivo_parada] ?? ''}
              </p>
            )}
          </footer>
        </>
      )}
    </section>
  );
}
