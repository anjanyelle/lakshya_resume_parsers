import { Trash2, Download, X, FileJson, FileText, FileSpreadsheet } from 'lucide-react'
import type { Candidate } from '../../types/candidate'
import { exportCandidatesCsv } from '../../utils/csv'
import { useState } from 'react'

type BulkActionsProps = {
  selectedIds: Set<string>
  candidates: Candidate[]
  onDelete: () => void
  onClear: () => void
}

export default function BulkActions({
  selectedIds,
  candidates,
  onDelete,
  onClear
}: BulkActionsProps) {
  const [showExport, setShowExport] = useState(false)
  const selected = candidates.filter((candidate) => selectedIds.has(candidate.id))

  if (selectedIds.size === 0) return null

  return (
    <div className="fixed bottom-8 left-1/2 z-[100] -translate-x-1/2 animate-slide-up-fade">
      <div className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white/90 p-2 pl-4 shadow-2xl backdrop-blur-xl dark:border-slate-700 dark:bg-slate-900/90 shadow-orange-200/50">
        <div className="flex items-center gap-2 pr-4 border-r border-slate-100 dark:border-slate-800">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-orange-600 text-[11px] font-black text-white">
            {selectedIds.size}
          </div>
          <span className="text-sm font-bold text-slate-600 dark:text-slate-300">
            Selected
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Export Dropdown in Bulk Actions */}
          <div className="relative">
            <button
              onClick={() => setShowExport(!showExport)}
              className="flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800 transition-all uppercase tracking-widest"
            >
              <Download className="h-4 w-4" />
              Export
            </button>

            {showExport && (
              <div className="absolute bottom-full left-0 mb-2 w-48 overflow-hidden rounded-2xl border border-slate-100 bg-white p-1.5 shadow-2xl dark:border-slate-800 dark:bg-slate-900">
                <button
                  onClick={() => { exportCandidatesCsv(selected); setShowExport(false); }}
                  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800 transition-all"
                >
                  <FileSpreadsheet className="h-4 w-4 text-emerald-500" />
                  EXCEL / CSV
                </button>
                <button
                  onClick={() => setShowExport(false)}
                  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800 transition-all"
                >
                  <FileText className="h-4 w-4 text-rose-500" />
                  PDF REPORT
                </button>
              </div>
            )}
          </div>

          <button
            onClick={onDelete}
            className="flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-bold text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all uppercase tracking-widest"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>

        <button
          onClick={onClear}
          className="ml-2 flex h-10 w-10 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-50 hover:text-slate-600 dark:hover:bg-slate-800 transition-all"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
