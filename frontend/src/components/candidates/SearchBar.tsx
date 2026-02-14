import { useEffect, useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import { useDebouncedValue } from '../../hooks/useDebouncedValue'
import { useFilterStore } from '../../store/filterStore'
import type { Candidate } from '../../types/candidate'

type SearchBarProps = {
  candidates: Candidate[]
}

export default function SearchBar({ candidates }: SearchBarProps) {
  const { setSearchTerm } = useFilterStore()
  const [value, setValue] = useState('')
  const debounced = useDebouncedValue(value, 400)

  const suggestions = useMemo(() => {
    if (!debounced) return []
    const lower = debounced.toLowerCase()
    const names = candidates
      .map((candidate) => candidate.full_name)
      .filter(Boolean)
      .map((name) => name as string)
      .filter((name) => name.toLowerCase().includes(lower))
    return Array.from(new Set(names)).slice(0, 5)
  }, [candidates, debounced])

  useEffect(() => {
    setSearchTerm(debounced)
  }, [debounced, setSearchTerm])

  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Search candidates..."
        className="w-full rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-3 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
      />
      {suggestions.length > 0 && (
        <div className="absolute left-0 right-0 top-11 z-10 rounded-xl border border-slate-200 bg-white shadow-subtle">
          {suggestions.map((item) => (
            <button
              key={item}
              onClick={() => setValue(item)}
              className="block w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
            >
              {item}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
