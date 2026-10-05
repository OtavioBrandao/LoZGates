/**
 * Cliente HTTP da API do LoZ Gates (BackEnd/api). Toda a lógica roda no
 * servidor em Python; aqui só montamos os pedidos e traduzimos os erros.
 *
 * Os caminhos são relativos à página ("api/..."), então o mesmo build funciona
 * servido pela própria API ("/"), pelo Vite em desenvolvimento (proxy) ou numa
 * subpasta atrás de um proxy reverso.
 */
import type {
  Conteudo,
  AnaliseDaExpressao,
  Conversao,
  Correcao,
  DefinicoesComponentes,
  EditorInicial,
  EstadoInterativo,
  ItemProblema,
  LayoutCircuito,
  ModoCircuito,
  Netlist,
  Problema,
  RespostaInterativa,
  ResultadoEquivalencia,
  ResultadoSimplificacao,
  ResumoDeUso,
  TabelaVerdade,
  ValidacaoCircuito,
} from './tipos';
import type { SessaoDeUso } from '../telemetria/registro';

/** Erro devolvido pela API ({"erro": {"tipo", "mensagem", "posicao"}}) ou falha de rede. */
export class ErroDaApi extends Error {
  readonly tipo: string;
  readonly status: number;
  readonly posicao: number | null;

  constructor(tipo: string, mensagem: string, status: number, posicao: number | null = null) {
    super(mensagem);
    this.name = 'ErroDaApi';
    this.tipo = tipo;
    this.status = status;
    this.posicao = posicao;
  }
}

export const MENSAGEM_SEM_SERVIDOR = 'Não foi possível falar com o servidor do LoZ Gates. Verifique a conexão e tente de novo.';

function url(caminho: string): string {
  return new URL(`api/${caminho}`, document.baseURI).href;
}

async function pedir<T>(metodo: 'GET' | 'POST', caminho: string, corpo?: unknown): Promise<T> {
  let resposta: Response;
  try {
    resposta = await fetch(url(caminho), {
      method: metodo,
      headers: corpo === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
    });
  } catch {
    throw new ErroDaApi('rede', MENSAGEM_SEM_SERVIDOR, 0);
  }

  let dados: unknown = null;
  try {
    dados = await resposta.json();
  } catch {
    // corpo vazio ou não-JSON (ex.: proxy fora do ar)
  }
  if (!resposta.ok) {
    const erro = (dados as { erro?: { tipo?: string; mensagem?: string; posicao?: number } } | null)?.erro;
    throw new ErroDaApi(
      erro?.tipo ?? 'http',
      erro?.mensagem ?? (resposta.status >= 500 ? MENSAGEM_SEM_SERVIDOR : `Erro ${resposta.status}`),
      resposta.status,
      erro?.posicao ?? null,
    );
  }
  return dados as T;
}

const get = <T>(caminho: string) => pedir<T>('GET', caminho);
const post = <T>(caminho: string, corpo: unknown) => pedir<T>('POST', caminho, corpo);

/** Mensagem para mostrar ao aluno a partir de qualquer erro. */
export function mensagemDe(erro: unknown): string {
  if (erro instanceof Error) return erro.message;
  return String(erro);
}

export const api = {
  // expressão
  converter: (expressao: string) => post<Conversao>('expressao/converter', { expressao }),
  /** Conferência enquanto o aluno digita: inválida vem como resposta normal, não como erro */
  analisarExpressao: (expressao: string) => post<AnaliseDaExpressao>('expressao/analisar', { expressao }),
  tabelaVerdade: (expressao: string) => post<TabelaVerdade>('expressao/tabela-verdade', { expressao }),

  // simplificações
  simplificarAutomatico: (expressao: string) => post<ResultadoSimplificacao>('simplificacao/automatica', { expressao }),
  iniciarInterativa: (expressao: string) => post<RespostaInterativa>('simplificacao/interativa/iniciar', { expressao }),
  aplicarLei: (estado: EstadoInterativo, lei: number) =>
    post<RespostaInterativa>('simplificacao/interativa/aplicar', { estado, lei }),
  pular: (estado: EstadoInterativo) => post<RespostaInterativa>('simplificacao/interativa/pular', { estado }),
  desfazer: (estado: EstadoInterativo) => post<RespostaInterativa>('simplificacao/interativa/desfazer', { estado }),

  // equivalência
  equivalencia: (expressao1: string, expressao2: string) =>
    post<ResultadoEquivalencia>('equivalencia', { expressao1, expressao2 }),

  // banco de problemas
  problemas: () => get<ItemProblema[]>('problemas'),
  problema: (indice: number) => get<Problema>(`problemas/${indice}`),
  verificarProblema: (indice: number, resposta: string) =>
    post<Correcao>(`problemas/${indice}/verificar`, { resposta }),

  // circuito
  layoutCircuito: (expressao: string, valores?: Record<string, boolean>) =>
    post<LayoutCircuito>('circuito/layout', valores ? { expressao, valores } : { expressao }),
  modos: () => get<ModoCircuito[]>('circuito/modos'),
  componentes: () => get<DefinicoesComponentes>('circuito/componentes'),
  editor: (expressao: string) => post<EditorInicial>('circuito/editor', { expressao }),
  validarCircuito: (expressao: string, modo: string, netlist: Netlist) =>
    post<ValidacaoCircuito>('circuito/validar', { expressao, modo, netlist }),
  simularCircuito: (netlist: Netlist, valores: Record<string, boolean>) =>
    post<{ saidas: Record<string, boolean | null> }>('circuito/simular', { netlist, valores }),

  // assistente de IA (a chave fica no servidor)
  sugestaoIa: (expressao: string, contexto: string) => post<{ resposta: string }>('ia/sugestao', { expressao, contexto }),
  perguntaIa: (pergunta: string, expressao: string) => post<{ resposta: string }>('ia/pergunta', { pergunta, expressao }),

  // registro de uso (os dados ficam no navegador; o servidor só monta o resumo e envia)
  resumoDeUso: (sessao: SessaoDeUso) => post<ResumoDeUso>('telemetria/resumo', sessao),
  enviarUso: (sessao: SessaoDeUso) => post<{ enviado: boolean }>('telemetria/enviar', sessao),

  // textos de ajuda (config.py)
  conteudo: () => get<Conteudo>('conteudo'),
};

/** Guarda em memória respostas que não mudam durante a sessão (modos, componentes, textos). */
export function memorizar<T>(buscar: () => Promise<T>): () => Promise<T> {
  let promessa: Promise<T> | null = null;
  return () => {
    if (!promessa) {
      promessa = buscar();
      promessa.catch(() => {
        promessa = null;
      });
    }
    return promessa;
  };
}

export const dadosFixos = {
  modos: memorizar(api.modos),
  componentes: memorizar(api.componentes),
  conteudo: memorizar(api.conteudo),
};
