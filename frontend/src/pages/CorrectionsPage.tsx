import { useEffect, useMemo, useState } from "react";
import {
  fetchRecentCorrections,
  type CorrectionRecord,
} from "../services/api/corrections";
import {
  ClipboardCheck, Search, Filter, ArrowRight,
  Activity, Tag, UserCheck, Calendar
} from "lucide-react";

export default function CorrectionsPage() {
  const [rows, setRows] = useState<CorrectionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const data = await fetchRecentCorrections();
        setRows(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load corrections");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filtered = useMemo(() => {
    if (!search) return rows;
    const term = search.toLowerCase();
    return rows.filter(
      (row) =>
        row.candidate_name?.toLowerCase().includes(term) ||
        row.candidate_email?.toLowerCase().includes(term) ||
        row.field.toLowerCase().includes(term)
    );
  }, [rows, search]);

  return (
    <div className="relative min-h-[calc(100vh-64px)] animate-in fade-in duration-700 py-6 px-6 max-w-[1400px] mx-auto overflow-hidden">

      {/* Mesh Background */}
      <div className="absolute top-0 right-0 -z-10 w-[600px] h-[600px] bg-indigo-500/5 blur-[120px] rounded-full -mr-48 -mt-48" />
      <div className="absolute bottom-0 left-0 -z-10 w-[500px] h-[500px] bg-sky-500/5 blur-[100px] rounded-full -ml-32 -mb-32" />

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
            REVIEW FEEDBACK APPLIED TO PARSED ASSETS
          </p>
        </div>
        
        <button className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-xl text-[12px] font-[900] text-white shadow-lg shadow-indigo-600/20 hover:scale-[1.02] active:scale-95 transition-all outline-none">
          <Filter size={14} />
          ADVANCED FILTERS
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

        {/* Corrections Main Panel */}
        <div className="lg:col-span-8 bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-[0_4px_20px_rgb(0,0,0,0.02)] border border-white/50">
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                <ClipboardCheck size={18} />
              </div>
              <h3 className="text-sm font-black text-slate-800 tracking-tight uppercase">Recent Edits</h3>
            </div>

            {/* Search Box */}
            <div className="relative group w-full md:w-64">
              <div className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none">
                <Search size={14} className="text-slate-300 group-focus-within:text-indigo-500" />
              </div>
              <input
                type="text"
                placeholder="Search entries..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full h-10 pl-10 pr-4 bg-slate-50/50 rounded-xl border border-transparent focus:border-indigo-100 focus:bg-white outline-none text-xs font-bold text-slate-700 placeholder:text-slate-300 transition-all"
              />
            </div>
          </div>

          {/* Data List (Modern Table Replace) */}
          <div className="space-y-4">
            {/* Header Row */}
            <div className="grid grid-cols-5 gap-4 px-4 py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-50/50 rounded-lg">
              <span className="col-span-1">Candidate</span>
              <span className="col-span-1">Field</span>
              <span className="col-span-1 text-center">Original</span>
              <span className="col-span-1 text-center">Correction</span>
              <span className="col-span-1 text-right">Date</span>
            </div>

            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-16 bg-slate-50 rounded-xl animate-pulse" style={{ animationDelay: `${i * 100}ms` }} />
              ))
            ) : error ? (
              <div className="p-8 text-center bg-rose-50 text-rose-500 rounded-2xl border border-rose-100 text-xs font-bold italic">
                Intelligence failure: {error}
              </div>
            ) : filtered.length === 0 ? (
              <div className="p-16 text-center">
                <p className="text-xs font-bold text-slate-300 uppercase tracking-[0.3em]">No matching adjustments found</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-50">
                {filtered.map((row) => (
                  <div key={`${row.corrected_at}-${row.field}`} className="grid grid-cols-5 gap-4 px-4 py-4 items-center group hover:bg-slate-50/50 transition-colors rounded-xl">
                    <div className="col-span-1 min-w-0">
                      <p className="text-[13px] font-black text-slate-800 truncate leading-tight group-hover:text-indigo-600 transition-colors">
                        {row.candidate_name ?? row.candidate_email ?? "Unknown Asset"}
                      </p>
                      <p className="text-[10px] font-bold text-slate-400 truncate opacity-0 group-hover:opacity-100 transition-opacity">User ID: {row.candidate_id?.slice(0, 8)}</p>
                    </div>
                    <div className="col-span-1">
                      <span className="px-2.5 py-1 bg-slate-100 text-slate-600 text-[10px] font-[900] uppercase tracking-wider rounded-lg border border-slate-200/50">
                        {row.field.split('.').pop()}
                      </span>
                    </div>
                    <div className="col-span-1 text-center">
                      <span className="text-xs text-slate-400 line-through decoration-slate-300 truncate block px-2 italic">{row.original ?? "—"}</span>
                    </div>
                    <div className="col-span-1 flex items-center justify-center gap-2">
                      <ArrowRight size={10} className="text-indigo-300" />
                      <span className="text-[13px] font-black text-indigo-600 bg-indigo-50/50 px-2 py-1 rounded-md">{row.corrected ?? "—"}</span>
                    </div>
                    <div className="col-span-1 text-right">
                      <span className="text-[12px] font-black text-slate-400 uppercase tracking-tighter">
                        {new Date(row.corrected_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Analytics Column */}
        <div className="lg:col-span-4 flex flex-col gap-8">

          {/* Activity Visualization Card */}
          <div className="bg-white rounded-2xl p-6 shadow-[0_4px_20px_rgb(0,0,0,0.02)] border border-slate-50/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-xl bg-sky-50 flex items-center justify-center text-sky-600">
                <UserCheck size={18} />
              </div>
              <h3 className="text-sm font-black text-slate-800 tracking-tight uppercase">Top Reviewers</h3>
            </div>

            <div className="space-y-4">
              {["Master Admin", "Senior Reviewer", "Lead Recruiter"].map((name, i) => (
                <div key={name} className="flex items-center justify-between p-4 bg-slate-50/50 rounded-2xl border border-transparent hover:border-sky-100 transition-all">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm shadow-md ${i === 0 ? 'bg-indigo-500' : 'bg-slate-300'}`}>
                      {name[0]}
                    </div>
                    <span className="text-[13px] font-bold text-slate-700">{name}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-[14px] font-black text-slate-800 leading-none">
                      {loading ? "—" : Math.floor(Math.random() * 50 + 10)}
                    </p>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Adjustments</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Critical Fields Card */}
          <div className="bg-white rounded-[24px] p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-50/50">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600">
                <Tag size={20} />
              </div>
              <h3 className="text-[17px] font-black text-slate-800 tracking-tight uppercase">Heatmap Fields</h3>
            </div>

            <div className="space-y-3">
              {[
                { field: "contact.name", status: "Critical", color: "text-rose-500 bg-rose-50" },
                { field: "education.degree", status: "Requires Training", color: "text-amber-500 bg-amber-50" },
                { field: "experience.company", status: "Stable", color: "text-emerald-500 bg-emerald-50" }
              ].map((item) => (
                <div key={item.field} className="group p-4 bg-slate-50/30 hover:bg-white rounded-2xl border border-transparent hover:border-slate-100 flex flex-col gap-2 transition-all">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-slate-500 group-hover:text-indigo-600 transition-colors uppercase tracking-tight">{item.field}</span>
                    <span className={`px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-widest ${item.color}`}>
                      {item.status}
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full ${item.color.split(' ')[0]} bg-current opacity-30 w-3/4 animate-pulse`} />
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
