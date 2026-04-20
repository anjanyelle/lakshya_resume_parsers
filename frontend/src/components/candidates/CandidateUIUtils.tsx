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

export function formatRelativeTime(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (isNaN(date.getTime())) return '—'
  if (diffInSeconds < 60) return 'Just now'
  
  const minutes = Math.floor(diffInSeconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} hours ago`
  
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} days ago`
  
  const weeks = Math.floor(days / 7)
  if (weeks < 4) return `${weeks} weeks ago`

  return date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric' })
}

interface ScoreBadgeProps {
  value: number
  size?: number
}

export function ScoreBadge({ value, size = 42 }: ScoreBadgeProps) {
  // Color configuration based on score
  let theme = {
    bg: 'bg-emerald-50/60',
    border: 'border-emerald-200/60',
    text: 'text-emerald-500',
    glow: 'shadow-emerald-200/40',
    gradient: 'from-emerald-400 to-teal-500',
    label: 'Match'
  }

  if (value < 50) {
    theme = {
      bg: 'bg-rose-50/60',
      border: 'border-rose-200/60',
      text: 'text-rose-500',
      glow: 'shadow-rose-200/40',
      gradient: 'from-rose-400 to-pink-500',
      label: 'Poor'
    }
  } else if (value < 80) {
    theme = {
      bg: 'bg-orange-50/60',
      border: 'border-orange-200/60',
      text: 'text-orange-500',
      glow: 'shadow-orange-200/40',
      gradient: 'from-orange-400 to-amber-500',
      label: 'Good'
    }
  }

  const isCompact = size < 40

  return (
    <div
      className={`relative flex items-center justify-center overflow-hidden rounded-xl border backdrop-blur-md transition-all duration-300 group hover:scale-[1.02] shadow-sm ${theme.bg} ${theme.border} ${theme.glow}`}
      style={{
        width: isCompact ? 'auto' : size * 2.2,
        height: size * 0.85,
        padding: isCompact ? '0 8px' : '0 12px'
      }}
    >
      {/* Dynamic Background Glow */}
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 bg-gradient-to-br ${theme.gradient} transition-opacity duration-500`} />

      <div className="relative flex items-center gap-2">
        {!isCompact && (
          <span className={`text-[8px] font-black uppercase tracking-[0.2em] opacity-50 ${theme.text}`}>
            {theme.label}
          </span>
        )}

        <div className="flex items-baseline gap-0.5">
          <span className={`text-[16px] font-black tracking-tight leading-none bg-clip-text text-transparent bg-gradient-to-br ${theme.gradient} drop-shadow-sm`}>
            {value}
          </span>
          <span className={`text-[9px] font-black bg-clip-text text-transparent bg-gradient-to-br ${theme.gradient} opacity-80`}>%</span>
        </div>
      </div>

      {/* Micro-Progress Underline */}
      <div className="absolute bottom-0 left-0 h-[2.5px] w-full bg-white/40">
        <div
          className={`h-full bg-gradient-to-r ${theme.gradient} transition-all duration-1000 ease-out shadow-[0_0_8px_rgba(0,0,0,0.1)]`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}

export function Gauge({ value, size = 42 }: { value: number; size?: number }) {
  return <ScoreBadge value={value} size={size} />
}

