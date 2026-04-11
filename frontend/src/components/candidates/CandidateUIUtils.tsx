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
  const strokeWidth = size * 0.12
  const center = size / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference
  
  // Decide colors and gradient IDs
  let gradientId = 'grad-red'
  let textColor = '#f43f5e'
  if (value >= 80) {
    gradientId = 'grad-green'
    textColor = '#0d9488' // Teal 600
  } else if (value >= 50) {
    gradientId = 'grad-amber'
    textColor = '#d97706' // Amber 600
  }

  return (
    <div className="relative flex items-center justify-center group" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90 overflow-visible drop-shadow-sm transition-transform duration-500 group-hover:scale-110">
        <defs>
          <linearGradient id="grad-green" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#2dd4bf" />
            <stop offset="50%" stopColor="#14b8a6" />
            <stop offset="100%" stopColor="#0d9488" />
          </linearGradient>
          <linearGradient id="grad-amber" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fbbf24" />
            <stop offset="50%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#d97706" />
          </linearGradient>
          <linearGradient id="grad-red" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fb7185" />
            <stop offset="50%" stopColor="#f43f5e" />
            <stop offset="100%" stopColor="#e11d48" />
          </linearGradient>
          
          <filter id="gauge-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="1.2" result="blur" />
            <feFlood floodColor="white" floodOpacity="0.3" result="glowColor" />
            <feComposite in="glowColor" in2="blur" operator="in" result="softGlow" />
            <feMerge>
              <feMergeNode in="softGlow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        
        {/* Track (Background Case) */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#f1f5f9"
          strokeWidth={strokeWidth}
        />
        
        {/* Inner Groove */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={strokeWidth * 0.3}
          opacity="0.5"
        />
        
        {/* Progress Arc */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          filter="url(#gauge-glow)"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      
      {/* Percentage Text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center translate-y-[0.5px]">
        <span className="text-[9px] font-black tracking-tight leading-none" style={{ color: textColor }}>
          {Math.round(value)}
        </span>
        <span className="text-[5.5px] font-bold opacity-30 uppercase tracking-widest mt-0.5" style={{ color: textColor }}>%</span>
      </div>
    </div>
  )
}
