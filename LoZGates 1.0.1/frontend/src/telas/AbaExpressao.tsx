import { Botao } from '../componentes/Botao';
import { PREFIXO_LABEL_CONVERTIDA, useAplicacao } from '../estado/Aplicacao';

/** Como cada conectivo vira álgebra booleana (a mesma tabela do manual). */
const REGRAS = [
  ['A & B', 'A*B'],
  ['A | B', 'A+B'],
  ['!A', '~A'],
  ['A > B', '~A+B'],
  ['A <> B', '(~A+B)*(~B+A)'],
];

/** Aba "Expressão": conversão, simplificações, tabela verdade e ajuda da IA. */
export function AbaExpressao() {
  const app = useAplicacao();
  const expressaoDigitada = () => app.entrada.trim().toUpperCase();
  const convertida = app.labelConvertida?.replace(PREFIXO_LABEL_CONVERTIDA, '') ?? null;

  return (
    <div className="aba-expressao">
      <section className="painel aba-expressao__conversao" aria-labelledby="titulo-conversao">
        <h2 id="titulo-conversao" className="titulo-painel">
          <span className="rotulo-secao">3.1</span> Conversão para álgebra booleana
        </h2>
        <div className="aba-expressao__conversao-corpo">
          <div className="aba-expressao__acao">
            <p className="texto-secundario pequeno">
              Cada conectivo da lógica proposicional vira uma operação da álgebra booleana; os parênteses que não mudam nada saem.
            </p>
            <Botao onClick={() => void app.executarConversao()}>Realizar conversão</Botao>
          </div>
          <table className="regras-conversao mono" aria-label="Regras de conversão">
            <thead>
              <tr>
                <th scope="col">Lógica</th>
                <th scope="col">Álgebra booleana</th>
              </tr>
            </thead>
            <tbody>
              {REGRAS.map(([logica, booleana]) => (
                <tr key={logica}>
                  <td>{logica}</td>
                  <td>{booleana}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {convertida !== null && (
          <dl className="resultado-conversao" role="status">
            <div>
              <dt className="resultado-conversao__rotulo">Lógica proposicional</dt>
              <dd className="mono">{expressaoDigitada()}</dd>
            </div>
            <div>
              <dt className="resultado-conversao__rotulo">Expressão em Álgebra Booleana</dt>
              <dd className="mono resultado-conversao__booleana">{convertida}</dd>
            </div>
          </dl>
        )}
      </section>

      <section className="painel" aria-labelledby="titulo-simplificacao">
        <h2 id="titulo-simplificacao" className="titulo-painel">
          <span className="rotulo-secao">3.2</span> Simplificação
        </h2>
        {app.botoesSimplificar ? (
          <div className="opcoes-simplificacao">
            <article className="cartao-opcao">
              <h3 className="cartao-opcao__titulo">Resultado</h3>
              <p className="texto-secundario pequeno">As leis são aplicadas automaticamente, e cada passo aparece com a lei usada.</p>
              <Botao onClick={() => void app.simplificarResultado()} disabled={app.simplificando}>
                Simplificar - Resultado
              </Botao>
            </article>
            <article className="cartao-opcao">
              <h3 className="cartao-opcao__titulo">Interativo</h3>
              <p className="texto-secundario pequeno">Você escolhe a lei a cada passo, com desfazer e histórico.</p>
              <Botao onClick={app.simplificarInterativo}>Simplificar - Interativo</Botao>
            </article>
          </div>
        ) : (
          <p className="texto-secundario pequeno">Faça a conversão primeiro: a simplificação parte da expressão em álgebra booleana.</p>
        )}
      </section>

      <section className="painel" aria-labelledby="titulo-analise">
        <h2 id="titulo-analise" className="titulo-painel">
          <span className="rotulo-secao">3.3</span> Análise
        </h2>
        <div className="linha-botoes linha-botoes--inicio">
          <Botao estilo="fantasma" onClick={() => void app.exibirTabelaVerdade(expressaoDigitada())}>
            Tabela Verdade
          </Botao>
          <Botao estilo="fantasma" onClick={() => app.abrirDuvidaExpressao(expressaoDigitada())}>
            Pedir ajuda à IA
          </Botao>
        </div>
      </section>
    </div>
  );
}
