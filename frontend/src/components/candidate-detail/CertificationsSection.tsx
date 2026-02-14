import type { Certification } from '../../types'

type CertificationsSectionProps = {
  items?: Certification[]
}

const isExpired = (expiryDate?: string | null) => {
  if (!expiryDate) return false
  return new Date(expiryDate).getTime() < Date.now()
}

export default function CertificationsSection({ items = [] }: CertificationsSectionProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Certifications</h2>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-600">No certifications.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {items.map((cert) => (
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
        </div>
      )}
    </div>
  )
}
