import React from 'react'

export function getInitials(name?: string | null) {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
}

export function getScoreColor(score: number) {
  if (score >= 80) return '#10b981' // Green
  if (score >= 50) return '#f59e0b' // Yellow (Amber)
  return '#ef4444' // Red
}

export function getAvatarColor(name?: string | null) {
  const colors = [
    '#ec4899', // Pink
    '#f97316', // Orange
    '#7c3aed', // Violet
    '#10b981', // Emerald
    '#3b82f6', // Blue
  ]
  const idx = (name?.charCodeAt(0) ?? 0) % colors.length
  return colors[idx]
}

export function formatScore(score?: number | null) {
  if (score == null) return null
  return score > 1 ? Math.round(score) : Math.round(score * 100)
}

interface GaugeProps {
  value: number
  size?: number
}

export function Gauge({ value, size = 42 }: GaugeProps) {
  const radius = size * 0.4
  const strokeWidth = 5
  const center = size / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference
  const color = getScoreColor(value)

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90 overflow-visible">
        <defs>
          <filter id="gauge-shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="1" />
            <feOffset dx="0" dy="0" result="offsetblur" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.3" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#f8fafc"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          filter="url(#gauge-shadow)"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center translate-y-[-0.5px]">
        <span className="text-[11px] font-black tracking-tighter" style={{ color }}>
          {Math.round(value)}%
        </span>
      </div>
    </div>
  )
}
