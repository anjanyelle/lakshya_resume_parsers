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
import BulkActions from '../components/candidates/BulkActions'
import { toast } from 'react-hot-toast'
import { FileText, FileSpreadsheet, ChevronDown } from 'lucide-react'

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
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('Sort by Date')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')
  const [localSearch, setLocalSearch] = useState('')
  const [showExportDropdown, setShowExportDropdown] = useState(false)

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

        // Status Filter Logic
        if (statusFilter !== 'all' && candidate.status?.toLowerCase() !== statusFilter) {
          return false
        }

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

  const statusOptions = [
    { label: 'All Statuses', value: 'all' },
    { label: 'New', value: 'new' },
    { label: 'Reviewing', value: 'reviewing' },
    { label: 'Shortlisted', value: 'shortlisted' },
    { label: 'Interviewed', value: 'interviewed' },
    { label: 'Hired', value: 'hired' },
    { label: 'Rejected', value: 'rejected' },
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
        <p className="text-[14px] font-black text-slate-500 uppercase tracking-[0.2em] select-none">
          Candidates ({candidates.length})
        </p>

        <div className="relative">
          <button
            onClick={() => setShowExportDropdown(!showExportDropdown)}
            className="flex items-center gap-2 rounded-xl px-5 py-2.5 text-[11px] font-black text-white shadow-lg shadow-orange-500/15 transition-all hover:bg-orange-600 hover:scale-[1.02] active:scale-95 uppercase tracking-widest bg-orange-500"
          >
            <Download className="h-4 w-4" />
            EXPORT DATA
            <ChevronDown className={`ml-1 h-3 w-3 transition-transform ${showExportDropdown ? 'rotate-180' : ''}`} />
          </button>

          {showExportDropdown && (
            <div className="absolute right-0 top-full mt-2 z-[60] w-56 overflow-hidden rounded-2xl border border-slate-100 bg-white/95 p-1.5 shadow-2xl backdrop-blur-xl animate-in fade-in zoom-in-95 slide-in-from-top-2">
              <button
                onClick={() => { handleExportData(); setShowExportDropdown(false); }}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-all uppercase tracking-tight"
              >
                <FileSpreadsheet className="h-4 w-4 text-emerald-500" />
                Excel / CSV Spreadsheet
              </button>
              <button
                onClick={() => setShowExportDropdown(false)}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-all uppercase tracking-tight"
              >
                <FileText className="h-4 w-4 text-rose-500" />
                Detailed PDF Report
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Search & Filter Bar Decoupled */}
      <div className="flex flex-col xl:flex-row items-stretch gap-4 transition-all duration-300">
        {/* Search Island */}
        <div className="flex-1 min-w-0 flex items-stretch rounded-2xl bg-white shadow-premium border border-slate-200/60 overflow-hidden focus-within:ring-2 focus-within:ring-orange-500/10 transition-all duration-300 h-[52px]">
          <div className="relative flex-1 group bg-slate-50/5">
            <Search className="absolute left-5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 group-focus-within:text-orange-500 transition-colors" />
            <input
              type="text"
              placeholder="Search candidates..."
              value={localSearch}
              onChange={(e) => setLocalSearch(e.target.value)}
              className="w-full h-full bg-transparent pl-12 pr-4 text-[13px] text-slate-600 placeholder-slate-400 focus:outline-none font-bold placeholder:font-medium"
            />
          </div>
        </div>

        {/* Filters & Sorting Islands */}
        <div className="flex flex-wrap items-center gap-3">
          <CustomDropdown
            options={scoreOptions}
            value={scoreFilter}
            onChange={setScoreFilter}
            icon={Filter}
            className="!min-w-[140px] shadow-premium"
          />

          <CustomDropdown
            options={statusOptions}
            value={statusFilter}
            onChange={setStatusFilter}
            icon={LayoutGrid}
            className="!min-w-[140px] shadow-premium"
          />

          <CustomDropdown
            options={sortOptions}
            value={sortBy}
            onChange={setSortBy}
            icon={Calendar}
            className="!min-w-[140px] shadow-premium"
          />

          {/* Direction Island */}
          <button
            onClick={() => setSortDir(sortDir === 'desc' ? 'asc' : 'desc')}
            className={`flex items-center justify-center gap-2 px-5 rounded-2xl border border-slate-200/60 bg-white shadow-premium text-[10px] font-black transition-all uppercase tracking-widest h-[52px] ${sortDir === 'asc' ? 'text-orange-600 ring-2 ring-orange-500/10' : 'text-slate-400 hover:border-orange-200 hover:text-slate-600 shadow-sm'}`}
          >
            <ArrowUpDown className={`h-3.5 w-3.5 transition-transform duration-500 ${sortDir === 'asc' ? 'rotate-180 scale-110' : ''}`} />
            <span className="hidden xl:inline">{sortDir === 'desc' ? 'Desc' : 'Asc'}</span>
          </button>
        </div>
      </div>

      {/* Select All Row */}
      <div className="flex items-center justify-between gap-3 px-2">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="select-all"
            checked={allSelected}
            onChange={() => allSelected ? clearSelected() : selectAll(filtered.map((c) => c.id))}
            className="h-3.5 w-3.5 rounded border-slate-300 accent-orange-600 cursor-pointer shadow-sm transition-transform active:scale-90"
          />
          <label htmlFor="select-all" className="text-[11px] font-black text-slate-400 cursor-pointer uppercase tracking-[0.15em] select-none">
            Select All <span className="text-orange-500 ml-1">({filtered.length})</span>
          </label>
        </div>
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
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-orange-50 text-orange-400 shadow-inner">
            <Search className="h-7 w-7" />
          </div>
          <div>
            <p className="text-base font-semibold text-slate-600">No candidates found</p>
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

      {/* Sticky Bulk Actions */}
      <BulkActions
        selectedIds={selectedIds}
        candidates={candidates}
        onDelete={() => {
          removeCandidates(Array.from(selectedIds))
          clearSelected()
        }}
        onClear={clearSelected}
      />
    </div>
  )
}
