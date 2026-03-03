// Configuration constants, examples, tips
// Ported from Python config.py

export const INTERACTIVE_EXAMPLES = {
  basic: [
    { expr: "A & B", name: "Conjuncao simples", desc: "Verdadeiro apenas se A E B forem verdadeiros" },
    { expr: "A | B", name: "Disjuncao simples", desc: "Verdadeiro se A OU B for verdadeiro" },
    { expr: "!A", name: "Negacao simples", desc: "Inverte o valor de A" },
    { expr: "A & B | C", name: "Precedencia basica", desc: "Primeiro A & B, depois OR com C" },
  ],
  intermediate: [
    { expr: "(A | B) & C", name: "Parenteses prioritarios", desc: "Primeiro A | B, depois AND com C" },
    { expr: "A > B", name: "Implicacao", desc: "Se A entao B: equivale a !A | B" },
    { expr: "!(A & B)", name: "Lei de De Morgan", desc: "Equivale a !A | !B" },
    { expr: "A <> B", name: "Bi-implicacao", desc: "A se e somente se B" },
  ],
  advanced: [
    { expr: "(A & B) | (!C & D)", name: "Combinacao complexa", desc: "Multiplos operadores e negacoes" },
    { expr: "(A > B) & (B > A)", name: "Equivalente a bi-implicacao", desc: "Duas implicacoes formam bi-implicacao" },
    { expr: "(A | B) & !(A & B)", name: "XOR logico", desc: "OU exclusivo: um ou outro, mas nao ambos" },
    { expr: "((A & B) | C) > (D <> E)", name: "Expressao hierarquica", desc: "Multiplos niveis de precedencia" },
  ],
}

export const SYNTAX_HELP = {
  operators: [
    { symbol: "&", name: "AND (E)", desc: "Conjuncao: verdadeiro se ambos forem verdadeiros" },
    { symbol: "|", name: "OR (OU)", desc: "Disjuncao: verdadeiro se ao menos um for verdadeiro" },
    { symbol: "!", name: "NOT (NAO)", desc: "Negacao: inverte o valor logico" },
    { symbol: ">", name: "Implicacao", desc: "Se A entao B: equivale a !A | B" },
    { symbol: "<>", name: "Bi-implicacao", desc: "A se e somente se B" },
    { symbol: "()", name: "Parenteses", desc: "Define precedencia de operacoes" },
  ],
  precedence: ["! (NOT) - maior precedencia", "& (AND)", "| (OR)", "> (Implicacao)", "<> (Bi-implicacao) - menor precedencia"],
  variables: "Use letras maiusculas A-Z para variaveis. Cada letra representa uma proposicao distinta.",
}

export const LOGIC_LAWS_INFO = [
  { name: "Identidade", formulas: ["A & 1 = A", "A | 0 = A"], desc: "Elemento neutro da operacao" },
  { name: "Nula", formulas: ["A & 0 = 0", "A | 1 = 1"], desc: "Elemento absorvente da operacao" },
  { name: "Idempotencia", formulas: ["A & A = A", "A | A = A"], desc: "Operacao com si mesmo" },
  { name: "Inversa", formulas: ["A & !A = 0", "A | !A = 1"], desc: "Complemento: elemento com sua negacao" },
  { name: "De Morgan", formulas: ["!(A & B) = !A | !B", "!(A | B) = !A & !B"], desc: "Negacao distribui e troca operador" },
  { name: "Absorcao", formulas: ["A & (A | B) = A", "A | (A & B) = A"], desc: "Termo absorvido pelo principal" },
  { name: "Distributiva", formulas: ["A & (B | C) = (A & B) | (A & C)", "A | (B & C) = (A | B) & (A | C)"], desc: "Distribuicao de operador" },
  { name: "Associativa", formulas: ["(A & B) & C = A & (B & C)", "(A | B) | C = A | (B | C)"], desc: "Reagrupamento de operandos" },
  { name: "Comutativa", formulas: ["A & B = B & A", "A | B = B | A"], desc: "Troca de ordem dos operandos" },
]

export const CONTEXTUAL_TIPS = {
  simplification: [
    "Procure primeiro por padroes como (A & !A) = 0",
    "Use parenteses para deixar a precedencia clara",
    "Aplique De Morgan para simplificar negacoes complexas",
    "Leis de absorcao frequentemente simplificam muito",
    "Use 'Desfazer' se aplicar uma lei por engano",
  ],
  expression_entry: [
    "Use & para AND, | para OR, ! para NOT",
    "Precedencia: ! > & > | > > > <>",
    "Teste com tabela verdade se nao tem certeza",
    "Pense na expressao em linguagem natural primeiro",
    "Use letras A-Z para variaveis",
  ],
}

export const COMMON_FAQ = [
  {
    question: "Qual a sintaxe correta das expressoes?",
    answer: "Use & ou * para AND, | ou + para OR, ! ou ~ para NOT, > para implicacao, <> para bi-implicacao, e parenteses () para precedencia.",
  },
  {
    question: "Estou travado na simplificacao, e agora?",
    answer: "Procure padroes como A & !A = 0, aplique De Morgan em negacoes complexas, use absorcao: A & (A | B) = A, ou use o botao 'Desfazer' se errar.",
  },
  {
    question: "Como funciona a tabela verdade?",
    answer: "A tabela verdade mostra todas as combinacoes possiveis de valores (0 e 1) para as variaveis e o resultado da expressao para cada combinacao.",
  },
  {
    question: "O que e tautologia, contradicao e satisfativel?",
    answer: "Tautologia: sempre verdadeira. Contradicao: sempre falsa. Satisfativel: verdadeira para algumas combinacoes e falsa para outras.",
  },
]
