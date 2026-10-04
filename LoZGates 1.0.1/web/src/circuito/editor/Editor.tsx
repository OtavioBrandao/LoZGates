import { useCallback, useEffect, useMemo, useRef, useState, type PointerEvent as EventoPonteiro } from 'react';
import { api, mensagemDe } from '../../api/cliente';
import type { ComponenteInicial, DefinicoesComponentes, Ponto } from '../../api/tipos';
import { registrar } from '../../telemetria/registro';
import { CORES, FormaDaPorta } from '../formas';
import { EditorDeCircuito, type Componente } from './modelo';

/** Tempo das mensagens de acerto/erro (300 quadros do laço de ~60 quadros/s do desktop) */
const DURACAO_DA_MENSAGEM_MS = 5000;

/** Atalhos na tela: as mesmas teclas do teclado físico (úteis em tablets e celulares). */
const ATALHOS: { rotulo: string; tecla: string; ctrl?: boolean; dica: string }[] = [
  { rotulo: 'Testar', tecla: ' ', dica: 'Espaço' },
  { rotulo: 'Desfazer', tecla: 'z', ctrl: true, dica: 'Ctrl+Z' },
  { rotulo: 'Refazer', tecla: 'y', ctrl: true, dica: 'Ctrl+Y' },
  { rotulo: 'Remover', tecla: 'Delete', dica: 'Delete' },
  { rotulo: 'Cancelar', tecla: 'Escape', dica: 'Esc' },
  { rotulo: 'Resetar vista', tecla: 'r', dica: 'R' },
];

const TECLAS_DO_EDITOR = new Set([' ', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Delete', 'Backspace', 'Escape']);

const rgb = ([r, g, b]: [number, number, number]) => `rgb(${r},${g},${b})`;

interface Props {
  definicoes: DefinicoesComponentes;
  iniciais: ComponenteInicial[];
  /** Portas liberadas no modo (null = todas) */
  permitidas: string[] | null;
  /** Expressão (em álgebra booleana) que o circuito precisa implementar */
  expressao: string;
  modo: string;
}

type Mensagem = { tipo: 'sucesso' | 'erro'; chave: number } | null;

/** CircuitoInterativoManual: o editor de circuito em SVG. */
export function EditorInterativo({ definicoes, iniciais, permitidas, expressao, modo }: Props) {
  const editor = useMemo(
    () => new EditorDeCircuito(definicoes, iniciais, permitidas, registrar),
    // O editor nasce uma vez por desafio (o componente é recriado a cada "Iniciar Desafio")
    [],
  );
  const [, setQuadro] = useState(0);
  const redesenhar = useCallback(() => setQuadro((q) => q + 1), []);
  const area = useRef<HTMLDivElement>(null);
  const svg = useRef<SVGSVGElement>(null);
  const pressionado = useRef(false);
  const [mensagem, setMensagem] = useState<Mensagem>(null);
  const [testando, setTestando] = useState(false);
  const vistaAjustada = useRef(false);

  // Tamanho da área (o pygame ocupava o frame inteiro e acompanhava o redimensionamento)
  useEffect(() => {
    const elemento = area.current;
    if (!elemento) return;
    const medir = () => {
      editor.redimensionar(elemento.clientWidth, elemento.clientHeight);
      if (!vistaAjustada.current) {
        editor.ajustarVistaInicial();
        vistaAjustada.current = true;
      }
      redesenhar();
    };
    medir();
    const observador = new ResizeObserver(medir);
    observador.observe(elemento);
    return () => observador.disconnect();
  }, [editor, redesenhar]);

  // Movimento contínuo da câmera pelo teclado
  useEffect(() => {
    let quadro = 0;
    let anterior = performance.now();
    const laco = (agora: number) => {
      const segundos = Math.min(0.1, (agora - anterior) / 1000);
      anterior = agora;
      if (editor.avancar(segundos)) redesenhar();
      quadro = requestAnimationFrame(laco);
    };
    quadro = requestAnimationFrame(laco);
    return () => cancelAnimationFrame(quadro);
  }, [editor, redesenhar]);

  // A roda do mouse dá zoom e não rola a página (scroll_control_callback no desktop)
  useEffect(() => {
    const elemento = svg.current;
    if (!elemento) return;
    const aoRolar = (e: WheelEvent) => {
      e.preventDefault();
      editor.rolar(pontoNaTela(elemento, e.clientX, e.clientY), e.deltaY);
      redesenhar();
    };
    elemento.addEventListener('wheel', aoRolar, { passive: false });
    return () => elemento.removeEventListener('wheel', aoRolar);
  }, [editor, redesenhar]);

  useEffect(() => {
    if (!mensagem) return;
    const tempo = window.setTimeout(() => setMensagem(null), DURACAO_DA_MENSAGEM_MS);
    return () => window.clearTimeout(tempo);
  }, [mensagem]);

  /** test_circuit_manual: a correção (tabela-verdade) é feita no servidor. */
  const testar = useCallback(async () => {
    if (testando) return;
    setTestando(true);
    try {
      const resultado = await api.validarCircuito(expressao, modo, editor.netlist());
      registrar('log_circuit_test', resultado.correto);
      setMensagem({ tipo: resultado.correto ? 'sucesso' : 'erro', chave: Date.now() });
    } catch (erro) {
      registrar('log_error', 'interactive_circuit_exception', mensagemDe(erro), 'circuit_test');
      setMensagem({ tipo: 'erro', chave: Date.now() });
    } finally {
      setTestando(false);
    }
  }, [editor, expressao, modo, testando]);

  const teclar = useCallback(
    (pressionada: boolean, tecla: string, ctrl: boolean) => {
      if (editor.tecla(pressionada, tecla, ctrl) === 'testar') void testar();
      redesenhar();
    },
    [editor, redesenhar, testar],
  );

  const aoPressionar = (e: EventoPonteiro<SVGSVGElement>) => {
    if (e.button !== 0) return;
    e.currentTarget.focus({ preventScroll: true });
    e.currentTarget.setPointerCapture(e.pointerId);
    pressionado.current = true;
    editor.clicar(pontoNaTela(e.currentTarget, e.clientX, e.clientY));
    redesenhar();
  };

  const aoMover = (e: EventoPonteiro<SVGSVGElement>) => {
    const ponto = pontoNaTela(e.currentTarget, e.clientX, e.clientY);
    if (pressionado.current) editor.arrastar(ponto);
    else editor.moverCursor(ponto);
    redesenhar();
  };

  const aoSoltar = () => {
    if (!pressionado.current) return;
    pressionado.current = false;
    editor.soltar();
    redesenhar();
  };

  const atalho = (tecla: string, ctrl = false) => {
    svg.current?.focus({ preventScroll: true });
    teclar(true, tecla, ctrl);
    teclar(false, tecla, ctrl);
  };

  const { largura, altura, camera } = editor;
  const [mundoX1, mundoY1] = editor.telaParaMundo([0, 0]);
  const [mundoX2, mundoY2] = editor.telaParaMundo([largura, altura]);
  const paleta = editor.paleta();
  const conectando = editor.componente(editor.conectando);
  const inicioDaLinha = conectando ? editor.saida(conectando) : null;

  return (
    <div className="editor-circuito">
      <div ref={area} className="editor-circuito__area">
        <svg
          ref={svg}
          className="editor-circuito__svg"
          width={largura}
          height={altura}
          tabIndex={0}
          role="application"
          aria-label="Área do circuito interativo. Clique numa porta da paleta para posicioná-la; ligue as bolinhas verdes; Espaço testa o circuito."
          onPointerDown={aoPressionar}
          onPointerMove={aoMover}
          onPointerUp={aoSoltar}
          onPointerCancel={aoSoltar}
          onMouseEnter={(e) => e.currentTarget.focus({ preventScroll: true })}
          onKeyDown={(e) => {
            if (e.key === 'Tab') return;
            if (TECLAS_DO_EDITOR.has(e.key) || (e.ctrlKey && /^[zy]$/i.test(e.key))) e.preventDefault();
            teclar(true, e.key, e.ctrlKey || e.metaKey);
          }}
          onKeyUp={(e) => teclar(false, e.key, e.ctrlKey || e.metaKey)}
          onBlur={() => {
            editor.movimento.cima = editor.movimento.baixo = editor.movimento.esquerda = editor.movimento.direita = false;
          }}
          onContextMenu={(e) => e.preventDefault()}
        >
          <defs>
            <pattern id="grade-editor" width={50} height={50} patternUnits="userSpaceOnUse">
              <path d="M 50 0 L 0 0 0 50" fill="none" stroke={CORES.grade} strokeWidth={1} vectorEffect="non-scaling-stroke" />
            </pattern>
          </defs>
          <rect width={largura} height={altura} fill={CORES.fundo} />

          <g transform={`translate(${largura / 2} ${altura / 2}) scale(${camera.zoom}) translate(${-camera.x} ${-camera.y})`}>
            <rect x={mundoX1 - 100} y={mundoY1 - 100} width={mundoX2 - mundoX1 + 200} height={mundoY2 - mundoY1 + 200} fill="url(#grade-editor)" />
            {editor.fios.map((f, i) => {
              const origem = editor.componente(f.origem);
              const destino = editor.componente(f.destino);
              const inicio = origem && editor.saida(origem);
              const fim = destino && editor.entradas(destino)[f.entrada];
              if (!inicio || !fim) return null;
              const meio = inicio[0] + (fim[0] - inicio[0]) * 0.7;
              return (
                <polyline
                  key={i}
                  points={`${inicio[0]},${inicio[1]} ${meio},${inicio[1]} ${meio},${fim[1]} ${fim[0]},${fim[1]}`}
                  fill="none"
                  stroke={CORES.fio}
                  strokeWidth={3}
                />
              );
            })}
            {editor.componentes.map((c) => (
              <DesenhoDoComponente key={c.id} editor={editor} c={c} selecionado={c.id === editor.selecionado} />
            ))}
            {editor.fantasma && <DesenhoDoComponente editor={editor} c={editor.fantasma} selecionado={false} fantasma />}
          </g>

          {editor.fantasma && editor.fantasmaColide() && <XDeColisao editor={editor} c={editor.fantasma} />}

          {inicioDaLinha && (
            <line
              x1={editor.mundoParaTela(inicioDaLinha)[0]}
              y1={editor.mundoParaTela(inicioDaLinha)[1]}
              x2={editor.cursor[0]}
              y2={editor.cursor[1]}
              stroke={CORES.selecionado}
              strokeWidth={2}
            />
          )}

          {/* Painel de componentes (ComponentPalette) */}
          <g className="editor-circuito__paleta" fontFamily="sans-serif">
            <rect x={paleta.x} y={paleta.y} width={paleta.largura} height={paleta.altura} fill="rgb(40,40,40)" stroke="rgb(100,100,100)" strokeWidth={2} />
            <text x={paleta.x + paleta.largura / 2} y={paleta.y + 16} fill="#ffffff" fontSize={15} textAnchor="middle">
              componentes
            </text>
            {paleta.botoes.map((b) => (
              <g key={b.tipo} aria-label={`${b.nome}${b.permitido ? '' : ' (não permitida neste modo)'}`}>
                <rect
                  x={b.x}
                  y={b.y}
                  width={b.largura}
                  height={b.altura}
                  fill={b.permitido ? rgb(b.cor) : 'rgb(60,60,60)'}
                  stroke={b.permitido ? 'rgb(150,150,150)' : 'rgb(80,80,80)'}
                  strokeWidth={2}
                />
                <text
                  x={b.x + b.largura / 2}
                  y={b.y + b.altura / 2}
                  fill={b.permitido ? '#ffffff' : 'rgb(120,120,120)'}
                  fontSize={Math.min(15, b.altura * 0.6)}
                  textAnchor="middle"
                  dominantBaseline="central"
                >
                  {b.nome}
                </text>
              </g>
            ))}
          </g>
        </svg>

        {mensagem && <MensagemDoTeste key={mensagem.chave} tipo={mensagem.tipo} expressao={expressao} permitidas={permitidas} />}
      </div>

      <div className="atalhos" aria-label="Atalhos do teclado">
        {ATALHOS.map((a) => (
          <button key={a.rotulo} type="button" className="atalho" onClick={() => atalho(a.tecla, a.ctrl)} title={a.dica}>
            {a.rotulo} <kbd>{a.dica}</kbd>
          </button>
        ))}
      </div>
    </div>
  );
}

function pontoNaTela(elemento: Element, clienteX: number, clienteY: number): Ponto {
  const caixa = elemento.getBoundingClientRect();
  return [clienteX - caixa.left, clienteY - caixa.top];
}

/** CircuitDrawer.draw_component */
function DesenhoDoComponente({
  editor,
  c,
  selecionado,
  fantasma = false,
}: {
  editor: EditorDeCircuito;
  c: Componente;
  selecionado: boolean;
  fantasma?: boolean;
}) {
  const { largura, altura } = editor.dimensoes(c.tipo);
  const saida = editor.saida(c);
  return (
    <g opacity={fantasma ? 0.65 : 1} fontFamily="sans-serif">
      {c.tipo === 'variable' && (
        <>
          <rect x={c.x} y={c.y} width={largura} height={altura} fill="none" stroke={selecionado ? CORES.selecionado : CORES.branco} strokeWidth={2} />
          <text x={c.x + largura / 2} y={c.y + altura / 2} fill={CORES.rotulo} fontSize={14} textAnchor="middle" dominantBaseline="central">
            {c.nome}
          </text>
        </>
      )}
      {c.tipo === 'output' && (
        <>
          <rect x={c.x} y={c.y} width={largura} height={altura} fill="none" stroke={selecionado ? CORES.selecionado : CORES.saida} strokeWidth={2} />
          <text x={c.x + largura / 2} y={c.y + altura / 2} fill={CORES.rotulo} fontSize={11} textAnchor="middle" dominantBaseline="central">
            SAÍDA
          </text>
        </>
      )}
      {c.tipo !== 'variable' && c.tipo !== 'output' && (
        <>
          {selecionado && (
            <rect
              x={c.x - 6}
              y={c.y - 6}
              width={largura + 12}
              height={altura + 12}
              fill="none"
              stroke={CORES.selecionado}
              strokeWidth={1.5}
              strokeDasharray="6 4"
            />
          )}
          <FormaDaPorta tipo={c.tipo} x={c.x} y={c.y} />
        </>
      )}
      {editor.entradas(c).map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={4} fill={editor.entradaLigada(c.id, i) ? CORES.pinoLigado : CORES.pino} />
      ))}
      {saida && <circle cx={saida[0]} cy={saida[1]} r={4} fill={editor.saidaLigada(c.id) ? CORES.pinoLigado : CORES.pino} />}
    </g>
  );
}

/** draw_collision_warning: X vermelho no centro do componente que está sendo posicionado. */
function XDeColisao({ editor, c }: { editor: EditorDeCircuito; c: Componente }) {
  const { largura, altura } = editor.dimensoes(c.tipo);
  const [x, y] = editor.mundoParaTela([c.x + Math.floor(largura / 2), c.y + Math.floor(altura / 2)]);
  const t = 15;
  return (
    <g stroke="rgb(255,0,0)" strokeWidth={3}>
      <line x1={x - t} y1={y - t} x2={x + t} y2={y + t} />
      <line x1={x + t} y1={y - t} x2={x - t} y2={y + t} />
    </g>
  );
}

/** draw_success_message / draw_error_message (o clique continua indo para o circuito). */
function MensagemDoTeste({ tipo, expressao, permitidas }: { tipo: 'sucesso' | 'erro'; expressao: string; permitidas: string[] | null }) {
  if (tipo === 'sucesso') {
    return (
      <div className="mensagem-teste mensagem-teste--sucesso" role="status" aria-live="assertive">
        <p className="mensagem-teste__titulo">🎉 PARABÉNS! 🎉</p>
        <p className="mensagem-teste__subtitulo">Circuito montado corretamente!</p>
        {permitidas && <p>Usando apenas: {permitidas.join(', ').toUpperCase()}</p>}
        <p>Expressão: {expressao}</p>
      </div>
    );
  }
  return (
    <div className="mensagem-teste mensagem-teste--erro" role="status" aria-live="assertive">
      <p className="mensagem-teste__titulo">❌ CIRCUITO INCORRETO ❌</p>
      <p className="mensagem-teste__subtitulo">Tente novamente!</p>
      <p className="mensagem-teste__secao">Possíveis problemas:</p>
      <ul>
        <li>• Verifique todas as conexões</li>
        <li>• Confira se implementou a expressão correta</li>
        <li>• Todas as variáveis devem estar conectadas</li>
        <li>• O circuito deve ter pelo menos uma porta lógica</li>
      </ul>
    </div>
  );
}
