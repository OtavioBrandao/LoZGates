import { useState } from 'react';
import { NOME_DO_TEMA, salvarTema, temaSalvo, type Tema } from '../tema';

const OPCOES: Tema[] = ['sistema', 'claro', 'escuro'];
/** No celular o "Automático" vira "Auto", para o seletor caber ao lado do Voltar. */
const CURTO: Partial<Record<Tema, string>> = { sistema: 'Auto' };

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
          {CURTO[opcao] ? (
            <>
              <span className="seletor-tema__longo">{NOME_DO_TEMA[opcao]}</span>
              <span className="seletor-tema__curto" aria-hidden="true">
                {CURTO[opcao]}
              </span>
            </>
          ) : (
            NOME_DO_TEMA[opcao]
          )}
        </button>
      ))}
    </div>
  );
}
