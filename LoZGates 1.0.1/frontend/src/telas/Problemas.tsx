import { useEffect, useState } from 'react';
import { api, mensagemDe } from '../api/cliente';
import type { ItemProblema, Problema } from '../api/tipos';
import { Botao } from '../componentes/Botao';
import { useAplicacao, type DestinoProblema } from '../estado/Aplicacao';

/** Cor do selo de dificuldade (IntegratedProblemsInterface.create_problem_buttons). */
const DIFICULDADES = ['Fácil', 'Médio', 'Difícil', 'Supremo'];
const classeDaDificuldade = (dificuldade: string) => `selo--${Math.max(0, DIFICULDADES.indexOf(dificuldade))}`;

/** Banco de problemas (FrontEnd/screens/problems/problems_screen.py). */
export function Problemas() {
  const app = useAplicacao();
  const [aberto, setAberto] = useState<number | null>(null);
  const [lista, setLista] = useState<ItemProblema[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    api
      .problemas()
      .then(setLista)
      .catch((e: unknown) => setErro(mensagemDe(e)));
  }, []);

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
    <main className="tela tela--media">
      <header className="problemas__cabecalho">
        <h1 className="problemas__titulo">🔬 Problemas do Mundo Real</h1>
        <p className="texto-secundario">Explore problemas reais que podem ser resolvidos com circuitos lógicos e lógica proposicional</p>
      </header>
      {erro && (
        <p className="cor-erro" role="alert">
          {erro}
        </p>
      )}
      {!lista && !erro && <p className="texto-secundario carregando-texto">Carregando…</p>}
      <ul className="lista-problemas">
        {lista?.map((p) => (
          <li key={p.indice}>
            <button type="button" className="cartao-problema" onClick={() => setAberto(p.indice)}>
              <span className="cartao-problema__nome">{p.nome}</span>
              <span className={`selo ${classeDaDificuldade(p.dificuldade)}`}>{p.dificuldade}</span>
            </button>
          </li>
        ))}
      </ul>
      <div className="pilha-botoes">
        <Botao estilo="voltar" onClick={() => app.voltarPara('principal')}>
          Voltar ao Menu Principal
        </Botao>
      </div>
    </main>
  );
}

function DetalheDoProblema({
  indice,
  voltarLista,
  analisar,
}: {
  indice: number;
  voltarLista: () => void;
  analisar: (resposta: string, destino: DestinoProblema) => void;
}) {
  const [problema, setProblema] = useState<Problema | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [resposta, setResposta] = useState('');
  const [feedback, setFeedback] = useState<{ texto: string; cor: 'aviso' | 'sucesso' | 'erro' } | null>(null);
  const [analiseHabilitada, setAnaliseHabilitada] = useState(false);
  const [verRespostaHabilitado, setVerRespostaHabilitado] = useState(false);
  const [respostaVisivel, setRespostaVisivel] = useState(false);
  const [rotuloVerResposta, setRotuloVerResposta] = useState('👁  Ver Resposta');
  const [verificando, setVerificando] = useState(false);

  useEffect(() => {
    api
      .problema(indice)
      .then(setProblema)
      .catch((e: unknown) => setErro(mensagemDe(e)));
  }, [indice]);

  const verificar = async () => {
    if (!resposta.trim()) {
      setFeedback({ texto: '⚠️ Por favor, digite uma resposta', cor: 'aviso' });
      return;
    }
    // Habilita "Ver Resposta" depois da PRIMEIRA tentativa
    setVerRespostaHabilitado(true);
    setVerificando(true);
    try {
      const correcao = await api.verificarProblema(indice, resposta);
      setFeedback({ texto: correcao.mensagem, cor: correcao.correta ? 'sucesso' : 'erro' });
      // A análise só fica disponível com a resposta correta
      setAnaliseHabilitada(correcao.correta);
    } catch (e) {
      setFeedback({ texto: `❌ Erro na validação: ${mensagemDe(e)}`, cor: 'erro' });
      setAnaliseHabilitada(false);
    } finally {
      setVerificando(false);
    }
  };

  const alternarResposta = () => {
    if (respostaVisivel) {
      setRespostaVisivel(false);
      setRotuloVerResposta('🔍 Mostrar Resposta');
    } else {
      setRespostaVisivel(true);
      setRotuloVerResposta('🙈 Ocultar Resposta');
    }
  };

  const irPara = (destino: DestinoProblema) => {
    const texto = resposta.trim();
    if (texto) analisar(texto, destino);
  };

  if (!problema) {
    return (
      <main className="tela tela--media">
        {erro ? (
          <p className="cor-erro" role="alert">
            {erro}
          </p>
        ) : (
          <p className="texto-secundario carregando-texto">Carregando…</p>
        )}
        <div className="pilha-botoes">
          <Botao estilo="voltar" onClick={voltarLista}>
            Voltar à Lista
          </Botao>
        </div>
      </main>
    );
  }

  return (
    <main className="tela tela--media">
      <article className="problema">
        <header className="problema__cabecalho">
          <h1 className="problema__titulo">📋 {problema.nome}</h1>
          <span className={`selo selo--grande ${classeDaDificuldade(problema.dificuldade)}`}>Nível: {problema.dificuldade}</span>
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
            onSubmit={(e) => {
              e.preventDefault();
              void verificar();
            }}
          >
            <input
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
          <Botao estilo="sucesso" onClick={() => void verificar()} disabled={verificando}>
            ✓&nbsp;&nbsp;Verificar Resposta
          </Botao>
          <Botao estilo="voltar" onClick={voltarLista}>
            Voltar à Lista
          </Botao>
          <Botao estilo="fantasma" onClick={alternarResposta} disabled={!verRespostaHabilitado}>
            {rotuloVerResposta}
          </Botao>
        </div>
        <div className="grade-acoes-problema">
          <Botao estilo="fantasma" onClick={() => irPara('circuit')} disabled={!analiseHabilitada}>
            ⚡&nbsp;&nbsp;Circuito
          </Botao>
          <Botao estilo="fantasma" onClick={() => irPara('simplifier')} disabled={!analiseHabilitada}>
            ↗&nbsp;&nbsp;Simplificar
          </Botao>
          <Botao estilo="fantasma" onClick={() => irPara('table')} disabled={!analiseHabilitada}>
            ⊤&nbsp;&nbsp;Tabela Verdade
          </Botao>
        </div>
      </article>
    </main>
  );
}
