/**
 * Registro de uso no navegador (D6).
 *
 * O desktop chamava o DetailedUserLogger direto (log_expression_entered,
 * log_law_applied...). Aqui anotamos as MESMAS chamadas, com os mesmos
 * argumentos e o instante de cada uma; os dados ficam no navegador. Ao
 * encerrar a sessão, o servidor refaz as chamadas num DetailedUserLogger em
 * memória (BackEnd/telemetria/reconstrucao.py) para montar a prévia do diálogo
 * de consentimento e, só se o aluno aceitar, o envio ao Google Forms.
 *
 * - A sessão em andamento fica no sessionStorage: sobrevive a recarregar a
 *   página e acaba junto com a aba (no desktop, a sessão era a janela aberta).
 * - O identificador anônimo e as configurações (logging_settings.json no
 *   desktop) ficam no localStorage.
 */

/** Métodos que o servidor aceita refazer (reconstrucao.METODOS_PERMITIDOS). */
export type MetodoDeRegistro =
  | 'log_event'
  | 'log_expression_entered'
  | 'log_interactive_simplification_start'
  | 'log_law_applied'
  | 'log_simplification_skip'
  | 'log_simplification_undo'
  | 'log_simplification_completed'
  | 'log_simplification_step_failed'
  | 'log_circuit_interaction_start'
  | 'log_component_action'
  | 'log_circuit_test'
  | 'log_equivalence_check_with_expressions'
  | 'log_feature_used'
  | 'log_error'
  | 'log_tab_changed';

export interface Chamada {
  metodo: string;
  argumentos: unknown[];
  momento: number;
}

/** Formato de BackEnd/api/esquemas.SessaoDeUso. */
export interface SessaoDeUso {
  id_usuario: string;
  plataforma: string;
  sistema: string;
  inicio: number;
  fim: number;
  fuso_minutos: number;
  versao_app: string;
  envio: number | null;
  chamadas: Chamada[];
}

interface Configuracoes {
  logging_enabled: boolean;
  auto_send_enabled: boolean;
  send_frequency_days: number;
  last_prompt?: string;
}

interface SessaoEmAndamento {
  inicio: number;
  chamadas: Chamada[];
}

/** Mesmo limite do servidor (reconstrucao.MAXIMO_DE_CHAMADAS). */
export const MAXIMO_DE_CHAMADAS = 5000;
/** interface: user_logger = DetailedUserLogger("1.0-beta") */
const VERSAO_DO_APP = '1.0-beta';

const CHAVE_SESSAO = 'lozgates:sessao';
const CHAVE_CONFIGURACOES = 'lozgates:configuracoes';
const CHAVE_ID = 'lozgates:id-usuario';

const agora = () => Date.now() / 1000;

function ler<T>(armazenamento: () => Storage, chave: string): T | null {
  try {
    const texto = armazenamento().getItem(chave);
    return texto === null ? null : (JSON.parse(texto) as T);
  } catch {
    return null;
  }
}

function gravar(armazenamento: () => Storage, chave: string, valor: unknown): void {
  try {
    armazenamento().setItem(chave, JSON.stringify(valor));
  } catch {
    // modo privado, cota cheia ou armazenamento bloqueado: o registro segue só em memória
  }
}

function apagar(armazenamento: () => Storage, chave: string): void {
  try {
    armazenamento().removeItem(chave);
  } catch {
    /* idem */
  }
}

const local = () => window.localStorage;
const daAba = () => window.sessionStorage;

/** ID anônimo e estável neste navegador (no desktop, um hash do hardware). */
function idDoUsuario(): string {
  const salvo = ler<string>(local, CHAVE_ID);
  if (salvo && /^[0-9a-f]{16}$/.test(salvo)) return salvo;
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  const novo = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
  gravar(local, CHAVE_ID, novo);
  return novo;
}

/** Equivalente ao platform.system() do desktop. */
export function sistemaOperacional(agente = navigator.userAgent): string {
  if (/android/i.test(agente)) return 'Android';
  if (/iphone|ipad|ipod/i.test(agente)) return 'iOS';
  if (/windows/i.test(agente)) return 'Windows';
  if (/mac os x|macintosh/i.test(agente)) return 'Darwin';
  if (/cros/i.test(agente)) return 'ChromeOS';
  if (/linux/i.test(agente)) return 'Linux';
  return 'Desconhecido';
}

/** Equivalente ao platform.platform() do desktop. */
function plataforma(): string {
  return `Navegador: ${navigator.userAgent}`.slice(0, 300);
}

function configuracoes(): Configuracoes {
  return {
    logging_enabled: true,
    auto_send_enabled: false,
    send_frequency_days: 7,
    ...(ler<Configuracoes>(local, CHAVE_CONFIGURACOES) ?? {}),
  };
}

let sessao: SessaoEmAndamento = carregarSessao();

function carregarSessao(): SessaoEmAndamento {
  const salva = ler<SessaoEmAndamento>(daAba, CHAVE_SESSAO);
  if (salva && typeof salva.inicio === 'number' && Array.isArray(salva.chamadas)) return salva;
  const nova = { inicio: agora(), chamadas: [] };
  gravar(daAba, CHAVE_SESSAO, nova);
  return nova;
}

/** O registro está ligado? ("🚫 Nunca Perguntar" desliga, como logging_enabled = False.) */
export function registroAtivo(): boolean {
  return configuracoes().logging_enabled;
}

/** Anota uma chamada ao registro de uso (o DetailedUserLogger ignora tudo se estiver desligado). */
export function registrar(metodo: MetodoDeRegistro, ...argumentos: unknown[]): void {
  if (!registroAtivo() || sessao.chamadas.length >= MAXIMO_DE_CHAMADAS) return;
  sessao.chamadas.push({ metodo, argumentos, momento: agora() });
  gravar(daAba, CHAVE_SESSAO, sessao);
}

/** Anota os eventos que a API devolveu (ex.: simplificação interativa). */
export function registrarEventos(eventos: { metodo: string; argumentos: unknown[] }[]): void {
  for (const evento of eventos) registrar(evento.metodo as MetodoDeRegistro, ...evento.argumentos);
}

/** Sessão encerrada agora, no formato que a API espera. */
export function sessaoEncerrada(envio: number | null = null): SessaoDeUso {
  return {
    id_usuario: idDoUsuario(),
    plataforma: plataforma(),
    sistema: sistemaOperacional(),
    inicio: sessao.inicio,
    fim: agora(),
    fuso_minutos: -new Date().getTimezoneOffset(),
    versao_app: VERSAO_DO_APP,
    envio,
    chamadas: sessao.chamadas,
  };
}

/** _save_settings(): grava as configurações com o horário do último diálogo. */
function salvarConfiguracoes(mudancas: Partial<Configuracoes> = {}): void {
  gravar(local, CHAVE_CONFIGURACOES, { ...configuracoes(), ...mudancas, last_prompt: new Date().toISOString() });
}

/** Depois de um envio bem-sucedido (o desktop gravava as configurações). */
export function envioConcluido(): void {
  salvarConfiguracoes();
}

/** "🚫 Nunca Perguntar": desliga o registro neste navegador. */
export function nuncaPerguntar(): void {
  salvarConfiguracoes({ logging_enabled: false });
}

/** Começa uma sessão nova (depois de "Encerrar sessão"). */
export function reiniciarSessao(): void {
  apagar(daAba, CHAVE_SESSAO);
  sessao = carregarSessao();
}
