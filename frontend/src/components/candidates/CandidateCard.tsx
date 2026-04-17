import { Eye, Download, Trash2, MoreVertical, Mail, Phone, MapPin, Calendar, ChevronDown, ChevronUp, Clock } from 'lucide-react'
import { useState } from 'react'
import type { Candidate } from '../../types/candidate'
import { getInitials, Gauge, ScoreBadge, getAvatarColor, formatScore, SkillChip, formatRelativeTime } from './CandidateUIUtils'

interface CandidateCardProps {
  candidate: Candidate
  isSelected?: boolean
  onToggleSelect?: (id: string) => void
  onDelete?: (id: string) => void
  onView?: (id: string) => void
}

export default function CandidateCard({
  candidate,
  isSelected,
  onToggleSelect,
  onDelete,
  onView
}: CandidateCardProps) {
  const rawScore = candidate.parsing_jobs?.[0]?.confidence_score
  const scoreValue = formatScore(rawScore)
  const skills = candidate.skills ?? []
  const topSkills = skills.slice(0, 5)
  const [showAllSkills, setShowAllSkills] = useState(false)

  const handleDownload = (e?: React.MouseEvent) => {
    e?.stopPropagation()
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
    <div
      onClick={() => onView?.(candidate.id)}
      className={`relative flex flex-col rounded-2xl bg-white dark:bg-slate-800/80 p-6 px-4 border transition-all duration-500 cursor-pointer hover-lift h-full ${isSelected
        ? 'border-brand-300 ring-4 ring-brand-50 dark:ring-brand-900/20 shadow-2xl shadow-brand-100 dark:shadow-none'
        : 'border-slate-100 dark:border-slate-700/50 shadow-premium shadow-slate-200/40 dark:shadow-none hover:shadow-2xl hover:shadow-brand-100/30 dark:hover:shadow-brand-900/20'
        }`}>
      {/* Header Row */}
      <div className="flex items-start gap-3 mt-1">
        {onToggleSelect && (
          <div className="pt-2" onClick={(e) => e.stopPropagation()}>
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => onToggleSelect(candidate.id)}
              className="h-3.5 w-3.5 rounded border-slate-200 dark:border-slate-600 accent-brand-500 cursor-pointer shadow-sm transition-all duration-200 active:scale-90 hover:border-brand-300"
            />
          </div>
        )}

        <div
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl text-[10px] font-bold text-white shadow-sm"
          style={{ background: getAvatarColor(candidate.full_name) }}
        >
          {getInitials(candidate.full_name)}
        </div>

        <div className="flex-1 min-w-0 pt-1">
          <h3 className="text-[13.5px] font-black text-[#1a2340] dark:text-slate-100 truncate leading-tight tracking-tight uppercase">
            {candidate.full_name || 'Anonymous'}
          </h3>
          <div className="flex items-center gap-1.5 mt-0.5 text-slate-500 dark:text-slate-400">
            <Clock className="h-3 w-3" />
            <span className="text-[10px] font-bold uppercase tracking-widest leading-none">
              {formatRelativeTime(candidate.created_at)}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-slate-600 dark:hover:text-slate-200 transition-all border border-transparent hover:border-slate-100 dark:hover:border-slate-600 shadow-none hover:shadow-sm">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content Wrapper to push footer down */}
      <div className="flex flex-1 flex-col">
        {/* Metadata Grid (2x2) */}
        <div className="mt-4 grid grid-cols-2 gap-x-3 gap-y-2.5 pl-11">
          <div className="flex items-center gap-2 min-w-0">
            <Mail className={`h-3.5 w-3.5 flex-shrink-0 ${candidate.email ? 'text-slate-500' : 'text-slate-200'}`} />
            <span className={`text-[12px] truncate ${candidate.email ? 'text-slate-800 dark:text-slate-300 font-semibold' : 'text-slate-300 dark:text-slate-600 font-normal italic'}`}>
              {candidate.email || 'Email not listed'}
            </span>
          </div>
          <div className="flex items-center gap-2 min-w-0">
            <Phone className={`h-3.5 w-3.5 flex-shrink-0 ${candidate.phone ? 'text-slate-500' : 'text-slate-200'}`} />
            <span className={`text-[12px] truncate ${candidate.phone ? 'text-slate-800 dark:text-slate-300 font-semibold' : 'text-slate-300 dark:text-slate-600 font-normal italic'}`}>
              {candidate.phone || 'Phone not listed'}
            </span>
          </div>
          <div className="flex items-center gap-2 min-w-0">
            <MapPin className={`h-3.5 w-3.5 flex-shrink-0 ${candidate.location ? 'text-slate-500' : 'text-slate-200'}`} />
            <span className={`text-[12px] truncate ${candidate.location ? 'text-slate-800 dark:text-slate-300 font-semibold' : 'text-slate-300 dark:text-slate-600 font-normal italic'}`}>
              {candidate.location || 'Location not listed'}
            </span>
          </div>
          <div className="flex items-center gap-2 min-w-0">
            <Calendar className={`h-3.5 w-3.5 flex-shrink-0 ${candidate.years_experience !== null ? 'text-slate-500' : 'text-slate-200'}`} />
            <span className={`text-[12px] truncate ${candidate.years_experience !== null ? 'text-slate-800 dark:text-slate-300 font-semibold' : 'text-slate-300 dark:text-slate-600 font-normal italic'}`}>
              {candidate.years_experience !== null ? `${candidate.years_experience} yrs exp.` : 'Exp. not listed'}
            </span>
          </div>
        </div>

        {/* Skills Section */}
        <div className="mt-2.5 pl-10">
          <div className="min-h-[28px]">
            <p className="text-[8.5px] font-black tracking-widest text-slate-500 dark:text-slate-500 uppercase mb-1">Top Skills</p>
            <div className="flex flex-wrap gap-1" onClick={(e) => e.stopPropagation()}>
              {(showAllSkills ? skills : topSkills).map((skill) => {
                const candSkill = candidate.candidate_skills?.find(cs => cs.skill?.id === skill.id || cs.skill?.name === skill.name);
                return (
                  <SkillChip
                    key={skill.id}
                    name={skill.name}
                    experience={candSkill?.years_experience}
                    source={skill.source}
                  />
                );
              })}
              {skills.length > 5 && (
                <button
                  onClick={() => setShowAllSkills(!showAllSkills)}
                  className={`flex items-center gap-1 rounded-lg border px-2 py-1 text-[11px] font-bold transition-all shadow-sm ${showAllSkills ? 'bg-brand-500 border-brand-500 text-white shadow-brand-100' : 'border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                >
                  {showAllSkills ? <><ChevronUp className="h-3 w-3" /> Hide</> : <>+{skills.length - 5} more</>}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="mt-auto border-slate-50 dark:border-slate-800 px-0.5 pt-3 flex items-center justify-between gap-4" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => onView?.(candidate.id)}
          className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-[13px] font-bold text-brand-600 dark:text-brand-400 bg-brand-50/0 hover:bg-brand-50 dark:hover:bg-brand-900/20 transition-all hover:-translate-y-0.5"
        >
          <Eye className="h-4 w-4" />
          <span>View Details</span>
        </button>

        <div className="flex items-center gap-4">
          <button
            onClick={handleDownload}
            className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-[13px] font-bold text-slate-500 dark:text-slate-400 bg-slate-50/0 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all hover:-translate-y-0.5"
          >
            <Download className="h-4 w-4" />
            <span>Download</span>
          </button>

          {onDelete && (
            <button
              onClick={() => onDelete(candidate.id)}
              className="flex h-9 w-9 items-center justify-center rounded-xl text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500 transition-all active:scale-90"
            >
              <Trash2 className="h-[17px] w-[17px]" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
