import { useEffect, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import {
  Upload,
  FileText,
  X,
  Eye,
  Download,
  Search,
} from 'lucide-react'
import { useUploadStore } from '../store/uploadStore'
import { useCandidateStore } from '../store/candidateStore'

function getScoreColor(score: number) {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

function getScoreLabel(score: number) {
  if (score >= 80) return 'Good'
  if (score >= 60) return 'Fair'
  return 'Poor'
}

function getInitials(name?: string | null) {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function getAvatarColor(name?: string | null) {
  const colors = [
    'linear-gradient(135deg,#7c3aed,#a78bfa)',
    'linear-gradient(135deg,#14b8a6,#2dd4bf)',
    'linear-gradient(135deg,#f97316,#fb923c)',
    'linear-gradient(135deg,#ec4899,#f472b6)',
  ]
  const idx = (name?.charCodeAt(0) ?? 0) % colors.length
  return colors[idx]
}

export default function ResumeAnalyzerPage() {
  const navigate = useNavigate()
  const { queue, addFiles, uploadAll, pollStatuses, setActivePreviewId } = useUploadStore()
  const { candidates, loadCandidates } = useCandidateStore()

  const files = useMemo(() => queue.map((item) => item.file), [queue])

  useEffect(() => {
    const controller = new AbortController()
    loadCandidates(controller.signal)
    return () => controller.abort()
  }, [loadCandidates])

  useEffect(() => {
    const interval = window.setInterval(() => {
      pollStatuses()
    }, 3000)
    return () => window.clearInterval(interval)
  }, [pollStatuses])

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      const dropped = Array.from(e.dataTransfer.files)
      handleFilesSelected(dropped)
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  )

  const handleFilesSelected = (selected: File[]) => {
    const allowed = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'application/rtf',
    ]
    const maxBytes = 10 * 1024 * 1024
    const valid = selected.filter(
      (file) => allowed.includes(file.type) && file.size <= maxBytes,
    )
    if (valid.length !== selected.length) {
      toast.error('Some files were rejected due to type or size')
    }
    if (valid.length) {
      const newItems = addFiles(valid)
      if (newItems.length > 0) {
        setActivePreviewId(newItems[0].id)
        uploadAll()
      }
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFilesSelected(Array.from(e.target.files))
    }
  }

  const analysisResults = candidates.filter(
    (c) => c.status === 'success' || c.status === 'failed',
  )

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Upload Drop Zone */}
      <div
        className="relative rounded-2xl border-2 border-dashed border-violet-200 transition-all duration-200 hover:border-violet-400 cursor-pointer"
        style={{
          background:
            'linear-gradient(135deg, rgba(245,243,255,0.7) 0%, rgba(204,251,241,0.5) 100%)',
          minHeight: 200,
        }}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.rtf"
          className="hidden"
          onChange={handleInputChange}
        />
        <div className="flex flex-col items-center justify-center py-16 text-center px-6">
          <div
            className="flex h-14 w-14 items-center justify-center rounded-2xl text-white shadow-lg mb-4"
            style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
          >
            <Upload className="h-6 w-6" />
          </div>
          <h3 className="text-base font-semibold text-slate-700">Upload Resume Files</h3>
          <p className="mt-1 text-sm text-slate-500">
            Drag &amp; drop your resume files here, or click to browse
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Supports PDF, DOC, and DOCX files • Max 10MB per file
          </p>
          <button
            className="mt-5 rounded-xl px-6 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:opacity-90 hover:shadow-lg"
            style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
            onClick={(e) => {
              e.stopPropagation()
              document.getElementById('file-input')?.click()
            }}
          >
            Choose Files
          </button>
        </div>
      </div>

      {/* Uploaded Files Queue */}
      {queue.length > 0 && (
        <div className="rounded-xl bg-white p-5 shadow-card border border-slate-100">
          <h3 className="mb-4 text-sm font-semibold text-slate-700">Uploaded Files</h3>
          <div className="space-y-3">
            {queue.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-3 rounded-xl border border-slate-100 p-3 hover:bg-slate-50 transition-colors"
              >
                <div
                  className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl text-white"
                  style={{ background: 'linear-gradient(135deg,#7c3aed,#a78bfa)' }}
                >
                  <FileText className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="truncate text-sm font-medium text-slate-700">
                    {item.file.name}
                  </p>
                  <p className="text-xs text-slate-400">
                    {(item.file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                  {(item.status === 'uploading' || item.status === 'processing') && (
                    <div className="mt-1.5 h-1 w-full rounded-full bg-slate-100">
                      <div
                        className="h-1 rounded-full transition-all duration-500"
                        style={{
                          width: `${item.progress}%`,
                          background: 'linear-gradient(90deg,#7c3aed,#14b8a6)',
                        }}
                      />
                    </div>
                  )}
                </div>
                <span
                  className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                    item.status === 'success'
                      ? 'bg-emerald-50 text-emerald-600'
                      : item.status === 'failed'
                        ? 'bg-red-50 text-red-500'
                        : item.status === 'uploading' || item.status === 'processing'
                          ? 'bg-violet-50 text-violet-600'
                          : 'bg-amber-50 text-amber-600'
                  }`}
                >
                  {item.status === 'queued' ? 'Pending' : item.status}
                </span>
                <button className="text-slate-300 hover:text-red-400 transition-colors">
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysisResults.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-base font-semibold text-slate-700">Analysis Results</h3>
          {analysisResults.map((candidate) => {
            const job = candidate.parsing_jobs?.[0]
            const score = job?.confidence_score != null ? Math.round(job.confidence_score * 100) : null
            return (
              <div
                key={candidate.id}
                className="rounded-xl bg-white p-5 shadow-card border border-slate-100"
              >
                {/* Result Header */}
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-xl text-white text-sm font-bold flex-shrink-0"
                      style={{ background: getAvatarColor(candidate.full_name) }}
                    >
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-700">
                        {job?.filename ?? 'Resume File'}
                      </p>
                      <p className="text-xs text-slate-400">
                        Analyzed on {new Date(candidate.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    {score != null && (
                      <div className="text-right">
                        <span
                          className="text-2xl font-bold"
                          style={{ color: getScoreColor(score) }}
                        >
                          {score}%
                        </span>
                        <p className="text-xs font-medium" style={{ color: getScoreColor(score) }}>
                          {getScoreLabel(score)}
                        </p>
                      </div>
                    )}
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => navigate(`/candidates/${candidate.id}`)}
                        className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:bg-slate-50 hover:text-slate-600 transition-colors"
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </button>
                      <button className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:bg-slate-50 hover:text-slate-600 transition-colors">
                        <Download className="h-3.5 w-3.5" />
                      </button>
                      <button className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:bg-red-50 hover:text-red-500 transition-colors">
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Candidate Info Grid */}
                <div className="mt-4 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 lg:grid-cols-4">
                  <div>
                    <p className="text-xs text-slate-400">Name</p>
                    <p className="mt-0.5 text-sm font-medium text-slate-700">
                      {candidate.full_name || '—'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Email</p>
                    <p className="mt-0.5 text-sm font-medium text-slate-700 truncate">
                      {candidate.email || '—'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Phone</p>
                    <p className="mt-0.5 text-sm font-medium text-slate-700">
                      {candidate.phone || '—'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Location</p>
                    <p className="mt-0.5 text-sm font-medium text-slate-700">
                      {candidate.location || '—'}
                    </p>
                  </div>
                </div>

                {/* Skills */}
                {(candidate.skills?.length ?? 0) > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-slate-400 mb-1.5">Top Skills</p>
                    <div className="flex flex-wrap gap-1.5">
                      {candidate.skills!.slice(0, 6).map((skill) => (
                        <span
                          key={skill.id}
                          className="rounded-full border border-violet-200 bg-violet-50 px-2.5 py-0.5 text-xs font-medium text-violet-700"
                        >
                          {skill.name}
                        </span>
                      ))}
                      {(candidate.skills!.length ?? 0) > 6 && (
                        <span className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-500">
                          +{candidate.skills!.length - 6} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Empty state */}
      {analysisResults.length === 0 && queue.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div
            className="flex h-16 w-16 items-center justify-center rounded-2xl text-white shadow-lg mb-4"
            style={{ background: 'linear-gradient(135deg,rgba(124,58,237,0.15),rgba(20,184,166,0.15))' }}
          >
            <Search className="h-8 w-8 text-violet-400" />
          </div>
          <h3 className="text-base font-semibold text-slate-600">No Resumes Uploaded</h3>
          <p className="mt-1 text-sm text-slate-400">
            Upload your first resume to get started with AI powered analysis.
          </p>
        </div>
      )}
    </div>
  )
}
