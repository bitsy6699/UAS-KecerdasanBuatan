import { useEffect, useRef, useCallback } from 'react'

const CHARS = '⠁⠂⠄⠈⠐⠠⡀⢀⠃⠅⠘⠨⠊⠋⠌⠍⠎⠏⠑⠒⠓⠔⠕⠖⠗⠙⠚⠛⠜⠝⠞⠟⠡⠢⠣⠤⠥⠦⠧⠩⠪⠫⠬⠭⠮⠯⠱⠲⠳⠴⠵⠶⠷⠹⠺⠻⠼⠽⠾⠿'

export default function BlinkingAsciiDots({
  backgroundColor = '#1a1a1a',
  textColor = '220, 38, 38',
  density = 1,
  animationSpeed = 0.75,
  removeWaveLine = true,
}: {
  backgroundColor?: string
  textColor?: string
  density?: number
  animationSpeed?: number
  removeWaveLine?: boolean
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const mouseRef = useRef({ x: 0, y: 0, isDown: false })
  const timeRef = useRef(0)
  const animationFrameId = useRef(0)
  const clickWaves = useRef<{ x: number; y: number; time: number; intensity: number }[]>([])

  const calculateGrid = useCallback(() => {
    if (!containerRef.current) return { cols: 0, rows: 0, cellSize: 0 }
    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight
    const baseCellSize = 16
    const cellSize = baseCellSize / density
    const cols = Math.ceil(width / cellSize)
    const rows = Math.ceil(height / cellSize)
    return { cols, rows, cellSize }
  }, [density])

  const handleResize = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || !containerRef.current) return
    canvas.width = containerRef.current.clientWidth
    canvas.height = containerRef.current.clientHeight
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    mouseRef.current.x = e.clientX - rect.left
    mouseRef.current.y = e.clientY - rect.top
  }, [])

  const handleMouseDown = useCallback((e: MouseEvent) => {
    mouseRef.current.isDown = true
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    clickWaves.current.push({ x, y, time: Date.now(), intensity: 2.5 })
    const now = Date.now()
    clickWaves.current = clickWaves.current.filter(w => now - w.time < 5000)
  }, [])

  const handleMouseUp = useCallback(() => {
    mouseRef.current.isDown = false
  }, [])

  const getWaveValue = useCallback((x: number, y: number, time: number) => {
    const w1 = Math.sin(x * 0.05 + time * 0.5) * Math.cos(y * 0.05 - time * 0.3)
    const w2 = Math.sin((x + y) * 0.04 + time * 0.7) * 0.5
    const w3 = Math.cos(x * 0.06 - y * 0.06 + time * 0.4) * 0.3
    return (w1 + w2 + w3) / 2
  }, [])

  const getClickWaveInfluence = useCallback((x: number, y: number, currentTime: number) => {
    let total = 0
    for (const wave of clickWaves.current) {
      const age = currentTime - wave.time
      if (age < 5000) {
        const dx = x - wave.x
        const dy = y - wave.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        const radius = (age / 5000) * 500
        const width = 100
        if (Math.abs(dist - radius) < width) {
          const strength = (1 - age / 5000) * wave.intensity
          const proximity = 1 - Math.abs(dist - radius) / width
          total += strength * proximity * Math.sin((dist - radius) * 0.05)
        }
      }
    }
    return total
  }, [])

  const getMouseInfluence = useCallback((x: number, y: number) => {
    const dx = x - mouseRef.current.x
    const dy = y - mouseRef.current.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    return Math.max(0, 1 - dist / 200)
  }, [])

  const animate = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || !containerRef.current) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const currentTime = Date.now()
    timeRef.current += animationSpeed * 0.016
    const { cols, rows, cellSize } = calculateGrid()

    ctx.fillStyle = backgroundColor
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.font = `${cellSize}px monospace`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'

    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const posX = x * cellSize + cellSize / 2
        const posY = y * cellSize + cellSize / 2

        let waveValue = getWaveValue(posX, posY, timeRef.current)

        const mouseInfluence = getMouseInfluence(posX, posY)
        if (mouseInfluence > 0) {
          waveValue += mouseInfluence * Math.sin(timeRef.current * 3) * 0.5
        }

        waveValue += getClickWaveInfluence(posX, posY, currentTime)

        const normalizedValue = (waveValue + 1) / 2
        if (Math.abs(waveValue) > 0.15) {
          const idx = Math.floor(normalizedValue * CHARS.length)
          const char = CHARS[Math.min(CHARS.length - 1, Math.max(0, idx))]
          const opacity = Math.min(0.9, Math.max(0.3, 0.4 + normalizedValue * 0.5))
          ctx.fillStyle = `rgba(${textColor}, ${opacity})`
          ctx.fillText(char, posX, posY)
        }
      }
    }

    animationFrameId.current = requestAnimationFrame(animate)
  }, [backgroundColor, textColor, animationSpeed, calculateGrid, getWaveValue, getClickWaveInfluence, getMouseInfluence, removeWaveLine])

  useEffect(() => {
    if (!containerRef.current) return
    handleResize()
    window.addEventListener('resize', handleResize)
    containerRef.current.addEventListener('mousemove', handleMouseMove)
    containerRef.current.addEventListener('mousedown', handleMouseDown)
    containerRef.current.addEventListener('mouseup', handleMouseUp)
    animate()

    return () => {
      window.removeEventListener('resize', handleResize)
      if (containerRef.current) {
        containerRef.current.removeEventListener('mousemove', handleMouseMove)
        containerRef.current.removeEventListener('mousedown', handleMouseDown)
        containerRef.current.removeEventListener('mouseup', handleMouseUp)
      }
      cancelAnimationFrame(animationFrameId.current)
    }
  }, [animate, handleResize, handleMouseMove, handleMouseDown, handleMouseUp])

  return (
    <div
      ref={containerRef}
      className="ascii-dots-bg"
      style={{ backgroundColor }}
    >
      <canvas ref={canvasRef} style={{ display: 'block', width: '100%', height: '100%' }} />
    </div>
  )
}
