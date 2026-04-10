import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search,
  Filter,
  Download,
  Eye,
  Trash2,
  MoreVertical,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Star,
  ChevronDown,
  ArrowUpDown,
} from 'lucide-react'
import { useCandidateStore } from '../store/candidateStore'
import { useFilterStore } from '../store/filterStore'
import Skeleton from '../components/common/Skeleton'

function getInitials(name?: string | null) {
  if (!name) return '?'
  return name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
}

function getAvatarColor(name?: string | null) {
  const colors = [
    'linear-gradient(135deg,#7c3aed,#a78bfa)',
    'linear-gradient(135deg,#14b8a6,#2dd4bf)',
    'linear-gradient(135deg,#f97316,#fb923c)',
    'linear-gradient(135deg,#ec4899,#f472b6)',
    'linear-gradient(135deg,#3b82f6,#60a5fa)',
    'linear-gradient(135deg,#10b981,#34d399)',
  ]
  const idx = (name?.charCodeAt(0) ?? 0) % colors.length
  return colors[idx]
}

function getScoreColor(score?: number | null) {
  if (!score && score !== 0) return '#94a3b8'
  const s = score > 1 ? score : score * 100
  if (s >= 80) return '#10b981'
  if (s >= 60) return '#f59e0b'
  return '#ef4444'
}

function formatScore(score?: number | null) {
  if (score == null) return null
  return score > 1 ? `${Math.round(score)}%` : `${Math.round(score * 100)}%`
}

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
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          Manage and review analyzed candidates ({filtered.length} of {candidates.length})
        </p>
        <button
          className="flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold text-white shadow-md transition-all hover:opacity-90"
          style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
        >
          <Download className="h-4 w-4" />
          Export
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-wrap items-center gap-2 rounded-xl bg-white p-3 shadow-card border border-slate-100">
        {/* Search */}
        <div className="relative flex-1 min-w-40">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search candidates..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            className="w-full rounded-lg border-0 bg-slate-50 py-2 pl-9 pr-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-300"
          />
        </div>

        {/* Score Filter */}
        <div className="flex items-center gap-1.5">
          <Filter className="h-3.5 w-3.5 text-slate-400" />
          <select
            value={scoreFilter}
            onChange={(e) => setScoreFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-8 text-sm text-slate-600 focus:outline-none focus:ring-2 focus:ring-violet-300"
          >
            <option>All Scores</option>
            <option>80%+</option>
            <option>60-79%</option>
            <option>Below 60%</option>
          </select>
        </div>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-8 text-sm text-slate-600 focus:outline-none focus:ring-2 focus:ring-violet-300"
        >
          <option>Sort by Date</option>
          <option>Sort by Score</option>
          <option>Sort by Name</option>
        </select>

        {/* Direction */}
        <button
          onClick={() => setSortDir(sortDir === 'desc' ? 'asc' : 'desc')}
          className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 transition-colors"
        >
          <ArrowUpDown className="h-3.5 w-3.5" />
          {sortDir === 'desc' ? 'Descending' : 'Ascending'}
        </button>
      </div>

      {/* Select All Row */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="select-all"
          checked={allSelected}
          onChange={() => allSelected ? clearSelected() : selectAll(filtered.map((c) => c.id))}
          className="h-4 w-4 rounded border-slate-300 accent-violet-600 cursor-pointer"
        />
        <label htmlFor="select-all" className="text-sm text-slate-600 cursor-pointer">
          Select All ({filtered.length} candidates)
        </label>
        {selectedIds.size > 0 && (
          <button
            onClick={() => removeCandidates(Array.from(selectedIds))}
            className="ml-auto flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-100 transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Delete Selected ({selectedIds.size})
          </button>
        )}
      </div>

      {/* Candidates Grid */}
      {loading ? (
        <div className="rounded-xl bg-white p-6 shadow-card border border-slate-100">
          <Skeleton lines={6} />
        </div>
      ) : error && candidates.length === 0 ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-600">
          {error}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-16 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-violet-50 text-violet-400">
            <Search className="h-5 w-5" />
          </div>
          <p className="text-sm font-medium text-slate-600">No candidates found</p>
          <p className="text-xs text-slate-400">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {filtered.map((candidate) => {
            const score = candidate.parsing_jobs?.[0]?.confidence_score
            const scoreDisplay = formatScore(score)
            const skills = candidate.skills ?? []
            const topSkills = skills.slice(0, 4)
            const extraCount = skills.length - 4

            return (
              <div
                key={candidate.id}
                className="relative rounded-xl bg-white p-5 shadow-card border border-slate-100 transition-all duration-200 hover:shadow-card-hover"
              >
                {/* Card Header */}
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(candidate.id)}
                    onChange={() => toggleSelected(candidate.id)}
                    className="mt-1 h-4 w-4 rounded border-slate-300 accent-violet-600 cursor-pointer flex-shrink-0"
                  />
                  <div
                    className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl text-sm font-bold text-white"
                    style={{ background: getAvatarColor(candidate.full_name) }}
                  >
                    {getInitials(candidate.full_name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-800">
                          {candidate.full_name || 'Unknown Candidate'}
                        </h3>
                        <p className="text-xs text-slate-400">
                          {new Date(candidate.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        {scoreDisplay && (
                          <span
                            className="text-lg font-bold"
                            style={{ color: getScoreColor(score) }}
                          >
                            {scoreDisplay}
                          </span>
                        )}
                        <button className="text-slate-300 hover:text-slate-500 transition-colors">
                          <MoreVertical className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Contact Info */}
                <div className="mt-3 grid grid-cols-2 gap-2 pl-[52px]">
                  <div className="flex items-center gap-1.5">
                    <Mail className="h-3 w-3 text-slate-400 flex-shrink-0" />
                    <span className="truncate text-xs text-slate-500">
                      {candidate.email || '—'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Phone className="h-3 w-3 text-slate-400 flex-shrink-0" />
                    <span className="truncate text-xs text-slate-500">
                      {candidate.phone || '—'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <MapPin className="h-3 w-3 text-slate-400 flex-shrink-0" />
                    <span className="truncate text-xs text-slate-500">
                      {candidate.location || '—'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Calendar className="h-3 w-3 text-slate-400 flex-shrink-0" />
                    <span className="text-xs text-slate-500">
                      {candidate.years_experience != null
                        ? `${candidate.years_experience} years exp.`
                        : '—'}
                    </span>
                  </div>
                </div>

                {/* Skills */}
                {topSkills.length > 0 && (
                  <div className="mt-3 pl-[52px]">
                    <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                      Top Skills
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {topSkills.map((skill) => (
                        <span
                          key={skill.id}
                          className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs text-slate-600"
                        >
                          {skill.name}
                        </span>
                      ))}
                      {extraCount > 0 && (
                        <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs text-slate-400">
                          +{extraCount} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 pl-[52px]">
                  <button
                    onClick={() => navigate(`/candidates/${candidate.id}`)}
                    className="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-violet-600 transition-colors"
                  >
                    <Eye className="h-3.5 w-3.5" />
                    View Details
                  </button>
                  <button className="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-violet-600 transition-colors">
                    <Download className="h-3.5 w-3.5" />
                    Download
                  </button>
                  <button
                    onClick={() => removeCandidates([candidate.id])}
                    className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-300 hover:bg-red-50 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
