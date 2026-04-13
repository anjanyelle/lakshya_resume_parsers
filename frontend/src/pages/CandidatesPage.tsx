import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCandidateStore } from "../store/useCandidateStore";
import toast from "react-hot-toast";
import { 
  Users, Search, Filter, ArrowUpDown, ArrowUp, ArrowDown, 
  Download, Eye, MoreVertical, Trash2, Mail, Phone, 
  MapPin, Calendar, FileText, ChevronLeft, ChevronRight, LogOut
} from "lucide-react";

type FilterType = "all" | "high-confidence" | "needs-review";
type SortType = "date-added" | "name" | "confidence-score";
type SortDir = "asc" | "desc";

export default function CandidatesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState<FilterType>("all");
  const [sort, setSort] = useState<SortType>("date-added");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const { candidates, pagination, isLoading, fetchCandidates, deleteCandidate } =
    useCandidateStore();
  const navigate = useNavigate();

  const itemsPerPage = 20;

  useEffect(() => {
    loadCandidates();
  }, [currentPage, searchTerm]);

  const loadCandidates = async () => {
    try {
      await fetchCandidates(currentPage, itemsPerPage, searchTerm);
    } catch (error) {
      toast.error("Failed to load candidates");
    }
  };

  const filteredCandidates = candidates
    .filter((candidate) => {
      const confidence = candidate.parsing_status?.confidence_score || 0;
      return (
        filter === "all" ||
        (filter === "high-confidence" && confidence >= 0.8) ||
        (filter === "needs-review" && confidence < 0.8)
      );
    })
    .sort((a, b) => {
      let cmp = 0;
      switch (sort) {
        case "name":
          cmp = (a.full_name || "").localeCompare(b.full_name || "");
          break;
        case "confidence-score":
          cmp =
            (a.parsing_status?.confidence_score || 0) -
            (b.parsing_status?.confidence_score || 0);
          break;
        default:
          cmp =
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      }
      return sortDir === "desc" ? -cmp : cmp;
    });

  const getInitials = (name: string) => {
    if (!name) return "?";
    return name
      .split(" ")
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  };

  const avatarColors: Record<string, string> = {};
  const colorList = [
    "from-rose-400 to-orange-400",
    "from-indigo-400 to-violet-400",
    "from-amber-400 to-orange-500",
    "from-blue-400 to-blue-600",
    "from-cyan-400 to-teal-500",
    "from-pink-400 to-purple-500",
    "from-green-400 to-emerald-600",
  ];
  
  const getAvatarColor = (id: string) => {
    const idx = id.charCodeAt(0) % colorList.length;
    return colorList[idx];
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const getScoreInfo = (score: number) => {
    if (score >= 80) return { color: "text-emerald-500", bg: "bg-emerald-50", stroke: "#10b981", track: "#ecfdf5" };
    if (score >= 60) return { color: "text-amber-500", bg: "bg-amber-50", stroke: "#f59e0b", track: "#fffbeb" };
    return { color: "text-rose-500", bg: "bg-rose-50", stroke: "#f43f5e", track: "#fff1f2" };
  };

  // Circular score SVG gauge - High Fidelity Version
  const ScoreGauge = ({ score }: { score: number }) => {
    const info = getScoreInfo(score);
    const r = 18;
    const circ = 2 * Math.PI * r;
    const filled = (score / 100) * circ;
    
    return (
      <div className="relative flex items-center justify-center w-12 h-12">
        <svg width="48" height="48" viewBox="0 0 48 48" className="transform -rotate-90">
          <circle cx="24" cy="24" r={r} fill="none" stroke="#F1F5F9" strokeWidth="4" />
          <circle
            cx="24" cy="24" r={r} fill="none"
            stroke={info.stroke} strokeWidth="4"
            strokeDasharray={`${filled} ${circ - filled}`}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <span className={`absolute text-[11px] font-[900] ${info.color}`}>
          {score}
        </span>
      </div>
    );
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    if (selectedIds.size === filteredCandidates.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredCandidates.map((c) => c.id)));
    }
  };

  const handleExport = () => {
    const rows = filteredCandidates
      .filter((c) => selectedIds.size === 0 || selectedIds.has(c.id))
      .map((c) => ({
        name: c.full_name,
        email: c.email,
        phone: c.phone,
        location: c.location,
        score: Math.round((c.parsing_status?.confidence_score || 0) * 100),
        status: c.parsing_status?.status,
        date: c.created_at,
      }));

    if (rows.length === 0) return;

    const csv = [
      Object.keys(rows[0] || {}).join(","),
      ...rows.map((r) => Object.values(r).join(",")),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "candidates.csv";
    a.click();
  };

  const handleDelete = async (id: string, e?: React.MouseEvent) => {
    e?.stopPropagation();
    if (!confirm("Delete this candidate?")) return;
    try {
      if (deleteCandidate) await deleteCandidate(id);
      toast.success("Candidate deleted");
      loadCandidates();
    } catch {
      toast.error("Failed to delete");
    }
  };

  const handleDownload = (candidate: any, e?: React.MouseEvent) => {
    e?.stopPropagation();
    const data = JSON.stringify(candidate, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${candidate.full_name || "candidate"}.json`;
    a.click();
  };

  const totalCount = pagination?.total_items || filteredCandidates.length;

  return (
    <div className="relative min-h-[calc(100vh-64px)] animate-in fade-in duration-700 py-8 px-6 max-w-[1400px] mx-auto overflow-hidden">
      
      {/* Dynamic Background Blobs */}
      <div className="absolute top-0 right-0 -z-10 w-[600px] h-[600px] bg-indigo-500/5 blur-[120px] rounded-full -mr-48 -mt-48 animate-pulse" />
      <div className="absolute bottom-0 left-0 -z-10 w-[500px] h-[500px] bg-emerald-500/5 blur-[100px] rounded-full -ml-32 -mb-32 animate-pulse" style={{ animationDelay: '2s' }} />

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
            MANAGE AND REVIEW ANALYZED CANDIDATES ({filteredCandidates.length} OF {totalCount})
          </p>
        </div>
        
        <button
          onClick={handleExport}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-indigo-500 rounded-xl text-[12px] font-[900] text-white shadow-lg shadow-indigo-600/20 hover:scale-[1.02] active:scale-95 transition-all outline-none"
        >
          <Download size={14} />
          EXPORT DATA
        </button>
      </div>

      {/* Modern Filter Bar */}
      <div className="bg-white/70 backdrop-blur-xl rounded-2xl p-2 mb-6 border border-white/50 shadow-[0_4px_20px_rgb(0,0,0,0.02)] flex flex-col lg:flex-row items-center gap-3">
        <div className="relative flex-1 group w-full">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <Search size={16} className="text-slate-300 group-focus-within:text-indigo-500 transition-colors" />
          </div>
          <input
            type="text"
            placeholder="Search Intelligence - name, email, or technical assets..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
            className="w-full h-11 pl-12 pr-4 bg-slate-50/20 rounded-xl border border-transparent focus:border-slate-100 focus:bg-white transition-all outline-none text-[12px] font-bold text-slate-700 placeholder:text-slate-300"
          />
        </div>

        <div className="flex items-center gap-2 w-full lg:w-auto h-11">
          {/* Status Filter */}
          <div className="flex items-center gap-2 h-full px-4 bg-white rounded-xl border border-slate-50 shadow-sm transition-all min-w-[160px] group/select">
            <Filter size={14} className="text-slate-300 group-focus-within:text-indigo-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as FilterType)}
              className="bg-transparent outline-none text-[12px] font-black text-slate-600 cursor-pointer w-full uppercase tracking-tighter"
            >
              <option value="all">ALL SCORES</option>
              <option value="high-confidence">HIGH MATCH</option>
              <option value="needs-review">NEEDS REVIEW</option>
            </select>
          </div>

          {/* Sort Menu */}
          <div className="flex items-center gap-2 h-full px-4 bg-white rounded-xl border border-slate-50 shadow-sm transition-all min-w-[160px] group/select">
            <ArrowUpDown size={14} className="text-slate-300 group-focus-within:text-indigo-500" />
            <select
              value={sort}
              onChange={(e) => { setSort(e.target.value as SortType); setCurrentPage(1); }}
              className="bg-transparent outline-none text-[12px] font-black text-slate-600 cursor-pointer w-full uppercase tracking-tighter"
            >
              <option value="date-added">SORT BY DATE</option>
              <option value="name">SORT BY NAME</option>
              <option value="confidence-score">SORT BY SCORE</option>
            </select>
          </div>

          {/* Sort Direction */}
          <button
            onClick={() => setSortDir((d) => d === "desc" ? "asc" : "desc")}
            className="h-full px-5 bg-white rounded-xl border border-slate-50 shadow-sm hover:border-indigo-100 transition-all flex items-center gap-2 text-slate-400 hover:text-indigo-600"
          >
            {sortDir === "desc" ? <ArrowDown size={14} /> : <ArrowUp size={14} />}
            <span className="text-[11px] font-black uppercase tracking-tighter">{sortDir === "desc" ? "DESCENDING" : "ASCENDING"}</span>
          </button>
        </div>
      </div>

      {/* Batch Selection Bar */}
      <div className="flex items-center gap-4 mb-6 px-1">
        <label className="group flex items-center gap-3 cursor-pointer">
          <div 
            onClick={selectAll}
            className={`
              w-5 h-5 rounded-md border-2 transition-all flex items-center justify-center
              ${selectedIds.size === filteredCandidates.length && filteredCandidates.length > 0 
                ? "bg-indigo-600 border-indigo-600" 
                : "bg-white border-slate-200 group-hover:border-indigo-300"}
            `}
          >
             {selectedIds.size === filteredCandidates.length && filteredCandidates.length > 0 && <CheckCircle2 size={14} className="text-white" />}
          </div>
          <span className="text-[12px] font-black text-indigo-500/80 uppercase tracking-widest">
            Select All ({filteredCandidates.length} Candidates)
          </span>
        </label>
      </div>

      {/* Content Area */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-32 animate-in fade-in zoom-in duration-500">
           <div className="relative w-16 h-16 blur-2xl bg-indigo-600/20 absolute -z-10 animate-pulse" />
           <div className="w-12 h-12 border-4 border-indigo-100 border-t-indigo-600 rounded-full animate-spin" />
           <p className="mt-6 text-[11px] font-[900] text-slate-400 tracking-[0.3em] uppercase">Deep Scanning Assets...</p>
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="bg-white/50 backdrop-blur-md rounded-[32px] border border-white/80 p-24 text-center shadow-xl shadow-slate-200/50">
           <div className="w-20 h-20 bg-indigo-50 text-indigo-200 rounded-3xl flex items-center justify-center mx-auto mb-6">
              <Users size={40} />
           </div>
           <h3 className="text-xl font-black text-slate-800 mb-2 uppercase tracking-tight">Zero Matches Found</h3>
           <p className="text-slate-400 text-sm max-w-sm mx-auto leading-relaxed">
             We couldn't find any candidates matching your current intelligence filters. 
             Try adjusting your search terms or confidence metrics.
           </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredCandidates.map((candidate) => {
              const score = Math.round((candidate.parsing_status?.confidence_score || 0) * 100);
              const topSkills = (candidate.skills || []).slice(0, 6);
              const extraSkills = (candidate.skills || []).length - topSkills.length;
              const isSelected = selectedIds.has(candidate.id);

              return (
                <div
                  key={candidate.id}
                  onClick={() => navigate(`/candidates/${candidate.id}`)}
                  className={`
                    group bg-white rounded-2xl p-6 border transition-all duration-300 cursor-pointer relative overflow-hidden
                    ${isSelected 
                      ? "border-indigo-600 shadow-xl shadow-indigo-600/10" 
                      : "border-slate-50 shadow-[0_4px_20px_rgb(0,0,0,0.02)] hover:shadow-xl hover:shadow-indigo-600/5 hover:border-indigo-100"}
                  `}
                >
                  <div className="flex gap-5">
                     {/* Selection Checkbox */}
                     <div 
                       onClick={(e) => { e.stopPropagation(); toggleSelect(candidate.id); }}
                       className={`
                        w-5 h-5 rounded-md border-2 mt-2 flex-shrink-0 transition-all flex items-center justify-center
                        ${isSelected ? "bg-indigo-600 border-indigo-600" : "bg-white border-slate-200"}
                       `}
                     >
                        {isSelected && <CheckCircle2 size={14} className="text-white" />}
                     </div>

                     <div className="flex-1 min-w-0">
                        {/* Top Profile Header */}
                        <div className="flex items-start justify-between gap-4 mb-6">
                           <div className="flex items-center gap-4 min-w-0">
                              <div className={`
                                w-11 h-11 rounded-xl bg-gradient-to-br ${getAvatarColor(candidate.id)} 
                                flex items-center justify-center text-white text-sm font-black shadow-lg shadow-indigo-100 flex-shrink-0
                              `}>
                                 {getInitials(candidate.full_name || "")}
                              </div>
                              <div className="min-w-0">
                                 <h3 className="text-base font-black text-slate-800 tracking-tight leading-none truncate group-hover:text-indigo-600 transition-colors">
                                   {candidate.full_name || "Unknown Asset"}
                                 </h3>
                                 <p className="text-[10px] font-bold text-slate-400 mt-1.5 uppercase tracking-wider">{formatDate(candidate.created_at)}</p>
                              </div>
                           </div>
                           <div className="flex items-center gap-2">
                              <ScoreGauge score={score} />
                              <button className="p-1.5 text-slate-300 hover:text-slate-500 transition-colors">
                                 <MoreVertical size={16} />
                              </button>
                           </div>
                        </div>

                        {/* Metadata 2x2 Grid */}
                        <div className="grid grid-cols-2 gap-x-8 gap-y-4 mb-6">
                           <div className="flex items-center gap-3 min-w-0">
                              <div className="text-slate-300"><Mail size={14} /></div>
                              <span className="text-[12px] font-bold text-slate-500 truncate">{candidate.email || "No Email"}</span>
                           </div>
                           <div className="flex items-center gap-3 min-w-0">
                              <div className="text-slate-300"><Phone size={14} /></div>
                              <span className="text-[12px] font-bold text-slate-500 truncate">{candidate.phone || "+914692696680"}</span>
                           </div>
                           <div className="flex items-center gap-3 min-w-0">
                              <div className="text-slate-300"><MapPin size={14} /></div>
                              <span className="text-[12px] font-bold text-slate-500 truncate">{candidate.location || "Remote"}</span>
                           </div>
                           <div className="flex items-center gap-3 min-w-0">
                              <div className="text-slate-300"><Calendar size={14} /></div>
                              <span className="text-[11px] font-bold text-slate-300 italic truncate">Exp. not listea</span>
                           </div>
                        </div>

                        {/* Skills Section */}
                        <div className="mb-6">
                           <p className="text-[10px] font-black text-slate-300 uppercase tracking-[0.2em] mb-3">Top Skills</p>
                           <div className="flex flex-wrap gap-2">
                              {topSkills.map((skill: any, i: number) => (
                                <span key={i} className="px-3 py-1.5 bg-slate-50 text-slate-500 text-[11px] font-bold rounded-lg border border-slate-100/50">
                                   {skill.skill_name || skill.name || ""}
                                </span>
                              ))}
                              {extraSkills > 0 && (
                                <span className="px-3 py-1.5 bg-slate-50 text-indigo-500/60 text-[11px] font-bold rounded-lg border border-slate-100/50">
                                   +{extraSkills} more
                                </span>
                              )}
                           </div>
                        </div>

                        {/* Card Action Footer */}
                        <div className="flex items-center justify-between pt-5 border-t border-slate-50">
                           <button className="flex items-center gap-2 text-indigo-600 text-[12px] font-black uppercase tracking-widest hover:gap-3 transition-all">
                              <Eye size={16} /> View Details
                           </button>
                           
                           <div className="flex items-center gap-3">
                              <button 
                                onClick={(e) => handleDownload(candidate, e)}
                                className="flex items-center gap-2 px-3 py-1.5 text-slate-400 hover:text-indigo-600 transition-all font-bold text-[12px]"
                              >
                                 <Download size={16} /> Download
                              </button>
                              <button 
                                onClick={(e) => handleDelete(candidate.id, e)}
                                className="w-9 h-9 flex items-center justify-center text-slate-400 hover:text-rose-600 bg-slate-50 hover:bg-rose-50 rounded-xl border border-slate-100 hover:border-rose-100 transition-all"
                              >
                                 <Trash2 size={16} />
                              </button>
                           </div>
                        </div>
                     </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {pagination && pagination.total_pages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-12 bg-white/50 backdrop-blur-sm p-3 rounded-2xl border border-white/50 w-fit mx-auto shadow-xl shadow-slate-200/20">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={!pagination.has_prev_page}
                className="p-2.5 bg-white rounded-xl border border-slate-100 text-slate-400 hover:text-indigo-600 hover:border-indigo-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                <ChevronLeft size={20} />
              </button>
              
              <div className="flex items-center gap-1.5 px-3">
                {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                  const pageNum = i + 1;
                  const active = pagination.current_page === pageNum;
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`
                        w-10 h-10 rounded-xl text-[13px] font-black transition-all
                        ${active 
                          ? "bg-indigo-600 text-white shadow-lg shadow-indigo-200" 
                          : "bg-white text-slate-500 border border-slate-100 hover:border-indigo-100 hover:text-indigo-600"}
                      `}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>

              <button
                onClick={() => setCurrentPage((p) => Math.min(pagination.total_pages, p + 1))}
                disabled={!pagination.has_next_page}
                className="p-2.5 bg-white rounded-xl border border-slate-100 text-slate-400 hover:text-indigo-600 hover:border-indigo-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
