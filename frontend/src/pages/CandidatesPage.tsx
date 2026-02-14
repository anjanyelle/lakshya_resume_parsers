import { useEffect, useMemo, useState } from 'react'
import { LayoutGrid, List, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import SearchBar from '../components/candidates/SearchBar'
import FilterPanel from '../components/candidates/FilterPanel'
import CandidateCard from '../components/candidates/CandidateCard'
import CandidateList from '../components/candidates/CandidateList'
import BulkActions from '../components/candidates/BulkActions'
import Skeleton from '../components/common/Skeleton'
import Button from '../components/common/Button'
import { useCandidateStore } from '../store/candidateStore'
import { useFilterStore } from '../store/filterStore'

export default function CandidatesPage() {
  const {
    candidates,
    loading,
    error,
    page,
    pageSize,
    sortKey,
    sortDirection,
    selectedIds,
    setPage,
    setPageSize,
    setSort,
    toggleSelected,
    loadCandidates,
    removeCandidates,
    selectAll,
    clearSelected,
  } = useCandidateStore()
  const { searchTerm, skills, location, minExperience, maxExperience } =
    useFilterStore()
  const [viewMode, setViewMode] = useState<'table' | 'card'>('table')

  useEffect(() => {
    const controller = new AbortController()
    loadCandidates(controller.signal)
    const interval = window.setInterval(() => loadCandidates(), 10000)
    return () => {
      controller.abort()
      window.clearInterval(interval)
    }
  }, [loadCandidates])

  useEffect(() => {
    setPage(1)
  }, [searchTerm, skills, location, minExperience, maxExperience, setPage])

  const filtered = useMemo(() => {
    return candidates
      .filter((candidate) => {
        if (searchTerm) {
          const search = searchTerm.toLowerCase()
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
        const valueA = a[sortKey]
        const valueB = b[sortKey]
        if (valueA === valueB) return 0
        if (valueA === undefined || valueA === null) return 1
        if (valueB === undefined || valueB === null) return -1
        const direction = sortDirection === 'asc' ? 1 : -1
        return valueA > valueB ? direction : -direction
      })
  }, [
    candidates,
    searchTerm,
    location,
    minExperience,
    maxExperience,
    skills,
    sortKey,
    sortDirection,
  ])

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize))
  const paginated = filtered.slice((page - 1) * pageSize, page * pageSize)

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Candidates</h1>
        <p className="mt-2 text-sm text-slate-600">
          Review and manage parsed candidate profiles.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr,1fr]">
        <SearchBar candidates={candidates} />
        <div className="flex items-center justify-end gap-2">
          <Button
            variant={viewMode === 'table' ? 'primary' : 'secondary'}
            onClick={() => setViewMode('table')}
            icon={<List className="h-4 w-4" />}
          >
            Table
          </Button>
          <Button
            variant={viewMode === 'card' ? 'primary' : 'secondary'}
            onClick={() => setViewMode('card')}
            icon={<LayoutGrid className="h-4 w-4" />}
          >
            Cards
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[3fr,1fr]">
        <div className="space-y-4">
          <BulkActions
            selectedIds={selectedIds}
            candidates={candidates}
            onDelete={() => removeCandidates(Array.from(selectedIds))}
          />

          {loading ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-6">
              <Skeleton lines={6} />
            </div>
          ) : error && candidates.length === 0 ? (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-600">
              {error}
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-10 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-brand-600">
                <Users className="h-5 w-5" />
              </div>
              <p className="text-sm text-slate-600">
                No candidates match your filters.
              </p>
            </div>
          ) : viewMode === 'table' ? (
            <CandidateList
              candidates={paginated}
              selectedIds={selectedIds}
              onToggle={toggleSelected}
              onSort={setSort}
              sortKey={sortKey}
              sortDirection={sortDirection}
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {paginated.map((candidate) => (
                <Link key={candidate.id} to={`/candidates/${candidate.id}`}>
                  <CandidateCard candidate={candidate} />
                </Link>
              ))}
            </div>
          )}

          {filtered.length > 0 && (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="text-xs text-slate-500">
                Page {page} of {totalPages} · {filtered.length} results
              </div>
              <div className="flex items-center gap-2">
                <button
                  className="rounded-lg border border-slate-200 px-3 py-1 text-xs text-slate-600"
                  disabled={page === 1}
                  onClick={() => setPage(Math.max(1, page - 1))}
                >
                  Prev
                </button>
                <button
                  className="rounded-lg border border-slate-200 px-3 py-1 text-xs text-slate-600"
                  disabled={page === totalPages}
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                >
                  Next
                </button>
                <select
                  value={pageSize}
                  onChange={(event) => setPageSize(Number(event.target.value))}
                  className="rounded-lg border border-slate-200 px-2 py-1 text-xs text-slate-600"
                >
                  {[10, 20, 50].map((size) => (
                    <option key={size} value={size}>
                      {size} / page
                    </option>
                  ))}
                </select>
                <button
                  className="rounded-lg border border-slate-200 px-3 py-1 text-xs text-slate-600"
                  onClick={() =>
                    selectedIds.size === paginated.length
                      ? clearSelected()
                      : selectAll(paginated.map((candidate) => candidate.id))
                  }
                >
                  {selectedIds.size === paginated.length ? 'Clear' : 'Select page'}
                </button>
              </div>
            </div>
          )}
        </div>

        <FilterPanel candidates={candidates} />
      </div>
    </section>
  )
}
