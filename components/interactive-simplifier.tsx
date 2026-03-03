"use client"

import { useState, useCallback, useRef } from "react"
import {
  buildInteractiveTree,
  nodeToStr,
  cloneNode,
  findNextStep,
  applyLawAndReplace,
  LOGIC_LAWS,
} from "@/lib/engine/interactive-simplifier"
import type { SimplifierNode, InteractiveStepInfo } from "@/lib/engine/types"
import { Undo2, SkipForward, RotateCcw } from "lucide-react"

interface HistoryEntry {
  root: SimplifierNode
  expression: string
  law: string
}

export function InteractiveSimplifier({ expression }: { expression: string }) {
  const initialRoot = useRef(buildInteractiveTree(expression))
  const [root, setRoot] = useState<SimplifierNode>(() => cloneNode(initialRoot.current)!)
  const [currentStep, setCurrentStep] = useState<InteractiveStepInfo | null>(() => findNextStep(root))
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [skipNodes, setSkipNodes] = useState<Set<string>>(new Set())
  const [message, setMessage] = useState("")

  const currentExpr = nodeToStr(root)

  const applicableLaws = currentStep
    ? LOGIC_LAWS.map((law, i) => ({ law, index: i, applicable: currentStep.applicableLaws[i] })).filter((l) => l.applicable)
    : []

  const handleApplyLaw = useCallback(
    (lawIndex: number) => {
      if (!currentStep) return

      const beforeExpr = currentExpr
      const lawName = LOGIC_LAWS[lawIndex].name

      setHistory((prev) => [...prev, { root: cloneNode(root)!, expression: beforeExpr, law: lawName }])

      const { newRoot, success } = applyLawAndReplace(root, currentStep, lawIndex)
      if (success) {
        const cloned = cloneNode(newRoot)!
        setRoot(cloned)
        setSkipNodes(new Set())
        const next = findNextStep(cloned)
        setCurrentStep(next)
        setMessage(`Aplicada: ${lawName}`)
      }
    },
    [currentStep, root, currentExpr]
  )

  const handleSkip = useCallback(() => {
    if (!currentStep) return
    const nodeStr = nodeToStr(currentStep.currentNode)
    const newSkip = new Set(skipNodes)
    newSkip.add(nodeStr)
    setSkipNodes(newSkip)
    const next = findNextStep(root, newSkip)
    setCurrentStep(next)
    setMessage("Passo pulado")
  }, [currentStep, root, skipNodes])

  const handleUndo = useCallback(() => {
    if (history.length === 0) return
    const last = history[history.length - 1]
    const restored = cloneNode(last.root)!
    setRoot(restored)
    setHistory((prev) => prev.slice(0, -1))
    setSkipNodes(new Set())
    setCurrentStep(findNextStep(restored))
    setMessage("Desfeito")
  }, [history])

  const handleReset = useCallback(() => {
    const fresh = cloneNode(initialRoot.current)!
    setRoot(fresh)
    setHistory([])
    setSkipNodes(new Set())
    setCurrentStep(findNextStep(fresh))
    setMessage("Reiniciado")
  }, [])

  return (
    <div className="flex flex-col gap-4">
      {/* Expressao atual */}
      <div className="flex flex-col gap-1 rounded-lg border border-primary/20 bg-primary/5 p-4">
        <span className="text-xs text-muted-foreground">Expressao atual</span>
        <code className="font-mono text-lg text-primary">{currentExpr}</code>
      </div>

      {/* Sub-expressao em foco */}
      {currentStep ? (
        <div className="flex flex-col gap-3 rounded-lg border border-border bg-card p-4">
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground">Sub-expressao em foco</span>
            <code className="font-mono text-base text-secondary">{nodeToStr(currentStep.currentNode)}</code>
          </div>

          {/* Leis aplicaveis */}
          {applicableLaws.length > 0 ? (
            <div className="flex flex-col gap-2">
              <span className="text-xs text-muted-foreground">Escolha a lei a aplicar:</span>
              <div className="flex flex-col gap-1.5">
                {applicableLaws.map((item) => (
                  <button
                    key={item.index}
                    onClick={() => handleApplyLaw(item.index)}
                    className="rounded-md border border-border bg-surface-dark px-3 py-2 text-left text-sm text-foreground transition-colors hover:border-primary hover:text-primary"
                  >
                    {item.law.name}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Nenhuma lei aplicavel nesta sub-expressao.
            </p>
          )}

          {/* Controles */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleSkip}
              className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-secondary hover:text-secondary"
            >
              <SkipForward className="h-3 w-3" />
              Pular
            </button>
            <button
              onClick={handleUndo}
              disabled={history.length === 0}
              className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-foreground hover:text-foreground disabled:opacity-40"
            >
              <Undo2 className="h-3 w-3" />
              Desfazer
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-destructive hover:text-destructive"
            >
              <RotateCcw className="h-3 w-3" />
              Reiniciar
            </button>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border border-success/20 bg-success/5 p-4">
          <p className="text-sm text-success">Simplificacao completa! Nao ha mais passos disponiveis.</p>
        </div>
      )}

      {/* Mensagem */}
      {message && (
        <p className="text-xs text-muted-foreground">{message}</p>
      )}

      {/* Historico */}
      {history.length > 0 && (
        <div className="flex flex-col gap-2">
          <span className="text-xs font-medium text-muted-foreground">Historico ({history.length} passo(s))</span>
          <div className="flex flex-col gap-1 rounded-lg border border-border bg-surface-dark p-3">
            {history.map((entry, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="font-mono text-muted-foreground">{i + 1}.</span>
                <span className="text-secondary">{entry.law}</span>
                <span className="font-mono text-muted-foreground">{entry.expression}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
