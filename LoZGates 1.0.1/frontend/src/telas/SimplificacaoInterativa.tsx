import { useEffect, useRef, useState } from 'react';
import { api, mensagemDe } from '../api/cliente';
import type { EstadoInterativo, ItemHistorico, RespostaInterativa, VisaoInterativa } from '../api/tipos';
import { Botao } from '../componentes/Botao';
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
  }
  if (visao.subexpressao) return { texto: visao.subexpressao, cor: 'primario' };
  return { texto: 'Aguardando próxima análise...', cor: 'secundario' };
}

/** A expressão atual com a subexpressão em análise destacada. */
function ExpressaoComDestaque({ visao }: { visao: VisaoInterativa }) {
  if (!visao.trecho) return <>{visao.expressao}</>;
  const [inicio, fim] = visao.trecho;
  return (
    <>
      {visao.expressao.slice(0, inicio)}
      <mark className="trecho-em-analise">{visao.expressao.slice(inicio, fim)}</mark>
      {visao.expressao.slice(fim)}
    </>
  );
}

function CartaoDoHistorico({ item }: { item: ItemHistorico }) {
  switch (item.tipo) {
    case 'inicial':
      return (
        <li className="cartao-passo cartao-passo--inicial">
          <p className="cartao-passo__titulo">Expressão inicial:</p>
          <p className="mono">{item.expressao}</p>
        </li>
      );
    case 'lei':
      return (
        <li className="cartao-passo cartao-passo--sucesso">
          <p className="cartao-passo__cabecalho">
            <span className="cor-sucesso">✓&nbsp;&nbsp;Passo {item.passo}:</span>
            <span className="destaque">{item.lei}</span>
          </p>
          <p className="mono texto-secundario">Antes:&nbsp;&nbsp;{item.antes}</p>
          <p className="mono">Depois:&nbsp;&nbsp;{item.depois}</p>
        </li>
      );
    case 'pulo':
      return (
        <li className="cartao-passo cartao-passo--pular">
          <p className="cartao-passo__titulo cor-aviso">→&nbsp;&nbsp;Subexpressão pulada:</p>
          <p className="mono texto-secundario">{item.subexpressao}</p>
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
  const fimDoHistorico = useRef<HTMLLIElement>(null);

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

  // O histórico rola para o fim a cada passo (yview_moveto(1.0))
  useEffect(() => {
    fimDoHistorico.current?.scrollIntoView({ block: 'nearest' });
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
  const leisDesabilitadas = !visao || concluida || aguardando;

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

  return (
    <main className="tela tela--media resolver" aria-busy={aguardando}>
      {/* ZONA 1 — contexto: expressão atual e subexpressão em análise */}
      <section className="painel resolver__zona" aria-labelledby="titulo-expressao-atual">
        <div className="painel__cabecalho">
          <h2 id="titulo-expressao-atual" className="painel__titulo">
            Expressão Atual
          </h2>
          <Botao tamanho="pequeno" onClick={abrirChatIA} aria-label="Pedir sugestão à IA">
            &nbsp;&nbsp;IA
          </Botao>
        </div>
        <p className="mono resolver__expressao">{visao ? <ExpressaoComDestaque visao={visao} /> : app.expressaoGlobal}</p>
        <p className="resolver__rotulo-analise">▼&nbsp;&nbsp;Subexpressão em análise:</p>
        <p className={`resolver__analise resolver__analise--${cor}`} role="status" aria-live="polite">
          {texto}
        </p>
      </section>

      {/* ZONA 2 — leis */}
      <section className="painel resolver__zona" aria-labelledby="titulo-leis">
        <h2 id="titulo-leis" className="painel__titulo">
          Escolha uma Lei para Aplicar
        </h2>
        {grupoDeLeis('Básicas', LEIS_BASICAS)}
        {grupoDeLeis('Estruturais', LEIS_ESTRUTURAIS)}
      </section>

      {/* ZONA 3 — histórico e controles */}
      <section className="painel resolver__zona" aria-labelledby="titulo-historico">
        <h2 id="titulo-historico" className="painel__titulo">
          Histórico de Passos
        </h2>
        <ol className="lista-passos lista-passos--rolavel">
          {visao?.historico.map((item, i) => (
            <CartaoDoHistorico key={i} item={item} />
          ))}
          <li ref={fimDoHistorico} aria-hidden="true" className="lista-passos__fim" />
        </ol>
      </section>

      <div className="resolver__controles">
        <Botao onClick={pular} disabled={!visao || concluida || aguardando}>
          Pular →
        </Botao>
        <Botao estilo="aviso" onClick={desfazer} disabled={!visao?.pode_desfazer || aguardando}>
          ↶ Desfazer
        </Botao>
        <Botao estilo="voltar" onClick={voltar}>
          Voltar
        </Botao>
      </div>
    </main>
  );
}
