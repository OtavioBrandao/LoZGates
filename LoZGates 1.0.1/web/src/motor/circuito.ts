/**
 * Liga o <canvas> do pygame à tela e encaminha teclado/mouse para o código original.
 *
 * - Mouse (clique, arrasto, rodinha): o próprio SDL/pygame lê do canvas, como no desktop.
 * - Teclado: no desktop chegava ao circuito pelo bind("<KeyPress>") do tk.Frame;
 *   aqui chega pelo mesmo bind, via QuadroWeb (python/lozweb/tkweb.py).
 */
import { motor } from './pyodide';

/** Altura do tk.Frame do pygame no desktop (circuit_mode_interface.py: height=600). */
export const ALTURA_CIRCUITO = 600;

let containerAtual: HTMLElement | null = null;
let aoMensagemAtual: ((texto: string, cor: string) => void) | null = null;
let eventosLigados = false;

/** Objeto passado ao Python (QuadroWeb): medir, focar, mensagem, rolagem. */
export const ponteCircuito = {
  medir: (): [number, number] => [containerAtual?.clientWidth ?? 0, containerAtual ? ALTURA_CIRCUITO : 0],
  focar: (): void => {
    motor().canvas.focus({ preventScroll: true });
  },
  mensagem: (texto: string, cor: string): void => {
    aoMensagemAtual?.(texto, cor);
  },
  // scroll_control_callback: no desktop bloqueava a rolagem da página com o mouse sobre
  // o pygame. Aqui o listener de 'wheel' abaixo já faz isso.
  rolagem: (_habilitar: boolean): void => {},
};

const TECLAS_SEM_ROLAGEM = new Set([' ', 'Spacebar', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']);

function ligarEventos(canvas: HTMLCanvasElement) {
  if (eventosLigados) return;
  eventosLigados = true;
  const { api } = motor();
  const tecla = (tipo: 'keydown' | 'keyup') => (e: KeyboardEvent) => {
    if (e.key === 'Tab') return; // mantém a navegação por teclado da página
    if (TECLAS_SEM_ROLAGEM.has(e.key)) e.preventDefault();
    api.circuito_tecla(tipo, e.key, e.ctrlKey, e.shiftKey, e.altKey);
  };
  canvas.addEventListener('keydown', tecla('keydown'));
  canvas.addEventListener('keyup', tecla('keyup'));
  canvas.addEventListener('mouseenter', () => api.circuito_mouse_entrou());
  canvas.addEventListener('wheel', (e) => e.preventDefault(), { passive: false });
}

/** Coloca o canvas dentro de `container`. Devolve a função que o retira. */
export function anexarCanvas(container: HTMLElement, aoMensagem: (texto: string, cor: string) => void): () => void {
  const { canvas } = motor();
  containerAtual = container;
  aoMensagemAtual = aoMensagem;
  container.appendChild(canvas);
  ligarEventos(canvas);
  return () => {
    if (canvas.parentElement === container) container.removeChild(canvas);
    if (containerAtual === container) {
      containerAtual = null;
      aoMensagemAtual = null;
    }
  };
}

/** Atalho na tela: envia a mesma tecla que o teclado físico enviaria. */
export function enviarTecla(tecla: string, { ctrl = false } = {}): void {
  const { api, canvas } = motor();
  canvas.focus({ preventScroll: true });
  api.circuito_tecla('keydown', tecla, ctrl, false, false);
  api.circuito_tecla('keyup', tecla, ctrl, false, false);
}
