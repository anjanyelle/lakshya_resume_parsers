import { useEffect, useState } from 'react'
import { BarChart3, ShieldCheck, TrendingUp, Target, Activity } from 'lucide-react'
import { fetchAccuracyOverview, type AccuracyOverview } from '../services/api/accuracy'
import Skeleton from '../components/common/Skeleton'

export default function AccuracyPage() {
  const [overview, setOverview] = useState<AccuracyOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const data = await fetchAccuracyOverview()
        setOverview(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load accuracy')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const sectionMetrics = overview?.section_scores ?? []
  const recentRuns = overview?.recent_runs ?? []

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Metrics Row */}
      <div className="grid gap-4 md:grid-cols-3">
        {[
          {
            label: 'Overall Accuracy',
            value: overview ? `${overview.success_rate}%` : '—',
            sub: 'Extraction success rate',
            icon: ShieldCheck,
            iconBg: 'linear-gradient(135deg,#10b981,#34d399)',
          },
          {
            label: 'Correction Rate',
            value: overview ? `${overview.correction_rate}%` : '—',
            sub: 'Requires manual edit',
            icon: Activity,
            iconBg: 'linear-gradient(135deg,#f59e0b,#fbbf24)',
          },
          {
            label: 'Avg. Confidence',
            value: overview ? overview.avg_confidence.toFixed(2) : '—',
            sub: 'AI model certainty',
            icon: Target,
            iconBg: 'linear-gradient(135deg,#7c3aed,#a78bfa)',
          },
        ].map((card) => {
          const Icon = card.icon
          return (
            <div
              key={card.label}
              className="group rounded-xl bg-white p-5 shadow-card border border-slate-100 transition-all duration-200 hover:shadow-card-hover"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium text-slate-400">{card.sub}</p>
                  <p className="mt-1 text-2xl font-medium text-slate-800">{card.value}</p>
                  <p className="mt-0.5 text-xs font-semibold text-slate-800 uppercase tracking-wider">{card.label}</p>
                </div>
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-xl text-white shadow-md transition-transform group-hover:scale-110"
                  style={{ background: card.iconBg }}
                >
                  <Icon className="h-5 w-5" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        {/* Section Accuracy Card */}
        <div className="rounded-xl bg-white p-6 shadow-card border border-slate-100">
          <div className="flex items-center gap-2 mb-6">
            <div className="h-2 w-2 rounded-full bg-violet-500" />
            <h3 className="text-sm font-semibold text-slate-800">Section Accuracy</h3>
          </div>

          <div className="space-y-5">
            {loading ? (
              <Skeleton lines={5} />
            ) : error ? (
              <div className="rounded-lg bg-red-50 p-4 text-xs text-red-600 border border-red-100">
                {error}
              </div>
            ) : sectionMetrics.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <BarChart3 className="h-8 w-8 text-slate-200 mb-2" />
                <p className="text-sm text-slate-400">No section data yet</p>
              </div>
            ) : (
              sectionMetrics.map((metric) => (
                <div key={metric.label} className="group">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="font-semibold text-slate-800 transition-colors group-hover:text-violet-600">{metric.label}</span>
                    <span className="font-semibold text-slate-800">
                      {(metric.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-50 overflow-hidden border border-slate-100 flex p-[1px]">
                    <div
                      className="h-full rounded-full transition-all duration-1000 ease-out"
                      style={{
                        width: `${metric.score * 100}%`,
                        background: 'linear-gradient(90deg, #7c3aed, #14b8a6)'
                      }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Runs Card */}
        <div className="rounded-xl bg-white p-6 shadow-card border border-slate-100">
          <div className="flex items-center gap-2 mb-6">
            <div className="h-2 w-2 rounded-full bg-teal-500" />
            <h3 className="text-sm font-semibold text-slate-800">Recent Parsing Runs</h3>
          </div>

          <div className="space-y-3">
            {loading ? (
              <Skeleton lines={5} />
            ) : error ? (
              <div className="rounded-lg bg-red-50 p-4 text-xs text-red-600 border border-red-100">
                {error}
              </div>
            ) : recentRuns.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <Activity className="h-8 w-8 text-slate-200 mb-2" />
                <p className="text-sm text-slate-400">No recent runs</p>
              </div>
            ) : (
              recentRuns.map((run) => (
                <div
                  key={run.job_id}
                  className="group rounded-xl border border-slate-100 bg-slate-50/50 p-3 transition-all hover:bg-white hover:shadow-md hover:border-violet-100"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-800">{run.job_id.slice(0, 12)}...</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${run.confidence > 0.8 ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'
                      }`}>
                      {(run.confidence * 100).toFixed(0)}% Confidence
                    </span>
                  </div>
                  <p className="mt-2 text-[11px] text-slate-500 leading-relaxed italic border-l-2 border-slate-200 pl-2">
                    {run.notes || 'No notes available for this run.'}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
