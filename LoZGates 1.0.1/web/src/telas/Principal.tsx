import { useEffect, useRef } from 'react';
import { Botao } from '../componentes/Botao';
import { TopoTela } from '../componentes/TopoTela';
import { useAplicacao } from '../estado/Aplicacao';

/** Legenda de operadores aceitos (mesma sintaxe do manual) */
export function LegendaOperadores() {
  return (
    <p className="legenda-operadores">
      <span><kbd>&amp;</kbd> e</span>
      <span><kbd>|</kbd> ou</span>
      <span><kbd>!</kbd> não</span>
      <span><kbd>&gt;</kbd> se… então</span>
      <span><kbd>&lt;&gt;</kbd> se e somente se</span>
    </p>
  );
}

/** principal — "Circuitos e Expressões" */
export function Principal() {
  const app = useAplicacao();
  const campo = useRef<HTMLInputElement>(null);

  // go_back_to(principal): entrada.focus_set()
  useEffect(() => {
    campo.current?.focus();
  }, []);

  return (
    <main className="tela tela--estreita">
      <TopoTela voltar={{ acao: () => app.voltarPara('inicio') }} />
      <section className="formulario-central" aria-labelledby="titulo-principal">
        <h1 id="titulo-principal" className="titulo-formulario">
          Digite a expressão em Lógica Proposicional:
        </h1>
        <input
          ref={campo}
          className="campo campo--expressao"
          placeholder="Digite aqui"
          aria-label="Expressão em lógica proposicional"
          value={app.entrada}
          spellCheck={false}
          autoCapitalize="characters"
          autoComplete="off"
          onChange={(e) => app.definirEntrada(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') app.confirmarExpressao();
          }}
        />
        <LegendaOperadores />

        <div className="pilha-botoes">
          <Botao estilo="sucesso" onClick={app.confirmarExpressao}>
            ✅Confirmar
          </Botao>
          {app.verCircuito && (
            <Botao onClick={() => void app.trocarParaAbas()} className="botao--surgir" disabled={app.ocupado}>
              🔌Ver Circuito
            </Botao>
          )}
          <Botao onClick={() => app.mostrarTela('problemas')}>🔬 Banco de problemas</Botao>
        </div>
      </section>
    </main>
  );
}
