import { useEffect, useMemo, useState } from 'react'
import { ClipboardCheck, Filter, UserRound, Search, Trash2, ArrowRight } from 'lucide-react'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { fetchRecentCorrections, type CorrectionRecord } from '../services/api/corrections'
import Skeleton from '../components/common/Skeleton'

export default function CorrectionsPage() {
  const [rows, setRows] = useState<CorrectionRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const [fieldFilter, setFieldFilter] = useState('All Fields')

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const data = await fetchRecentCorrections()
        setRows(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load corrections')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const filtered = useMemo(() => {
    if (!search) return rows
    const term = search.toLowerCase()
    return rows.filter((row) => {
      return (
        row.full_name?.toLowerCase().includes(term) ||
        row.candidate_email?.toLowerCase().includes(term) ||
        row.field.toLowerCase().includes(term)
      )
    })

    if (fieldFilter !== 'All Fields') {
      result = result.filter(row => row.field.toLowerCase() === fieldFilter.toLowerCase())
    }

    return result
  }, [rows, search, fieldFilter])

  const fields = useMemo(() => {
    const set = new Set(rows.map(r => r.field))
    return ['All Fields', ...Array.from(set)]
  }, [rows])

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Search & Stats Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-xl shadow-card border border-slate-300">
        <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm outline-none transition-all focus:border-orange-400 focus:bg-white focus:ring-2 focus:ring-orange-100 placeholder-slate-500 font-bold"
              placeholder="Search candidate, field, or value..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
           <button 
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className={`flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-semibold transition-all ${
              isFilterOpen ? 'bg-orange-500 border-orange-500 text-white shadow-lg' : 'border-slate-200 bg-white text-slate-600 hover:bg-orange-50 hover:text-orange-600 hover:border-orange-100'
            }`}
          >
            <Filter className="h-4 w-4" />
            Advanced Filters
          </button>
        </div>
      </div>

      {isFilterOpen && (
        <div className="bg-white p-5 rounded-xl shadow-xl shadow-slate-200/40 border border-slate-100 flex flex-wrap gap-4 animate-slide-down">
          <div className="space-y-1.5 flex-1 min-w-[200px]">
             <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Filter by Field</label>
             <select
               className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-xs font-bold text-slate-700 outline-none focus:border-orange-400"
               value={fieldFilter}
               onChange={(e) => setFieldFilter(e.target.value)}
             >
               {fields.map(f => <option key={f} value={f}>{f}</option>)}
             </select>
          </div>
          <div className="space-y-1.5 flex-1 min-w-[200px]">
             <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Reviewer</label>
             <input disabled className="w-full rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-2 text-xs font-bold text-slate-300 cursor-not-allowed" placeholder="Coming soon..." />
          </div>
          <div className="space-y-1.5 flex-1 min-w-[200px]">
             <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest ml-1">Date Range</label>
             <input disabled className="w-full rounded-xl border border-slate-200 bg-slate-50/50 px-4 py-2 text-xs font-bold text-slate-300 cursor-not-allowed" placeholder="Coming soon..." />
          </div>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        {/* Main Table Card */}
        <div className="rounded-xl bg-white shadow-card border border-slate-300 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-50 bg-slate-50/30">
            <div className="flex items-center gap-2">
              <ClipboardCheck className="h-4 w-4 text-orange-600" />
              <h3 className="text-sm font-bold text-slate-800">Recent Corrections</h3>
            </div>
            <span className="text-[10px] font-black text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full uppercase tracking-widest">
              {filtered.length} entries
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50/50 text-[11px] font-black text-slate-500 uppercase tracking-wider border-b border-slate-100">
                  <th className="px-6 py-3">Candidate</th>
                  <th className="px-6 py-3">Field</th>
                  <th className="px-6 py-3">Original</th>
                  <th className="px-6 py-3">Corrected</th>
                  <th className="px-6 py-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8"><Skeleton lines={4} /></td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-sm text-red-500">{error}</td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-20 text-center">
                       <div className="flex flex-col items-center justify-center opacity-40">
                         <ClipboardCheck className="h-10 w-10 text-slate-200 mb-2" />
                         <p className="text-sm font-bold text-slate-500">No corrections found</p>
                       </div>
                    </td>
                  </tr>
                ) : (
                  filtered.map((row) => (
                    <tr
                      key={`${row.corrected_at}-${row.field}`}
                      className="group transition-colors hover:bg-orange-50/30"
                    >
                      <td className="px-6 py-4">
                        <div className="flex flex-col">
                          <span className="text-sm font-bold text-slate-800">{row.candidate_name ?? 'Unknown'}</span>
                          <span className="text-[10px] font-bold text-slate-500">{row.candidate_email}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex rounded-lg bg-slate-100 px-2 py-0.5 text-[10px] font-black text-slate-500 uppercase tracking-tight">
                          {row.field}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-xs text-slate-500 font-bold line-through decoration-slate-300 decoration-1">
                          {row.original || '—'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="flex items-center gap-1.5 text-xs font-bold text-teal-600">
                          <ArrowRight className="h-3 w-3" />
                          {row.corrected || '—'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-xs text-slate-500 font-bold">
                          {new Date(row.corrected_at).toLocaleDateString()}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sidebar Cards */}
        <div className="space-y-6 flex flex-col">
          {/* Reviewer Activity */}
          <div className="rounded-xl bg-white p-6 shadow-card border border-slate-300">
            <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-orange-600" />
              Reviewer Activity
            </h3>
            <div className="space-y-3">
              {['Admin', 'Reviewer', 'Recruiter'].map((name) => (
                <div
                  key={name}
                  className="flex items-center justify-between group cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-50 text-orange-600 transition-colors group-hover:bg-orange-600 group-hover:text-white">
                      <UserRound className="h-4 w-4" />
                    </div>
                    <span className="text-xs font-bold text-slate-800">{name}</span>
                  </div>
                  <span className="text-[10px] font-black text-slate-500 bg-slate-50 px-2 py-1 rounded-lg">
                    {loading ? '—' : `${rows.filter(r => (r.reviewer || '').toLowerCase().includes(name.toLowerCase())).length} edits`}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Training Needs */}
          <div className="rounded-xl bg-white p-6 shadow-card border border-slate-300">
            <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-teal-500" />
              Fields Needing Training
            </h3>
            <div className="space-y-2">
              {[
                { field: 'contact.name.name', level: 'High' },
                { field: 'education.degree', level: 'Medium' },
                { field: 'work_experience.company', level: 'Low' }
              ].map((item) => (
                <div key={item.field} className="group rounded-xl border border-dashed border-slate-200 p-3 hover:border-orange-300 transition-colors">
                  <p className="text-[11px] font-black text-slate-800 truncate">{item.field}</p>
                  <div className="mt-2 flex items-center justify-between">
                     <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-tighter ${
                       item.level === 'High' ? 'bg-red-50 text-red-500' : 
                       item.level === 'Medium' ? 'bg-amber-50 text-amber-600' : 'bg-blue-50 text-blue-500'
                     }`}>
                       {item.level} Priority
                     </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
