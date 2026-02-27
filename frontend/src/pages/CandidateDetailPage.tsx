import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import * as mammoth from 'mammoth'
import ProfileHeader from '../components/candidate-detail/ProfileHeader'
import SummarySection from '../components/candidate-detail/SummarySection'
import WorkHistoryTimeline from '../components/candidate-detail/WorkHistoryTimeline'
import EducationSection from '../components/candidate-detail/EducationSection'
import SkillsSection from '../components/candidate-detail/SkillsSection'
import CertificationsSection from '../components/candidate-detail/CertificationsSection'
import ParsingStatusTimeline from '../components/candidate-detail/ParsingStatusTimeline'
import CorrectionSplitView from '../components/candidate-detail/CorrectionSplitView'
import DebugPanel from '../components/candidate-detail/DebugPanel'
import Modal from '../components/common/Modal'
import Skeleton from '../components/common/Skeleton'
import type { Candidate, ParsingJob, Education, Certification, Skill } from '../types'
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
  workHistoryFromParsed,
  educationFromParsed,
  certificationsFromParsed,
  skillsFromParsed,
  contactFromParsed,
  summaryFromParsed,
  shouldUseParsedDataFallback,
  getDisplayWorkHistory,
  getDisplayEducation,
  getDisplaySummary,
  getDisplayCertifications,
} from '../utils/parsedDataFallback'

type ReviewFlags = {
  overall_confidence: number | null
  flagged_fields: Record<string, number>
  discrepancies: string[]
}

const clone = (value: any) => JSON.parse(JSON.stringify(value))

const getPathValue = (obj: Record<string, any>, path: string) =>
  path.split('.').reduce((acc, key) => acc?.[key], obj)

const setPathValue = (obj: Record<string, any>, path: string, value: string) => {
  const keys = path.split('.')
  const target = keys.slice(0, -1).reduce((acc, key) => {
    if (!acc[key]) acc[key] = {}
    return acc[key]
  }, obj as Record<string, any>)
  target[keys[keys.length - 1]] = value
}

export default function CandidateDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [originalCandidate, setOriginalCandidate] = useState<Candidate | null>(null)
  const [latestJob, setLatestJob] = useState<ParsingJob | null>(null)
  const [reviewFlags, setReviewFlags] = useState<ReviewFlags>({
    overall_confidence: null,
    flagged_fields: {},
    discrepancies: [],
  })
  const [resumeUrl, setResumeUrl] = useState<string | null>(null)
  const [resumePreviewUrl, setResumePreviewUrl] = useState<string | null>(null)
  const [resumePreviewError, setResumePreviewError] = useState<string | null>(null)
  const [resumePreviewHtml, setResumePreviewHtml] = useState<string | null>(null)
  const [resumePreviewType, setResumePreviewType] = useState<'pdf' | 'docx' | null>(
    null,
  )
  const [previewOpen, setPreviewOpen] = useState(false)
  const [parsedData, setParsedData] = useState<Record<string, any>>({})
  const [originalData, setOriginalData] = useState<Record<string, any>>({})
  const [compareMode, setCompareMode] = useState(false)
  const [history, setHistory] = useState<Record<string, any>[]>([])
  const [future, setFuture] = useState<Record<string, any>[]>([])
  const [pendingChanges, setPendingChanges] = useState<
    Record<string, { original: string | null; corrected: string | null }>
  >({})
  const [loading, setLoading] = useState(true)

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
        setReviewFlags(reviewData.review_flags)
        setParsedData(clone(reviewData.latest_job?.parsed_data || {}))
        setOriginalData(clone(reviewData.latest_job?.parsed_data || {}))
        setHistory([])
        setFuture([])
        setPendingChanges({})

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

  const handleWorkHistoryChange = useCallback(
    (workHistoryId: string, field: string, value: string) => {
      setCandidate((prev) => {
        if (!prev?.work_history) return prev
        const next = {
          ...prev,
          work_history: prev.work_history.map((item) =>
            item.id === workHistoryId ? { ...item, [field]: value } : item,
          ),
        }
        return next
      })

      const original =
        originalCandidate?.work_history?.find((item) => item.id === workHistoryId) as any
      const originalValue = original?.[field]
      const path = `work_history.${workHistoryId}.${field}`
      setPendingChanges((prev) => ({
        ...prev,
        [path]: {
          original: originalValue ? String(originalValue) : null,
          corrected: value,
        },
      }))
    },
    [originalCandidate],
  )

  const handleSkillsUpdate = useCallback(
    async (updatedSkills: Skill[]) => {
      if (!id) return
      const skillsString = updatedSkills.map((s) => s.name).join(', ')
      const originalSkillsString =
        originalCandidate?.skills?.map((s) => s.name).join(', ') || ''

      if (skillsString === originalSkillsString) return

      // Optimistic update
      setCandidate((prev) => (prev ? { ...prev, skills: updatedSkills } : prev))

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
        setCandidate(originalCandidate)
      }
    },
    [id, originalCandidate],
  )

  const handleEducationUpdate = useCallback(
    async (educationId: string, updated: Partial<Education>) => {
      const originalItem = originalCandidate?.education?.find(
        (item) => item.id === educationId,
      ) as any
      if (!originalItem) return

      const allowedFields = [
        'institution',
        'degree',
        'field_of_study',
        'start_date',
        'end_date',
        'description',
      ]

      const corrections = Object.entries(updated)
        .filter(([field, value]) => {
          if (!allowedFields.includes(field)) return false
          // Only send if it actually changed
          return String(value ?? '') !== String(originalItem[field] ?? '')
        })
        .map(([field, value]) => ({
          field_name: `education.${educationId}.${field}`,
          original_value: originalItem[field] ? String(originalItem[field]) : null,
          corrected_value: value ? String(value) : null,
        }))

      if (corrections.length === 0) return

      // Optimistic update
      setCandidate((prev) => {
        if (!prev?.education) return prev
        return {
          ...prev,
          education: prev.education.map((item) =>
            item.id === educationId ? { ...item, ...updated } : item,
          ),
        }
      })

      try {
        const updatedCandidate = await submitCorrections(id!, corrections)
        setCandidate(updatedCandidate)
        setOriginalCandidate(updatedCandidate)
        toast.success('Education updated')
      } catch (error: any) {
        const msg = error?.response?.data?.detail || 'Failed to update education'
        toast.error(msg)
        setCandidate(originalCandidate)
      }
    },
    [id, originalCandidate],
  )

  const handleCertificationUpdate = useCallback(
    async (certId: string, updated: Partial<Certification>) => {
      const originalItem = originalCandidate?.certifications?.find(
        (item) => item.id === certId,
      ) as any
      if (!originalItem) return

      const allowedFields = [
        'name',
        'issuing_organization',
        'issue_date',
        'expiry_date',
        'credential_id',
      ]

      const corrections = Object.entries(updated)
        .filter(([field, value]) => {
          if (!allowedFields.includes(field)) return false
          return String(value ?? '') !== String(originalItem[field] ?? '')
        })
        .map(([field, value]) => ({
          field_name: `certifications.${certId}.${field}`,
          original_value: originalItem[field] ? String(originalItem[field]) : null,
          corrected_value: value ? String(value) : null,
        }))

      if (corrections.length === 0) return

      // Optimistic update
      setCandidate((prev) => {
        if (!prev?.certifications) return prev
        return {
          ...prev,
          certifications: prev.certifications.map((item) =>
            item.id === certId ? { ...item, ...updated } : item,
          ),
        }
      })

      try {
        const updatedCandidate = await submitCorrections(id!, corrections)
        setCandidate(updatedCandidate)
        setOriginalCandidate(updatedCandidate)
        toast.success('Certification updated')
      } catch (error: any) {
        const msg = error?.response?.data?.detail || 'Failed to update certification'
        toast.error(msg)
        setCandidate(originalCandidate)
      }
    },
    [id, originalCandidate],
  )

  const handleCertificationChange = useCallback(
    (certificationId: string, field: string, value: string) => {
      handleCertificationUpdate(certificationId, { [field]: value })
    },
    [handleCertificationUpdate],
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

  const onFieldChange = useCallback(
    (path: string, value: string) => {
      setHistory((prev) => [...prev, clone(parsedData)])
      setFuture([])
      setParsedData((prev) => {
        const next = clone(prev)
        setPathValue(next, path, value)
        return next
      })
      const original = getPathValue(originalData, path)
      setPendingChanges((prev) => ({
        ...prev,
        [path]: {
          original: original ? String(original) : null,
          corrected: value,
        },
      }))
    },
    [parsedData, originalData],
  )

  const handleSaveCorrections = async () => {
    if (!id) return
    const corrections = Object.entries(pendingChanges).map(([field, values]) => ({
      field_name: field,
      original_value: values.original,
      corrected_value: values.corrected,
    }))
    if (!corrections.length) {
      toast('No changes to save')
      return
    }
    try {
      const updatedCandidate = await submitCorrections(id, corrections)
      const nextOriginal = clone(originalData)
      corrections.forEach((item) => {
        if (item.corrected_value) {
          setPathValue(nextOriginal, item.field_name, item.corrected_value)
        }
      })
      setOriginalData(nextOriginal)
      setCandidate(updatedCandidate)
      setOriginalCandidate(updatedCandidate)
      setPendingChanges({})
      toast.success('Corrections saved')
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : 'Failed to save corrections',
      )
    }
  }

  const handleUndo = () => {
    if (!history.length) return
    const prev = history[history.length - 1]
    setHistory((items) => items.slice(0, -1))
    setFuture((items) => [clone(parsedData), ...items])
    setParsedData(prev)
    setPendingChanges((prevChanges) => {
      const next: Record<string, { original: string | null; corrected: string | null }> = {}
      Object.keys(prevChanges).forEach((path) => {
        const original = getPathValue(originalData, path)
        const corrected = getPathValue(prev, path)
        if (String(original ?? '') !== String(corrected ?? '')) {
          next[path] = {
            original: original ? String(original) : null,
            corrected: corrected ? String(corrected) : null,
          }
        }
      })
      return next
    })
  }

  const handleRedo = () => {
    if (!future.length) return
    const next = future[0]
    setFuture((items) => items.slice(1))
    setHistory((items) => [...items, clone(parsedData)])
    setParsedData(next)
    setPendingChanges((prevChanges) => {
      const updated: Record<string, { original: string | null; corrected: string | null }> = {}
      Object.keys(prevChanges).forEach((path) => {
        const original = getPathValue(originalData, path)
        const corrected = getPathValue(next, path)
        if (String(original ?? '') !== String(corrected ?? '')) {
          updated[path] = {
            original: original ? String(original) : null,
            corrected: corrected ? String(corrected) : null,
          }
        }
      })
      return updated
    })
  }

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

  const useParsedDataFallback = shouldUseParsedDataFallback(candidate, parsedData)
  const fallbackWorkHistory = workHistoryFromParsed(parsedData.work_experience)
  const fallbackEducation = educationFromParsed(parsedData.education)
  const fallbackCertifications = certificationsFromParsed(parsedData.certifications)
  const { skills: fallbackSkills, candidateSkills: fallbackCandidateSkills } =
    skillsFromParsed(parsedData.skills)
  const fallbackContact = contactFromParsed(parsedData.contact)
  const fallbackSummary = summaryFromParsed(parsedData)

  // Prefer parsed_data per section when it has content so UI matches Export JSON
  const displayWorkHistory = getDisplayWorkHistory(parsedData, dbHistory)
  const displayEducation = getDisplayEducation(parsedData, candidate.education ?? [])
  const displayCertifications = getDisplayCertifications(parsedData, candidate.certifications ?? [])
  const displaySummary = getDisplaySummary(parsedData, candidate.summary)

  const displaySkills = useParsedDataFallback ? fallbackSkills : (candidate.skills ?? [])
  const displayCandidateSkills = useParsedDataFallback
    ? fallbackCandidateSkills
    : (candidate.candidate_skills ?? [])
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

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <SummarySection
          summary={displaySummary}
          onSave={handleSummarySave}
          readOnly={useParsedDataFallback}
        />
        <ParsingStatusTimeline job={latestJob} onRetry={handleReprocess} />
      </div>

      {showMismatchBanner && (
        <div className="mb-4 rounded border border-yellow-300 bg-yellow-50 p-3 text-sm text-yellow-800">
          ⚠️ Work history was parsed ({parsedExperience.length} entries) but
          not saved to the database. Try re-processing this resume or contact
          support.
        </div>
      )}
      <WorkHistoryTimeline
        candidateId={id!}
        items={displayWorkHistory}
        onUpdate={(updated) => {
          setCandidate((prev) => (prev ? { ...prev, work_history: updated } : prev))
          setOriginalCandidate((prev) => (prev ? { ...prev, work_history: updated } : prev))
        }}
        readOnly={useParsedDataFallback}
      />

      <div className="grid gap-6 lg:grid-cols-[1fr,1fr]">
        <EducationSection
          candidateId={id!}
          items={displayEducation}
          onUpdate={(updated) => {
            setCandidate((prev) => (prev ? { ...prev, education: updated } : prev))
            setOriginalCandidate((prev) => (prev ? { ...prev, education: updated } : prev))
          }}
          readOnly={useParsedDataFallback}
        />
        <CertificationsSection
          candidateId={id!}
          items={displayCertifications}
          rawContent={(parsedData as any)?.sections?.certifications?.content as any}
          onUpdate={(updated) => {
            setCandidate((prev) => (prev ? { ...prev, certifications: updated } : prev))
            setOriginalCandidate((prev) => (prev ? { ...prev, certifications: updated } : prev))
          }}
          readOnly={useParsedDataFallback}
        />
      </div>

      <SkillsSection
        skills={
          Array.isArray((latestJob as any)?.parsed_data?.skills)
            ? ((latestJob as any).parsed_data.skills as any[]).map(
                (s: any, i: number) =>
                  ({
                    id: s.id ?? `skill-${i}`,
                    name: s.name ?? s.normalized_name ?? '',
                    category: s.category ?? null,
                    normalized_name: s.normalized_name ?? null,
                    source: s.source ?? null,
                  }) as Skill
              )
            : candidate.skills ?? []
        }
        candidateSkills={candidate.candidate_skills}
        onUpdate={handleSkillsUpdate}
      />

      <DebugPanel debug={(parsedData as any)?.debug} />

      <div className="space-y-3">
        <h2 className="text-xl font-semibold text-slate-900">
          Correction interface
        </h2>
        <CorrectionSplitView
          resumeUrl={resumePreviewUrl}
          resumeError={resumePreviewError}
          parsedData={parsedData}
          originalData={originalData}
          workHistory={displayWorkHistory}
          originalWorkHistory={
            useParsedDataFallback ? fallbackWorkHistory : (originalCandidate?.work_history || [])
          }
          onWorkHistoryChange={handleWorkHistoryChange}
          certifications={displayCertifications}
          originalCertifications={
            useParsedDataFallback ? fallbackCertifications : (originalCandidate?.certifications || [])
          }
          onCertificationChange={handleCertificationChange}
          flaggedFields={reviewFlags.flagged_fields}
          discrepancies={reviewFlags.discrepancies}
          compareMode={compareMode}
          onToggleCompare={() => setCompareMode((prev) => !prev)}
          onFieldChange={onFieldChange}
          onUndo={handleUndo}
          onRedo={handleRedo}
          onSave={handleSaveCorrections}
          canUndo={history.length > 0}
          canRedo={future.length > 0}
          readOnly={useParsedDataFallback}
        />
      </div>
    </section>
  )
}