import { Router } from 'express'
import { 
  matchCandidatesToJob, 
  getMatchResultsForJob, 
  matchSingleCandidate 
} from '../controllers/matching.controller'

const router = Router()

/**
 * Matching Routes
 * Endpoints for candidate-job matching operations
 */

// POST /api/matching/job/:jobId/candidates
// Match all candidates to a specific job
router.post('/job/:jobId/candidates', matchCandidatesToJob)

// GET /api/matching/job/:jobId/results
// Get cached match results for a specific job
router.get('/job/:jobId/results', getMatchResultsForJob)

// POST /api/matching/candidate/:candidateId/job/:jobId
// Match a single candidate to a specific job
router.post('/candidate/:candidateId/job/:jobId', matchSingleCandidate)

export default router
