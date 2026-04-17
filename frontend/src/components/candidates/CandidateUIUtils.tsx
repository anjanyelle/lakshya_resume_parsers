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
    '#fb923c', // Brand Light
    '#f97316', // Brand
    '#0ea5e9', // Blue
    '#10b981', // Emerald
  ]
  const idx = (name?.charCodeAt(0) ?? 0) % colors.length
  return colors[idx]
}

export function formatScore(score?: number | null) {
  if (score == null) return null
  return score > 1 ? Math.round(score) : Math.round(score * 100)
}

export function formatRelativeTime(dateString?: string | null) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`

  return date.toLocaleDateString()
}

export function ScoreBadge({ value, size = 44 }: ScoreBadgeProps) {
  const [animatedValue, setAnimatedValue] = React.useState(0)

  React.useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 100)
    return () => clearTimeout(timer)
  }, [value])

  const radius = size * 0.42
  const stroke = size * 0.1
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (animatedValue / 100) * circumference

  return (
    <div
      title={`Match Score: ${value}%`}
      className="relative flex items-center justify-center transition-all duration-500 group"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="rotate-[-90deg] relative z-10 transition-transform duration-700 group-hover:rotate-0">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="currentColor"
          strokeWidth={stroke}
          className="text-slate-100 dark:text-slate-800"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="currentColor"
          strokeWidth={stroke}
          className="text-slate-100 dark:text-slate-800"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="currentColor"
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="text-brand-500 transition-all duration-1000 ease-[cubic-bezier(0.34, 1.56, 0.64, 1)]"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center z-20">
        <span className="text-[11px] font-black text-brand-600 dark:text-brand-400 tracking-tight">
          {value}%
        </span>
      </div>
    </div>
  )
}

export function Gauge({ value, size = 42 }: { value: number; size?: number }) {
  return <ScoreBadge value={value} size={size} />
}

export function ProcessingGauge({ value, size = 200 }: { value: number; size?: number }) {
  const angle = -90 + (value * 1.8)
  const radius = 42
  const strokeWidth = 8
  const center = 50

  // Calculate arc path for SVG
  const arcPath = `M ${center - radius} ${center} A ${radius} ${radius} 0 0 1 ${center + radius} ${center}`

  // Calculate stroke-dasharray for progress
  const circumference = Math.PI * radius
  const strokeDashoffset = circumference - (value / 100) * circumference

  return (
    <div className="relative flex flex-col items-center justify-center select-none group" style={{ width: size, height: size / 1.6 }}>
      <svg
        viewBox="0 0 100 60"
        className="w-full h-full drop-shadow-2xl overflow-visible"
      >
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f97316" />
            <stop offset="100%" stopColor="#fb923c" />
          </linearGradient>
          <filter id="needleShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="1" />
            <feOffset dx="0" dy="1" result="offsetblur" />
            <feComponentTransfer>
              <feFuncA type="linear" slope="0.3" />
            </feComponentTransfer>
            <feMerge>
              <feMergeNode />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background Arc */}
        <path
          d={arcPath}
          fill="none"
          stroke="currentColor"
          className="text-slate-100 dark:text-slate-800"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Progress Arc */}
        <path
          d={arcPath}
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className="transition-all duration-700 ease-out"
        />

        {/* Start/End Ticks */}
        <line x1={center - radius} y1={center} x2={center - radius + 2} y2={center} stroke="currentColor" className="text-slate-300 dark:text-slate-600" strokeWidth="1" />
        <line x1={center + radius} y1={center} x2={center + radius - 2} y2={center} stroke="currentColor" className="text-slate-300 dark:text-slate-600" strokeWidth="1" />

        {/* Needle */}
        <g
          transform={`rotate(${angle}, ${center}, ${center})`}
          className="transition-transform duration-1000"
          style={{ transitionTimingFunction: 'cubic-bezier(0.34, 1.56, 0.64, 1)' }}
          filter="url(#needleShadow)"
        >
          {/* Needle Base Pin */}
          <circle cx={center} cy={center} r="3" fill="currentColor" stroke="white" className="text-slate-600 dark:text-slate-400" strokeWidth="1.5" />
          {/* The Needle Tip */}
          <path
            d={`M ${center - 1.5} ${center} L ${center} ${center - radius + 10} L ${center + 1.5} ${center} Z`}
            fill="currentColor"
            className="text-slate-600 dark:text-slate-400"
          />
        </g>

        {/* Percentage Text - Inside Arc */}
        <text
          x={center}
          y={center - 10}
          textAnchor="middle"
          className="fill-slate-600 dark:fill-slate-200 font-extrabold text-[15px] tracking-tight"
        >
          {Math.round(value)}%
        </text>
      </svg>

    </div>
  )
}

export function SkillChip({ name, experience, source }: { name: string; experience?: number | string | null; source?: string | null }) {
  return (
    <div className="flex items-center gap-1.5 rounded-lg border border-emerald-200/60 dark:border-emerald-500/20 bg-emerald-50/40 dark:bg-emerald-500/10 px-2.5 py-1 transition-all hover:scale-[1.02] hover:bg-emerald-50/60 dark:hover:bg-emerald-500/20 group shadow-sm">
      <span className="text-[11px] font-bold text-emerald-700 dark:text-emerald-400 leading-none">
        {name}
      </span>

      {experience && (
        <div className="flex items-center justify-center rounded bg-emerald-100/50 dark:bg-emerald-500/20 px-1 py-0.5 min-w-[18px]">
          <span className="text-[9px] font-black text-emerald-800/60 dark:text-emerald-400/60 leading-none">
            {experience}x
          </span>
        </div>
      )}

      {source === 'llm' && !experience && (
        <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shadow-[0_0_5px_rgba(251,191,36,0.5)]" title="AI Suggested" />
      )}
    </div>
  )
}
