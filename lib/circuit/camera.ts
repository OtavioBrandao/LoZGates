// Porte de camera.py - Sistema de camera para viewport do circuito
export class Camera {
  x = 0
  y = 0
  zoom = 1.0
  minZoom = 0.2
  maxZoom = 3.0
  screenWidth: number
  screenHeight: number
  dragging = false
  lastMousePos = { x: 0, y: 0 }

  constructor(screenWidth: number, screenHeight: number) {
    this.screenWidth = screenWidth
    this.screenHeight = screenHeight
  }

  worldToScreen(worldX: number, worldY: number): { x: number; y: number } {
    return {
      x: (worldX - this.x) * this.zoom + this.screenWidth / 2,
      y: (worldY - this.y) * this.zoom + this.screenHeight / 2,
    }
  }

  screenToWorld(screenX: number, screenY: number): { x: number; y: number } {
    return {
      x: (screenX - this.screenWidth / 2) / this.zoom + this.x,
      y: (screenY - this.screenHeight / 2) / this.zoom + this.y,
    }
  }

  move(dx: number, dy: number) {
    this.x += dx / this.zoom
    this.y += dy / this.zoom
  }

  zoomAt(screenX: number, screenY: number, delta: number) {
    const worldPos = this.screenToWorld(screenX, screenY)
    const oldZoom = this.zoom
    this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom + delta))
    const zoomRatio = this.zoom / oldZoom
    this.x = worldPos.x - (worldPos.x - this.x) * zoomRatio
    this.y = worldPos.y - (worldPos.y - this.y) * zoomRatio
  }

  resetView() {
    this.x = 0
    this.y = 0
    this.zoom = 1.0
  }

  resize(width: number, height: number) {
    this.screenWidth = width
    this.screenHeight = height
  }
}
