import { Eye, Download, Trash2, Mail, FileText, CheckCircle2 } from 'lucide-react'
import type { Candidate } from '../../types/candidate'
import { getInitials, Gauge, ScoreBadge, getAvatarColor, formatScore } from './CandidateUIUtils'

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
    return (
      <div className="flex items-center gap-4 rounded-xl border border-slate-100 bg-white p-3 shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-violet-500 border border-violet-100 flex-shrink-0">
          <FileText className="h-5 w-5" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="text-[13px] font-bold text-slate-700 truncate">{item.file.name}</h4>
            <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">{item.status}</span>
          </div>
          <div className="mt-1.5 h-1.5 w-full max-w-xs rounded-full bg-slate-50 overflow-hidden border border-slate-100/50">
            <div 
              className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 transition-all duration-500"
              style={{ width: `${item.progress}%` }}
            />
          </div>
        </div>

        <div className="flex items-center gap-3 pr-2">
          <span className="text-xs font-bold text-violet-600">{Math.round(item.progress)}%</span>
          <div className="h-4 w-px bg-slate-100" />
          <button className="text-slate-300 hover:text-red-400 transition-colors">
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
              <h4 className="text-[14px] font-bold text-slate-800 truncate">{candidate.full_name || 'Anonymous'}</h4>
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
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-tighter">
                {new Date(candidate.created_at).toLocaleDateString()}
              </span>
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
