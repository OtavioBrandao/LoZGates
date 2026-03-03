// Expression Normalizer for structural comparison
// Ported from Python normalizer.py

class NormNode {
  value: string
  left: NormNode | null
  right: NormNode | null

  constructor(value: string, left: NormNode | null = null, right: NormNode | null = null) {
    this.value = value
    this.left = left
    this.right = right
  }

  equals(other: NormNode | null): boolean {
    if (!other) return false
    return this.value === other.value && (this.left?.equals(other.left) ?? other.left === null) && (this.right?.equals(other.right) ?? other.right === null)
  }

  toString(): string {
    if (["&", "|", "*", "+", ">", "<>"].includes(this.value)) {
      return `(${this.left}${this.value}${this.right})`
    } else if (this.value === "!" || this.value === "~") {
      return `${this.value}${this.left}`
    }
    return this.value
  }
}

function buildNormTree(expr: string): NormNode {
  expr = expr.replace(/\s/g, "").toUpperCase()
  expr = expr.replace(/->/g, ">").replace(/<->/g, "<>")
  expr = expr.replace(/\*/g, "&").replace(/\+/g, "|").replace(/~/g, "!")

  function parseBiImpl(s: string): NormNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (depth === 0 && i > 0 && s.slice(i - 1, i + 1) === "<>") {
        return new NormNode("<>", parseBiImpl(s.slice(0, i - 1)), parseImpl(s.slice(i + 1)))
      }
    }
    return parseImpl(s)
  }

  function parseImpl(s: string): NormNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === ">" && depth === 0) {
        return new NormNode(">", parseImpl(s.slice(0, i)), parseOr(s.slice(i + 1)))
      }
    }
    return parseOr(s)
  }

  function parseOr(s: string): NormNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "|" && depth === 0) {
        return new NormNode("|", parseOr(s.slice(0, i)), parseAnd(s.slice(i + 1)))
      }
    }
    return parseAnd(s)
  }

  function parseAnd(s: string): NormNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "&" && depth === 0) {
        return new NormNode("&", parseAnd(s.slice(0, i)), parseNot(s.slice(i + 1)))
      }
    }
    return parseNot(s)
  }

  function parseNot(s: string): NormNode {
    if (s.startsWith("!")) return new NormNode("!", parseNot(s.slice(1)))
    if (s.startsWith("(") && s.endsWith(")")) return parseBiImpl(s.slice(1, -1))
    return new NormNode(s)
  }

  return parseBiImpl(expr)
}

function normalizeTreeVariables(tree: NormNode, varMap: Map<string, string> = new Map(), counter = { val: 0 }): NormNode {
  if (!tree.left && !tree.right) {
    if (/^[A-Z]$/.test(tree.value) && !varMap.has(tree.value)) {
      varMap.set(tree.value, String.fromCharCode(65 + counter.val))
      counter.val++
    }
    if (varMap.has(tree.value)) return new NormNode(varMap.get(tree.value)!)
    return tree
  }

  const leftNorm = tree.left ? normalizeTreeVariables(tree.left, varMap, counter) : null
  const rightNorm = tree.right ? normalizeTreeVariables(tree.right, varMap, counter) : null
  return new NormNode(tree.value, leftNorm, rightNorm)
}

function treeToCanonical(tree: NormNode): string {
  if (!tree.left && !tree.right) return tree.value

  if (tree.value === "!") {
    const operand = treeToCanonical(tree.left!)
    if (tree.left && ["&", "|", ">", "<>"].includes(tree.left.value)) return `!(${operand})`
    return `!${operand}`
  }

  let leftStr = treeToCanonical(tree.left!)
  let rightStr = treeToCanonical(tree.right!)

  const precedence: Record<string, number> = { "&": 1, "|": 2, ">": 3, "<>": 4 }
  const currentPrec = precedence[tree.value] ?? 999

  if (tree.left && tree.left.value in precedence) {
    if (precedence[tree.left.value] > currentPrec) leftStr = `(${leftStr})`
  }
  if (tree.right && tree.right.value in precedence) {
    const rightPrec = precedence[tree.right.value]
    if (rightPrec > currentPrec) rightStr = `(${rightStr})`
    else if (tree.value === ">" && rightPrec === currentPrec) rightStr = `(${rightStr})`
  }

  return `${leftStr}${tree.value}${rightStr}`
}

export function normalizeForComparison(expression: string): string {
  try {
    const tree = buildNormTree(expression)
    const normalized = normalizeTreeVariables(tree)
    return treeToCanonical(normalized)
  } catch {
    return simpleNormalize(expression)
  }
}

function simpleNormalize(expression: string): string {
  let expr = expression.trim().toUpperCase().replace(/\s/g, "")
  const found: string[] = []
  for (const char of expr) {
    if (/[A-Z]/.test(char) && !found.includes(char)) found.push(char)
  }
  const mapping: Record<string, string> = {}
  found.forEach((v, i) => {
    if (i < 26) mapping[v] = String.fromCharCode(65 + i)
  })
  for (const [orig, norm] of Object.entries(mapping)) {
    expr = expr.split(orig).join(`__${norm}__`)
  }
  expr = expr.replace(/__/g, "")
  return expr
}

export function expressionsAreStructurallyEquivalent(expr1: string, expr2: string): boolean {
  try {
    return normalizeForComparison(expr1) === normalizeForComparison(expr2)
  } catch {
    return false
  }
}
