// Universal Logic Analyzer
// Ported from Python equivalencia.py

type Values = Record<string, boolean>
type Token = string | boolean

const operators: Record<string, (a: boolean, b?: boolean) => boolean> = {
  "&": (a, b) => a && (b ?? false),
  "|": (a, b) => a || (b ?? false),
  ">": (a, b) => !a || (b ?? false),
  "<>": (a, b) => a === (b ?? false),
  "=": (a, b) => a === (b ?? false),
  "!": (a) => !a,
}

export function extractVariables(...expressions: string[]): string[] {
  const allVars = new Set<string>()
  for (const expr of expressions) {
    const clean = expr.replace(/\s/g, "")
    const vars = clean.match(/[A-Z]/g) || []
    vars.forEach((v) => allVars.add(v))
  }
  return Array.from(allVars).sort()
}

export function tokenize(expression: string): string[] {
  const tokens: string[] = []
  let i = 0
  const expr = expression.replace(/\s/g, "")

  while (i < expr.length) {
    if (expr.slice(i, i + 2) === "<>") {
      tokens.push("<>")
      i += 2
    } else if (expr.slice(i, i + 2) === "->") {
      tokens.push(">")
      i += 2
    } else if ("()&|>!=~".includes(expr[i])) {
      // Treat ~ as !
      tokens.push(expr[i] === "~" ? "!" : expr[i])
      i += 1
    } else if (/[A-Za-z]/.test(expr[i])) {
      tokens.push(expr[i].toUpperCase())
      i += 1
    } else if (/[0-9]/.test(expr[i])) {
      tokens.push(expr[i])
      i += 1
    } else {
      i += 1
    }
  }
  return tokens
}

function evaluateToken(token: Token, values: Values): boolean {
  if (typeof token === "boolean") return token
  if (token === "1") return true
  if (token === "0") return false
  if (typeof token === "string" && token in values) return values[token]
  return false
}

function processParentheses(tokens: Token[], values: Values): Token[] {
  const startIdx = tokens.indexOf("(")
  let level = 1
  let end = startIdx + 1

  while (end < tokens.length && level > 0) {
    if (tokens[end] === "(") level++
    else if (tokens[end] === ")") level--
    end++
  }

  const subTokens = tokens.slice(startIdx + 1, end - 1) as string[]
  const result = evaluateExpression(subTokens, values)
  return [...tokens.slice(0, startIdx), result, ...tokens.slice(end)]
}

function processNegation(tokens: Token[], values: Values): Token[] {
  const result: Token[] = []
  let i = 0
  while (i < tokens.length) {
    if (tokens[i] === "!" && i + 1 < tokens.length) {
      const value = evaluateToken(tokens[i + 1], values)
      result.push(!value)
      i += 2
    } else {
      result.push(tokens[i])
      i += 1
    }
  }
  return result
}

function processOperator(tokens: Token[], operator: string, values: Values): Token[] {
  let result = [...tokens]

  if (operator === ">") {
    // Right to left for implication
    const indices: number[] = []
    result.forEach((t, i) => {
      if (t === operator) indices.push(i)
    })
    for (const idx of indices.reverse()) {
      const left = evaluateToken(result[idx - 1], values)
      const right = evaluateToken(result[idx + 1], values)
      const opResult = operators[operator](left, right)
      result = [...result.slice(0, idx - 1), opResult, ...result.slice(idx + 2)]
    }
  } else {
    while (result.includes(operator)) {
      const idx = result.indexOf(operator)
      const left = evaluateToken(result[idx - 1], values)
      const right = evaluateToken(result[idx + 1], values)
      const opResult = operators[operator](left, right)
      result = [...result.slice(0, idx - 1), opResult, ...result.slice(idx + 2)]
    }
  }

  return result
}

export function evaluateExpression(tokens: string[], values: Values): boolean {
  if (!tokens.length) return false
  if (tokens.length === 1) return evaluateToken(tokens[0], values)

  let current: Token[] = [...tokens]

  // Process parentheses
  while (current.includes("(")) {
    current = processParentheses(current, values)
  }

  // Process negation
  current = processNegation(current, values)

  // Process binary operators by precedence
  for (const op of ["<>", ">", "&", "|"]) {
    current = processOperator(current, op, values)
  }

  return typeof current[0] === "boolean" ? current[0] : evaluateToken(current[0], values)
}

export function analyzeExpression(expression: string, values: Values): boolean {
  const tokens = tokenize(expression)
  return evaluateExpression(tokens, values)
}

function* generateCombinations(n: number): Generator<boolean[]> {
  for (let i = 0; i < Math.pow(2, n); i++) {
    const combo: boolean[] = []
    for (let j = n - 1; j >= 0; j--) {
      combo.push(Boolean((i >> j) & 1))
    }
    yield combo
  }
}

export function checkEquivalence(
  expr1: string,
  expr2: string
): { equivalent: boolean; differences: Array<{ values: Values; result1: boolean; result2: boolean }> } {
  const variables = extractVariables(expr1, expr2)
  const differences: Array<{ values: Values; result1: boolean; result2: boolean }> = []

  for (const combination of generateCombinations(variables.length)) {
    const values: Values = {}
    variables.forEach((v, i) => {
      values[v] = combination[i]
    })

    try {
      const result1 = analyzeExpression(expr1, values)
      const result2 = analyzeExpression(expr2, values)

      if (result1 !== result2) {
        differences.push({ values: { ...values }, result1, result2 })
      }
    } catch {
      return { equivalent: false, differences }
    }
  }

  return { equivalent: differences.length === 0, differences }
}
