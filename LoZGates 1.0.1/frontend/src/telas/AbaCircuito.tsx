import { useEffect, useMemo, useRef, useState } from 'react';
import { api, dadosFixos, mensagemDe } from '../api/cliente';
import type { TabelaVerdade } from '../api/tipos';
import { Botao } from '../componentes/Botao';
import { CircuitoVivo } from '../circuito/CircuitoVivo';
import { DiagramaDeTempo } from '../circuito/DiagramaDeTempo';
import { combinacaoDoIndice, indiceDaCombinacao } from '../circuito/diagrama';
import { exportarPng } from '../circuito/exportarPng';
import { TabelaCompacta } from '../circuito/TabelaCompacta';
import { PREFIXO_LABEL_CIRCUITO, useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';

/** Até quantas variáveis o diagrama de tempo cabe com folga (64 fatias). */
const VARIAVEIS_NO_DIAGRAMA = 6;

const CONCLUSOES: Record<string, string> = {
  tautologia: 'Tautologia',
  contradicao: 'Contradição',
  satisfativel: 'Satisfatível',
};

/**
 * Aba "Circuito": o circuito da expressão com os sinais das entradas atuais,
 * a tabela-verdade e o diagrama de tempo, todos apontando para a mesma
 * combinação. Os níveis lógicos vêm do servidor (layout.py e tabela.py).
 */
export function AbaCircuito() {
  const app = useAplicacao();
  const janelas = useJanelas();
  const svg = useRef<SVGSVGElement>(null);
  const [duvida, setDuvida] = useState<string | null>(null);
  const [tabela, setTabela] = useState<TabelaVerdade | null>(null);
  const [erroTabela, setErroTabela] = useState<string | null>(null);

  const expressao = app.labelCircuito.startsWith(PREFIXO_LABEL_CIRCUITO)
    ? app.labelCircuito.slice(PREFIXO_LABEL_CIRCUITO.length)
    : app.labelCircuito;

  useEffect(() => {
    dadosFixos
      .conteudo()
      .then((c) => setDuvida(c.duvida_circuitos))
      .catch(() => setDuvida(null));
  }, []);

  useEffect(() => {
    if (!expressao) return;
    let valido = true;
    setTabela(null);
    setErroTabela(null);
    api
      .tabelaVerdade(expressao)
      .then((t) => valido && setTabela(t))
      .catch((e: unknown) => valido && setErroTabela(mensagemDe(e)));
    return () => {
      valido = false;
    };
  }, [expressao]);

  const variaveis = app.variaveis;
  const atual = indiceDaCombinacao(variaveis, app.valores);
  const escolher = (indice: number) => app.definirValores(combinacaoDoIndice(variaveis, indice));
  const total = 2 ** variaveis.length;
  const saida = app.layout?.valor ?? (tabela ? Boolean(tabela.resultados_finais[atual]) : null);
  const linhasDaTabela = useMemo(() => tabela?.tabela.map((linha) => linha.slice(0, tabela.total_variaveis)) ?? null, [tabela]);
  const variaveisDaTabela = useMemo(() => tabela?.colunas.slice(0, tabela.total_variaveis) ?? [], [tabela]);

  // salvar_imagem()
  const salvarImagem = async () => {
    if (!app.layout || !svg.current) {
      janelas.popupErro('Imagem não encontrada.');
      return;
    }
    try {
      await exportarPng(svg.current, 'circuito.png');
      janelas.popupErro('Imagem salva com sucesso!', 'LoZ Gates');
    } catch (erro) {
      janelas.popupErro(`Erro ao salvar imagem: ${mensagemDe(erro)}`);
    }
  };

  return (
    <div className="tela-circuito">
      <section className="painel painel-circuito" aria-labelledby="titulo-figura-circuito">
        <header className="painel__cabecalho">
          <h2 id="titulo-figura-circuito" className="titulo-painel">
            <span className="rotulo-secao">Figura 1</span> Circuito lógico
          </h2>
          <div className="painel__acoes">
            <button
              type="button"
              className="botao botao--fantasma botao--icone"
              aria-label="Ajuda rápida sobre circuitos"
              disabled={duvida === null}
              onClick={() => duvida !== null && janelas.popupDuvida(duvida)}
            >
              ?
            </button>
            <Botao tamanho="pequeno" onClick={() => void salvarImagem()}>
              Exportar PNG
            </Botao>
          </div>
        </header>
        {app.layout ? (
          <CircuitoVivo ref={svg} layout={app.layout} rotulo={`Circuito lógico de ${expressao}`} />
        ) : (
          <p className="aviso-vazio">{app.gerandoCircuito ? 'Gerando circuito…' : app.textoCircuito}</p>
        )}
      </section>

      <aside className="lateral-circuito">
        <section className="painel" aria-labelledby="titulo-entradas">
          <h2 id="titulo-entradas" className="titulo-painel">
            Entradas
          </h2>
          {variaveis.length === 0 ? (
            <p className="texto-secundario pequeno">A expressão não tem variáveis: a saída é constante.</p>
          ) : (
            <div className="entradas">
              {variaveis.map((nome) => {
                const ligada = Boolean(app.valores[nome]);
                return (
                  <button
                    key={nome}
                    type="button"
                    className={`chave-entrada ${ligada ? 'chave-entrada--1' : ''}`}
                    aria-pressed={ligada}
                    aria-label={`Entrada ${nome}: ${ligada ? '1' : '0'}`}
                    onClick={() => app.definirValores({ ...app.valores, [nome]: !ligada })}
                  >
                    <span className="chave-entrada__nome mono">{nome}</span>
                    <span className="chave-entrada__trilho" aria-hidden="true">
                      <span className="chave-entrada__botao" />
                    </span>
                    <span className="chave-entrada__valor mono">{ligada ? '1' : '0'}</span>
                  </button>
                );
              })}
            </div>
          )}
          <div className="saida-atual" aria-live="polite">
            <span className="mono">S</span>
            <span className={`led-html ${saida ? 'led-html--1' : ''}`} aria-hidden="true" />
            <strong className={`mono ${saida ? 'cor-sinal-1' : 'cor-sinal-0'}`}>{saida === null ? '·' : saida ? '1' : '0'}</strong>
          </div>
          {variaveis.length > 0 && (
            <div className="passos-combinacao">
              <Botao estilo="fantasma" tamanho="pequeno" onClick={() => escolher((atual - 1 + total) % total)}>
                ◂ Anterior
              </Botao>
              <Botao estilo="fantasma" tamanho="pequeno" onClick={() => escolher((atual + 1) % total)}>
                Próxima ▸
              </Botao>
            </div>
          )}
        </section>

        <section className="painel" aria-labelledby="titulo-tabela-compacta">
          <h2 id="titulo-tabela-compacta" className="titulo-painel">
            <span className="rotulo-secao">Tabela 1</span> Tabela-verdade
          </h2>
          {erroTabela && <p className="cor-erro pequeno">{erroTabela}</p>}
          {!tabela && !erroTabela && <p className="texto-secundario pequeno carregando-texto">Calculando…</p>}
          {tabela && linhasDaTabela && (
            <>
              <TabelaCompacta
                variaveis={variaveisDaTabela}
                tabela={linhasDaTabela}
                resultados={tabela.resultados_finais}
                atual={atual}
                aoEscolher={escolher}
              />
              <div className="tabela-compacta__rodape">
                {tabela.tipo_conclusao && (
                  <span className={`selo-conclusao selo-conclusao--${tabela.tipo_conclusao}`}>{CONCLUSOES[tabela.tipo_conclusao]}</span>
                )}
                <button type="button" className="link-discreto" onClick={() => void app.exibirTabelaVerdade(expressao)}>
                  Tabela completa
                </button>
              </div>
            </>
          )}
        </section>
      </aside>

      <section className="painel painel-tempo" aria-labelledby="titulo-diagrama">
        <h2 id="titulo-diagrama" className="titulo-painel">
          <span className="rotulo-secao">Figura 2</span> Diagrama de tempo
        </h2>
        {tabela && linhasDaTabela && tabela.total_variaveis <= VARIAVEIS_NO_DIAGRAMA ? (
          <DiagramaDeTempo
            variaveis={variaveisDaTabela}
            tabela={linhasDaTabela}
            resultados={tabela.resultados_finais}
            atual={atual}
            aoEscolher={escolher}
          />
        ) : (
          <p className="texto-secundario pequeno">
            {tabela ? `O diagrama de tempo aparece para expressões com até ${VARIAVEIS_NO_DIAGRAMA} variáveis.` : '…'}
          </p>
        )}
      </section>
    </div>
  );
}
