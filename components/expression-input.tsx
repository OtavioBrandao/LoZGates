"use client"

import { useState, useCallback } from "react"
import { Zap, AlertCircle, Keyboard } from "lucide-react"
import { validateExpression } from "@/lib/logic/converter"

interface ExpressionInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  placeholder?: string
  label?: string
}

const operatorButtons = [
  { label: "&", title: "AND", key: "&" },
  { label: "|", title: "OR", key: "|" },
  { label: "!", title: "NOT", key: "!" },
  { label: ">", title: "Implicacao", key: ">" },
  { label: "<>", title: "Bi-implicacao", key: "<>" },
  { label: "(", title: "Abre parentese", key: "(" },
  { label: ")", title: "Fecha parentese", key: ")" },
]

export function ExpressionInput({ value, onChange, onSubmit, placeholder = "Ex: (A & B) | !C", label = "Expressao Logica" }: ExpressionInputProps) {
  const [showKeyboard, setShowKeyboard] = useState(false)
  const validation = value.trim() ? validateExpression(value) : { valid: true, error: "" }

  const insertOperator = useCallback(
    (op: string) => {
      onChange(value + op)
    },
    [value, onChange]
  )

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && validation.valid && value.trim()) {
      e.preventDefault()
      onSubmit()
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-muted-foreground" htmlFor="expression-input">{label}</label>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            id="expression-input"
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value.toUpperCase())}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={`w-full rounded-lg border bg-background px-4 py-3 font-mono text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 ${
              !validation.valid && value.trim()
                ? "border-destructive focus:ring-destructive/50"
                : "border-border focus:ring-cyan/50"
            }`}
            autoComplete="off"
            spellCheck={false}
            aria-invalid={!validation.valid && !!value.trim()}
            aria-describedby={!validation.valid && value.trim() ? "expression-error" : undefined}
          />
        </div>
        <button
          onClick={() => setShowKeyboard(!showKeyboard)}
          className="rounded-lg border border-border bg-card p-3 text-muted-foreground transition-colors hover:bg-surface-dark hover:text-foreground md:hidden"
          aria-label="Teclado de operadores"
          aria-expanded={showKeyboard}
        >
          <Keyboard className="h-4 w-4" />
        </button>
        <button
          onClick={onSubmit}
          disabled={!validation.valid || !value.trim()}
          className="flex items-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label="Analisar expressao"
        >
          <Zap className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">Analisar</span>
        </button>
      </div>

      {/* Error message */}
      {!validation.valid && value.trim() && (
        <div id="expression-error" className="flex items-center gap-1.5 text-xs text-destructive" role="alert">
          <AlertCircle className="h-3.5 w-3.5" aria-hidden="true" />
          <span>{validation.error}</span>
        </div>
      )}

      {/* Operator buttons - always visible on desktop, toggle on mobile */}
      <div className={`flex flex-wrap gap-1.5 ${showKeyboard ? "flex" : "hidden md:flex"}`} role="toolbar" aria-label="Operadores logicos">
        {operatorButtons.map((op) => (
          <button
            key={op.key}
            onClick={() => insertOperator(op.key)}
            title={op.title}
            className="rounded-md border border-border bg-surface-dark px-3 py-1.5 font-mono text-sm text-cyan transition-colors hover:bg-surface-light hover:text-foreground"
          >
            {op.label}
          </button>
        ))}
        {["A", "B", "C", "D", "E"].map((v) => (
          <button
            key={v}
            onClick={() => insertOperator(v)}
            className="rounded-md border border-border bg-surface-dark px-3 py-1.5 font-mono text-sm text-foreground transition-colors hover:bg-surface-light"
          >
            {v}
          </button>
        ))}
      </div>
    </div>
  )
}
