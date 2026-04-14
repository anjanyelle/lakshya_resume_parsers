import React from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Command, Hash, Cpu } from 'lucide-react'
import { useCandidateStore } from '../../store/candidateStore'

interface GlobalSearchProps {
  isOpen: boolean
  onClose: () => void
  query: string
}

export default function GlobalSearch({ isOpen, onClose, query }: GlobalSearchProps) {
  const navigate = useNavigate()
  const { candidates } = useCandidateStore()

  if (!isOpen) return null

  const q = query.toLowerCase()
  const results = !q.trim() ? [] : candidates.filter((c) =>
    c.full_name?.toLowerCase().includes(q) ||
    c.email?.toLowerCase().includes(q) ||
    (c.skills ?? []).some(s => s.name.toLowerCase().includes(q))
  ).slice(0, 6)

  const handleNavigate = (id: string) => {
    navigate(`/candidates/${id}`)
    onClose()
  }

  return (
    <div className="absolute left-0 top-full mt-3 w-[450px] overflow-hidden rounded-2xl bg-white/95 backdrop-blur-xl shadow-2xl ring-1 ring-slate-100 z-50 animate-in fade-in zoom-in-95 slide-in-from-top-2 duration-300">
      <div className="max-h-[380px] overflow-y-auto scrollbar-thin">
        {!query.trim() ? (
          <div className="py-12 px-4 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-50 text-violet-500 mx-auto mb-3 shadow-inner">
              <Command className="h-6 w-6" />
            </div>
            <p className="text-sm font-black text-slate-800 uppercase tracking-tight">Intelligence Search</p>
            <p className="text-xs text-slate-400 mt-1 max-w-[240px] mx-auto uppercase tracking-tighter italic-placeholder">— START TYPING TO EXPLORE ASSETS —</p>
          </div>
        ) : results.length === 0 ? (
          <div className="py-12 px-4 text-center">
            <p className="text-sm font-black text-slate-400 uppercase tracking-widest leading-none italic-placeholder">— NO MATCHES DETECTED —</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-50 p-1.5">
            {results.map((result) => (
              <button
                key={result.id}
                onClick={() => handleNavigate(result.id)}
                className="flex w-full items-center gap-4 rounded-xl px-3 py-3 text-left transition-all duration-300 hover:bg-violet-50/50 group"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-50 text-slate-400 group-hover:bg-white group-hover:shadow-md transition-all duration-300">
                  <User className="h-5.5 w-5.5 group-hover:text-violet-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-black text-slate-800 truncate leading-none uppercase tracking-tight mb-1 group-hover:text-violet-900 transition-colors">
                    {result.full_name}
                  </p>
                  <p className="text-[11px] font-bold text-slate-400 truncate tracking-tight uppercase opacity-70 italic-placeholder">
                    {result.email}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-teal-50 text-teal-600 text-[9px] font-black tracking-widest uppercase">
                      <Cpu className="h-2.5 w-2.5" />
                      Match {Math.round((result.parsing_jobs?.[0]?.confidence_score || 0) * 100)}%
                    </div>
                  </div>
                </div>
                <div className="opacity-0 group-hover:opacity-100 transition-all transform group-hover:translate-x-1">
                  <Hash className="h-4 w-4 text-violet-300" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between px-4 py-3 bg-slate-50/50 border-t border-slate-100 text-[10px] text-slate-400 font-black uppercase tracking-widest">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 italic-placeholder"><Command className="h-3 w-3" /> SELECT</span>
          <span className="flex items-center gap-1.5 italic-placeholder"><Hash className="h-3 w-3" /> NAVIGATE</span>
        </div>
        <div className="animate-pulse">
          RESUME AI
        </div>
      </div>
    </div>
  )
}
