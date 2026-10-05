import { Fragment, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { api, mensagemDe } from '../api/cliente';
import type { ItemProblema, Problema } from '../api/tipos';
import { Botao } from '../componentes/Botao';
import { CabecalhoDaTela } from '../componentes/CabecalhoDaTela';
import { CampoDeExpressao, type ControleDoCampo } from '../componentes/CampoDeExpressao';
import { TecladoDeOperadores } from '../componentes/TecladoDeOperadores';
import { useAplicacao, type DestinoProblema } from '../estado/Aplicacao';

/** Cor do selo de dificuldade (IntegratedProblemsInterface.create_problem_buttons). */
const DIFICULDADES = ['Fácil', 'Médio', 'Difícil', 'Supremo'];
const classeDaDificuldade = (dificuldade: string) => `selo--${Math.max(0, DIFICULDADES.indexOf(dificuldade))}`;
const numero = (indice: number) => `P-${String(indice + 1).padStart(2, '0')}`;

/**
 * Os enunciados vêm com quebras de linha fixas, pensadas para a janela do desktop:
 * aqui só as linhas em branco separam parágrafos, e o texto se ajusta à largura.
 */
function paragrafos(texto: string): string {
  return texto
    .split(/\n\s*\n/)
    .map((paragrafo) => paragrafo.split('\n').map((linha) => linha.trim()).filter(Boolean).join(' '))
    .filter(Boolean)
    .join('\n\n');
}

/** As letras entre parênteses do enunciado, como "(V)", são as variáveis: viram etiquetas. */
function comVariaveis(texto: string): ReactNode {
  return paragrafos(texto).split(/(\([A-Z]\))/g).map((parte, i) =>
    /^\([A-Z]\)$/.test(parte) ? (
      <kbd key={i} className="variavel-do-enunciado" title={`Variável ${parte[1]}`}>
        {parte[1]}
      </kbd>
    ) : (
      <Fragment key={i}>{parte}</Fragment>
    ),
  );
}

/** Banco de problemas (FrontEnd/screens/problems/problems_screen.py). */
export function Problemas() {
  const app = useAplicacao();
  const [aberto, setAberto] = useState<number | null>(null);
  const [lista, setLista] = useState<ItemProblema[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [filtro, setFiltro] = useState<string | null>(null);

  useEffect(() => {
    api
      .problemas()
      .then(setLista)
      .catch((e: unknown) => setErro(mensagemDe(e)));
  }, []);

  const contagem = useMemo(() => {
    const porNivel = new Map<string, number>();
    for (const p of lista ?? []) porNivel.set(p.dificuldade, (porNivel.get(p.dificuldade) ?? 0) + 1);
    return porNivel;
  }, [lista]);

  if (aberto !== null) {
    return (
      <DetalheDoProblema
        key={aberto}
        indice={aberto}
        total={lista?.length ?? null}
        voltarLista={() => setAberto(null)}
        analisar={(resposta, destino) => {
          setAberto(null); // back_to_problems_list
          app.responderProblema(resposta, destino);
        }}
      />
    );
  }

  const visiveis = lista?.filter((p) => !filtro || p.dificuldade === filtro) ?? [];

  return (
    <main className="pagina pagina--formulario">
      <CabecalhoDaTela secao="2.3 · Problemas & Exercícios" titulo="Problemas do Mundo Real" aoVoltar={() => app.voltarPara('principal')} />

      <section className="painel" aria-labelledby="titulo-lista-problemas">
        <div className="problemas__topo">
          <div>
            <h2 id="titulo-lista-problemas" className="titulo-painel">
              <span className="rotulo-secao">1</span> Escolha um problema
            </h2>
            <p className="texto-secundario pequeno">
              Explore problemas reais que podem ser resolvidos com circuitos lógicos e lógica proposicional.
            </p>
          </div>
          {lista && (
            <div className="filtro-nivel" role="group" aria-label="Filtrar por nível">
              <button type="button" aria-pressed={filtro === null} onClick={() => setFiltro(null)}>
                Todos <span className="mono">{lista.length}</span>
              </button>
              {DIFICULDADES.filter((d) => contagem.has(d)).map((d) => (
                <button key={d} type="button" aria-pressed={filtro === d} onClick={() => setFiltro(d)}>
                  {d} <span className="mono">{contagem.get(d)}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {erro && (
          <p className="cor-erro" role="alert">
            {erro}
          </p>
        )}
        {!lista && !erro && <p className="texto-secundario carregando-texto">Carregando…</p>}
        <ul className="lista-problemas">
          {visiveis.map((p) => (
            <li key={p.indice}>
              <button type="button" className="cartao-problema" onClick={() => setAberto(p.indice)}>
                <span className="cartao-problema__numero mono">{numero(p.indice)}</span>
                <span className="cartao-problema__nome">{p.nome}</span>
                <span className={`selo ${classeDaDificuldade(p.dificuldade)}`}>{p.dificuldade}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

function DetalheDoProblema({
  indice,
  total,
  voltarLista,
  analisar,
}: {
  indice: number;
  total: number | null;
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
  const [rotuloVerResposta, setRotuloVerResposta] = useState('Ver Resposta');
  const [verificando, setVerificando] = useState(false);
  const campo = useRef<ControleDoCampo>(null);

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
      setRotuloVerResposta('Mostrar Resposta');
    } else {
      setRespostaVisivel(true);
      setRotuloVerResposta('Ocultar Resposta');
    }
  };

  const irPara = (destino: DestinoProblema) => {
    const texto = resposta.trim();
    if (texto) analisar(texto, destino);
  };

  const secao = `2.3 · Problema ${numero(indice)}${total ? ` de ${total}` : ''}`;

  if (!problema) {
    return (
      <main className="pagina pagina--formulario">
        <CabecalhoDaTela secao={secao} titulo="Carregando…" aoVoltar={voltarLista} />
        {erro ? (
          <p className="cor-erro" role="alert">
            {erro}
          </p>
        ) : (
          <p className="texto-secundario carregando-texto">Carregando…</p>
        )}
      </main>
    );
  }

  return (
    <main className="pagina pagina--formulario">
      <CabecalhoDaTela secao={secao} titulo={problema.nome} aoVoltar={voltarLista} />

      <article className="problema">
        <section className="painel problema__enunciado-painel" aria-labelledby="titulo-enunciado">
          <div className="problema__topo">
            <h2 id="titulo-enunciado" className="titulo-painel">
              <span className="rotulo-secao">1</span> Enunciado
            </h2>
            <span className={`selo selo--grande ${classeDaDificuldade(problema.dificuldade)}`}>Nível: {problema.dificuldade}</span>
          </div>
          <p className="problema__enunciado">{comVariaveis(problema.pergunta)}</p>
        </section>

        <section className="painel problema__resposta-painel" aria-labelledby="titulo-resposta">
          <h2 id="titulo-resposta" className="titulo-painel">
            <span className="rotulo-secao">2</span> Sua resposta
          </h2>
          <CampoDeExpressao
            ref={campo}
            id="resposta-problema"
            rotulo="Expressão que representa o sistema"
            valor={resposta}
            aoMudar={setResposta}
            aoConfirmar={() => void verificar()}
            placeholder="Ex.: A & B | C"
          />
          <TecladoDeOperadores aoInserir={(texto) => campo.current?.inserir(texto)} />
          <div className="problema__acoes">
            <Botao estilo="sucesso" onClick={() => void verificar()} disabled={verificando}>
              ✓&nbsp;&nbsp;Verificar Resposta
            </Botao>
            <Botao estilo="fantasma" onClick={alternarResposta} disabled={!verRespostaHabilitado}>
              {rotuloVerResposta}
            </Botao>
          </div>
          <p className={`problema__feedback ${feedback ? `problema__feedback--${feedback.cor}` : ''}`} role="status" aria-live="polite">
            {feedback?.texto}
          </p>

          {respostaVisivel && (
            <div className="problema__correta-caixa" aria-labelledby="titulo-correta">
              <p id="titulo-correta" className="rotulo-campo">
                Resposta correta
              </p>
              <p className="problema__correta mono">{problema.resposta}</p>
            </div>
          )}

          <div className="problema__analise">
            <p className="rotulo-campo">Depois de acertar, analise a sua resposta</p>
            <div className="problema__analise-botoes">
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
          </div>
        </section>
      </article>
    </main>
  );
}
