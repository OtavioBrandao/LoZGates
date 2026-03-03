// Porte direto de tabela.py - Gerador de tabela verdade
import type { TruthTableResult } from "./types"
import { analyzeExpression, extractVariables } from "./evaluator"

function extractSubExpressions(expression: string): Set<string> {
  const subs = new Set<string>()
  for (let i = 0; i < expression.length; i++) {
    if (expression[i] === "(") {
      let count = 1
      for (let j = i + 1; j < expression.length; j++) {
        if (expression[j] === "(") count++
        else if (expression[j] === ")") count--
        if (count === 0) {
          const sub = expression.slice(i, j + 1)
          const inner = sub.slice(1, -1).trim()
          if (inner.length > 1 || !/^[a-zA-Z]$/.test(inner)) {
            subs.add(sub)
          }
          break
        }
      }
    }
  }
  return subs
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

  const rows: number[][] = []
  const finalResults: number[] = []

  for (let i = 0; i < totalCombinations; i++) {
    const values: Record<string, boolean> = {}
    variables.forEach((v, idx) => {
      values[v] = Boolean((i >> (variables.length - 1 - idx)) & 1)
    })

    const row: number[] = []
    for (const col of columns) {
      try {
        const result = analyzeExpression(col, values)
        row.push(result ? 1 : 0)
      } catch {
        row.push(0)
      }
    }
    rows.push(row)
    if (row.length > 0) {
      finalResults.push(row[row.length - 1])
    }
  }

  const trueCount = finalResults.filter((r) => r === 1).length
  let classification: TruthTableResult["classification"]
  if (trueCount === totalCombinations) classification = "TAUTOLOGIA"
  else if (trueCount === 0) classification = "CONTRADICAO"
  else classification = "SATISFATIVEL"

  return {
    columns,
    rows,
    finalResults,
    totalCombinations,
    totalVariables: variables.length,
    classification,
  }
}
