"use client"

import { useMemo } from "react"
import type { TruthTableResult } from "@/lib/engine/types"

export function TruthTable({ data }: { data: TruthTableResult }) {
  const highlightedLastCol = useMemo(() => data.columns.length - 1, [data.columns])

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <span className="text-sm text-muted-foreground">
          {data.totalVariables} variavel(is) | {data.totalCombinations} combinacao(oes)
        </span>
        <ClassificationBadge classification={data.classification} />
      </div>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-dark">
              {data.columns.map((col, i) => (
                <th
                  key={i}
                  className={`whitespace-nowrap px-3 py-2 text-center font-mono text-xs font-medium ${
                    i === highlightedLastCol ? "text-primary" : "text-muted-foreground"
                  }`}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, ri) => (
              <tr key={ri} className="border-b border-border/50 transition-colors hover:bg-surface-dark/50">
                {row.map((val, ci) => (
                  <td
                    key={ci}
                    className={`px-3 py-1.5 text-center font-mono text-xs ${
                      ci === highlightedLastCol
                        ? val === 1
                          ? "font-bold text-success"
                          : "font-bold text-destructive"
                        : val === 1
                          ? "text-foreground"
                          : "text-muted-foreground"
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
    </div>
  )
}

function ClassificationBadge({ classification }: { classification: TruthTableResult["classification"] }) {
  const styles = {
    TAUTOLOGIA: "border-success/40 bg-success/10 text-success",
    CONTRADICAO: "border-destructive/40 bg-destructive/10 text-destructive",
    SATISFATIVEL: "border-warning/40 bg-warning/10 text-warning",
  }

  return (
    <span className={`rounded-md border px-2 py-0.5 text-xs font-medium ${styles[classification]}`}>
      {classification}
    </span>
  )
}
