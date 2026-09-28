import { useRef, type KeyboardEvent } from 'react';

interface Props<T extends string> {
  abas: { id: T; rotulo: string }[];
  atual: T;
  aoMudar: (id: T) => void;
  rotulo: string;
  variante?: 'principal' | 'manual';
  idBase: string;
}

/** Barra de abas acessível (equivale ao segmented button do CTkTabview). */
export function Abas<T extends string>({ abas, atual, aoMudar, rotulo, variante = 'principal', idBase }: Props<T>) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);

  const aoTeclar = (e: KeyboardEvent, indice: number) => {
    let proximo = -1;
    if (e.key === 'ArrowRight') proximo = (indice + 1) % abas.length;
    if (e.key === 'ArrowLeft') proximo = (indice - 1 + abas.length) % abas.length;
    if (e.key === 'Home') proximo = 0;
    if (e.key === 'End') proximo = abas.length - 1;
    if (proximo >= 0) {
      e.preventDefault();
      refs.current[proximo]?.focus();
      aoMudar(abas[proximo].id);
    }
  };

  return (
    <div className={`abas abas--${variante}`} role="tablist" aria-label={rotulo}>
      {abas.map((aba, i) => (
        <button
          key={aba.id}
          ref={(el) => {
            refs.current[i] = el;
          }}
          type="button"
          role="tab"
          id={`${idBase}-aba-${aba.id}`}
          aria-selected={aba.id === atual}
          aria-controls={`${idBase}-painel-${aba.id}`}
          tabIndex={aba.id === atual ? 0 : -1}
          className="abas__botao"
          onClick={() => aba.id !== atual && aoMudar(aba.id)}
          onKeyDown={(e) => aoTeclar(e, i)}
        >
          {aba.rotulo}
        </button>
      ))}
    </div>
  );
}
