import { useEffect, useMemo } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts'
import { useCandidateStore } from '../store/candidateStore'
import { BarChart2 } from 'lucide-react'

const SCORE_RANGES = [
  { range: '0-20', min: 0, max: 0.2, color: '#ef4444' },
  { range: '21-40', min: 0.2, max: 0.4, color: '#f97316' },
  { range: '41-60', min: 0.4, max: 0.6, color: '#f59e0b' },
  { range: '61-80', min: 0.6, max: 0.8, color: '#3b82f6' },
  { range: '81-100', min: 0.8, max: 1.01, color: '#10b981' },
]

export default function AnalyticsPage() {
  const { candidates, loadCandidates } = useCandidateStore()

  useEffect(() => {
    const controller = new AbortController()
    loadCandidates(controller.signal)
    return () => controller.abort()
  }, [loadCandidates])

  // --- Compute stats from real data ---
  const totalCandidates = candidates.length
  const successCandidates = candidates.filter((c) => c.status === 'success')

  const scores = successCandidates
    .map((c) => c.parsing_jobs?.[0]?.confidence_score)
    .filter((s): s is number => typeof s === 'number')

  const avgScore =
    scores.length > 0
      ? Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 100)
      : null

  const successRate =
    totalCandidates > 0
      ? Math.round((successCandidates.length / totalCandidates) * 100)
      : null

  // Top Skill
  const skillMap: Record<string, number> = {}
  candidates.forEach((c) => {
    ;(c.skills ?? []).forEach((s) => {
      skillMap[s.name] = (skillMap[s.name] ?? 0) + 1
    })
  })
  const topSkill =
    Object.entries(skillMap).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null

  // Score distribution from real data
  const scoreDistData = SCORE_RANGES.map(({ range, min, max, color }) => ({
    range,
    count: scores.filter((s) => s >= min && s < max).length,
    color,
  }))

  // Weekly data: group candidates by day of week created_at
  const weeklyData = useMemo(() => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    const dayMap: Record<string, { applications: number; analyzed: number }> = {}
    days.forEach((d) => { dayMap[d] = { applications: 0, analyzed: 0 } })

    candidates.forEach((c) => {
      const d = new Date(c.created_at)
      // getDay(): 0=Sun, 1=Mon...6=Sat
      const dayIdx = d.getDay()
      // Reorder to Mon-Sun
      const dayName = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][dayIdx]
      if (dayName in dayMap) {
        dayMap[dayName].applications += 1
        if (c.status === 'success') dayMap[dayName].analyzed += 1
      }
    })

    // Return in Mon-Sun order
    return days.map((day) => ({ day, ...dayMap[day] }))
  }, [candidates])

  const summaryStats = [
    {
      label: 'Total Candidates',
      value: totalCandidates > 0 ? String(totalCandidates) : '—',
      sub: 'All time',
    },
    {
      label: 'Avg. ATS Score',
      value: avgScore != null ? `${avgScore}%` : '—',
      sub: 'Across all resumes',
    },
    {
      label: 'Top Skill',
      value: topSkill ?? '—',
      sub: 'Most detected',
    },
    {
      label: 'Processing Rate',
      value: successRate != null ? `${successRate}%` : '—',
      sub: 'Success rate',
    },
  ]

  const hasAnyData = totalCandidates > 0

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {summaryStats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl bg-white p-4 shadow-card border border-slate-100"
          >
            <p className="text-xs text-slate-400">{stat.sub}</p>
            <p className="mt-1 text-2xl font-bold text-slate-800">{stat.value}</p>
            <p className="mt-0.5 text-xs font-medium text-slate-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Weekly Activity Chart */}
      <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
        <h3 className="mb-4 text-sm font-semibold text-slate-800">Weekly Activity</h3>
        {hasAnyData ? (
          <>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={weeklyData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="appGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id="anaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }} />
                <Area type="monotone" dataKey="applications" stroke="#7c3aed" strokeWidth={2} fill="url(#appGrad)" name="Applications" />
                <Area type="monotone" dataKey="analyzed" stroke="#14b8a6" strokeWidth={2} fill="url(#anaGrad)" name="Analyzed" />
              </AreaChart>
            </ResponsiveContainer>
            <div className="mt-2 flex items-center gap-4 justify-center">
              <span className="flex items-center gap-1.5 text-xs text-slate-500">
                <span className="h-2 w-2 rounded-full bg-violet-500" /> Applications
              </span>
              <span className="flex items-center gap-1.5 text-xs text-slate-500">
                <span className="h-2 w-2 rounded-full bg-teal-500" /> Analyzed
              </span>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <BarChart2 className="h-10 w-10 text-slate-200 mb-3" />
            <p className="text-sm text-slate-400">No activity data yet</p>
            <p className="text-xs text-slate-300 mt-1">Upload resumes to see weekly trends</p>
          </div>
        )}
      </div>

      {/* Score Distribution */}
      <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
        <h3 className="mb-4 text-sm font-semibold text-slate-800">Score Distribution</h3>
        {scores.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={scoreDistData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="range" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]} name="Candidates">
                {scoreDistData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <BarChart2 className="h-10 w-10 text-slate-200 mb-3" />
            <p className="text-sm text-slate-400">No score data yet</p>
            <p className="text-xs text-slate-300 mt-1">Scores will appear after resumes are analyzed</p>
          </div>
        )}
      </div>
    </div>
  )
}
