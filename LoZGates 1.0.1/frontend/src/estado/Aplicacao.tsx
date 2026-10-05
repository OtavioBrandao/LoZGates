/**
 * Controlador da aplicação — equivalente web da navegação e dos callbacks de
 * FrontEnd/screens/expression/expression_screen.py do interface_update
 * (go_back_to, confirmar_expressao, trocar_para_abas, on_tab_change,
 * executar_conversao, expressao_simplificada, go_to_interactive,
 * handle_problem_answer...) e do on_closing de FrontEnd/app/loz_app.py.
 *
 * As regras (o que é limpo ao voltar, quando o circuito interativo é criado ou
 * descartado, quais mensagens aparecem e o que vai para o registro de uso)
 * seguem o desktop. A lógica em si roda no servidor (BackEnd/api).
 */
import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from 'react';
import { api, mensagemDe } from '../api/cliente';
import type { LayoutCircuito, ResultadoSimplificacao } from '../api/tipos';
import {
  envioConcluido,
  nuncaPerguntar,
  registrar,
  registroAtivo,
  reiniciarSessao,
  sessaoEncerrada,
} from '../telemetria/registro';
import { useJanelas } from './Janelas';

export type Tela = 'inicio' | 'principal' | 'equivalencia' | 'abas' | 'resolucao' | 'interativo' | 'problemas' | 'encerrada';
export type Aba = 'circuito' | 'interativo' | 'expressao';
export type DestinoProblema = 'circuit' | 'simplifier' | 'table';

/** Nomes das abas exatamente como no CTkTabview (FrontEnd/app/navigation.py); vão para o registro de uso. */
export const NOMES_ABAS: Record<Aba, string> = {
  circuito: '      Circuito      ',
  interativo: '  Circuito Interativo  ',
  expressao: '      Expressão      ',
};

interface Estado {
  tela: Tela;
  /** Campo "Expressão Lógica Proposicional" da tela principal */
  entrada: string;
  /** Botão "🔌 Ver Circuito" (criado por confirmar_expressao) */
  verCircuito: boolean;
  /** circuit_generation_in_progress: o botão vira "Processando..." */
  gerandoCircuito: boolean;
  aba: Aba;
  labelCircuito: string;
  layout: LayoutCircuito | null;
  /** Texto no lugar do circuito quando não há o que mostrar */
  textoCircuito: string;
  /** expressao_global: a expressão em álgebra booleana usada pelo circuito e pelo modo interativo */
  expressaoGlobal: string;
  /** Variáveis da expressão (em ordem alfabética) e os valores atuais das entradas do circuito */
  variaveis: string[];
  valores: Record<string, boolean>;
  labelConvertida: string | null;
  expressaoBooleanaAtual: string;
  botoesSimplificar: boolean;
  /** Instância do CircuitModeSelector: 0 = não existe; > 0 = identificador */
  seletor: number;
  resolucao: ResultadoSimplificacao | null;
  /** simplification_in_progress */
  simplificando: boolean;
  /** Cada entrada na simplificação interativa começa uma sessão nova */
  sessaoInterativa: number;
  ocupado: boolean;
}

const ESTADO_INICIAL: Estado = {
  tela: 'inicio',
  entrada: '',
  verCircuito: false,
  gerandoCircuito: false,
  aba: 'circuito',
  labelCircuito: '',
  layout: null,
  textoCircuito: '',
  expressaoGlobal: '',
  variaveis: [],
  valores: {},
  labelConvertida: null,
  expressaoBooleanaAtual: '',
  botoesSimplificar: false,
  seletor: 0,
  resolucao: null,
  simplificando: false,
  sessaoInterativa: 0,
  ocupado: false,
};

export const PREFIXO_LABEL_CIRCUITO = 'Expressão Lógica Proposicional: ';
export const PREFIXO_LABEL_CONVERTIDA = 'Expressão em Álgebra Booleana: ';

/** entrada.get().strip().upper().replace(" ", "") */
export const normalizar = (texto: string) => texto.trim().toUpperCase().replaceAll(' ', '');

export interface ApiAplicacao extends Estado {
  /** Expressão que o circuito interativo usa (expressao_global ou o texto digitado) */
  expressaoDoCircuito: string;
  mostrarTela: (tela: Tela) => void;
  voltarPara: (destino: Tela) => void;
  definirEntrada: (texto: string) => void;
  confirmarExpressao: () => void;
  trocarParaAbas: (alvo?: Aba) => Promise<boolean>;
  /** Liga/desliga as entradas do circuito: o servidor devolve o circuito com os novos sinais */
  definirValores: (valores: Record<string, boolean>) => void;
  mudarAba: (aba: Aba) => void;
  garantirSeletor: () => void;
  executarConversao: () => Promise<void>;
  simplificarResultado: () => Promise<void>;
  voltarParaAbas: () => void;
  simplificarInterativo: () => void;
  exibirTabelaVerdade: (expressao: string) => Promise<void>;
  abrirDuvidaExpressao: (expressao: string) => void;
  responderProblema: (expressao: string, destino: DestinoProblema) => void;
  encerrarSessao: () => Promise<void>;
}

const Contexto = createContext<ApiAplicacao | null>(null);

export function useAplicacao(): ApiAplicacao {
  const contexto = useContext(Contexto);
  if (!contexto) throw new Error('useAplicacao fora do ProvedorAplicacao');
  return contexto;
}

export function ProvedorAplicacao({ children }: { children: ReactNode }) {
  const janelas = useJanelas();
  const [estado, setEstado] = useState<Estado>(ESTADO_INICIAL);
  const ref = useRef<Estado>(ESTADO_INICIAL);
  const contadorSeletor = useRef(0);
  const pedidoDeCircuito = useRef(0);

  const atualizar = useCallback((mudancas: Partial<Estado>) => {
    ref.current = { ...ref.current, ...mudancas };
    setEstado(ref.current);
  }, []);

  // --- navigation.show_screen ------------------------------------------------
  const mostrarTela = useCallback((tela: Tela) => atualizar({ tela }), [atualizar]);

  // --- CircuitScreen.initialize_if_needed -------------------------------------
  const garantirSeletor = useCallback(() => {
    const expressao = ref.current.expressaoGlobal || normalizar(ref.current.entrada);
    if (!expressao) return; // "Nenhuma expressao disponivel para criar circuito"
    if (ref.current.seletor) return; // já existe: o seletor mostra a expressão atual
    registrar('log_circuit_interaction_start');
    contadorSeletor.current += 1;
    atualizar({ seletor: contadorSeletor.current });
  }, [atualizar]);

  // --- on_tab_change -----------------------------------------------------------
  const aoMudarAba = useCallback(
    (aba: Aba) => {
      registrar('log_tab_changed', 'tab_navigation', NOMES_ABAS[aba]);
      if (aba === 'interativo') garantirSeletor();
    },
    [garantirSeletor],
  );

  const mudarAba = useCallback(
    (aba: Aba) => {
      atualizar({ aba });
      aoMudarAba(aba);
    },
    [atualizar, aoMudarAba],
  );

  // --- go_back_to --------------------------------------------------------------
  const voltarPara = useCallback(
    (destino: Tela) => {
      const mudancas: Partial<Estado> = { verCircuito: false, tela: destino };
      // Voltando para as abas o circuito interativo continua; para qualquer outro lugar, é limpo
      if (destino !== 'abas') mudancas.seletor = 0;
      // Limpa a entrada apenas se não for para certas telas
      if (!['abas', 'resolucao', 'interativo'].includes(destino)) {
        mudancas.entrada = '';
        mudancas.botoesSimplificar = false;
      }
      // Esconde os resultados da aba de expressão se NÃO for para as abas
      if (destino !== 'abas') {
        mudancas.labelConvertida = null;
        mudancas.resolucao = null;
        mudancas.botoesSimplificar = false;
      }
      atualizar(mudancas);
      if (destino === 'abas' && ref.current.expressaoGlobal) {
        window.setTimeout(() => aoMudarAba(ref.current.aba), 200);
      }
    },
    [atualizar, aoMudarAba],
  );

  const definirEntrada = useCallback((texto: string) => atualizar({ entrada: texto }), [atualizar]);

  // --- confirmar_expressao --------------------------------------------------------
  const confirmarExpressao = useCallback(() => {
    atualizar({ verCircuito: false });
    const texto = ref.current.entrada.trim();
    if (!texto) {
      registrar('log_expression_entered', '', false);
      janelas.popupErro('A expressão não pode estar vazia.');
      return;
    }
    registrar('log_expression_entered', normalizar(texto), true);
    atualizar({ botoesSimplificar: false, verCircuito: true });
  }, [atualizar, janelas]);

  // --- ver_circuito_pygame (agora: layout em JSON desenhado em SVG) ---------------
  // O layout volta com o nível lógico de cada barramento, porta e fio para os valores das entradas.
  const gerarCircuito = useCallback(
    async (expressao: string, valores: Record<string, boolean>) => {
      const pedido = ++pedidoDeCircuito.current;
      try {
        const layout = await api.layoutCircuito(expressao, valores);
        if (pedido === pedidoDeCircuito.current) atualizar({ layout, textoCircuito: '' });
      } catch (erro) {
        if (pedido !== pedidoDeCircuito.current) return;
        atualizar({ layout: null, textoCircuito: 'Imagem do circuito não encontrada' });
        janelas.popupErro(`Erro ao gerar circuito: ${mensagemDe(erro)}`);
      } finally {
        if (pedido === pedidoDeCircuito.current) atualizar({ gerandoCircuito: false });
      }
    },
    [atualizar, janelas],
  );

  const definirValores = useCallback(
    (valores: Record<string, boolean>) => {
      if (!ref.current.expressaoGlobal) return;
      atualizar({ valores });
      const pedido = ++pedidoDeCircuito.current;
      // Mantém o desenho anterior até chegar o novo (a geometria é a mesma, só mudam os sinais)
      api
        .layoutCircuito(ref.current.expressaoGlobal, valores)
        .then((layout) => {
          if (pedido === pedidoDeCircuito.current) atualizar({ layout, textoCircuito: '', gerandoCircuito: false });
        })
        .catch((erro: unknown) => {
          console.warn('Não foi possível atualizar os sinais do circuito', erro);
          if (pedido === pedidoDeCircuito.current) atualizar({ gerandoCircuito: false });
        });
    },
    [atualizar],
  );

  // --- trocar_para_abas ------------------------------------------------------------
  const trocarParaAbas = useCallback(
    async (alvo: Aba = 'circuito'): Promise<boolean> => {
      if (ref.current.gerandoCircuito) return false; // já há uma geração em andamento
      const inicio = performance.now();
      const expressao = normalizar(ref.current.entrada);
      registrar('log_expression_entered', expressao, Boolean(expressao));
      if (!expressao) {
        registrar('log_error', 'validation_error', 'Empty expression');
        janelas.popupErro('A expressão não pode estar vazia.');
        return false;
      }
      atualizar({ labelCircuito: `${PREFIXO_LABEL_CIRCUITO}${expressao}`, ocupado: true });
      let saida: string;
      let variaveis: string[];
      try {
        const conversao = await api.converter(expressao);
        saida = conversao.expressao_booleana;
        variaveis = conversao.variaveis;
      } catch (erro) {
        janelas.popupErro(`Erro ao processar expressão: ${mensagemDe(erro)}`);
        return false;
      } finally {
        atualizar({ ocupado: false });
      }
      // As entradas começam todas em 0, como a primeira linha da tabela-verdade
      const valores = Object.fromEntries(variaveis.map((nome) => [nome, false]));
      atualizar({ expressaoGlobal: saida, variaveis, valores, gerandoCircuito: true, layout: null, textoCircuito: '' });
      // No desktop o circuito é gerado em segundo plano e a tela troca na hora
      void gerarCircuito(saida, valores);
      // Uma ação explícita escolhe sua aba (show_tab não passa por on_tab_change)
      atualizar({ tela: 'abas', aba: alvo });
      registrar('log_feature_used', 'circuit_generation', (performance.now() - inicio) / 1000);
      return true;
    },
    [atualizar, gerarCircuito, janelas],
  );

  // --- executar_conversao / mostrar_expressao_convertida ------------------------------
  const executarConversao = useCallback(async () => {
    atualizar({ botoesSimplificar: false });
    const texto = ref.current.entrada.trim().toUpperCase();
    if (!texto) {
      janelas.popupErro('Digite uma expressão primeiro.');
    } else {
      try {
        const { expressao_booleana } = await api.converter(texto);
        atualizar({
          expressaoBooleanaAtual: expressao_booleana,
          labelConvertida: `${PREFIXO_LABEL_CONVERTIDA}${expressao_booleana}`,
        });
      } catch (erro) {
        janelas.popupErro(`Erro ao converter expressão: ${mensagemDe(erro)}`);
      }
    }
    // Como no desktop, os botões de simplificação aparecem depois da tentativa
    atualizar({ botoesSimplificar: true });
  }, [atualizar, janelas]);

  // --- executar_simplificacao_resultado / expressao_simplificada ------------------------
  const simplificarResultado = useCallback(async () => {
    if (ref.current.simplificando) return; // pedido duplicado
    atualizar({ botoesSimplificar: false, tela: 'resolucao' });
    const texto = ref.current.entrada.trim().toUpperCase();
    if (!texto) {
      janelas.popupErro('A expressão na tela principal está vazia.');
      return;
    }
    atualizar({ simplificando: true, resolucao: null });
    try {
      atualizar({ resolucao: await api.simplificarAutomatico(texto) });
    } catch (erro) {
      janelas.popupErro(`Erro ao simplificar expressão: ${mensagemDe(erro)}`);
    } finally {
      atualizar({ simplificando: false });
    }
  }, [atualizar, janelas]);

  // --- voltar_para_abas ---------------------------------------------------------------
  const voltarParaAbas = useCallback(() => {
    if (ref.current.expressaoBooleanaAtual) atualizar({ botoesSimplificar: true });
    voltarPara('abas');
  }, [atualizar, voltarPara]);

  // --- executar_simplificacao_interativa / go_to_interactive ---------------------------
  const simplificarInterativo = useCallback(() => {
    atualizar({ botoesSimplificar: false, tela: 'interativo' });
    if (!ref.current.expressaoGlobal) {
      janelas.popupErro('Por favor, primeiro insira e converta uma expressão.');
      voltarPara('abas');
      mostrarTela('principal');
      return;
    }
    atualizar({ sessaoInterativa: ref.current.sessaoInterativa + 1 });
  }, [atualizar, janelas, mostrarTela, voltarPara]);

  // --- exibir_tabela_verdade ----------------------------------------------------------
  const exibirTabelaVerdade = useCallback(
    async (expressao: string) => {
      if (!expressao.trim()) {
        janelas.popupErro('Erro ao gerar tabela verdade: A expressão está vazia.');
        return;
      }
      try {
        const tabela = await api.tabelaVerdade(expressao);
        janelas.abrirTabela({
          titulo: `Tabela Verdade: ${expressao}`,
          colunas: tabela.colunas,
          tabela: tabela.tabela,
          conclusao: tabela.conclusao,
          cor_conclusao:
            tabela.tipo_conclusao === 'tautologia' ? 'sucesso' : tabela.tipo_conclusao === 'contradicao' ? 'erro' : 'info',
        });
      } catch (erro) {
        janelas.popupErro(`Erro ao gerar tabela verdade: ${mensagemDe(erro)}`);
      }
    },
    [janelas],
  );

  // --- abrir_duvida_expressao ("❓Pedir ajuda à IA") -----------------------------------
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

  // --- handle_problem_answer (depois de voltar_para(principal)) -------------------------
  const responderProblema = useCallback(
    (expressao: string, destino: DestinoProblema) => {
      voltarPara('principal');
      // Preenche o campo de entrada principal
      atualizar({ entrada: expressao });
      registrar('log_feature_used', 'problem_answer_analysis', 0);

      if (destino === 'circuit') {
        confirmarExpressao();
        window.setTimeout(() => void trocarParaAbas(), 500);
      } else if (destino === 'simplifier') {
        confirmarExpressao();
        window.setTimeout(async () => {
          await trocarParaAbas('expressao');
          window.setTimeout(() => void executarConversao(), 200);
        }, 500);
      } else {
        void exibirTabelaVerdade(expressao);
      }
    },
    [atualizar, confirmarExpressao, executarConversao, exibirTabelaVerdade, trocarParaAbas, voltarPara],
  );

  // --- on_closing (o navegador não deixa perguntar ao fechar a aba: há um botão) ----------
  const encerrarSessao = useCallback(async () => {
    atualizar({ seletor: 0, ocupado: true });
    const sessao = sessaoEncerrada();
    // "Nunca Perguntar" desliga o registro; aí não há o que pedir nem enviar
    if (registroAtivo()) {
      try {
        const { previa } = await api.resumoDeUso(sessao);
        atualizar({ ocupado: false });
        const escolha = await janelas.perguntarCompartilhamento(previa);
        if (escolha === 'enviar') {
          atualizar({ ocupado: true });
          const { enviado } = await api.enviarUso({ ...sessao, envio: Date.now() / 1000 });
          if (enviado) envioConcluido();
          else console.warn('O envio de dados de atividade falhou');
        } else if (escolha === 'nunca') {
          nuncaPerguntar();
        }
      } catch (erro) {
        console.warn('Erro no diálogo de compartilhamento', erro);
      }
    }
    reiniciarSessao();
    atualizar({ ocupado: false, tela: 'encerrada' });
  }, [atualizar, janelas]);

  const valor = useMemo<ApiAplicacao>(
    () => ({
      ...estado,
      expressaoDoCircuito: estado.expressaoGlobal || normalizar(estado.entrada),
      mostrarTela,
      voltarPara,
      definirEntrada,
      confirmarExpressao,
      trocarParaAbas,
      definirValores,
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
      definirValores,
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

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}
