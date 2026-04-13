import { useEffect, useState } from "react";
import {
  fetchAccuracyOverview,
  type AccuracyOverview,
} from "../services/api/accuracy";
import {
  Shield, TrendingUp, Activity, BarChart3,
  ChevronRight, Clock, CheckCircle2, AlertCircle
} from "lucide-react";

export default function AccuracyPage() {
  const [overview, setOverview] = useState<AccuracyOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await fetchAccuracyOverview();
        setOverview(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load accuracy");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const sectionMetrics = overview?.section_scores ?? [];
  const recentRuns = overview?.recent_runs ?? [];

  const statCards = [
    {
      label: "OVERALL ACCURACY",
      sublabel: "Extraction success rate",
      value: loading ? "—" : `${overview?.success_rate ?? 0}%`,
      icon: <Shield size={24} />,
      color: "from-emerald-600 to-teal-500",
      shadow: "shadow-emerald-200"
    },
    {
      label: "CORRECTION RATE",
      sublabel: "Manual human edits",
      value: loading ? "—" : `${overview?.correction_rate ?? 0}%`,
      icon: <TrendingUp size={24} />,
      color: "from-amber-600 to-orange-500",
      shadow: "shadow-amber-200"
    },
    {
      label: "AVG. CONFIDENCE",
      sublabel: "AI model certainty",
      value: loading ? "—" : (overview?.avg_confidence ?? 0).toFixed(2),
      icon: <Activity size={24} />,
      color: "from-indigo-600 to-blue-500",
      shadow: "shadow-indigo-200"
    },
  ];

  const getConfidenceBadge = (conf: number) => {
    const pct = Math.round(conf * 100);
    if (conf >= 0.75) return { label: `${pct}% Confidence`, color: "text-emerald-500", bg: "bg-emerald-50", icon: <CheckCircle2 size={12} /> };
    if (conf >= 0.55) return { label: `${pct}% Confidence`, color: "text-amber-500", bg: "bg-amber-50", icon: <Activity size={12} /> };
    return { label: `${pct}% Confidence`, color: "text-rose-500", bg: "bg-rose-50", icon: <AlertCircle size={12} /> };
  };

  return (
    <div className="relative min-h-[calc(100vh-64px)] animate-in fade-in duration-700 py-6 px-6 max-w-[1400px] mx-auto overflow-hidden">

      {/* Background Atmosphere */}
      <div className="absolute top-0 right-0 -z-10 w-[600px] h-[600px] bg-indigo-500/5 blur-[120px] rounded-full -mr-48 -mt-48" />
      <div className="absolute bottom-0 left-0 -z-10 w-[500px] h-[500px] bg-emerald-500/5 blur-[100px] rounded-full -ml-32 -mb-32" />

      {/* Internal Sub-header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
            PERFORMANCE METRICS & MODEL EXTRACTION CONFIDENCE
          </p>
        </div>
        
        <button
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-xl text-[12px] font-[900] text-white shadow-lg shadow-indigo-600/20 hover:scale-[1.02] active:scale-95 transition-all outline-none"
        >
          <TrendingUp size={14} />
          EXPORT ANALYTICS
        </button>
      </div>

      {/* Stat Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {statCards.map((card, i) => (
          <div key={i} className="bg-white rounded-2xl p-5 shadow-[0_4px_20px_rgb(0,0,0,0.02)] border border-slate-50 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-slate-50/50 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
            
            <div className="flex items-center justify-between mb-3">
               <div>
                  <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest mb-1">{card.sublabel}</p>
                  <h3 className="text-2xl font-black text-slate-800 tracking-tight leading-none">{card.value}</h3>
               </div>
               <div className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${card.color} text-white flex items-center justify-center shadow-md ${card.shadow} transform transition-transform group-hover:scale-110`}>
                  <div className="scale-90">{card.icon}</div>
               </div>
            </div>
            <p className="text-[10px] font-[900] text-slate-400 uppercase tracking-[0.2em]">{card.label}</p>
          </div>
        ))}
      </div>

      {/* Main Insights Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Section Accuracy Chart */}
        <div className="lg:col-span-8 bg-white rounded-2xl p-6 shadow-[0_4px_20px_rgb(0,0,0,0.02)] border border-slate-50/50">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                <BarChart3 size={18} />
              </div>
              <h3 className="text-sm font-black text-slate-800 tracking-tight uppercase">Segment Precision</h3>
            </div>
            <div className="px-2.5 py-1 bg-slate-50 rounded-lg text-[9px] font-black text-slate-400 uppercase tracking-widest">
              Last 30 Days
            </div>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
              <div className="w-8 h-8 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin mb-4" />
              <p className="text-[10px] font-black text-slate-300 tracking-[0.2em] uppercase">Aggregating Metrics...</p>
            </div>
          ) : error ? (
            <div className="bg-rose-50 text-rose-500 p-4 rounded-xl text-xs font-bold border border-rose-100 italic">
              Error loading segments: {error}
            </div>
          ) : (
            <div className="grid gap-6">
              {sectionMetrics.map((metric) => {
                const pct = Math.round(metric.score * 100);
                return (
                  <div key={metric.label} className="group">
                    <div className="flex justify-between items-end mb-2">
                      <span className="text-[13px] font-bold text-slate-600 group-hover:text-indigo-600 transition-colors uppercase tracking-tight">{metric.label}</span>
                      <span className="text-[14px] font-black text-slate-800 leading-none">{pct}%</span>
                    </div>
                    <div className="h-3 w-full bg-slate-50 rounded-full overflow-hidden border border-slate-100 shadow-inner">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-600 to-teal-400 rounded-full transition-all duration-1000 ease-out shadow-sm"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Recent Processing Runs */}
        <div className="lg:col-span-4 bg-white rounded-2xl p-6 shadow-[0_4px_20px_rgb(0,0,0,0.02)] border border-slate-50/50 relative overflow-hidden">
          {/* Subtle decoration */}
          <div className="absolute -top-12 -right-12 w-48 h-48 bg-slate-50 rounded-full blur-3xl opacity-60" />

          <div className="flex items-center gap-3 mb-6 relative">
              <div className="w-9 h-9 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600">
                <Clock size={16} />
              </div>
              <h3 className="text-sm font-black text-slate-800 tracking-tight uppercase">Parsing Stream</h3>
          </div>

          <div className="space-y-4 relative">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-20 bg-slate-50 rounded-2xl animate-pulse" style={{ animationDelay: `${i * 150}ms` }} />
              ))
            ) : recentRuns.length === 0 ? (
              <div className="text-center py-10">
                <p className="text-xs font-bold text-slate-300 uppercase tracking-widest">No recent stream data</p>
              </div>
            ) : (
              recentRuns.map((run) => {
                const badge = getConfidenceBadge(run.confidence);
                return (
                  <div key={run.job_id} className="group p-4 bg-slate-50/50 hover:bg-white hover:shadow-lg hover:shadow-slate-200/50 rounded-2xl border border-transparent hover:border-slate-100 transition-all cursor-default">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[12px] font-black text-slate-800 uppercase tracking-tight truncate max-w-[120px]">
                        {run.job_id.slice(0, 10)}...
                      </span>
                      <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${badge.bg} ${badge.color} text-[10px] font-[900] uppercase tracking-wider`}>
                        {badge.icon}
                        {badge.label}
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-slate-400 italic truncate max-w-[150px]">{run.notes || "save_to_database"}</span>
                      <ChevronRight size={14} className="text-slate-300 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
