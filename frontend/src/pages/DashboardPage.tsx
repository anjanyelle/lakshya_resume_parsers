import { useEffect, useState, useMemo } from "react";
import { useCandidateStore } from "../store/useCandidateStore";
import { useJobStore } from "../store/useJobStore";
import { LayoutDashboard, Users, Briefcase, Target, Activity, FileText, ChevronRight, TrendingUp, ArrowUpRight } from "lucide-react";
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
  Cell
} from "recharts";

interface StatCard {
  title: string;
  value: string | number;
  change?: string;
  changeType?: "increase" | "decrease" | "neutral";
  icon: React.ReactNode;
  gradient: string;
}

export default function DashboardPage() {
  const { candidates, fetchCandidates } = useCandidateStore();
  const { jobs, fetchJobs, matchResults } = useJobStore();
  const [stats, setStats] = useState<StatCard[]>([]);

  useEffect(() => {
    fetchCandidates();
    fetchJobs();
  }, [fetchCandidates, fetchJobs]);

  useEffect(() => {
    const displayCandidates = candidates || [];
    const displayMatchResults = matchResults || [];

    const totalCandidates = displayCandidates.length;
    const activeJobs = (jobs || []).length;
    const matchesToday = displayMatchResults.length;
    const avgScore =
      displayMatchResults.length > 0
        ? Math.round(
          displayMatchResults.reduce((acc, match) => acc + match.overall_score, 0) /
          displayMatchResults.length,
        )
        : 0;

    setStats([
      {
        title: "Total Candidates",
        value: totalCandidates,
        change: "+12%",
        changeType: "increase",
        icon: <Users className="h-5 w-5" />,
        gradient: "",
      },
      {
        title: "Active Jobs",
        value: activeJobs,
        change: "+5%",
        changeType: "increase",
        icon: <Briefcase className="h-5 w-5" />,
        gradient: "",
      },
      {
        title: "Total Matches",
        value: matchesToday,
        change: "+8%",
        changeType: "increase",
        icon: <Target className="h-5 w-5" />,
        gradient: "",
      },
      {
        title: "Avg Match Score",
        value: `${avgScore}%`,
        change: "+3%",
        changeType: "increase",
        icon: <Activity className="h-5 w-5" />,
        gradient: "",
      },
    ]);
  }, [candidates, jobs, matchResults]);

  const displayCandidates = candidates || [];
  const displayMatchResults = matchResults || [];

  const recentUploads = displayCandidates.slice(0, 5);
  const topMatches = displayMatchResults.slice(0, 5);

  const matchChartData = useMemo(() => {
    if (!topMatches.length) return [];
    return topMatches.map(m => ({
      name: m.candidate_name.split(' ')[0] || 'Unknown',
      score: m.overall_score
    }));
  }, [topMatches]);

  const uploadTrendData = useMemo(() => {
    const base = (candidates || []).length;
    return [
      { day: 'Mon', count: Math.max(0, base - 12) },
      { day: 'Tue', count: Math.max(0, base - 8) },
      { day: 'Wed', count: Math.max(0, base - 5) },
      { day: 'Thu', count: Math.max(0, base - 2) },
      { day: 'Fri', count: base },
      { day: 'Sat', count: base + 3 },
      { day: 'Sun', count: base + 7 },
    ];
  }, [candidates]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0F172A] transition-colors duration-500">
      <div className="p-6 sm:p-8 max-w-7xl mx-auto space-y-6">

        {/* Page Header */}
        <div className="flex items-center gap-4 mb-2">
          <div className="p-2.5 rounded-xl shadow-sm text-white flex-shrink-0" style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
            <LayoutDashboard className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Dashboard</h1>
            <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Welcome back! Here's your resume parsing overview for today.</p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm interactive-box p-5 flex flex-col gap-4 cursor-default transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="h-10 w-10 rounded-xl flex items-center justify-center text-white shadow-sm" style={{ background: 'linear-gradient(135deg, #7C3AED, #9333EA)' }}>
                  {stat.icon}
                </div>
                {stat.change && (
                  <span className="flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full" style={{ color: '#7C3AED', background: '#f3e8ff' }}>
                    <TrendingUp className="w-3 h-3" />
                    {stat.change}
                  </span>
                )}
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">
                  {stat.title}
                </p>
                <h3 className="text-3xl font-extrabold text-slate-800 dark:text-white">
                  {stat.value}
                </h3>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Trend Chart */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 interactive-box cursor-default">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-slate-800 dark:text-white">Upload Activity</h3>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Resumes uploaded this week</p>
              </div>
              <div className="h-8 w-8 rounded-xl flex items-center justify-center" style={{ background: '#f3e8ff' }}>
                <Activity className="w-4 h-4" style={{ color: '#7C3AED' }} />
              </div>
            </div>
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%" minHeight={220}>
                <AreaChart data={uploadTrendData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#9333ea" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#9333ea" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} dy={8} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)', fontSize: '12px' }}
                    itemStyle={{ color: '#7e22ce', fontWeight: 'bold' }}
                  />
                  <Area type="monotone" dataKey="count" stroke="#9333ea" strokeWidth={2.5} fillOpacity={1} fill="url(#colorCount)" dot={{ fill: '#9333ea', r: 3, strokeWidth: 0 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Match Scores Chart */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 interactive-box cursor-default">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-slate-800">Top Matching Scores</h3>
                <p className="text-xs text-slate-400 mt-0.5">Best candidate matches</p>
              </div>
              <div className="h-8 w-8 rounded-xl flex items-center justify-center" style={{ background: '#f3e8ff' }}>
                <Target className="w-4 h-4" style={{ color: '#7C3AED' }} />
              </div>
            </div>
            <div className="h-[220px] w-full">
              {matchChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%" minHeight={220}>
                  <BarChart data={matchChartData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} dy={8} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <Tooltip
                      cursor={{ fill: '#faf5ff', opacity: 0.1 }}
                      contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)', fontSize: '12px', color: '#fff' }}
                    />
                    <Bar dataKey="score" radius={[6, 6, 0, 0]} maxBarSize={36}>
                      {matchChartData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#7e22ce' : '#c084fc'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-300">
                  <Target size={40} className="mb-3 opacity-40" />
                  <p className="text-sm font-medium text-slate-400">No matching data yet</p>
                  <p className="text-xs text-slate-300 mt-1">Run matching to see scores</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Activity Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Uploads */}
          <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden interactive-box cursor-default transition-all">
            <div className="px-6 py-4 border-b border-slate-50 dark:border-slate-700/50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-7 w-7 bg-purple-50 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                  <FileText className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="text-sm font-bold text-slate-800 dark:text-white">Recent Uploads</h3>
              </div>
              <button className="flex items-center gap-1 text-xs font-semibold text-purple-600 dark:text-purple-400 hover:text-purple-700 transition-colors">
                View all <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="divide-y divide-slate-50">
              {recentUploads.length > 0 ? (
                recentUploads.map((candidate) => (
                  <div key={candidate.id} className="px-6 py-3.5 flex items-center justify-between hover:bg-slate-50/70 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="h-9 w-9 bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-900 dark:to-purple-800 rounded-xl flex items-center justify-center flex-shrink-0">
                        <span className="text-sm font-bold text-purple-700 dark:text-purple-200">
                          {candidate.full_name?.charAt(0)?.toUpperCase() || "?"}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-800 dark:text-white">{candidate.full_name}</p>
                        <p className="text-xs text-slate-400 dark:text-slate-500">{candidate.email}</p>
                      </div>
                    </div>
                    <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${candidate.parsing_status?.status === "completed"
                      ? "bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400"
                      : candidate.parsing_status?.status === "processing"
                        ? "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                      }`}>
                      {candidate.parsing_status?.status || "Unknown"}
                    </span>
                  </div>
                ))
              ) : (
                <div className="px-6 py-12 text-center">
                  <FileText className="mx-auto h-10 w-10 text-slate-200 mb-3" />
                  <p className="text-sm font-medium text-slate-400">No recent uploads</p>
                  <p className="text-xs text-slate-300 mt-1">Upload resumes to get started</p>
                </div>
              )}
            </div>
          </div>

          {/* Top Matching Candidates */}
          <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden interactive-box cursor-default transition-all">
            <div className="px-6 py-4 border-b border-slate-50 dark:border-slate-700/50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-7 w-7 bg-purple-50 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                  <Users className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="text-sm font-bold text-slate-800 dark:text-white">Top Matches</h3>
              </div>
              <button className="flex items-center gap-1 text-xs font-semibold text-purple-600 dark:text-purple-400 hover:text-purple-700 transition-colors">
                View all <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="divide-y divide-slate-50">
              {topMatches.length > 0 ? (
                topMatches.map((match, index) => (
                  <div key={match.id} className="px-6 py-3.5 flex items-center justify-between hover:bg-slate-50/70 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="h-9 w-9 bg-purple-50 dark:bg-purple-900/30 border border-purple-100 dark:border-purple-800/50 rounded-xl flex items-center justify-center flex-shrink-0">
                        <span className="text-xs font-black text-purple-600 dark:text-purple-400">#{index + 1}</span>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-800 dark:text-white">{match.candidate_name}</p>
                        <p className="text-xs text-slate-400 dark:text-slate-500">{match.candidate_email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${match.recommendation === "Strong Match" ? "bg-purple-100 dark:bg-purple-900/40 text-purple-800 dark:text-purple-300"
                        : match.recommendation === "Good Match" ? "bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                        }`}>
                        {match.recommendation}
                      </span>
                      <div className="flex items-center gap-1">
                        <span className="text-base font-black text-purple-700 dark:text-purple-400">{match.overall_score}%</span>
                        <ArrowUpRight className="w-3.5 h-3.5 text-purple-500" />
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-6 py-12 text-center">
                  <Users className="mx-auto h-10 w-10 text-slate-200 mb-3" />
                  <p className="text-sm font-medium text-slate-400">No matching results yet</p>
                  <p className="text-xs text-slate-300 mt-1">Run matching to see top candidates</p>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
