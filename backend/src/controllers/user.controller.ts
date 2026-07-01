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

interface User {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  tenant_id: string;
  created_at: string;
}

// Get all users with pagination
export const getAllUsers = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const skip = parseInt(req.query.skip as string) || 0;
    const limit = parseInt(req.query.limit as string) || 20;
    const userRole = (req as any).user?.role;

    // Only admins can view all users
    if (userRole !== 'admin') {
      res.status(403).json({
        error: "Forbidden",
        message: "Only admins can view all users",
      });
      return;
    }

    const client = await getClient();
    try {
      // Get total count
      const countResult = await client.query("SELECT COUNT(*) as total FROM users");
      const total = parseInt(countResult.rows[0].total);

      // Get paginated users
      const result = await client.query(
        `SELECT id, email, role, is_active, tenant_id, created_at
         FROM users
         ORDER BY created_at DESC
         LIMIT $1 OFFSET $2`,
        [limit, skip]
      );

      const users: User[] = result.rows.map(row => ({
        id: row.id,
        email: row.email,
        role: row.role,
        is_active: row.is_active,
        tenant_id: row.tenant_id,
        created_at: row.created_at,
      }));

      res.json({
        users,
        total,
        skip,
        limit,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get all users error:", error);
    res.status(500).json({
      error: "Internal server error",
      message: "Failed to fetch users",
    });
  }
};

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

// Update user role
export const updateUserRole = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const { id } = req.params;
    const { role } = req.body;
    const userRole = (req as any).user?.role;

    // Only admins can update user roles
    if (userRole !== 'admin') {
      res.status(403).json({
        error: "Forbidden",
        message: "Only admins can update user roles",
      });
      return;
    }

    const client = await getClient();
    try {
      const result = await client.query(
        "UPDATE users SET role = $1 WHERE id = $2 RETURNING id, email, role",
        [role, id]
      );

      if (result.rows.length === 0) {
        res.status(404).json({ error: "User not found" });
        return;
      }

      res.json({
        message: "User role updated successfully",
        user: result.rows[0],
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Update user role error:", error);
    res.status(500).json({
      error: "Internal server error",
      message: "Failed to update user role",
    });
  }
};

// Activate user
export const activateUser = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const { id } = req.params;
    const userRole = (req as any).user?.role;

    // Only admins can activate users
    if (userRole !== 'admin') {
      res.status(403).json({
        error: "Forbidden",
        message: "Only admins can activate users",
      });
      return;
    }

    const client = await getClient();
    try {
      const result = await client.query(
        "UPDATE users SET is_active = true WHERE id = $1 RETURNING id, email, is_active",
        [id]
      );

      if (result.rows.length === 0) {
        res.status(404).json({ error: "User not found" });
        return;
      }

      res.json({
        message: "User activated successfully",
        user: result.rows[0],
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Activate user error:", error);
    res.status(500).json({
      error: "Internal server error",
      message: "Failed to activate user",
    });
  }
};

// Deactivate user
export const deactivateUser = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const { id } = req.params;
    const userRole = (req as any).user?.role;

    // Only admins can deactivate users
    if (userRole !== 'admin') {
      res.status(403).json({
        error: "Forbidden",
        message: "Only admins can deactivate users",
      });
      return;
    }

    const client = await getClient();
    try {
      const result = await client.query(
        "UPDATE users SET is_active = false WHERE id = $1 RETURNING id, email, is_active",
        [id]
      );

      if (result.rows.length === 0) {
        res.status(404).json({ error: "User not found" });
        return;
      }

      res.json({
        message: "User deactivated successfully",
        user: result.rows[0],
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Deactivate user error:", error);
    res.status(500).json({
      error: "Internal server error",
      message: "Failed to deactivate user",
    });
  }
};