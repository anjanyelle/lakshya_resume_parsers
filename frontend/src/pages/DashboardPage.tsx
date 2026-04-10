import { useEffect, useState } from 'react'
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

// Monthly applications demo data
const monthlyData = [
  { month: 'Jan', value: 4 },
  { month: 'Feb', value: 6 },
  { month: 'Mar', value: 20 },
  { month: 'Apr', value: 18 },
  { month: 'May', value: 16 },
  { month: 'Jun', value: 18 },
]

// Score distribution demo data
const scoreDistData = [
  { range: '0-20', count: 1 },
  { range: '21-40', count: 2 },
  { range: '41-60', count: 3 },
  { range: '61-80', count: 8 },
  { range: '81-100', count: 12 },
]

const SKILL_COLORS = ['#7c3aed', '#14b8a6', '#6366f1', '#f97316', '#ef4444', '#eab308']

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

export default function DashboardPage() {
  const navigate = useNavigate()
  const { candidates, loadCandidates } = useCandidateStore()
  const [skillData, setSkillData] = useState<{ name: string; value: number }[]>([])

  useEffect(() => {
    const controller = new AbortController()
    loadCandidates(controller.signal)
    return () => controller.abort()
  }, [loadCandidates])

  // Compute stats from real data
  const totalResumes = candidates.length
  const analyzedCandidates = candidates.filter((c) => c.status === 'success').length
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
      ;(c.skills ?? []).forEach((s) => {
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

  const displayScore =
    avgScore > 0
      ? `${avgScore}%`
      : '—'

  const statsCards = [
    {
      label: 'Total Resumes',
      value: totalResumes > 0 ? String(totalResumes) : '—',
      trend: '+12%',
      up: true,
      icon: FileText,
      iconBg: 'linear-gradient(135deg,#7c3aed,#a78bfa)',
    },
    {
      label: 'Analyzed Candidates',
      value: analyzedCandidates > 0 ? String(analyzedCandidates) : '—',
      trend: '+8%',
      up: true,
      icon: Users,
      iconBg: 'linear-gradient(135deg,#14b8a6,#2dd4bf)',
    },
    {
      label: 'Avg. Match Score',
      value: displayScore,
      trend: '+5%',
      up: true,
      icon: Star,
      iconBg: 'linear-gradient(135deg,#10b981,#34d399)',
    },
    {
      label: 'Avg. Processing Time',
      value:
        candidates.length > 0 ? `${avgProcessingDays} days` : '—',
      trend: '-2 days',
      up: false,
      icon: Clock,
      iconBg: 'linear-gradient(135deg,#f97316,#fb923c)',
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        {statsCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.label}
              className="rounded-xl bg-white p-5 shadow-card border border-slate-100 transition-all duration-200 hover:shadow-card-hover"
            >
              <div className="flex items-start justify-between">
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-xl text-white shadow-md"
                  style={{ background: stat.iconBg }}
                >
                  <Icon className="h-4 w-4" />
                </div>
                <span
                  className={`flex items-center gap-1 text-xs font-semibold ${
                    stat.up ? 'text-emerald-600' : 'text-rose-500'
                  }`}
                >
                  {stat.up ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {stat.trend}
                </span>
              </div>
              <div className="mt-4">
                <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
                <p className="mt-0.5 text-xs text-slate-500">{stat.label}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Monthly Applications */}
        <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-700">Monthly Applications</h3>
            <button className="text-slate-400 hover:text-slate-600 transition-colors">
              <MoreVertical className="h-4 w-4" />
            </button>
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={monthlyData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 8,
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#7c3aed"
                strokeWidth={2}
                fill="url(#areaGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Top Skills Detected */}
        <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-700">Top Skills Detected</h3>
            <button className="text-slate-400 hover:text-slate-600 transition-colors">
              <MoreVertical className="h-4 w-4" />
            </button>
          </div>
          {skillData.length > 0 ? (
            <>
              <div className="flex justify-center">
                <PieChart width={160} height={160}>
                  <Pie
                    data={skillData}
                    cx={75}
                    cy={75}
                    innerRadius={50}
                    outerRadius={75}
                    dataKey="value"
                    paddingAngle={2}
                  >
                    {skillData.map((_, index) => (
                      <Cell key={index} fill={SKILL_COLORS[index % SKILL_COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </div>
              <div className="mt-2 flex flex-wrap gap-2 justify-center">
                {skillData.map((skill, index) => (
                  <span key={skill.name} className="flex items-center gap-1 text-xs text-slate-600">
                    <span
                      className="inline-block h-2 w-2 rounded-full"
                      style={{ backgroundColor: SKILL_COLORS[index % SKILL_COLORS.length] }}
                    />
                    {skill.name} ({skill.value})
                  </span>
                ))}
              </div>
            </>
          ) : (
            // Demo pie chart
            <div className="flex flex-col items-center">
              <PieChart width={160} height={160}>
                <Pie
                  data={[
                    { name: 'Python', value: 2 },
                    { name: 'Django', value: 1 },
                    { name: 'PostgreSQL', value: 1 },
                    { name: 'Docker', value: 1 },
                    { name: 'JavaScript', value: 1 },
                  ]}
                  cx={75}
                  cy={75}
                  innerRadius={50}
                  outerRadius={75}
                  dataKey="value"
                  paddingAngle={2}
                >
                  {SKILL_COLORS.map((color, index) => (
                    <Cell key={index} fill={color} />
                  ))}
                </Pie>
              </PieChart>
              <div className="mt-2 flex flex-wrap gap-2 justify-center">
                {[
                  { name: 'Python', count: 2, color: SKILL_COLORS[0] },
                  { name: 'Django', count: 1, color: SKILL_COLORS[1] },
                  { name: 'PostgreSQL', count: 1, color: SKILL_COLORS[2] },
                  { name: 'Docker', count: 1, color: SKILL_COLORS[3] },
                  { name: 'JavaScript', count: 1, color: SKILL_COLORS[4] },
                ].map((s) => (
                  <span key={s.name} className="flex items-center gap-1 text-xs text-slate-600">
                    <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: s.color }} />
                    {s.name} ({s.count})
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Processing Queue */}
        <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-700">Processing Queue</h3>
            <span className="text-xs text-slate-400">
              {candidates.filter((c) => c.status === 'processing').length} active
            </span>
          </div>
          {candidates.filter((c) => c.status === 'processing').length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-slate-200">
                <Clock className="h-7 w-7 text-slate-300" />
              </div>
              <p className="mt-3 text-sm text-slate-400">No resumes processing</p>
            </div>
          ) : (
            <div className="space-y-2">
              {candidates
                .filter((c) => c.status === 'processing')
                .slice(0, 3)
                .map((c) => (
                  <div
                    key={c.id}
                    className="flex items-center gap-3 rounded-lg border border-slate-100 p-3"
                  >
                    <div
                      className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-xs font-bold text-white"
                      style={{ background: getAvatarColor(c.full_name) }}
                    >
                      {getInitials(c.full_name)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-sm font-medium text-slate-700">
                        {c.full_name || 'Unknown'}
                      </p>
                      <p className="text-xs text-slate-400">Processing...</p>
                    </div>
                    <div className="h-1.5 w-20 rounded-full bg-slate-100">
                      <div
                        className="h-1.5 rounded-full"
                        style={{
                          width: '60%',
                          background: 'linear-gradient(90deg,#7c3aed,#14b8a6)',
                        }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Recent Resumes */}
        <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-700">Recent Resumes</h3>
            <button
              onClick={() => navigate('/candidates')}
              className="text-xs font-medium text-violet-600 hover:text-violet-700 transition-colors"
            >
              View All
            </button>
          </div>

          {recentResumes.length > 0 ? (
            <div className="space-y-3">
              {recentResumes.map((candidate) => {
                const score = candidate.parsing_jobs?.[0]?.confidence_score
                const scoreDisplay = score != null ? `${Math.round(score * 100)}%` : '—'
                return (
                  <div
                    key={candidate.id}
                    className="flex items-center gap-3 cursor-pointer hover:bg-slate-50 rounded-lg p-2 -mx-2 transition-colors"
                    onClick={() => navigate(`/candidates/${candidate.id}`)}
                  >
                    <div
                      className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl text-xs font-bold text-white"
                      style={{ background: getAvatarColor(candidate.full_name) }}
                    >
                      {getInitials(candidate.full_name)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-sm font-medium text-slate-700">
                        {candidate.full_name || 'Unknown candidate'}
                      </p>
                      <p className="text-xs text-slate-400">
                        {new Date(candidate.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {score != null && (
                        <span
                          className="text-sm font-bold"
                          style={{ color: getScoreColor(score * 100) }}
                        >
                          {scoreDisplay}
                        </span>
                      )}
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          candidate.status === 'success'
                            ? 'bg-emerald-50 text-emerald-600'
                            : candidate.status === 'failed'
                              ? 'bg-red-50 text-red-500'
                              : 'bg-amber-50 text-amber-600'
                        }`}
                      >
                        {candidate.status === 'success' ? 'completed' : candidate.status}
                      </span>
                      <button
                        className="text-slate-300 hover:text-slate-500 transition-colors"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/candidates/${candidate.id}`)
                        }}
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </button>
                      <button className="text-slate-300 hover:text-slate-500 transition-colors">
                        <Download className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <FileText className="h-8 w-8 text-slate-200 mb-2" />
              <p className="text-sm text-slate-400">No resumes uploaded yet</p>
              <button
                onClick={() => navigate('/upload')}
                className="mt-3 rounded-lg px-4 py-1.5 text-xs font-medium text-white transition-all hover:opacity-90"
                style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
              >
                Upload Resume
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Score Distribution */}
      <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-700">Score Distribution</h3>
          <button className="text-slate-400 hover:text-slate-600 transition-colors">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={scoreDistData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="range"
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                fontSize: 12,
                borderRadius: 8,
                border: '1px solid #e2e8f0',
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
              }}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {scoreDistData.map((_, index) => (
                <Cell
                  key={index}
                  fill={`url(#barGrad${index})`}
                />
              ))}
              <defs>
                {scoreDistData.map((_, index) => (
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
