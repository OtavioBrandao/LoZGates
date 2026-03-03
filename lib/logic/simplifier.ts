// Automatic Simplifier with 9 Logic Laws
// Ported from Python identificar_lei.py

import { ExprNode, buildTree } from "./expression-tree"

export interface SimplificationStep {
  law: string
  before: string
  after: string
}

function areInverses(n1: ExprNode | null, n2: ExprNode | null): boolean {
  if (!n1 || !n2) return false
  return (
    (n1.valor === "!" && n1.esquerda?.toString() === n2.toString()) ||
    (n2.valor === "!" && n2.esquerda?.toString() === n1.toString())
  )
}

// --- Logic Laws ---

function deMorgan(node: ExprNode): ExprNode | null {
  if (node.valor === "!" && node.esquerda && (node.esquerda.valor === "&" || node.esquerda.valor === "|")) {
    const inner = node.esquerda
    const newOp = inner.valor === "&" ? "|" : "&"
    return new ExprNode(newOp, new ExprNode("!", inner.esquerda), new ExprNode("!", inner.direita))
  }
  return null
}

function identity(node: ExprNode): ExprNode | null {
  if (node.valor === "&") {
    if (node.esquerda?.toString() === "1") return node.direita
    if (node.direita?.toString() === "1") return node.esquerda
  } else if (node.valor === "|") {
    if (node.esquerda?.toString() === "0") return node.direita
    if (node.direita?.toString() === "0") return node.esquerda
  }
  return null
}

function nullLaw(node: ExprNode): ExprNode | null {
  if (node.valor === "&") {
    if (node.esquerda?.toString() === "0" || node.direita?.toString() === "0") {
      return new ExprNode("0")
    }
  } else if (node.valor === "|") {
    if (node.esquerda?.toString() === "1" || node.direita?.toString() === "1") {
      return new ExprNode("1")
    }
  }
  return null
}

function idempotent(node: ExprNode): ExprNode | null {
  if ((node.valor === "&" || node.valor === "|") && node.esquerda?.toString() === node.direita?.toString()) {
    return node.esquerda
  }
  return null
}

function inverse(node: ExprNode): ExprNode | null {
  if (node.esquerda && node.direita && areInverses(node.esquerda, node.direita)) {
    if (node.valor === "&") return new ExprNode("0")
    if (node.valor === "|") return new ExprNode("1")
  }
  return null
}

function absorption(node: ExprNode): ExprNode | null {
  if (node.valor === "&" && node.direita?.valor === "|") {
    if (
      node.esquerda?.toString() === node.direita.esquerda?.toString() ||
      node.esquerda?.toString() === node.direita.direita?.toString()
    )
      return node.esquerda
  }
  if (node.valor === "&" && node.esquerda?.valor === "|") {
    if (
      node.direita?.toString() === node.esquerda.esquerda?.toString() ||
      node.direita?.toString() === node.esquerda.direita?.toString()
    )
      return node.direita
  }
  if (node.valor === "|" && node.direita?.valor === "&") {
    if (
      node.esquerda?.toString() === node.direita.esquerda?.toString() ||
      node.esquerda?.toString() === node.direita.direita?.toString()
    )
      return node.esquerda
  }
  if (node.valor === "|" && node.esquerda?.valor === "&") {
    if (
      node.direita?.toString() === node.esquerda.esquerda?.toString() ||
      node.direita?.toString() === node.esquerda.direita?.toString()
    )
      return node.direita
  }
  return null
}

function associative(node: ExprNode): ExprNode | null {
  if ((node.valor === "&" || node.valor === "|") && node.esquerda?.valor === node.valor) {
    const op = node.valor
    const a = node.esquerda.esquerda
    const b = node.esquerda.direita
    const c = node.direita
    return new ExprNode(op, a, new ExprNode(op, b, c))
  }
  return null
}

function commutative(node: ExprNode): ExprNode | null {
  if (
    (node.valor === "&" || node.valor === "|") &&
    node.esquerda &&
    node.direita &&
    node.direita.toString() < node.esquerda.toString()
  ) {
    return new ExprNode(node.valor, node.direita, node.esquerda)
  }
  return null
}

function distributive(node: ExprNode): ExprNode | null {
  if (
    node.valor === "&" &&
    node.esquerda?.valor === "|" &&
    node.direita?.valor === "|"
  ) {
    const a = node.esquerda.esquerda
    const b = node.esquerda.direita
    const c = node.direita.esquerda
    const d = node.direita.direita

    let common: ExprNode | null = null
    let o1: ExprNode | null = null
    let o2: ExprNode | null = null

    if (a?.toString() === c?.toString()) { common = a; o1 = b; o2 = d }
    else if (a?.toString() === d?.toString()) { common = a; o1 = b; o2 = c }
    else if (b?.toString() === c?.toString()) { common = b; o1 = a; o2 = d }
    else if (b?.toString() === d?.toString()) { common = b; o1 = a; o2 = c }

    if (common && o1 && o2) {
      return new ExprNode("|", common, new ExprNode("&", o1, o2))
    }
  }
  return null
}

interface LawDef {
  name: string
  apply: (node: ExprNode) => ExprNode | null
}

const laws: LawDef[] = [
  { name: "Nula", apply: nullLaw },
  { name: "Inversa", apply: inverse },
  { name: "Idempotencia", apply: idempotent },
  { name: "Identidade", apply: identity },
  { name: "Absorcao", apply: absorption },
  { name: "De Morgan", apply: deMorgan },
  { name: "Associativa", apply: associative },
  { name: "Distributiva", apply: distributive },
  { name: "Comutativa", apply: commutative },
]

function applyLawsRecursive(node: ExprNode | null, steps: SimplificationStep[]): ExprNode | null {
  if (!node) return null

  // Simplify children first
  if (node.esquerda) node.esquerda = applyLawsRecursive(node.esquerda, steps)
  if (node.direita) node.direita = applyLawsRecursive(node.direita, steps)

  const originalStr = node.toString()

  for (const law of laws) {
    const result = law.apply(node)
    if (result) {
      steps.push({
        law: law.name,
        before: originalStr,
        after: result.toString(),
      })
      return applyLawsRecursive(result, steps)
    }
  }

  return node
}

export function simplify(expression: string): { result: string; steps: SimplificationStep[] } {
  const steps: SimplificationStep[] = []

  // Normalize: replace boolean algebra operators to logical
  let normalizedExpr = expression.replace(/\+/g, "|").replace(/\*/g, "&").replace(/~/g, "!")

  let tree = buildTree(normalizedExpr)
  let maxIterations = 50
  let iteration = 0

  while (iteration < maxIterations) {
    const previousStr = tree.toString()
    tree = applyLawsRecursive(tree, steps)!
    if (tree.toString() === previousStr) break
    iteration++
  }

  return { result: tree.toString(), steps }
}
