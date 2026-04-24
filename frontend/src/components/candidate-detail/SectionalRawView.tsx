

interface SectionData {
  content?: string | null
  detected?: boolean
}

interface SectionalRawViewProps {
  sections?: Record<string, SectionData>
  rawText?: string | null
}

const FIXED_SECTIONS = [
  'summary',
  'experience',
  'education',
  'skills',
  'certifications',
  'projects',
  'other'
]

const FRIENDLY_LABELS: Record<string, string> = {
  summary: 'SUMMARY',
  experience: 'EXPERIENCE',
  education: 'EDUCATION',
  skills: 'SKILLS',
  certifications: 'CERTIFICATIONS',
  projects: 'PROJECTS',
  other: 'OTHER'
}

export default function SectionalRawView({ sections = {}, rawText }: SectionalRawViewProps) {
  // Use the strict 8-box architectural layout
  const finalKeys = FIXED_SECTIONS

  return (
    <div className="space-y-6 bg-slate-50/10 p-2">
      {/* Raw Text Box - Scrollable */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-100 bg-white px-5 py-4">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-bold tracking-wider text-slate-900 uppercase">Raw Resume Text</h3>
            <span className="text-xs font-medium text-slate-400">
              {(rawText || '').length.toLocaleString()} characters
            </span>
          </div>
          <div className={`flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-tight ${
            rawText 
              ? 'bg-indigo-50 text-indigo-600 border border-indigo-100' 
              : 'bg-rose-50 text-rose-500 border border-rose-100'
          }`}>
            <span className={`h-1.5 w-1.5 rounded-full ${rawText ? 'bg-indigo-500' : 'bg-rose-500'}`} />
            {rawText ? 'Extracted' : 'Empty'}
          </div>
        </div>
        <div className="h-80 overflow-auto bg-slate-50/30 p-5 scrollbar-thin scrollbar-thumb-slate-200">
          {rawText ? (
            <pre className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-slate-700">
              {rawText}
            </pre>
          ) : (
            <div className="flex h-full items-center justify-center italic text-slate-400 text-sm">
              No raw text extracted for this document
            </div>
          )}
        </div>
      </div>

      {/* Section Boxes */}
      <div className="grid grid-cols-1 gap-6">
        {finalKeys.map((key) => {
          const data = sections[key]
          
          // Render all 8 boxes unconditionally according to pipeline specification
          const sectionData = data || {}
          const content = sectionData.content || ''
          const charCount = content.length
          const isDetected = charCount > 0
          const label = FRIENDLY_LABELS[key] || key.toUpperCase().replace(/_/g, ' ')

          return (
            <div key={key} className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
              <div className="flex items-center justify-between border-b border-slate-100 bg-white px-5 py-4">
                <div className="flex items-center gap-3">
                  <h3 className="text-sm font-bold tracking-wider text-slate-900">{label}</h3>
                  <span className="text-xs font-medium text-slate-400">
                    {charCount.toLocaleString()} characters
                  </span>
                </div>
                <div className={`flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-tight ${
                  isDetected 
                    ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' 
                    : 'bg-rose-50 text-rose-500 border border-rose-100'
                }`}>
                  <span className={`h-1.5 w-1.5 rounded-full ${isDetected ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                  {isDetected ? 'Detected' : 'Empty'}
                </div>
              </div>
              <div className="h-64 overflow-auto bg-slate-50/30 p-5 scrollbar-thin scrollbar-thumb-slate-200">
                {isDetected ? (
                  <pre className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-slate-700">
                    {content}
                  </pre>
                ) : (
                  <div className="flex h-full items-center justify-center italic text-slate-400 text-sm">
                    No content detected for this section
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
