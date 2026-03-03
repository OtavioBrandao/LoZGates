// Porte direto de converter.py - Converte expressoes logicas proposicionais para algebra booleana
import type { ConversionResult } from "./types"

const LOGICAL_OPERATORS: Record<string, string> = {
  "&": "*",
  "|": "+",
  "!": "~",
}

function eraseExpression(expression: string): string {
  return expression.replace(/\s/g, "").trim()
}

function findLeftOperand(expr: string, pos: number): [string, number] {
  let j = pos - 1
  if (j >= 0 && expr[j] === ")") {
    let count = 1
    j--
    while (j >= 0 && count > 0) {
      if (expr[j] === ")") count++
      else if (expr[j] === "(") count--
      j--
    }
    return [expr.slice(j + 1, pos), j + 1]
  } else {
    let start = j
    if (j > 0 && (expr[j - 1] === "!" || expr[j - 1] === "~")) {
      start = j - 1
    }
    return [expr.slice(start, pos), start]
  }
}

function findRightOperand(expr: string, pos: number): [string, number] {
  let k = pos
  if (k < expr.length && expr[k] === "(") {
    let count = 1
    k++
    const start = k
    while (k < expr.length && count > 0) {
      if (expr[k] === "(") count++
      else if (expr[k] === ")") count--
      k++
    }
    return [expr.slice(start, k - 1), k]
  } else {
    const start = k
    if (k < expr.length && (expr[k] === "!" || expr[k] === "~")) k++
    if (k < expr.length) k++
    return [expr.slice(start, k), k]
  }
}

function replaceBiImplications(expr: string, history: string[]): string {
  let i = 0
  while (i < expr.length) {
    let opSize = 0
    if (i + 2 < expr.length && expr.slice(i, i + 3) === "<->") {
      opSize = 3
    } else if (i + 1 < expr.length && expr.slice(i, i + 2) === "<>") {
      opSize = 2
    }
    if (opSize > 0) {
      const [a, aStart] = findLeftOperand(expr, i)
      const [b, bEnd] = findRightOperand(expr, i + opSize)
      const newExpr = expr.slice(0, aStart) + `((~${a}+${b})*(~${b}+${a}))` + expr.slice(bEnd)
      history.push(`Bi-implicacao: ${expr} -> ${newExpr}`)
      return replaceBiImplications(newExpr, history)
    }
    i++
  }
  return expr
}

function replaceImplications(expr: string, history: string[]): string {
  let i = 0
  while (i < expr.length) {
    let opSize = 0
    if (i + 1 < expr.length && expr.slice(i, i + 2) === "->") {
      opSize = 2
    } else if (expr[i] === ">" && (i === 0 || expr[i - 1] !== "<")) {
      opSize = 1
    }
    if (opSize > 0) {
      const [a, aStart] = findLeftOperand(expr, i)
      const [b, bEnd] = findRightOperand(expr, i + opSize)
      const newExpr = expr.slice(0, aStart) + `(~${a}+${b})` + expr.slice(bEnd)
      history.push(`Implicacao: ${expr} -> ${newExpr}`)
      return replaceImplications(newExpr, history)
    }
    i++
  }
  return expr
}

function replaceBasicOperators(expr: string, history: string[]): string {
  const original = expr
  for (const [logical, algebraic] of Object.entries(LOGICAL_OPERATORS)) {
    expr = expr.split(logical).join(algebraic)
  }
  if (expr !== original) {
    history.push(`Operadores basicos: ${original} -> ${expr}`)
  }
  return expr
}

export function convertToBooleanAlgebra(expression: string): ConversionResult {
  const history: string[] = []
  let expr = eraseExpression(expression)
  history.push(`Original: ${expression}`)

  expr = replaceBiImplications(expr, history)
  expr = replaceImplications(expr, history)
  expr = replaceBasicOperators(expr, history)

  return {
    original: expression,
    converted: expr,
    steps: history,
  }
}

export function validateExpression(expression: string): { valid: boolean; error: string } {
  let count = 0
  for (let i = 0; i < expression.length; i++) {
    if (expression[i] === "(") count++
    else if (expression[i] === ")") {
      count--
      if (count < 0) return { valid: false, error: `Parentese fechado sem abertura na posicao ${i}` }
    }
  }
  if (count !== 0) return { valid: false, error: `Parenteses nao balanceados: ${count} abertos` }
  return { valid: true, error: "" }
}
