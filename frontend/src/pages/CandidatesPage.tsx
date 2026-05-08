import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCandidateStore } from "../store/useCandidateStore";
import CustomSelect from "../components/common/CustomSelect";
import { Users, Search, RefreshCw, User, ChevronLeft, ChevronRight, Filter } from "lucide-react";

type FilterType = "all" | "high-confidence" | "needs-review";
type SortType = "date-added" | "name" | "confidence-score";

export default function CandidatesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("date-added");
  const [currentPage, setCurrentPage] = useState(1);

  const { candidates, pagination, isLoading, fetchCandidates } = useCandidateStore();
  const navigate = useNavigate();

  const itemsPerPage = 20;

  useEffect(() => {
    loadCandidates();
  }, [currentPage, searchTerm]);

  const loadCandidates = async () => {
    try {
      await fetchCandidates(currentPage, itemsPerPage, searchTerm);
    } catch (error) {
      console.error("Failed to load candidates, using dummy data");
    }
  };

  const displayCandidates = candidates || [];

  const filteredCandidates = displayCandidates
    .filter((candidate) => {
      const confidence = candidate.parsing_status?.confidence_score || 0;
      return (
        filter === "all" ||
        (filter === "high-confidence" && confidence >= 0.8) ||
        (filter === "needs-review" && confidence < 0.8)
      );
    })
    .sort((a, b) => {
      switch (sort) {
        case "name":
          return (a.full_name || "").localeCompare(b.full_name || "");
        case "confidence-score":
          return (b.parsing_status?.confidence_score || 0) - (a.parsing_status?.confidence_score || 0);
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });

  const paginatedCandidates = filteredCandidates;

  console.log("🔍 Pagination state:", pagination);
  console.log("🔍 Candidates count:", candidates.length);

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.8) return { bg: "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/50", label: "High" };
    if (confidence >= 0.6) return { bg: "bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-800/50", label: "Medium" };
    return { bg: "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700", label: "Low" };
  };

  const getExperienceSummary = (workExperience: any[]) => {
    if (!workExperience || workExperience.length === 0) return "No experience";
    const currentJob = workExperience.find((exp) => exp.is_current);
    if (currentJob) return `${currentJob.job_title} at ${currentJob.company_name}`;
    const latestJob = workExperience[0];
    return `${latestJob.job_title} at ${latestJob.company_name}`;
  };

  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0F172A] transition-colors duration-500">
      <div className="p-6 sm:p-8 max-w-7xl mx-auto space-y-6">

        {/* Page Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-4">
            <div className="p-2.5 rounded-xl shadow-sm text-white flex-shrink-0" style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Candidates</h1>
              <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Manage and review candidate profiles with AI-powered resume insights</p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl border border-slate-100 dark:border-slate-700/50 rounded-xl px-4 py-2 shadow-sm transition-all">
            <Users className="w-4 h-4 text-slate-400" />
            <span className="text-slate-700 dark:text-white font-bold text-lg">{pagination?.total_items || displayCandidates.length}</span>
            <span className="text-slate-400 dark:text-slate-500 text-xs uppercase tracking-wider font-semibold ml-1">total</span>
          </div>
        </div>

        {/* Search + Filters Bar */}
        <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm p-4 sm:p-5 transition-all">
          <div className="flex flex-col lg:flex-row gap-3">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by name, email, or skill..."
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all outline-none dark:text-white"
              />
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400 flex-shrink-0" />
              {(["all", "high-confidence", "needs-review"] as FilterType[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  style={filter === f ? { background: '#7C3AED' } : {}}
                  className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${filter === f
                    ? "text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:text-slate-800"
                    }`}
                >
                  {f === "all" ? `All (${pagination?.total_items || candidates.length})` : f === "high-confidence" ? "High Confidence" : "Needs Review"}
                </button>
              ))}
            </div>

            {/* Sort */}
            <CustomSelect
              options={[
                { value: "date-added", label: "Date Added" },
                { value: "name", label: "Name" },
                { value: "confidence-score", label: "Confidence" }
              ]}
              value={sort}
              onChange={(val) => { setSort(val as SortType); setCurrentPage(1); }}
              className="w-40"
            />
          </div>

          {/* Results bar */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-50 dark:border-slate-700/50">
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Showing <span className="font-bold text-slate-700 dark:text-slate-200">{paginatedCandidates.length}</span> of{" "}
              <span className="font-bold text-slate-700 dark:text-slate-200">{pagination?.total_items || filteredCandidates.length}</span> candidates
              {pagination && ` · Page ${pagination.current_page} of ${pagination.total_pages}`}
            </p>
            <button
              onClick={loadCandidates}
              disabled={isLoading}
              className="flex items-center gap-1.5 text-xs font-bold text-purple-600 dark:text-purple-400 hover:text-purple-700 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
              {isLoading ? "Refreshing..." : "Refresh List"}
            </button>
          </div>
        </div>

        {/* Candidates Grid */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-64 bg-white rounded-2xl border border-slate-100">
            <div className="animate-spin rounded-full h-10 w-10 border-[3px] border-brand-100 border-t-brand-600 mb-3" />
            <p className="text-sm font-medium text-slate-400">Loading candidates...</p>
          </div>
        ) : paginatedCandidates.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {paginatedCandidates.map((candidate) => {
              const confidence = candidate.parsing_status?.confidence_score || 0;
              const badge = getConfidenceBadge(confidence);
              return (
                <div
                  key={candidate.id}
                  className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm interactive-box p-5 flex flex-col transition-all"
                >
                  {/* Card Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="h-11 w-11 bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-900 dark:to-purple-800 rounded-xl flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-purple-600 dark:text-purple-300" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="font-bold text-slate-800 dark:text-white text-sm truncate">{candidate.full_name}</h3>
                        <p className="text-xs text-slate-400 dark:text-slate-500 truncate">{candidate.email}</p>
                      </div>
                    </div>
                    <span className={`flex-shrink-0 px-2.5 py-1 text-xs font-bold rounded-full border ${badge.bg}`}>
                      {Math.round(confidence * 100)}%
                    </span>
                  </div>

                  {/* Skills */}
                  {candidate.skills && candidate.skills.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5">Skills</p>
                      <div className="flex flex-wrap gap-1.5">
                        {candidate.skills.slice(0, 4).map((skill, index) => (
                          <span key={index} className="px-2 py-0.5 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 text-xs font-semibold rounded-lg border border-purple-100 dark:border-purple-800/50">
                            {skill.skill_name}
                          </span>
                        ))}
                        {candidate.skills.length > 4 && (
                          <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 text-xs font-semibold rounded-lg">
                            +{candidate.skills.length - 4}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Experience */}
                  <div className="mb-4 flex-1">
                    <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">Experience</p>
                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-medium">
                      {getExperienceSummary(candidate.work_experience || [])}
                    </p>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-3 border-t border-slate-50 dark:border-slate-700/50">
                    <span className="text-xs text-slate-400 dark:text-slate-500">Added {formatDate(candidate.created_at)}</span>
                    <button
                      onClick={() => navigate(`/candidates/${candidate.id}`)}
                      className="px-4 py-1.5 text-white text-xs font-bold rounded-lg transition-all shadow-sm hover:shadow-purple-500/20 active:scale-95"
                      style={{ background: '#7C3AED' }}
                    >
                      View Profile
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-16 text-center">
            <div className="h-16 w-16 bg-brand-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Users className="h-8 w-8 text-brand-300" />
            </div>
            <h3 className="text-base font-bold text-slate-700 mb-1">No candidates found</h3>
            <p className="text-sm text-slate-400">
              {searchTerm ? "Try adjusting your search terms" : "Get started by uploading some resumes"}
            </p>
          </div>
        )}

        {/* Pagination */}
        {pagination && pagination.total_pages > 1 && (
          <div className="flex items-center justify-between bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-3.5">
            <p className="text-xs font-medium text-slate-500">
              Page {pagination.current_page} of {pagination.total_pages}
            </p>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={!pagination.has_prev_page}
                className="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-brand-50 hover:border-brand-300 hover:text-brand-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              {Array.from({ length: Math.min(5, pagination.total_pages) }).map((_, idx) => {
                let pageNum = idx + 1;
                if (pagination.total_pages > 5) {
                  if (pagination.current_page <= 3) pageNum = idx + 1;
                  else if (pagination.current_page >= pagination.total_pages - 2)
                    pageNum = pagination.total_pages - 4 + idx;
                  else pageNum = pagination.current_page - 2 + idx;
                }
                return (
                  <button
                    key={idx}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`h-8 w-8 flex items-center justify-center rounded-lg text-xs font-bold transition-all ${pageNum === pagination.current_page
                      ? "bg-brand-600 text-white shadow-sm"
                      : "border border-slate-200 text-slate-600 hover:bg-brand-50 hover:border-brand-300 hover:text-brand-700"
                      }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
              <button
                onClick={() => setCurrentPage((p) => Math.min(pagination.total_pages, p + 1))}
                disabled={!pagination.has_next_page}
                className="h-8 w-8 flex items-center justify-center rounded-lg border border-slate-200 text-slate-600 hover:bg-brand-50 hover:border-brand-300 hover:text-brand-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
