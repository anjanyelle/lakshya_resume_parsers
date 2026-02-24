import { useState } from 'react'
import { Edit2, Check, X } from 'lucide-react'
import type { Education } from '../../types/candidate'

type EducationSectionProps = {
  items?: Education[]
  onUpdate?: (id: string, updated: Partial<Education>) => void
}

export default function EducationSection({ items = [], onUpdate }: EducationSectionProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [draft, setDraft] = useState<Partial<Education>>({})

  const handleEdit = (item: Education) => {
    setEditingId(item.id)
    setDraft(item)
  }

  const handleCancel = () => {
    setEditingId(null)
    setDraft({})
  }

  const handleSave = (id: string) => {
    if (onUpdate) {
      onUpdate(id, draft)
    }
    setEditingId(null)
    setDraft({})
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Education</h2>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-600">No education records.</p>
      ) : (
        <div className="mt-4 space-y-4">
          {items.map((item) => {
            const isEditing = editingId === item.id
            return (
              <div key={item.id} className="relative rounded-xl border border-slate-100 bg-slate-50 p-4 transition-all">
                <div className="absolute right-4 top-4 flex items-center gap-2">
                  {!isEditing ? (
                    <button
                      onClick={() => handleEdit(item)}
                      className="rounded-lg border border-slate-200 bg-white p-1.5 text-slate-500 hover:text-slate-700 hover:shadow-sm transition-all"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={() => handleSave(item.id)}
                        className="rounded-lg border border-emerald-200 bg-white p-1.5 text-emerald-600 hover:text-emerald-700 hover:shadow-sm transition-all"
                      >
                        <Check className="h-4 w-4" />
                      </button>
                      <button
                        onClick={handleCancel}
                        className="rounded-lg border border-slate-200 bg-white p-1.5 text-slate-500 hover:text-slate-700 hover:shadow-sm transition-all"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </>
                  )}
                </div>

                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center flex-shrink-0 text-xl">
                    🎓
                  </div>
                  <div className="flex-1 pr-20">
                    {isEditing ? (
                      <div className="space-y-3">
                        <div>
                          <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Institution</label>
                          <input
                            type="text"
                            value={draft.institution || ''}
                            onChange={(e) => setDraft({ ...draft, institution: e.target.value })}
                            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                            placeholder="Institution"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Degree</label>
                            <input
                              type="text"
                              value={draft.degree || ''}
                              onChange={(e) => setDraft({ ...draft, degree: e.target.value })}
                              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                              placeholder="Degree"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Field of Study</label>
                            <input
                              type="text"
                              value={draft.field_of_study || ''}
                              onChange={(e) => setDraft({ ...draft, field_of_study: e.target.value })}
                              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                              placeholder="Field of Study"
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Start Date</label>
                            <input
                              type="month"
                              value={draft.start_date || ''}
                              onChange={(e) => setDraft({ ...draft, start_date: e.target.value })}
                              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">End Date</label>
                            <input
                              type="month"
                              value={draft.end_date || ''}
                              onChange={(e) => setDraft({ ...draft, end_date: e.target.value })}
                              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                            />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <>
                        <p className="text-sm font-semibold text-slate-900">
                          {item.institution || 'Institution'}
                        </p>
                        <p className="text-xs text-slate-600 mt-1">
                          {item.degree || 'Degree'} {item.field_of_study ? `· ${item.field_of_study}` : ''}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {item.start_date || '—'} → {item.end_date || '—'}
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
