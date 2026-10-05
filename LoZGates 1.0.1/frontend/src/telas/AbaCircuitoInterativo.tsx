import { useEffect, useMemo, useState } from 'react';
import { api, dadosFixos, mensagemDe } from '../api/cliente';
import type { DefinicoesComponentes, EditorInicial, ModoCircuito } from '../api/tipos';
import { Botao, escurecer } from '../componentes/Botao';
import { EditorInterativo } from '../circuito/editor/Editor';
import { useAplicacao } from '../estado/Aplicacao';
import { registrar } from '../telemetria/registro';

type Cor = 'destaque' | 'secundario' | 'sucesso' | 'aviso' | 'erro';

const TEXTO_CONTROLES =
  '🎮 CONTROLES BÁSICOS:\n\n' +
  '  • Espaço: Testar circuito\n' +
  '  • Clique: Selecionar componente\n' +
  '  • Arrastar: Mover componente\n' +
  '  • Bolinhas verdes: Pontos de conexão\n' +
  '  • Delete: Remover selecionado\n' +
  '  • WASD: Mover câmera\n' +
  '  • Scroll: Zoom\n' +
  '  • Ctrl+Z/Y: Desfazer/Refazer\n' +
  '  • Esc: Cancela conexão\n' +
  '  • R: Reset vista\n\n';

interface Desafio {
  modo: ModoCircuito;
  definicoes: DefinicoesComponentes;
  editor: EditorInicial;
  expressao: string;
  /** Muda a cada "Iniciar Desafio": o editor começa do zero */
  rodada: number;
}

/** CircuitModeSelector (FrontEnd/screens/circuit/circuit_mode_interface.py). */
export function AbaCircuitoInterativo() {
  const app = useAplicacao();
  const expressao = app.expressaoDoCircuito; // get_global_expression()
  const [modos, setModos] = useState<ModoCircuito[]>([]);
  const [erroModos, setErroModos] = useState<string | null>(null);
  const [modoAtual, setModoAtual] = useState<string | null>(null);
  const [desafio, setDesafio] = useState<Desafio | null>(null);
  const [iniciando, setIniciando] = useState(false);
  const [descricao, setDescricao] = useState('Escolha um modo para ver detalhes');
  const [status, setStatus] = useState<{ texto: string; cor: Cor }>({
    texto: "Escolha um modo e clique em 'Iniciar Desafio'",
    cor: 'secundario',
  });
  const [info, setInfo] = useState<string | null>(null);
  const ativo = desafio !== null;

  useEffect(() => {
    dadosFixos
      .modos()
      .then(setModos)
      .catch((e: unknown) => setErroModos(mensagemDe(e)));
  }, []);

  const infoModo = (chave: string) => modos.find((m) => m.chave === chave) ?? modos[0];
  // create_circuit_area(): o título é montado quando a tela é criada
  const tituloCircuito = useMemo(() => `🎯 Monte o Circuito ${expressao}`, []);

  const selecionarModo = (chave: string) => {
    // Só permite trocar de modo se o circuito não estiver ativo
    if (ativo && chave !== modoAtual) {
      setStatus({ texto: '⚠️ Pare o circuito antes de trocar de modo', cor: 'aviso' });
      return;
    }
    setModoAtual(chave);
    const modo = infoModo(chave);
    setDescricao(`🎯 ${modo.name} - ${modo.difficulty}\n📝 ${modo.description}`);
    if (expressao) {
      if (ativo) setStatus({ texto: `Status: Desafio ativo - ${modo.name} | Pressione ESPAÇO para testar`, cor: 'destaque' });
      else setStatus({ texto: `Modo selecionado: ${modo.name} | Pronto para iniciar!`, cor: 'sucesso' });
    } else {
      setStatus({ texto: '⚠️ Defina uma expressão na tela principal primeiro', cor: 'aviso' });
    }
  };

  const iniciar = async () => {
    if (!expressao) {
      setStatus({ texto: '❌ Erro: Defina uma expressão na tela principal primeiro', cor: 'erro' });
      return;
    }
    if (modoAtual === null) {
      setStatus({ texto: '⚠️ Selecione um modo de desafio primeiro', cor: 'aviso' });
      return;
    }
    const modo = infoModo(modoAtual);
    registrar('log_event', 'circuit_mode_selected', {
      mode: modoAtual,
      expression: expressao.slice(0, 30),
      restrictions: modo.restrictions,
    });
    setIniciando(true);
    try {
      const [definicoes, editor] = await Promise.all([dadosFixos.componentes(), api.editor(expressao)]);
      setDesafio({ modo, definicoes, editor, expressao, rodada: Date.now() });
      setStatus({ texto: `Status: Desafio ativo - ${modo.name} | Pressione ESPAÇO para testar`, cor: 'destaque' });
    } catch (erro) {
      setDesafio(null);
      setStatus({ texto: `❌ Erro ao iniciar: ${mensagemDe(erro)}`, cor: 'erro' });
    } finally {
      setIniciando(false);
    }
  };

  const parar = () => {
    setDesafio(null);
    setInfo(null);
    setStatus({ texto: '⏹️ Circuito parado - Selecione um modo para reiniciar', cor: 'aviso' });
  };

  const mostrarDicas = () => {
    if (modoAtual) registrar('log_event', 'circuit_tips_viewed', { mode: modoAtual, circuit_active: ativo });
    if (modoAtual === null) {
      setInfo('Primeiro selecione um modo de desafio para ver dicas específicas.');
      return;
    }
    const modo = infoModo(modoAtual);
    setInfo(`💡 DICAS - ${modo.name} (${modo.difficulty})\n\n` + modo.dicas.map((d, i) => `  ${i + 1}. ${d}\n\n`).join(''));
  };

  return (
    <div className="seletor-circuito">
      {/* Enquanto o desafio está ativo, os painéis de cima saem para o circuito ter espaço */}
      {!ativo && (
        <>
          <header className="seletor-circuito__cabecalho">
            <h2 className="titulo-secao">⚡&nbsp;&nbsp;Circuito Interativo</h2>
            {expressao ? (
              <p className="destaque mono">Expressão: {expressao}</p>
            ) : (
              <p className="cor-aviso">⚠️ Nenhuma expressão definida - Vá para a tela principal primeiro</p>
            )}
          </header>

          <section className="painel seletor-circuito__modos" aria-labelledby="titulo-modos">
            <h3 id="titulo-modos" className="painel__titulo">
              Selecione o Modo de Desafio:
            </h3>
            {erroModos && <p className="cor-erro">{erroModos}</p>}
            <div className="grade-modos">
              {modos.map((modo) => (
                <Botao
                  key={modo.chave}
                  estilo="cor"
                  cor={modo.color}
                  corHover={escurecer(modo.color)}
                  corTexto="#FFFFFF"
                  className={`botao-modo ${modoAtual === modo.chave ? 'botao-modo--atual' : ''}`}
                  aria-pressed={modoAtual === modo.chave}
                  onClick={() => selecionarModo(modo.chave)}
                >
                  <span>
                    {modo.icon} {modo.name}
                  </span>
                  <small>{modo.difficulty}</small>
                </Botao>
              ))}
            </div>
            <p className="seletor-circuito__descricao texto-secundario">{descricao}</p>
          </section>
        </>
      )}

      <section className="painel seletor-circuito__controles" aria-label="Controles do desafio">
        <div className="linha-botoes">
          <Botao estilo="sucesso" tamanho="pequeno" onClick={() => void iniciar()} disabled={ativo || iniciando}>
            🚀 Iniciar Desafio
          </Botao>
          <Botao estilo="erro" tamanho="pequeno" onClick={parar} disabled={!ativo}>
            ⏹️ Parar
          </Botao>
          <Botao tamanho="pequeno" onClick={mostrarDicas} disabled={!ativo}>
            i&nbsp;&nbsp;Dicas
          </Botao>
          <Botao estilo="aviso" tamanho="pequeno" onClick={() => setInfo(TEXTO_CONTROLES)} disabled={!ativo}>
            🎮 Controles
          </Botao>
        </div>
        <p className={`seletor-circuito__status cor-${status.cor}`} role="status" aria-live="polite">
          {status.texto}
        </p>
      </section>

      {info !== null && (
        <section className="painel seletor-circuito__info" aria-labelledby="titulo-info">
          <h3 id="titulo-info" className="painel__titulo">
            ℹ️ Informações
          </h3>
          <pre className="texto-pre">{info}</pre>
        </section>
      )}

      {desafio && (
        <section className="painel seletor-circuito__area" aria-labelledby="titulo-area">
          <h3 id="titulo-area" className="painel__titulo">
            {tituloCircuito}
          </h3>
          <EditorInterativo
            key={desafio.rodada}
            definicoes={desafio.definicoes}
            iniciais={desafio.editor.componentes}
            permitidas={desafio.modo.restrictions}
            expressao={desafio.expressao}
            modo={desafio.modo.chave}
          />
        </section>
      )}
    </div>
  );
}
