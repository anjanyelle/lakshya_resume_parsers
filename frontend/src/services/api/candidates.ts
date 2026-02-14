import { apiClient } from './client'
import type { Candidate, ParsingJob } from '../../types/candidate'

export const fetchCandidates = async (signal?: AbortSignal) => {
  const response = await apiClient.get<Candidate[]>('/api/v1/candidates', {
    signal,
  })
  return response.data
}

export const fetchCandidate = async (id: string) => {
  const response = await apiClient.get<Candidate>(`/api/v1/candidates/${id}`)
  return response.data
}

export const fetchCandidateReview = async (id: string) => {
  const response = await apiClient.get<{
    candidate: Candidate
    latest_job: ParsingJob | null
    review_flags: {
      overall_confidence: number | null
      flagged_fields: Record<string, number>
      discrepancies: string[]
    }
    suggested_corrections?: Record<string, string>
  }>(`/api/v1/candidates/${id}/review`)
  return response.data
}

export const submitCorrections = async (
  id: string,
  corrections: Array<{
    field_name: string
    original_value?: string | null
    corrected_value?: string | null
  }>,
  reviewNotes?: string,
) => {
  const response = await apiClient.put<Candidate>(
    `/api/v1/candidates/${id}/corrections`,
    {
      corrections,
      review_notes: reviewNotes,
    },
  )
  return response.data
}

export const approveCandidate = async (id: string) => {
  const response = await apiClient.post<Candidate>(
    `/api/v1/candidates/${id}/approve`,
  )
  return response.data
}

export const reprocessCandidate = async (id: string) => {
  const response = await apiClient.post(`/api/v1/candidates/${id}/reprocess`)
  return response.data as { job_id: string; status: string }
}

export const downloadResume = async (id: string) => {
  const response = await apiClient.get<{ download_url: string }>(
    `/api/v1/candidates/${id}/resume`,
  )
  return response.data.download_url
}

export const exportCandidateJson = async (id: string) => {
  const response = await apiClient.get(`/api/v1/gdpr/export/${id}`)
  return response.data as Record<string, unknown>
}

export const deleteCandidate = async (id: string) => {
  await apiClient.delete(`/api/v1/candidates/${id}`)
}
