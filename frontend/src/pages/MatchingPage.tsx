import React, { useState, useEffect } from "react";
import { useJobStore } from "../store/useJobStore";
import CustomSelect from "../components/common/CustomSelect";
import toast from "react-hot-toast";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";
import { Target, Download, Play, ChevronDown, ChevronUp, CheckCircle, AlertCircle, MinusCircle, XCircle } from "lucide-react";

interface MatchResult {
  id: string; job_id: string; job_title?: string; candidate_id: string;
  candidate_name: string; candidate_email: string; overall_score: number;
  skill_score: number; experience_score: number; education_score: number;
  matching_skills: string[]; missing_skills: string[];
  recommendation: "Strong Match" | "Good Match" | "Partial Match" | "Not Recommended";
  reason: string; created_at: string;
}

interface Job {
  id: string; title: string; department: string; location: string;
  employment_type: string; status: "active" | "inactive" | "closed";
}

export default function MatchingPage() {
  const [selectedJob, setSelectedJob] = useState<string>("");
  const [isMatching, setIsMatching] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [matchResults, setMatchResults] = useState<MatchResult[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);

  const { runMatching, fetchMatchResults, fetchJobs } = useJobStore();

  useEffect(() => { loadJobs(); loadMatchResults(); }, []);

  const loadJobs = async () => {
    try {
      const fetchedJobs = await fetchJobs();
      if (fetchedJobs && Array.isArray(fetchedJobs)) {
        setJobs(fetchedJobs.filter((job: Job) => job.status === "active"));
      }
    } catch { toast.error("Failed to load jobs"); }
  };

  const loadMatchResults = async () => {
    try {
      const results = await fetchMatchResults("all");
      if (results && Array.isArray(results)) {
        setMatchResults(results);
      }
    } catch { console.error("Failed to load match results"); }
  };

  const handleRunMatching = async () => {
    if (!selectedJob) { toast.error("Please select a job first"); return; }
    setIsMatching(true);
    try { await runMatching(selectedJob); toast.success("Matching completed!"); loadMatchResults(); }
    catch (error: any) { toast.error(error.message || "Matching failed"); }
    finally { setIsMatching(false); }
  };

  const toggleRowExpansion = (resultId: string) => {
    setExpandedRows((prev) => { const s = new Set(prev); s.has(resultId) ? s.delete(resultId) : s.add(resultId); return s; });
  };

  const exportToCSV = () => {
    if (matchResults.length === 0) { toast.error("No data to export"); return; }
    const headers = ["Rank", "Candidate Name", "Email", "Overall Score", "Skill Score", "Experience Score", "Education Score", "Recommendation", "Matching Skills", "Missing Skills"];
    const csvContent = [headers.join(","), ...matchResults.map((r, i) =>
      [i + 1, r.candidate_name, r.candidate_email, r.overall_score, r.skill_score, r.experience_score, r.education_score, r.recommendation, `"${r.matching_skills.join("; ")}"`, `"${r.missing_skills.join("; ")}"`].join(",")
    )].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = `matching_results_${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a); window.URL.revokeObjectURL(url);
    toast.success("Results exported!");
  };

  const getScoreBar = (score: number) => {
    if (score >= 80) return "bg-gradient-to-r from-brand-500 to-brand-600";
    if (score >= 60) return "bg-gradient-to-r from-amber-400 to-amber-500";
    return "bg-gradient-to-r from-slate-300 to-slate-400";
  };

  const getRecommendationConfig = (r: string) => {
    switch (r) {
      case "Strong Match": return { bg: "bg-emerald-50 text-emerald-700 border-emerald-200", icon: <CheckCircle className="w-3.5 h-3.5" /> };
      case "Good Match": return { bg: "bg-brand-50 text-brand-700 border-brand-200", icon: <CheckCircle className="w-3.5 h-3.5" /> };
      case "Partial Match": return { bg: "bg-amber-50 text-amber-700 border-amber-200", icon: <MinusCircle className="w-3.5 h-3.5" /> };
      case "Not Recommended": return { bg: "bg-red-50 text-red-700 border-red-200", icon: <XCircle className="w-3.5 h-3.5" /> };
      default: return { bg: "bg-slate-100 text-slate-600 border-slate-200", icon: <AlertCircle className="w-3.5 h-3.5" /> };
    }
  };

  const getInitials = (name: string) => name.split(" ").map((p) => p.charAt(0).toUpperCase()).slice(0, 2).join("");

  const filteredResults = selectedJob ? matchResults.filter((r) => r.job_id === selectedJob) : matchResults;

  const scoreDistribution = [
    { range: "90-100", count: matchResults.filter((r) => r.overall_score >= 90).length },
    { range: "80-89", count: matchResults.filter((r) => r.overall_score >= 80 && r.overall_score < 90).length },
    { range: "70-79", count: matchResults.filter((r) => r.overall_score >= 70 && r.overall_score < 80).length },
    { range: "60-69", count: matchResults.filter((r) => r.overall_score >= 60 && r.overall_score < 70).length },
    { range: "<60", count: matchResults.filter((r) => r.overall_score < 60).length },
  ];

  const recommendationData = [
    { name: "Strong Match", value: matchResults.filter((r) => r.recommendation === "Strong Match").length, color: "#10b981" },
    { name: "Good Match", value: matchResults.filter((r) => r.recommendation === "Good Match").length, color: "#9333ea" },
    { name: "Partial Match", value: matchResults.filter((r) => ["Partial Match", "Fair Match"].includes(r.recommendation)).length, color: "#f59e0b" },
    { name: "Not Recommended", value: matchResults.filter((r) => r.recommendation === "Not Recommended").length, color: "#ef4444" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0F172A] transition-colors duration-500">
      <div className="p-6 sm:p-8 max-w-7xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center gap-4 mb-2">
          <div className="p-2.5 rounded-xl shadow-sm text-white flex-shrink-0" style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Candidate Matching</h1>
            <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Match candidates against job requirements using AI scoring</p>
          </div>
        </div>

        {/* Controls Bar */}
        <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm p-5 transition-all">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <CustomSelect
              label="Select Job"
              placeholder="All Jobs"
              options={[
                { value: "", label: "All Jobs" },
                ...jobs.map(job => ({ 
                  value: job.id, 
                  label: `${job.title} — ${job.department}` 
                }))
              ]}
              value={selectedJob}
              onChange={setSelectedJob}
              searchable
              className="flex-1 max-w-sm"
            />
            <div className="flex gap-3 sm:ml-auto">
              <button onClick={handleRunMatching} disabled={isMatching || !selectedJob}
                className="flex items-center gap-2 px-5 py-2.5 text-white text-sm font-bold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
                style={{ background: '#7C3AED' }}>
                {isMatching ? (
                  <><div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white" /> Running...</>
                ) : (
                  <><Play className="w-4 h-4" /> Run Matching</>
                )}
              </button>
              <button onClick={exportToCSV} disabled={filteredResults.length === 0}
                className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 text-slate-700 hover:bg-slate-50 text-sm font-bold rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                <Download className="w-4 h-4" /> Export CSV
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Results Table */}
          <div className="xl:col-span-2 bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all">
            <div className="px-6 py-4 border-b border-slate-50 dark:border-slate-700/50 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-800 dark:text-white">Match Results</h3>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{filteredResults.length} candidates evaluated</p>
              </div>
              {filteredResults.length > 0 && (
                <span className="text-xs font-semibold bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 px-3 py-1 rounded-full">
                  Avg: {Math.round(filteredResults.reduce((a, r) => a + r.overall_score, 0) / filteredResults.length)}%
                </span>
              )}
            </div>

            {isMatching ? (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="animate-spin rounded-full h-12 w-12 border-[3px] border-brand-100 border-t-brand-600 mb-4" />
                <p className="text-sm font-medium text-slate-500">Running matching algorithm...</p>
              </div>
            ) : filteredResults.length > 0 ? (
              <div className="divide-y divide-slate-50">
                {filteredResults.map((result, index) => {
                  const recConfig = getRecommendationConfig(result.recommendation);
                  const isExpanded = expandedRows.has(result.id);
                  return (
                    <React.Fragment key={result.id}>
                      <div className="px-6 py-4 hover:bg-slate-50/50 dark:hover:bg-slate-700/30 cursor-pointer transition-colors" onClick={() => toggleRowExpansion(result.id)}>
                        <div className="flex items-center gap-4">
                          {/* Rank */}
                          <div className="h-8 w-8 bg-purple-50 dark:bg-purple-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                            <span className="text-xs font-black text-purple-600 dark:text-purple-400">#{index + 1}</span>
                          </div>

                          {/* Candidate */}
                          <div className="flex items-center gap-2.5 flex-1 min-w-0">
                            <div className="h-9 w-9 bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-900 dark:to-purple-800 rounded-xl flex items-center justify-center flex-shrink-0">
                              <span className="text-xs font-bold text-purple-700 dark:text-purple-200">{getInitials(result.candidate_name)}</span>
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-bold text-slate-800 dark:text-white truncate">{result.candidate_name}</p>
                              <p className="text-xs text-slate-400 dark:text-slate-500 truncate">{result.candidate_email}</p>
                            </div>
                          </div>

                          {/* Score bar */}
                          <div className="hidden sm:flex items-center gap-3 flex-shrink-0">
                            <div className="w-24 bg-slate-100 dark:bg-slate-700 rounded-full h-1.5">
                              <div className={`h-1.5 rounded-full ${getScoreBar(result.overall_score)}`} style={{ width: `${result.overall_score}%` }} />
                            </div>
                            <span className="text-sm font-black text-slate-800 dark:text-white w-10 text-right">{result.overall_score}%</span>
                          </div>

                          {/* Recommendation */}
                          <span className={`hidden md:flex items-center gap-1 px-2.5 py-1 text-xs font-bold rounded-full border flex-shrink-0 ${recConfig.bg}`}>
                            {recConfig.icon} {result.recommendation}
                          </span>

                          <div className="flex-shrink-0 text-slate-300">
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </div>
                        </div>
                      </div>

                      {/* Expanded Row */}
                      {isExpanded && (
                        <div className="px-6 py-5 bg-slate-50/60 dark:bg-slate-800/40 border-t border-slate-100 dark:border-slate-700/50">
                          {/* Score Breakdown */}
                          <div className="grid grid-cols-3 gap-4 mb-4">
                            {[
                              { label: "Skills", value: result.skill_score },
                              { label: "Experience", value: result.experience_score },
                              { label: "Education", value: result.education_score },
                            ].map(({ label, value }) => (
                              <div key={label} className="bg-white dark:bg-slate-800/60 rounded-xl p-3 border border-slate-100 dark:border-slate-700/50 text-center transition-all">
                                <div className="text-xl font-black text-purple-600 dark:text-purple-400">{value}%</div>
                                <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{label}</div>
                                <div className="mt-2 w-full bg-slate-100 dark:bg-slate-700 rounded-full h-1">
                                  <div className={`h-1 rounded-full ${getScoreBar(value)}`} style={{ width: `${value}%` }} />
                                </div>
                              </div>
                            ))}
                          </div>

                          {/* Skills */}
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Matching Skills</p>
                              <div className="flex flex-wrap gap-1.5">
                                {result.matching_skills.map((s, i) => (
                                  <span key={i} className="px-2 py-0.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/50 text-xs font-semibold rounded-lg">{s}</span>
                                ))}
                              </div>
                            </div>
                            <div>
                              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Missing Skills</p>
                              <div className="flex flex-wrap gap-1.5">
                                {result.missing_skills.map((s, i) => (
                                  <span key={i} className="px-2 py-0.5 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800/50 text-xs font-semibold rounded-lg">{s}</span>
                                ))}
                              </div>
                            </div>
                          </div>

                          {result.reason && (
                            <div className="bg-white dark:bg-slate-800/60 rounded-xl p-3 border border-slate-100 dark:border-slate-700/50">
                              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Analysis</p>
                              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{result.reason}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="h-16 w-16 bg-brand-50 rounded-2xl flex items-center justify-center mb-4">
                  <Target className="w-8 h-8 text-brand-300" />
                </div>
                <p className="text-sm font-bold text-slate-600 mb-1">No results yet</p>
                <p className="text-xs text-slate-400">{selectedJob ? "Run matching to see results" : "Select a job and run matching"}</p>
              </div>
            )}
          </div>

          {/* Side Charts */}
          <div className="space-y-5">
            {/* Stats summary */}
            <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm p-5 interactive-box transition-all">
              <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-4">Summary</h3>
              <div className="space-y-3">
                {[
                  { label: "Total Evaluated", value: filteredResults.length, color: "text-slate-800 dark:text-white" },
                  { label: "Avg Score", value: filteredResults.length > 0 ? `${Math.round(filteredResults.reduce((a, r) => a + r.overall_score, 0) / filteredResults.length)}%` : "—", color: "text-purple-600 dark:text-purple-400" },
                  { label: "Strong Matches", value: filteredResults.filter((r) => r.recommendation === "Strong Match").length, color: "text-emerald-600 dark:text-emerald-400" },
                  { label: "Good Matches", value: filteredResults.filter((r) => r.recommendation === "Good Match").length, color: "text-purple-600 dark:text-purple-400" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="flex justify-between items-center py-2 border-b border-slate-50 dark:border-slate-700/50 last:border-0">
                    <span className="text-xs text-slate-500 dark:text-slate-400">{label}</span>
                    <span className={`text-sm font-bold ${color}`}>{value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Score Distribution */}
            <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm p-5 interactive-box transition-all">
              <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-4">Score Distribution</h3>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={scoreDistribution} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 10 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 10 }} />
                  <Tooltip contentStyle={{ borderRadius: "10px", border: "none", boxShadow: "0 4px 20px rgba(0,0,0,0.1)", fontSize: "11px" }} />
                  <Bar dataKey="count" fill="#9333ea" radius={[4, 4, 0, 0]} maxBarSize={28} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Recommendation Pie */}
            <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm p-5 interactive-box transition-all">
              <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-4">Recommendations</h3>
              <ResponsiveContainer width="100%" height={140}>
                <PieChart>
                  <Pie data={recommendationData} cx="50%" cy="50%" innerRadius={35} outerRadius={60} paddingAngle={4} dataKey="value">
                    {recommendationData.map((entry, index) => <Cell key={index} fill={entry.color} />)}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderRadius: "10px", border: "none", boxShadow: "0 4px 20px rgba(0,0,0,0.1)", fontSize: "11px", color: '#fff' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-2 space-y-1.5">
                {recommendationData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                      <span className="text-slate-500 dark:text-slate-400 truncate">{item.name}</span>
                    </div>
                    <span className="font-bold text-slate-800 dark:text-white">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
