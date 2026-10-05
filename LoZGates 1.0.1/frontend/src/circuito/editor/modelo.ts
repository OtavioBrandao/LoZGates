/**
 * Editor do circuito interativo — a interação que o interface_update fazia em
 * pygame (BackEnd/circuito_logico/interactive/interactive_circuit.py, palette.py
 * e rendering/camera.py), agora no navegador. Aqui não há desenho nem DOM: só o
 * estado e as regras (clique, pinos, fios, arrasto, colisão, câmera, histórico).
 *
 * A geometria (tamanhos, pinos, margens) vem da API
 * (circuito_logico/logic/componentes.py) e a correção do circuito montado é
 * feita no servidor (circuito_logico/logic/validacao.py).
 *
 * Diferença deliberada: desfazer/refazer guardam o circuito inteiro. No
 * original o histórico restaurava só posições e fios pelo índice na lista, então
 * desfazer uma inclusão não removia a porta e desfazer uma remoção podia
 * perder fios; e um estado só era salvo se a ação anterior tivesse mais de 0,5 s.
 */
import type { ComponenteInicial, DefinicoesComponentes, Netlist, Ponto } from '../../api/tipos';

export interface Componente {
  id: string;
  /** variable, and, or, not, nand, nor, xor, xnor, output */
  tipo: string;
  nome: string;
  x: number;
  y: number;
}

/** Fio da saída de `origem` para a entrada `entrada` de `destino`. */
export interface Fio {
  origem: string;
  destino: string;
  entrada: number;
}

export interface Camera {
  x: number;
  y: number;
  zoom: number;
}

interface Instantaneo {
  componentes: Componente[];
  fios: Fio[];
  selecionado: string | null;
}

export interface BotaoDaPaleta {
  tipo: string;
  nome: string;
  cor: [number, number, number];
  permitido: boolean;
  x: number;
  y: number;
  largura: number;
  altura: number;
}

export interface Paleta {
  x: number;
  y: number;
  largura: number;
  altura: number;
  botoes: BotaoDaPaleta[];
}

/** Ação que o editor pede para quem o usa (testar o circuito vai ao servidor). */
export type Pedido = 'testar' | null;

/** Componentes da paleta (ComponentPalette.components). */
export const COMPONENTES_DA_PALETA: { tipo: string; nome: string; cor: [number, number, number] }[] = [
  { tipo: 'and', nome: 'AND', cor: [60, 120, 220] },
  { tipo: 'or', nome: 'OR', cor: [50, 200, 130] },
  { tipo: 'not', nome: 'NOT', cor: [250, 170, 70] },
  { tipo: 'nand', nome: 'NAND', cor: [120, 60, 220] },
  { tipo: 'nor', nome: 'NOR', cor: [200, 50, 130] },
  { tipo: 'xor', nome: 'XOR', cor: [220, 120, 60] },
  { tipo: 'xnor', nome: 'XNOR', cor: [60, 220, 120] },
];

const ZOOM_MINIMO = 0.2;
const ZOOM_MAXIMO = 3.0;
const PASSO_DO_ZOOM = 0.1;
/** Camera.move_speed: pixels de tela por quadro (o laço do desktop rodava a ~60 quadros/s) */
const VELOCIDADE_DA_CAMERA = 5;
const QUADROS_POR_SEGUNDO = 60;

type Registrar = (metodo: 'log_component_action', ...argumentos: unknown[]) => void;

/** pygame.Rect trunca as coordenadas para inteiros. */
interface Retangulo {
  x: number;
  y: number;
  l: number;
  a: number;
}
const retangulo = (x: number, y: number, l: number, a: number): Retangulo => ({
  x: Math.trunc(x),
  y: Math.trunc(y),
  l: Math.trunc(l),
  a: Math.trunc(a),
});
/** Rect.colliderect: bordas que só se encostam não colidem. */
const colidem = (r: Retangulo, s: Retangulo) =>
  r.l > 0 && r.a > 0 && s.l > 0 && s.a > 0 && r.x < s.x + s.l && r.x + r.l > s.x && r.y < s.y + s.a && r.y + r.a > s.y;
/** Rect.collidepoint: inclui a borda esquerda/superior e exclui a direita/inferior (o ponto também vira inteiro). */
const contemPonto = (r: Retangulo, [px, py]: Ponto) => {
  const x = Math.trunc(px);
  const y = Math.trunc(py);
  return x >= r.x && x < r.x + r.l && y >= r.y && y < r.y + r.a;
};
const distancia = ([ax, ay]: Ponto, [bx, by]: Ponto) => Math.hypot(ax - bx, ay - by);
const copiar = <T>(valor: T): T => JSON.parse(JSON.stringify(valor)) as T;

export class EditorDeCircuito {
  componentes: Componente[];
  fios: Fio[] = [];
  selecionado: string | null = null;
  /** Conexão começada numa saída (connection_start) */
  conectando: string | null = null;
  /** Componente "fantasma" seguindo o cursor enquanto é posicionado */
  fantasma: Componente | null = null;
  camera: Camera = { x: 0, y: 0, zoom: 1 };
  /** Vista inicial (a tecla R volta para ela) */
  vistaInicial: Camera = { x: 0, y: 0, zoom: 1 };
  largura = 640;
  altura = 480;
  /** Última posição do cursor, em coordenadas de tela */
  cursor: Ponto = [0, 0];
  readonly movimento = { cima: false, baixo: false, esquerda: false, direita: false };

  private historico: Instantaneo[] = [];
  private indiceHistorico = -1;
  private proximoId = 1;
  private arrastou = false;

  constructor(
    private readonly definicoes: DefinicoesComponentes,
    iniciais: ComponenteInicial[],
    private readonly permitidas: string[] | null,
    private readonly registrar: Registrar = () => {},
  ) {
    this.componentes = iniciais.map((c) => ({ ...c }));
    this.salvarEstado();
  }

  // ------------------------------ geometria ------------------------------

  private definicao(tipo: string) {
    const definicao = this.definicoes.tipos[tipo];
    if (!definicao) throw new Error(`Tipo de componente desconhecido: ${tipo}`);
    return definicao;
  }

  dimensoes(tipo: string): { largura: number; altura: number } {
    const { largura, altura } = this.definicao(tipo);
    return { largura, altura };
  }

  entradas(c: Componente): Ponto[] {
    return this.definicao(c.tipo).entradas.map(([dx, dy]) => [c.x + dx, c.y + dy]);
  }

  saida(c: Componente): Ponto | null {
    const pino = this.definicao(c.tipo).saida;
    return pino ? [c.x + pino[0], c.y + pino[1]] : null;
  }

  private retanguloDeSelecao(c: Componente): Retangulo {
    const { largura, altura, folga_de_selecao: folga } = this.definicao(c.tipo);
    return retangulo(c.x - folga, c.y - folga, largura + 2 * folga, altura + 2 * folga);
  }

  /** check_collision: há outro componente (com margem) na posição (x, y)? */
  colide(c: Componente, x: number, y: number, ignorar: string | null = null): boolean {
    const m = this.definicoes.margem_de_colisao;
    const { largura, altura } = this.definicao(c.tipo);
    const area = retangulo(x - m, y - m, largura + 2 * m, altura + 2 * m);
    return this.componentes.some((outro) => {
      if (outro.id === c.id || outro.id === ignorar) return false;
      const d = this.definicao(outro.tipo);
      return colidem(area, retangulo(outro.x - m, outro.y - m, d.largura + 2 * m, d.altura + 2 * m));
    });
  }

  /** find_valid_position: a posição pedida ou a primeira livre numa espiral em volta dela. */
  posicaoValida(c: Componente, x: number, y: number): Ponto {
    if (!this.colide(c, x, y)) return [x, y];
    const { passo, raio_maximo: raioMaximo, passo_angulo: passoAngulo } = this.definicoes.busca_espiral;
    for (let raio = passo; raio < raioMaximo; raio += passo) {
      for (let angulo = 0; angulo < 360; angulo += passoAngulo) {
        const rad = (angulo * Math.PI) / 180;
        const tx = x + raio * Math.cos(rad);
        const ty = y + raio * Math.sin(rad);
        if (!this.colide(c, tx, ty)) return [tx, ty];
      }
    }
    // Sem lugar livre por perto: fica onde foi pedido mesmo
    return [x, y];
  }

  /** find_connection_point: saídas primeiro, depois entradas. */
  pinoEm(c: Componente, ponto: Ponto): { tipo: 'saida' | 'entrada'; indice: number } | null {
    const raio = this.definicoes.raio_de_deteccao_do_pino;
    const saida = this.saida(c);
    if (saida && distancia(ponto, saida) <= raio) return { tipo: 'saida', indice: 0 };
    const indice = this.entradas(c).findIndex((entrada) => distancia(ponto, entrada) <= raio);
    return indice >= 0 ? { tipo: 'entrada', indice } : null;
  }

  /** O primeiro componente (na ordem da lista) cuja área de seleção contém o ponto, e o pino clicado nele. */
  alvoEm(ponto: Ponto): { componente: Componente | undefined; pino: ReturnType<EditorDeCircuito['pinoEm']> } {
    const componente = this.componentes.find((c) => contemPonto(this.retanguloDeSelecao(c), ponto));
    return { componente, pino: componente ? this.pinoEm(componente, ponto) : null };
  }

  componente(id: string | null): Componente | undefined {
    return id === null ? undefined : this.componentes.find((c) => c.id === id);
  }

  /** Entrada `indice` de `destino` já recebe um fio? */
  entradaLigada(destino: string, indice: number): boolean {
    return this.fios.some((f) => f.destino === destino && f.entrada === indice);
  }

  saidaLigada(origem: string): boolean {
    return this.fios.some((f) => f.origem === origem);
  }

  // ------------------------------ câmera ------------------------------

  redimensionar(largura: number, altura: number): void {
    // fit_surface_size: no mínimo 320×240
    this.largura = Math.max(320, Math.trunc(largura));
    this.altura = Math.max(240, Math.trunc(altura));
  }

  telaParaMundo([sx, sy]: Ponto): Ponto {
    const { x, y, zoom } = this.camera;
    return [(sx - this.largura / 2) / zoom + x, (sy - this.altura / 2) / zoom + y];
  }

  mundoParaTela([wx, wy]: Ponto): Ponto {
    const { x, y, zoom } = this.camera;
    return [(wx - x) * zoom + this.largura / 2, (wy - y) * zoom + this.altura / 2];
  }

  /**
   * Vista inicial: a do desktop (centro na origem, zoom 1) quando tudo cabe;
   * em telas estreitas, afasta o zoom para os componentes iniciais caberem.
   */
  ajustarVistaInicial(): void {
    const paleta = this.paleta();
    const caixa = this.caixaDosComponentes();
    const cabe = (camera: Camera) => {
      this.camera = camera;
      const [x1] = this.mundoParaTela([caixa.x1, caixa.y1]);
      const [x2] = this.mundoParaTela([caixa.x2, caixa.y2]);
      const [, y1] = this.mundoParaTela([caixa.x1, caixa.y1]);
      const [, y2] = this.mundoParaTela([caixa.x2, caixa.y2]);
      return x1 >= paleta.x + paleta.largura + 8 && x2 <= this.largura - 8 && y1 >= 8 && y2 <= this.altura - 8;
    };
    let vista: Camera = { x: 0, y: 0, zoom: 1 };
    if (!cabe(vista)) {
      const larguraUtil = this.largura - (paleta.x + paleta.largura + 16) - 8;
      const zoom = Math.max(
        ZOOM_MINIMO,
        Math.min(1, larguraUtil / (caixa.x2 - caixa.x1), (this.altura - 16) / (caixa.y2 - caixa.y1)),
      );
      // Centraliza na área à direita da paleta
      const centroTelaX = (paleta.x + paleta.largura + 8 + this.largura) / 2;
      const centroMundoX = (caixa.x1 + caixa.x2) / 2;
      vista = {
        x: centroMundoX - (centroTelaX - this.largura / 2) / zoom,
        y: (caixa.y1 + caixa.y2) / 2,
        zoom,
      };
    }
    this.vistaInicial = vista;
    this.camera = { ...vista };
  }

  private caixaDosComponentes() {
    let x1 = Infinity;
    let y1 = Infinity;
    let x2 = -Infinity;
    let y2 = -Infinity;
    for (const c of this.componentes) {
      const { largura, altura } = this.definicao(c.tipo);
      x1 = Math.min(x1, c.x);
      y1 = Math.min(y1, c.y);
      x2 = Math.max(x2, c.x + largura);
      y2 = Math.max(y2, c.y + altura);
    }
    return { x1, y1, x2, y2 };
  }

  /** Camera.zoom_at: aproxima mantendo fixo o ponto sob o cursor. */
  zoomEm(pontoTela: Ponto, delta: number): void {
    const [wx, wy] = this.telaParaMundo(pontoTela);
    const zoom = Math.max(ZOOM_MINIMO, Math.min(ZOOM_MAXIMO, this.camera.zoom + delta));
    this.camera = {
      zoom,
      x: wx - (pontoTela[0] - this.largura / 2) / zoom,
      y: wy - (pontoTela[1] - this.altura / 2) / zoom,
    };
  }

  /** Roda do mouse: um "clique" da roda muda o zoom em 0,1. */
  rolar(pontoTela: Ponto, direcao: number): void {
    this.zoomEm(pontoTela, direcao > 0 ? -PASSO_DO_ZOOM : PASSO_DO_ZOOM);
  }

  resetarVista(): void {
    this.camera = { ...this.vistaInicial };
  }

  /** Movimento contínuo pelo teclado (WASD/setas). Devolve true se a câmera andou. */
  avancar(segundos: number): boolean {
    if (this.fantasma) return false; // desabilitado durante a colocação
    const { cima, baixo, esquerda, direita } = this.movimento;
    const passo = (VELOCIDADE_DA_CAMERA * QUADROS_POR_SEGUNDO * segundos) / this.camera.zoom;
    const dx = (direita ? passo : 0) - (esquerda ? passo : 0);
    const dy = (baixo ? passo : 0) - (cima ? passo : 0);
    if (!dx && !dy) return false;
    this.camera = { ...this.camera, x: this.camera.x + dx, y: this.camera.y + dy };
    return true;
  }

  // ------------------------------ paleta ------------------------------

  permitido(tipo: string): boolean {
    return this.permitidas === null || this.permitidas.includes(tipo);
  }

  /** ComponentPalette.resize + get_button_rect */
  paleta(): Paleta {
    const largura = Math.max(320, this.largura);
    const altura = Math.max(240, this.altura);
    const x = 8;
    const larguraPaleta = Math.max(100, Math.min(140, Math.trunc(largura * 0.14)));
    const y = Math.max(60, Math.min(160, Math.trunc(altura * 0.2)));
    const disponivel = Math.max(170, altura - y - 8);
    const areaDosBotoes = Math.max(140, disponivel - 30);
    const margem = 4;
    const total = COMPONENTES_DA_PALETA.length;
    const alturaBotao = Math.max(16, Math.min(45, Math.floor(areaDosBotoes / total) - margem));
    return {
      x,
      y,
      largura: larguraPaleta,
      altura: Math.min(disponivel, 30 + total * (alturaBotao + margem)),
      botoes: COMPONENTES_DA_PALETA.map((c, i) => ({
        ...c,
        permitido: this.permitido(c.tipo),
        x: x + 5,
        y: y + 30 + i * (alturaBotao + margem),
        largura: larguraPaleta - 10,
        altura: alturaBotao,
      })),
    };
  }

  // ------------------------------ mouse ------------------------------

  private posicionarFantasma(): void {
    if (!this.fantasma) return;
    const [wx, wy] = this.telaParaMundo(this.cursor);
    const [dx, dy] = this.definicoes.deslocamento_ao_posicionar;
    this.fantasma.x = wx - dx;
    this.fantasma.y = wy - dy;
  }

  moverCursor(pontoTela: Ponto): void {
    this.cursor = pontoTela;
    this.posicionarFantasma();
  }

  /** handle_mouse_click */
  clicar(pontoTela: Ponto): void {
    this.moverCursor(pontoTela);
    this.arrastou = false;

    // Colocando um componente: o clique o solta aqui
    if (this.fantasma) {
      this.soltarFantasma();
      return;
    }

    // Clique na paleta
    const paleta = this.paleta();
    if (contemPonto(retangulo(paleta.x, paleta.y, paleta.largura, paleta.altura), pontoTela)) {
      const botao = paleta.botoes.find((b) => b.permitido && contemPonto(retangulo(b.x, b.y, b.largura, b.altura), pontoTela));
      if (botao) this.comecarColocacao(botao.tipo);
      return; // o clique foi do painel
    }

    const { componente: clicado, pino } = this.alvoEm(this.telaParaMundo(pontoTela));
    if (!clicado) {
      // Clique no vazio: desseleciona e cancela a conexão
      this.selecionado = null;
      this.conectando = null;
      return;
    }
    if (!pino) {
      this.selecionado = clicado.id;
      return;
    }
    if (this.conectando) {
      if (pino.tipo === 'entrada') this.ligarEntrada(clicado, pino.indice);
      else this.conectando = clicado.id; // outra saída: recomeça a conexão dela
    } else if (pino.tipo === 'saida') {
      this.conectando = clicado.id;
    } else {
      this.selecionado = clicado.id;
    }
  }

  /** try_connect_to_input */
  private ligarEntrada(destino: Componente, indice: number): void {
    const origem = this.conectando;
    this.conectando = null;
    if (origem === null) return;
    if (this.entradaLigada(destino.id, indice)) return; // a entrada já está ocupada
    if (origem === destino.id) return; // um componente não se liga a si mesmo
    this.registrar('log_component_action', 'connect');
    this.fios.push({ origem, destino: destino.id, entrada: indice });
    this.salvarEstado();
  }

  /** handle_mouse_drag (botão pressionado e cursor andando). Devolve true se moveu. */
  arrastar(pontoTela: Ponto): boolean {
    this.moverCursor(pontoTela);
    if (this.fantasma || this.conectando) return false;
    const c = this.componente(this.selecionado);
    if (!c) return false;
    const [wx, wy] = this.telaParaMundo(pontoTela);
    const { largura, altura } = this.definicao(c.tipo);
    const nx = wx - Math.floor(largura / 2);
    const ny = wy - Math.floor(altura / 2);
    let destino: Ponto | null = null;
    if (!this.colide(c, nx, ny, c.id)) {
      destino = [nx, ny];
    } else {
      // Em cima de outro componente: só aceita um lugar livre bem perto
      const valida = this.posicaoValida(c, nx, ny);
      if (distancia(valida, [nx, ny]) < this.definicoes.distancia_maxima_de_ajuste_no_arrasto) destino = valida;
    }
    if (!destino || (destino[0] === c.x && destino[1] === c.y)) return false;
    c.x = destino[0];
    c.y = destino[1];
    this.arrastou = true;
    return true;
  }

  /** Fim do arrasto: um passo no histórico. */
  soltar(): void {
    if (this.arrastou) this.salvarEstado();
    this.arrastou = false;
  }

  /** start_component_placement */
  comecarColocacao(tipo: string): void {
    if (!this.permitido(tipo)) return;
    this.fantasma = { id: `g${this.proximoId++}`, tipo, nome: COMPONENTES_DA_PALETA.find((c) => c.tipo === tipo)?.nome ?? tipo, x: 0, y: 0 };
    this.posicionarFantasma();
  }

  /** place_ghost_component */
  private soltarFantasma(): void {
    const fantasma = this.fantasma;
    if (!fantasma) return;
    this.fantasma = null;
    const [x, y] = this.posicaoValida(fantasma, fantasma.x, fantasma.y);
    this.componentes.push({ ...fantasma, x, y });
    this.registrar('log_component_action', 'add', fantasma.tipo);
    this.salvarEstado();
  }

  /** O fantasma está sobre outro componente? (desenha o X vermelho) */
  fantasmaColide(): boolean {
    return this.fantasma !== null && this.colide(this.fantasma, this.fantasma.x, this.fantasma.y);
  }

  // ------------------------------ teclado e ações ------------------------------

  /** Esc: cancela a colocação; se não houver, cancela a conexão. */
  cancelar(): void {
    if (this.fantasma) this.fantasma = null;
    else this.conectando = null;
  }

  /** delete_selected: tira os fios do componente e o remove (variáveis e saída ficam). */
  remover(): void {
    const c = this.componente(this.selecionado);
    if (!c) return;
    this.registrar('log_component_action', 'delete', c.tipo);
    const fiosAntes = this.fios.length;
    this.fios = this.fios.filter((f) => f.origem !== c.id && f.destino !== c.id);
    let mudou = this.fios.length !== fiosAntes;
    if (c.tipo !== 'variable' && c.tipo !== 'output') {
      this.componentes = this.componentes.filter((outro) => outro.id !== c.id);
      mudou = true;
    }
    this.selecionado = null;
    if (mudou) this.salvarEstado();
  }

  podeDesfazer(): boolean {
    return this.indiceHistorico > 0;
  }

  podeRefazer(): boolean {
    return this.indiceHistorico < this.historico.length - 1;
  }

  desfazer(): boolean {
    if (!this.podeDesfazer()) return false;
    this.registrar('log_component_action', 'undo');
    this.indiceHistorico -= 1;
    this.restaurar(this.historico[this.indiceHistorico]);
    return true;
  }

  refazer(): boolean {
    if (!this.podeRefazer()) return false;
    this.indiceHistorico += 1;
    this.restaurar(this.historico[this.indiceHistorico]);
    return true;
  }

  /**
   * _on_key_press / _on_key_release. `tecla` é KeyboardEvent.key.
   * Devolve 'testar' quando o aluno aperta ESPAÇO (a correção é feita no servidor).
   */
  tecla(pressionada: boolean, tecla: string, ctrl: boolean): Pedido {
    const k = tecla.length === 1 ? tecla.toLowerCase() : tecla;
    const direcao: Record<string, keyof EditorDeCircuito['movimento']> = {
      w: 'cima',
      ArrowUp: 'cima',
      s: 'baixo',
      ArrowDown: 'baixo',
      a: 'esquerda',
      ArrowLeft: 'esquerda',
      d: 'direita',
      ArrowRight: 'direita',
    };
    if (!pressionada) {
      if (direcao[k]) this.movimento[direcao[k]] = false;
      return null;
    }
    if (ctrl && k === 'z') {
      this.desfazer();
      return null;
    }
    if (ctrl && k === 'y') {
      this.refazer();
      return null;
    }
    if (k === 'Escape') {
      this.cancelar();
      return null;
    }
    if (direcao[k]) this.movimento[direcao[k]] = true;
    if (k === 'r') this.resetarVista();
    if (k === 'Delete' || k === 'Backspace') this.remover();
    if (k === ' ') return 'testar';
    return null;
  }

  // ------------------------------ histórico ------------------------------

  private salvarEstado(): void {
    this.historico = this.historico.slice(0, this.indiceHistorico + 1);
    this.historico.push(copiar({ componentes: this.componentes, fios: this.fios, selecionado: this.selecionado }));
    if (this.historico.length > this.definicoes.maximo_de_estados_no_historico) this.historico.shift();
    this.indiceHistorico = this.historico.length - 1;
  }

  private restaurar(estado: Instantaneo): void {
    const copia = copiar(estado);
    this.componentes = copia.componentes;
    this.fios = copia.fios;
    this.selecionado = copia.selecionado && this.componente(copia.selecionado) ? copia.selecionado : null;
    if (this.conectando && !this.componente(this.conectando)) this.conectando = null;
  }

  // ------------------------------ correção ------------------------------

  /** O circuito montado, no formato que a API corrige (validacao.montar_netlist). */
  netlist(): Netlist {
    return {
      componentes: this.componentes.map(({ id, tipo, nome }) => ({ id, tipo, nome })),
      fios: this.fios.map(({ origem, destino, entrada }) => ({ origem, destino, entrada })),
    };
  }
}
