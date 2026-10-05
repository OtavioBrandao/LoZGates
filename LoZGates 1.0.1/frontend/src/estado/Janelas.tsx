import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from 'react';
import { ChatIA } from '../modais/ChatIA';
import { CompartilharDados, type EscolhaCompartilhamento } from '../modais/CompartilharDados';
import { ManualInterativo } from '../modais/ManualInterativo';
import { PopupDuvida, PopupErro } from '../modais/Popups';
import { TabelaVerdade, type DadosTabela } from '../modais/TabelaVerdade';

type Janela =
  | { id: number; tipo: 'erro'; mensagem: string; titulo?: string }
  | { id: number; tipo: 'duvida'; mensagem: string }
  | { id: number; tipo: 'tabela'; dados: DadosTabela }
  | { id: number; tipo: 'manual' }
  | { id: number; tipo: 'chat'; expressao: string; contexto: string }
  | { id: number; tipo: 'compartilhar'; preview: string; responder: (e: EscolhaCompartilhamento) => void };

type SemId<T> = T extends { id: number } ? Omit<T, 'id'> : never;

interface ApiJanelas {
  popupErro: (mensagem: string, titulo?: string) => void;
  popupDuvida: (mensagem: string) => void;
  abrirTabela: (dados: DadosTabela) => void;
  abrirManual: () => void;
  abrirChat: (expressao: string, contexto: string) => void;
  perguntarCompartilhamento: (preview: string) => Promise<EscolhaCompartilhamento>;
}

const Contexto = createContext<ApiJanelas | null>(null);

export function useJanelas(): ApiJanelas {
  const api = useContext(Contexto);
  if (!api) throw new Error('useJanelas fora do ProvedorJanelas');
  return api;
}

/** As janelas que o desktop abria como CTkToplevel (popups, tabela verdade, manual, chat, consentimento). */
export function ProvedorJanelas({ children }: { children: ReactNode }) {
  const [janelas, setJanelas] = useState<Janela[]>([]);
  const sequencia = useRef(0);

  const abrir = useCallback((janela: SemId<Janela>) => {
    sequencia.current += 1;
    const id = sequencia.current;
    setJanelas((atuais) => [...atuais, { ...janela, id } as Janela]);
  }, []);

  const fechar = useCallback((id: number) => {
    setJanelas((atuais) => atuais.filter((j) => j.id !== id));
  }, []);

  const api = useMemo<ApiJanelas>(
    () => ({
      popupErro: (mensagem, titulo) => abrir({ tipo: 'erro', mensagem, titulo }),
      popupDuvida: (mensagem) => abrir({ tipo: 'duvida', mensagem }),
      abrirTabela: (dados) => abrir({ tipo: 'tabela', dados }),
      abrirManual: () =>
        // InteractiveHelpSystem.show_help(): se já estiver aberto, só traz para frente
        setJanelas((atuais) => {
          if (atuais.some((j) => j.tipo === 'manual')) return atuais;
          sequencia.current += 1;
          return [...atuais, { id: sequencia.current, tipo: 'manual' }];
        }),
      abrirChat: (expressao, contexto) => abrir({ tipo: 'chat', expressao, contexto }),
      perguntarCompartilhamento: (preview) =>
        new Promise<EscolhaCompartilhamento>((resolver) => abrir({ tipo: 'compartilhar', preview, responder: resolver })),
    }),
    [abrir],
  );

  return (
    <Contexto.Provider value={api}>
      {children}
      {janelas.map((j) => {
        const aoFechar = () => fechar(j.id);
        switch (j.tipo) {
          case 'erro':
            return <PopupErro key={j.id} mensagem={j.mensagem} titulo={j.titulo} aoFechar={aoFechar} />;
          case 'duvida':
            return <PopupDuvida key={j.id} mensagem={j.mensagem} aoFechar={aoFechar} />;
          case 'tabela':
            return <TabelaVerdade key={j.id} dados={j.dados} aoFechar={aoFechar} />;
          case 'manual':
            return <ManualInterativo key={j.id} aoFechar={aoFechar} />;
          case 'chat':
            return <ChatIA key={j.id} expressao={j.expressao} contexto={j.contexto} aoFechar={aoFechar} />;
          case 'compartilhar':
            return (
              <CompartilharDados
                key={j.id}
                preview={j.preview}
                aoEscolher={(escolha) => {
                  fechar(j.id);
                  j.responder(escolha);
                }}
              />
            );
        }
      })}
    </Contexto.Provider>
  );
}
