/** Formas distintivas das portas (ANSI/IEEE Std 91), num quadro de 48×32. */
const FORMAS: Record<string, string[]> = {
  and: ['M2 10 H10 M2 22 H10 M34 16 H46', 'M10 4 H22 A12 12 0 0 1 22 28 H10 Z'],
  or: ['M2 10 H13 M2 22 H13 M36 16 H46', 'M8 4 Q22 4 36 16 Q22 28 8 28 Q14 16 8 4 Z'],
  not: ['M2 16 H10 M39 16 H46', 'M10 5 L31 16 L10 27 Z'],
  nand: ['M2 10 H10 M2 22 H10 M39 16 H46', 'M10 4 H19 A12 12 0 0 1 19 28 H10 Z'],
  nor: ['M2 10 H11 M2 22 H11 M39 16 H46', 'M6 4 Q19 4 31 16 Q19 28 6 28 Q12 16 6 4 Z'],
  xor: ['M2 10 H13 M2 22 H13 M36 16 H46', 'M3 4 Q9 16 3 28', 'M8 4 Q22 4 36 16 Q22 28 8 28 Q14 16 8 4 Z'],
  xnor: ['M2 10 H11 M2 22 H11 M39 16 H46', 'M2 4 Q8 16 2 28', 'M6 4 Q19 4 31 16 Q19 28 6 28 Q12 16 6 4 Z'],
};
const COM_BOLHA: Record<string, number> = { not: 35, nand: 35, nor: 35, xnor: 35 };

export type TipoDePorta = keyof typeof FORMAS;

/** Só os traços (no quadro 48×32), para quem já está dentro de um <svg> (a paleta do editor). */
export function TracosDaPorta({ tipo }: { tipo: TipoDePorta }) {
  const bolha = COM_BOLHA[tipo];
  return (
    <>
      {FORMAS[tipo].map((d, i) => (
        <path key={i} d={d} />
      ))}
      {bolha !== undefined && <circle cx={bolha} cy={16} r={3.5} />}
    </>
  );
}

export function IconePorta({ tipo, tamanho = 48, rotulo, className = '' }: { tipo: TipoDePorta; tamanho?: number; rotulo?: string; className?: string }) {
  return (
    <svg
      className={`icone-porta ${className}`}
      width={tamanho}
      height={Math.round((tamanho * 32) / 48)}
      viewBox="0 0 48 32"
      role={rotulo ? 'img' : undefined}
      aria-label={rotulo}
      aria-hidden={rotulo ? undefined : true}
      focusable="false"
    >
      <TracosDaPorta tipo={tipo} />
    </svg>
  );
}
