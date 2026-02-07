import type { WorkHistory } from '../../types'

type WorkHistoryTimelineProps = {
  items?: WorkHistory[]
}

export default function WorkHistoryTimeline({ items = [] }: WorkHistoryTimelineProps) {
  if (!items.length) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-slate-900">Work history</h2>
        <p className="mt-3 text-sm text-slate-600">No work history available.</p>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Work history</h2>
      <div className="mt-4 space-y-4">
        {items.map((item, idx) => (
          <div key={item.id} className="relative pl-6">
            <span className="absolute left-0 top-1.5 h-3 w-3 rounded-full bg-brand-500" />
            {idx !== items.length - 1 && (
              <span className="absolute left-[5px] top-5 h-full w-px bg-slate-200" />
            )}
            <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-900">
                {item.job_title || 'Role'} · {item.company_name || 'Company'}
              </p>
              <p className="text-xs text-slate-500">
                {item.start_date || '—'} → {item.end_date || 'Present'}
              </p>
              {item.description && (
                <p className="mt-2 text-xs text-slate-600">{item.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
