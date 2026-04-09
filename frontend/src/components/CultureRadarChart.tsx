// file: src/components/CultureRadarChart.tsx
import { useEffect, useRef } from 'react'

type CultureRadarChartProps = {
  values: number[]
}

const labels = [
  '希少性',
  'ストリート',
  'SNS',
  'コラボ',
  'ブランド',
  'アスリート',
  'テック',
  'ヴィンテージ',
  '流動性',
  'モメンタム',
  'スタイル',
  '文化遺産',
  'デザイン',
  '素材',
  '限定性',
]

export function CultureRadarChart({ values }: CultureRadarChartProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) {
      return
    }

    const context = canvas.getContext('2d')
    if (!context) {
      return
    }

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) / 2 - 36
    const axisCount = labels.length

    context.clearRect(0, 0, width, height)

    for (let ring = 1; ring <= 5; ring += 1) {
      context.beginPath()
      for (let axis = 0; axis < axisCount; axis += 1) {
        const angle = (axis / axisCount) * Math.PI * 2 - Math.PI / 2
        const ringRadius = (ring / 5) * radius
        const x = centerX + ringRadius * Math.cos(angle)
        const y = centerY + ringRadius * Math.sin(angle)
        if (axis === 0) {
          context.moveTo(x, y)
        } else {
          context.lineTo(x, y)
        }
      }
      context.closePath()
      context.strokeStyle = 'rgba(0,200,255,0.1)'
      context.lineWidth = 0.6
      context.stroke()
    }

    for (let axis = 0; axis < axisCount; axis += 1) {
      const angle = (axis / axisCount) * Math.PI * 2 - Math.PI / 2
      context.beginPath()
      context.moveTo(centerX, centerY)
      context.lineTo(centerX + radius * Math.cos(angle), centerY + radius * Math.sin(angle))
      context.strokeStyle = 'rgba(0,200,255,0.14)'
      context.lineWidth = 0.5
      context.stroke()
    }

    context.beginPath()
    for (let axis = 0; axis < axisCount; axis += 1) {
      const angle = (axis / axisCount) * Math.PI * 2 - Math.PI / 2
      const pointRadius = values[axis] * radius
      const x = centerX + pointRadius * Math.cos(angle)
      const y = centerY + pointRadius * Math.sin(angle)
      if (axis === 0) {
        context.moveTo(x, y)
      } else {
        context.lineTo(x, y)
      }
    }
    context.closePath()
    context.fillStyle = 'rgba(0,200,255,0.12)'
    context.fill()
    context.strokeStyle = '#00c8ff'
    context.lineWidth = 1.5
    context.stroke()

    for (let axis = 0; axis < axisCount; axis += 1) {
      const angle = (axis / axisCount) * Math.PI * 2 - Math.PI / 2
      const pointRadius = values[axis] * radius
      const x = centerX + pointRadius * Math.cos(angle)
      const y = centerY + pointRadius * Math.sin(angle)
      context.beginPath()
      context.arc(x, y, 2.8, 0, Math.PI * 2)
      context.fillStyle = '#00c8ff'
      context.fill()
    }

    context.font = '9px "Space Mono", monospace'
    context.fillStyle = '#8899bb'
    context.textAlign = 'center'
    for (let axis = 0; axis < axisCount; axis += 1) {
      const angle = (axis / axisCount) * Math.PI * 2 - Math.PI / 2
      const labelRadius = radius + 18
      const x = centerX + labelRadius * Math.cos(angle)
      const y = centerY + labelRadius * Math.sin(angle) + 3
      context.fillText(labels[axis], x, y)
    }
  }, [values])

  return <canvas className="radar-canvas" ref={canvasRef} width={320} height={280} />
}
