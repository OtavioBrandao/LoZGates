/** Botões das 9 leis do Resolver (FrontEnd/screens/resolver/resolver_screen.py), em dois grupos. */
export interface BotaoLei {
  texto: string;
  desc: string;
  /** Índice em simplificador_interativo.LEIS_LOGICAS */
  idx: number;
}

export const LEIS_BASICAS: BotaoLei[] = [
  { texto: 'Inversa', desc: 'A · ¬A = 0', idx: 0 },
  { texto: 'Nula', desc: 'A · 0 = 0', idx: 1 },
  { texto: 'Identidade', desc: 'A · 1 = A', idx: 2 },
  { texto: 'Idempotente', desc: 'A · A = A', idx: 3 },
];

export const LEIS_ESTRUTURAIS: BotaoLei[] = [
  { texto: 'Absorção', desc: 'A·(A+B)=A', idx: 4 },
  { texto: 'De Morgan', desc: '¬(A·B)=¬A+¬B', idx: 5 },
  { texto: 'Distributiva', desc: '(A+B)·(A+C)', idx: 6 },
  { texto: 'Associativa', desc: '(A·B)·C', idx: 7 },
  { texto: 'Comutativa', desc: 'B·A = A·B', idx: 8 },
];
