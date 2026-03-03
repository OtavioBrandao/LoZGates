// Converter: Logica Proposicional -> Algebra Booleana
// Ported from Python converter.py

export interface ConversionResult {
  result: string
  steps: string[]
}

const logicalOperators: Record<string, string> = {
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
    j -= 1
    while (j >= 0 && count > 0) {
      if (expr[j] === ")") count += 1
      else if (expr[j] === "(") count -= 1
      j -= 1
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
    k += 1
    const start = k
    while (k < expr.length && count > 0) {
      if (expr[k] === "(") count += 1
      else if (expr[k] === ")") count -= 1
      k += 1
    }
    return [expr.slice(start, k - 1), k]
  } else {
    const start = k
    if (k < expr.length && (expr[k] === "!" || expr[k] === "~")) {
      k += 1
    }
    if (k < expr.length) {
      k += 1
    }
    return [expr.slice(start, k), k]
  }
}

function replaceBiImplications(expr: string, steps: string[]): string {
  let i = 0
  while (i < expr.length) {
    if (
      (i + 2 < expr.length && expr.slice(i, i + 3) === "<->") ||
      (i + 1 < expr.length && expr.slice(i, i + 2) === "<>")
    ) {
      const opSize = expr.slice(i, i + 3) === "<->" ? 3 : 2
      const [a, aStart] = findLeftOperand(expr, i)
      const [b, bEnd] = findRightOperand(expr, i + opSize)
      const newExpr = expr.slice(0, aStart) + `((~${a}+${b})*(~${b}+${a}))` + expr.slice(bEnd)
      steps.push(`Bi-implicacao: ${expr} -> ${newExpr}`)
      return replaceBiImplications(newExpr, steps)
    }
    i += 1
  }
  return expr
}

function replaceImplications(expr: string, steps: string[]): string {
  let i = 0
  while (i < expr.length) {
    if (
      (i + 1 < expr.length && expr.slice(i, i + 2) === "->") ||
      (expr[i] === ">" && (i === 0 || expr[i - 1] !== "<"))
    ) {
      const opSize = expr.slice(i, i + 2) === "->" ? 2 : 1
      const [a, aStart] = findLeftOperand(expr, i)
      const [b, bEnd] = findRightOperand(expr, i + opSize)
      const newExpr = expr.slice(0, aStart) + `(~${a}+${b})` + expr.slice(bEnd)
      steps.push(`Implicacao: ${expr} -> ${newExpr}`)
      return replaceImplications(newExpr, steps)
    }
    i += 1
  }
  return expr
}

function replaceBasicOperators(expr: string, steps: string[]): string {
  const original = expr
  for (const [logical, algebraic] of Object.entries(logicalOperators)) {
    expr = expr.split(logical).join(algebraic)
  }
  if (expr !== original) {
    steps.push(`Operadores basicos: ${original} -> ${expr}`)
  }
  return expr
}

export function convertToBooleanAlgebra(expression: string): ConversionResult {
  const steps: string[] = []
  let expr = eraseExpression(expression)
  steps.push(`Original: ${expression}`)

  expr = replaceBiImplications(expr, steps)
  expr = replaceImplications(expr, steps)
  expr = replaceBasicOperators(expr, steps)

  return { result: expr, steps }
}

export function validateExpression(expression: string): { valid: boolean; error: string } {
  let count = 0
  for (let i = 0; i < expression.length; i++) {
    if (expression[i] === "(") count += 1
    else if (expression[i] === ")") {
      count -= 1
      if (count < 0) return { valid: false, error: `Parentese fechado sem abertura na posicao ${i}` }
    }
  }
  if (count !== 0) return { valid: false, error: `Parenteses nao balanceados: ${count} abertos` }

  // Check for valid characters
  const validChars = /^[A-Za-z0-9&|!~*+><()=\-\s]+$/
  const cleaned = expression.trim()
  if (cleaned.length === 0) return { valid: false, error: "Expressao vazia" }
  if (!validChars.test(cleaned)) return { valid: false, error: "Caracteres invalidos na expressao" }

  return { valid: true, error: "" }
}
