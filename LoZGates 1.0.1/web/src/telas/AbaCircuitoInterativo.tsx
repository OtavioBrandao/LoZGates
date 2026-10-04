import { useEffect, useMemo, useRef, useState } from 'react';
import { Botao, escurecer } from '../componentes/Botao';
import { useAplicacao } from '../estado/Aplicacao';
import { anexarCanvas, enviarTecla } from '../motor/circuito';
import { chamar } from '../motor/pyodide';
import { textos, type ModoCircuito } from '../motor/textos';

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

/** Atalhos na tela: mandam exatamente as mesmas teclas do teclado físico (útil em tablets). */
const ATALHOS: { rotulo: string; tecla: string; ctrl?: boolean; dica: string }[] = [
  { rotulo: 'Testar', tecla: ' ', dica: 'Espaço' },
  { rotulo: 'Desfazer', tecla: 'z', ctrl: true, dica: 'Ctrl+Z' },
  { rotulo: 'Refazer', tecla: 'y', ctrl: true, dica: 'Ctrl+Y' },
  { rotulo: 'Remover', tecla: 'Delete', dica: 'Delete' },
  { rotulo: 'Cancelar', tecla: 'Escape', dica: 'Esc' },
  { rotulo: 'Resetar vista', tecla: 'r', dica: 'R' },
];

/** CircuitModeSelector (FrontEnd/circuit_mode_interface.py) */
export function AbaCircuitoInterativo() {
  const app = useAplicacao();
  const expressao = app.expressaoGlobal; // get_global_expression()
  const { modos, dicas_modos } = textos();
  const infoModo = (chave: string) => modos.find((m) => m.chave === chave) ?? modos[0];

  const [modoAtual, setModoAtual] = useState<string | null>(null);
  const [ativo, setAtivo] = useState(false);
  const [descricao, setDescricao] = useState('Escolha um modo para ver detalhes');
  const [status, setStatus] = useState<{ texto: string; cor: Cor }>({
    texto: "Escolha um modo e clique em 'Iniciar Desafio'",
    cor: 'secundario',
  });
  const [info, setInfo] = useState<string | null>(null);
  const [mensagemPygame, setMensagemPygame] = useState<{ texto: string; cor: string } | null>(null);
  const area = useRef<HTMLDivElement>(null);
  const soltarCanvas = useRef<(() => void) | null>(null);

  // create_circuit_area(): o título é montado quando a tela é criada
  const tituloCircuito = useMemo(() => `🎯 Monte o Circuito ${expressao}`, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(
    () => () => {
      soltarCanvas.current?.();
    },
    [],
  );

  const selecionarModo = (chave: string) => {
    // Só permite trocar de modo se o circuito não estiver ativo
    if (ativo && chave !== modoAtual) {
      setStatus({ texto: '⚠️ Pare o circuito antes de trocar de modo', cor: 'aviso' });
      return;
    }
    setModoAtual(chave);
    chamar('circuito_selecionar_modo', chave);
    const modo = infoModo(chave);
    setDescricao(`🎯 ${modo.name} - ${modo.difficulty}\n📝 ${modo.description}\n`);
    if (expressao) {
      if (ativo) {
        setStatus({ texto: `Status: Desafio ativo - ${modo.name} | Pressione ESPAÇO para testar`, cor: 'destaque' });
      } else {
        setStatus({ texto: `Modo selecionado: ${modo.name} | Pronto para iniciar!`, cor: 'sucesso' });
      }
    } else {
      setStatus({ texto: '⚠️ Defina uma expressão na tela principal primeiro', cor: 'aviso' });
    }
  };

  const iniciar = () => {
    if (!expressao) {
      setStatus({ texto: '❌ Erro: Defina uma expressão na tela principal primeiro', cor: 'erro' });
      return;
    }
    if (modoAtual === null) {
      setStatus({ texto: '⚠️ Selecione um modo de desafio primeiro', cor: 'aviso' });
      return;
    }
    setMensagemPygame(null);
    if (area.current && !soltarCanvas.current) {
      soltarCanvas.current = anexarCanvas(area.current, (texto, cor) => setMensagemPygame({ texto, cor }));
    }
    const r = chamar('circuito_iniciar', expressao, modoAtual);
    if (!r.ok) {
      setAtivo(false);
      setStatus({ texto: `❌ Erro ao iniciar: ${String(r.mensagem ?? r.excecao ?? '')}`, cor: 'erro' });
      console.log(`❌ Erro: ${r.excecao}`);
      return;
    }
    setAtivo(true);
    const modo = infoModo(modoAtual);
    setStatus({ texto: `Status: Desafio ativo - ${modo.name} | Pressione ESPAÇO para testar`, cor: 'destaque' });
    console.log(`✅ Circuito iniciado - Expressão: ${expressao} | Modo: ${modo.name}`);
  };

  const parar = () => {
    chamar('circuito_parar');
    setInfo(null);
    setAtivo(false);
    setStatus({ texto: '⏹️ Circuito parado - Selecione um modo para reiniciar', cor: 'aviso' });
  };

  const mostrarDicas = () => {
    if (modoAtual) {
      chamar('registrar_evento', 'circuit_tips_viewed', JSON.stringify({ mode: modoAtual, circuit_active: ativo }));
    }
    if (modoAtual === null) {
      setInfo('Primeiro selecione um modo de desafio para ver dicas específicas.');
      return;
    }
    const modo = infoModo(modoAtual);
    const dicas = dicas_modos[modoAtual] ?? dicas_modos.livre;
    setInfo(`💡 DICAS - ${modo.name} (${modo.difficulty})\n\n` + dicas.map((d, i) => `  ${i + 1}. ${d}\n\n`).join(''));
  };

  return (
    <div className="seletor-circuito">
      <header className="seletor-circuito__cabecalho">
        <h2 className="titulo-secao">🔌 Circuito Interativo - Escolha o Desafio</h2>
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
        <div className="grade-modos">
          {modos.map((modo: ModoCircuito) => (
            <Botao
              key={modo.chave}
              estilo="cor"
              cor={modo.color}
              corHover={escurecer(modo.color)}
              corTexto="#FFFFFF"
              className={`botao-modo ${modoAtual === modo.chave ? 'botao-modo--atual' : ''}`}
              aria-pressed={modoAtual === modo.chave}
              disabled={ativo && modo.chave !== modoAtual}
              onClick={() => selecionarModo(modo.chave)}
            >
              <span>
                {modo.icon} {modo.name}
              </span>
              <small>{modo.difficulty}</small>
            </Botao>
          ))}
        </div>
        <p className="seletor-circuito__descricao texto-secundario">{descricao.trim()}</p>
      </section>

      <section className="painel seletor-circuito__controles" aria-label="Controles do desafio">
        <div className="linha-botoes">
          <Botao estilo="sucesso" tamanho="pequeno" onClick={iniciar} disabled={ativo}>
            🚀 Iniciar Desafio
          </Botao>
          <Botao estilo="erro" tamanho="pequeno" onClick={parar} disabled={!ativo}>
            ⏹️ Parar
          </Botao>
          <Botao estilo="cor" tamanho="pequeno" cor="#070BDB" corHover="#0A0D97" corTexto="#FFFFFF" onClick={mostrarDicas} disabled={!ativo}>
            💡 Dicas
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

      <section className="painel seletor-circuito__area" hidden={!ativo} aria-labelledby="titulo-area">
        <h3 id="titulo-area" className="painel__titulo">
          {tituloCircuito}
        </h3>
        <div ref={area} className="area-pygame" />
        {mensagemPygame && (
          <p className="area-pygame__mensagem" style={{ color: mensagemPygame.cor || undefined }}>
            {mensagemPygame.texto}
          </p>
        )}
        <div className="atalhos" aria-label="Atalhos do teclado">
          {ATALHOS.map((a) => (
            <button key={a.rotulo} type="button" className="atalho" onClick={() => enviarTecla(a.tecla, { ctrl: a.ctrl })} title={a.dica}>
              {a.rotulo} <kbd>{a.dica}</kbd>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}
