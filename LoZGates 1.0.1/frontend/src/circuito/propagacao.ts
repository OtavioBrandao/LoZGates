import type { FioDoLayout, LayoutCircuito, Ponto } from '../api/tipos';

/**
 * Quando uma entrada muda, o novo nível percorre o circuito: primeiro o
 * barramento da entrada, depois os fios que saem dele, a saída de cada porta
 * cujo valor mudou, e assim por diante até o LED. Cada trecho leva o mesmo
 * tempo; `ordem` diz quantos trechos o sinal já atravessou antes deste.
 * Os níveis vêm prontos do servidor: aqui só se compara o antes e o depois.
 */
export const DURACAO_DO_TRECHO = 260; // ms

/** Disparado no <svg> do circuito por quem precisa do desenho já no estado final (exportar PNG). */
export const EVENTO_ESTADO_FINAL = 'circuito:estado-final';

export interface Trecho {
  /** id do fio, `barramento:<id>` ou `saida` */
  id: string;
  pontos: Ponto[];
  comprimento: number;
  /** true: o trecho acende (0 → 1); false: apaga (1 → 0) */
  sobe: boolean;
  ordem: number;
}

export interface Propagacao {
  trechos: Trecho[];
  /** Trechos que acendem: até o sinal chegar, continuam desenhados apagados */
  sobem: Set<string>;
  led: { acende: boolean; ordem: number } | null;
  /** Tempo total, em ms */
  duracao: number;
}

export function comprimento(pontos: Ponto[]): number {
  let total = 0;
  for (let i = 1; i < pontos.length; i += 1) {
    total += Math.hypot(pontos[i][0] - pontos[i - 1][0], pontos[i][1] - pontos[i - 1][1]);
  }
  return total;
}

const mudou = (antes: boolean | null | undefined, depois: boolean | null) =>
  antes !== undefined && antes !== null && depois !== null && antes !== depois;

function mesmoDesenho(a: LayoutCircuito, b: LayoutCircuito): boolean {
  return (
    a.expressao_booleana === b.expressao_booleana &&
    a.barramentos.length === b.barramentos.length &&
    a.barramentos.every((barramento, i) => barramento.id === b.barramentos[i].id) &&
    a.fios.length === b.fios.length &&
    a.fios.every((fio, i) => fio.id === b.fios[i].id)
  );
}

/** O que muda entre dois layouts do mesmo circuito, ou null se nada muda (ou o circuito é outro). */
export function calcularPropagacao(antes: LayoutCircuito, depois: LayoutCircuito): Propagacao | null {
  if (!mesmoDesenho(antes, depois)) return null;
  const trechos: Trecho[] = [];
  const novoTrecho = (id: string, pontos: Ponto[], sobe: boolean, ordem: number) =>
    trechos.push({ id, pontos, comprimento: comprimento(pontos), sobe, ordem });

  const barramentosAntes = new Map(antes.barramentos.map((b) => [b.id, b.valor]));
  for (const b of depois.barramentos) {
    if (mudou(barramentosAntes.get(b.id), b.valor)) {
      novoTrecho(`barramento:${b.id}`, [[b.x, b.y_inicio], [b.x, b.y_fim]], Boolean(b.valor), 0);
    }
  }

  const fiosAntes = new Map(antes.fios.map((f) => [f.id, f.valor]));
  const entradasDaPorta = new Map<string, FioDoLayout[]>();
  for (const fio of depois.fios) {
    const lista = entradasDaPorta.get(fio.destino.porta) ?? [];
    lista.push(fio);
    entradasDaPorta.set(fio.destino.porta, lista);
  }
  const ordemDoFio = new Map<string, number | null>();
  const ordemDaPorta = new Map<string, number | null>();

  // A porta "dispara" quando chega a última das suas entradas que mudaram
  const ordemDaPortaDe = (id: string): number | null => {
    if (ordemDaPorta.has(id)) return ordemDaPorta.get(id) ?? null;
    ordemDaPorta.set(id, null);
    const ordens = (entradasDaPorta.get(id) ?? []).map(ordemDe).filter((o): o is number => o !== null);
    const resultado = ordens.length ? Math.max(...ordens) : null;
    ordemDaPorta.set(id, resultado);
    return resultado;
  };

  function ordemDe(fio: FioDoLayout): number | null {
    if (ordemDoFio.has(fio.id)) return ordemDoFio.get(fio.id) ?? null;
    if (!mudou(fiosAntes.get(fio.id), fio.valor)) {
      ordemDoFio.set(fio.id, null);
      return null;
    }
    const origem = fio.origem.tipo === 'barramento' ? 0 : (ordemDaPortaDe(fio.origem.id) ?? 0);
    ordemDoFio.set(fio.id, origem + 1);
    return origem + 1;
  }

  for (const fio of depois.fios) {
    const ordem = ordemDe(fio);
    if (ordem !== null) novoTrecho(fio.id, fio.pontos, Boolean(fio.valor), ordem);
  }

  let led: Propagacao['led'] = null;
  if (depois.saida && antes.saida && mudou(antes.saida.valor, depois.saida.valor)) {
    const raiz = depois.portas[0]?.id;
    const ordem = (raiz ? ordemDaPortaDe(raiz) : null) ?? 0;
    novoTrecho('saida', [depois.saida.de, depois.saida.ate], Boolean(depois.saida.valor), ordem + 1);
    led = { acende: Boolean(depois.saida.valor), ordem: ordem + 2 };
  }

  if (!trechos.length) return null;
  const ultima = Math.max(...trechos.map((t) => t.ordem), led?.ordem ?? 0);
  return {
    trechos,
    sobem: new Set(trechos.filter((t) => t.sobe).map((t) => t.id)),
    led,
    duracao: (ultima + 1) * DURACAO_DO_TRECHO,
  };
}

/** O usuário pediu menos movimento? Então o circuito muda de estado sem animação. */
export function movimentoReduzido(): boolean {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true;
}
