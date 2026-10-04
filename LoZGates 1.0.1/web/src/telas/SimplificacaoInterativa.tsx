import { useEffect, useRef, useState } from 'react';
import { Botao } from '../componentes/Botao';
import { TopoTela } from '../componentes/TopoTela';
import { BOTOES_LEIS } from '../dados/leis';
import { useAplicacao } from '../estado/Aplicacao';
import { useJanelas } from '../estado/Janelas';
import { chamar, type RespostaApi } from '../motor/pyodide';

type Cartao =
  | { tipo: 'inicial'; titulo: string; expressao: string }
  | { tipo: 'sucesso'; titulo: string; subexpressao: string; transformacao: string; status: string }
  | { tipo: 'pular'; titulo: string; texto: string };

interface EstadoInterativo {
  expressao: string;
  analise: { texto: string; cor: 'texto-primario' | 'texto-secundario' | 'sucesso' };
  cartoes: Cartao[];
  leis_habilitadas: boolean;
  pular_habilitado: boolean;
  desfazer_habilitado: boolean;
}

interface RespostaInterativo extends RespostaApi {
  estado: EstadoInterativo;
  popups: string[];
  destino?: 'principal' | 'abas';
}

/** frame_interativo — "Simplificar - Interativo" (parte_interativa e botões) */
export function SimplificacaoInterativa() {
  const app = useAplicacao();
  const janelas = useJanelas();
  const [estado, setEstado] = useState<EstadoInterativo | null>(null);
  const fimPassos = useRef<HTMLLIElement>(null);
  const iniciado = useRef(false);

  const aplicar = (r: RespostaInterativo) => {
    if (r.ok) setEstado(r.estado);
    r.popups?.forEach((p) => janelas.popupErro(p));
  };

  // parte_interativa()
  useEffect(() => {
    if (iniciado.current) return;
    iniciado.current = true;
    const r = chamar<RespostaInterativo>('interativo_iniciar');
    if (!r.ok) {
      if (r.popup) janelas.popupErro(r.popup);
      if (r.destino === 'principal') {
        app.voltarPara('abas');
        app.mostrarTela('principal');
      } else {
        app.voltarPara('abas');
      }
      return;
    }
    aplicar(r);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-scroll para o final (scroll_passos.yview_moveto(1.0))
  useEffect(() => {
    fimPassos.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [estado?.cartoes.length]);

  const abrirChatIA = () => {
    const r = chamar<RespostaApi & { expressao: string; contexto: string }>('interativo_contexto_ia');
    if (r.ok) janelas.abrirChat(r.expressao, r.contexto);
    else janelas.popupErro(`Erro ao abrir chat com IA: ${r.mensagem ?? ''}`);
  };

  const voltar = () => {
    // finalizar_sessao_expressao(), limpar_frame_interativo(), go_back_to(frame_abas)
    app.voltarPara('abas');
  };

  if (!estado) {
    return (
      <main className="tela tela--larga">
        <TopoTela voltar={{ acao: voltar }} titulo="Simplificação interativa" />
      </main>
    );
  }

  return (
    <main className="tela tela--larga">
      <TopoTela voltar={{ acao: voltar }} titulo="Simplificação interativa" />
      <div className="interativo">
        <div className="interativo__trabalho">
          {/* 1. Expressão Inicial */}
          <section className="painel painel--claro" aria-labelledby="titulo-expr-inicial">
            <div className="painel__cabecalho">
              <h2 id="titulo-expr-inicial" className="painel__titulo">
                Expressão Inicial
              </h2>
              <Botao tamanho="pequeno" onClick={abrirChatIA}>
                🤖 Sugestão de IA
              </Botao>
            </div>
            <p className="mono interativo__expressao">{estado.expressao}</p>
          </section>

          {/* 2. Análise Atual */}
          <section className="painel" aria-labelledby="titulo-analise">
            <h2 id="titulo-analise" className="painel__titulo">
              Análise
            </h2>
            <p className={`interativo__analise cor-${estado.analise.cor}`} role="status" aria-live="polite">
              {estado.analise.texto}
            </p>
          </section>

          {/* 4. Seleção de Leis */}
          <section className="painel" aria-labelledby="titulo-leis">
            <h2 id="titulo-leis" className="painel__titulo">
              Selecione uma Lei para Aplicar:
            </h2>
            <div className="grade-leis">
              {BOTOES_LEIS.map((lei) => (
                <Botao
                  key={lei.idx}
                  className="botao-lei"
                  disabled={!estado.leis_habilitadas}
                  onClick={() => aplicar(chamar<RespostaInterativo>('interativo_lei', lei.idx))}
                >
                  <span>{lei.texto}</span>
                  <small className="mono">({lei.desc})</small>
                </Botao>
              ))}
            </div>
          </section>

          {/* 5. Controles */}
          <div className="linha-botoes linha-botoes--inicio">
            <Botao
              disabled={!estado.desfazer_habilitado}
              onClick={() => aplicar(chamar<RespostaInterativo>('interativo_desfazer'))}
            >
              ↩ Desfazer
            </Botao>
            <Botao disabled={!estado.pular_habilitado} onClick={() => aplicar(chamar<RespostaInterativo>('interativo_pular'))}>
              ↪ Pular
            </Botao>
          </div>
        </div>

        {/* 3. Passos da Simplificação */}
        <section className="painel painel--escuro interativo__passos" aria-labelledby="titulo-passos">
          <h2 id="titulo-passos" className="painel__titulo">
            Passos da Simplificação
          </h2>
          <ol className="lista-passos lista-passos--rolavel">
            {estado.cartoes.map((c, i) => (
              <li
                key={`${i}-${c.titulo}`}
                ref={i === estado.cartoes.length - 1 ? fimPassos : undefined}
                className={`cartao-passo cartao-passo--${c.tipo}`}
              >
                <p className="cartao-passo__titulo">{c.titulo}</p>
                {c.tipo === 'inicial' && <p className="mono cartao-passo__expressao">{c.expressao}</p>}
                {c.tipo === 'sucesso' && (
                  <>
                    {c.subexpressao && <p className="texto-secundario mono">{c.subexpressao}</p>}
                    <p className="cartao-passo__transformacao mono">{c.transformacao}</p>
                    <p className="cartao-passo__status cor-sucesso mono">{c.status}</p>
                  </>
                )}
                {c.tipo === 'pular' && <p className="texto-secundario mono">{c.texto}</p>}
              </li>
            ))}
          </ol>
        </section>
      </div>
    </main>
  );
}
