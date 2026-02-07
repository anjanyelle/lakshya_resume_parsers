import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import ProfileHeader from '../components/candidate-detail/ProfileHeader'
import SummarySection from '../components/candidate-detail/SummarySection'
import WorkHistoryTimeline from '../components/candidate-detail/WorkHistoryTimeline'
import EducationSection from '../components/candidate-detail/EducationSection'
import SkillsSection from '../components/candidate-detail/SkillsSection'
import CertificationsSection from '../components/candidate-detail/CertificationsSection'
import ParsingStatusTimeline from '../components/candidate-detail/ParsingStatusTimeline'
import CorrectionSplitView from '../components/candidate-detail/CorrectionSplitView'
import Skeleton from '../components/common/Skeleton'
import type { Candidate, ParsingJob } from '../types'
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
  const [latestJob, setLatestJob] = useState<ParsingJob | null>(null)
  const [reviewFlags, setReviewFlags] = useState<ReviewFlags>({
    overall_confidence: null,
    flagged_fields: {},
    discrepancies: [],
  })
  const [resumeUrl, setResumeUrl] = useState<string | null>(null)
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
        setLatestJob(reviewData.latest_job)
        setReviewFlags(reviewData.review_flags)
        setParsedData(clone(reviewData.latest_job?.parsed_data || {}))
        setOriginalData(clone(reviewData.latest_job?.parsed_data || {}))
        setHistory([])
        setFuture([])
        setPendingChanges({})
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

  useEffect(() => {
    if (!id) return
    downloadResume(id)
      .then((url) => setResumeUrl(url))
      .catch(() => setResumeUrl(null))
  }, [id])

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
      await submitCorrections(id, corrections)
      const nextOriginal = clone(originalData)
      corrections.forEach((item) => {
        if (item.corrected_value) {
          setPathValue(nextOriginal, item.field_name, item.corrected_value)
        }
      })
      setOriginalData(nextOriginal)
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
      await submitCorrections(id, [
        {
          field_name: 'summary',
          original_value: candidate?.summary ?? null,
          corrected_value: value,
        },
      ])
      setCandidate((prev) => (prev ? { ...prev, summary: value } : prev))
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
    window.open(resumeUrl, '_blank')
  }

  if (loading || !candidate) {
    return (
      <section className="space-y-6">
        <Skeleton lines={8} />
      </section>
    )
  }

  return (
    <section className="space-y-6">
      <ProfileHeader
        candidate={candidate}
        onDownload={handleDownload}
        onExportJson={handleExport}
        onReprocess={handleReprocess}
        onApprove={handleApprove}
        onDelete={handleDelete}
      />

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <SummarySection summary={candidate.summary} onSave={handleSummarySave} />
        <ParsingStatusTimeline job={latestJob} onRetry={handleReprocess} />
      </div>

      <WorkHistoryTimeline items={candidate.work_history} />

      <div className="grid gap-6 lg:grid-cols-[1fr,1fr]">
        <EducationSection items={candidate.education} />
        <CertificationsSection items={candidate.certifications} />
      </div>

      <SkillsSection skills={candidate.skills} candidateSkills={candidate.candidate_skills} />

      <div className="space-y-3">
        <h2 className="text-xl font-semibold text-slate-900">
          Correction interface
        </h2>
        <CorrectionSplitView
          resumeUrl={resumeUrl}
          parsedData={parsedData}
          originalData={originalData}
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
        />
      </div>
    </section>
  )
}
