/**
 * Formatos das respostas da API (BackEnd/api). Os nomes dos campos são os do
 * Python, para a correspondência ficar óbvia.
 */

export type Ponto = [number, number];

// ------------------------------ expressão ------------------------------

export interface Conversao {
  expressao: string;
  expressao_booleana: string;
  variaveis: string[];
}

export type AnaliseDaExpressao =
  | { valida: true; expressao_booleana: string; variaveis: string[] }
  | { valida: false; mensagem: string; posicao: number | null };

export interface TabelaVerdade {
  colunas: string[];
  tabela: number[][];
  resultados_finais: number[];
  total_combinacoes: number;
  /** As primeiras `total_variaveis` colunas são as variáveis (em ordem alfabética) */
  total_variaveis: number;
  conclusao: string;
  tipo_conclusao: 'tautologia' | 'contradicao' | 'satisfativel' | null;
}

// ------------------------------ Simplificar — Resultado ------------------------------

export interface PassoSimplificacao {
  iteracao: number;
  lei: string;
  caminho: number[];
  subexpressao_antes: string;
  subexpressao_depois: string;
  expressao_antes: string;
  expressao_depois: string;
  trecho_antes: [number, number];
  trecho_depois: [number, number];
}

export interface ResultadoSimplificacao {
  expressao_original: string;
  expressao_booleana: string;
  expressao_inicial: string;
  expressao_final: string;
  motivo_parada: string;
  passos: PassoSimplificacao[];
}

// ------------------------------ Simplificar — Interativo ------------------------------

/** Estado opaco da sessão: o cliente só guarda e devolve (D4). */
export type EstadoInterativo = Record<string, unknown>;

export type ItemHistorico =
  | { tipo: 'inicial'; expressao: string }
  | { tipo: 'lei'; passo: number; lei: string; antes: string; depois: string }
  | { tipo: 'pulo'; subexpressao: string };

export interface VisaoInterativa {
  expressao: string;
  subexpressao: string | null;
  trecho: [number, number] | null;
  motivo_parada: string | null;
  concluida: boolean;
  pode_desfazer: boolean;
  contador_passos: number;
  historico: ItemHistorico[];
  leis: string[];
}

/** Chamada ao registro de uso que o servidor pede para o navegador anotar. */
export interface EventoDeUso {
  metodo: string;
  argumentos: unknown[];
}

export interface RespostaInterativa {
  estado: EstadoInterativo;
  visao: VisaoInterativa;
  mensagem: string | null;
  eventos: EventoDeUso[];
}

// ------------------------------ equivalência e problemas ------------------------------

export interface ResultadoEquivalencia {
  equivalentes: boolean;
  variaveis: string[];
  contraexemplo: Record<string, boolean> | null;
  valor_1: boolean | null;
  valor_2: boolean | null;
}

export interface ItemProblema {
  indice: number;
  nome: string;
  dificuldade: string;
}

export interface Problema extends ItemProblema {
  pergunta: string;
  resposta: string;
}

export interface Correcao {
  correta: boolean;
  mensagem: string;
  tipo: string;
}

// ------------------------------ circuito ------------------------------

export interface Barramento {
  id: string;
  rotulo: string;
  x: number;
  tipo: 'variavel' | 'negado' | 'constante';
  valor: boolean | null;
  y_inicio: number;
  y_fim: number;
  y_rotulo: number;
}

export interface PortaDoLayout {
  id: string;
  tipo: 'AND' | 'OR' | 'NOT';
  x: number;
  y: number;
  largura: number;
  altura: number;
  entradas: Ponto[];
  saida: Ponto;
  subexpressao: string;
  caminho: number[];
  valor: boolean | null;
}

export interface FioDoLayout {
  id: string;
  origem: { tipo: 'barramento' | 'porta'; id: string };
  destino: { porta: string; entrada: number };
  pontos: Ponto[];
  valor: boolean | null;
}

export interface LayoutCircuito {
  expressao: string;
  expressao_booleana: string;
  variaveis: string[];
  barramentos: Barramento[];
  portas: PortaDoLayout[];
  fios: FioDoLayout[];
  conexoes: { barramento: string; ponto: Ponto }[];
  saida: { de: Ponto; ate: Ponto; rotulo: Ponto; valor: boolean | null } | null;
  valor: boolean | null;
  limites: { x_min: number; y_min: number; x_max: number; y_max: number };
}

export interface ModoCircuito {
  chave: string;
  name: string;
  description: string;
  restrictions: string[] | null;
  color: string;
  icon: string;
  difficulty: string;
  dicas: string[];
}

export interface DefinicaoComponente {
  nome: string;
  largura: number;
  altura: number;
  folga_de_selecao: number;
  entradas: Ponto[];
  saida: Ponto | null;
}

export interface DefinicoesComponentes {
  tipos: Record<string, DefinicaoComponente>;
  portas: string[];
  rotulo_saida: string;
  margem_de_colisao: number;
  raio_de_deteccao_do_pino: number;
  deslocamento_ao_posicionar: Ponto;
  busca_espiral: { passo: number; raio_maximo: number; passo_angulo: number };
  distancia_maxima_de_ajuste_no_arrasto: number;
  maximo_de_estados_no_historico: number;
}

export interface ComponenteInicial {
  id: string;
  tipo: string;
  nome: string;
  x: number;
  y: number;
}

export interface EditorInicial {
  expressao_booleana: string;
  variaveis: string[];
  componentes: ComponenteInicial[];
}

export interface Netlist {
  componentes: { id: string; tipo: string; nome?: string }[];
  fios: { origem: string; destino: string; entrada: number }[];
}

export interface ValidacaoCircuito {
  correto: boolean;
  motivo: string;
  variaveis: string[];
  variaveis_faltando: string[];
  portas_nao_permitidas: string[];
  falhas: { entradas: Record<string, boolean>; esperado: boolean; obtido: boolean }[];
  combinacoes: number;
}

// ------------------------------ registro de uso e textos ------------------------------

export interface ResumoDeUso {
  sessao: Record<string, unknown>;
  resumo: Record<string, unknown>;
  previa: string;
}

export interface Conteudo {
  boas_vindas: string;
  duvida_circuitos: string;
  informacoes: string;
}
