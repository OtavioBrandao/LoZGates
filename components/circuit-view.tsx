"use client"

import { useEffect, useRef, useCallback } from "react"
import { Camera } from "@/lib/circuit/camera"
import { renderStaticCircuit } from "@/lib/circuit/renderer"

export function CircuitView({ expression }: { expression: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const cameraRef = useRef<Camera | null>(null)
  const animationRef = useRef<number>(0)

  const render = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return
    const camera = cameraRef.current
    if (!camera) return

    renderStaticCircuit(ctx, expression, canvas.width, canvas.height, camera)
  }, [expression])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const resize = () => {
      const rect = canvas.getBoundingClientRect()
      const dpr = window.devicePixelRatio || 1
      canvas.width = rect.width * dpr
      canvas.height = rect.height * dpr
      const ctx = canvas.getContext("2d")
      if (ctx) ctx.scale(dpr, dpr)
      if (cameraRef.current) cameraRef.current.resize(rect.width, rect.height)
      render()
    }

    const rect = canvas.getBoundingClientRect()
    cameraRef.current = new Camera(rect.width, rect.height)

    resize()
    const obs = new ResizeObserver(resize)
    obs.observe(canvas.parentElement!)

    return () => {
      obs.disconnect()
      cancelAnimationFrame(animationRef.current)
    }
  }, [render])

  // Mouse handlers for pan/zoom
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const camera = cameraRef.current
    if (!camera) return

    let dragging = false
    let lastPos = { x: 0, y: 0 }

    const onMouseDown = (e: MouseEvent) => {
      if (e.button === 0) {
        dragging = true
        lastPos = { x: e.clientX, y: e.clientY }
      }
    }
    const onMouseUp = () => { dragging = false }
    const onMouseMove = (e: MouseEvent) => {
      if (!dragging) return
      camera.move(-(e.clientX - lastPos.x), -(e.clientY - lastPos.y))
      lastPos = { x: e.clientX, y: e.clientY }
      render()
    }
    const onWheel = (e: WheelEvent) => {
      e.preventDefault()
      const rect = canvas.getBoundingClientRect()
      camera.zoomAt(e.clientX - rect.left, e.clientY - rect.top, e.deltaY > 0 ? -0.1 : 0.1)
      render()
    }
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "r" || e.key === "R") {
        camera.resetView()
        render()
      }
    }

    canvas.addEventListener("mousedown", onMouseDown)
    window.addEventListener("mouseup", onMouseUp)
    canvas.addEventListener("mousemove", onMouseMove)
    canvas.addEventListener("wheel", onWheel, { passive: false })
    window.addEventListener("keydown", onKeyDown)

    // Touch
    let lastTouch = { x: 0, y: 0 }
    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        dragging = true
        lastTouch = { x: e.touches[0].clientX, y: e.touches[0].clientY }
      }
    }
    const onTouchMove = (e: TouchEvent) => {
      if (!dragging || e.touches.length !== 1) return
      const dx = e.touches[0].clientX - lastTouch.x
      const dy = e.touches[0].clientY - lastTouch.y
      camera.move(-dx, -dy)
      lastTouch = { x: e.touches[0].clientX, y: e.touches[0].clientY }
      render()
    }
    const onTouchEnd = () => { dragging = false }

    canvas.addEventListener("touchstart", onTouchStart, { passive: true })
    canvas.addEventListener("touchmove", onTouchMove, { passive: true })
    canvas.addEventListener("touchend", onTouchEnd)

    return () => {
      canvas.removeEventListener("mousedown", onMouseDown)
      window.removeEventListener("mouseup", onMouseUp)
      canvas.removeEventListener("mousemove", onMouseMove)
      canvas.removeEventListener("wheel", onWheel)
      window.removeEventListener("keydown", onKeyDown)
      canvas.removeEventListener("touchstart", onTouchStart)
      canvas.removeEventListener("touchmove", onTouchMove)
      canvas.removeEventListener("touchend", onTouchEnd)
    }
  }, [render])

  return (
    <div className="flex flex-col gap-2">
      <div className="relative w-full overflow-hidden rounded-lg border border-border" style={{ height: "400px" }}>
        <canvas ref={canvasRef} className="h-full w-full cursor-grab active:cursor-grabbing" />
        <div className="pointer-events-none absolute bottom-2 left-2 rounded-md bg-background/80 px-2 py-1 text-xs text-muted-foreground backdrop-blur-sm">
          Arrastar: mover | Scroll: zoom | R: resetar
        </div>
      </div>
    </div>
  )
}
