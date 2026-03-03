"use client"

import Link from "next/link"
import { useState } from "react"
import { CircuitBoard, Scale, BookOpen, Brain, Zap, Binary } from "lucide-react"
import { HelpDialog } from "@/components/help-dialog"

const features = [
  {
    title: "Circuitos e Expressoes",
    description: "Visualize circuitos logicos, tabelas verdade e simplifique expressoes passo a passo.",
    icon: CircuitBoard,
    href: "/circuits",
    color: "text-cyan",
    borderColor: "border-cyan/30",
    hoverBg: "hover:bg-cyan/5",
  },
  {
    title: "Equivalencia Logica",
    description: "Compare duas expressoes logicas e verifique se sao equivalentes.",
    icon: Scale,
    href: "/equivalence",
    color: "text-gold",
    borderColor: "border-gold/30",
    hoverBg: "hover:bg-gold/5",
  },
  {
    title: "Banco de Problemas",
    description: "Mais de 30 problemas do mundo real com 4 niveis de dificuldade.",
    icon: Brain,
    href: "/problems",
    color: "text-success",
    borderColor: "border-success/30",
    hoverBg: "hover:bg-success/5",
  },
]

export default function HomePage() {
  const [helpOpen, setHelpOpen] = useState(false)

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-12">
      {/* Background pattern */}
      <div className="fixed inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--color-cyan)_0%,transparent_70%)] opacity-[0.03]" />
      </div>

      <div className="relative z-10 flex flex-col items-center gap-12 max-w-4xl w-full">
        {/* Logo and Title */}
        <header className="flex flex-col items-center gap-4 text-center">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Zap className="h-10 w-10 text-cyan" aria-hidden="true" />
              <div className="absolute -inset-1 rounded-full bg-cyan/20 blur-md" aria-hidden="true" />
            </div>
            <h1 className="text-5xl font-bold tracking-tight text-balance md:text-6xl">
              <span className="text-cyan">LoZ</span>
              <span className="text-foreground">Gates</span>
            </h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-md text-pretty leading-relaxed">
            Ferramenta educacional interativa para Logica Proposicional e Circuitos Digitais
          </p>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Binary className="h-4 w-4" aria-hidden="true" />
            <span>v2.0 Web</span>
          </div>
        </header>

        {/* Feature Cards */}
        <nav className="grid gap-4 w-full md:grid-cols-3" aria-label="Funcionalidades principais">
          {features.map((feature) => (
            <Link
              key={feature.href}
              href={feature.href}
              className={`group flex flex-col gap-3 rounded-xl border ${feature.borderColor} bg-card p-6 transition-all duration-200 ${feature.hoverBg} hover:border-opacity-60 hover:shadow-lg`}
            >
              <div className="flex items-center gap-3">
                <feature.icon className={`h-6 w-6 ${feature.color} transition-transform group-hover:scale-110`} aria-hidden="true" />
                <h2 className="font-semibold text-foreground">{feature.title}</h2>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
            </Link>
          ))}
        </nav>

        {/* Help Button */}
        <button
          onClick={() => setHelpOpen(true)}
          className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-surface-dark hover:text-foreground"
          aria-label="Abrir manual de ajuda"
        >
          <BookOpen className="h-4 w-4" aria-hidden="true" />
          <span>Manual de Ajuda</span>
        </button>

        {/* Quick info */}
        <footer className="flex flex-wrap items-center justify-center gap-6 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-success" aria-hidden="true" />
            <span>Tabela Verdade</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan" aria-hidden="true" />
            <span>Simplificacao Automatica</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-gold" aria-hidden="true" />
            <span>9 Leis Logicas</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-warning" aria-hidden="true" />
            <span>30+ Problemas</span>
          </div>
        </footer>
      </div>

      <HelpDialog open={helpOpen} onOpenChange={setHelpOpen} />
    </main>
  )
}
