interface Props {
  nome: string;
  ligada: boolean;
  aoAlternar: () => void;
  className?: string;
}

/** Interruptor de uma entrada do circuito: nome, alavanca e o nível (0 ou 1). */
export function ChaveDeEntrada({ nome, ligada, aoAlternar, className = '' }: Props) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={ligada}
      aria-label={`Entrada ${nome}`}
      className={`chave-entrada ${ligada ? 'chave-entrada--1' : ''} ${className}`}
      onClick={aoAlternar}
    >
      <span className="chave-entrada__nome mono">{nome}</span>
      <span className="chave-entrada__trilho" aria-hidden="true">
        <span className="chave-entrada__botao" />
      </span>
      <span className="chave-entrada__valor mono" aria-hidden="true">
        {ligada ? '1' : '0'}
      </span>
    </button>
  );
}
