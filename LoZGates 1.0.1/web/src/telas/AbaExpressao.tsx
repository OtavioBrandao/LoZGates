import { Botao } from '../componentes/Botao';
import { useAplicacao } from '../estado/Aplicacao';

/** Aba "Expressão": conversão, simplificação, tabela verdade e ajuda da IA */
export function AbaExpressao() {
  const app = useAplicacao();
  const expressaoDigitada = () => app.entrada.trim().toUpperCase();

  return (
    <div className="aba-expressao">
      <div className="aba-expressao__grupo">
        <Botao onClick={app.executarConversao}>🔗Realizar conversão</Botao>
        {app.labelConvertida && (
          <p className="resultado-conversao" role="status">
            <span className="resultado-conversao__rotulo">Expressão em Álgebra Booleana:</span>
            <span className="mono">{app.labelConvertida.replace('Expressão em Álgebra Booleana: ', '')}</span>
          </p>
        )}
        {app.botoesSimplificar && (
          <div className="linha-botoes">
            <Botao onClick={() => void app.simplificarResultado()} disabled={app.ocupado}>
              🔍Simplificar - Resultado
            </Botao>
            <Botao onClick={app.simplificarInterativo}>🔎Simplificar - Interativo</Botao>
          </div>
        )}
      </div>

      <div className="linha-botoes aba-expressao__outros">
        <Botao onClick={() => app.exibirTabelaVerdade(expressaoDigitada())}>🔢Tabela Verdade</Botao>
        <Botao onClick={() => app.abrirDuvidaExpressao(expressaoDigitada())}>❓Pedir ajuda à IA</Botao>
      </div>
    </div>
  );
}
