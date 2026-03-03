"use client"

import { useState, useMemo } from "react"
import { checkEquivalence } from "@/lib/engine/evaluator"
import { convertToBooleanAlgebra } from "@/lib/engine/converter"
import { Check, X } from "lucide-react"

export function EquivalenceChecker({ primaryExpression }: { primaryExpression: string }) {
  const [secondExpr, setSecondExpr] = useState("")
  const [result, setResult] = useState<null | { equivalent: boolean; diffCount: number }>(null)

  const converted = useMemo(() => convertToBooleanAlgebra(primaryExpression), [primaryExpression])

  const handleCheck = () => {
    if (!secondExpr.trim()) return
    const r = checkEquivalence(primaryExpression, secondExpr.trim())
    setResult({ equivalent: r.equivalent, diffCount: r.differences.length })
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Expressao principal */}
      <div className="flex flex-col gap-1 rounded-lg border border-border bg-card p-3">
        <span className="text-xs text-muted-foreground">Expressao 1 (original)</span>
        <code className="font-mono text-sm text-foreground">{primaryExpression}</code>
        {converted.converted !== primaryExpression && (
          <>
            <span className="text-xs text-muted-foreground">Algebra booleana</span>
            <code className="font-mono text-sm text-primary">{converted.converted}</code>
          </>
        )}
      </div>

      {/* Segunda expressao */}
      <div className="flex flex-col gap-2">
        <label htmlFor="second-expr" className="text-sm text-muted-foreground">
          Expressao 2 (para comparar)
        </label>
        <div className="flex gap-2">
          <input
            id="second-expr"
            type="text"
            value={secondExpr}
            onChange={(e) => {
              setSecondExpr(e.target.value)
              setResult(null)
            }}
            onKeyDown={(e) => { if (e.key === "Enter") handleCheck() }}
            placeholder="Ex: !A | B"
            className="flex-1 rounded-lg border border-input bg-background px-3 py-2 font-mono text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            spellCheck={false}
          />
          <button
            onClick={handleCheck}
            disabled={!secondExpr.trim()}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-all hover:opacity-90 disabled:opacity-40"
          >
            Verificar
          </button>
        </div>
      </div>

      {/* Resultado */}
      {result && (
        <div
          className={`flex items-center gap-3 rounded-lg border p-4 ${
            result.equivalent
              ? "border-success/30 bg-success/5"
              : "border-destructive/30 bg-destructive/5"
          }`}
        >
          {result.equivalent ? (
            <>
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-success/20">
                <Check className="h-5 w-5 text-success" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-medium text-success">Equivalentes</span>
                <span className="text-xs text-muted-foreground">
                  As duas expressoes produzem os mesmos resultados para todas as combinacoes de variaveis.
                </span>
              </div>
            </>
          ) : (
            <>
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-destructive/20">
                <X className="h-5 w-5 text-destructive" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-medium text-destructive">Nao equivalentes</span>
                <span className="text-xs text-muted-foreground">
                  {result.diffCount} diferenca(s) encontrada(s) na tabela verdade.
                </span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
