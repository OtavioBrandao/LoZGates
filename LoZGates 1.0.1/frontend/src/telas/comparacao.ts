import type { TabelaVerdade } from '../api/tipos';
import { combinacaoDoIndice, indiceDaCombinacao } from '../circuito/diagrama';

export interface LinhaComparada {
  valores: number[];
  primeira: number;
  segunda: number;
  iguais: boolean;
}

export interface Comparacao {
  variaveis: string[];
  linhas: LinhaComparada[];
  diferentes: number;
}

/**
 * Junta as tabelas-verdade (calculadas no servidor) de duas expressões sobre
 * todas as variáveis que aparecem nelas. Uma expressão sem uma das variáveis
 * vale o mesmo com ela em 0 ou em 1, então basta procurar a linha dela que
 * tem os valores das suas próprias variáveis.
 */
export function compararTabelas(variaveis: string[], primeira: TabelaVerdade, segunda: TabelaVerdade): Comparacao {
  const resultado = (tabela: TabelaVerdade, valores: Record<string, boolean>) => {
    const proprias = tabela.colunas.slice(0, tabela.total_variaveis);
    return tabela.resultados_finais[indiceDaCombinacao(proprias, valores)] ? 1 : 0;
  };
  const linhas: LinhaComparada[] = [];
  for (let i = 0; i < 2 ** variaveis.length; i += 1) {
    const valores = combinacaoDoIndice(variaveis, i);
    const a = resultado(primeira, valores);
    const b = resultado(segunda, valores);
    linhas.push({ valores: variaveis.map((v) => (valores[v] ? 1 : 0)), primeira: a, segunda: b, iguais: a === b });
  }
  return { variaveis, linhas, diferentes: linhas.filter((l) => !l.iguais).length };
}
