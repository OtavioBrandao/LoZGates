// Porte direto de normalizer.py - Normaliza expressoes para comparacao estrutural
import { checkEquivalence } from "./evaluator"

interface ExprNode {
  value: string
  left: ExprNode | null
  right: ExprNode | null
}

function createExprNode(value: string, left: ExprNode | null = null, right: ExprNode | null = null): ExprNode {
  return { value, left, right }
}

function exprNodeToString(node: ExprNode | null): string {
  if (!node) return ""
  if (node.value === "&" || node.value === "|" || node.value === "*" || node.value === "+" || node.value === ">" || node.value === "<>") {
    return `(${exprNodeToString(node.left)}${node.value}${exprNodeToString(node.right)})`
  } else if (node.value === "!" || node.value === "~") {
    return `${node.value}${exprNodeToString(node.left)}`
  }
  return node.value
}

function buildExpressionTree(expr: string): ExprNode {
  expr = expr.replace(/\s/g, "").toUpperCase()
  expr = expr.replace(/->/g, ">").replace(/<->/g, "<>")
  expr = expr.replace(/\*/g, "&").replace(/\+/g, "|").replace(/~/g, "!")

  function parseBiImplication(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (depth === 0 && i > 0 && s.slice(i - 1, i + 1) === "<>") {
        return createExprNode("<>", parseBiImplication(s.slice(0, i - 1)), parseImplication(s.slice(i + 1)))
      }
    }
    return parseImplication(s)
  }

  function parseImplication(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === ">" && depth === 0) {
        return createExprNode(">", parseImplication(s.slice(0, i)), parseOr(s.slice(i + 1)))
      }
    }
    return parseOr(s)
  }

  function parseOr(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "|" && depth === 0) {
        return createExprNode("|", parseOr(s.slice(0, i)), parseAnd(s.slice(i + 1)))
      }
    }
    return parseAnd(s)
  }

  function parseAnd(s: string): ExprNode {
    let depth = 0
    for (let i = s.length - 1; i >= 0; i--) {
      if (s[i] === ")") depth++
      else if (s[i] === "(") depth--
      else if (s[i] === "&" && depth === 0) {
        return createExprNode("&", parseAnd(s.slice(0, i)), parseNot(s.slice(i + 1)))
      }
    }
    return parseNot(s)
  }

  function parseNot(s: string): ExprNode {
    if (s.startsWith("!")) return createExprNode("!", parseNot(s.slice(1)))
    if (s.startsWith("(") && s.endsWith(")")) return parseBiImplication(s.slice(1, -1))
    return createExprNode(s)
  }

  return parseBiImplication(expr)
}

function normalizeTreeVariables(tree: ExprNode, varMap: Map<string, string> = new Map(), counter = { val: 0 }): ExprNode {
  if (!tree.left && !tree.right) {
    if (/^[A-Z]$/.test(tree.value) && !varMap.has(tree.value)) {
      varMap.set(tree.value, String.fromCharCode(65 + counter.val))
      counter.val++
    }
    const mapped = varMap.get(tree.value)
    return mapped ? createExprNode(mapped) : tree
  }
  const left = tree.left ? normalizeTreeVariables(tree.left, varMap, counter) : null
  const right = tree.right ? normalizeTreeVariables(tree.right, varMap, counter) : null
  return createExprNode(tree.value, left, right)
}

function treeToCanonicalString(tree: ExprNode): string {
  if (!tree.left && !tree.right) return tree.value
  if (tree.value === "!") {
    const operand = treeToCanonicalString(tree.left!)
    if (tree.left && ["&", "|", ">", "<>"].includes(tree.left.value)) return `!(${operand})`
    return `!${operand}`
  }
  const precedence: Record<string, number> = { "&": 1, "|": 2, ">": 3, "<>": 4 }
  let leftStr = treeToCanonicalString(tree.left!)
  let rightStr = treeToCanonicalString(tree.right!)
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
    const tree = buildExpressionTree(expression)
    const normalized = normalizeTreeVariables(tree)
    return treeToCanonicalString(normalized)
  } catch {
    return expression.trim().toUpperCase().replace(/\s/g, "")
  }
}

export function expressionsAreStructurallyEquivalent(expr1: string, expr2: string): boolean {
  try {
    const norm1 = normalizeForComparison(expr1)
    const norm2 = normalizeForComparison(expr2)
    return norm1 === norm2
  } catch {
    return false
  }
}

// Verifica se duas expressoes sao logicamente equivalentes (por forca bruta na tabela verdade)
export function expressionsAreLogicallyEquivalent(expr1: string, expr2: string): boolean {
  return checkEquivalence(expr1, expr2).equivalent
}
