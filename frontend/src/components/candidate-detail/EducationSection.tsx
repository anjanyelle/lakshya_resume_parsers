import type { Education } from '../../types'

type EducationSectionProps = {
  items?: Education[]
}

export default function EducationSection({ items = [] }: EducationSectionProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Education</h2>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-600">No education records.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {items.map((item) => (
            <div key={item.id} className="flex items-start gap-3 rounded-xl bg-slate-50 p-4">
              <div className="h-10 w-10 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center">
                🎓
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">
                  {item.institution || 'Institution'}
                </p>
                <p className="text-xs text-slate-500">
                  {item.degree || 'Degree'} {item.field_of_study ? `· ${item.field_of_study}` : ''}
                </p>
                <p className="text-xs text-slate-500">
                  {item.start_date || '—'} → {item.end_date || '—'}
                </p>
                {item.gpa != null && (
                  <p className="text-xs text-slate-500">
                    GPA: <span className="font-medium text-slate-700">{item.gpa}</span>
                  </p>
                )}
                {item.description && (
                  <p className="text-xs italic text-slate-500 mt-0.5">
                    {item.description}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
