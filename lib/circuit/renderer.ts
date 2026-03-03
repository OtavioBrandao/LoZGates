// Porte de circuit_renderer.py - Renderizacao estatica de circuitos logicos
import type { CircuitLayout } from "../engine/types"
import { parseCircuitExpression, calculateDynamicLayout, collectVariables } from "../engine/circuit-parser"
import { Camera } from "./camera"
import { CircuitDrawer, NODE_H_SPACING } from "./gate-shapes"

interface DrawResult {
  type: "bus_connection" | "gate_output"
  busX?: number
  yPos?: number
  x?: number
  y?: number
}

const OP_MAP: Record<string, string> = { "*": "AND", "+": "OR", "~": "NOT" }

function drawDynamic(layout: CircuitLayout, xPos: number, busPositions: Map<string, number>, drawer: CircuitDrawer): DrawResult {
  if (layout.type === "variable" || layout.type === "negated_variable") {
    const busName = layout.type === "variable" ? layout.name! : `~${layout.name!}`
    return { type: "bus_connection", busX: busPositions.get(busName) ?? 50, yPos: layout.yPos + 40 }
  }

  if (layout.type === "gate") {
    const gateHeight = 80
    const gateCenterY = layout.yPos
    const gateTopY = gateCenterY - gateHeight / 2
    const gateName = OP_MAP[layout.op!] ?? "AND"

    const outputPos = drawer.drawGateShape(gateName, xPos, gateTopY)

    const numInputs = layout.children?.length ?? 0
    const inputPositions: { x: number; y: number }[] = []

    if (numInputs === 1) {
      inputPositions.push({ x: xPos, y: gateCenterY })
    } else {
      const spacing = numInputs > 1 ? (gateHeight - 30) / (numInputs - 1) : 0
      for (let i = 0; i < numInputs; i++) {
        inputPositions.push({ x: xPos, y: gateTopY + 15 + spacing * i })
      }
    }

    layout.children?.forEach((child, i) => {
      const childOutput = drawDynamic(child, xPos - NODE_H_SPACING, busPositions, drawer)
      if (childOutput.type === "bus_connection") {
        drawer.drawSmartWire(childOutput.busX!, childOutput.yPos!, inputPositions[i].x, inputPositions[i].y)
        drawer.drawConnectionDot(childOutput.busX!, childOutput.yPos!)
      } else {
        drawer.drawSmartWire(childOutput.x!, childOutput.y!, inputPositions[i].x, inputPositions[i].y)
      }
    })

    return { type: "gate_output", x: outputPos.x, y: outputPos.y }
  }

  return { type: "bus_connection", busX: 50, yPos: 50 }
}

export function renderStaticCircuit(ctx: CanvasRenderingContext2D, expression: string, width: number, height: number, camera?: Camera) {
  const cam = camera ?? new Camera(width, height)
  const drawer = new CircuitDrawer(ctx, cam)

  // Limpa
  ctx.fillStyle = "rgb(13, 13, 15)"
  ctx.fillRect(0, 0, width, height)

  // Grid
  drawer.drawGrid(width, height)

  let astRoot
  try {
    astRoot = parseCircuitExpression(expression)
  } catch (e) {
    ctx.fillStyle = "rgb(255, 80, 80)"
    ctx.font = "16px var(--font-mono, monospace)"
    ctx.textAlign = "center"
    ctx.fillText(`Erro: ${e instanceof Error ? e.message : "Expressao invalida"}`, width / 2, height / 2)
    return
  }

  const variables = Array.from(collectVariables(astRoot)).sort()
  const busPositions = new Map<string, number>()
  const busXStart = 100
  const busSpacing = 100
  let lastBusX = busXStart

  variables.forEach((varName, i) => {
    const trueBusX = busXStart + i * busSpacing
    drawer.drawBus(trueBusX, 40, height * 3, varName)
    busPositions.set(varName, trueBusX)

    const negatedBusX = trueBusX + 40
    drawer.drawBus(negatedBusX, 40, height * 3, `~${varName}`)
    busPositions.set(`~${varName}`, negatedBusX)
    lastBusX = negatedBusX
  })

  const layout = calculateDynamicLayout(astRoot, 100)
  const firstGateX = lastBusX + 150
  const finalOutput = drawDynamic(layout, firstGateX + (layout.width ?? 0), busPositions, drawer)

  if (finalOutput.type === "gate_output") {
    drawer.drawOutputLabel(finalOutput.x!, finalOutput.y!)
  }
}
