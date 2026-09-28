import { useMemo, useRef, useState } from 'react';
import { Botao } from '../componentes/Botao';
import { TopoTela } from '../componentes/TopoTela';
import { useAplicacao } from '../estado/Aplicacao';
import { chamar, type RespostaApi } from '../motor/pyodide';

interface ItemProblema {
  indice: number;
  nome: string;
  dificuldade: string;
}

interface DetalheProblema extends RespostaApi {
  nome: string;
  dificuldade: string;
  pergunta: string;
  resposta: string;
}

/** Cores por dificuldade (IntegratedProblemsInterface.create_problem_buttons) */
const CORES_DIFICULDADE: Record<string, [string, string]> = {
  Fácil: ['#45A049', '#09BB62'],
  Médio: ['#D17710', '#F38D08'],
  Difícil: ['#961730', '#D32F2F'],
  Supremo: ['#72076E', '#B019AB'],
};
const corDe = (dificuldade: string) => CORES_DIFICULDADE[dificuldade] ?? CORES_DIFICULDADE['Fácil'];

/** frame_problemas_reais — IntegratedProblemsInterface (FrontEnd/problems_interface.py) */
export function Problemas() {
  const app = useAplicacao();
  const [aberto, setAberto] = useState<number | null>(null);
  const lista = useMemo(() => chamar<RespostaApi & { problemas: ItemProblema[] }>('problemas_lista').problemas ?? [], []);

  if (aberto !== null) {
    return (
      <DetalheDoProblema
        key={aberto}
        indice={aberto}
        voltarLista={() => setAberto(null)}
        analisar={(resposta, destino) => {
          setAberto(null); // back_to_problems_list
          app.responderProblema(resposta, destino);
        }}
      />
    );
  }

  return (
    <main className="tela tela--larga">
      <TopoTela voltar={{ rotulo: 'Voltar ao Menu Principal', acao: () => app.voltarPara('principal') }} />
      <header className="problemas__cabecalho">
        <h1 className="problemas__titulo">🔬 Problemas do Mundo Real</h1>
        <p className="texto-secundario">Explore problemas reais que podem ser resolvidos com circuitos lógicos e lógica proposicional</p>
      </header>
      <ul className="grade-problemas">
        {lista.map((p) => {
          const [cor, hover] = corDe(p.dificuldade);
          return (
            <li key={p.indice}>
              <Botao estilo="cor" cor={cor} corHover={hover} corTexto="#FFFFFF" className="botao-problema" onClick={() => setAberto(p.indice)}>
                <span>{p.nome}</span>
                <small>({p.dificuldade})</small>
              </Botao>
            </li>
          );
        })}
      </ul>
    </main>
  );
}

type Destino = 'circuit' | 'simplifier' | 'table';

function DetalheDoProblema({
  indice,
  voltarLista,
  analisar,
}: {
  indice: number;
  voltarLista: () => void;
  analisar: (resposta: string, destino: Destino) => void;
}) {
  const problema = useMemo(() => chamar<DetalheProblema>('problema_detalhe', indice), [indice]);
  const [resposta, setResposta] = useState('');
  const [feedback, setFeedback] = useState<{ texto: string; cor: 'aviso' | 'sucesso' | 'erro' } | null>(null);
  const [analiseHabilitada, setAnaliseHabilitada] = useState(false);
  const [mostrarRespostaHabilitado, setMostrarRespostaHabilitado] = useState(false);
  const [respostaVisivel, setRespostaVisivel] = useState(false);
  const [rotuloMostrar, setRotuloMostrar] = useState('👁️ Mostrar Resposta');
  const campo = useRef<HTMLInputElement>(null);
  const [corFundo] = corDe(problema.dificuldade);

  const verificar = () => {
    const r = chamar<RespostaApi & { vazio?: boolean; correta?: boolean; mensagem?: string }>('problema_verificar', indice, resposta);
    if (!r.ok) return;
    if (r.vazio) {
      setFeedback({ texto: '⚠️ Por favor, digite uma resposta', cor: 'aviso' });
      return;
    }
    // Habilita "Mostrar Resposta" após a PRIMEIRA tentativa
    setMostrarRespostaHabilitado(true);
    setFeedback({ texto: r.mensagem ?? '', cor: r.correta ? 'sucesso' : 'erro' });
    // Análise só fica disponível com a resposta correta
    setAnaliseHabilitada(Boolean(r.correta));
  };

  const alternarResposta = () => {
    if (respostaVisivel) {
      setRespostaVisivel(false);
      setRotuloMostrar('🔍 Mostrar Resposta');
    } else {
      setRespostaVisivel(true);
      setRotuloMostrar('🙈 Ocultar Resposta');
    }
  };

  const irPara = (destino: Destino) => {
    const texto = resposta.trim();
    if (texto) analisar(texto, destino);
  };

  return (
    <main className="tela tela--media">
      <TopoTela voltar={{ rotulo: '📋 Voltar à Lista', acao: voltarLista }} />
      <article className="problema">
        <header className="problema__cabecalho">
          <h1 className="problema__titulo">📋 {problema.nome}</h1>
          <span className="pilula" style={{ background: corFundo }}>
            Nível: {problema.dificuldade}
          </span>
        </header>

        <section className="painel" aria-labelledby="titulo-enunciado">
          <h2 id="titulo-enunciado" className="painel__titulo painel__titulo--ciano">
            📖 Problema:
          </h2>
          <p className="problema__enunciado">{problema.pergunta}</p>
        </section>

        <section className="painel painel--escuro" aria-labelledby="titulo-resposta">
          <h2 id="titulo-resposta" className="painel__titulo painel__titulo--ciano">
            ✍️ Sua Resposta:
          </h2>
          <form
            className="problema__formulario"
            onSubmit={(e) => {
              e.preventDefault();
              verificar();
            }}
          >
            <input
              ref={campo}
              className="campo campo--expressao"
              placeholder="Digite sua expressão lógica aqui (ex: A & B | C)"
              aria-label="Sua resposta"
              value={resposta}
              spellCheck={false}
              autoComplete="off"
              onChange={(e) => setResposta(e.target.value)}
            />
          </form>
          <p className={`problema__feedback ${feedback ? `cor-${feedback.cor}` : ''}`} role="status" aria-live="polite">
            {feedback?.texto}
          </p>
        </section>

        {respostaVisivel && (
          <section className="painel painel--escuro" aria-labelledby="titulo-correta">
            <h2 id="titulo-correta" className="painel__titulo cor-sucesso">
              💡 Resposta Correta:
            </h2>
            <p className="problema__correta mono">{problema.resposta}</p>
          </section>
        )}

        <div className="grade-acoes-problema">
          <Botao onClick={verificar}>🔍 Verificar Resposta</Botao>
          <Botao onClick={() => irPara('circuit')} disabled={!analiseHabilitada}>
            🔌 Analisar no Circuito
          </Botao>
          <Botao onClick={() => irPara('simplifier')} disabled={!analiseHabilitada}>
            🔎 Simplificar
          </Botao>
          <Botao onClick={() => irPara('table')} disabled={!analiseHabilitada}>
            📊 Tabela Verdade
          </Botao>
          <Botao onClick={alternarResposta} disabled={!mostrarRespostaHabilitado}>
            {rotuloMostrar}
          </Botao>
        </div>
      </article>
    </main>
  );
}
