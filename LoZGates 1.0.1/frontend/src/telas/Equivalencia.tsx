import { useEffect, useRef, useState } from 'react';
import { api, ErroDaApi, mensagemDe } from '../api/cliente';
import type { ResultadoEquivalencia } from '../api/tipos';
import { Botao } from '../componentes/Botao';
import { CabecalhoDaTela } from '../componentes/CabecalhoDaTela';
import { CampoDeExpressao, type ControleDoCampo } from '../componentes/CampoDeExpressao';
import { TecladoDeOperadores } from '../componentes/TecladoDeOperadores';
import { useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';
import { registrar } from '../telemetria/registro';
import { compararTabelas, type Comparacao } from './comparacao';

/** Até quantas variáveis a tabela de comparação aparece (64 linhas). */
const VARIAVEIS_NA_COMPARACAO = 6;

interface Resultado extends ResultadoEquivalencia {
  expressao1: string;
  expressao2: string;
}

const bit = (v: boolean | null | undefined) => (v ? '1' : '0');

/**
 * Tela "Equivalência Lógica" (EquivalenceScreen + EquivalenceController).
 * A comparação é só por tabela-verdade (D3d); quando as expressões diferem,
 * o servidor devolve a primeira combinação em que isso acontece.
 */
export function Equivalencia() {
  const app = useAplicacao();
  const janelas = useJanelas();
  // on_back() limpa os campos e o resultado; aqui isso vem de graça porque o estado é desta tela
  const [expressao1, setExpressao1] = useState('');
  const [expressao2, setExpressao2] = useState('');
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [comparacao, setComparacao] = useState<Comparacao | null>(null);
  const [comparando, setComparando] = useState(false);
  const campoA = useRef<ControleDoCampo>(null);
  const campoB = useRef<ControleDoCampo>(null);
  const ativo = useRef<'a' | 'b'>('a');
  const pedido = useRef(0);

  useEffect(() => {
    campoA.current?.focar();
  }, []);

  const comparar = async () => {
    const e1 = expressao1.trim().toUpperCase();
    const e2 = expressao2.trim().toUpperCase();
    if (!e1 || !e2) {
      janelas.popupErro('As expressões não podem estar vazias.');
      return;
    }
    const atual = ++pedido.current;
    setComparando(true);
    setComparacao(null);
    try {
      const dados = await api.equivalencia(e1, e2);
      registrar('log_equivalence_check_with_expressions', e1, e2, dados.equivalentes);
      setResultado({ ...dados, expressao1: e1, expressao2: e2 });
      if (dados.variaveis.length <= VARIAVEIS_NA_COMPARACAO) {
        // A tabela é um complemento: se falhar, o veredito continua valendo
        Promise.all([api.tabelaVerdade(e1), api.tabelaVerdade(e2)])
          .then(([t1, t2]) => atual === pedido.current && setComparacao(compararTabelas(dados.variaveis, t1, t2)))
          .catch((erro: unknown) => console.warn('Não foi possível montar a comparação linha a linha', erro));
      }
    } catch (erro) {
      // Expressão inválida (ValueError no desktop) só gera o aviso; outros erros também vão para o registro
      if (!(erro instanceof ErroDaApi && erro.tipo === 'expressao_invalida')) {
        registrar('log_error', 'equivalence_check_error', mensagemDe(erro), 'comparar_function');
        janelas.popupErro(`Erro ao comparar expressões: ${mensagemDe(erro)}`);
      } else {
        janelas.popupErro(mensagemDe(erro));
      }
    } finally {
      setComparando(false);
    }
  };

  // O teclado não tira o foco do campo: vale o campo focado, ou o último que teve foco
  const inserir = (texto: string) => {
    const focado = document.activeElement?.id;
    if (focado === 'expressao-a' || focado === 'expressao-b') ativo.current = focado === 'expressao-a' ? 'a' : 'b';
    (ativo.current === 'a' ? campoA : campoB).current?.inserir(texto);
  };
  const combinacao = resultado?.contraexemplo
    ? Object.entries(resultado.contraexemplo)
        .map(([nome, valor]) => `${nome} = ${bit(valor)}`)
        .join(', ')
    : '';

  return (
    <main className="pagina pagina--formulario">
      <CabecalhoDaTela secao="2.2 · Equivalência Lógica" titulo="As duas expressões dizem a mesma coisa?" aoVoltar={() => app.mostrarTela('inicio')} />

      <section className="painel equivalencia" aria-labelledby="titulo-equivalencia">
        <h2 id="titulo-equivalencia" className="titulo-painel">
          <span className="rotulo-secao">1</span> Expressões
        </h2>
        <p className="texto-secundario pequeno">
          Duas expressões são equivalentes quando têm o mesmo valor em todas as combinações das variáveis, ou seja, a mesma tabela-verdade.
        </p>
        <div className="equivalencia__campos">
          <CampoDeExpressao
            ref={campoA}
            id="expressao-a"
            rotulo="Expressão A"
            valor={expressao1}
            aoMudar={setExpressao1}
            aoConfirmar={() => void comparar()}
            aoFocar={() => (ativo.current = 'a')}
            placeholder="Ex.: P > Q"
          />
          <span className="equivalencia__simbolo" aria-hidden="true">
            ⟺
          </span>
          <CampoDeExpressao
            ref={campoB}
            id="expressao-b"
            rotulo="Expressão B"
            valor={expressao2}
            aoMudar={setExpressao2}
            aoConfirmar={() => void comparar()}
            aoFocar={() => (ativo.current = 'b')}
            placeholder="Ex.: !P | Q"
          />
        </div>
        <TecladoDeOperadores aoInserir={inserir} />
        <div className="folha-expressao__acoes">
          <Botao estilo="sucesso" onClick={() => void comparar()} disabled={comparando}>
            ⟺&nbsp;&nbsp;Comparar Expressões
          </Botao>
        </div>
      </section>

      <div role="status" aria-live="polite">
        {resultado && (
          <section className="painel equivalencia__resultado" aria-labelledby="titulo-resultado">
            <h2 id="titulo-resultado" className="titulo-painel">
              <span className="rotulo-secao">2</span> Resultado
            </h2>
            <p className={`resultado-equivalencia ${resultado.equivalentes ? 'resultado-equivalencia--sim' : 'resultado-equivalencia--nao'}`}>
              {resultado.equivalentes ? '✓  São equivalentes!' : '✕  Não são equivalentes'}
            </p>
            <p className="equivalencia__explicacao">
              {resultado.equivalentes ? (
                <>
                  <span className="mono">{resultado.expressao1}</span> e <span className="mono">{resultado.expressao2}</span> têm o mesmo valor nas{' '}
                  {2 ** resultado.variaveis.length} combinações {resultado.variaveis.length ? `de ${resultado.variaveis.join(', ')}` : ''}.
                </>
              ) : (
                <>
                  Com <strong className="mono">{combinacao || 'qualquer valor'}</strong>, <span className="mono">{resultado.expressao1}</span> vale{' '}
                  <strong className="mono">{bit(resultado.valor_1)}</strong>, mas <span className="mono">{resultado.expressao2}</span> vale{' '}
                  <strong className="mono">{bit(resultado.valor_2)}</strong>.
                </>
              )}
            </p>

            {comparacao && (
              <figure className="comparacao">
                <figcaption className="titulo-painel">
                  <span className="rotulo-secao">Tabela 1</span> Comparação linha a linha
                  <span className="comparacao__resumo texto-secundario">
                    {comparacao.diferentes === 0
                      ? 'iguais em todas as linhas'
                      : `diferem em ${comparacao.diferentes} de ${comparacao.linhas.length} linhas`}
                  </span>
                </figcaption>
                <div className="comparacao__rolagem">
                  <table className="comparacao__tabela mono">
                    <thead>
                      <tr>
                        {comparacao.variaveis.map((v) => (
                          <th key={v} scope="col">
                            {v}
                          </th>
                        ))}
                        <th scope="col" className="comparacao__saida comparacao__expressao" title={resultado.expressao1}>
                          {resultado.expressao1}
                        </th>
                        <th scope="col" className="comparacao__saida comparacao__expressao" title={resultado.expressao2}>
                          {resultado.expressao2}
                        </th>
                        <th scope="col">iguais</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparacao.linhas.map((linha, i) => (
                        <tr key={i} className={linha.iguais ? '' : 'comparacao__linha--diferente'}>
                          {linha.valores.map((valor, j) => (
                            <td key={j} className={valor ? 'nivel-1' : 'nivel-0'}>
                              {valor}
                            </td>
                          ))}
                          <td className={`comparacao__saida ${linha.primeira ? 'nivel-1' : 'nivel-0'}`}>{linha.primeira}</td>
                          <td className={`comparacao__saida ${linha.segunda ? 'nivel-1' : 'nivel-0'}`}>{linha.segunda}</td>
                          <td className={linha.iguais ? 'cor-sucesso' : 'comparacao__diferenca'}>{linha.iguais ? '=' : '≠'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </figure>
            )}
            {!comparacao && resultado.variaveis.length > VARIAVEIS_NA_COMPARACAO && (
              <p className="texto-secundario pequeno">
                A comparação linha a linha aparece para até {VARIAVEIS_NA_COMPARACAO} variáveis ({2 ** VARIAVEIS_NA_COMPARACAO} linhas).
              </p>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
