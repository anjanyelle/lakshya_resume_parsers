import { useState } from 'react'
import { Edit2, Check, X } from 'lucide-react'

type SummarySectionProps = {
  summary?: string | null
  onSave: (value: string) => void
  readOnly?: boolean
}

export default function SummarySection({ summary, onSave, readOnly = false }: SummarySectionProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(summary ?? '')

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Summary</h2>
        {!readOnly && !editing ? (
          <button
            onClick={() => setEditing(true)}
            className="rounded-lg border border-slate-200 p-1 text-slate-500 hover:text-slate-700"
          >
            <Edit2 className="h-4 w-4" />
          </button>
        ) : !readOnly ? (
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                onSave(draft)
                setEditing(false)
              }}
              className="rounded-lg border border-emerald-200 p-1 text-emerald-600 hover:text-emerald-700"
            >
              <Check className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                setDraft(summary ?? '')
                setEditing(false)
              }}
              className="rounded-lg border border-slate-200 p-1 text-slate-500 hover:text-slate-700"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ) : null}
      </div>
      {editing ? (
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          className="mt-3 min-h-[120px] w-full rounded-lg border border-slate-200 p-3 text-sm"
        />
      ) : (
        <p className="mt-3 text-sm text-slate-600">
          {summary || 'No summary provided yet.'}
        </p>
      )}
    </div>
  )
}
