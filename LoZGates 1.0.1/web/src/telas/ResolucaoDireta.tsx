import type { ResultadoSimplificacao } from '../api/tipos';
import { Botao } from '../componentes/Botao';
import { useAplicacao } from '../estado/Aplicacao';

/** frame_resolucao_direta — "Solução da expressão:" + StepView. */
export function ResolucaoDireta() {
  const app = useAplicacao();
  return (
    <main className="tela tela--media">
      <h1 className="titulo-secao titulo-centralizado">Solução da expressão:</h1>
      <VistaPassos resolucao={app.resolucao} processando={app.simplificando} />
      <div className="pilha-botoes">
        <Botao estilo="voltar" onClick={app.voltarParaAbas} disabled={app.simplificando}>
          Voltar
        </Botao>
      </div>
    </main>
  );
}

/**
 * StepView (FrontEnd/components/step_view.py). Os passos chegam prontos da API
 * (antes vinham do texto impresso pelo simplificador, lido pelo StepParser).
 */
function VistaPassos({ resolucao, processando }: { resolucao: ResultadoSimplificacao | null; processando: boolean }) {
  return (
    <section className="vista-passos" aria-labelledby="titulo-progresso" aria-busy={processando}>
      <h2 id="titulo-progresso" className="titulo-secao">
        {processando ? 'Simplificando expressão...' : 'Progresso da Simplificação'}
      </h2>
      {resolucao && (
        <>
          <ol className="lista-passos" aria-live="polite">
            <li className="cartao-passo cartao-passo--inicial">
              <p className="cartao-passo__titulo">Expressão Inicial</p>
              <p className="mono cartao-passo__expressao">{resolucao.expressao_booleana}</p>
            </li>
            {resolucao.passos.map((passo, i) => (
              <li key={passo.iteracao} className="cartao-passo cartao-passo--entrada">
                <p className="cartao-passo__titulo">
                  Iteração {i + 1} — {passo.lei}
                </p>
                <p className="texto-secundario mono">Subexpressão: {passo.subexpressao_antes}</p>
                <p className="cartao-passo__transformacao mono">
                  {passo.subexpressao_antes} → {passo.subexpressao_depois}
                </p>
                <p className="cartao-passo__status cor-sucesso mono">✔ {passo.expressao_depois}</p>
              </li>
            ))}
          </ol>

          <footer className="resultado-final">
            <p className="cartao-passo__titulo">Expressão Resultante</p>
            <p className="mono resultado-final__expressao">{resolucao.expressao_final}</p>
            {resolucao.passos.length === 0 && <p className="texto-secundario">Nenhuma simplificação adicional foi identificada.</p>}
            {resolucao.passos.length > 0 && <p className="texto-secundario pequeno">Iterações: {resolucao.passos.length}</p>}
          </footer>
        </>
      )}
    </section>
  );
}
