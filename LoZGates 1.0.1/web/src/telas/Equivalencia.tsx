import { useState } from 'react';
import { Botao } from '../componentes/Botao';
import { TopoTela } from '../componentes/TopoTela';
import { useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';
import { chamar, type RespostaApi } from '../motor/pyodide';
import { LegendaOperadores } from './Principal';

/** frame_equivalencia — "Equivalência Lógica" */
export function Equivalencia() {
  const app = useAplicacao();
  const janelas = useJanelas();
  // go_back_to() sempre limpa entrada2/entrada3 e esconde o resultado; aqui isso
  // acontece naturalmente porque o estado é desta tela.
  const [expressao1, setExpressao1] = useState('');
  const [expressao2, setExpressao2] = useState('');
  const [resultado, setResultado] = useState<boolean | null>(null);

  const comparar = () => {
    const r = chamar<RespostaApi & { equivalente: boolean }>('comparar', expressao1, expressao2);
    if (!r.ok) {
      if (r.popup) janelas.popupErro(r.popup);
      return;
    }
    setResultado(r.equivalente);
  };

  return (
    <main className="tela tela--estreita">
      <TopoTela voltar={{ acao: () => app.voltarPara('inicio') }} />
      <form
        className="formulario-central"
        aria-labelledby="titulo-equivalencia"
        onSubmit={(e) => {
          e.preventDefault();
          comparar();
        }}
      >
        <h1 id="titulo-equivalencia" className="titulo-formulario">
          Digite as expressões que deseja comparar:
        </h1>
        <input
          className="campo campo--expressao"
          placeholder="Primeira expressão"
          aria-label="Primeira expressão"
          value={expressao1}
          spellCheck={false}
          autoComplete="off"
          autoFocus
          onChange={(e) => setExpressao1(e.target.value)}
        />
        <input
          className="campo campo--expressao"
          placeholder="Segunda expressão"
          aria-label="Segunda expressão"
          value={expressao2}
          spellCheck={false}
          autoComplete="off"
          onChange={(e) => setExpressao2(e.target.value)}
        />
        <LegendaOperadores />
        <div className="pilha-botoes">
          <Botao estilo="sucesso" type="submit">
            ✅Comparar
          </Botao>
        </div>
        <p className="resultado-equivalencia" role="status" aria-live="polite">
          {resultado === true && <span className="cor-sucesso">✅ São equivalentes!</span>}
          {resultado === false && <span className="cor-erro">❌ Não são equivalentes</span>}
        </p>
      </form>
    </main>
  );
}
