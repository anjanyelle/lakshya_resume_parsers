import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useLayout } from '../contexts/LayoutContext'
import { toast } from 'react-hot-toast'
import * as mammoth from 'mammoth'
import ProfileHeader from '../components/candidate-detail/ProfileHeader'
import ResumeViewerWithHighlights, { type FieldMapping } from '../components/candidate-detail/ResumeViewerWithHighlights'
import StructuredDataPanel from '../components/candidate-detail/StructuredDataPanel'
import Modal from '../components/common/Modal'
import Skeleton from '../components/common/Skeleton'
import type { Candidate, ParsingJob, Skill } from '../types'
import {
  approveCandidate,
  deleteCandidate,
  downloadResume,
  exportCandidateJson,
  fetchCandidate,
  fetchCandidateReview,
  reprocessCandidate,
  submitCorrections,
} from '../services/api/candidates'
import { fetchJobExtractionDebug } from '../services/api/uploads'
import {
  skillsFromParsed,
  contactFromParsed,
  shouldUseParsedDataFallback,
  getDisplayWorkHistory,
  getDisplayEducation,
  getDisplaySummary,
  getDisplayCertifications
} from '../utils/parsedDataFallback'

const clone = (value: any) => JSON.parse(JSON.stringify(value))

export default function CandidateDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [originalCandidate, setOriginalCandidate] = useState<Candidate | null>(null)
  const [latestJob, setLatestJob] = useState<ParsingJob | null>(null)
  const [resumeUrl, setResumeUrl] = useState<string | null>(null)
  const [resumePreviewUrl, setResumePreviewUrl] = useState<string | null>(null)
  const [resumePreviewError, setResumePreviewError] = useState<string | null>(null)
  const [resumePreviewHtml, setResumePreviewHtml] = useState<string | null>(null)
  const [resumePreviewType, setResumePreviewType] = useState<'pdf' | 'docx' | null>(
    null,
  )
  const [previewOpen, setPreviewOpen] = useState(false)
  const [parsedData, setParsedData] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(true)
  const [activeField, setActiveField] = useState<string | null>(null)
  const [activeFieldId, setActiveFieldId] = useState<string | null>(null)
  const [scrollToFieldId, setScrollToFieldId] = useState<string | null>(null)
  const [panelScrollToFieldId, setPanelScrollToFieldId] = useState<string | null>(null)
  const [autoEditFieldId, setAutoEditFieldId] = useState<string | null>(null)
  const { collapseSidebar } = useLayout()

  // Refs for scrollIntoView: name, email, phone, skills, experience
  const fieldRefsMap = useRef<Record<string, HTMLDivElement | null>>({
    full_name: null,
    email: null,
    phone: null,
    skills: null,
    experience: null,
  })

  // Prepare scrollToField for later use (highlight not implemented yet)
  const scrollToField = useCallback((fieldId: string) => {
    const el = fieldRefsMap.current[fieldId]
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }, [])
    
  useEffect(() => {
    if (!id) return
    const fetchData = async () => {
      try {
        setLoading(true)
        const [candidateData, reviewData] = await Promise.all([
          fetchCandidate(id),
          fetchCandidateReview(id),
        ])
        setCandidate(candidateData)
        setOriginalCandidate(candidateData)
        setLatestJob(reviewData.latest_job)
        setParsedData(clone(reviewData.latest_job?.parsed_data || {}))

        if (import.meta.env.DEV) {
          const pd = reviewData.latest_job?.parsed_data || {}
          const work = pd.work_experience || []
          const edu = pd.education || []
          const certs = pd.certifications || []
          const sections = (pd.sections || {}) as Record<string, unknown>
          const summaryBlock = sections.summary || {}
          const summaryContent =
            typeof summaryBlock === 'object' && summaryBlock !== null && 'content' in summaryBlock
              ? String((summaryBlock as { content?: string }).content || '')
              : ''
          console.log('[DATA-LOSS CHECK] Final frontend rendering — data received from API:', {
            candidateId: id,
            db_work_history_count: candidateData.work_history?.length ?? 0,
            db_education_count: candidateData.education?.length ?? 0,
            db_certifications_count: candidateData.certifications?.length ?? 0,
            parsed_work_experience_count: Array.isArray(work) ? work.length : 0,
            parsed_education_count: Array.isArray(edu) ? edu.length : 0,
            parsed_certifications_count: Array.isArray(certs) ? certs.length : 0,
            parsed_summary_length: summaryContent.length,
            summary_sample: summaryContent.slice(0, 120) + (summaryContent.length > 120 ? '...' : ''),
          })
          const jobId = reviewData.latest_job?.id
          if (jobId) {
            fetchJobExtractionDebug(jobId)
              .then((debug) => {
                console.log('[DATA-LOSS CHECK] Backend extraction debug (compare with rendering):', {
                  raw_text_length: debug.raw_text_length,
                  raw_sample_first_200: debug.raw_text_sample_first_200?.slice(0, 100) + '...',
                  parsed_work_count: debug.parsed_work_experience_count,
                  parsed_work_desc_chars: debug.parsed_work_description_total_chars,
                  parsed_education_count: debug.parsed_education_count,
                  parsed_certifications_count: debug.parsed_certifications_count,
                  parsed_summary_length: debug.parsed_summary_length,
                  method: debug.text_extraction_method,
                  used_ocr: debug.used_ocr,
                })
              })
              .catch(() => {})
          }
        }
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : 'Failed to load candidate',
        )
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleSkillsUpdate = useCallback(
    async (updatedSkills: Skill[]) => {
      if (!id) return
      const skillsString = updatedSkills.map((s) => s.name).join(', ')
      const originalSkillsString =
        originalCandidate?.skills?.map((s) => s.name).join(', ') || ''

      if (skillsString === originalSkillsString) return

      // Optimistic update
      //setCandidate((prev) => (prev ? { ...prev, skills: updatedSkills } : prev))

      try {
        const updatedCandidate = await submitCorrections(id, [
          {
            field_name: 'skills',
            original_value: originalSkillsString,
            corrected_value: skillsString,
          },
        ])
        setCandidate(updatedCandidate)
        setOriginalCandidate(updatedCandidate)
        toast.success('Skills updated')
      } catch (error: any) {
        const msg = error?.response?.data?.detail || 'Failed to update skills'
        toast.error(msg)
        //setCandidate(originalCandidate)
      }
    },
    [id, originalCandidate],
  )

  useEffect(() => {
    if (!id || !candidate) return

    const jobs = [...(candidate.parsing_jobs || [])].sort((a, b) => {
      const aTime = a.started_at ? new Date(a.started_at).getTime() : 0
      const bTime = b.started_at ? new Date(b.started_at).getTime() : 0
      return bTime - aTime
    })
    const latestJob = jobs[0]
    const filename = latestJob?.filename || ''
    const ext = filename.split('.').pop()?.toLowerCase() || ''

    downloadResume(id)
      .then(async (url) => {
        setResumeUrl(url)
        setResumePreviewHtml(null)
        setResumePreviewType(null)

        if (ext === 'doc') {
          setResumePreviewUrl(null)
          setResumePreviewHtml(null)
          setResumePreviewType(null)
          setResumePreviewError(
            'Preview not supported for this file type. Please download.',
          )
          return
        }

        setResumePreviewError(null)
        try {
          const { fetchFileAsBlobUrl, fetchFileAsBlob } = await import(
            '../services/api/files'
          )

          let previewUrl = url
          const apiOrigin = new URL(
            import.meta.env.VITE_API_URL?.toString() ?? 'http://localhost:8000',
          ).origin
          const isAbsolute = /^https?:\/\//i.test(url)
          if (isAbsolute) {
            const targetOrigin = new URL(url).origin
            if (targetOrigin !== apiOrigin && latestJob?.id) {
              previewUrl = `/api/v1/files/${latestJob.id}`
            }
          }

          if (ext === 'docx') {
            const blob = await fetchFileAsBlob(previewUrl)
            const buf = await blob.arrayBuffer()
            const result = await mammoth.convertToHtml({ arrayBuffer: buf })
            setResumePreviewHtml(result.value)
            setResumePreviewType('docx')
            setResumePreviewUrl(null)
            return
          }

          if (ext === 'pdf' && latestJob?.id) {
            try {
              console.log('=== PDF HTML Debug ===')
              console.log('Job ID:', latestJob.id)
              console.log('Extension:', ext)
              const { fetchFileHtml } = await import('../services/api/files')
              const html = await fetchFileHtml(latestJob.id)
              console.log('Raw HTML response:', html)
              console.log('HTML type:', typeof html)
              console.log('HTML length:', html?.length || 0)
              console.log('HTML trimmed length:', html?.trim()?.length || 0)
              
              if (html && html.trim().length > 0) {
                console.log('✅ Setting HTML preview state')
                setResumePreviewHtml(html)
                setResumePreviewType('docx')
                setResumePreviewUrl(null)
                setResumePreviewError(null)
                console.log('Final state - type: docx, html exists:', !!resumePreviewHtml)
              } else {
                console.log('❌ HTML invalid, falling back to iframe')
                console.log('Final state - type: pdf, html exists:', !!resumePreviewHtml)
                setResumePreviewError('PDF highlighting not available. Showing standard PDF viewer.')
                /* fall through to iframe */
              }
              return
            } catch (error: any) {
              console.error('❌ PDF HTML preview failed:', error)
              console.warn('PDF HTML preview not available, falling back to iframe:', error?.message || error)
              setResumePreviewError('PDF highlighting not available. Showing standard PDF viewer.')
              /* fall through to iframe */
            }
          }

          const blobUrl = await fetchFileAsBlobUrl(previewUrl)
          setResumePreviewUrl(blobUrl)
          setResumePreviewType('pdf')
        } catch (error) {
          setResumePreviewUrl(null)
          setResumePreviewHtml(null)
          setResumePreviewType(null)
          setResumePreviewError(
            error instanceof Error
              ? error.message
              : 'Resume preview unavailable. Please download.',
          )
        }
      })
      .catch(() => {
        setResumeUrl(null)
        setResumePreviewUrl(null)
        setResumePreviewHtml(null)
        setResumePreviewType(null)
        setResumePreviewError('Resume preview unavailable. Please download.')
      })
  }, [id, candidate])

  useEffect(() => {
    return () => {
      if (resumePreviewUrl) {
        URL.revokeObjectURL(resumePreviewUrl)
      }
    }
  }, [resumePreviewUrl])

  const handleSummarySave = async (value: string) => {
    if (!id) return
    try {
      const updatedCandidate = await submitCorrections(
        id, [
        {
          field_name: 'summary',
          original_value: candidate?.summary ?? null,
          corrected_value: value,
        },
      ])

      // 🔥 Always use backend response
      setCandidate(updatedCandidate)
      setOriginalCandidate(updatedCandidate)
      setParsedData((prev) => ({
        ...prev,
        sections: {
          ...prev.sections,
          summary: {
            ...(prev.sections?.summary || {}),
            content: value,
        },
      },
    }))
      // setCandidate((prev) => (prev ? { ...prev, summary: value } : prev))
      toast.success('Summary updated')
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : 'Failed to update summary',
      )
    }
  }

  const handleExport = async () => {
    if (!id) return
    try {
      const data = await exportCandidateJson(id)
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `candidate-${id}.json`
      link.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      toast.error('Failed to export JSON')
    }
  }

  const handleDelete = async () => {
    if (!id) return
    try {
      await deleteCandidate(id)
      toast.success('Candidate deleted')
      navigate('/candidates')
    } catch (error) {
      toast.error('Failed to delete candidate')
    }
  }

  const handleApprove = async () => {
    if (!id) return
    try {
      const data = await approveCandidate(id)
      setCandidate(data)
      toast.success('Marked as reviewed')
    } catch (error) {
      toast.error('Failed to approve candidate')
    }
  }

  const handleReprocess = async () => {
    if (!id) return
    try {
      await reprocessCandidate(id)
      toast.success('Reprocess triggered')
    } catch (error) {
      toast.error('Failed to reprocess')
    }
  }

  const handleDownload = async () => {
    if (!resumeUrl) return
    try {
      const { downloadFile } = await import('../services/api/files')
      const fallbackName = `resume-${candidate?.id ?? 'candidate'}.pdf`
      await downloadFile(resumeUrl, fallbackName)
    } catch (error) {
      window.open(resumeUrl, '_blank')
    }
  }

  const handlePreview = async () => {
    if (!resumePreviewUrl && !resumePreviewHtml) {
      toast.error(resumePreviewError || 'Resume preview unavailable. Please download.')
      return
    }
    setPreviewOpen(true)
  }

  const handleFieldClickFromResume = useCallback(
    (fieldId: string) => {
      collapseSidebar()
      setActiveField(fieldId)
      setActiveFieldId(fieldId)
      setPanelScrollToFieldId(fieldId)
      setAutoEditFieldId(fieldId)
    },
    [collapseSidebar]
  )

  const handleFieldSelectFromPanel = useCallback((fieldId: string) => {
    setActiveField(fieldId)
    setActiveFieldId(fieldId)
    setScrollToFieldId(fieldId)
  }, [])

  const handleScrollComplete = useCallback(() => {
    setScrollToFieldId(null)
  }, [])

  const handlePanelScrollComplete = useCallback(() => {
    setPanelScrollToFieldId(null)
  }, [])

  const handleAutoEditConsumed = useCallback(() => {
    setAutoEditFieldId(null)
  }, [])

  if (loading || !candidate) {
    return (
      <section className="space-y-6">
        <Skeleton lines={8} />
      </section>
    )
  }

  const parsedExperience = Array.isArray(latestJob?.parsed_data?.work_experience)
    ? latestJob.parsed_data.work_experience
    : []
  const dbHistory = candidate.work_history ?? []

  // const useParsedDataFallback = shouldUseParsedDataFallback(candidate, parsedData)
  // const { skills: fallbackSkills, candidateSkills: fallbackCandidateSkills } =
  //   skillsFromParsed(parsedData.skills)
  // const fallbackContact = contactFromParsed(parsedData.contact)

  const useParsedDataFallback = shouldUseParsedDataFallback(candidate, parsedData)

  const fallbackContact = contactFromParsed(parsedData.contact)

  // Prefer parsed_data per section when it has content so UI matches Export JSON
  const displayWorkHistory = getDisplayWorkHistory(parsedData, dbHistory)
  const displayEducation = getDisplayEducation(parsedData, candidate.education ?? [])
  const displayCertifications = getDisplayCertifications(parsedData, candidate.certifications ?? [])
  const displaySummary = getDisplaySummary(parsedData, candidate.summary)
  const displaySkills = candidate.skills ?? []
  const displayCandidateSkills = candidate.candidate_skills ?? []

  //const displaySkills = useParsedDataFallback ? fallbackSkills : (candidate.skills ?? [])
  //const displayCandidateSkills = useParsedDataFallback ? fallbackCandidateSkills : (candidate.candidate_skills ?? [])

  // Prefer parsed name/contact when DB fields are empty (fixes "Unnamed candidate" for PDFs)
  const displayCandidate: Candidate = useParsedDataFallback
    ? {
        ...candidate,
        full_name: fallbackContact.full_name ?? candidate.full_name,
        email: fallbackContact.email ?? candidate.email,
        phone: fallbackContact.phone ?? candidate.phone,
        location: fallbackContact.location ?? candidate.location,
      }
    : {
        ...candidate,
        full_name: (candidate.full_name?.trim() || fallbackContact.full_name) ?? candidate.full_name,
        email: candidate.email || fallbackContact.email || candidate.email,
        phone: candidate.phone || fallbackContact.phone || candidate.phone,
        location: candidate.location || fallbackContact.location || candidate.location,
      }

  const showMismatchBanner =
    dbHistory.length === 0 && parsedExperience.length > 0 && !useParsedDataFallback

  const summaryExcerpt =
    (displaySummary ?? '').trim().length > 3
      ? (displaySummary ?? '').trim().slice(0, 60)
      : ''
  const fieldMappings: FieldMapping[] = [
    { id: 'full_name', value: displayCandidate.full_name ?? '', label: 'Candidate Name' },
    { id: 'email', value: displayCandidate.email ?? '', label: 'Candidate Email' },
    { id: 'phone', value: displayCandidate.phone ?? '', label: 'Candidate Phone' },
    { id: 'location', value: displayCandidate.location ?? '', label: 'Location' },
    { id: 'linkedin_url', value: displayCandidate.linkedin_url ?? '', label: 'LinkedIn' },
    { id: 'github_url', value: displayCandidate.github_url ?? '', label: 'GitHub' },
    ...(summaryExcerpt
      ? [{ id: 'summary' as const, value: summaryExcerpt, label: 'Summary' }]
      : []),
    ...displaySkills
      .filter((s) => s.name?.trim().length > 2)
      .map((s) => ({ id: 'skills' as const, value: s.name, label: 'Skills' })),
    ...displayWorkHistory
      .filter((wh) => (wh.company_name ?? '').trim().length > 2)
      .map((wh) => ({ id: 'experience' as const, value: wh.company_name ?? '', label: 'Experience' })),
    ...displayWorkHistory
      .filter((wh) => (wh.job_title ?? '').trim().length > 2)
      .map((wh) => ({ id: 'experience' as const, value: wh.job_title ?? '', label: 'Experience' })),
    ...displayEducation
      .filter((e) => (e.institution ?? '').trim().length > 2)
      .map((e) => ({ id: 'education' as const, value: e.institution ?? '', label: 'Education' })),
  ]

  // Debug: log data availability for troubleshooting missing UI data
  if (import.meta.env.DEV) {
    console.log('[CandidateDetail] Data loaded:', {
      candidateId: id,
      name: candidate?.full_name || '(empty)',
      summaryLen: candidate?.summary?.length ?? 0,
      workHistoryCount: dbHistory.length,
      parsedExperienceCount: parsedExperience.length,
      educationCount: candidate?.education?.length ?? 0,
      certificationsCount: candidate?.certifications?.length ?? 0,
      skillsCount: candidate?.candidate_skills?.length ?? 0,
      mismatch: showMismatchBanner,
    })
  }

  return (
    <section className="space-y-6">
      {useParsedDataFallback && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Showing parsed data (not yet saved to database). Reprocess or save corrections to persist.
        </div>
      )}
      <ProfileHeader
        candidate={displayCandidate}
        onPreview={handlePreview}
        onDownload={handleDownload}
        onExportJson={handleExport}
        onReprocess={handleReprocess}
        onApprove={handleApprove}
        onDelete={handleDelete}
      />

      <Modal open={previewOpen} onClose={() => setPreviewOpen(false)} title="Resume preview">
        {resumePreviewType === 'docx' && resumePreviewHtml ? (
          <div className="h-[80vh] w-full overflow-auto rounded-lg border border-slate-200 bg-white p-6">
            <div
              className="prose prose-slate max-w-none"
              dangerouslySetInnerHTML={{ __html: resumePreviewHtml }}
            />
          </div>
        ) : resumePreviewUrl ? (
          <iframe
            src={resumePreviewUrl}
            className="h-[80vh] w-full rounded-lg border border-slate-200"
            title="Resume preview"
          />
        ) : (
          <div className="rounded-lg border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
            Resume preview unavailable.
          </div>
        )}
      </Modal>

      {/* Full height 50/50 layout: Resume on left, Structured data on right */}
      <div className="grid min-h-[calc(100vh-14rem)] grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left: Resume Document Viewer */}
        <div className="flex min-h-[400px] flex-col lg:min-h-[calc(100vh-14rem)]">
          <div className="mb-2 flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-2 shadow-sm">
            <span className="text-sm font-medium text-slate-700">
              {latestJob?.filename ?? 'Resume'}
            </span>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
              Document Viewer
            </span>
          </div>
          <div className="min-h-0 flex-1 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <ResumeViewerWithHighlights
              html={resumePreviewHtml}
              pdfUrl={resumePreviewType === 'pdf' ? resumePreviewUrl : null}
              emptyMessage="Loading resume…"
              fieldMappings={fieldMappings}
              activeFieldId={activeField ?? activeFieldId}
              onFieldClick={handleFieldClickFromResume}
              scrollToFieldId={scrollToFieldId}
              onScrollComplete={handleScrollComplete}
            />
          </div>
        </div>

        {/* Right: Structured Candidate Data Panel */}
        <div className="flex min-h-[400px] flex-col lg:min-h-[calc(100vh-14rem)]">
          <div className="mb-2 flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-2 shadow-sm">
            <span className="text-sm font-medium text-slate-700">
              Structured Data
            </span>
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
              Editable Fields
            </span>
          </div>
          <div className="min-h-0 flex-1 overflow-hidden rounded-xl border border-slate-200 bg-slate-50 p-4 shadow-sm">
            <StructuredDataPanel
              candidate={displayCandidate}
              displayWorkHistory={displayWorkHistory}
              displayEducation={displayEducation}
              displayCertifications={displayCertifications}              displaySkills={displaySkills}
              displayCandidateSkills={displayCandidateSkills}
              displaySummary={displaySummary}
              activeFieldId={activeField ?? activeFieldId}
              onFieldSelect={handleFieldSelectFromPanel}
              panelScrollToFieldId={panelScrollToFieldId}
              onPanelScrollComplete={handlePanelScrollComplete}
              autoEditFieldId={autoEditFieldId}
              onAutoEditConsumed={handleAutoEditConsumed}
              onCandidateUpdate={(updated) => {
                setCandidate(updated)
                setOriginalCandidate(updated)
              }}
              onWorkHistoryUpdate={(updated) => {
                setCandidate((prev) => (prev ? { ...prev, work_history: updated } : prev))
                setOriginalCandidate((prev) => (prev ? { ...prev, work_history: updated } : prev))
              }}
              onEducationUpdate={(updated) => {
                setCandidate((prev) => (prev ? { ...prev, education: updated } : prev))
                setOriginalCandidate((prev) => (prev ? { ...prev, education: updated } : prev))
              }}
              onSkillsUpdate={handleSkillsUpdate}
              onSummarySave={handleSummarySave}
              readOnly={useParsedDataFallback}
              candidateId={id!}
              showMismatchBanner={showMismatchBanner}
            />
          </div>
        </div>
      </div>
    </section>
  )
}