"use client"

import { type SimplificationStep } from "@/lib/logic/simplifier"
import { ArrowDown, Sparkles } from "lucide-react"

interface SimplificationStepsProps {
  steps: SimplificationStep[]
  result: string
  originalExpression: string
}

export function SimplificationSteps({ steps, result, originalExpression }: SimplificationStepsProps) {
  if (steps.length === 0) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-info/30 bg-info/10 p-4 text-sm text-info">
        <Sparkles className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
        <span>A expressao ja esta na forma mais simples.</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-cyan" aria-hidden="true" />
        <h3 className="text-sm font-semibold text-foreground">
          Simplificacao Automatica ({steps.length} passo{steps.length !== 1 ? "s" : ""})
        </h3>
      </div>

      {/* Original */}
      <div className="rounded-lg border border-border bg-surface-dark p-3">
        <span className="text-xs text-muted-foreground">Original</span>
        <code className="block mt-1 font-mono text-sm text-foreground">{originalExpression}</code>
      </div>

      {/* Steps */}
      <div className="flex flex-col gap-1">
        {steps.map((step, i) => (
          <div key={i} className="flex flex-col">
            <div className="flex items-center gap-2 py-1">
              <ArrowDown className="h-3 w-3 text-cyan flex-shrink-0" aria-hidden="true" />
              <span className="rounded bg-cyan/10 px-2 py-0.5 text-xs font-medium text-cyan">{step.law}</span>
            </div>
            <div className="ml-5 rounded-lg border border-border bg-surface-dark p-2.5">
              <code className="font-mono text-xs text-foreground">{step.after}</code>
            </div>
          </div>
        ))}
      </div>

      {/* Final result */}
      <div className="rounded-lg border border-success/30 bg-success/10 p-3">
        <span className="text-xs text-success">Resultado Final</span>
        <code className="block mt-1 font-mono text-sm font-bold text-success">{result}</code>
      </div>
    </div>
  )
}
