"use client"

import { useMemo } from "react"
import { generateTruthTable, type TruthTableResult } from "@/lib/logic/truth-table"
import { Table, Info } from "lucide-react"

interface TruthTableProps {
  expression: string
}

function getConclusionStyle(conclusion: string) {
  if (conclusion.includes("TAUTOLOGIA")) return "text-success bg-success/10 border-success/30"
  if (conclusion.includes("CONTRADICAO")) return "text-destructive bg-destructive/10 border-destructive/30"
  return "text-info bg-info/10 border-info/30"
}

export function TruthTable({ expression }: TruthTableProps) {
  const result: TruthTableResult | null = useMemo(() => {
    try {
      return generateTruthTable(expression)
    } catch {
      return null
    }
  }, [expression])

  if (!result) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
        <Info className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
        <span>Erro ao gerar tabela verdade. Verifique a expressao.</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Table className="h-4 w-4 text-cyan" aria-hidden="true" />
          <h3 className="text-sm font-semibold text-foreground">Tabela Verdade</h3>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>{result.totalVariables} variaveis</span>
          <span>{result.totalCombinations} combinacoes</span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="truth-table w-full text-sm" role="table">
          <thead>
            <tr>
              {result.columns.map((col, i) => (
                <th
                  key={i}
                  className={`border-b border-border px-3 py-2.5 text-center font-mono text-xs font-semibold ${
                    i === result.columns.length - 1 ? "bg-cyan/10 text-cyan" : "bg-surface-dark text-muted-foreground"
                  }`}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.table.map((row, rowIdx) => (
              <tr key={rowIdx} className="transition-colors hover:bg-surface-dark/50">
                {row.map((val, colIdx) => (
                  <td
                    key={colIdx}
                    className={`border-b border-border px-3 py-2 text-center font-mono text-xs ${
                      colIdx === row.length - 1
                        ? val === 1
                          ? "font-bold text-success"
                          : "font-bold text-destructive"
                        : "text-foreground"
                    }`}
                  >
                    {val}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Conclusion */}
      <div className={`flex items-center gap-2 rounded-lg border p-3 text-sm font-medium ${getConclusionStyle(result.conclusion)}`} role="status">
        <Info className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
        <span>{result.conclusion}</span>
      </div>
    </div>
  )
}
