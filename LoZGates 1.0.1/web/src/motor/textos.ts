import { chamar, type RespostaApi } from './pyodide';

export interface ModoCircuito {
  chave: string;
  name: string;
  description: string;
  restrictions: string[] | null;
  color: string;
  icon: string;
  difficulty: string;
}

export interface Textos extends RespostaApi {
  duvida_circuitos: string;
  welcome_message: string;
  modos: ModoCircuito[];
  dicas_modos: Record<string, string[]>;
}

let cache: Textos | null = null;

/** Textos vindos de config.py e de CircuitModeManager (uma leitura só). */
export function textos(): Textos {
  if (!cache) cache = chamar<Textos>('textos');
  return cache;
}
