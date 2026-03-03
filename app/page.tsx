"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { ArrowRight, Zap, Sparkles, BookOpen, HelpCircle } from "lucide-react"
import { validateExpression } from "@/lib/engine/converter"
import { Header } from "@/components/layout/header"

const EXAMPLE_EXPRESSIONS = [
  { label: "Simples AND", expr: "A & B" },
  { label: "Implicacao", expr: "A -> B" },
  { label: "Bi-implicacao", expr: "A <-> B" },
  { label: "De Morgan", expr: "!(A & B)" },
  { label: "Complexa", expr: "(A | B) & (C -> D)" },
]

const OPERATOR_BUTTONS = [
  { label: "&", symbol: "&", desc: "AND" },
  { label: "|", symbol: "|", desc: "OR" },
  { label: "!", symbol: "!", desc: "NOT" },
  { label: "->", symbol: "->", desc: "Implica" },
  { label: "<->", symbol: "<->", desc: "Bi-implica" },
  { label: "(", symbol: "(", desc: "Abre" },
  { label: ")", symbol: ")", desc: "Fecha" },
]

export default function HomePage() {
  const [expression, setExpression] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = useCallback(() => {
    if (!expression.trim()) {
      setError("Digite uma expressao logica.")
      return
    }
    const validation = validateExpression(expression)
    if (!validation.valid) {
      setError(validation.error)
      return
    }
    setError("")
    router.push(`/workspace?expr=${encodeURIComponent(expression.trim())}`)
  }, [expression, router])

  const insertOperator = (symbol: string) => {
    setExpression((prev) => prev + symbol)
    setError("")
  }

  const loadExample = (expr: string) => {
    setExpression(expr)
    setError("")
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />

      <main className="flex flex-1 flex-col items-center justify-center px-4 py-12">
        <div className="flex w-full max-w-2xl flex-col items-center gap-8">
          {/* Titulo */}
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 glow-cyan">
              <Zap className="h-9 w-9 text-primary" />
            </div>
            <h1 className="text-balance font-mono text-4xl font-bold text-foreground md:text-5xl">
              LoZ<span className="text-primary text-glow-cyan">Gates</span>
            </h1>
            <p className="max-w-md text-pretty text-muted-foreground">
              Converta, simplifique e visualize expressoes logicas proposicionais
              como circuitos digitais interativos.
            </p>
          </div>

          {/* Card de input */}
          <div className="flex w-full flex-col gap-4 rounded-xl border border-border bg-card p-6">
            {/* Campo principal */}
            <div className="flex flex-col gap-2">
              <label htmlFor="expression" className="text-sm font-medium text-muted-foreground">
                Expressao logica
              </label>
              <div className="flex gap-2">
                <input
                  id="expression"
                  type="text"
                  value={expression}
                  onChange={(e) => {
                    setExpression(e.target.value)
                    setError("")
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSubmit()
                  }}
                  placeholder="Ex: (A & B) | !C -> D"
                  className="flex-1 rounded-lg border border-input bg-background px-4 py-3 font-mono text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  autoComplete="off"
                  spellCheck={false}
                />
                <button
                  onClick={handleSubmit}
                  className="flex items-center gap-2 rounded-lg bg-primary px-5 py-3 font-medium text-primary-foreground transition-all hover:opacity-90 glow-cyan"
                >
                  <span className="hidden sm:inline">Analisar</span>
                  <ArrowRight className="h-5 w-5" />
                </button>
              </div>
              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}
            </div>

            {/* Botoes de operadores */}
            <div className="flex flex-col gap-2">
              <span className="text-xs text-muted-foreground">Operadores</span>
              <div className="flex flex-wrap gap-2">
                {OPERATOR_BUTTONS.map((op) => (
                  <button
                    key={op.symbol}
                    onClick={() => insertOperator(op.symbol)}
                    className="flex items-center gap-1 rounded-md border border-border bg-surface-dark px-3 py-1.5 font-mono text-sm text-foreground transition-colors hover:border-primary hover:text-primary"
                    title={op.desc}
                  >
                    {op.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Exemplos */}
            <div className="flex flex-col gap-2">
              <span className="text-xs text-muted-foreground">Exemplos rapidos</span>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_EXPRESSIONS.map((ex) => (
                  <button
                    key={ex.expr}
                    onClick={() => loadExample(ex.expr)}
                    className="rounded-md border border-border bg-surface-dark px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-secondary hover:text-secondary"
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="grid w-full grid-cols-1 gap-3 sm:grid-cols-3">
            <FeatureCard
              icon={<Sparkles className="h-5 w-5 text-primary" />}
              title="Simplificacao"
              desc="Automatica e interativa com leis da algebra booleana"
            />
            <FeatureCard
              icon={<Zap className="h-5 w-5 text-secondary" />}
              title="Circuitos"
              desc="Visualize e construa circuitos com portas logicas"
            />
            <FeatureCard
              icon={<BookOpen className="h-5 w-5 text-primary" />}
              title="Problemas"
              desc="30+ desafios do mundo real com verificacao automatica"
            />
          </div>

          {/* Guia rapido */}
          <div className="flex w-full flex-col gap-2 rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2">
              <HelpCircle className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium text-muted-foreground">Guia rapido de operadores</span>
            </div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs sm:grid-cols-3">
              <span className="text-muted-foreground"><code className="font-mono text-foreground">&</code> ou <code className="font-mono text-foreground">*</code> = AND</span>
              <span className="text-muted-foreground"><code className="font-mono text-foreground">|</code> ou <code className="font-mono text-foreground">+</code> = OR</span>
              <span className="text-muted-foreground"><code className="font-mono text-foreground">!</code> ou <code className="font-mono text-foreground">~</code> = NOT</span>
              <span className="text-muted-foreground"><code className="font-mono text-foreground">{'->'}</code> = Implicacao</span>
              <span className="text-muted-foreground"><code className="font-mono text-foreground">{'<->'}</code> = Bi-implicacao</span>
              <span className="text-muted-foreground">Variaveis: <code className="font-mono text-foreground">A-Z</code> maiusculas</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border bg-card p-4">
      {icon}
      <h3 className="text-sm font-medium text-foreground">{title}</h3>
      <p className="text-xs text-muted-foreground">{desc}</p>
    </div>
  )
}
