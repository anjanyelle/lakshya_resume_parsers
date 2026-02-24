import { useState } from 'react'
import { Edit2, Check, X } from 'lucide-react'
import type { Certification } from '../../types/candidate'

type CertificationsSectionProps = {
  items?: Certification[] | null
  rawContent?: string | null
  onUpdate?: (id: string, updated: Partial<Certification>) => void
}

const isExpired = (expiryDate?: string | null) => {
  if (!expiryDate) return false
  const date = new Date(expiryDate)
  if (isNaN(date.getTime())) return false
  return date.getTime() < Date.now()
}

const parseFallbackItems = (rawContent: string | null | undefined): Array<{ id: string; name: string }> => {
  const raw = (rawContent ?? '').trim()
  if (!raw) return []
  const lines = raw
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.replace(/^[•\-\*\u2022]+\s*/u, '').trim())
    .filter(Boolean)
    .filter((line) => line.length <= 250)
  return lines.map((name, idx) => ({ id: `fallback-${idx}`, name }))
}

export default function CertificationsSection({ items = [], rawContent, onUpdate }: CertificationsSectionProps) {
  const safeItems = items ?? []
  const fallback = safeItems.length === 0 ? parseFallbackItems(rawContent) : []

  const [editingId, setEditingId] = useState<string | null>(null)
  const [draft, setDraft] = useState<Partial<Certification>>({})

  const handleEdit = (cert: Certification) => {
    setEditingId(cert.id)
    setDraft(cert)
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
      <h2 className="text-lg font-semibold text-slate-900">Certifications</h2>
      {safeItems.length === 0 && fallback.length === 0 ? (
        <p className="mt-3 text-sm text-slate-600">No certifications.</p>
      ) : (
        <div className="mt-4 space-y-4">
          {safeItems.map((cert) => {
            const isEditing = editingId === cert.id
            return (
              <div key={cert.id} className="relative rounded-xl border border-slate-100 bg-slate-50 p-4 transition-all">
                <div className="absolute right-4 top-4 flex items-center gap-2">
                  {!isEditing ? (
                    <button
                      onClick={() => handleEdit(cert)}
                      className="rounded-lg border border-slate-200 bg-white p-1.5 text-slate-500 hover:text-slate-700 hover:shadow-sm transition-all"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={() => handleSave(cert.id)}
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

                <div className="flex items-center justify-between">
                  <div className="flex-1 pr-20">
                    {isEditing ? (
                      <div className="space-y-3">
                        <div>
                          <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Certification Name</label>
                          <input
                            type="text"
                            value={draft.name || ''}
                            onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                            placeholder="Certification Name"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Issuing Organization</label>
                          <input
                            type="text"
                            value={draft.issuing_organization || ''}
                            onChange={(e) => setDraft({ ...draft, issuing_organization: e.target.value })}
                            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                            placeholder="Issuer"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Issue Date</label>
                            <input
                              type="month"
                              value={draft.issue_date || ''}
                              onChange={(e) => setDraft({ ...draft, issue_date: e.target.value })}
                              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                            />
                          </div>
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Expiry Date</label>
                            <input
                              type="month"
                              value={draft.expiry_date || ''}
                              onChange={(e) => setDraft({ ...draft, expiry_date: e.target.value })}
                              className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 outline-none"
                            />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <>
                        <p className="text-sm font-semibold text-slate-900">{cert.name}</p>
                        <p className="text-xs text-slate-600 mt-1">
                          {cert.issuing_organization || 'Issuer'}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {cert.issue_date || '—'} → {cert.expiry_date || 'No expiry'}
                        </p>
                      </>
                    )}
                  </div>
                  {!isEditing && (
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold shrink-0 ${isExpired(cert.expiry_date)
                        ? 'bg-red-50 text-red-600'
                        : 'bg-emerald-50 text-emerald-700'
                        }`}
                    >
                      {isExpired(cert.expiry_date) ? 'Expired' : 'Active'}
                    </span>
                  )}
                </div>
              </div>
            )
          })}

          {safeItems.length === 0 &&
            fallback.map((cert) => (
              <div key={cert.id} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">{cert.name}</p>
              </div>
            ))}
        </div>
      )}
    </div>
  )
}
