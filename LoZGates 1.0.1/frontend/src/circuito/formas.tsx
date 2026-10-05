/**
 * Formas das portas lógicas, nas mesmas medidas do desenho original
 * (CircuitDrawer.draw_gate_shape): largura útil 40, altura 80, círculo de
 * negação com raio 8. As coordenadas são as do "mundo" do circuito.
 */

/** Cores do desenho original (CircuitDrawer) */
export const CORES = {
  fundo: '#000000',
  branco: 'rgb(230,230,230)',
  rotulo: '#ffffff',
  fio: 'rgb(200,200,200)',
  selecionado: 'rgb(255,255,0)',
  pino: 'rgb(100,255,100)',
  pinoLigado: 'rgb(255,255,0)',
  saida: 'rgb(220,60,60)',
  grade: 'rgb(30,30,30)',
  porta: {
    and: 'rgb(60,120,220)',
    or: 'rgb(50,200,130)',
    not: 'rgb(250,170,70)',
    nand: 'rgb(120,60,220)',
    nor: 'rgb(200,50,130)',
    xor: 'rgb(220,120,60)',
    xnor: 'rgb(60,220,120)',
  } as Record<string, string>,
};

const L = 40; // GATE_WIDTH - 20
const A = 80; // GATE_HEIGHT

function caminhoAnd(x: number, y: number): string {
  return `M ${x} ${y} H ${x + L / 2} A ${L / 2} ${A / 2} 0 0 1 ${x + L / 2} ${y + A} H ${x} Z`;
}

function caminhoOr(x: number, y: number): string {
  const tras = x - 7.5;
  return `M ${tras} ${y} H ${x + L / 2} A ${L / 2} ${A / 2} 0 0 1 ${x + L / 2} ${y + A} H ${tras} A 10 ${A / 2} 0 0 0 ${tras} ${y} Z`;
}

function caminhoCurvaXor(x: number, y: number): string {
  const tras = x - 15;
  return `M ${tras} ${y + 5} A 8 ${A / 2 - 5} 0 0 1 ${tras} ${y + A - 5}`;
}

interface PropsPorta {
  /** and, or, not, nand, nor, xor, xnor */
  tipo: string;
  x: number;
  y: number;
  cor?: string;
}

/** Desenha a porta com o canto superior esquerdo em (x, y). */
export function FormaDaPorta({ tipo, x, y, cor = CORES.porta[tipo] }: PropsPorta) {
  const traco = { fill: 'none', stroke: cor, strokeWidth: 3, strokeLinejoin: 'round' as const };
  const centroY = y + A / 2;
  switch (tipo) {
    case 'and':
      return <path d={caminhoAnd(x, y)} {...traco} />;
    case 'nand':
      return (
        <g>
          <path d={caminhoAnd(x, y)} {...traco} />
          <circle cx={x + L + 8} cy={centroY} r={8} {...traco} />
        </g>
      );
    case 'or':
      return <path d={caminhoOr(x, y)} {...traco} />;
    case 'nor':
      return (
        <g>
          <path d={caminhoOr(x, y)} {...traco} />
          <circle cx={x + L + 8} cy={centroY} r={8} {...traco} />
        </g>
      );
    case 'xor':
      return (
        <g>
          <path d={caminhoCurvaXor(x, y)} {...traco} />
          <path d={caminhoOr(x, y)} {...traco} />
        </g>
      );
    case 'xnor':
      return (
        <g>
          <path d={caminhoCurvaXor(x, y)} {...traco} />
          <path d={caminhoOr(x, y)} {...traco} />
          <circle cx={x + L + 8} cy={centroY} r={8} {...traco} />
        </g>
      );
    case 'not':
      return (
        <g>
          <path d={`M ${x} ${y + 15} L ${x} ${y + A - 15} L ${x + 30} ${centroY} Z`} {...traco} />
          <circle cx={x + 38} cy={centroY} r={8} {...traco} />
        </g>
      );
    default:
      return null;
  }
}
