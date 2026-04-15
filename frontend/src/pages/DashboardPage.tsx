import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  Users,
  Star,
  Clock,
  TrendingUp,
  TrendingDown,
  MoreVertical,
  Eye,
  Download,
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts'
import { useCandidateStore } from '../store/candidateStore'
import { useTheme } from '../contexts/ThemeContext'
import { useAuthStore } from '../store/authStore'

const SKILL_COLORS = ['#7c3aed', '#14b8a6', '#6366f1', '#f97316', '#ef4444', '#eab308']

// Helper components
function getInitials(name?: string | null) {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function getAvatarColor(name?: string | null) {
  const colors = [
    'linear-gradient(135deg,#7c3aed,#a78bfa)',
    'linear-gradient(135deg,#14b8a6,#2dd4bf)',
    'linear-gradient(135deg,#f97316,#fb923c)',
    'linear-gradient(135deg,#ec4899,#f472b6)',
    'linear-gradient(135deg,#3b82f6,#60a5fa)',
    'linear-gradient(135deg,#10b981,#34d399)',
  ]
  const idx = (name?.charCodeAt(0) ?? 0) % colors.length
  return colors[idx]
}

function getScoreColor(score?: number | null) {
  if (!score) return '#94a3b8'
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

function CountUp({ end, duration = 1000, suffix = '' }: { end: number; duration?: number; suffix?: string }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTimestamp: number | null = null
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / duration, 1)
      setCount(Math.floor(progress * end))
      if (progress < 1) {
        window.requestAnimationFrame(step)
      }
    }
    window.requestAnimationFrame(step)
  }, [end, duration])

  return <span>{count}{suffix}</span>
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { candidates, loadCandidates } = useCandidateStore()
  const { theme } = useTheme()
  const { user } = useAuthStore()
  const [skillData, setSkillData] = useState<{ name: string; value: number }[]>([])

  // Functionality: Dynamic data mapping for charts
  const dynamicMonthlyData = useMemo(() => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    const now = new Date()
    const last6 = []
    for (let i = 5; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
      last6.push({
        month: months[d.getMonth()],
        fullMonth: d.getMonth(),
        year: d.getFullYear(),
        value: 0
      })
    }
    candidates.forEach(c => {
      const created = new Date(c.created_at)
      const match = last6.find(m => m.fullMonth === created.getMonth() && m.year === created.getFullYear())
      if (match) match.value += 1
    })
    return last6
  }, [candidates])

  const dynamicScoreDistData = useMemo(() => {
    const ranges = [
      { range: '0-20', count: 0 },
      { range: '21-40', count: 0 },
      { range: '41-60', count: 0 },
      { range: '61-80', count: 0 },
      { range: '81-100', count: 0 },
    ]
    candidates.forEach(c => {
      const score = (c.parsing_jobs?.[0]?.confidence_score || 0) * 100
      if (score <= 20) ranges[0].count++
      else if (score <= 40) ranges[1].count++
      else if (score <= 60) ranges[2].count++
      else if (score <= 80) ranges[3].count++
      else ranges[4].count++
    })
    return ranges
  }, [candidates])

  // Functionality: Polling logic
  useEffect(() => {
    const controller = new AbortController()
    loadCandidates(controller.signal)
    const interval = window.setInterval(() => loadCandidates(), 10000)
    return () => {
      controller.abort()
      window.clearInterval(interval)
    }
  }, [loadCandidates])

  // Compute stats from real data
  const totalResumes = candidates.length
  const analyzedCandidates = candidates.filter((c) => c.status === 'success' || c.status === 'completed').length
  const scores = candidates
    .map((c) => c.parsing_jobs?.[0]?.confidence_score)
    .filter((s): s is number => typeof s === 'number')
  const avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length * 100) : 0
  const avgProcessingDays =
    candidates.length > 0
      ? Math.round(
        candidates.reduce((sum, c) => {
          const created = new Date(c.created_at).getTime()
          const updated = new Date(c.updated_at).getTime()
          return sum + (updated - created) / (1000 * 60 * 60 * 24)
        }, 0) / candidates.length,
      )
      : 0

  // Compute skill frequency
  useEffect(() => {
    const skillMap: Record<string, number> = {}
    candidates.forEach((c) => {
      ; (c.skills ?? []).forEach((s) => {
        skillMap[s.name] = (skillMap[s.name] ?? 0) + 1
      })
    })
    const sorted = Object.entries(skillMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([name, value]) => ({ name, value }))
    setSkillData(sorted)
  }, [candidates])

  const recentResumes = [...candidates]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3)

  const statsCards = [
    {
      label: 'Total Resumes',
      value: totalResumes,
      display: totalResumes > 0 ? <CountUp end={totalResumes} /> : '—',
      trend: '+12.5%',
      up: true,
      icon: FileText,
      colors: 'from-orange-500 to-orange-600',
      shadow: 'shadow-orange-200/50 dark:shadow-orange-900/20',
      glow: 'group-hover:shadow-orange-500/40',
    },
    {
      label: 'Analyzed Candidates',
      value: analyzedCandidates,
      display: analyzedCandidates > 0 ? <CountUp end={analyzedCandidates} /> : '—',
      trend: '+8.2%',
      up: true,
      icon: Users,
      colors: 'from-teal-400 to-emerald-600',
      shadow: 'shadow-emerald-200/50 dark:shadow-emerald-900/20',
      glow: 'group-hover:shadow-emerald-500/40',
    },
    {
      label: 'Avg. Match Score',
      value: avgScore,
      display: avgScore > 0 ? <CountUp end={avgScore} suffix="%" /> : '—',
      trend: '+5.4%',
      up: true,
      icon: Star,
      colors: 'from-amber-400 to-orange-500',
      shadow: 'shadow-orange-200/50 dark:shadow-orange-900/20',
      glow: 'group-hover:shadow-orange-500/40',
    },
    {
      label: 'Avg. Processing Time',
      value: avgProcessingDays,
      display: candidates.length > 0 ? <CountUp end={avgProcessingDays} suffix=" days" /> : '—',
      trend: '-2.1%',
      up: false,
      icon: Clock,
      colors: 'from-blue-400 to-indigo-500',
      shadow: 'shadow-blue-200/50 dark:shadow-blue-900/20',
      glow: 'group-hover:shadow-blue-500/40',
    },
  ]

  const chartTheme = theme === 'dark' ? {
    text: '#94a3b8',
    grid: '#334155',
    bg: '#1e293b',
    border: '#475569'
  } : {
    text: '#64748b',
    grid: '#f1f5f9',
    bg: '#ffffff',
    border: '#e2e8f0'
  }

  const timeGreeting = useMemo(() => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Morning'
    if (hour < 17) return 'Afternoon'
    return 'Evening'
  }, [])

  const displayName = useMemo(() => {
    if (user?.full_name) return user.full_name
    if (user?.name) return user.name
    const emailPrefix = user?.email.split('@')[0] || 'User'
    return emailPrefix.charAt(0).toUpperCase() + emailPrefix.slice(1)
  }, [user])

  return (
    <div className="space-y-6 animate-fade-in pb-10">
      {/* Welcome Greeting */}
      <div className="flex flex-col gap-0.5">
        <p className="text-[14px] font-black text-slate-500 uppercase tracking-[0.2em] select-none">Welcome</p>
        <h2 className="text-xl font-bold text-slate-700 dark:text-slate-100 tracking-tight flex items-center gap-3">
          Good {timeGreeting}, {displayName}
          <span className="animate-wave inline-block origin-[70%_70%]">👋</span>
        </h2>
        <p className="text-[13px] font-medium text-slate-400 dark:text-slate-500">
          Here's an overview of your resume analysis activity.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.label}
              className={`group relative overflow-hidden rounded-2xl bg-white dark:bg-slate-800/50 p-4 border border-slate-100 dark:border-slate-700/50 shadow-md ${stat.shadow} transition-all duration-500 hover:-translate-y-1 hover:shadow-xl ${stat.glow} cursor-pointer backdrop-blur-sm`}
            >
              <div className={`absolute -right-6 -top-6 h-20 w-20 rounded-full bg-gradient-to-br ${stat.colors} opacity-[0.05] group-hover:opacity-[0.1] group-hover:scale-150 transition-all duration-700 blur-2xl`} />

              <div className="flex items-start justify-between relative z-10">
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-xl text-white shadow-md bg-gradient-to-br ${stat.colors} ring-4 ring-white dark:ring-slate-700/50 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3`}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-black tracking-tight transition-all duration-300 ${stat.up
                  ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                  : 'bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400'
                  }`}>
                  {stat.up ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {stat.trend}
                </div>
              </div>

              <div className="mt-4 relative z-10">
                <h3 className="text-2xl font-bold text-slate-700 dark:text-slate-100 tracking-tighter transition-colors leading-none">
                  {stat.display}
                </h3>
                <p className="mt-1.5 text-[8.5px] font-black text-slate-300 dark:text-slate-500 uppercase tracking-[0.2em] leading-none">
                  {stat.label}
                </p>
              </div>

              <div className={`absolute bottom-0 left-0 h-1 w-0 bg-gradient-to-r ${stat.colors} transition-all duration-700 group-hover:w-full opacity-40`} />
            </div>
          )
        })}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-[1.5rem] bg-white dark:bg-slate-800/50 p-6 shadow-xl border border-slate-100 dark:border-slate-700/50 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <div className="flex flex-col">
              <h3 className="text-[9px] font-black text-slate-300 dark:text-slate-500 uppercase tracking-[0.2em]">Application Velocity</h3>
              <p className="text-lg font-bold text-slate-700 dark:text-slate-100 mt-1">Monthly Analytics</p>
            </div>
            <button className="h-10 w-10 flex items-center justify-center rounded-xl text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
              <MoreVertical className="h-5 w-5" />
            </button>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={dynamicMonthlyData} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} vertical={false} />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 11, fill: chartTheme.text, fontWeight: 600 }}
                axisLine={false}
                tickLine={false}
                dy={10}
              />
              <YAxis
                tick={{ fontSize: 11, fill: chartTheme.text, fontWeight: 600 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 16,
                  backgroundColor: chartTheme.bg,
                  border: `1px solid ${chartTheme.border}`,
                  boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
                  color: chartTheme.text,
                }}
                itemStyle={{ color: '#0ea5e9', fontWeight: 800 }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#0ea5e9"
                strokeWidth={4}
                fill="url(#areaGrad)"
                animationDuration={2000}
                activeDot={{ r: 6, stroke: '#fff', strokeWidth: 3, shadow: '0 0 12px rgba(14, 165, 233, 0.5)' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-[1.5rem] bg-white dark:bg-slate-800/50 p-6 shadow-xl border border-slate-100 dark:border-slate-700/50 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <div className="flex flex-col">
              <h3 className="text-[9px] font-black text-slate-300 dark:text-slate-500 uppercase tracking-[0.2em]">Talent Composition</h3>
              <p className="text-lg font-bold text-slate-700 dark:text-slate-100 mt-1">Skill Distribution</p>
            </div>
            <button className="h-10 w-10 flex items-center justify-center rounded-xl text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
              <MoreVertical className="h-5 w-5" />
            </button>
          </div>
          <div className="flex flex-col md:flex-row items-center justify-center gap-10">
            <div className="relative">
              <PieChart width={200} height={200}>
                <Pie
                  data={skillData.length > 0 ? skillData : [
                    { name: 'Python', value: 2 },
                    { name: 'Django', value: 1 },
                    { name: 'PostgreSQL', value: 1 },
                    { name: 'Docker', value: 1 },
                    { name: 'JavaScript', value: 1 },
                  ]}
                  cx={100}
                  cy={100}
                  innerRadius={65}
                  outerRadius={95}
                  dataKey="value"
                  paddingAngle={5}
                  stroke="none"
                  animationDuration={1500}
                >
                  {SKILL_COLORS.map((color, index) => (
                    <Cell key={index} fill={color} />
                  ))}
                </Pie>
              </PieChart>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-2xl font-black text-slate-700 dark:text-slate-200">{skillData.length}</span>
                <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Total Skills</span>
              </div>
            </div>
            <div className="flex-1 grid grid-cols-2 gap-4">
              {skillData.map((skill, index) => (
                <div key={skill.name} className="flex items-center gap-3 p-3 rounded-2xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800 transition-transform hover:scale-105">
                  <div className="h-3 w-3 rounded-full shadow-sm" style={{ backgroundColor: SKILL_COLORS[index % SKILL_COLORS.length] }} />
                  <div className="flex flex-col min-w-0">
                    <span className="text-xs font-bold text-slate-700 dark:text-slate-200 truncate">{skill.name}</span>
                    <span className="text-[10px] font-medium text-slate-400">{skill.value} Resumes</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-[1.5rem] bg-white dark:bg-slate-800/50 p-6 shadow-xl border border-slate-100 dark:border-slate-700/50 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <p className="text-lg font-bold text-slate-700 dark:text-slate-100">Processing Queue</p>
            <span className="px-3 py-1.5 rounded-xl bg-orange-50 dark:bg-orange-500/10 text-orange-600 dark:text-orange-400 text-[10px] font-black uppercase tracking-wider">
              {candidates.filter((c) => c.status === 'processing').length} active
            </span>
          </div>
          {candidates.filter((c) => c.status === 'processing').length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Clock className="h-10 w-10 text-slate-200 dark:text-slate-700" />
              <p className="mt-5 text-sm font-bold text-slate-400 dark:text-slate-500">Engine Idle.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {candidates.filter((c) => c.status === 'processing').slice(0, 3).map((c) => (
                <div key={c.id} className="flex items-center gap-4 rounded-2xl border border-slate-100 dark:border-slate-800 p-4 transition-all hover:bg-slate-50 dark:hover:bg-slate-900/50">
                  <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-2xl text-xs font-black text-white" style={{ background: getAvatarColor(c.full_name) }}>
                    {getInitials(c.full_name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-bold text-slate-700 dark:text-slate-200">{c.full_name || 'Candidate'}</p>
                    <div className="flex-1 h-2 rounded-full bg-slate-100 dark:bg-slate-900 mt-1 overflow-hidden">
                      <div className="h-full rounded-full animate-pulse" style={{ width: '65%', background: 'linear-gradient(90deg,#ea580c,#f97316)' }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-[1.5rem] bg-white dark:bg-slate-800/50 p-6 shadow-xl border border-slate-100 dark:border-slate-700/50 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <p className="text-lg font-bold text-slate-700 dark:text-slate-100">Global Feed</p>
            <button onClick={() => navigate('/candidates')} className="px-3 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-900 text-[10px] font-black text-orange-500 dark:text-orange-400 uppercase tracking-widest">
              View All
            </button>
          </div>
          <div className="space-y-4">
            {recentResumes.map((candidate) => {
              const score = candidate.parsing_jobs?.[0]?.confidence_score
              return (
                <div key={candidate.id} className="flex items-center gap-4 cursor-pointer p-4 -mx-2 rounded-2xl hover:bg-slate-50 dark:hover:bg-slate-900 group" onClick={() => navigate(`/candidates/${candidate.id}`)}>
                  <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-2xl text-xs font-black text-white" style={{ background: getAvatarColor(candidate.full_name) }}>
                    {getInitials(candidate.full_name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-bold text-slate-700 dark:text-slate-200 group-hover:text-orange-600">{candidate.full_name || 'Anonymous'}</p>
                    <p className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase mt-1">{new Date(candidate.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex flex-col items-end">
                    {score != null && <span className="text-xs font-black" style={{ color: getScoreColor(score * 100) }}>{Math.round(score * 100)}%</span>}
                    <span className={`mt-1.5 rounded-full px-2 py-0.5 text-[9px] font-black uppercase ${candidate.status === 'success' ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-red-50 text-red-500'}`}>{candidate.status}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="rounded-3xl bg-white dark:bg-slate-800/50 p-6 shadow-xl border border-slate-100 dark:border-slate-700/50 backdrop-blur-sm">
        <p className="text-lg font-bold text-slate-700 dark:text-slate-100 mb-8">Accuracy Distribution</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={dynamicScoreDistData} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} vertical={false} />
            <XAxis dataKey="range" tick={{ fontSize: 11, fill: chartTheme.text, fontWeight: 700 }} axisLine={false} tickLine={false} dy={10} />
            <YAxis tick={{ fontSize: 11, fill: chartTheme.text, fontWeight: 700 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 16, backgroundColor: chartTheme.bg, border: `1px solid ${chartTheme.border}` }} />
            <Bar dataKey="count" radius={[8, 8, 8, 8]} barSize={40}>
              {dynamicScoreDistData.map((_, index) => (
                <Cell key={index} fill={`url(#barGrad${index})`} />
              ))}
              <defs>
                {dynamicScoreDistData.map((_, index) => (
                  <linearGradient key={index} id={`barGrad${index}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#7c3aed" />
                    <stop offset="100%" stopColor="#14b8a6" />
                  </linearGradient>
                ))}
              </defs>
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
