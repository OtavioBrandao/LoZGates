/**
 * Tema claro (datasheet) ou escuro (planta técnica). Por padrão segue o
 * sistema operacional; a escolha do aluno fica só neste navegador.
 */
export type Tema = 'sistema' | 'claro' | 'escuro';

const CHAVE = 'lozgates:tema';

export function temaSalvo(): Tema {
  try {
    const valor = window.localStorage.getItem(CHAVE);
    return valor === 'claro' || valor === 'escuro' ? valor : 'sistema';
  } catch {
    return 'sistema';
  }
}

/** Aplica no <html>: sem atributo, vale o prefers-color-scheme. */
export function aplicarTema(tema: Tema): void {
  const raiz = document.documentElement;
  if (tema === 'sistema') delete raiz.dataset.tema;
  else raiz.dataset.tema = tema;
}

export function salvarTema(tema: Tema): void {
  aplicarTema(tema);
  try {
    if (tema === 'sistema') window.localStorage.removeItem(CHAVE);
    else window.localStorage.setItem(CHAVE, tema);
  } catch {
    // armazenamento bloqueado: a escolha vale só até recarregar
  }
}

/** O tema que está valendo agora (resolve "sistema"). */
export function temaEfetivo(tema: Tema): 'claro' | 'escuro' {
  if (tema !== 'sistema') return tema;
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'escuro' : 'claro';
}

export const PROXIMO_TEMA: Record<Tema, Tema> = { sistema: 'claro', claro: 'escuro', escuro: 'sistema' };
export const NOME_DO_TEMA: Record<Tema, string> = { sistema: 'Automático', claro: 'Claro', escuro: 'Escuro' };
