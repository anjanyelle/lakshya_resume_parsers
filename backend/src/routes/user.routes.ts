import { Router } from "express";
import {
  getMyTeam,
} from "../controllers/user.controller";
import { authenticateToken } from "../middleware/auth.middleware";

const router = Router();

// Apply authentication middleware to all routes
router.use(authenticateToken);

/**
 * @swagger
 * /api/users/my-team:
 *   get:
 *     summary: Get team members for a team lead
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Team members retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 team_members:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       id:
 *                         type: string
 *                         format: uuid
 *                       email:
 *                         type: string
 *                       role:
 *                         type: string
 *                       is_active:
 *                         type: boolean
 *                       active_assignment_count:
 *                         type: integer
 *                         description: Number of active job assignments
 *                       team_lead_id:
 *                         type: string
 *                         format: uuid
 *                         nullable: true
 *                 count:
 *                   type: integer
 *                   description: Total number of team members
 *                 user_role:
 *                   type: string
 *                   description: Role of the requesting user
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Forbidden - User is not a team lead or admin
 *       500:
 *         description: Internal server error
 */
router.get("/my-team", getMyTeam);

export default router;