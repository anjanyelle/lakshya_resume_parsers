import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  Filter,
  Download,
  ArrowUpDown,
  Trash2,
} from 'lucide-react'
import { useCandidateStore } from '../store/candidateStore'
import { useFilterStore } from '../store/filterStore'
import Skeleton from '../components/common/Skeleton'
import CandidateCard from '../components/candidates/CandidateCard'

export default function CandidatesPage() {
  const navigate = useNavigate()
  const {
    candidates,
    loading,
    error,
    selectedIds,
    toggleSelected,
    loadCandidates,
    removeCandidates,
    selectAll,
    clearSelected,
  } = useCandidateStore()
  const { searchTerm, skills, location, minExperience, maxExperience } = useFilterStore()
  const [scoreFilter, setScoreFilter] = useState('All Scores')
  const [sortBy, setSortBy] = useState('Sort by Date')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')
  const [localSearch, setLocalSearch] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    loadCandidates(controller.signal)
    const interval = window.setInterval(() => loadCandidates(), 10000)
    return () => {
      controller.abort()
      window.clearInterval(interval)
    }
  }, [loadCandidates])

  const filtered = useMemo(() => {
    return candidates
      .filter((candidate) => {
        const search = (localSearch || searchTerm).toLowerCase()
        if (search) {
          const values = [
            candidate.full_name,
            candidate.email,
            candidate.current_company,
            candidate.current_title,
            candidate.location,
          ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase()
          if (!values.includes(search)) return false
        }
        if (location && !candidate.location?.toLowerCase().includes(location.toLowerCase())) {
          return false
        }
        if (minExperience !== null && (candidate.years_experience ?? 0) < minExperience) {
          return false
        }
        if (maxExperience !== null && (candidate.years_experience ?? 0) > maxExperience) {
          return false
        }
        if (skills.length) {
          const candidateSkills = (candidate.skills ?? []).map((skill) => skill.name)
          if (!skills.some((skill) => candidateSkills.includes(skill))) return false
        }
        return true
      })
      .sort((a, b) => {
        const dir = sortDir === 'asc' ? 1 : -1
        const dateA = new Date(a.created_at).getTime()
        const dateB = new Date(b.created_at).getTime()
        return (dateB - dateA) * dir
      })
  }, [candidates, localSearch, searchTerm, location, minExperience, maxExperience, skills, sortDir])

  const allSelected = filtered.length > 0 && filtered.every((c) => selectedIds.has(c.id))

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Export Button Row */}
      <div className="flex items-center justify-between px-1">
        <p className="text-[13px] font-semibold text-slate-400 uppercase tracking-widest">
          Manage and review analyzed candidates ({filtered.length} of {candidates.length})
        </p>
        <button
          className="flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-violet-200 transition-all hover:bg-violet-700 active:scale-95 uppercase tracking-wider"
          style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
        >
          <Download className="h-4 w-4" />
          EXPORT DATA
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row flex-wrap items-center gap-3 rounded-xl bg-white p-3 shadow-xl shadow-slate-200/50 border border-slate-100/50">
        {/* Search */}
        <div className="relative w-full sm:flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search candidates..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            className="w-full rounded-lg border-0 bg-slate-50 py-2.5 pl-9 pr-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-300 transition-all font-medium"
          />
        </div>

        {/* Filters Group */}
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          {/* Score Filter */}
          <div className="flex flex-1 sm:flex-initial items-center gap-1.5">
            <select
              value={scoreFilter}
              onChange={(e) => setScoreFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-8 text-sm font-semibold text-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-300 cursor-pointer"
            >
              <option>All Scores</option>
              <option>80%+</option>
              <option>60-79%</option>
              <option>Below 60%</option>
            </select>
          </div>

          {/* Sort */}
          <div className="flex flex-1 sm:flex-initial items-center gap-1.5">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-8 text-sm font-semibold text-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-300 cursor-pointer"
            >
              <option>Sort by Date</option>
              <option>Sort by Score</option>
              <option>Sort by Name</option>
            </select>
          </div>

          {/* Direction */}
          <button
            onClick={() => setSortDir(sortDir === 'desc' ? 'asc' : 'desc')}
            className="flex h-9 items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-500 hover:bg-slate-50 transition-colors shadow-sm"
          >
            <ArrowUpDown className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">{sortDir === 'desc' ? 'Descending' : 'Ascending'}</span>
          </button>
        </div>
      </div>

      {/* Select All Row */}
      <div className="flex items-center justify-between gap-3 px-1">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="select-all"
            checked={allSelected}
            onChange={() => allSelected ? clearSelected() : selectAll(filtered.map((c) => c.id))}
            className="h-4 w-4 rounded border-slate-300 accent-violet-600 cursor-pointer shadow-sm"
          />
          <label htmlFor="select-all" className="text-[12.5px] font-semibold text-slate-400 cursor-pointer uppercase tracking-wider">
            Select All <span className="text-violet-500/80 ml-1 font-bold">({filtered.length} candidates)</span>
          </label>
        </div>
        {selectedIds.size > 0 && (
          <button
            onClick={() => removeCandidates(Array.from(selectedIds))}
            className="flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-100 transition-colors shadow-sm"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete Selected ({selectedIds.size})
          </button>
        )}
      </div>

      {/* Candidates Grid */}
      {loading ? (
        <div className="rounded-xl bg-white p-6 shadow-xl shadow-slate-200/50 border border-slate-100/50">
          <Skeleton lines={6} />
        </div>
      ) : error && candidates.length === 0 ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-600 shadow-sm">
          {error}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-slate-200 bg-white/50 p-12 md:p-20 text-center shadow-sm">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-50 text-violet-400 shadow-inner">
            <Search className="h-7 w-7" />
          </div>
          <div>
            <p className="text-base font-bold text-slate-800">No candidates found</p>
            <p className="text-sm text-slate-500 mt-1">Try adjusting your search or filters to see more results.</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 items-stretch">
          {filtered.map((candidate) => (
            <CandidateCard
              key={candidate.id}
              candidate={candidate}
              isSelected={selectedIds.has(candidate.id)}
              onToggleSelect={() => toggleSelected(candidate.id)}
              onDelete={(id) => removeCandidates([id])}
              onView={(id) => navigate(`/candidates/${id}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
