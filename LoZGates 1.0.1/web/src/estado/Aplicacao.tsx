/**
 * Controlador da aplicação — equivalente web das funções de navegação e estado de
 * FrontEnd/interface.py (show_frame, go_back_to, confirmar_expressao, trocar_para_abas,
 * on_tab_change, executar_conversao, handle_problem_answer, on_closing...).
 *
 * As regras (o que é limpo ao voltar, quando o circuito interativo é criado/limpo,
 * quais mensagens aparecem) seguem o desktop; a lógica em si roda no Python.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { ponteCircuito } from '../motor/circuito';
import { aguardarPintura, chamar, persistir, type RespostaApi } from '../motor/pyodide';
import { executarPedido, type PedidoHttp } from '../motor/rede';
import { useJanelas } from './Janelas';
import type { DadosTabela } from '../modais/TabelaVerdade';

export type Tela = 'inicio' | 'principal' | 'equivalencia' | 'abas' | 'resolucao' | 'interativo' | 'problemas' | 'encerrada';
export type Aba = 'circuito' | 'interativo' | 'expressao';

/** Nomes das abas exatamente como no CTkTabview (usados no log de navegação). */
export const NOMES_ABAS: Record<Aba, string> = {
  circuito: '      Circuito      ',
  interativo: '  Circuito Interativo  ',
  expressao: '      Expressão      ',
};

export interface ImagemCircuito {
  src: string;
  original: string;
  largura: number;
  altura: number;
}

export interface PassoResolucao {
  iteration: number;
  law: string;
  subexpression?: string;
  before: string;
  after: string;
  success: boolean;
  note?: string | null;
  result_expression?: string;
  t: number;
}

export interface Resolucao {
  expressao_inicial: string;
  passos: PassoResolucao[];
  final: { expressao: string; sucesso: boolean; iteracoes: number; t: number } | null;
  popup?: string | null;
  iniciadoEm: number;
}

interface Estado {
  tela: Tela;
  entrada: string;
  verCircuito: boolean;
  aba: Aba;
  labelCircuito: string;
  imagem: ImagemCircuito | null;
  textoImagem: string;
  expressaoGlobal: string;
  labelConvertida: string | null;
  expressaoBooleanaAtual: string;
  botoesSimplificar: boolean;
  /** circuito_interativo_instance: 0 = não existe; >0 = identificador da instância */
  seletor: number;
  resolucao: Resolucao | null;
  sessaoInterativa: number;
  ocupado: boolean;
}

const ESTADO_INICIAL: Estado = {
  tela: 'inicio',
  entrada: '',
  verCircuito: false,
  aba: 'circuito',
  labelCircuito: '',
  imagem: null,
  textoImagem: '',
  expressaoGlobal: '',
  labelConvertida: null,
  expressaoBooleanaAtual: '',
  botoesSimplificar: false,
  seletor: 0,
  resolucao: null,
  sessaoInterativa: 0,
  ocupado: false,
};

interface RespostaTrocarAbas extends RespostaApi {
  label: string;
  expressao_global: string;
  imagem: string | null;
  imagem_original: string | null;
  largura?: number;
  altura?: number;
  texto_imagem?: string;
}

export interface ApiAplicacao extends Estado {
  mostrarTela: (tela: Tela) => void;
  voltarPara: (destino: Tela) => void;
  definirEntrada: (texto: string) => void;
  confirmarExpressao: () => void;
  trocarParaAbas: () => Promise<void>;
  mudarAba: (aba: Aba) => void;
  garantirSeletor: () => void;
  executarConversao: () => void;
  simplificarResultado: () => Promise<void>;
  voltarParaAbas: () => void;
  simplificarInterativo: () => void;
  exibirTabelaVerdade: (expressao: string) => void;
  abrirDuvidaExpressao: (expressao: string) => void;
  responderProblema: (expressao: string, destino: 'circuit' | 'simplifier' | 'table') => void;
  encerrarSessao: () => Promise<void>;
}

const Contexto = createContext<ApiAplicacao | null>(null);

export function useAplicacao(): ApiAplicacao {
  const api = useContext(Contexto);
  if (!api) throw new Error('useAplicacao fora do ProvedorAplicacao');
  return api;
}

const pngParaUrl = (base64: string) => `data:image/png;base64,${base64}`;

export function ProvedorAplicacao({ children }: { children: ReactNode }) {
  const janelas = useJanelas();
  const [estado, setEstado] = useState<Estado>(ESTADO_INICIAL);
  const ref = useRef<Estado>(ESTADO_INICIAL);
  const contadorSeletor = useRef(0);
  const encerrada = useRef(false);

  const atualizar = useCallback((mudancas: Partial<Estado>) => {
    ref.current = { ...ref.current, ...mudancas };
    setEstado(ref.current);
  }, []);

  const executar = useCallback(
    async (acao: () => void | Promise<void>) => {
      atualizar({ ocupado: true });
      await aguardarPintura();
      try {
        await acao();
      } finally {
        atualizar({ ocupado: false });
      }
    },
    [atualizar],
  );

  // --- show_frame -------------------------------------------------------
  const mostrarTela = useCallback((tela: Tela) => atualizar({ tela }), [atualizar]);

  // --- if_necessary_create_a_circuit / create_interactive_circuit --------
  const garantirSeletor = useCallback(() => {
    if (ref.current.seletor !== 0 || !ref.current.expressaoGlobal) return;
    console.log('Criando interface de seleção de modo...');
    const r = chamar('circuito_novo_seletor', ponteCircuito);
    if (r.ok) {
      contadorSeletor.current += 1;
      atualizar({ seletor: contadorSeletor.current });
    }
  }, [atualizar]);

  // --- go_back_to --------------------------------------------------------
  const voltarPara = useCallback(
    (destino: Tela) => {
      const atual = ref.current;
      const mudancas: Partial<Estado> = { verCircuito: false };

      if (atual.seletor) {
        if (destino === 'abas') {
          console.log('Voltando para abas - mantendo circuito ativo');
        } else {
          chamar('circuito_limpar');
          mudancas.seletor = 0;
          console.log('Circuito interativo limpo');
        }
      }
      // Limpa a entrada apenas se não for para certas telas
      if (!['abas', 'resolucao', 'interativo'].includes(destino)) {
        mudancas.entrada = '';
        mudancas.botoesSimplificar = false;
      }
      // Esconde os resultados da aba de expressão ao voltar apenas se NÃO for para as abas
      if (destino !== 'abas') {
        mudancas.labelConvertida = null;
        mudancas.resolucao = null;
        mudancas.botoesSimplificar = false;
      }
      mudancas.tela = destino;
      atualizar(mudancas);

      if (destino === 'abas' && atual.expressaoGlobal) {
        setTimeout(garantirSeletor, 200);
      }
    },
    [atualizar, garantirSeletor],
  );

  const definirEntrada = useCallback((texto: string) => atualizar({ entrada: texto }), [atualizar]);

  // --- confirmar_expressao ------------------------------------------------
  const confirmarExpressao = useCallback(() => {
    atualizar({ verCircuito: false });
    const r = chamar('confirmar_expressao', ref.current.entrada);
    if (!r.ok) {
      if (r.popup) janelas.popupErro(r.popup);
      return;
    }
    atualizar({ botoesSimplificar: false, verCircuito: true });
  }, [atualizar, janelas]);

  // --- trocar_para_abas ---------------------------------------------------
  const trocarParaAbas = useCallback(
    () =>
      executar(() => {
        const r = chamar<RespostaTrocarAbas>('trocar_para_abas', ref.current.entrada);
        if (!r.ok) {
          if (r.popup) janelas.popupErro(r.popup);
          return;
        }
        atualizar({
          labelCircuito: r.label,
          expressaoGlobal: r.expressao_global,
          imagem:
            r.imagem && r.imagem_original
              ? { src: pngParaUrl(r.imagem), original: pngParaUrl(r.imagem_original), largura: r.largura ?? 0, altura: r.altura ?? 0 }
              : null,
          textoImagem: r.imagem ? '' : r.texto_imagem || 'Imagem do circuito não encontrada',
          tela: 'abas',
        });
        if (r.popup) janelas.popupErro(r.popup);
      }),
    [atualizar, executar, janelas],
  );

  // --- on_tab_change ------------------------------------------------------
  const mudarAba = useCallback(
    (aba: Aba) => {
      atualizar({ aba });
      chamar('mudar_aba', NOMES_ABAS[aba]);
      if (aba === 'interativo') {
        if (!ref.current.expressaoGlobal) {
          console.log('Expressão global não definida - não é possível criar circuito');
          return;
        }
        garantirSeletor();
      }
    },
    [atualizar, garantirSeletor],
  );

  // --- executar_conversao / mostrar_expressao_convertida -------------------
  const executarConversao = useCallback(() => {
    atualizar({ botoesSimplificar: false });
    const r = chamar<RespostaApi & { texto: string; expressao_booleana: string }>('expressao_convertida', ref.current.entrada);
    if (r.ok) {
      atualizar({ labelConvertida: r.texto, expressaoBooleanaAtual: r.expressao_booleana });
    } else if (r.popup) {
      janelas.popupErro(r.popup);
    }
    atualizar({ botoesSimplificar: true });
  }, [atualizar, janelas]);

  // --- executar_simplificacao_resultado / expressao_simplificada ----------
  const simplificarResultado = useCallback(
    () =>
      executar(() => {
        atualizar({ botoesSimplificar: false, tela: 'resolucao', resolucao: null });
        const r = chamar<RespostaApi & Omit<Resolucao, 'iniciadoEm'>>('simplificar_resultado', ref.current.entrada);
        if (!r.ok) {
          if (r.popup) janelas.popupErro(r.popup);
          return;
        }
        atualizar({ resolucao: { ...r, iniciadoEm: performance.now() } });
        if (r.popup) {
          const atraso = (r.final?.t ?? r.passos.at(-1)?.t ?? 0) * 1000;
          setTimeout(() => janelas.popupErro(r.popup as string), atraso);
        }
      }),
    [atualizar, executar, janelas],
  );

  // --- voltar_para_abas ----------------------------------------------------
  const voltarParaAbas = useCallback(() => {
    if (ref.current.expressaoBooleanaAtual) atualizar({ botoesSimplificar: true });
    voltarPara('abas');
  }, [atualizar, voltarPara]);

  // --- executar_simplificacao_interativa / go_to_interactive --------------
  const simplificarInterativo = useCallback(() => {
    atualizar({ botoesSimplificar: false, tela: 'interativo', sessaoInterativa: ref.current.sessaoInterativa + 1 });
  }, [atualizar]);

  // --- exibir_tabela_verdade ----------------------------------------------
  const exibirTabelaVerdade = useCallback(
    (expressao: string) => {
      const r = chamar<RespostaApi & DadosTabela>('tabela_verdade', expressao);
      if (r.ok) janelas.abrirTabela(r);
      else if (r.popup) janelas.popupErro(r.popup);
    },
    [janelas],
  );

  // --- abrir_duvida_expressao ("❓Pedir ajuda à IA") ------------------------
  const abrirDuvidaExpressao = useCallback(
    (expressao: string) => {
      if (!expressao) {
        janelas.popupErro('Digite uma expressão primeiro.');
        return;
      }
      const pergunta = `Como posso simplificar a seguinte expressão lógica proposicional e qual sua interpretação? Como ela fica em álgebra booleana e qual sua tabela verdade? ${expressao}`;
      window.open(`https://chat.openai.com/?q=${encodeURIComponent(pergunta)}`, '_blank', 'noopener');
    },
    [janelas],
  );

  // --- handle_problem_answer ----------------------------------------------
  const responderProblema = useCallback(
    (expressao: string, destino: 'circuit' | 'simplifier' | 'table') => {
      voltarPara('principal');
      // Preenche o campo de entrada principal
      atualizar({ entrada: expressao });
      chamar('problema_analisar');

      if (destino === 'circuit') {
        confirmarExpressao();
        setTimeout(() => void trocarParaAbas(), 500);
      } else if (destino === 'simplifier') {
        confirmarExpressao();
        setTimeout(async () => {
          await trocarParaAbas();
          setTimeout(() => {
            atualizar({ aba: 'expressao' });
            setTimeout(executarConversao, 200);
          }, 300);
        }, 500);
      } else if (destino === 'table') {
        exibirTabelaVerdade(expressao);
      }
    },
    [atualizar, confirmarExpressao, executarConversao, exibirTabelaVerdade, trocarParaAbas, voltarPara],
  );

  // --- on_closing ---------------------------------------------------------
  const encerrarSessao = useCallback(async () => {
    const r = chamar<RespostaApi & { mostrar_dialogo: boolean; preview: string }>('encerrar_sessao');
    encerrada.current = true;
    persistir();
    if (r.ok && r.mostrar_dialogo) {
      try {
        const escolha = await janelas.perguntarCompartilhamento(r.preview);
        if (escolha === 'enviar') {
          const fase1 = chamar<RespostaApi & { pedido: PedidoHttp | null }>('compartilhar_dados');
          if (fase1.ok && fase1.pedido) {
            const resposta = await executarPedido(fase1.pedido, { semCors: true });
            chamar('compartilhar_dados', JSON.stringify(resposta));
          }
        } else if (escolha === 'nunca') {
          chamar('nunca_perguntar');
        }
      } catch (erro) {
        console.log(`Erro no dialog de compartilhamento: ${erro}`);
      }
      persistir();
    }
    // janela.destroy()
    atualizar({ tela: 'encerrada', seletor: 0 });
  }, [atualizar, janelas]);

  // Fechar a aba sem "Encerrar sessão": salva a sessão (sem diálogo, o navegador não permite)
  useEffect(() => {
    const aoSair = () => {
      if (encerrada.current) return;
      try {
        chamar('encerrar_sessao_silenciosa');
        persistir();
        encerrada.current = true;
      } catch {
        /* motor não carregado */
      }
    };
    window.addEventListener('pagehide', aoSair);
    return () => window.removeEventListener('pagehide', aoSair);
  }, []);

  const api = useMemo<ApiAplicacao>(
    () => ({
      ...estado,
      mostrarTela,
      voltarPara,
      definirEntrada,
      confirmarExpressao,
      trocarParaAbas,
      mudarAba,
      garantirSeletor,
      executarConversao,
      simplificarResultado,
      voltarParaAbas,
      simplificarInterativo,
      exibirTabelaVerdade,
      abrirDuvidaExpressao,
      responderProblema,
      encerrarSessao,
    }),
    [
      estado,
      mostrarTela,
      voltarPara,
      definirEntrada,
      confirmarExpressao,
      trocarParaAbas,
      mudarAba,
      garantirSeletor,
      executarConversao,
      simplificarResultado,
      voltarParaAbas,
      simplificarInterativo,
      exibirTabelaVerdade,
      abrirDuvidaExpressao,
      responderProblema,
      encerrarSessao,
    ],
  );

  return <Contexto.Provider value={api}>{children}</Contexto.Provider>;
}
