/**
 * Formas das portas lógicas do editor, nas mesmas medidas do desenho original
 * (CircuitDrawer.draw_gate_shape): largura útil 40, altura 80, círculo de
 * negação com raio 8. As coordenadas são as do "mundo" do circuito; as cores
 * vêm do tema (classe porta-editor no CSS).
 */

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
}

/** Desenha a porta com o canto superior esquerdo em (x, y). */
export function FormaDaPorta({ tipo, x, y }: PropsPorta) {
  const centroY = y + A / 2;
  const bolha = <circle className="porta-editor__corpo" cx={x + L + 8} cy={centroY} r={8} />;
  const curva = <path className="porta-editor__traco" d={caminhoCurvaXor(x, y)} />;
  switch (tipo) {
    case 'and':
      return <path className="porta-editor__corpo" d={caminhoAnd(x, y)} />;
    case 'nand':
      return (
        <g>
          <path className="porta-editor__corpo" d={caminhoAnd(x, y)} />
          {bolha}
        </g>
      );
    case 'or':
      return <path className="porta-editor__corpo" d={caminhoOr(x, y)} />;
    case 'nor':
      return (
        <g>
          <path className="porta-editor__corpo" d={caminhoOr(x, y)} />
          {bolha}
        </g>
      );
    case 'xor':
      return (
        <g>
          {curva}
          <path className="porta-editor__corpo" d={caminhoOr(x, y)} />
        </g>
      );
    case 'xnor':
      return (
        <g>
          {curva}
          <path className="porta-editor__corpo" d={caminhoOr(x, y)} />
          {bolha}
        </g>
      );
    case 'not':
      return (
        <g>
          <path className="porta-editor__corpo" d={`M ${x} ${y + 15} L ${x} ${y + A - 15} L ${x + 30} ${centroY} Z`} />
          <circle className="porta-editor__corpo" cx={x + 38} cy={centroY} r={8} />
        </g>
      );
    default:
      return null;
  }
}
