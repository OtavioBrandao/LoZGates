// Interactive Simplifier - User applies laws manually
// Ported from Python simplificador_interativo.py

export class ISNode {
  valor: string
  esquerda: ISNode | null
  direita: ISNode | null

  constructor(valor: string, esquerda: ISNode | null = null, direita: ISNode | null = null) {
    this.valor = valor
    this.esquerda = esquerda
    this.direita = direita
  }

  toString(): string {
    if (this.valor === "*" || this.valor === "+") {
      return `(${this.esquerda}${this.valor}${this.direita})`
    } else if (this.valor === "~") {
      return `~${this.esquerda}`
    }
    return this.valor
  }

  getSize(): number {
    let size = 1
    if (this.esquerda) size += this.esquerda.getSize()
    if (this.direita) size += this.direita.getSize()
    return size
  }

  clone(): ISNode {
    return new ISNode(
      this.valor,
      this.esquerda ? this.esquerda.clone() : null,
      this.direita ? this.direita.clone() : null
    )
  }
}

export function buildISTree(expr: string): ISNode {
  expr = expr.replace(/\s/g, "")

  function parseOr(s: string): ISNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      const c = s[i]
      if (c === ")") depth++
      else if (c === "(") depth--
      else if (c === "+" && depth === 0) {
        return new ISNode("+", parseOr(s.slice(0, i)), parseAnd(s.slice(i + 1)))
      }
    }
    return parseAnd(s)
  }

  function parseAnd(s: string): ISNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      const c = s[i]
      if (c === ")") depth++
      else if (c === "(") depth--
      else if (c === "*" && depth === 0) {
        return new ISNode("*", parseAnd(s.slice(0, i)), parseNot(s.slice(i + 1)))
      }
    }
    return parseNot(s)
  }

  function parseNot(s: string): ISNode {
    if (s.startsWith("~")) {
      return new ISNode("~", parseOr(s.slice(1)))
    } else if (s.startsWith("(") && s.endsWith(")")) {
      return parseOr(s.slice(1, -1))
    }
    return new ISNode(s)
  }

  return parseOr(expr)
}

// --- Verification functions ---

function areInverses(n1: ISNode | null, n2: ISNode | null): boolean {
  if (!n1 || !n2) return false
  return (
    (n1.valor === "~" && n1.esquerda?.toString() === n2.toString()) ||
    (n2.valor === "~" && n2.esquerda?.toString() === n1.toString())
  )
}

function canDeMorgan(node: ISNode | null): boolean {
  return !!node && node.valor === "~" && !!node.esquerda && (node.esquerda.valor === "*" || node.esquerda.valor === "+")
}

function canIdentity(node: ISNode | null): boolean {
  if (!node || !node.esquerda || !node.direita) return false
  if (node.valor === "*") return node.esquerda.toString() === "1" || node.direita.toString() === "1"
  if (node.valor === "+") return node.esquerda.toString() === "0" || node.direita.toString() === "0"
  return false
}

function canNull(node: ISNode | null): boolean {
  if (!node || !node.esquerda || !node.direita) return false
  if (node.valor === "*") return node.esquerda.toString() === "0" || node.direita.toString() === "0"
  if (node.valor === "+") return node.esquerda.toString() === "1" || node.direita.toString() === "1"
  return false
}

function canIdempotent(node: ISNode | null): boolean {
  return (
    !!node &&
    (node.valor === "*" || node.valor === "+") &&
    !!node.esquerda &&
    !!node.direita &&
    node.esquerda.toString() === node.direita.toString()
  )
}

function canInverse(node: ISNode | null): boolean {
  return (
    !!node &&
    (node.valor === "*" || node.valor === "+") &&
    !!node.esquerda &&
    !!node.direita &&
    areInverses(node.esquerda, node.direita)
  )
}

function canAbsorption(node: ISNode | null): boolean {
  if (!node || !node.esquerda || !node.direita) return false
  if (node.valor === "*" && node.direita?.valor === "+") {
    if (node.esquerda.toString() === node.direita.esquerda?.toString() || node.esquerda.toString() === node.direita.direita?.toString()) return true
  }
  if (node.valor === "*" && node.esquerda?.valor === "+") {
    if (node.direita.toString() === node.esquerda.esquerda?.toString() || node.direita.toString() === node.esquerda.direita?.toString()) return true
  }
  if (node.valor === "+" && node.direita?.valor === "*") {
    if (node.esquerda.toString() === node.direita.esquerda?.toString() || node.esquerda.toString() === node.direita.direita?.toString()) return true
  }
  if (node.valor === "+" && node.esquerda?.valor === "*") {
    if (node.direita.toString() === node.esquerda.esquerda?.toString() || node.direita.toString() === node.esquerda.direita?.toString()) return true
  }
  return false
}

function canDistributive(node: ISNode | null): boolean {
  if (!node) return false
  if (node.valor === "+" && node.direita?.valor === "*") return true
  if (node.valor === "+" && node.esquerda?.valor === "*") return true
  if (node.valor === "*" && node.direita?.valor === "+") return true
  if (node.valor === "*" && node.esquerda?.valor === "+") return true
  if (node.valor === "*" && node.esquerda?.valor === "+" && node.direita?.valor === "+") {
    const a = node.esquerda.esquerda
    const b = node.esquerda.direita
    const c = node.direita.esquerda
    const d = node.direita.direita
    if ([a, b].some((x) => [c, d].some((y) => x?.toString() === y?.toString()))) return true
  }
  return false
}

function canAssociative(node: ISNode | null): boolean {
  if (!node) return false
  if ((node.valor === "*" || node.valor === "+") && node.esquerda?.valor === node.valor) return true
  if ((node.valor === "*" || node.valor === "+") && node.direita?.valor === node.valor) return true
  return false
}

function canCommutative(node: ISNode | null): boolean {
  if (!node || !node.esquerda || !node.direita) return false
  return (node.valor === "*" || node.valor === "+") && node.direita.toString() < node.esquerda.toString()
}

// --- Law application functions ---

function applyDeMorgan(node: ISNode): ISNode {
  const inner = node.esquerda!
  const newOp = inner.valor === "*" ? "+" : "*"
  return new ISNode(newOp, new ISNode("~", inner.esquerda), new ISNode("~", inner.direita))
}

function applyIdentity(node: ISNode): ISNode {
  if (node.valor === "*") return node.esquerda?.toString() === "1" ? node.direita! : node.esquerda!
  return node.esquerda?.toString() === "0" ? node.direita! : node.esquerda!
}

function applyNull(node: ISNode): ISNode {
  return node.valor === "*" ? new ISNode("0") : new ISNode("1")
}

function applyIdempotent(node: ISNode): ISNode {
  return node.esquerda!
}

function applyInverse(node: ISNode): ISNode {
  return node.valor === "*" ? new ISNode("0") : new ISNode("1")
}

function applyAbsorption(node: ISNode): ISNode {
  if (node.valor === "*" && node.direita?.valor === "+") return node.esquerda!
  if (node.valor === "*" && node.esquerda?.valor === "+") return node.direita!
  if (node.valor === "+" && node.direita?.valor === "*") return node.esquerda!
  if (node.valor === "+" && node.esquerda?.valor === "*") return node.direita!
  return node
}

function applyDistributive(node: ISNode): ISNode {
  if (node.valor === "*" && node.esquerda?.valor === "+" && node.direita?.valor === "+") {
    const a = node.esquerda.esquerda
    const b = node.esquerda.direita
    const c = node.direita.esquerda
    const d = node.direita.direita
    let common: ISNode | null = null
    let o1: ISNode | null = null
    let o2: ISNode | null = null
    if (a?.toString() === c?.toString()) { common = a; o1 = b; o2 = d }
    else if (a?.toString() === d?.toString()) { common = a; o1 = b; o2 = c }
    else if (b?.toString() === c?.toString()) { common = b; o1 = a; o2 = d }
    else if (b?.toString() === d?.toString()) { common = b; o1 = a; o2 = c }
    if (common && o1 && o2) return new ISNode("+", common, new ISNode("*", o1, o2))
  }
  if (node.valor === "*") {
    if (node.direita?.valor === "+") {
      const a = node.esquerda!
      const b = node.direita.esquerda!
      const c = node.direita.direita!
      return new ISNode("+", new ISNode("*", a, b), new ISNode("*", a, c))
    }
    if (node.esquerda?.valor === "+") {
      const a = node.direita!
      const b = node.esquerda.esquerda!
      const c = node.esquerda.direita!
      return new ISNode("+", new ISNode("*", a, b), new ISNode("*", a, c))
    }
  }
  return node
}

function applyAssociative(node: ISNode): ISNode {
  const op = node.valor
  if (node.esquerda?.valor === op) {
    const a = node.esquerda.esquerda!
    const b = node.esquerda.direita!
    const c = node.direita!
    return new ISNode(op, a, new ISNode(op, b, c))
  }
  if (node.direita?.valor === op) {
    const a = node.esquerda!
    const b = node.direita.esquerda!
    const c = node.direita.direita!
    return new ISNode(op, new ISNode(op, a, b), c)
  }
  return node
}

function applyCommutative(node: ISNode): ISNode {
  return new ISNode(node.valor, node.direita, node.esquerda)
}

// --- Public interface ---

export interface LogicLaw {
  name: string
  description: string
  canApply: (node: ISNode | null) => boolean
  apply: (node: ISNode) => ISNode
}

export const LOGIC_LAWS: LogicLaw[] = [
  { name: "Inversa", description: "A * ~A = 0", canApply: canInverse, apply: applyInverse },
  { name: "Nula", description: "A * 0 = 0", canApply: canNull, apply: applyNull },
  { name: "Identidade", description: "A * 1 = A", canApply: canIdentity, apply: applyIdentity },
  { name: "Idempotente", description: "A * A = A", canApply: canIdempotent, apply: applyIdempotent },
  { name: "Absorcao", description: "A * (A+B) = A", canApply: canAbsorption, apply: applyAbsorption },
  { name: "De Morgan", description: "~(A*B) = ~A+~B", canApply: canDeMorgan, apply: applyDeMorgan },
  { name: "Distributiva", description: "(A+B)*(A+C) = A+(B*C)", canApply: canDistributive, apply: applyDistributive },
  { name: "Associativa", description: "(A*B)*C = A*(B*C)", canApply: canAssociative, apply: applyAssociative },
  { name: "Comutativa", description: "B*A = A*B", canApply: canCommutative, apply: applyCommutative },
]

export interface NodeInfo {
  node: ISNode
  parent: ISNode | null
  branch: "esquerda" | "direita" | null
  applicableLaws: boolean[]
}

export function collectAllNodes(node: ISNode | null, parent: ISNode | null = null, branch: "esquerda" | "direita" | null = null): NodeInfo[] {
  const collected: NodeInfo[] = []
  if (!node) return collected

  if (node.esquerda || node.direita) {
    collected.push({
      node,
      parent,
      branch,
      applicableLaws: LOGIC_LAWS.map((law) => law.canApply(node)),
    })
  }

  collected.push(...collectAllNodes(node.esquerda, node, "esquerda"))
  collected.push(...collectAllNodes(node.direita, node, "direita"))

  return collected
}

export function applyLawAndReplace(
  treeRoot: ISNode,
  nodeInfo: NodeInfo,
  lawIndex: number
): { newTree: ISNode; success: boolean } {
  const law = LOGIC_LAWS[lawIndex]
  if (!law.canApply(nodeInfo.node)) return { newTree: treeRoot, success: false }

  const newNode = law.apply(nodeInfo.node)
  if (nodeInfo.parent === null) return { newTree: newNode, success: true }

  if (nodeInfo.branch === "esquerda") nodeInfo.parent.esquerda = newNode
  else if (nodeInfo.branch === "direita") nodeInfo.parent.direita = newNode

  return { newTree: treeRoot, success: true }
}
