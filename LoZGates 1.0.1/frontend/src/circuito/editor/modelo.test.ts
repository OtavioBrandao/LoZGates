import { describe, expect, it } from 'vitest';
import type { ComponenteInicial, DefinicoesComponentes, Ponto } from '../../api/tipos';
import { EditorDeCircuito, type Componente } from './modelo';
import cenarios from './paridade-editor.json';

/** Geometria do servidor (circuito_logico/logic/componentes.definicoes), gravada junto com os cenários */
const definicoes = cenarios.definicoes as unknown as DefinicoesComponentes;

interface Posicao {
  tipo: string;
  x: number;
  y: number;
}

function editorCom(layout: Posicao[], permitidas: string[] | null = null, registrar = () => {}) {
  const iniciais: ComponenteInicial[] = layout.map((c, i) => ({ id: `c${i}`, tipo: c.tipo, nome: 'A', x: c.x, y: c.y }));
  const editor = new EditorDeCircuito(definicoes, iniciais, permitidas, registrar);
  editor.redimensionar(800, 600);
  editor.camera = { x: 0, y: 0, zoom: 1 };
  return editor;
}

describe('paridade com o editor pygame do interface_update', () => {
  it('detecta colisão e acha posição livre como find_valid_position', () => {
    for (const c of cenarios.posicao) {
      const editor = editorCom(c.layout);
      const novo: Componente = { id: 'novo', tipo: c.tipo, nome: '', x: c.x, y: c.y };
      const contexto = JSON.stringify({ tipo: c.tipo, x: c.x, y: c.y });
      expect(editor.colide(novo, c.x, c.y), contexto).toBe(c.colide);
      const [x, y] = editor.posicaoValida(novo, c.x, c.y);
      expect(x, contexto).toBeCloseTo(c.valida[0], 9);
      expect(y, contexto).toBeCloseTo(c.valida[1], 9);
    }
  });

  it('acha o componente e o pino clicados como handle_mouse_click', () => {
    for (const c of cenarios.clique) {
      const editor = editorCom(c.layout);
      const { componente, pino } = editor.alvoEm(c.ponto as Ponto);
      const indice = componente ? editor.componentes.indexOf(componente) : null;
      const contexto = JSON.stringify({ ponto: c.ponto });
      expect(indice, contexto).toBe(c.componente);
      expect(pino ? [pino.tipo, pino.indice] : null, contexto).toEqual(c.pino);
    }
  });

  it('arrasta como handle_mouse_drag (inclusive quando não pode sair do lugar)', () => {
    for (const c of cenarios.arrasto) {
      const editor = editorCom(c.layout);
      editor.selecionado = `c${c.selecionado}`;
      editor.arrastar(c.tela as Ponto);
      const final = editor.componentes[c.selecionado];
      const contexto = JSON.stringify({ selecionado: c.selecionado, tela: c.tela });
      expect(final.x, contexto).toBeCloseTo(c.final[0], 9);
      expect(final.y, contexto).toBeCloseTo(c.final[1], 9);
    }
  });

  it('monta a paleta com as medidas de ComponentPalette', () => {
    for (const c of cenarios.paleta) {
      const editor = editorCom([]);
      editor.redimensionar(c.largura, c.altura);
      const paleta = editor.paleta();
      expect([paleta.x, paleta.y, paleta.largura, paleta.altura]).toEqual(c.paleta);
      expect(paleta.botoes.map((b) => [b.x, b.y, b.largura, b.altura])).toEqual(c.botoes);
    }
  });
});

describe('interação do editor', () => {
  const variaveis: ComponenteInicial[] = [
    { id: 'var-A', tipo: 'variable', nome: 'A', x: -300, y: -100 },
    { id: 'var-B', tipo: 'variable', nome: 'B', x: -300, y: 0 },
    { id: 'saida', tipo: 'output', nome: 'SAÍDA', x: 300, y: 0 },
  ];

  function novoEditor(permitidas: string[] | null = null) {
    const registros: unknown[][] = [];
    const editor = new EditorDeCircuito(definicoes, variaveis, permitidas, (...args: unknown[]) => {
      registros.push(args);
    });
    editor.redimensionar(800, 600);
    editor.camera = { x: 0, y: 0, zoom: 1 };
    return { editor, registros };
  }

  const tela = (editor: EditorDeCircuito, ponto: Ponto) => editor.mundoParaTela(ponto);
  const centroDoBotao = (editor: EditorDeCircuito, tipo: string): Ponto => {
    const botao = editor.paleta().botoes.find((b) => b.tipo === tipo)!;
    return [botao.x + botao.largura / 2, botao.y + botao.altura / 2];
  };

  function colocar(editor: EditorDeCircuito, tipo: string, mundo: Ponto) {
    editor.clicar(centroDoBotao(editor, tipo));
    expect(editor.fantasma?.tipo).toBe(tipo);
    editor.moverCursor(tela(editor, mundo));
    editor.clicar(tela(editor, mundo));
    return editor.componentes[editor.componentes.length - 1];
  }

  it('posiciona uma porta pela paleta e registra a inclusão', () => {
    const { editor, registros } = novoEditor();
    const porta = colocar(editor, 'and', [0, 0]);
    expect(porta).toMatchObject({ tipo: 'and', x: -40, y: -30 });
    expect(editor.fantasma).toBeNull();
    expect(registros).toEqual([['log_component_action', 'add', 'and']]);
  });

  it('não deixa escolher porta fora do modo', () => {
    const { editor } = novoEditor(['nand']);
    editor.clicar(centroDoBotao(editor, 'and'));
    expect(editor.fantasma).toBeNull();
    editor.clicar(centroDoBotao(editor, 'nand'));
    expect(editor.fantasma?.tipo).toBe('nand');
  });

  it('Esc cancela a colocação e depois a conexão', () => {
    const { editor } = novoEditor();
    editor.clicar(centroDoBotao(editor, 'or'));
    editor.tecla(true, 'Escape', false);
    expect(editor.fantasma).toBeNull();
    editor.clicar(tela(editor, editor.saida(editor.componentes[0])!));
    expect(editor.conectando).toBe('var-A');
    editor.tecla(true, 'Escape', false);
    expect(editor.conectando).toBeNull();
  });

  it('liga saída em entrada, recusa entrada ocupada e o próprio componente', () => {
    const { editor, registros } = novoEditor();
    const porta = colocar(editor, 'and', [0, 0]);
    const [a, b] = editor.componentes;
    const ligar = (origem: Componente, destino: Componente, entrada: number) => {
      editor.clicar(tela(editor, editor.saida(origem)!));
      editor.clicar(tela(editor, editor.entradas(destino)[entrada]));
    };
    ligar(a, porta, 0);
    ligar(b, porta, 1);
    ligar(b, porta, 0); // entrada já ocupada
    ligar(porta, porta, 0); // o próprio componente
    ligar(porta, editor.componentes[2], 0);
    expect(editor.fios).toEqual([
      { origem: 'var-A', destino: porta.id, entrada: 0 },
      { origem: 'var-B', destino: porta.id, entrada: 1 },
      { origem: porta.id, destino: 'saida', entrada: 0 },
    ]);
    expect(registros.filter((r) => r[1] === 'connect')).toHaveLength(3);
    expect(editor.netlist()).toEqual({
      componentes: [
        { id: 'var-A', tipo: 'variable', nome: 'A' },
        { id: 'var-B', tipo: 'variable', nome: 'B' },
        { id: 'saida', tipo: 'output', nome: 'SAÍDA' },
        { id: porta.id, tipo: 'and', nome: 'AND' },
      ],
      fios: editor.fios,
    });
  });

  it('Delete remove a porta e seus fios; variáveis e saída só perdem os fios', () => {
    const { editor, registros } = novoEditor();
    const porta = colocar(editor, 'not', [0, 0]);
    editor.clicar(tela(editor, editor.saida(editor.componentes[0])!));
    editor.clicar(tela(editor, editor.entradas(porta)[0]));
    editor.clicar(tela(editor, [porta.x + 20, porta.y + 5])); // seleciona pelo corpo
    expect(editor.selecionado).toBe(porta.id);
    editor.tecla(true, 'Delete', false);
    expect(editor.componentes.map((c) => c.id)).toEqual(['var-A', 'var-B', 'saida']);
    expect(editor.fios).toEqual([]);
    editor.clicar(tela(editor, [-260, -95])); // seleciona a variável A
    editor.tecla(true, 'Delete', false);
    expect(editor.componentes).toHaveLength(3);
    expect(registros.filter((r) => r[1] === 'delete').map((r) => r[2])).toEqual(['not', 'variable']);
  });

  it('desfazer e refazer restauram o circuito inteiro (inclusive porta incluída ou removida)', () => {
    const { editor, registros } = novoEditor();
    const porta = colocar(editor, 'xor', [0, 0]);
    expect(editor.tecla(true, 'z', true)).toBeNull();
    expect(editor.componentes.map((c) => c.id)).toEqual(['var-A', 'var-B', 'saida']);
    editor.tecla(true, 'y', true);
    expect(editor.componentes.map((c) => c.id)).toContain(porta.id);
    editor.selecionado = porta.id;
    editor.remover();
    editor.desfazer();
    expect(editor.componentes.map((c) => c.id)).toContain(porta.id);
    expect(registros.filter((r) => r[1] === 'undo')).toHaveLength(2);
    // Sem nada para desfazer, não registra
    while (editor.podeDesfazer()) editor.desfazer();
    const antes = registros.length;
    expect(editor.desfazer()).toBe(false);
    expect(registros).toHaveLength(antes);
  });

  it('ESPAÇO pede o teste do circuito', () => {
    const { editor } = novoEditor();
    expect(editor.tecla(true, ' ', false)).toBe('testar');
    expect(editor.tecla(true, 'q', false)).toBeNull();
  });

  it('WASD move a câmera e R volta à vista inicial', () => {
    const { editor } = novoEditor();
    editor.ajustarVistaInicial();
    const inicio = editor.camera.x;
    editor.tecla(true, 'd', false);
    expect(editor.avancar(1)).toBe(true);
    // 5 pixels de tela por quadro, a 60 quadros/s
    expect(editor.camera.x - inicio).toBeCloseTo(300 / editor.camera.zoom);
    editor.tecla(false, 'd', false);
    expect(editor.avancar(1)).toBe(false);
    editor.tecla(true, 'r', false);
    expect(editor.camera).toEqual(editor.vistaInicial);
  });

  it('o zoom mantém parado o ponto sob o cursor', () => {
    const { editor } = novoEditor();
    const cursor: Ponto = [123, 456];
    const antes = editor.telaParaMundo(cursor);
    editor.rolar(cursor, -100);
    expect(editor.camera.zoom).toBeCloseTo(1.1);
    const depois = editor.telaParaMundo(cursor);
    expect(depois[0]).toBeCloseTo(antes[0]);
    expect(depois[1]).toBeCloseTo(antes[1]);
    const ida = editor.mundoParaTela([10, -20]);
    expect(editor.telaParaMundo(ida)[0]).toBeCloseTo(10);
  });

  it('em tela estreita afasta o zoom para os componentes iniciais caberem', () => {
    const { editor } = novoEditor();
    editor.redimensionar(360, 480);
    editor.ajustarVistaInicial();
    expect(editor.vistaInicial.zoom).toBeLessThan(1);
    const [x] = editor.mundoParaTela([-300, -100]);
    const paleta = editor.paleta();
    expect(x).toBeGreaterThanOrEqual(paleta.x + paleta.largura);
    editor.redimensionar(1280, 600);
    editor.ajustarVistaInicial();
    expect(editor.vistaInicial).toEqual({ x: 0, y: 0, zoom: 1 });
  });
});
