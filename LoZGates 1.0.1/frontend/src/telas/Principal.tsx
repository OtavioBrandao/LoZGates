import { useEffect, useRef } from 'react';
import { Botao } from '../componentes/Botao';
import { useAplicacao } from '../estado/Aplicacao';

/** Dica de sintaxe do cartão principal (os mesmos operadores do manual). */
export function LegendaOperadores() {
  return (
    <p className="legenda-operadores">
      <span><kbd>&amp;</kbd> = E (AND)</span>
      <span><kbd>|</kbd> = OU (OR)</span>
      <span><kbd>!</kbd> = NÃO (NOT)</span>
      <span><kbd>&gt;</kbd> = Implica</span>
      <span><kbd>&lt;&gt;</kbd> = Se e somente se</span>
      <span><kbd>( )</kbd> = grupos</span>
    </p>
  );
}

/** Tela "Expressões & Circuitos" (principal_card de expression_screen.py). */
export function Principal() {
  const app = useAplicacao();
  const campo = useRef<HTMLInputElement>(null);

  // go_back_to(principal): entrada.focus_set()
  useEffect(() => {
    campo.current?.focus();
  }, []);

  return (
    <main className="tela tela--estreita">
      <section className="formulario-central cartao-formulario" aria-labelledby="titulo-principal">
        <h1 id="titulo-principal" className="titulo-formulario">
          Expressão Lógica Proposicional
        </h1>
        <LegendaOperadores />
        <input
          ref={campo}
          className="campo campo--expressao"
          placeholder="Ex.: (A & B) | !C"
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

        <div className="pilha-botoes">
          <Botao estilo="sucesso" onClick={app.confirmarExpressao}>
            ✓&nbsp;&nbsp;Confirmar Expressão
          </Botao>
          {app.verCircuito && (
            <Botao onClick={() => void app.trocarParaAbas()} className="botao--surgir" disabled={app.gerandoCircuito || app.ocupado}>
              {app.gerandoCircuito ? 'Processando...' : '🔌 Ver Circuito'}
            </Botao>
          )}
          <Botao onClick={() => app.mostrarTela('problemas')}>⚑&nbsp;&nbsp;Banco de Problemas</Botao>
          <Botao estilo="voltar" onClick={() => app.voltarPara('inicio')}>
            Voltar
          </Botao>
        </div>
      </section>
    </main>
  );
}
