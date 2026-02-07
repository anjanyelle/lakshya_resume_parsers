import { apiClient } from './client'

export const uploadResume = async (
  file: File,
  onProgress?: (progress: number) => void,
) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await apiClient.post('/api/v1/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (!event.total) return
      const progress = Math.round((event.loaded / event.total) * 100)
      onProgress?.(progress)
    },
  })
  const job = response.data.jobs?.[0]
  return job?.job_id as string
}

export const fetchJobStatus = async (jobId: string) => {
  const response = await apiClient.get<{ status: string }>(
    `/api/v1/jobs/${jobId}/status`,
  )
  return response.data.status
}
