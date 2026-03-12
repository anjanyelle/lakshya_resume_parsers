import { create } from 'zustand'
import { api } from '../services/api'
import toast from 'react-hot-toast'

interface Candidate {
  id: string
  full_name: string
  email: string
  phone?: string
  location?: string
  linkedin_url?: string
  github_url?: string
  summary?: string
  raw_resume_text?: string
  created_at: string
  updated_at: string
  skills?: Array<{
    id: string
    skill_name: string
    category: string
    proficiency_level: string
    years_experience?: number
    confidence_score?: number
  }>
  work_experience?: Array<{
    id: string
    job_title: string
    company_name: string
    start_date: string
    end_date?: string
    is_current: boolean
    description?: string
    location?: string
  }>
  education?: Array<{
    id: string
    degree: string
    institution: string
    field_of_study?: string
    start_date?: string
    end_date?: string
    gpa?: number
  }>
  parsing_status?: {
    status: string
    progress?: number
    confidence_score?: number
    error_message?: string
  }
}

interface CandidateState {
  candidates: Candidate[]
  currentCandidate: Candidate | null
  isLoading: boolean
  uploadProgress: number
  isUploading: boolean
  error: string | null
}

interface CandidateActions {
  fetchCandidates: () => Promise<void>
  fetchCandidate: (id: string) => Promise<void>
  uploadResume: (file: File, candidateId?: string) => Promise<Candidate>
  deleteCandidate: (id: string) => Promise<void>
  setUploadProgress: (percent: number) => void
  setCurrentCandidate: (candidate: Candidate | null) => void
  clearError: () => void
  updateCandidateStatus: (candidateId: string, status: any) => void
}

export const useCandidateStore = create<CandidateState & CandidateActions>((set) => ({
  // Initial state
  candidates: [],
  currentCandidate: null,
  isLoading: false,
  uploadProgress: 0,
  isUploading: false,
  error: null,

  // Actions
  fetchCandidates: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get('/candidates')
      set({ candidates: response.data.candidates, isLoading: false })
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch candidates'
      set({ error: errorMessage, isLoading: false })
      toast.error(errorMessage)
    }
  },

  fetchCandidate: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get(`/candidates/${id}`)
      set({ currentCandidate: response.data.candidate, isLoading: false })
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to fetch candidate'
      set({ error: errorMessage, isLoading: false })
      toast.error(errorMessage)
    }
  },

  uploadResume: async (file: File, candidateId?: string) => {
    set({ isUploading: true, uploadProgress: 0, error: null })
    
    try {
      const formData = new FormData()
      formData.append('resume', file)
      if (candidateId) {
        formData.append('candidate_id', candidateId)
      }

      const response = await api.post('/upload/resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            set({ uploadProgress: progress })
          }
        },
      })

      const newCandidate: Candidate = {
        id: response.data.data.candidateId,
        full_name: 'Processing...',
        email: 'processing@resume.com',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      // Update candidates list
      set((state) => ({
        candidates: candidateId 
          ? state.candidates.map(c => c.id === candidateId ? newCandidate : c)
          : [...state.candidates, newCandidate],
        isUploading: false,
        uploadProgress: 100,
      }))

      toast.success(candidateId ? 'Resume updated successfully' : 'Resume uploaded successfully')
      return newCandidate
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to upload resume'
      set({ error: errorMessage, isUploading: false, uploadProgress: 0 })
      toast.error(errorMessage)
      throw error
    }
  },

  deleteCandidate: async (id: string) => {
    try {
      await api.delete(`/candidates/${id}`)
      set((state) => ({
        candidates: state.candidates.filter(c => c.id !== id),
        currentCandidate: state.currentCandidate?.id === id ? null : state.currentCandidate,
      }))
      toast.success('Candidate deleted successfully')
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Failed to delete candidate'
      set({ error: errorMessage })
      toast.error(errorMessage)
      throw error
    }
  },

  setUploadProgress: (percent: number) => {
    set({ uploadProgress: percent })
  },

  setCurrentCandidate: (candidate: Candidate | null) => {
    set({ currentCandidate: candidate })
  },

  clearError: () => {
    set({ error: null })
  },

  updateCandidateStatus: (candidateId: string, status: any) => {
    set((state) => ({
      candidates: state.candidates.map(candidate =>
        candidate.id === candidateId
          ? { ...candidate, parsing_status: status }
          : candidate
      ),
      currentCandidate: state.currentCandidate?.id === candidateId
        ? { ...state.currentCandidate, parsing_status: status }
        : state.currentCandidate,
    }))
  },
}))
