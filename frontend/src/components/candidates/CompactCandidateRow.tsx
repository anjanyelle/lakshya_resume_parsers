import { Eye, Download, Trash2, Mail, FileText, CheckCircle2, Clock } from 'lucide-react'
import type { Candidate } from '../../types/candidate'
import { getInitials, Gauge, ScoreBadge, getAvatarColor, formatScore, formatRelativeTime } from './CandidateUIUtils'

interface CompactCandidateRowProps {
  candidate?: Candidate
  item?: {
    file: File
    status: string
    progress: number
    error?: string | null
  }
  onView?: (id: string) => void
  onDelete?: (id: string) => void
}

export default function CompactCandidateRow({
  candidate,
  item,
  onView,
  onDelete
}: CompactCandidateRowProps) {
  // If it's a processing item
  if (item) {
    const isError = item.status === 'error' || !!item.error
    const isProcessing = item.status === 'processing' || item.status === 'uploading'

    return (
      <div className={`flex items-center gap-4 rounded-2xl border transition-all duration-300 p-3 shadow-sm animate-in fade-in slide-in-from-bottom-2 ${isError ? 'bg-rose-50/50 border-rose-100' : 'bg-white dark:bg-slate-800/50 border-slate-100 dark:border-slate-700/50'
        }`}>
        <div className={`flex h-10 w-10 items-center justify-center rounded-xl border flex-shrink-0 transition-colors ${isError ? 'bg-rose-100 text-rose-500 border-rose-200' :
          isProcessing ? 'bg-violet-50 dark:bg-violet-500/10 text-violet-500 border-violet-100 dark:border-violet-500/20' :
            'bg-slate-50 text-slate-400 border-slate-100'
          }`}>
          {isProcessing ? (
            <div className="relative">
              <FileText className="h-5 w-5" />
              <div className="absolute inset-0 h-5 w-5 border-2 border-violet-500 border-t-transparent rounded-full animate-spin opacity-40" />
            </div>
          ) : isError ? (
            <X className="h-5 w-5" />
          ) : (
            <FileText className="h-5 w-5" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="text-[13px] font-bold text-slate-700 dark:text-slate-200 truncate pr-4">{item.file.name}</h4>
            <span className={`text-[10px] font-black uppercase tracking-widest ${isError ? 'text-rose-500' : 'text-slate-300 dark:text-slate-500'
              }`}>
              {isError ? 'Failed' : item.status}
            </span>
          </div>
          <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-900 overflow-hidden">
            <div
              className={`h-full transition-all duration-1000 ease-out ${isError ? 'bg-rose-400' : 'bg-gradient-to-r from-orange-600 via-orange-500 to-orange-400 animate-shimmer'
                }`}
              style={{ width: `${item.progress}%`, backgroundSize: '200% 100%' }}
            />
          </div>
        </div>

        <div className="flex items-center gap-3 pr-2">
          <span className={`text-xs font-black ${isError ? 'text-rose-500' : 'text-violet-600 dark:text-violet-400'}`}>
            {isError ? '!' : `${Math.round(item.progress)}%`}
          </span>
          <div className="h-4 w-px bg-slate-100 dark:bg-slate-700" />
          <button className="text-slate-300 hover:text-rose-500 transition-colors active:scale-90">
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    )
  }

  // If it's a success candidate
  if (candidate) {
    const rawScore = candidate.parsing_jobs?.[0]?.confidence_score
    const scoreValue = formatScore(rawScore)

    return (
      <div className="flex items-center gap-4 rounded-xl border border-slate-100 bg-white p-3 shadow-sm hover:border-violet-200 hover:shadow-md transition-all duration-300 group animate-in fade-in slide-in-from-top-2">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-lg text-xs font-bold text-white shadow-sm flex-shrink-0"
          style={{ background: getAvatarColor(candidate.full_name) }}
        >
          {getInitials(candidate.full_name)}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="text-[14px] font-extrabold text-slate-800 dark:text-slate-100 truncate uppercase tracking-tight">{candidate.full_name || 'Anonymous'}</h4>
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-50 text-emerald-500">
              <CheckCircle2 className="h-3.5 w-3.5" />
            </div>
          </div>
          <div className="flex items-center gap-3 mt-0.5">
            <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400">
              <Mail className="h-3 w-3" />
              <span className="truncate max-w-[150px]">{candidate.email || 'No email'}</span>
            </div>
            <span className="text-[11px] text-slate-200">|</span>
            <div className="flex items-center gap-1.5 text-slate-400">
              <Clock className="h-3 w-3" />
              <span className="text-[10px] font-bold uppercase tracking-tighter">
                {formatRelativeTime(candidate.created_at)}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6 pr-2">
          {scoreValue !== null && (
            <ScoreBadge value={scoreValue} size={34} />
          )}

          <div className="h-4 w-px bg-slate-100" />

          <div className="flex items-center gap-2">
            <button
              onClick={() => onView?.(candidate.id)}
              className="p-2 rounded-lg text-slate-400 hover:text-violet-600 hover:bg-violet-50 transition-all active:scale-90"
              title="View Details"
            >
              <Eye className="h-4 w-4" />
            </button>
            <button
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all active:scale-90"
              title="Download"
            >
              <Download className="h-4 w-4" />
            </button>
            <button
              onClick={() => onDelete?.(candidate.id)}
              className="p-2 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-all active:scale-90"
              title="Delete"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    )
  }

  return null
}
