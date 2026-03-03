// Porte de drawer.py - Desenho de portas logicas via Canvas 2D API
import { Camera } from "./camera"

// Cores do tema, compativel com o original
export const GATE_COLORS = {
  AND: "rgb(60, 120, 220)",
  OR: "rgb(50, 200, 130)",
  NOT: "rgb(250, 170, 70)",
  NAND: "rgb(120, 60, 220)",
  NOR: "rgb(200, 50, 130)",
  XOR: "rgb(220, 120, 60)",
  XNOR: "rgb(60, 220, 120)",
}

const WIRE_COLOR = "rgb(200, 200, 200)"
const LABEL_COLOR = "rgb(255, 255, 255)"
const GATE_WIDTH = 40
const GATE_HEIGHT = 80
export const NODE_H_SPACING = 180

export class CircuitDrawer {
  ctx: CanvasRenderingContext2D
  camera: Camera

  constructor(ctx: CanvasRenderingContext2D, camera: Camera) {
    this.ctx = ctx
    this.camera = camera
  }

  private drawLine(sx: number, sy: number, ex: number, ey: number, color: string, width = 2) {
    const s = this.camera.worldToScreen(sx, sy)
    const e = this.camera.worldToScreen(ex, ey)
    const sw = Math.max(1, width * this.camera.zoom)
    this.ctx.strokeStyle = color
    this.ctx.lineWidth = sw
    this.ctx.beginPath()
    this.ctx.moveTo(s.x, s.y)
    this.ctx.lineTo(e.x, e.y)
    this.ctx.stroke()
  }

  private drawCircle(cx: number, cy: number, radius: number, color: string, fill = true, width = 2) {
    const c = this.camera.worldToScreen(cx, cy)
    const sr = Math.max(1, radius * this.camera.zoom)
    this.ctx.beginPath()
    this.ctx.arc(c.x, c.y, sr, 0, Math.PI * 2)
    if (fill) {
      this.ctx.fillStyle = color
      this.ctx.fill()
    } else {
      this.ctx.strokeStyle = color
      this.ctx.lineWidth = Math.max(1, width * this.camera.zoom)
      this.ctx.stroke()
    }
  }

  private drawText(text: string, wx: number, wy: number, fontSize = 36, color?: string) {
    const c = this.camera.worldToScreen(wx, wy)
    const sf = Math.max(8, fontSize * this.camera.zoom)
    this.ctx.fillStyle = color ?? LABEL_COLOR
    this.ctx.font = `${sf}px var(--font-mono, monospace)`
    this.ctx.textAlign = "center"
    this.ctx.textBaseline = "middle"
    this.ctx.fillText(text, c.x, c.y)
  }

  private drawArc(centerX: number, centerY: number, radiusX: number, radiusY: number, startAngle: number, endAngle: number, color: string, width = 3) {
    const segments = 16
    const step = (endAngle - startAngle) / segments
    for (let i = 0; i < segments; i++) {
      const a1 = startAngle + i * step
      const a2 = startAngle + (i + 1) * step
      const x1 = centerX + radiusX * Math.cos(a1)
      const y1 = centerY + radiusY * Math.sin(a1)
      const x2 = centerX + radiusX * Math.cos(a2)
      const y2 = centerY + radiusY * Math.sin(a2)
      this.drawLine(x1, y1, x2, y2, color, width)
    }
  }

  drawGateShape(name: string, worldX: number, worldY: number): { x: number; y: number } {
    const w = GATE_WIDTH
    const h = GATE_HEIGHT

    if (name === "AND") {
      this.drawLine(worldX, worldY, worldX, worldY + h, GATE_COLORS.AND, 3)
      this.drawLine(worldX, worldY, worldX + w / 2, worldY, GATE_COLORS.AND, 3)
      this.drawLine(worldX, worldY + h, worldX + w / 2, worldY + h, GATE_COLORS.AND, 3)
      this.drawArc(worldX + w / 2, worldY + h / 2, w / 2, h / 2, -Math.PI / 2, Math.PI / 2, GATE_COLORS.AND, 3)
      return { x: worldX + w, y: worldY + h / 2 }
    }

    if (name === "OR") {
      const bc = { x: worldX - 7.5, y: worldY + h / 2 }
      const fc = { x: worldX + w / 2, y: worldY + h / 2 }
      this.drawArc(bc.x, bc.y, 10, h / 2, -Math.PI / 2, Math.PI / 2, GATE_COLORS.OR, 3)
      this.drawArc(fc.x, fc.y, w / 2, h / 2, -Math.PI / 2, Math.PI / 2, GATE_COLORS.OR, 3)
      this.drawLine(bc.x, bc.y - h / 2, fc.x, fc.y - h / 2, GATE_COLORS.OR, 3)
      this.drawLine(bc.x, bc.y + h / 2, fc.x, fc.y + h / 2, GATE_COLORS.OR, 3)
      return { x: worldX + w, y: worldY + h / 2 }
    }

    if (name === "NOT") {
      const cy = worldY + h / 2
      const p1 = { x: worldX, y: worldY + 15 }
      const p2 = { x: worldX, y: worldY + h - 15 }
      const p3 = { x: worldX + 30, y: cy }
      this.drawLine(p1.x, p1.y, p2.x, p2.y, GATE_COLORS.NOT, 3)
      this.drawLine(p2.x, p2.y, p3.x, p3.y, GATE_COLORS.NOT, 3)
      this.drawLine(p3.x, p3.y, p1.x, p1.y, GATE_COLORS.NOT, 3)
      this.drawCircle(worldX + 38, cy, 8, GATE_COLORS.NOT, false, 3)
      return { x: worldX + 46, y: cy }
    }

    if (name === "NAND") {
      this._drawAndShape(worldX, worldY, w, h, GATE_COLORS.NAND)
      this.drawCircle(worldX + w + 8, worldY + h / 2, 8, GATE_COLORS.NAND, false, 3)
      return { x: worldX + w + 16, y: worldY + h / 2 }
    }

    if (name === "NOR") {
      this._drawOrShape(worldX, worldY, w, h, GATE_COLORS.NOR)
      this.drawCircle(worldX + w + 8, worldY + h / 2, 8, GATE_COLORS.NOR, false, 3)
      return { x: worldX + w + 16, y: worldY + h / 2 }
    }

    if (name === "XOR") {
      this._drawXorShape(worldX, worldY, w, h, GATE_COLORS.XOR)
      return { x: worldX + w, y: worldY + h / 2 }
    }

    if (name === "XNOR") {
      this._drawXorShape(worldX, worldY, w, h, GATE_COLORS.XNOR)
      this.drawCircle(worldX + w + 8, worldY + h / 2, 8, GATE_COLORS.XNOR, false, 3)
      return { x: worldX + w + 16, y: worldY + h / 2 }
    }

    return { x: worldX + w, y: worldY + h / 2 }
  }

  private _drawAndShape(x: number, y: number, w: number, h: number, color: string) {
    this.drawLine(x, y, x, y + h, color, 3)
    this.drawLine(x, y, x + w / 2, y, color, 3)
    this.drawLine(x, y + h, x + w / 2, y + h, color, 3)
    this.drawArc(x + w / 2, y + h / 2, w / 2, h / 2, -Math.PI / 2, Math.PI / 2, color, 3)
  }

  private _drawOrShape(x: number, y: number, w: number, h: number, color: string) {
    const bc = { x: x - 7.5, y: y + h / 2 }
    const fc = { x: x + w / 2, y: y + h / 2 }
    this.drawArc(bc.x, bc.y, 10, h / 2, -Math.PI / 2, Math.PI / 2, color, 3)
    this.drawArc(fc.x, fc.y, w / 2, h / 2, -Math.PI / 2, Math.PI / 2, color, 3)
    this.drawLine(bc.x, bc.y - h / 2, fc.x, fc.y - h / 2, color, 3)
    this.drawLine(bc.x, bc.y + h / 2, fc.x, fc.y + h / 2, color, 3)
  }

  private _drawXorShape(x: number, y: number, w: number, h: number, color: string) {
    const ebc = { x: x - 15, y: y + h / 2 }
    this.drawArc(ebc.x, ebc.y, 8, h / 2 - 5, -Math.PI / 2, Math.PI / 2, color, 3)
    this._drawOrShape(x, y, w, h, color)
  }

  drawSmartWire(sx: number, sy: number, ex: number, ey: number) {
    const midX = sx + (ex - sx) * 0.5
    this.drawLine(sx, sy, midX, sy, WIRE_COLOR, 2)
    this.drawLine(midX, sy, midX, ey, WIRE_COLOR, 2)
    this.drawLine(midX, ey, ex, ey, WIRE_COLOR, 2)
  }

  drawConnectionDot(wx: number, wy: number, color?: string, radius = 5) {
    this.drawCircle(wx, wy, radius, color ?? WIRE_COLOR)
  }

  drawBus(x: number, y1: number, y2: number, label: string) {
    this.drawLine(x, y1, x, y2, "rgb(230, 230, 230)", 2)
    this.drawText(label, x, y1 - 15, 24)
  }

  drawOutputLabel(wx: number, wy: number) {
    this.drawLine(wx, wy, wx + 80, wy, "rgb(230, 230, 230)", 4)
    this.drawText("SAIDA", wx + 120, wy, 30)
  }

  drawGrid(screenWidth: number, screenHeight: number) {
    const gridSize = 50
    const color = "rgb(30, 30, 30)"
    const tl = this.camera.screenToWorld(0, 0)
    const br = this.camera.screenToWorld(screenWidth, screenHeight)
    const margin = gridSize * 2

    const startX = Math.floor((tl.x - margin) / gridSize) * gridSize
    const endX = Math.ceil((br.x + margin) / gridSize) * gridSize
    const startY = Math.floor((tl.y - margin) / gridSize) * gridSize
    const endY = Math.ceil((br.y + margin) / gridSize) * gridSize

    for (let x = startX; x <= endX; x += gridSize) {
      this.drawLine(x, tl.y - margin, x, br.y + margin, color, 1)
    }
    for (let y = startY; y <= endY; y += gridSize) {
      this.drawLine(tl.x - margin, y, br.x + margin, y, color, 1)
    }
  }
}
