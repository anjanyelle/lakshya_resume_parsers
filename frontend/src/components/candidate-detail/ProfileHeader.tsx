import { Mail, MapPin, Phone, Download, RefreshCcw, Trash2, CheckCircle, FileJson } from 'lucide-react'
import Button from '../common/Button'
import type { Candidate } from '../../types/candidate'

type ProfileHeaderProps = {
  candidate: Candidate
  onDownload: () => void
  onExportJson: () => void
  onReprocess: () => void
  onApprove: () => void
  onDelete: () => void
}

export default function ProfileHeader({
  candidate,
  onDownload,
  onExportJson,
  onReprocess,
  onApprove,
  onDelete,
}: ProfileHeaderProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-subtle">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 text-lg font-semibold text-brand-700">
            {candidate.full_name?.charAt(0).toUpperCase() ?? 'C'}
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">
              {candidate.full_name || 'Unnamed candidate'}
            </h1>
            <p className="text-sm text-slate-600">
              {candidate.current_title || 'Role'} · {candidate.current_company || 'Company'}
            </p>
            <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">
              {candidate.email && (
                <span className="inline-flex items-center gap-1">
                  <Mail className="h-3 w-3" /> {candidate.email}
                </span>
              )}
              {candidate.phone && (
                <span className="inline-flex items-center gap-1">
                  <Phone className="h-3 w-3" /> {candidate.phone}
                </span>
              )}
              {candidate.location && (
                <span className="inline-flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> {candidate.location}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={onDownload} icon={<Download className="h-4 w-4" />}>
            Download
          </Button>
          <Button variant="secondary" onClick={onExportJson} icon={<FileJson className="h-4 w-4" />}>
            Export JSON
          </Button>
          <Button variant="secondary" onClick={onReprocess} icon={<RefreshCcw className="h-4 w-4" />}>
            Reprocess
          </Button>
          <Button onClick={onApprove} icon={<CheckCircle className="h-4 w-4" />}>
            Mark reviewed
          </Button>
          <Button variant="danger" onClick={onDelete} icon={<Trash2 className="h-4 w-4" />}>
            Delete
          </Button>
        </div>
      </div>
    </div>
  )
}
