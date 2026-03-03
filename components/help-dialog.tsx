"use client"

import { useState } from "react"
import { X, BookOpen, Code, Lightbulb, Scale, HelpCircle, Users } from "lucide-react"
import { SYNTAX_HELP, LOGIC_LAWS_INFO, INTERACTIVE_EXAMPLES, COMMON_FAQ } from "@/lib/config"

interface HelpDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const tabs = [
  { id: "syntax", label: "Sintaxe", icon: Code },
  { id: "laws", label: "Leis", icon: Scale },
  { id: "examples", label: "Exemplos", icon: Lightbulb },
  { id: "faq", label: "FAQ", icon: HelpCircle },
  { id: "credits", label: "Creditos", icon: Users },
]

export function HelpDialog({ open, onOpenChange }: HelpDialogProps) {
  const [activeTab, setActiveTab] = useState("syntax")

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="help-dialog-title">
      <div className="relative w-full max-w-3xl max-h-[85vh] rounded-xl border border-border bg-card shadow-2xl flex flex-col mx-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-cyan" aria-hidden="true" />
            <h2 id="help-dialog-title" className="text-lg font-semibold text-foreground">Manual de Ajuda</h2>
          </div>
          <button onClick={() => onOpenChange(false)} className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-surface-dark hover:text-foreground" aria-label="Fechar">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 border-b border-border px-4 overflow-x-auto" role="tablist">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium transition-colors border-b-2 whitespace-nowrap ${
                activeTab === tab.id
                  ? "border-cyan text-cyan"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <tab.icon className="h-4 w-4" aria-hidden="true" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6" role="tabpanel">
          {activeTab === "syntax" && <SyntaxTab />}
          {activeTab === "laws" && <LawsTab />}
          {activeTab === "examples" && <ExamplesTab />}
          {activeTab === "faq" && <FaqTab />}
          {activeTab === "credits" && <CreditsTab />}
        </div>
      </div>
    </div>
  )
}

function SyntaxTab() {
  return (
    <div className="flex flex-col gap-6">
      <section>
        <h3 className="text-sm font-semibold text-cyan mb-3">Operadores</h3>
        <div className="grid gap-2">
          {SYNTAX_HELP.operators.map((op) => (
            <div key={op.symbol} className="flex items-start gap-3 rounded-lg bg-surface-dark p-3">
              <code className="rounded bg-background px-2 py-0.5 text-sm font-mono text-cyan font-bold">{op.symbol}</code>
              <div>
                <span className="text-sm font-medium text-foreground">{op.name}</span>
                <p className="text-xs text-muted-foreground">{op.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h3 className="text-sm font-semibold text-cyan mb-3">Precedencia (maior para menor)</h3>
        <ol className="flex flex-col gap-1.5">
          {SYNTAX_HELP.precedence.map((item, i) => (
            <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-cyan/10 text-xs font-bold text-cyan">{i + 1}</span>
              <span className="font-mono">{item}</span>
            </li>
          ))}
        </ol>
      </section>
      <section>
        <h3 className="text-sm font-semibold text-cyan mb-2">Variaveis</h3>
        <p className="text-sm text-muted-foreground">{SYNTAX_HELP.variables}</p>
      </section>
    </div>
  )
}

function LawsTab() {
  return (
    <div className="flex flex-col gap-3">
      {LOGIC_LAWS_INFO.map((law) => (
        <div key={law.name} className="rounded-lg border border-border bg-surface-dark p-4">
          <h4 className="text-sm font-semibold text-foreground mb-1">{law.name}</h4>
          <p className="text-xs text-muted-foreground mb-2">{law.desc}</p>
          <div className="flex flex-wrap gap-2">
            {law.formulas.map((f, i) => (
              <code key={i} className="rounded bg-background px-2 py-1 text-xs font-mono text-cyan">{f}</code>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function ExamplesTab() {
  const categories = [
    { key: "basic", label: "Basico" },
    { key: "intermediate", label: "Intermediario" },
    { key: "advanced", label: "Avancado" },
  ] as const

  return (
    <div className="flex flex-col gap-6">
      {categories.map((cat) => (
        <section key={cat.key}>
          <h3 className="text-sm font-semibold text-cyan mb-3">{cat.label}</h3>
          <div className="grid gap-2">
            {INTERACTIVE_EXAMPLES[cat.key].map((ex) => (
              <div key={ex.expr} className="rounded-lg bg-surface-dark p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-foreground">{ex.name}</span>
                  <code className="rounded bg-background px-2 py-0.5 text-xs font-mono text-cyan">{ex.expr}</code>
                </div>
                <p className="text-xs text-muted-foreground">{ex.desc}</p>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}

function FaqTab() {
  return (
    <div className="flex flex-col gap-3">
      {COMMON_FAQ.map((faq, i) => (
        <div key={i} className="rounded-lg border border-border bg-surface-dark p-4">
          <h4 className="text-sm font-semibold text-foreground mb-2">{faq.question}</h4>
          <p className="text-sm text-muted-foreground leading-relaxed">{faq.answer}</p>
        </div>
      ))}
    </div>
  )
}

function CreditsTab() {
  return (
    <div className="flex flex-col items-center gap-4 py-8 text-center">
      <h3 className="text-lg font-semibold text-foreground">LoZGates v2.0 Web</h3>
      <p className="text-sm text-muted-foreground max-w-md leading-relaxed">
        Ferramenta educacional para Logica Proposicional e Circuitos Digitais. Desenvolvida como projeto academico para auxiliar estudantes de Ciencia e Engenharia da Computacao.
      </p>
      <div className="flex flex-col gap-1 text-sm text-muted-foreground">
        <span>Migrado de Python/Tkinter para Next.js/TypeScript</span>
        <span className="text-cyan">Versao original: LoZGates 1.0.1</span>
      </div>
    </div>
  )
}
