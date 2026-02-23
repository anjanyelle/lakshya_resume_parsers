import type { Certification } from '../../types'

type CertificationsSectionProps = {
  items?: Certification[] | null
  rawContent?: string | null
}

const isExpired = (expiryDate?: string | null) => {
  if (!expiryDate) return false
  return new Date(expiryDate).getTime() < Date.now()
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

export default function CertificationsSection({ items = [], rawContent }: CertificationsSectionProps) {
  const safeItems = items ?? []
  const fallback = safeItems.length === 0 ? parseFallbackItems(rawContent) : []

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Certifications</h2>
      {safeItems.length === 0 && fallback.length === 0 ? (
        <p className="mt-3 text-sm text-slate-600">No certifications.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {safeItems.map((cert) => (
            <div key={cert.id} className="flex items-center justify-between rounded-xl bg-slate-50 p-4">
              <div>
                <p className="text-sm font-semibold text-slate-900">{cert.name}</p>
                <p className="text-xs text-slate-500">
                  {cert.issuing_organization || 'Issuer'}
                </p>
                <p className="text-xs text-slate-500">
                  {cert.issue_date || '—'} → {cert.expiry_date || 'No expiry'}
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  isExpired(cert.expiry_date)
                    ? 'bg-red-50 text-red-600'
                    : 'bg-emerald-50 text-emerald-700'
                }`}
              >
                {isExpired(cert.expiry_date) ? 'Expired' : 'Active'}
              </span>
            </div>
          ))}

          {safeItems.length === 0 &&
            fallback.map((cert) => (
              <div key={cert.id} className="rounded-xl bg-slate-50 p-4">
                <p className="text-sm font-semibold text-slate-900">{cert.name}</p>
              </div>
            ))}
        </div>
      )}
    </div>
  )
}