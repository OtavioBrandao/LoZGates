import { useEffect, useRef, useState } from 'react';
import { api, mensagemDe } from '../api/cliente';
import { Botao } from '../componentes/Botao';
import { Modal } from '../componentes/Modal';

type Remetente = 'Você' | 'IA' | 'Sistema';

interface Mensagem {
  id: number;
  remetente: Remetente;
  texto: string;
  erro?: boolean;
  carregando?: boolean;
}

/**
 * Pergunta à IA pela API (a chave fica no servidor, D7) e devolve o que o
 * callback do AIAssistant recebia: (resposta, erro).
 */
async function perguntarIA(
  tipo: 'sugestao' | 'pergunta',
  expressao: string,
  contexto: string,
  pergunta: string,
): Promise<{ resposta: string | null; erro: string | null }> {
  try {
    const { resposta } = tipo === 'sugestao' ? await api.sugestaoIa(expressao, contexto) : await api.perguntaIa(pergunta, expressao);
    return { resposta, erro: null };
  } catch (e) {
    return { resposta: null, erro: mensagemDe(e) };
  }
}

const EXPLICACAO_LEIS = `Principais leis da lógica proposicional:

• De Morgan: ~(A∧B) = ~A∨~B e ~(A∨B) = ~A∧~B
• Distributiva: A∧(B∨C) = (A∧B)∨(A∧C)
• Absorção: A∧(A∨B) = A e A∨(A∧B) = A
• Identidade: A∧1 = A e A∨0 = A
• Nula: A∧0 = 0 e A∨1 = 1
• Inversa: A∧~A = 0 e A∨~A = 1
• Idempotente: A∧A = A e A∨A = A

Use essas leis para simplificar sua expressão passo a passo!`;

/** AIChatPopup (FrontEnd/dialogs/ai_chat_popup.py) */
export function ChatIA({ expressao, contexto, aoFechar }: { expressao: string; contexto: string; aoFechar: () => void }) {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [entrada, setEntrada] = useState('');
  const sequencia = useRef(0);
  const fim = useRef<HTMLDivElement>(null);
  const aberto = useRef(true);

  const adicionar = (remetente: Remetente, texto: string, erro = false, carregando = false) => {
    sequencia.current += 1;
    const id = sequencia.current;
    setMensagens((m) => [...m, { id, remetente, texto, erro, carregando }]);
    return id;
  };
  const remover = (id: number) => setMensagens((m) => m.filter((x) => x.id !== id));

  useEffect(() => {
    fim.current?.scrollIntoView({ block: 'end' });
  }, [mensagens]);

  // get_initial_suggestion(): pedida automaticamente se houver expressão
  useEffect(() => {
    aberto.current = true;
    if (expressao) {
      void perguntarIA('sugestao', expressao, contexto, '').then(({ resposta, erro }) => {
        if (!aberto.current) return;
        if (erro) {
          adicionar('IA', `Erro ao conectar: ${erro}`, true);
        } else {
          adicionar('IA', `Olá! Vou ajudar você a simplificar a expressão: ${expressao}`);
          if (resposta) adicionar('IA', resposta);
        }
      });
    }
    return () => {
      aberto.current = false;
    };
  }, []); // só ao abrir a janela

  const enviarMensagem = () => {
    const mensagem = entrada.trim();
    if (!mensagem) return;
    adicionar('Você', mensagem);
    setEntrada('');
    const carregando = adicionar('IA', 'IA está pensando...', false, true);
    void perguntarIA('pergunta', expressao, '', mensagem).then(({ resposta, erro }) => {
      if (!aberto.current) return;
      remover(carregando);
      if (erro) adicionar('IA', `Erro: ${erro}`, true);
      else adicionar('IA', resposta || 'Desculpe, não consegui gerar uma resposta.');
    });
  };

  const novaSugestao = () => {
    if (!expressao) {
      adicionar('Sistema', 'Nenhuma expressão disponível para análise.', true);
      return;
    }
    adicionar('Você', 'Solicitar nova sugestão');
    const carregando = adicionar('IA', 'IA analisando expressão...', false, true);
    void perguntarIA('sugestao', expressao, contexto, '').then(({ resposta, erro }) => {
      if (!aberto.current) return;
      remover(carregando);
      if (erro) adicionar('IA', `Erro: ${erro}`, true);
      else adicionar('IA', resposta || 'Não consegui gerar uma sugestão específica.');
    });
  };

  const explicarLeis = () => {
    adicionar('Você', 'Explicar leis da lógica');
    adicionar('IA', EXPLICACAO_LEIS);
  };

  return (
    <Modal
      titulo="Sugestão de IA - Simplificador Lógico"
      tamanho="medio"
      aoFechar={aoFechar}
      classe="chat-ia"
      rodape={
        <div className="chat-ia__acoes">
          <Botao estilo="fantasma" tamanho="pequeno" onClick={novaSugestao}>
            Nova Sugestão
          </Botao>
          <Botao estilo="fantasma" tamanho="pequeno" onClick={explicarLeis}>
            Explicar Leis
          </Botao>
          <Botao estilo="fantasma" tamanho="pequeno" onClick={aoFechar} className="chat-ia__fechar">
            Fechar
          </Botao>
        </div>
      }
    >
      <p className="chat-ia__titulo">Assistente de IA para Lógica Proposicional</p>
      {expressao && (
        <p className="chat-ia__expressao">
          Expressão: <span className="mono">{expressao}</span>
        </p>
      )}
      <div className="chat-ia__mensagens" role="log" aria-live="polite" aria-label="Conversa com a IA">
        {mensagens.map((m) => (
          <div
            key={m.id}
            className={`chat-ia__mensagem ${m.remetente === 'Você' ? 'chat-ia__mensagem--voce' : m.erro ? 'chat-ia__mensagem--erro' : 'chat-ia__mensagem--ia'}`}
          >
            <strong>{m.remetente}:</strong>
            <p className={m.carregando ? 'chat-ia__carregando' : undefined}>{m.texto}</p>
          </div>
        ))}
        <div ref={fim} />
      </div>
      <form
        className="chat-ia__entrada"
        onSubmit={(e) => {
          e.preventDefault();
          enviarMensagem();
        }}
      >
        <input
          className="campo"
          value={entrada}
          onChange={(e) => setEntrada(e.target.value)}
          placeholder="Digite sua pergunta sobre a simplificação..."
          aria-label="Sua pergunta"
          maxLength={1000}
        />
        <Botao tamanho="pequeno" type="submit">
          Enviar
        </Botao>
      </form>
    </Modal>
  );
}
