// Porte direto de equivalencia.py - Avaliador universal de expressoes logicas
import type { EquivalenceResult, Token } from "./types"

function extractVariables(...expressions: string[]): string[] {
  const allVars = new Set<string>()
  for (const expr of expressions) {
    const clean = expr.replace(/\s/g, "")
    const vars = clean.match(/[A-Z]/g)
    if (vars) vars.forEach((v) => allVars.add(v))
  }
  return Array.from(allVars).sort()
}

function tokenize(expression: string): Token[] {
  const tokens: Token[] = []
  let i = 0
  const expr = expression.replace(/\s/g, "")

  while (i < expr.length) {
    if (expr.slice(i, i + 2) === "<>") {
      tokens.push("<>")
      i += 2
    } else if (expr.slice(i, i + 3) === "<->") {
      tokens.push("<>")
      i += 3
    } else if (expr.slice(i, i + 2) === "->") {
      tokens.push(">")
      i += 2
    } else if ("()&|>!=".includes(expr[i])) {
      tokens.push(expr[i])
      i++
    } else if (/[a-zA-Z]/.test(expr[i])) {
      tokens.push(expr[i])
      i++
    } else if (/\d/.test(expr[i])) {
      tokens.push(expr[i])
      i++
    } else {
      i++
    }
  }
  return tokens
}

function evaluateToken(token: Token, values: Record<string, boolean>): boolean {
  if (typeof token === "boolean") return token
  if (token === "1") return true
  if (token === "0") return false
  if (typeof token === "string" && token in values) return values[token]
  return false
}

function processParentheses(tokens: Token[], values: Record<string, boolean>): Token[] {
  const startIdx = tokens.indexOf("(")
  let level = 1
  let end = startIdx + 1
  while (end < tokens.length && level > 0) {
    if (tokens[end] === "(") level++
    else if (tokens[end] === ")") level--
    end++
  }
  const subTokens = tokens.slice(startIdx + 1, end - 1)
  const result = evaluateExpression(subTokens, values)
  return [...tokens.slice(0, startIdx), result, ...tokens.slice(end)]
}

function processNegation(tokens: Token[], values: Record<string, boolean>): Token[] {
  const result: Token[] = []
  let i = 0
  while (i < tokens.length) {
    if (tokens[i] === "!" && i + 1 < tokens.length) {
      const value = evaluateToken(tokens[i + 1], values)
      result.push(!value)
      i += 2
    } else {
      result.push(tokens[i])
      i++
    }
  }
  return result
}

const OPERATORS: Record<string, (a: boolean, b: boolean) => boolean> = {
  "&": (a, b) => a && b,
  "|": (a, b) => a || b,
  ">": (a, b) => !a || b,
  "<>": (a, b) => a === b,
  "=": (a, b) => a === b,
}

function processOperator(tokens: Token[], operator: string, values: Record<string, boolean>): Token[] {
  if (operator === ">") {
    const indices: number[] = []
    tokens.forEach((t, i) => {
      if (t === operator) indices.push(i)
    })
    for (const idx of indices.reverse()) {
      if (idx > 0 && idx < tokens.length - 1) {
        const left = evaluateToken(tokens[idx - 1], values)
        const right = evaluateToken(tokens[idx + 1], values)
        const result = OPERATORS[operator](left, right)
        tokens = [...tokens.slice(0, idx - 1), result, ...tokens.slice(idx + 2)]
      }
    }
  } else {
    while (tokens.includes(operator)) {
      const idx = tokens.indexOf(operator)
      if (idx > 0 && idx < tokens.length - 1) {
        const left = evaluateToken(tokens[idx - 1], values)
        const right = evaluateToken(tokens[idx + 1], values)
        const result = OPERATORS[operator](left, right)
        tokens = [...tokens.slice(0, idx - 1), result, ...tokens.slice(idx + 2)]
      } else {
        break
      }
    }
  }
  return tokens
}

function evaluateExpression(tokens: Token[], values: Record<string, boolean>): boolean {
  if (!tokens.length) return false
  if (tokens.length === 1) return evaluateToken(tokens[0], values)

  let t = [...tokens]
  while (t.includes("(")) {
    t = processParentheses(t, values)
  }
  t = processNegation(t, values)
  for (const op of ["<>", ">", "&", "|"]) {
    t = processOperator(t, op, values)
  }
  return typeof t[0] === "boolean" ? t[0] : evaluateToken(t[0], values)
}

export function analyzeExpression(expression: string, values: Record<string, boolean>): boolean {
  const tokens = tokenize(expression)
  return evaluateExpression(tokens, values)
}

export function checkEquivalence(expr1: string, expr2: string): EquivalenceResult {
  const variables = extractVariables(expr1, expr2)
  const totalCombos = Math.pow(2, variables.length)
  const differences: EquivalenceResult["differences"] = []

  for (let i = 0; i < totalCombos; i++) {
    const values: Record<string, boolean> = {}
    variables.forEach((v, idx) => {
      values[v] = Boolean((i >> (variables.length - 1 - idx)) & 1)
    })

    try {
      const r1 = analyzeExpression(expr1, values)
      const r2 = analyzeExpression(expr2, values)
      if (r1 !== r2) {
        differences.push({ values: { ...values }, result1: r1, result2: r2 })
      }
    } catch {
      return { equivalent: false, variables, differences }
    }
  }

  return { equivalent: differences.length === 0, variables, differences }
}

export { extractVariables, tokenize, evaluateExpression }
