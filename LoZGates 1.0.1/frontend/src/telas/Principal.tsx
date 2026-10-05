import { useEffect, useRef } from 'react';
import { Botao } from '../componentes/Botao';
import { CabecalhoDaTela } from '../componentes/CabecalhoDaTela';
import { CampoDeExpressao, type ControleDoCampo } from '../componentes/CampoDeExpressao';
import { TecladoDeOperadores } from '../componentes/TecladoDeOperadores';
import { useAplicacao } from '../estado/Aplicacao';

/** Para começar sem saber a sintaxe: tocar num exemplo o coloca no campo. */
const EXEMPLOS = ['(A & B) | !C', 'A > B', 'A <> B', '!(A | B)', '(P > Q) & (Q > R)'];

/** Tela "Expressões & Circuitos" (principal_card de expression_screen.py). */
export function Principal() {
  const app = useAplicacao();
  const campo = useRef<ControleDoCampo>(null);

  // go_back_to(principal): entrada.focus_set()
  useEffect(() => {
    campo.current?.focar();
  }, []);

  return (
    <main className="pagina pagina--formulario">
      <CabecalhoDaTela secao="2.1 · Expressões & Circuitos" titulo="Expressão Lógica Proposicional" aoVoltar={() => app.voltarPara('inicio')} />

      <div className="folha-expressao">
        <section className="painel folha-expressao__entrada" aria-labelledby="titulo-principal">
          <h2 id="titulo-principal" className="titulo-painel">
            <span className="rotulo-secao">1</span> Digite a expressão
          </h2>
          <CampoDeExpressao
            ref={campo}
            id="expressao-principal"
            rotulo="Expressão em lógica proposicional"
            valor={app.entrada}
            aoMudar={app.definirEntrada}
            aoConfirmar={app.confirmarExpressao}
            placeholder="Ex.: (A & B) | !C"
          />
          <TecladoDeOperadores aoInserir={(texto) => campo.current?.inserir(texto)} />
          <div className="folha-expressao__acoes">
            <Botao estilo="sucesso" onClick={app.confirmarExpressao}>
              ✓&nbsp;&nbsp;Confirmar Expressão
            </Botao>
            {app.verCircuito && (
              <Botao onClick={() => void app.trocarParaAbas()} className="botao--surgir" disabled={app.gerandoCircuito || app.ocupado}>
                {app.gerandoCircuito ? 'Processando...' : 'Ver Circuito →'}
              </Botao>
            )}
          </div>
        </section>

        <aside className="folha-expressao__lateral">
          <section className="painel" aria-labelledby="titulo-exemplos">
            <h2 id="titulo-exemplos" className="titulo-painel">
              <span className="rotulo-secao">2</span> Exemplos
            </h2>
            <ul className="exemplos">
              {EXEMPLOS.map((exemplo) => (
                <li key={exemplo}>
                  <button
                    type="button"
                    className="exemplo mono"
                    onClick={() => {
                      app.definirEntrada(exemplo);
                      campo.current?.focar();
                    }}
                  >
                    {exemplo}
                  </button>
                </li>
              ))}
            </ul>
          </section>
          <section className="painel" aria-labelledby="titulo-problemas">
            <h2 id="titulo-problemas" className="titulo-painel">
              <span className="rotulo-secao">3</span> Problemas do mundo real
            </h2>
            <p className="texto-secundario pequeno">Situações para traduzir em lógica proposicional e conferir a resposta.</p>
            <Botao estilo="fantasma" onClick={() => app.mostrarTela('problemas')}>
              ⚑&nbsp;&nbsp;Banco de Problemas
            </Botao>
          </section>
        </aside>
      </div>
    </main>
  );
}
