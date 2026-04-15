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
  HelpCircle,
} from 'lucide-react'
import { useUploadStore } from '../store/uploadStore'
import { useCandidateStore } from '../store/candidateStore'
import { useTheme } from '../contexts/ThemeContext'
import CandidateCard from '../components/candidates/CandidateCard'
import CompactCandidateRow from '../components/candidates/CompactCandidateRow'
import { ProcessingGauge } from '../components/candidates/CandidateUIUtils'


export default function ResumeAnalyzerPage() {
  const navigate = useNavigate()
  const { theme } = useTheme()
  const [activeTab, setActiveTab] = useState<'single' | 'bulk'>('single')
  const [showModelDetails, setShowModelDetails] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const { queue, addFiles, uploadAll, pollStatuses, setActivePreviewId, resetQueue } = useUploadStore()
  const { candidates, loadCandidates } = useCandidateStore()

  const files = useMemo(() => queue.map((item) => item.file), [queue])

  useEffect(() => {
    // Reset queue if it only contains finished items when mounting
    // Fixes the issue where navigating back shows a stale success screen
    if (queue.length > 0 && queue.every(q => q.status === 'success' || q.status === 'failed')) {
      resetQueue()
    }

    const controller = new AbortController()
    loadCandidates(controller.signal)
    return () => controller.abort()
  }, []) // Only on mount

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
  const activeItemsCount = queue.filter(item => item.status === 'processing' || item.status === 'uploading').length
  const hasJustFinished = useMemo(() => {
    return queue.length > 0 && activeItemsCount === 0 && queue.every(q => q.status === 'success' || q.status === 'error')
  }, [queue, activeItemsCount])

  useEffect(() => {
    if (hasJustFinished && queue.some(q => q.status === 'success')) {
      setShowSuccess(true)
      const timer = setTimeout(() => setShowSuccess(false), 8000)
      return () => clearTimeout(timer)
    }
  }, [hasJustFinished, queue])

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
            <p className="text-[14px] font-black text-slate-500 uppercase tracking-[0.2em] select-none">
              Resume Analyzer
            </p>
            <p className="mt-1.5 text-[13px] font-semibold text-slate-400 uppercase tracking-widest leading-none">
              Transforming raw talent data into actionable AI intelligence
            </p>
          </div>

          {/* Upload Drop Zone */}
          <div
            onDrop={(e) => {
              handleDrop(e)
              setIsDragging(false)
            }}
            onDragOver={(e) => {
              e.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            className={`relative rounded-3xl border-2 border-dashed transition-all duration-500 group cursor-pointer overflow-hidden shadow-sm flex items-center justify-center ${isDragging
              ? 'border-orange-500 bg-orange-50 shadow-orange-100'
              : 'border-slate-200 hover:border-orange-400 bg-white hover:bg-orange-50/20'
              }`}
            style={{
              background: isDragging
                ? 'rgba(234, 88, 12, 0.05)'
                : undefined, // Let the hover class or base bg-white handle it
              minHeight: 280,
            }}
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
            <div className="flex flex-col items-center justify-center py-10 text-center px-6 h-full">
              {activeQueue.length > 0 ? (
                <div className="w-full max-w-md space-y-8 animate-in fade-in zoom-in-95 duration-500">
                  <div className="flex flex-col items-center gap-4">

                    <div>
                      <h3 className="text-xl font-bold text-slate-600 dark:text-slate-200 tracking-tight">
                        AI Scanning in Progress<span className="dots-loading" />
                      </h3>
                      <p className="text-sm font-bold text-slate-400 mt-1 uppercase tracking-widest animate-pulse">Processing {activeQueue.length} {activeQueue.length === 1 ? 'Resume' : 'Resumes'}</p>
                    </div>
                  </div>

                  <div className="flex flex-col items-center gap-6">
                    <ProcessingGauge value={averageProgress} size={240} />

                    <div className="flex justify-center gap-2 -mt-4">
                      <span className="px-3 py-1 rounded-lg bg-orange-50 dark:bg-orange-500/10 text-[9px] font-bold text-orange-600 dark:text-orange-400 uppercase tracking-tight">Extracting Skills</span>
                      <span className="px-3 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-[9px] font-bold text-emerald-500 dark:text-emerald-400 uppercase tracking-tight">Mapping Entities</span>
                    </div>
                  </div>
                </div>
              ) : showSuccess ? (
                <div className="flex flex-col items-center justify-center py-10 animate-in zoom-in-95 duration-700">
                  <div className="h-20 w-20 rounded-[2.5rem] bg-emerald-500 text-white flex items-center justify-center shadow-xl shadow-emerald-200 mb-6 pulse-glow">
                    <CheckCircle2 className="h-10 w-10" />
                  </div>
                  <h3 className="text-2xl font-black text-emerald-600 tracking-tight">Process Complete!</h3>
                  <p className="text-slate-500 font-bold mt-2">All resumes have been successfully analyzed.</p>
                  <button
                    onClick={() => setShowSuccess(false)}
                    className="mt-6 px-6 py-2 rounded-xl bg-slate-100 text-slate-600 text-xs font-black uppercase tracking-widest hover:bg-slate-200 transition-colors"
                  >
                    Upload More
                  </button>
                </div>
              ) : (
                <>
                  <div className="flex flex-col items-center justify-center py-6 text-center">
                    <div className="mb-6 relative transition-transform duration-500 group-hover:scale-110">
                      <div className="flex h-16 w-16 items-center justify-center rounded-[1.2rem] bg-orange-50 dark:bg-orange-900/20 shadow-sm border border-orange-100/50">
                        <FileText className="h-8 w-8 text-slate-300 dark:text-slate-600" />
                      </div>
                    </div>

                    <h3 className="text-xl font-bold text-slate-700 dark:text-slate-100 tracking-tight mb-2">
                      Upload Your Resume
                    </h3>

                    <p className="text-[14px] text-slate-400 dark:text-slate-500 font-medium max-w-sm mb-6 leading-relaxed">
                      Drag & drop or click to browse<br />
                      PDF, DOC, DOCX — Max 5MB
                    </p>

                    <span className="text-[14px] font-bold text-orange-500 hover:text-orange-600 transition-colors">
                      Browse Files
                    </span>
                  </div>
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
        <div className="lg:col-span-4 space-y-5 lg:sticky lg:top-8">

          {/* Upload Mode Tabs */}
          <div className="bg-white p-4 rounded-[2rem] border border-slate-100 shadow-sm">
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-3 px-1">Upload Mode</h3>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => setActiveTab('single')}
                className={`flex items-center justify-between w-full px-4 py-3 rounded-xl text-[13px] font-bold transition-all border ${activeTab === 'single'
                  ? 'bg-blue-50 text-blue-600 shadow-sm border-blue-200'
                  : 'bg-slate-50/50 text-slate-500 border-slate-100/50 hover:border-blue-100'
                  }`}
              >
                Single Upload
                {activeTab === 'single' && <CheckCircle2 className="h-4 w-4" />}
              </button>
              <button
                onClick={() => setActiveTab('bulk')}
                className={`flex items-center justify-between w-full px-4 py-3 rounded-xl text-[13px] font-bold transition-all border ${activeTab === 'bulk'
                  ? 'bg-blue-50 text-blue-600 shadow-sm border-blue-200'
                  : 'bg-slate-50/50 text-slate-500 border-slate-100/50 hover:border-blue-100'
                  }`}
              >
                Bulk Upload
                {activeTab === 'bulk' && <CheckCircle2 className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Model Selection sidebar card */}
          <div className="rounded-[2rem] bg-white border border-slate-100 shadow-sm overflow-hidden p-4">
            <div className="flex flex-col gap-1 mb-3">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-1">Processing Model</span>
              <div className="flex items-center gap-2 mt-1 relative group/model px-1">
                <span className="text-[15px] font-bold text-slate-700 dark:text-slate-200">NER v2</span>
                <span className="px-2 py-0.5 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-[8px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Active</span>
                <button className="text-slate-300 hover:text-orange-500 transition-colors">
                  <HelpCircle className="h-3 w-3" />
                </button>
                <div className="absolute bottom-full left-0 mb-2 w-48 p-3 rounded-xl bg-slate-800 text-white text-[10px] leading-relaxed opacity-0 invisible group-hover/model:opacity-100 group-hover/model:visible transition-all duration-300 shadow-xl z-20">
                  <p className="font-bold border-b border-slate-700 pb-1 mb-1 italic">NER v2 Details:</p>
                  Built-in BERT & Rule-based extraction optimized for zero-latency resume parsing and high entity accuracy.
                </div>
              </div>
            </div>

            <div className="space-y-3 pt-1">
              <div className="p-3.5 rounded-2xl bg-slate-50/50 border border-slate-100/50">
                <div className="flex items-center gap-3 mb-1.5">
                  <div className="h-7 w-7 rounded-lg bg-white flex items-center justify-center border border-slate-100 text-orange-500">
                    <Settings className="h-3.5 w-3.5" />
                  </div>
                  <span className="text-[11px] font-bold text-slate-600">Model Engine</span>
                </div>
                <p className="text-[10px] text-slate-400 font-medium leading-relaxed">
                  Using our built-in rule-based + BERT NER pipeline for zero-latency extraction.
                </p>
              </div>

              <div className="p-3 rounded-2xl bg-indigo-50/30 border border-indigo-100/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
                    <span className="text-[11px] font-bold text-slate-700">Data Privacy</span>
                  </div>
                  <span className="text-[8px] font-black text-emerald-600 uppercase">Secure</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => resetQueue()}
              className="flex-1 py-3 px-4 rounded-2xl bg-white border border-slate-100 text-[10px] font-bold text-slate-400 uppercase tracking-wider hover:bg-slate-50 transition-colors"
            >
              Clear Queue
            </button>
            <button className="flex-1 py-3 px-4 rounded-2xl bg-white border border-slate-100 text-[10px] font-bold text-slate-400 uppercase tracking-wider hover:bg-slate-50 transition-colors">
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
