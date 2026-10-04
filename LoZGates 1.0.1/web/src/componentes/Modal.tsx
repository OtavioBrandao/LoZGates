import { useEffect, useId, useRef, type ReactNode } from 'react';

interface Props {
  titulo: string;
  aoFechar: () => void;
  children: ReactNode;
  tamanho?: 'pequeno' | 'medio' | 'grande';
  /** Rodapé fixo (botões) */
  rodape?: ReactNode;
  classe?: string;
}

/** Janela modal (substitui os CTkToplevel/tk.Toplevel do desktop). */
export function Modal({ titulo, aoFechar, children, tamanho = 'medio', rodape, classe = '' }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const idTitulo = useId();
  const aoFecharRef = useRef(aoFechar);
  aoFecharRef.current = aoFechar;

  useEffect(() => {
    const dialogo = ref.current;
    if (dialogo && !dialogo.open) dialogo.showModal();
    return () => dialogo?.close();
  }, []);

  return (
    <dialog
      ref={ref}
      className={`modal modal--${tamanho} ${classe}`}
      aria-labelledby={idTitulo}
      onCancel={(e) => {
        e.preventDefault();
        aoFecharRef.current();
      }}
      onMouseDown={(e) => {
        if (e.target === ref.current) aoFecharRef.current();
      }}
    >
      <header className="modal__cabecalho">
        <h2 id={idTitulo} className="modal__titulo">
          {titulo}
        </h2>
        <button type="button" className="modal__fechar" onClick={() => aoFecharRef.current()} aria-label="Fechar janela">
          ×
        </button>
      </header>
      <div className="modal__corpo">{children}</div>
      {rodape && <footer className="modal__rodape">{rodape}</footer>}
    </dialog>
  );
}
