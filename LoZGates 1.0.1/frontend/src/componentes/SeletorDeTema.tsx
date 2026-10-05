import { useState } from 'react';
import { NOME_DO_TEMA, salvarTema, temaSalvo, type Tema } from '../tema';

const OPCOES: Tema[] = ['sistema', 'claro', 'escuro'];

/** Tema da interface: automático (segue o sistema), claro ou escuro. */
export function SeletorDeTema() {
  const [tema, setTema] = useState<Tema>(temaSalvo);
  return (
    <div className="seletor-tema" role="group" aria-label="Tema">
      {OPCOES.map((opcao) => (
        <button
          key={opcao}
          type="button"
          className="seletor-tema__opcao"
          aria-pressed={tema === opcao}
          onClick={() => {
            salvarTema(opcao);
            setTema(opcao);
          }}
        >
          {NOME_DO_TEMA[opcao]}
        </button>
      ))}
    </div>
  );
}
