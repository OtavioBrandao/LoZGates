// Truth Table Generator
// Ported from Python tabela.py

import { extractVariables, analyzeExpression } from "./equivalence"

export interface TruthTableResult {
  columns: string[]
  table: number[][]
  finalResults: number[]
  totalCombinations: number
  totalVariables: number
  conclusion: string
}

function extractSubExpressions(expression: string): Set<string> {
  const subExpressions = new Set<string>()

  for (let i = 0; i < expression.length; i++) {
    if (expression[i] === "(") {
      let count = 1
      for (let j = i + 1; j < expression.length; j++) {
        if (expression[j] === "(") count++
        else if (expression[j] === ")") count--

        if (count === 0) {
          const subExpr = expression.slice(i, j + 1)
          const content = subExpr.slice(1, -1).trim()
          if (content.length > 1 || !/^[A-Za-z]$/.test(content)) {
            subExpressions.add(subExpr)
          }
          break
        }
      }
    }
  }

  return subExpressions
}

function buildColumns(variables: string[], subExpressions: Set<string>, fullExpression: string): string[] {
  const columns = [...variables]
  const sortedSubs = Array.from(subExpressions).sort((a, b) => a.length - b.length)
  columns.push(...sortedSubs)

  if (!columns.includes(fullExpression)) {
    columns.push(fullExpression)
  }

  return columns
}

export function generateTruthTable(expression: string): TruthTableResult {
  const variables = extractVariables(expression).sort()
  const subExpressions = extractSubExpressions(expression)
  const columns = buildColumns(variables, subExpressions, expression)
  const totalCombinations = Math.pow(2, variables.length)
  const table: number[][] = []
  const finalResults: number[] = []

  for (let i = 0; i < totalCombinations; i++) {
    const values: Record<string, boolean> = {}
    for (let j = 0; j < variables.length; j++) {
      values[variables[j]] = Boolean((i >> (variables.length - 1 - j)) & 1)
    }

    const row: number[] = []
    for (const col of columns) {
      try {
        const result = analyzeExpression(col, values)
        row.push(result ? 1 : 0)
      } catch {
        row.push(0)
      }
    }

    table.push(row)
    if (row.length > 0) {
      finalResults.push(row[row.length - 1])
    }
  }

  const conclusion = getConclusion(finalResults)

  return {
    columns,
    table,
    finalResults,
    totalCombinations,
    totalVariables: variables.length,
    conclusion,
  }
}

function getConclusion(results: number[]): string {
  if (results.length === 0) return "Nenhum resultado para analisar."

  const trueCount = results.reduce((acc, r) => acc + r, 0)
  const total = results.length

  if (trueCount === total) return "A expressao e uma TAUTOLOGIA."
  if (trueCount === 0) return "A expressao e uma CONTRADICAO."
  return "A expressao e SATISFATIVEL."
}
