import { useEffect, useRef, useState } from 'react';
import { api, mensagemDe } from '../api/cliente';
import type { EstadoInterativo, ItemHistorico, RespostaInterativa, VisaoInterativa } from '../api/tipos';
import { Botao } from '../componentes/Botao';
import { CabecalhoDaTela } from '../componentes/CabecalhoDaTela';
import { TextoComTrecho } from '../componentes/TextoComTrecho';
import { LEIS_BASICAS, LEIS_ESTRUTURAIS, type BotaoLei } from '../dados/leis';
import { useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';
import { registrar, registrarEventos } from '../telemetria/registro';

/** Texto da zona "Subexpressão em análise" (ResolverScreen.atualizar_ui). */
function analise(visao: VisaoInterativa | null): { texto: string; cor: 'sucesso' | 'aviso' | 'primario' | 'secundario' } {
  if (!visao) return { texto: 'Aguardando início da análise...', cor: 'secundario' };
  switch (visao.motivo_parada) {
    case 'no_further_simplification':
      return { texto: '✓  Expressão totalmente simplificada!', cor: 'sucesso' };
    case 'maximum_steps':
      return { texto: '!  Limite máximo de transformações atingido.', cor: 'aviso' };
    case 'repeated_state':
      return { texto: '!  Transformação resultou em estado repetido.', cor: 'aviso' };
    // A lei se aplica, mas o resultado não é menor: o motor desfaz a troca (como no desktop)
    case 'no_progress':
      return { texto: '!  Esta lei se aplica, mas não reduz a expressão.', cor: 'aviso' };
  }
  if (visao.subexpressao) return { texto: visao.subexpressao, cor: 'primario' };
  return { texto: 'Aguardando próxima análise...', cor: 'secundario' };
}

function ItemDoHistorico({ item }: { item: ItemHistorico }) {
  switch (item.tipo) {
    case 'inicial':
      return (
        <li className="registro-passos__item registro-passos__item--inicial">
          <span className="registro-passos__marca mono" aria-hidden="true">
            0
          </span>
          <div className="registro-passos__corpo">
            <p className="registro-passos__titulo">Expressão inicial</p>
            <p className="mono registro-passos__expressao">{item.expressao}</p>
          </div>
        </li>
      );
    case 'lei':
      return (
        <li className="registro-passos__item">
          <span className="registro-passos__marca mono" aria-hidden="true">
            {item.passo}
          </span>
          <div className="registro-passos__corpo">
            <p className="registro-passos__titulo">
              Passo {item.passo} <span className="registro-passos__lei">{item.lei}</span>
            </p>
            <dl className="registro-passos__contexto mono">
              <div>
                <dt>antes</dt>
                <dd>{item.antes}</dd>
              </div>
              <div>
                <dt>depois</dt>
                <dd className="cor-sucesso">{item.depois}</dd>
              </div>
            </dl>
          </div>
        </li>
      );
    case 'pulo':
      return (
        <li className="registro-passos__item registro-passos__item--pulo">
          <span className="registro-passos__marca mono" aria-hidden="true">
            →
          </span>
          <div className="registro-passos__corpo">
            <p className="registro-passos__titulo">Subexpressão pulada</p>
            <p className="mono texto-secundario">{item.subexpressao}</p>
          </div>
        </li>
      );
  }
}

/**
 * "Simplificar - Interativo" (ResolverScreen + ResolverController). As regras
 * rodam no servidor sem guardar nada: a cada ação mandamos o estado atual e
 * recebemos o próximo (D4).
 */
export function SimplificacaoInterativa() {
  const app = useAplicacao();
  const janelas = useJanelas();
  const [visao, setVisao] = useState<VisaoInterativa | null>(null);
  const [aguardando, setAguardando] = useState(false);
  const estado = useRef<EstadoInterativo | null>(null);
  const inicio = useRef(performance.now());
  const iniciado = useRef(false);
  const listaDoHistorico = useRef<HTMLOListElement>(null);

  const aplicarResposta = (resposta: RespostaInterativa) => {
    estado.current = resposta.estado;
    setVisao(resposta.visao);
    registrarEventos(resposta.eventos);
    if (resposta.mensagem) janelas.popupErro(resposta.mensagem);
  };

  const executar = async (acao: (estado: EstadoInterativo) => Promise<RespostaInterativa>, mensagemDeFalha: string) => {
    if (aguardando || !estado.current) return;
    setAguardando(true);
    try {
      aplicarResposta(await acao(estado.current));
    } catch (erro) {
      console.warn(erro);
      janelas.popupErro(`${mensagemDeFalha} (${mensagemDe(erro)})`);
    } finally {
      setAguardando(false);
    }
  };

  // initialize_if_needed(): cada entrada nesta tela começa uma sessão nova
  useEffect(() => {
    if (iniciado.current) return;
    iniciado.current = true;
    inicio.current = performance.now();
    setAguardando(true);
    api
      .iniciarInterativa(app.expressaoGlobal)
      .then(aplicarResposta)
      .catch((erro: unknown) => janelas.popupErro(`Não foi possível iniciar a simplificação: ${mensagemDe(erro)}`))
      .finally(() => setAguardando(false));
  }, []); // uma sessão por montagem da tela

  // O histórico rola para o fim a cada passo (yview_moveto(1.0)), sem mexer na página
  useEffect(() => {
    const lista = listaDoHistorico.current;
    if (lista) lista.scrollTop = lista.scrollHeight;
  }, [visao?.historico.length]);

  const aplicarLei = (lei: BotaoLei) =>
    void executar((e) => api.aplicarLei(e, lei.idx), 'Não foi possível aplicar a lei selecionada.');
  const pular = () => void executar(api.pular, 'Não foi possível pular a subexpressão.');
  const desfazer = () => void executar(api.desfazer, 'Não foi possível desfazer.');

  const abrirChatIA = () => {
    const expressao = visao?.expressao ?? app.expressaoGlobal;
    const contexto = visao?.subexpressao ? `Analisando subexpressão: ${visao.subexpressao}` : '';
    janelas.abrirChat(expressao, contexto);
  };

  // voltar_tela(): encerra a sessão (registra a conclusão, como o desktop) e vai para o início
  const voltar = () => {
    if (visao && !visao.concluida) {
      registrar('log_simplification_completed', visao.contador_passos, (performance.now() - inicio.current) / 1000);
    }
    app.mostrarTela('inicio');
  };

  const { texto, cor } = analise(visao);
  const concluida = visao?.concluida ?? false;
  // Sem subexpressão em análise, leis e Pular não fazem nada no motor: ficam desabilitados
  const semAnalise = !visao?.subexpressao;
  const leisDesabilitadas = !visao || concluida || aguardando || semAnalise;

  const grupoDeLeis = (titulo: string, leis: BotaoLei[]) => (
    <div className="grupo-leis">
      <h3 className="grupo-leis__titulo">{titulo}</h3>
      <div className="grade-leis">
        {leis.map((lei) => (
          <Botao key={lei.idx} estilo="lei" className="botao-lei" disabled={leisDesabilitadas} onClick={() => aplicarLei(lei)}>
            <span>{lei.texto}</span>
            <small className="mono">{lei.desc}</small>
          </Botao>
        ))}
      </div>
    </div>
  );

  // Duas colunas: à esquerda o estado atual, as leis e os controles (sempre à vista);
  // à direita o histórico, que rola sozinho. O Voltar fica com Pular e Desfazer.
  return (
    <main className="pagina pagina--simplificacao resolver" aria-busy={aguardando}>
      <CabecalhoDaTela secao="3.2 · Simplificação · Interativa" titulo="Escolha a lei a cada passo" />
      <div className="resolver__colunas">
        <div className="resolver__principal">
          {/* ZONA 1 — contexto: expressão atual e subexpressão em análise */}
          <section className="painel resolver__zona" aria-labelledby="titulo-expressao-atual">
            <div className="painel__cabecalho">
              <h2 id="titulo-expressao-atual" className="titulo-painel">
                <span className="rotulo-secao">1</span> Expressão Atual
              </h2>
              <Botao estilo="fantasma" tamanho="pequeno" onClick={abrirChatIA} aria-label="Pedir sugestão à IA">
                Pedir ajuda à IA
              </Botao>
            </div>
            <p className="mono resolver__expressao">
              {visao ? <TextoComTrecho texto={visao.expressao} trecho={visao.trecho} classe="trecho-em-analise" /> : app.expressaoGlobal}
            </p>
            <p className="resolver__rotulo-analise">▼&nbsp;&nbsp;Subexpressão em análise:</p>
            <p className={`resolver__analise resolver__analise--${cor}`} role="status" aria-live="polite">
              {texto}
            </p>
            {visao?.motivo_parada === 'no_progress' && (
              <p className="resolver__dica">
                {visao.pode_desfazer
                  ? 'Use ↶ Desfazer para voltar à subexpressão anterior e tentar outra lei.'
                  : 'Use Voltar para recomeçar e tentar outra lei.'}
              </p>
            )}
            <p className="resolver__progresso texto-secundario pequeno">
              {visao ? `${visao.contador_passos} ${visao.contador_passos === 1 ? 'lei aplicada' : 'leis aplicadas'}` : '…'}
            </p>
          </section>

          {/* ZONA 2 — leis */}
          <section className="painel resolver__zona" aria-labelledby="titulo-leis">
            <h2 id="titulo-leis" className="titulo-painel">
              <span className="rotulo-secao">2</span> Escolha uma Lei para Aplicar
            </h2>
            {grupoDeLeis('Básicas', LEIS_BASICAS)}
            {grupoDeLeis('Estruturais', LEIS_ESTRUTURAIS)}
          </section>

          {/* ZONA 3 — controles, logo abaixo das leis */}
          <div className="resolver__controles">
            <Botao onClick={pular} disabled={!visao || concluida || aguardando || semAnalise}>
              Pular →
            </Botao>
            <Botao estilo="aviso" onClick={desfazer} disabled={!visao?.pode_desfazer || aguardando}>
              ↶ Desfazer
            </Botao>
            <Botao estilo="voltar" onClick={voltar}>
              Voltar
            </Botao>
          </div>
        </div>

        {/* Histórico, na coluna da direita */}
        <section className="painel resolver__historico" aria-labelledby="titulo-historico">
          <h2 id="titulo-historico" className="titulo-painel">
            <span className="rotulo-secao">3</span> Histórico de Passos
          </h2>
          <ol ref={listaDoHistorico} className="registro-passos lista-passos--historico">
            {visao?.historico.map((item, i) => (
              <ItemDoHistorico key={i} item={item} />
            ))}
          </ol>
        </section>
      </div>
    </main>
  );
}
