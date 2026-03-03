// Tipos compartilhados para a engine de logica proposicional

// --- AST Nodes ---
export interface ASTNode {
  type: "variable" | "operator"
}

export interface VariableNode extends ASTNode {
  type: "variable"
  name: string
}

export interface OperatorNode extends ASTNode {
  type: "operator"
  op: string
  children: CircuitNode[]
}

export type CircuitNode = VariableNode | OperatorNode

// --- Simplificacao ---
export interface SimplifierNode {
  valor: string
  esquerda: SimplifierNode | null
  direita: SimplifierNode | null
}

export interface SimplificationStep {
  law: string
  before: string
  after: string
}

export interface SimplificationResult {
  original: string
  simplified: string
  steps: SimplificationStep[]
}

// --- Tabela Verdade ---
export interface TruthTableResult {
  columns: string[]
  rows: number[][]
  finalResults: number[]
  totalCombinations: number
  totalVariables: number
  classification: "TAUTOLOGIA" | "CONTRADICAO" | "SATISFATIVEL"
}

// --- Equivalencia ---
export interface EquivalenceResult {
  equivalent: boolean
  variables: string[]
  differences: {
    values: Record<string, boolean>
    result1: boolean
    result2: boolean
  }[]
}

// --- Simplificacao interativa ---
export interface LogicLaw {
  name: string
  check: (node: SimplifierNode) => boolean
  apply: (node: SimplifierNode) => SimplifierNode
}

export interface InteractiveStepInfo {
  currentNode: SimplifierNode
  parent: SimplifierNode | null
  branch: "esquerda" | "direita" | null
  applicableLaws: boolean[]
}

// --- Circuit Layout ---
export interface CircuitLayout {
  type: "variable" | "negated_variable" | "gate"
  name?: string
  op?: string
  yPos: number
  height: number
  width: number
  children?: CircuitLayout[]
}

// --- Problemas ---
export interface Problem {
  name: string
  question: string
  answer: string
  difficulty: "Facil" | "Medio" | "Dificil" | "Supremo"
}

// --- Conversao ---
export interface ConversionResult {
  original: string
  converted: string
  steps: string[]
}

// --- Token types ---
export type Token = string | boolean
