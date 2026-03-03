// Porte direto de identificar_lei.py - Simplificador automatico por arvore
import type { SimplifierNode, SimplificationStep, SimplificationResult } from "./types"

// --- Node helpers ---
export function createNode(valor: string, esquerda: SimplifierNode | null = null, direita: SimplifierNode | null = null): SimplifierNode {
  return { valor, esquerda, direita }
}

export function nodeToString(node: SimplifierNode | null): string {
  if (!node) return ""
  if (node.valor === "&" || node.valor === "|") {
    return `(${nodeToString(node.esquerda)}${node.valor}${nodeToString(node.direita)})`
  } else if (node.valor === "!") {
    return `!${nodeToString(node.esquerda)}`
  }
  return node.valor
}

function cloneNode(node: SimplifierNode | null): SimplifierNode | null {
  if (!node) return null
  return { valor: node.valor, esquerda: cloneNode(node.esquerda), direita: cloneNode(node.direita) }
}

// --- Parser ---
export function buildTree(expr: string): SimplifierNode {
  expr = expr.replace(/\s/g, "")

  function parseOr(s: string): SimplifierNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "|" && depth === 0) {
        return createNode("|", parseOr(s.slice(0, i)), parseAnd(s.slice(i + 1)))
      }
    }
    return parseAnd(s)
  }

  function parseAnd(s: string): SimplifierNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "&" && depth === 0) {
        return createNode("&", parseAnd(s.slice(0, i)), parseNot(s.slice(i + 1)))
      }
    }
    return parseNot(s)
  }

  function parseNot(s: string): SimplifierNode {
    if (s.startsWith("!")) {
      return createNode("!", parseOr(s.slice(1)))
    }
    if (s.startsWith("(") && s.endsWith(")")) {
      return parseOr(s.slice(1, -1))
    }
    return createNode(s)
  }

  return parseOr(expr)
}

// --- Checagens de inverso ---
function areInverses(n1: SimplifierNode | null, n2: SimplifierNode | null): boolean {
  if (!n1 || !n2) return false
  return (
    (n1.valor === "!" && nodeToString(n1.esquerda) === nodeToString(n2)) ||
    (n2.valor === "!" && nodeToString(n2.esquerda) === nodeToString(n1))
  )
}

// --- Leis logicas ---
function deMorgan(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if (node.valor === "!" && node.esquerda && (node.esquerda.valor === "&" || node.esquerda.valor === "|")) {
    const inner = node.esquerda
    const newOp = inner.valor === "&" ? "|" : "&"
    const result = createNode(newOp, createNode("!", cloneNode(inner.esquerda)), createNode("!", cloneNode(inner.direita)))
    steps.push({ law: "De Morgan", before: nodeToString(node), after: nodeToString(result) })
    return result
  }
  return node
}

function identidade(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if (node.valor === "&") {
    if (node.esquerda && nodeToString(node.esquerda) === "1") {
      steps.push({ law: "Identidade", before: nodeToString(node), after: nodeToString(node.direita) })
      return node.direita!
    }
    if (node.direita && nodeToString(node.direita) === "1") {
      steps.push({ law: "Identidade", before: nodeToString(node), after: nodeToString(node.esquerda) })
      return node.esquerda!
    }
  } else if (node.valor === "|") {
    if (node.esquerda && nodeToString(node.esquerda) === "0") {
      steps.push({ law: "Identidade", before: nodeToString(node), after: nodeToString(node.direita) })
      return node.direita!
    }
    if (node.direita && nodeToString(node.direita) === "0") {
      steps.push({ law: "Identidade", before: nodeToString(node), after: nodeToString(node.esquerda) })
      return node.esquerda!
    }
  }
  return node
}

function nula(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if (node.valor === "&") {
    if ((node.esquerda && nodeToString(node.esquerda) === "0") || (node.direita && nodeToString(node.direita) === "0")) {
      steps.push({ law: "Nula", before: nodeToString(node), after: "0" })
      return createNode("0")
    }
  } else if (node.valor === "|") {
    if ((node.esquerda && nodeToString(node.esquerda) === "1") || (node.direita && nodeToString(node.direita) === "1")) {
      steps.push({ law: "Nula", before: nodeToString(node), after: "1" })
      return createNode("1")
    }
  }
  return node
}

function idempotente(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if ((node.valor === "&" || node.valor === "|") && nodeToString(node.esquerda) === nodeToString(node.direita)) {
    steps.push({ law: "Idempotente", before: nodeToString(node), after: nodeToString(node.esquerda) })
    return node.esquerda!
  }
  return node
}

function inversa(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if (node.esquerda && node.direita && areInverses(node.esquerda, node.direita)) {
    if (node.valor === "&") {
      steps.push({ law: "Inversa", before: nodeToString(node), after: "0" })
      return createNode("0")
    }
    if (node.valor === "|") {
      steps.push({ law: "Inversa", before: nodeToString(node), after: "1" })
      return createNode("1")
    }
  }
  return node
}

function absorcao(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  const es = nodeToString(node.esquerda)
  const ds = nodeToString(node.direita)

  if (node.valor === "&" && node.direita?.valor === "|") {
    if (es === nodeToString(node.direita.esquerda) || es === nodeToString(node.direita.direita)) {
      steps.push({ law: "Absorcao", before: nodeToString(node), after: es })
      return node.esquerda!
    }
  }
  if (node.valor === "&" && node.esquerda?.valor === "|") {
    if (ds === nodeToString(node.esquerda.esquerda) || ds === nodeToString(node.esquerda.direita)) {
      steps.push({ law: "Absorcao", before: nodeToString(node), after: ds })
      return node.direita!
    }
  }
  if (node.valor === "|" && node.direita?.valor === "&") {
    if (es === nodeToString(node.direita.esquerda) || es === nodeToString(node.direita.direita)) {
      steps.push({ law: "Absorcao", before: nodeToString(node), after: es })
      return node.esquerda!
    }
  }
  if (node.valor === "|" && node.esquerda?.valor === "&") {
    if (ds === nodeToString(node.esquerda.esquerda) || ds === nodeToString(node.esquerda.direita)) {
      steps.push({ law: "Absorcao", before: nodeToString(node), after: ds })
      return node.direita!
    }
  }
  return node
}

function associativa(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if ((node.valor === "&" || node.valor === "|") && node.esquerda && node.esquerda.valor === node.valor) {
    const a = node.esquerda.esquerda
    const b = node.esquerda.direita
    const c = node.direita
    const result = createNode(node.valor, cloneNode(a), createNode(node.valor, cloneNode(b), cloneNode(c)))
    steps.push({ law: "Associativa", before: nodeToString(node), after: nodeToString(result) })
    return result
  }
  return node
}

function comutativa(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if ((node.valor === "&" || node.valor === "|") && node.esquerda && node.direita) {
    if (nodeToString(node.direita) < nodeToString(node.esquerda)) {
      const result = createNode(node.valor, cloneNode(node.direita), cloneNode(node.esquerda))
      steps.push({ law: "Comutativa", before: nodeToString(node), after: nodeToString(result) })
      return result
    }
  }
  return node
}

function distributiva(node: SimplifierNode, steps: SimplificationStep[]): SimplifierNode {
  if (
    node.valor === "&" &&
    node.esquerda?.valor === "|" &&
    node.direita?.valor === "|"
  ) {
    const a = node.esquerda.esquerda
    const b = node.esquerda.direita
    const c = node.direita.esquerda
    const d = node.direita.direita

    let common: SimplifierNode | null = null
    let o1: SimplifierNode | null = null
    let o2: SimplifierNode | null = null

    const as_ = nodeToString(a), bs = nodeToString(b), cs = nodeToString(c), ds_ = nodeToString(d)
    if (as_ === cs) { common = a; o1 = b; o2 = d }
    else if (as_ === ds_) { common = a; o1 = b; o2 = c }
    else if (bs === cs) { common = b; o1 = a; o2 = d }
    else if (bs === ds_) { common = b; o1 = a; o2 = c }

    if (common && o1 && o2) {
      const result = createNode("|", cloneNode(common), createNode("&", cloneNode(o1), cloneNode(o2)))
      steps.push({ law: "Distributiva", before: nodeToString(node), after: nodeToString(result) })
      return result
    }
  }
  return node
}

// --- Processo de simplificacao recursivo ---
type LawFn = (node: SimplifierNode, steps: SimplificationStep[]) => SimplifierNode

const LAWS: LawFn[] = [nula, inversa, idempotente, identidade, absorcao, deMorgan, associativa, distributiva, comutativa]

function applyLawsRecursive(node: SimplifierNode | null, steps: SimplificationStep[]): SimplifierNode | null {
  if (!node) return null

  if (node.esquerda) node.esquerda = applyLawsRecursive(node.esquerda, steps)
  if (node.direita) node.direita = applyLawsRecursive(node.direita, steps)

  const originalStr = nodeToString(node)
  let current = node

  for (const law of LAWS) {
    current = law(current, steps)
  }

  if (nodeToString(current) !== originalStr) {
    return applyLawsRecursive(current, steps)
  }
  return current
}

export function simplify(expression: string): SimplificationResult {
  let expr = expression.replace(/\+/g, "|").replace(/\*/g, "&").replace(/~/g, "!")
  const steps: SimplificationStep[] = []
  let tree = buildTree(expr)

  let maxIterations = 50
  while (maxIterations-- > 0) {
    const before = nodeToString(tree)
    tree = applyLawsRecursive(tree, steps) ?? tree
    if (nodeToString(tree) === before) break
  }

  return {
    original: expression,
    simplified: nodeToString(tree),
    steps,
  }
}
