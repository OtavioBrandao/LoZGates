/**
 * Motor Python do LoZ Gates no navegador.
 *
 * Carrega o Pyodide (CPython em WebAssembly), o pygame-ce e o Pillow, descompacta o
 * código ORIGINAL do LoZ Gates (BackEnd/, FrontEnd/, config.py) e expõe as funções de
 * python/lozweb/api.py.
 */
import type { PyodideInterface } from 'pyodide';
import type { PyProxy } from 'pyodide/ffi';
import { restaurarArquivos, salvarArquivos } from './persistencia';

export const VERSAO_PYODIDE = '0.29.3';
const URL_PYODIDE = import.meta.env.VITE_PYODIDE_URL || `https://cdn.jsdelivr.net/pyodide/v${VERSAO_PYODIDE}/full/`;
const PASTA_APP = '/home/pyodide/lozgates';
export const PASTA_DADOS = '/home/pyodide/dados';
const ID_TECLADO_SDL = 'lozgates-sdl-teclado';

export type Progresso = (etapa: string, fracao: number) => void;

export interface Motor {
  py: PyodideInterface;
  api: PyProxy & Record<string, (...args: unknown[]) => unknown>;
  canvas: HTMLCanvasElement;
  arquivosPersistentes: string[];
}

let carregamento: Promise<Motor> | null = null;
let motorAtual: Motor | null = null;

function urlAbsoluta(base: string): string {
  const url = new URL(base, document.baseURI).href;
  return url.endsWith('/') ? url : `${url}/`;
}

function criarCanvasDoPygame(): HTMLCanvasElement {
  // Elemento oculto que o SDL usa como "alvo" do teclado (ver lozweb/plataforma.py).
  if (!document.getElementById(ID_TECLADO_SDL)) {
    const alvo = document.createElement('div');
    alvo.id = ID_TECLADO_SDL;
    alvo.hidden = true;
    document.body.appendChild(alvo);
  }
  const canvas = document.createElement('canvas');
  canvas.id = 'canvas';
  canvas.className = 'canvas-pygame';
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', 'Área do circuito interativo (pygame)');
  canvas.addEventListener('contextmenu', (e) => e.preventDefault());
  return canvas;
}

export function carregarMotor(progresso: Progresso = () => {}): Promise<Motor> {
  if (carregamento) return carregamento;
  carregamento = (async () => {
    const base = urlAbsoluta(URL_PYODIDE);
    progresso('Baixando o interpretador Python (Pyodide)…', 0.05);
    const modulo = (await import(/* @vite-ignore */ `${base}pyodide.mjs`)) as typeof import('pyodide');

    const py = await modulo.loadPyodide({
      indexURL: base,
      // Saída do Python vai para o console do navegador (no desktop ia para o terminal)
      stdout: (linha: string) => console.log(linha),
      stderr: (linha: string) => console.warn(linha),
    });

    progresso('Preparando a área do pygame…', 0.45);
    const canvas = criarCanvasDoPygame();
    py.canvas.setCanvas2D(canvas);

    progresso('Carregando pygame-ce e Pillow…', 0.55);
    await py.loadPackage(['pygame-ce', 'pillow'], { messageCallback: () => {} });

    progresso('Carregando o código do LoZ Gates…', 0.8);
    const resposta = await fetch(new URL('lozgates-python.zip', document.baseURI), { cache: 'no-cache' });
    if (!resposta.ok) throw new Error(`Não foi possível baixar o código do LoZ Gates (HTTP ${resposta.status}).`);
    py.unpackArchive(await resposta.arrayBuffer(), 'zip', { extractDir: PASTA_APP });

    progresso('Iniciando…', 0.92);
    py.FS.mkdirTree(PASTA_DADOS);
    restaurarArquivos(py, PASTA_DADOS);

    py.runPython(`import sys\nif ${JSON.stringify(PASTA_APP)} not in sys.path: sys.path.insert(0, ${JSON.stringify(PASTA_APP)})`);
    const api = py.pyimport('lozweb.api') as Motor['api'];
    const inicio = JSON.parse(api.iniciar(import.meta.env.VITE_GROQ_API_KEY || '') as string);
    if (!inicio.ok) throw new Error(inicio.excecao || 'Falha ao iniciar o LoZ Gates.');

    const motor: Motor = { py, api, canvas, arquivosPersistentes: inicio.arquivos };
    salvarArquivos(py, PASTA_DADOS, motor.arquivosPersistentes);
    motorAtual = motor;
    progresso('Pronto', 1);
    return motor;
  })();
  carregamento.catch(() => {
    carregamento = null;
  });
  return carregamento;
}

export function motor(): Motor {
  if (!motorAtual) throw new Error('O motor Python ainda não foi carregado.');
  return motorAtual;
}

export function motorPronto(): boolean {
  return motorAtual !== null;
}

/** Resposta padrão das funções de lozweb/api.py */
export interface RespostaApi {
  ok: boolean;
  popup?: string;
  excecao?: string;
  [chave: string]: unknown;
}

/** Chama uma função de lozweb/api.py e devolve o JSON já convertido. */
export function chamar<T extends RespostaApi = RespostaApi>(nome: string, ...args: unknown[]): T {
  const { api } = motor();
  const funcao = api[nome];
  if (typeof funcao !== 'function') throw new Error(`Função inexistente em lozweb.api: ${nome}`);
  const resultado = JSON.parse(funcao(...args) as string) as T;
  if (resultado.excecao) {
    // No desktop: traceback no terminal e nada na tela.
    console.error(`[lozweb.${nome}]`, resultado.excecao);
  }
  return resultado;
}

/** Deixa o navegador pintar a tela (ex.: estado "processando") antes de uma chamada síncrona ao Python. */
export function aguardarPintura(): Promise<void> {
  return new Promise((resolve) => requestAnimationFrame(() => setTimeout(resolve, 0)));
}

export function persistir(): void {
  if (!motorAtual) return;
  salvarArquivos(motorAtual.py, PASTA_DADOS, motorAtual.arquivosPersistentes);
}
