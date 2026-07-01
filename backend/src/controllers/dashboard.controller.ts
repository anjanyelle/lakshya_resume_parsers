import { Request, Response } from "express";
import { getClient } from "../database/db";
import { authenticateToken, requirePermission } from "../middleware/auth.middleware";

interface RecruiterSummary {
  assignedRequirementsCount: number;
  activeSubmissionsCount: number;
  upcomingInterviews: Array<{
    id: string;
    round_name: string;
    scheduled_at: string;
    mode: string;
    status: string;
    job_title?: string;
    job_company?: string;
    candidate_name?: string;
    candidate_email?: string;
  }>;
  dailyTarget: number;
}

interface ClientManagerSummary {
  assignedClientsCount: number;
  openRequirementsCount: number;
  pendingFeedbackCount: number;
  followUpsDueCount: number;
}

// Get recruiter summary for dashboard
export const getRecruiterSummary = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    const tenantId = (req as any).user?.tenant_id || "default";

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
        code: "USER_ID_REQUIRED"
      });
      return;
    }

    const client = await getClient();
    try {
      // Get assigned requirements count
      const requirementsQuery = `
        SELECT COUNT(*) as count 
        FROM job_recruiter_assignments jra
        JOIN job_descriptions jd ON jra.job_id = jd.id
        WHERE jra.recruiter_id = $1 AND jd.tenant_id = $2
      `;
      const requirementsResult = await client.query(requirementsQuery, [userId, tenantId]);
      const assignedRequirementsCount = parseInt(requirementsResult.rows[0].count);

      // Get active submissions count (status not in Rejected/Offer Accepted)
      const submissionsQuery = `
        SELECT COUNT(*) as count 
        FROM submissions 
        WHERE submitted_by = $1 
        AND tenant_id = $2 
        AND status NOT IN ('rejected', 'offer_accepted', 'offer_declined')
      `;
      const submissionsResult = await client.query(submissionsQuery, [userId, tenantId]);
      const activeSubmissionsCount = parseInt(submissionsResult.rows[0].count);

      // Get upcoming interviews (next 5)
      const interviewsQuery = `
        SELECT 
          i.id,
          i.round_name,
          i.scheduled_at,
          i.mode,
          i.status,
          j.title as job_title,
          j.company as job_company,
          c.full_name as candidate_name,
          c.email as candidate_email
        FROM interviews i
        JOIN submissions s ON i.submission_id = s.id
        LEFT JOIN job_descriptions j ON s.job_id = j.id
        LEFT JOIN candidates c ON s.candidate_id = c.id
        WHERE (i.scheduled_by = $1 OR s.submitted_by = $1)
        AND i.tenant_id = $2 
        AND i.scheduled_at > NOW() 
        AND i.status = 'scheduled'
        ORDER BY i.scheduled_at ASC
        LIMIT 5
      `;
      const interviewsResult = await client.query(interviewsQuery, [userId, tenantId]);
      const upcomingInterviews = interviewsResult.rows;

      // Hardcoded daily target (placeholder for future targets system)
      const dailyTarget = 5;

      const summary: RecruiterSummary = {
        assignedRequirementsCount,
        activeSubmissionsCount,
        upcomingInterviews,
        dailyTarget
      };

      res.json(summary);

    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get recruiter summary error:", error);
    res.status(500).json({
      error: "Internal Server Error",
      message: "Failed to fetch recruiter summary",
      code: "GET_RECRUITER_SUMMARY_FAILED"
    });
  }
};

// Get team lead summary for dashboard
export const getTeamLeadSummary = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    const tenantId = (req as any).user?.tenant_id || "default";

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
        code: "USER_ID_REQUIRED"
      });
      return;
    }

    const client = await getClient();
    try {
      // Get team size (count of recruiters under req.user.id)
      const teamSizeQuery = `
        SELECT COUNT(*) as count 
        FROM users 
        WHERE team_lead_id = $1 
        AND tenant_id = $2 
        AND role = 'recruiter'
      `;
      const teamSizeResult = await client.query(teamSizeQuery, [userId, tenantId]);
      const teamSize = parseInt(teamSizeResult.rows[0].count);

      // Get open requirements count (requirements assigned to the team, status not closed)
      const openRequirementsQuery = `
        SELECT COUNT(DISTINCT jd.id) as count 
        FROM job_descriptions jd
        JOIN job_recruiter_assignments jra ON jd.id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
        AND jd.tenant_id = $2 
        AND jd.status != 'closed'
      `;
      const openRequirementsResult = await client.query(openRequirementsQuery, [userId, tenantId]);
      const openRequirementsCount = parseInt(openRequirementsResult.rows[0].count);

      // Get pending reviews count (reuse the Prompt 6 query, just return the count)
      const pendingReviewsQuery = `
        SELECT COUNT(*) as count 
        FROM submissions s
        JOIN job_descriptions jd ON s.job_id = jd.id
        JOIN job_recruiter_assignments jra ON jd.id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
        AND s.tenant_id = $2
        AND NOT EXISTS (
          SELECT 1 FROM submission_reviews sr 
          WHERE sr.submission_id = s.id
        )
      `;
      const pendingReviewsResult = await client.query(pendingReviewsQuery, [userId, tenantId]);
      const pendingReviewsCount = parseInt(pendingReviewsResult.rows[0].count);

      // Get monthly closures count (submissions that reached 'Offer Accepted' status this month)
      const monthlyClosuresQuery = `
        SELECT COUNT(*) as count 
        FROM submissions s
        JOIN job_recruiter_assignments jra ON s.job_id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
        AND s.tenant_id = $2
        AND s.status = 'Offer Accepted'
        AND EXTRACT(MONTH FROM s.updated_at) = EXTRACT(MONTH FROM NOW())
        AND EXTRACT(YEAR FROM s.updated_at) = EXTRACT(YEAR FROM NOW())
      `;
      const monthlyClosuresResult = await client.query(monthlyClosuresQuery, [userId, tenantId]);
      const monthlyClosuresCount = parseInt(monthlyClosuresResult.rows[0].count);

      const summary = {
        teamSize,
        openRequirementsCount,
        pendingReviewsCount,
        monthlyClosuresCount
      };

      res.json(summary);

    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get team lead summary error:", error);
    res.status(500).json({
      error: "Internal Server Error",
      message: "Failed to fetch team lead summary",
      code: "GET_TEAM_LEAD_SUMMARY_FAILED"
    });
  }
};

// Get client manager summary for dashboard
export const getClientManagerSummary = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    const tenantId = (req as any).user?.tenant_id || "default";

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
        code: "USER_ID_REQUIRED"
      });
      return;
    }

    const client = await getClient();
    try {
      // Get assigned clients count (clients where owner_user_id = req.user.id)
      const assignedClientsQuery = `
        SELECT COUNT(*) as count 
        FROM clients 
        WHERE owner_user_id = $1 
        AND tenant_id = $2
        AND is_archived = false
      `;
      const assignedClientsResult = await client.query(assignedClientsQuery, [userId, tenantId]);
      const assignedClientsCount = parseInt(assignedClientsResult.rows[0].count);

      // Get open requirements count (requirements for owned clients, status not closed)
      const openRequirementsQuery = `
        SELECT COUNT(*) as count 
        FROM job_descriptions jd
        JOIN clients c ON jd.client_id = c.id
        WHERE c.owner_user_id = $1 
        AND jd.tenant_id = $2 
        AND jd.status != 'closed'
      `;
      const openRequirementsResult = await client.query(openRequirementsQuery, [userId, tenantId]);
      const openRequirementsCount = parseInt(openRequirementsResult.rows[0].count);

      // Get pending feedback count (submissions with status "Shortlisted" - awaiting client decision)
      const pendingFeedbackQuery = `
        SELECT COUNT(*) as count 
        FROM submissions s
        JOIN job_descriptions jd ON s.job_id = jd.id
        JOIN clients c ON jd.client_id = c.id
        WHERE c.owner_user_id = $1 
        AND s.tenant_id = $2
        AND s.status = 'Shortlisted'
      `;
      const pendingFeedbackResult = await client.query(pendingFeedbackQuery, [userId, tenantId]);
      const pendingFeedbackCount = parseInt(pendingFeedbackResult.rows[0].count);

      // Get follow-ups due count (reuse Prompt 9's query, count only)
      const followUpsDueQuery = `
        SELECT COUNT(*) as count
        FROM client_communications cc
        JOIN clients c ON cc.client_id = c.id
        WHERE cc.tenant_id = $1
          AND cc.follow_up_date IS NOT NULL
          AND cc.follow_up_date <= NOW()
          AND cc.logged_by = $2
      `;
      const followUpsDueResult = await client.query(followUpsDueQuery, [tenantId, userId]);
      const followUpsDueCount = parseInt(followUpsDueResult.rows[0].count);

      const summary: ClientManagerSummary = {
        assignedClientsCount,
        openRequirementsCount,
        pendingFeedbackCount,
        followUpsDueCount
      };

      res.json(summary);

    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get client manager summary error:", error);
    res.status(500).json({
      error: "Internal Server Error",
      message: "Failed to fetch client manager summary",
      code: "GET_CLIENT_MANAGER_SUMMARY_FAILED"
    });
  }
};