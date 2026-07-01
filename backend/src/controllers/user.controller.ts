import { Request, Response } from "express";
import { getClient } from "../database/db";
import { authenticateToken } from "../middleware/auth.middleware";

interface TeamMember {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  active_assignment_count: number;
  team_lead_id: string | null;
}

// Get team members for a team lead
export const getMyTeam = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    const userRole = (req as any).user?.role;
    const tenantId = (req as any).user?.tenant_id || "default";

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
      });
      return;
    }

    // Only team leads and admins can access this endpoint
    if (userRole !== 'team_lead' && userRole !== 'admin') {
      res.status(403).json({
        error: "Forbidden",
        message: "Only team leads and admins can view team members",
      });
      return;
    }

    const client = await getClient();
    try {
      let query = `
        SELECT 
          u.id,
          u.email,
          u.role,
          u.is_active,
          u.team_lead_id,
          COALESCE(COUNT(DISTINCT jra.id), 0) as active_assignment_count
        FROM users u
        LEFT JOIN job_recruiter_assignments jra ON u.id = jra.recruiter_id
        WHERE u.tenant_id = $1
          AND u.role = 'recruiter'
      `;

      const params: any[] = [tenantId];
      let paramCount = 1;

      // Team leads can only see their own team members
      if (userRole === 'team_lead') {
        paramCount++;
        query += ` AND u.team_lead_id = $${paramCount}`;
        params.push(userId);
      }

      // Admins can see all recruiters (no additional filter needed)
      // If you want to restrict admins to specific teams, add logic here

      query += `
        GROUP BY u.id, u.email, u.role, u.is_active, u.team_lead_id
        ORDER BY u.email
      `;

      const result = await client.query(query, params);

      const teamMembers: TeamMember[] = result.rows.map(row => ({
        id: row.id,
        email: row.email,
        role: row.role,
        is_active: row.is_active,
        active_assignment_count: parseInt(row.active_assignment_count),
        team_lead_id: row.team_lead_id,
      }));

      res.json({
        team_members: teamMembers,
        count: teamMembers.length,
        user_role: userRole,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get my team error:", error);
    res.status(500).json({
      error: "Internal server error",
      message: "Failed to fetch team members",
    });
  }
};