"use client"

import type { SimplificationResult } from "@/lib/engine/types"
import { ArrowDown } from "lucide-react"

export function SimplificationView({ result }: { result: SimplificationResult }) {
  return (
    <div className="flex flex-col gap-4">
      {/* Resultado */}
      <div className="flex flex-col gap-2 rounded-lg border border-primary/20 bg-primary/5 p-4">
        <span className="text-xs font-medium text-muted-foreground">Resultado simplificado</span>
        <code className="font-mono text-lg text-primary">{result.simplified}</code>
      </div>

      {/* Passos */}
      {result.steps.length > 0 ? (
        <div className="flex flex-col gap-1">
          <span className="text-sm font-medium text-muted-foreground">
            Passos ({result.steps.length})
          </span>
          <div className="flex flex-col gap-2">
            {result.steps.map((step, i) => (
              <div key={i} className="flex flex-col gap-1">
                <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                    {i + 1}
                  </span>
                  <div className="flex flex-1 flex-col gap-1">
                    <span className="text-xs font-medium text-secondary">{step.law}</span>
                    <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                      <span className="text-muted-foreground">{step.before}</span>
                      <ArrowDown className="h-3 w-3 shrink-0 text-primary" />
                      <span className="text-foreground">{step.after}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          A expressao ja esta na forma mais simplificada.
        </p>
      )}
    </div>
  )
}
