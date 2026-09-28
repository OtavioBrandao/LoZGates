/**
 * O DetailedUserLogger (FrontEnd/logging_system.py) grava user_activity_detailed.json e
 * logging_settings.json na pasta de trabalho, como no desktop. No navegador essa pasta
 * fica na memória; aqui copiamos os arquivos de/para o localStorage para que os dados
 * de uso sobrevivam entre visitas.
 */
import type { PyodideInterface } from 'pyodide';

const PREFIXO = 'lozgates:arquivo:';

export function restaurarArquivos(py: PyodideInterface, pasta: string): void {
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const chave = localStorage.key(i);
      if (!chave || !chave.startsWith(PREFIXO)) continue;
      const nome = chave.slice(PREFIXO.length);
      if (nome.includes('/') || nome.includes('..')) continue;
      const conteudo = localStorage.getItem(chave);
      if (conteudo !== null) py.FS.writeFile(`${pasta}/${nome}`, conteudo, { encoding: 'utf8' });
    }
  } catch (erro) {
    console.warn('Não foi possível restaurar os dados de uso salvos:', erro);
  }
}

export function salvarArquivos(py: PyodideInterface, pasta: string, nomes: string[]): void {
  for (const nome of nomes) {
    try {
      const caminho = `${pasta}/${nome}`;
      if (!py.FS.analyzePath(caminho).exists) continue;
      const conteudo = py.FS.readFile(caminho, { encoding: 'utf8' }) as string;
      localStorage.setItem(PREFIXO + nome, conteudo);
    } catch (erro) {
      console.warn(`Não foi possível guardar ${nome} no navegador:`, erro);
    }
  }
}
