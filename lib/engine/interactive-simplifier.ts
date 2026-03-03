// Porte direto de simplificador_interativo.py - Simplificacao interativa com escolha do usuario
import type { SimplifierNode, LogicLaw, InteractiveStepInfo } from "./types"

function createNode(valor: string, esquerda: SimplifierNode | null = null, direita: SimplifierNode | null = null): SimplifierNode {
  return { valor, esquerda, direita }
}

export function nodeToStr(node: SimplifierNode | null): string {
  if (!node) return ""
  if (node.valor === "*" || node.valor === "+") {
    return `(${nodeToStr(node.esquerda)}${node.valor}${nodeToStr(node.direita)})`
  } else if (node.valor === "~") {
    return `~${nodeToStr(node.esquerda)}`
  }
  return node.valor
}

function getNodeSize(node: SimplifierNode | null): number {
  if (!node) return 0
  return 1 + getNodeSize(node.esquerda) + getNodeSize(node.direita)
}

export function cloneNode(node: SimplifierNode | null): SimplifierNode | null {
  if (!node) return null
  return { valor: node.valor, esquerda: cloneNode(node.esquerda), direita: cloneNode(node.direita) }
}

export function buildInteractiveTree(expr: string): SimplifierNode {
  expr = expr.replace(/\s/g, "")

  function parseOr(s: string): SimplifierNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "+" && depth === 0) {
        return createNode("+", parseOr(s.slice(0, i)), parseAnd(s.slice(i + 1)))
      }
    }
    return parseAnd(s)
  }

  function parseAnd(s: string): SimplifierNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "*" && depth === 0) {
        return createNode("*", parseAnd(s.slice(0, i)), parseNot(s.slice(i + 1)))
      }
    }
    return parseNot(s)
  }

  function parseNot(s: string): SimplifierNode {
    if (s.startsWith("~")) return createNode("~", parseOr(s.slice(1)))
    if (s.startsWith("(") && s.endsWith(")")) return parseOr(s.slice(1, -1))
    return createNode(s)
  }

  return parseOr(expr)
}

// --- Verificacoes ---
function areInverses(n1: SimplifierNode | null, n2: SimplifierNode | null): boolean {
  if (!n1 || !n2) return false
  return (
    (n1.valor === "~" && nodeToStr(n1.esquerda) === nodeToStr(n2)) ||
    (n2.valor === "~" && nodeToStr(n2.esquerda) === nodeToStr(n1))
  )
}

function canDeMorgan(node: SimplifierNode): boolean {
  return node.valor === "~" && !!node.esquerda && (node.esquerda.valor === "*" || node.esquerda.valor === "+")
}
function canIdentity(node: SimplifierNode): boolean {
  if (!node.esquerda || !node.direita) return false
  if (node.valor === "*") return nodeToStr(node.esquerda) === "1" || nodeToStr(node.direita) === "1"
  if (node.valor === "+") return nodeToStr(node.esquerda) === "0" || nodeToStr(node.direita) === "0"
  return false
}
function canNull(node: SimplifierNode): boolean {
  if (!node.esquerda || !node.direita) return false
  if (node.valor === "*") return nodeToStr(node.esquerda) === "0" || nodeToStr(node.direita) === "0"
  if (node.valor === "+") return nodeToStr(node.esquerda) === "1" || nodeToStr(node.direita) === "1"
  return false
}
function canIdempotent(node: SimplifierNode): boolean {
  return (node.valor === "*" || node.valor === "+") && !!node.esquerda && !!node.direita && nodeToStr(node.esquerda) === nodeToStr(node.direita)
}
function canInverse(node: SimplifierNode): boolean {
  return (node.valor === "*" || node.valor === "+") && !!node.esquerda && !!node.direita && areInverses(node.esquerda, node.direita)
}
function canAbsorption(node: SimplifierNode): boolean {
  if (!node.esquerda || !node.direita) return false
  const es = nodeToStr(node.esquerda), ds = nodeToStr(node.direita)
  if (node.valor === "*" && node.direita.valor === "+") {
    if (es === nodeToStr(node.direita.esquerda) || es === nodeToStr(node.direita.direita)) return true
  }
  if (node.valor === "*" && node.esquerda.valor === "+") {
    if (ds === nodeToStr(node.esquerda.esquerda) || ds === nodeToStr(node.esquerda.direita)) return true
  }
  if (node.valor === "+" && node.direita.valor === "*") {
    if (es === nodeToStr(node.direita.esquerda) || es === nodeToStr(node.direita.direita)) return true
  }
  if (node.valor === "+" && node.esquerda.valor === "*") {
    if (ds === nodeToStr(node.esquerda.esquerda) || ds === nodeToStr(node.esquerda.direita)) return true
  }
  return false
}
function canDistributive(node: SimplifierNode): boolean {
  if (node.valor === "+" && node.direita?.valor === "*") return true
  if (node.valor === "+" && node.esquerda?.valor === "*") return true
  if (node.valor === "*" && node.direita?.valor === "+") return true
  if (node.valor === "*" && node.esquerda?.valor === "+") return true
  if (node.valor === "*" && node.esquerda?.valor === "+" && node.direita?.valor === "+") {
    const a = nodeToStr(node.esquerda.esquerda), b = nodeToStr(node.esquerda.direita)
    const c = nodeToStr(node.direita.esquerda), d = nodeToStr(node.direita.direita)
    if ([a, b].some((x) => [c, d].some((y) => x === y))) return true
  }
  return false
}
function canAssociative(node: SimplifierNode): boolean {
  if ((node.valor === "*" || node.valor === "+") && node.esquerda?.valor === node.valor) return true
  if ((node.valor === "*" || node.valor === "+") && node.direita?.valor === node.valor) return true
  return false
}
function canCommutative(node: SimplifierNode): boolean {
  if (!node.esquerda || !node.direita) return false
  return (node.valor === "*" || node.valor === "+") && nodeToStr(node.direita) < nodeToStr(node.esquerda)
}

// --- Aplicacoes ---
function applyDeMorgan(node: SimplifierNode): SimplifierNode {
  const inner = node.esquerda!
  const newOp = inner.valor === "*" ? "+" : "*"
  return createNode(newOp, createNode("~", cloneNode(inner.esquerda)), createNode("~", cloneNode(inner.direita)))
}
function applyIdentity(node: SimplifierNode): SimplifierNode {
  if (node.valor === "*") return nodeToStr(node.esquerda) === "1" ? cloneNode(node.direita)! : cloneNode(node.esquerda)!
  return nodeToStr(node.esquerda) === "0" ? cloneNode(node.direita)! : cloneNode(node.esquerda)!
}
function applyNull(node: SimplifierNode): SimplifierNode {
  return node.valor === "*" ? createNode("0") : createNode("1")
}
function applyIdempotent(node: SimplifierNode): SimplifierNode {
  return cloneNode(node.esquerda)!
}
function applyInverse(node: SimplifierNode): SimplifierNode {
  return node.valor === "*" ? createNode("0") : createNode("1")
}
function applyAbsorption(node: SimplifierNode): SimplifierNode {
  if (node.valor === "*" && node.direita?.valor === "+") return cloneNode(node.esquerda)!
  if (node.valor === "*" && node.esquerda?.valor === "+") return cloneNode(node.direita)!
  if (node.valor === "+" && node.direita?.valor === "*") return cloneNode(node.esquerda)!
  if (node.valor === "+" && node.esquerda?.valor === "*") return cloneNode(node.direita)!
  return node
}
function applyDistributive(node: SimplifierNode): SimplifierNode {
  if (node.valor === "*" && node.esquerda?.valor === "+" && node.direita?.valor === "+") {
    const a = node.esquerda.esquerda, b = node.esquerda.direita
    const c = node.direita.esquerda, d = node.direita.direita
    const as_ = nodeToStr(a), bs = nodeToStr(b), cs = nodeToStr(c), ds_ = nodeToStr(d)
    let common: SimplifierNode | null = null, o1: SimplifierNode | null = null, o2: SimplifierNode | null = null
    if (as_ === cs) { common = a; o1 = b; o2 = d }
    else if (as_ === ds_) { common = a; o1 = b; o2 = c }
    else if (bs === cs) { common = b; o1 = a; o2 = d }
    else if (bs === ds_) { common = b; o1 = a; o2 = c }
    if (common) return createNode("+", cloneNode(common)!, createNode("*", cloneNode(o1)!, cloneNode(o2)!))
  }
  if (node.valor === "*") {
    if (node.direita?.valor === "+") {
      const a = node.esquerda, b = node.direita.esquerda, c = node.direita.direita
      return createNode("+", createNode("*", cloneNode(a)!, cloneNode(b)!), createNode("*", cloneNode(a)!, cloneNode(c)!))
    }
    if (node.esquerda?.valor === "+") {
      const a = node.direita, b = node.esquerda.esquerda, c = node.esquerda.direita
      return createNode("+", createNode("*", cloneNode(a)!, cloneNode(b)!), createNode("*", cloneNode(a)!, cloneNode(c)!))
    }
  }
  return node
}
function applyAssociative(node: SimplifierNode): SimplifierNode {
  const op = node.valor
  if (node.esquerda?.valor === op) {
    const a = node.esquerda.esquerda, b = node.esquerda.direita, c = node.direita
    return createNode(op, cloneNode(a)!, createNode(op, cloneNode(b)!, cloneNode(c)!))
  }
  if (node.direita?.valor === op) {
    const a = node.esquerda, b = node.direita.esquerda, c = node.direita.direita
    return createNode(op, createNode(op, cloneNode(a)!, cloneNode(b)!), cloneNode(c)!)
  }
  return node
}
function applyCommutative(node: SimplifierNode): SimplifierNode {
  return createNode(node.valor, cloneNode(node.direita)!, cloneNode(node.esquerda)!)
}

// --- Estrutura de leis ---
export const LOGIC_LAWS: LogicLaw[] = [
  { name: "Inversa (A * ~A = 0)", check: canInverse, apply: applyInverse },
  { name: "Nula (A * 0 = 0)", check: canNull, apply: applyNull },
  { name: "Identidade (A * 1 = A)", check: canIdentity, apply: applyIdentity },
  { name: "Idempotente (A * A = A)", check: canIdempotent, apply: applyIdempotent },
  { name: "Absorcao (A * (A+B) = A)", check: canAbsorption, apply: applyAbsorption },
  { name: "De Morgan (~(A*B) = ~A+~B)", check: canDeMorgan, apply: applyDeMorgan },
  { name: "Distributiva ((A+B)*(A+C) = A+(B*C))", check: canDistributive, apply: applyDistributive },
  { name: "Associativa ((A*B)*C = A*(B*C))", check: canAssociative, apply: applyAssociative },
  { name: "Comutativa (B*A = A*B)", check: canCommutative, apply: applyCommutative },
]

// --- Coleta de nos ---
export function collectAllNodes(
  node: SimplifierNode | null,
  parent: SimplifierNode | null = null,
  branch: "esquerda" | "direita" | null = null
): InteractiveStepInfo[] {
  if (!node) return []
  const collected: InteractiveStepInfo[] = []

  if (node.esquerda || node.direita) {
    collected.push({
      currentNode: node,
      parent,
      branch,
      applicableLaws: LOGIC_LAWS.map((law) => law.check(node)),
    })
  }

  collected.push(...collectAllNodes(node.esquerda, node, "esquerda"))
  collected.push(...collectAllNodes(node.direita, node, "direita"))

  return collected
}

export function findNextStep(root: SimplifierNode, skipNodes: Set<string> = new Set()): InteractiveStepInfo | null {
  const allNodes = collectAllNodes(root)
  const filtered = allNodes.filter((info) => !skipNodes.has(nodeToStr(info.currentNode)))
  filtered.sort((a, b) => {
    const sizeA = getNodeSize(a.currentNode)
    const sizeB = getNodeSize(b.currentNode)
    if (sizeA !== sizeB) return sizeA - sizeB
    return nodeToStr(a.currentNode).localeCompare(nodeToStr(b.currentNode))
  })
  return filtered.length > 0 ? filtered[0] : null
}

export function applyLawAndReplace(
  root: SimplifierNode,
  stepInfo: InteractiveStepInfo,
  lawIndex: number
): { newRoot: SimplifierNode; success: boolean } {
  const law = LOGIC_LAWS[lawIndex]
  const target = stepInfo.currentNode

  if (!law.check(target)) return { newRoot: root, success: false }

  const newNode = law.apply(target)

  if (!stepInfo.parent) {
    return { newRoot: newNode, success: true }
  }

  if (stepInfo.branch === "esquerda") {
    stepInfo.parent.esquerda = newNode
  } else if (stepInfo.branch === "direita") {
    stepInfo.parent.direita = newNode
  }

  return { newRoot: root, success: true }
}
