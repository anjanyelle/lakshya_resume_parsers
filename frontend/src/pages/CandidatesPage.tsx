import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  Filter,
  Download,
  ArrowUpDown,
  Trash2,
  Star,
  Calendar,
  Type,
  LayoutGrid
} from 'lucide-react'
import { useCandidateStore } from '../store/candidateStore'
import { useFilterStore } from '../store/filterStore'
import Skeleton from '../components/common/Skeleton'
import CandidateCard from '../components/candidates/CandidateCard'
import CustomDropdown from '../components/common/CustomDropdown'

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
        // Search Logic
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
        
        // Match Score Filter Logic
        const score = (candidate.parsing_jobs?.[0]?.confidence_score || 0) * 100
        if (scoreFilter === '80%+ ' && score < 80) return false
        if (scoreFilter === '60-79% ' && (score < 60 || score >= 80)) return false
        if (scoreFilter === 'Below 60% ' && score >= 60) return false

        // Status/Store Filter Logic
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
        
        if (sortBy === 'Sort by Score') {
          const scoreA = a.parsing_jobs?.[0]?.confidence_score || 0
          const scoreB = b.parsing_jobs?.[0]?.confidence_score || 0
          return (scoreB - scoreA) * dir
        }

        if (sortBy === 'Sort by Name') {
          return (a.full_name || '').localeCompare(b.full_name || '') * dir
        }

        // Default: Sort by Date
        const dateA = new Date(a.created_at).getTime()
        const dateB = new Date(b.created_at).getTime()
        return (dateB - dateA) * dir
      })
  }, [candidates, localSearch, searchTerm, location, minExperience, maxExperience, skills, sortDir, scoreFilter, sortBy])

  const scoreOptions = [
    { label: 'All Scores ', value: 'All Scores' },
    { label: '80%+ ', value: '80%+ ', icon: Star, iconColor: 'text-emerald-500' },
    { label: '60-79% ', value: '60-79% ', icon: Star, iconColor: 'text-amber-500' },
    { label: 'Below 60% ', value: 'Below 60% ', icon: Star, iconColor: 'text-rose-500' },
  ]

  const sortOptions = [
    { label: 'Sort by Date', value: 'Sort by Date', icon: Calendar },
    { label: 'Sort by Score', value: 'Sort by Score', icon: Star },
    { label: 'Sort by Name', value: 'Sort by Name', icon: Type },
  ]

  const allSelected = filtered.length > 0 && filtered.every((c) => selectedIds.has(c.id))

  const handleExportData = () => {
    if (filtered.length === 0) {
      toast.error('No data to export')
      return
    }

    const headers = ['Full Name', 'Email', 'Phone', 'Location', 'Experience', 'Match Score', 'Status']
    const csvContent = [
      headers.join(','),
      ...filtered.map(c => [
        `"${c.full_name || ''}"`,
        `"${c.email || ''}"`,
        `"${c.phone || ''}"`,
        `"${c.location || ''}"`,
        `"${c.years_experience ?? 0}"`,
        `"${Math.round((c.parsing_jobs?.[0]?.confidence_score || 0) * 100)}%"`,
        `"${c.status}"`
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', `candidates_export_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    toast.success(`Exported ${filtered.length} candidates`)
  }

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Export Button Row */}
      <div className="flex items-center justify-between px-1">
        <p className="text-[13px] font-bold text-slate-800 uppercase tracking-widest">
          Candidates ({candidates.length})
        </p>
        <button
          onClick={handleExportData}
          className="flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-violet-200 transition-all hover:bg-violet-700 active:scale-95 uppercase tracking-wider"
          style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
        >
          <Download className="h-4 w-4" />
          EXPORT DATA
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col lg:flex-row flex-wrap items-center gap-3 rounded-2xl bg-white p-3 shadow-xl shadow-slate-200/40 border border-slate-100">
        {/* Search */}
        <div className="relative w-full lg:flex-1 min-w-[300px]">
          <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search candidates..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            className="w-full rounded-xl border-slate-100 bg-slate-50/50 py-3 pl-11 pr-4 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-200 transition-all font-semibold"
          />
        </div>

        {/* Filters Group */}
        <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto">
          <CustomDropdown
            options={scoreOptions}
            value={scoreFilter}
            onChange={setScoreFilter}
            icon={Filter}
            className="flex-1 lg:flex-initial"
          />

          <CustomDropdown
            options={sortOptions}
            value={sortBy}
            onChange={setSortBy}
            icon={LayoutGrid}
            className="flex-1 lg:flex-initial"
          />

          {/* Direction */}
          <button
            onClick={() => setSortDir(sortDir === 'desc' ? 'asc' : 'desc')}
            className="flex h-[42px] items-center justify-center gap-2 rounded-xl border border-slate-100 bg-white px-4 text-xs font-bold text-slate-400 hover:bg-slate-50 transition-all shadow-sm uppercase tracking-widest"
          >
            <ArrowUpDown className={`h-3.5 w-3.5 transition-transform duration-300 ${sortDir === 'asc' ? 'rotate-180 text-violet-500' : ''}`} />
            <span className="hidden xl:inline">{sortDir === 'desc' ? 'Descending' : 'Ascending'}</span>
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
          <label htmlFor="select-all" className="text-[12.5px] font-bold text-slate-400 cursor-pointer uppercase tracking-wider">
            Select All <span className="text-violet-500 ml-1 font-bold">({filtered.length})</span>
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
      {loading && candidates.length === 0 ? (
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
            <p className="text-base font-semibold text-slate-800">No candidates found</p>
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
