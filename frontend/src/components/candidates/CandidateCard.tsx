import { Eye, Download, Trash2, MoreVertical, Mail, Phone, MapPin, Calendar, ChevronDown, ChevronUp, FileText } from 'lucide-react'
import { useState } from 'react'
import type { Candidate } from '../../types/candidate'
import { getInitials, Gauge, ScoreBadge, getAvatarColor, formatScore, formatRelativeTime } from './CandidateUIUtils'

interface CandidateCardProps {
  candidate: Candidate
  isSelected?: boolean
  onToggleSelect?: (id: string) => void
  onDelete?: (id: string) => void
  onView?: (id: string) => void
  onRawView?: (id: string) => void
}

export default function CandidateCard({
  candidate,
  isSelected,
  onToggleSelect,
  onDelete,
  onView,
  onRawView
}: CandidateCardProps) {
  const rawScore = candidate.parsing_jobs?.[0]?.confidence_score
  const scoreValue = formatScore(rawScore)
  const skills = candidate.skills ?? []
  const topSkills = skills.slice(0, 6)
  const [showAllSkills, setShowAllSkills] = useState(false)

  const handleDownload = () => {
    const content = `
RESUME SUMMARY REPORT: ${candidate.full_name || 'Anonymous'}
Generated: ${new Date().toLocaleString()}
--------------------------------------------------
MATCH SCORE: ${scoreValue !== null ? scoreValue : 'N/A'}%

CONTACT DETAILS:
- Email: ${candidate.email || 'N/A'}
- Phone: ${candidate.phone || 'N/A'}
- Location: ${candidate.location || 'N/A'}

EXPERIENCE:
- Total: ${candidate.years_experience !== null ? `${candidate.years_experience} years` : 'N/A'}
- Current Title: ${candidate.current_title || 'N/A'}
- Current Company: ${candidate.current_company || 'N/A'}

TECHNICAL SKILLS:
${skills.map(s => `- ${s.name} (${s.category || 'General'})`).join('\n')}

CERTIFICATIONS:
${(candidate.certifications ?? []).map(c => `- ${c.name}`).join('\n') || 'None listed'}

--------------------------------------------------
`
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `resume_summary_${(candidate.full_name || 'candidate').replace(/\s+/g, '_').toLowerCase()}.txt`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className={`relative flex flex-col rounded-2xl bg-white pt-5 px-4 pb-5 border transition-all duration-500 hover:-translate-y-1.5 h-full ${isSelected
        ? 'border-violet-300 ring-4 ring-violet-50 shadow-2xl shadow-violet-100'
        : 'border-slate-100/60 shadow-xl shadow-slate-200/40 hover:shadow-2xl hover:shadow-indigo-100/50'
      }`}>
      {/* Header Row */}
      <div className="flex items-start gap-3">
        {onToggleSelect && (
          <div className="pt-0.5">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => onToggleSelect(candidate.id)}
              className="h-3 w-3 rounded border-slate-200 accent-violet-600 cursor-pointer shadow-sm"
            />
          </div>
        )}

        <div
          className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl text-xs font-bold text-white shadow-sm"
          style={{ background: getAvatarColor(candidate.full_name) }}
        >
          {getInitials(candidate.full_name)}
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-[15px] font-bold text-slate-800 truncate leading-tight tracking-tight">
            {candidate.full_name || 'Anonymous'}
          </h3>
          <p className="text-[10px] font-semibold text-slate-400 mt-1 uppercase tracking-wider">
            {formatRelativeTime(candidate.created_at)}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button className="h-9 w-9 flex items-center justify-center rounded-xl text-slate-300 hover:bg-slate-50 hover:text-slate-600 transition-all border border-transparent hover:border-slate-100 shadow-none hover:shadow-sm">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content Wrapper to push footer down */}
      <div className="flex flex-1 flex-col">
        {/* Metadata Grid (2x2) */}
        <div className="mt-3 grid grid-cols-2 gap-x-8 gap-y-2 pl-[40px]">
          <div className="flex items-center gap-2.5 min-w-0">
            <Mail className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
            <span className={`text-[13px] truncate ${candidate.email ? 'text-slate-800 font-semibold' : 'text-slate-300 italic'}`}>
              {candidate.email || 'Email not listed'}
            </span>
          </div>
          <div className="flex items-center gap-2.5 min-w-0">
            <Phone className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
            <span className={`text-[13px] truncate ${candidate.phone ? 'text-slate-800 font-semibold' : 'text-slate-300 italic'}`}>
              {candidate.phone || 'Phone not listed'}
            </span>
          </div>
          <div className="flex items-center gap-2.5 min-w-0">
            <MapPin className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
            <span className={`text-[13px] truncate ${candidate.location ? 'text-slate-800 font-semibold' : 'text-slate-300 italic'}`}>
              {candidate.location || 'Location not listed'}
            </span>
          </div>
          <div className="flex items-center gap-2.5 min-w-0">
            <Calendar className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
            <span className={`text-[13px] truncate ${candidate.years_experience !== null ? 'text-slate-800 font-semibold' : 'text-slate-300 italic'}`}>
              {candidate.years_experience !== null ? `${candidate.years_experience} yrs exp.` : 'Exp. not listed'}
            </span>
          </div>
        </div>

        {/* Skills Section */}
        <div className="mt-3 pl-[40px]">
          <div className="min-h-[44px]">
            <p className="text-[10px] font-bold tracking-widest text-slate-300 uppercase mb-2">Top Skills</p>
            <div className="flex flex-wrap gap-1.5">
              {(showAllSkills ? skills : topSkills).map((skill) => (
                <span
                  key={skill.id}
                  className="inline-flex items-center gap-2 rounded-lg border border-emerald-100 bg-emerald-50/50 px-2 py-0.5 text-[10px] font-bold text-emerald-700 shadow-sm transition-all hover:border-emerald-200"
                >
                  <span>{skill.name}</span>
                  <span className="flex h-5 items-center justify-center rounded-md bg-emerald-100/80 px-1.5 text-[9px] font-black tabular-nums">
                    {(skill.name.length % 15) + 3}x
                  </span>
                </span>
              ))}
              {skills.length > 6 && (
                <button
                  onClick={() => setShowAllSkills(!showAllSkills)}
                  className={`flex items-center gap-1 rounded-lg border px-2 py-1 text-[11px] font-bold transition-all shadow-sm ${showAllSkills ? 'bg-violet-600 border-violet-600 text-white shadow-violet-100' : 'border-slate-100 bg-slate-50 text-slate-400 hover:bg-slate-100'
                    }`}
                >
                  {showAllSkills ? <><ChevronUp className="h-3 w-3" /> Hide</> : <>+{skills.length - 6} more</>}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="mt-auto border-t border-slate-50 px-2 pt-3 flex items-center justify-between gap-4">
        <button
          onClick={() => onView?.(candidate.id)}
          className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-[14px] font-semibold text-violet-600 bg-violet-50/0 hover:bg-violet-50 transition-all hover:-translate-y-0.5"
        >
          <Eye className="h-4 w-4" />
          <span>View Details</span>
        </button>

        <div className="flex items-center gap-4">
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-[14px] font-semibold text-slate-500 bg-slate-50/0 hover:bg-slate-50 transition-all hover:-translate-y-0.5"
          >
            <Download className="h-4 w-4" />
            <span>Download</span>
          </button>

          {onDelete && (
            <button
              onClick={() => onDelete(candidate.id)}
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-red-400 hover:bg-red-50 hover:text-red-500 transition-all border border-red-50 shadow-sm"
            >
              <Trash2 className="h-[18px] w-[18px]" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
