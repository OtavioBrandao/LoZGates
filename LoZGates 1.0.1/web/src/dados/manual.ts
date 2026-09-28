/**
 * Conteúdo do manual interativo — transcrito de FrontEnd/interactive_help.py
 * (InteractiveHelpSystem). Mantenha os dois arquivos em sincronia.
 */

export type Cor = 'sucesso' | 'aviso' | 'erro';

export type Bloco =
  | { tipo: 'titulo'; texto: string }
  | { tipo: 'paragrafo'; texto: string }
  | { tipo: 'lista'; itens: string[] }
  | { tipo: 'codigo'; texto: string }
  | { tipo: 'operador'; nome: string; simbolo: string; exemplo: string; significado: string }
  | { tipo: 'funcionalidade'; titulo: string; descricao: string; detalhes: string[] }
  | { tipo: 'exemplos'; nivel: string; cor: Cor; exemplos: [string, string][] }
  | { tipo: 'lei'; nome: string; regras: string[]; explicacao: string }
  | { tipo: 'controles'; titulo: string; controles: [string, string][] }
  | { tipo: 'dicas'; titulo: string; icone: string; dicas: string[] }
  | { tipo: 'botoes'; botoes: { texto: string; url?: string; acao?: 'fechar'; cor?: string }[] }
  | { tipo: 'destaque'; texto: string };

export interface AbaManual {
  id: string;
  rotulo: string;
  blocos: Bloco[];
}

export const ABAS_MANUAL: AbaManual[] = [
  {
    id: 'sobre',
    rotulo: '📘 Sobre',
    blocos: [
      { tipo: 'titulo', texto: '🎯 Objetivo do projeto' },
      {
        tipo: 'paragrafo',
        texto:
          'O LoZ Gates é uma ferramenta educacional interativa que conecta os conceitos de Lógica Proposicional com Circuitos Digitais, proporcionando uma experiência de aprendizado visual e prática para estudantes e educadores.',
      },
      { tipo: 'titulo', texto: '👥 Equipe de desenvolvimento' },
      {
        tipo: 'lista',
        itens: [
          '• Larissa Ferreira Dias de Souza - Sistemas interativos & Backend - lfds@ic.ufal.br',
          '• Otávio Joshua Costa Brandão Menezes - UI & UX - ojcbm@ic.ufal.br',
          '• Zilderlan Naty dos Santos - IA - zns@ic.ufal.br',
          '• David Kelve Oliveira Barbosa - Simplificação & Banco de problemas - dkob@ic.ufal.br',
          '👨‍🏫 Orientador: Prof. Dr. Evandro de Barros Costa',
        ],
      },
      { tipo: 'titulo', texto: '🏛️ Instituição' },
      { tipo: 'paragrafo', texto: 'Universidade Federal de Alagoas (UFAL)\nInstituto de Computação (IC)' },
      { tipo: 'botoes', botoes: [{ texto: '🌐 Site da UFAL', url: 'https://ufal.br' }] },
    ],
  },
  {
    id: 'funcionalidades',
    rotulo: '🔧 Funcionalidades',
    blocos: [
      {
        tipo: 'funcionalidade',
        titulo: '📊 Visualização de circuitos',
        descricao: 'Geração automática de circuitos lógicos a partir de expressões',
        detalhes: ['• Visualização em tempo real das conexões', '• Export de imagens PNG dos circuitos', '• Interface intuitiva e didática'],
      },
      {
        tipo: 'funcionalidade',
        titulo: '🎮 Circuito interativo',
        descricao: 'Construção manual de circuitos',
        detalhes: [
          '• 6 modos de desafio diferentes',
          '• Sistema de validação automática',
          '• Feedback visual em tempo real',
          '• Suporte a componentes básicos e avançados',
        ],
      },
      {
        tipo: 'funcionalidade',
        titulo: '🧮 Simplificação interativa',
        descricao: 'Aplicação passo a passo das leis de simplificação',
        detalhes: [
          '• Interface guiada com explicações',
          '• Sistema de undo/redo',
          '• Histórico completo das transformações',
          '• Aplicação de 9 leis lógicas diferentes',
        ],
      },
      {
        tipo: 'funcionalidade',
        titulo: '📋 Tabela verdade inteligente',
        descricao: 'Geração automática para qualquer expressão',
        detalhes: ['• Análise de tautologias e contradições', '• Interface colorizada', '• Suporte a expressões complexas'],
      },
      {
        tipo: 'funcionalidade',
        titulo: '🧪 Problemas do mundo real',
        descricao: 'Mais de 30 problemas práticos categorizados',
        detalhes: ['• 4 níveis de dificuldade', '• Aplicações reais de lógica proposicional'],
      },
    ],
  },
  {
    id: 'sintaxe',
    rotulo: '📝 Sintaxe',
    blocos: [
      { tipo: 'titulo', texto: '🔤 Variáveis aceitas' },
      { tipo: 'codigo', texto: 'Qualquer letra de A-Z (maiúscula ou minúscula)\nExemplo: A, B, C, p, Q, R, x, y, Z' },
      { tipo: 'titulo', texto: '🔣 Operadores lógicos' },
      { tipo: 'operador', nome: 'CONJUNÇÃO', simbolo: '&', exemplo: 'A & B', significado: '"A e B"' },
      { tipo: 'operador', nome: 'DISJUNÇÃO', simbolo: '|', exemplo: 'A | B', significado: '"A ou B"' },
      { tipo: 'operador', nome: 'NEGAÇÃO', simbolo: '!', exemplo: '!A', significado: '"não A"' },
      { tipo: 'operador', nome: 'IMPLICAÇÃO', simbolo: '>', exemplo: 'A > B', significado: '"se A então B"' },
      { tipo: 'operador', nome: 'BI-IMPLICAÇÃO', simbolo: '<>', exemplo: 'A <> B', significado: '"A se e somente se B"' },
      { tipo: 'titulo', texto: '⚠️ Precedência dos operadores' },
      {
        tipo: 'lista',
        itens: [
          '1. ! (Negação) - MAIOR precedência',
          '2. & (Conjunção)',
          '3. | (Disjunção)',
          '4. > (Implicação)',
          '5. <> (Bi-implicação) - MENOR precedência',
        ],
      },
    ],
  },
  {
    id: 'exemplos',
    rotulo: '💡 Exemplos',
    blocos: [
      {
        tipo: 'exemplos',
        nivel: '🟢 Básicas',
        cor: 'sucesso',
        exemplos: [
          ['A & B', 'Conjunção simples'],
          ['A | B', 'Disjunção simples'],
          ['!A', 'Negação simples'],
          ['A & B | C', 'Conjunção seguida de disjunção'],
        ],
      },
      {
        tipo: 'exemplos',
        nivel: '🟡 Intermediárias',
        cor: 'aviso',
        exemplos: [
          ['(A | B) & C', 'Disjunção prioritária'],
          ['A > B', 'Implicação'],
          ['!(A & B)', 'Negação de conjunção'],
          ['A <> B', 'Bi-implicação'],
        ],
      },
      {
        tipo: 'exemplos',
        nivel: '🔴 Avançadas',
        cor: 'erro',
        exemplos: [
          ['(A & B) | (!C & D)', 'Combinação complexa'],
          ['(A > B) & (B > A)', 'Equivalente à bi-implicação'],
          ['(A | B) & !(A & B)', 'XOR lógico'],
          ['((A & B) | C) > (D <> E)', 'Expressão hierárquica'],
        ],
      },
      { tipo: 'botoes', botoes: [{ texto: '🧪 Testar exemplos no LoZ Gates', acao: 'fechar', cor: '#1976D2' }] },
    ],
  },
  {
    id: 'leis',
    rotulo: '⚖️ Leis',
    blocos: [
      { tipo: 'titulo', texto: '📚 Leis fundamentais da lógica' },
      {
        tipo: 'lei',
        nome: '🔶 Lei da identidade',
        regras: ['A & 1 = A', 'A | 0 = A'],
        explicacao: '"E com verdadeiro (1) é a própria variável"\n"OU com falso (0) é a própria variável"',
      },
      {
        tipo: 'lei',
        nome: '🔶 Lei nula (absorção total)',
        regras: ['A & 0 = 0', 'A | 1 = 1'],
        explicacao: '"E com falso (0) é sempre falso"\n"Ou com verdadeiro (1) é sempre verdadeiro"',
      },
      { tipo: 'lei', nome: '🔶 Lei idempotente', regras: ['A & A = A', 'A | A = A'], explicacao: '"Variável consigo mesma não muda"' },
      {
        tipo: 'lei',
        nome: '🔶 Lei inversa (complemento)',
        regras: ['A & !A = 0', 'A | !A = 1'],
        explicacao: '"Variável com sua negação dá resultado fixo"',
      },
      {
        tipo: 'lei',
        nome: '🔶 Lei de De Morgan',
        regras: ['!(A & B) = !A | !B', '!(A | B) = !A & !B'],
        explicacao: '"Negação distribui trocando o operador"',
      },
      {
        tipo: 'lei',
        nome: '🔶 Lei de absorção',
        regras: ['A & (A | B) = A', 'A | (A & B) = A'],
        explicacao: '"Variável absorve expressões que a contêm"',
      },
      {
        tipo: 'lei',
        nome: '🔶 Lei distributiva',
        regras: ['A & (B | C) = (A & B) | (A & C)', 'A | (B & C) = (A | B) & (A | C)'],
        explicacao: '"Distribui um operador sobre o outro"',
      },
      {
        tipo: 'lei',
        nome: '🔶 Lei associativa',
        regras: ['(A & B) & C = A & (B & C)', '(A | B) | C = A | (B | C)'],
        explicacao: '"Reagrupa operações do mesmo tipo"',
      },
      { tipo: 'lei', nome: '🔶 Lei comutativa', regras: ['A & B = B & A', 'A | B = B | A'], explicacao: '"Ordem das variáveis não importa"' },
    ],
  },
  {
    id: 'controles',
    rotulo: '🎮 Controles',
    blocos: [
      {
        tipo: 'controles',
        titulo: '🔧 Controles básicos - circuito interativo',
        controles: [
          ['ESPAÇO', 'Testar circuito'],
          ['Clique', 'Selecionar componente'],
          ['Arrastar', 'Mover componente'],
          ['DELETE', 'Remover selecionado'],
          ['ESC', 'Cancelar ação atual'],
        ],
      },
      {
        tipo: 'controles',
        titulo: '📐 Navegação da câmera',
        controles: [
          ['W / ↑', 'Mover câmera para cima'],
          ['S / ↓', 'Mover câmera para baixo'],
          ['A / ←', 'Mover câmera para esquerda'],
          ['D / →', 'Mover câmera para direita'],
          ['Scroll', 'Zoom in/out'],
          ['R', 'Resetar vista'],
        ],
      },
      {
        tipo: 'controles',
        titulo: '✏️ Edição avançada',
        controles: [
          ['CTRL+Z', 'Desfazer última ação'],
          ['CTRL+Y', 'Refazer ação desfeita'],
          ['Bolinhas verdes', 'Pontos de conexão'],
          ['Clique duplo', 'Focar em componente'],
        ],
      },
      { tipo: 'titulo', texto: '📋 Como jogar - passo a passo' },
      {
        tipo: 'lista',
        itens: [
          '1. 🎯 Selecione um modo de desafio',
          "2. ▶️ Clique em 'Iniciar desafio'",
          '3. 🔧 Adicione componentes clicando no painel',
          '4. 🔗 Conecte os pontos verdes',
          '5. 🧪 Pressione ESPAÇO para testar!',
          '6. ✅ Implemente a expressão corretamente!',
        ],
      },
    ],
  },
  {
    id: 'dicas',
    rotulo: '💭 Dicas',
    blocos: [
      {
        tipo: 'dicas',
        titulo: '🔰 Para iniciantes',
        icone: '🟢',
        dicas: [
          'Comece com expressões simples (2-3 variáveis)',
          'Use parênteses quando em dúvida sobre precedência',
          'Teste suas expressões com a tabela verdade primeiro',
          "Explore o modo 'Portas básicas' no circuito interativo",
        ],
      },
      {
        tipo: 'dicas',
        titulo: '🎯 Para intermediários',
        icone: '🟡',
        dicas: [
          'Pratique simplificação manual antes do modo interativo',
          'Tente os desafios NAND e NOR',
          'Compare diferentes formas da mesma expressão',
          'Explore os problemas do mundo real',
        ],
      },
      {
        tipo: 'dicas',
        titulo: '🚀 Para avançados',
        icone: '🔴',
        dicas: [
          "Use o modo 'Desafio mínimo' para otimizar",
          'Experimente com expressões de 4+ variáveis',
          'Crie seus próprios problemas complexos',
          'Explore as nuances das leis distributivas',
        ],
      },
      { tipo: 'titulo', texto: '🎯 Estratégias de Simplificação' },
      {
        tipo: 'paragrafo',
        texto:
          '✅ Ordem Recomendada:\n    1️ Leis nula\n    2️ Leis inversas\n    3️ Identidade e idempotente\n    4️ Absorção\n    5️ De Morgan e distributiva\n\n🔍 Reconhecimento de padrões:\n  • Procure por (A & !A) ou (A | !A) primeiro\n  • Identifique oportunidades de absorção\n  • Use De Morgan para simplificar negações complexas',
      },
    ],
  },
  {
    id: 'creditos',
    rotulo: '🏆 Créditos',
    blocos: [
      { tipo: 'titulo', texto: '🎓 Sobre o LoZ Gates' },
      {
        tipo: 'paragrafo',
        texto: 'Versão 1.0-Beta\nProjeto educacional desenvolvido na Universidade Federal de Alagoas (UFAL)\nInstituto de Computação - 2024',
      },
      { tipo: 'titulo', texto: '💡 Tecnologias Utilizadas' },
      {
        tipo: 'lista',
        itens: [
          '• Python 3.8+ (Linguagem principal)',
          '• CustomTkinter (Interface moderna)',
          '• Pygame (Circuitos interativos)',
          '• PIL/Pillow (Processamento de imagens)',
          '• Requests (Comunicação web)',
        ],
      },
      {
        tipo: 'botoes',
        botoes: [
          { texto: '🐙 Repositório GitHub', url: 'https://github.com/LarissaFDS/LoZGates/tree/main', cor: '#333333' },
          { texto: '🏛️ IC-UFAL', url: 'https://ic.ufal.br', cor: '#1A9AB0' },
        ],
      },
      {
        tipo: 'destaque',
        texto:
          '"É importante extrair sabedoria de diferentes lugares.\nSe você a extrai de um lugar só, ela se torna rígida e obsoleta."\n- Iroh\n\n🚀 Obrigado por usar o LoZ Gates!',
      },
    ],
  },
];
