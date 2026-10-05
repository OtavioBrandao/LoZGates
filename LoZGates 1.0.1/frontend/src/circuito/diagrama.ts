/**
 * Geometria do diagrama de tempo: cada linha da tabela-verdade vira uma fatia
 * de tempo, e cada variável (e a saída S) vira uma onda quadrada. Os níveis
 * vêm prontos da tabela-verdade calculada no servidor.
 */
export interface LinhaDoDiagrama {
  nome: string;
  niveis: number[];
  saida: boolean;
  /** Caminho da onda (SVG) */
  onda: string;
  /** Trechos em nível 1, para o preenchimento */
  altos: { x: number; largura: number }[];
  topo: number;
}

export interface Diagrama {
  largura: number;
  altura: number;
  larguraFatia: number;
  inicioX: number;
  alturaLinha: number;
  linhas: LinhaDoDiagrama[];
  rotulos: { x: number; texto: string }[];
  baseRotulos: number;
}

const ROTULO = 44;
const ALTURA_LINHA = 34;
const ESPACO = 10;
const NIVEL_ALTO = 6;
const NIVEL_BAIXO = 26;
const MARGEM_DIREITA = 8;
/** Com espaço sobrando as fatias se alargam, até este limite. */
const FATIA_MAXIMA = 96;

/** Largura mínima de uma fatia: cabe o rótulo da combinação ("0110", 11 px monoespaçado ≈ 6,6 px por dígito). */
export function larguraDaFatia(variaveis: number): number {
  return Math.max(36, Math.ceil(variaveis * 6.6 + 12));
}

/** `larguraDisponivel` (em px) estica as fatias para ocupar o painel; sem ela, usa a largura mínima. */
export function montarDiagrama(variaveis: string[], tabela: number[][], resultados: number[], larguraDisponivel = 0): Diagrama {
  const cabe = Math.floor((larguraDisponivel - ROTULO - MARGEM_DIREITA) / Math.max(1, tabela.length));
  const fatia = Math.max(larguraDaFatia(variaveis.length), Math.min(FATIA_MAXIMA, cabe));
  const series = [
    ...variaveis.map((nome, coluna) => ({ nome, niveis: tabela.map((linha) => linha[coluna]), saida: false })),
    { nome: 'S', niveis: resultados, saida: true },
  ];
  const linhas = series.map((serie, i) => {
    const topo = i * (ALTURA_LINHA + ESPACO);
    const y = (nivel: number) => topo + (nivel ? NIVEL_ALTO : NIVEL_BAIXO);
    const partes: string[] = [];
    const altos: { x: number; largura: number }[] = [];
    serie.niveis.forEach((nivel, k) => {
      const x = ROTULO + k * fatia;
      partes.push(k === 0 ? `M${x} ${y(nivel)}` : `V${y(nivel)}`);
      partes.push(`H${x + fatia}`);
      if (nivel) {
        const anterior = altos[altos.length - 1];
        if (anterior && anterior.x + anterior.largura === x) anterior.largura += fatia;
        else altos.push({ x, largura: fatia });
      }
    });
    return { ...serie, onda: partes.join(' '), altos, topo };
  });
  const baseRotulos = series.length * (ALTURA_LINHA + ESPACO) + 6;
  return {
    largura: ROTULO + tabela.length * fatia + MARGEM_DIREITA,
    altura: baseRotulos + 16,
    larguraFatia: fatia,
    inicioX: ROTULO,
    alturaLinha: ALTURA_LINHA,
    linhas,
    rotulos: tabela.map((linha, k) => ({
      x: ROTULO + k * fatia + fatia / 2,
      texto: linha.slice(0, variaveis.length).join(''),
    })),
    baseRotulos,
  };
}

/** Índice da linha da tabela-verdade para os valores atuais (a primeira variável é o bit mais alto). */
export function indiceDaCombinacao(variaveis: string[], valores: Record<string, boolean>): number {
  return variaveis.reduce((indice, nome) => indice * 2 + (valores[nome] ? 1 : 0), 0);
}

/** Valores das variáveis na linha `indice` da tabela-verdade. */
export function combinacaoDoIndice(variaveis: string[], indice: number): Record<string, boolean> {
  const n = variaveis.length;
  return Object.fromEntries(variaveis.map((nome, i) => [nome, Boolean((indice >> (n - 1 - i)) & 1)]));
}
