import { Router } from 'express'
import { 
  createCandidate, 
  getAllCandidates, 
  getCandidateById, 
  updateCandidate, 
  deleteCandidate, 
  getCandidateParsingStatus 
} from '../controllers/candidate.controller'
import { authenticateToken, requireRole } from '../middleware/auth.middleware'

const router = Router()

// All candidate routes require authentication
router.use(authenticateToken)

/**
 * @swagger
 * /api/candidates:
 *   post:
 *     summary: Create a new candidate
 *     tags: [Candidates]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               full_name:
 *                 type: string
 *               email:
 *                 type: string
 *                 format: email
 *               phone:
 *                 type: string
 *               location:
 *                 type: string
 *               linkedin_url:
 *                 type: string
 *                 format: uri
 *               github_url:
 *                 type: string
 *                 format: uri
 *               summary:
 *                 type: string
 *               raw_resume_text:
 *                 type: string
 *               file_path:
 *                 type: string
 *               file_type:
 *                 type: string
 *                 enum: [pdf, docx, txt, image]
 *     responses:
 *       201:
 *         description: Candidate created successfully
 *       400:
 *         description: Bad request
 *       401:
 *         description: Unauthorized
 */
router.post('/', createCandidate)

/**
 * @swagger
 * /api/candidates:
 *   get:
 *     summary: Get all candidates with pagination and search
 *     tags: [Candidates]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: Page number
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *           maximum: 100
 *         description: Number of items per page
 *       - in: query
 *         name: search
 *         schema:
 *           type: string
 *         description: Search in full_name, email, or location
 *     responses:
 *       200:
 *         description: Candidates retrieved successfully
 *       401:
 *         description: Unauthorized
 */
router.get('/', getAllCandidates)

/**
 * @swagger
 * /api/candidates/{id}:
 *   get:
 *     summary: Get a specific candidate with all details
 *     tags: [Candidates]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Candidate ID
 *     responses:
 *       200:
 *         description: Candidate retrieved successfully
 *       404:
 *         description: Candidate not found
 *       401:
 *         description: Unauthorized
 */
router.get('/:id', getCandidateById)

/**
 * @swagger
 * /api/candidates/{id}:
 *   put:
 *     summary: Update a candidate
 *     tags: [Candidates]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Candidate ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               full_name:
 *                 type: string
 *               email:
 *                 type: string
 *                 format: email
 *               phone:
 *                 type: string
 *               location:
 *                 type: string
 *               linkedin_url:
 *                 type: string
 *                 format: uri
 *               github_url:
 *                 type: string
 *                 format: uri
 *               summary:
 *                 type: string
 *     responses:
 *       200:
 *         description: Candidate updated successfully
 *       400:
 *         description: Bad request
 *       404:
 *         description: Candidate not found
 *       401:
 *         description: Unauthorized
 */
router.put('/:id', updateCandidate)

/**
 * @swagger
 * /api/candidates/{id}:
 *   delete:
 *     summary: Soft delete a candidate
 *     tags: [Candidates]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Candidate ID
 *     responses:
 *       200:
 *         description: Candidate deleted successfully
 *       404:
 *         description: Candidate not found
 *       401:
 *         description: Unauthorized
 */
router.delete('/:id', deleteCandidate)

/**
 * @swagger
 * /api/candidates/{id}/parsing-status:
 *   get:
 *     summary: Get parsing status for a candidate
 *     tags: [Candidates]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Candidate ID
 *     responses:
 *       200:
 *         description: Parsing status retrieved successfully
 *       404:
 *         description: No parsing job found
 *       401:
 *         description: Unauthorized
 */
router.get('/:id/parsing-status', getCandidateParsingStatus)

export default router
