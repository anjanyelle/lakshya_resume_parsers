import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import {
  Upload,
  FileText,
  X,
  Eye,
  Download,
  Search,
  ChevronDown,
  CheckCircle2,
  Settings,
  ShieldCheck,
} from 'lucide-react'
import { useUploadStore } from '../store/uploadStore'
import { useCandidateStore } from '../store/candidateStore'
import CandidateCard from '../components/candidates/CandidateCard'
import CompactCandidateRow from '../components/candidates/CompactCandidateRow'


export default function ResumeAnalyzerPage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'single' | 'bulk'>('single')
  const [showModelDetails, setShowModelDetails] = useState(false)
  const { queue, addFiles, uploadAll, pollStatuses, setActivePreviewId } = useUploadStore()
  const { candidates, loadCandidates } = useCandidateStore()

  const files = useMemo(() => queue.map((item) => item.file), [queue])

  useEffect(() => {
    const controller = new AbortController()
    loadCandidates(controller.signal)
    return () => controller.abort()
  }, [loadCandidates])

  useEffect(() => {
    // We use a ref-like approach by accessing the live store state inside the interval 
    // to avoid stale closures and infinite loop triggers.
    const interval = window.setInterval(async () => {
      const currentQueue = useUploadStore.getState().queue
      const prevSuccessCount = currentQueue.filter(q => q.status === 'success').length

      await pollStatuses()

      const updatedQueue = useUploadStore.getState().queue
      const newSuccessCount = updatedQueue.filter(q => q.status === 'success').length

      // Only trigger a candidate refresh if we actually transitioned a new item to 'success'
      if (newSuccessCount > prevSuccessCount) {
        if (import.meta.env.DEV) console.log('[UI-SYNC] New processing success detected, refreshing candidates...')
        loadCandidates()
      }
    }, 5000) // 5s is plenty for background polling
    return () => window.clearInterval(interval)
  }, [pollStatuses, loadCandidates])

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

  const activeQueue = queue.filter(item => item.status === 'processing' || item.status === 'uploading')
  const averageProgress = activeQueue.length > 0
    ? activeQueue.reduce((acc, item) => acc + item.progress, 0) / activeQueue.length
    : 0

  // Combine processing items and success candidates for a unified list
  const successItems = queue.filter(item => item.status === 'success')
  const processedCandidates = candidates.filter(c =>
    successItems.some(item => c.parsing_jobs?.some(job => job.id === item.jobId))
  )

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-fade-in">
      {/* 2-Column Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

        {/* LEFT COLUMN: Upload & Results (Span 8) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Header */}
          <div className="mb-2">
            <h1 
              className="text-3xl font-semibold tracking-tight drop-shadow-sm"
              style={{ background: 'linear-gradient(135deg, #7c3aed 0%, #14b8a6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
            >
              Upload & Analyze Resumes
            </h1>
            <p className="mt-1.5 text-[13px] font-semibold text-slate-400 uppercase tracking-widest leading-none">
              Transforming raw talent data into actionable AI intelligence
            </p>
          </div>

          {/* Upload Drop Zone */}
          <div
            className="relative rounded-3xl border-2 border-dashed border-violet-200 transition-all duration-300 hover:border-violet-400 group cursor-pointer overflow-hidden shadow-sm"
            style={{
              background: 'linear-gradient(135deg, rgba(245,243,255,0.7) 0%, rgba(204,251,241,0.5) 100%)',
              minHeight: 320,
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
            <div className="flex flex-col items-center justify-center py-20 text-center px-6 h-full">
              {activeQueue.length > 0 ? (
                <div className="w-full max-w-md space-y-8 animate-in fade-in zoom-in-95 duration-500">
                  <div className="flex flex-col items-center gap-4">
                    <div className="relative h-20 w-20 flex items-center justify-center">
                      <div className="absolute inset-0 rounded-[2.5rem] bg-violet-600 animate-ping opacity-20" />
                      <div className="relative flex h-20 w-20 items-center justify-center rounded-[2.5rem] bg-white text-violet-600 shadow-xl border border-violet-50">
                        <Upload className="h-9 w-9 animate-bounce" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-800 tracking-tight">AI Scanning in Progress...</h3>
                      <p className="text-sm font-bold text-slate-400 mt-1 uppercase tracking-widest">Processing {activeQueue.length} {activeQueue.length === 1 ? 'Resume' : 'Resumes'}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between px-1">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Overall Progress</span>
                      <span className="text-sm font-bold text-violet-600">{Math.round(averageProgress)}%</span>
                    </div>
                    <div className="h-4 w-full rounded-full bg-white shadow-inner p-1 border border-violet-100 overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700 ease-out shadow-lg"
                        style={{
                          width: `${Math.max(averageProgress, 5)}%`,
                          background: 'linear-gradient(90deg, #7c3aed, #14b8a6)'
                        }}
                      />
                    </div>
                    <div className="flex justify-center gap-2 pt-2">
                      <span className="px-3 py-1 rounded-lg bg-indigo-50 text-[9px] font-bold text-indigo-500 uppercase tracking-tight">Extracting Skills</span>
                      <span className="px-3 py-1 rounded-lg bg-emerald-50 text-[9px] font-bold text-emerald-500 uppercase tracking-tight">Mapping Entities</span>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex h-20 w-20 items-center justify-center rounded-[2.5rem] bg-white text-violet-500 group-hover:scale-110 transition-all duration-500 mb-6 shadow-xl shadow-violet-100 border border-violet-50">
                    <Upload className="h-9 w-9" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-800">Ready to Analyze?</h3>
                  <p className="mt-2 text-sm text-slate-500 font-medium max-w-xs mx-auto">
                    Drag & drop your resumes here for deep AI insights and optimization scoring
                  </p>
                  <button
                    className="mt-8 rounded-2xl px-10 py-3 text-sm font-bold text-white shadow-lg shadow-violet-500/20 transition-all hover:opacity-90 active:scale-95 uppercase tracking-wider"
                    style={{ background: 'linear-gradient(135deg, #7c3aed 0%, #14b8a6 100%)' }}
                    onClick={(e) => {
                      e.stopPropagation()
                      document.getElementById('file-input')?.click()
                    }}
                  >
                    Choose Resume Files
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Uploaded Files Queue */}
          {/* Unified Queue & Results List */}
          {(activeQueue.length > 0 || processedCandidates.length > 0) && (
            <div className="space-y-6 animate-in fade-in slide-in-from-top-4 duration-500">

              {/* Active Scans Section */}
              {activeQueue.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] px-2">Active Scanning</h3>
                  <div className="space-y-2">
                    {activeQueue.map((item) => (
                      <CompactCandidateRow key={item.id} item={item} />
                    ))}
                  </div>
                </div>
              )}

              {/* Successfully Processed Section */}
              {processedCandidates.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between px-2">
                    <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">Successfully Processed</h3>
                    <span className="text-[10px] font-bold text-slate-300 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-100/50">
                      {processedCandidates.length} Items
                    </span>
                  </div>
                  <div className="space-y-2">
                    {processedCandidates.map((candidate) => (
                      <CompactCandidateRow
                        key={candidate.id}
                        candidate={candidate}
                        onView={(id) => navigate(`/candidates/${id}`)}
                        onDelete={() => {/* Handled globally */ }}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Results are now shown directly in the queue above */}
        </div>

        {/* RIGHT COLUMN: Sidebar Controls (Span 4) */}
        <div className="lg:col-span-4 space-y-6 lg:sticky lg:top-8">

          {/* Upload Mode Tabs */}
          <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-[0.2em] mb-4">Upload Mode</h3>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => setActiveTab('single')}
                className={`flex items-center justify-between w-full px-5 py-3.5 rounded-2xl text-sm font-bold transition-all border ${activeTab === 'single'
                  ? 'bg-violet-50 shadow-sm border-violet-200 scale-[1.01]'
                  : 'bg-slate-50/50 text-slate-500 border-slate-100 hover:border-violet-100'
                  }`}
              >
                <span style={activeTab === 'single' ? { background: 'linear-gradient(135deg, #7c3aed 0%, #14b8a6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' } : {}}>
                  Single Upload
                </span>
                {activeTab === 'single' && <CheckCircle2 className="h-4 w-4 text-emerald-500" />}
              </button>
              <button
                onClick={() => setActiveTab('bulk')}
                className={`flex items-center justify-between w-full px-5 py-3.5 rounded-2xl text-sm font-bold transition-all border ${activeTab === 'bulk'
                  ? 'bg-violet-50 shadow-sm border-violet-200 scale-[1.01]'
                  : 'bg-slate-50/50 text-slate-500 border-slate-100 hover:border-violet-100'
                  }`}
              >
                <span style={activeTab === 'bulk' ? { background: 'linear-gradient(135deg, #7c3aed 0%, #14b8a6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' } : {}}>
                  Bulk Upload
                </span>
                {activeTab === 'bulk' && <CheckCircle2 className="h-4 w-4 text-emerald-500" />}
              </button>
            </div>
          </div>

          {/* Model Selection sidebar card */}
          <div className="rounded-3xl bg-white border border-slate-100 shadow-sm overflow-hidden p-5">
            <div className="flex flex-col gap-1 mb-4">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Processing Model</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-base font-bold text-slate-800">NER v2</span>
                <span className="px-2 py-0.5 rounded-lg bg-emerald-50 text-[8px] font-bold text-emerald-600 uppercase tracking-wider">Active</span>
              </div>
            </div>

            <div className="space-y-4 pt-2">
              <div className="p-4 rounded-2xl bg-slate-50/50 border border-slate-100/50">
                <div className="flex items-center gap-3 mb-2">
                  <div className="h-8 w-8 rounded-xl bg-white flex items-center justify-center border border-slate-100 text-violet-500">
                    <Settings className="h-4 w-4" />
                  </div>
                  <span className="text-xs font-bold text-slate-800">Model Engine</span>
                </div>
                <p className="text-[11px] text-slate-400 font-medium leading-relaxed">
                  Using our built-in rule-based + BERT NER pipeline for zero-latency extraction.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-indigo-50/30 border border-indigo-100/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-emerald-500" />
                    <span className="text-xs font-bold text-slate-800">Data Privacy</span>
                  </div>
                  <span className="text-[9px] font-black text-emerald-600 uppercase">Secure</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions (Future placeholder) */}
          <div className="flex items-center gap-3">
            <button className="flex-1 py-3 px-4 rounded-2xl bg-white border border-slate-100 text-xs font-bold text-slate-500 hover:bg-slate-50 transition-colors">
              Clear Queue
            </button>
            <button className="flex-1 py-3 px-4 rounded-2xl bg-white border border-slate-100 text-xs font-bold text-slate-500 hover:bg-slate-50 transition-colors">
              Help Docs
            </button>
          </div>
        </div>
      </div>

      {/* Empty state */}
      {processedCandidates.length === 0 && activeQueue.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-center opacity-30">
          <Upload className="h-10 w-10 text-slate-300 mb-4" />
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Upload queue is empty</h3>
        </div>
      )}
    </div>
  )
}
