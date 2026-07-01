import { Request, Response } from "express";
import { query, getClient } from "../database/db";
import { AuthenticatedRequest } from "../middleware/auth.middleware";

// Helper function to write audit logs
const writePermissionsAuditLog = async (
  userId: string,
  action: string,
  details: any = null,
  ipAddress?: string
) => {
  const client = await getClient();
  try {
    await client.query(
      `INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, ip_address, details)
       VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [
        crypto.randomUUID(),
        userId,
        action,
        "role_permissions",
        details.role_id || "system",
        ipAddress,
        JSON.stringify(details),
      ]
    );
  } catch (error) {
    console.error("Failed to write audit log:", error);
  } finally {
    client.release();
  }
};

/**
 * @swagger
 * /api/permissions/me:
 *   get:
 *     summary: Get current user's permissions
 *     tags: [Permissions]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: User permissions retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 permissions:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       module:
 *                         type: string
 *                       name:
 *                         type: string
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Insufficient permissions
 *       500:
 *         description: Internal server error
 */
export const getUserPermissions = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    if (!req.user) {
      res.status(401).json({ error: "Authentication required" });
      return;
    }

    // If user doesn't have roleId, return permissions based on legacy role check
    if (!req.user.roleId) {
      // For backward compatibility, admin users get all permissions
      if (req.user.role === 'admin') {
        const allPermissionsResult = await query(
          "SELECT module, name FROM permissions ORDER BY module, name"
        );
        res.json({ permissions: allPermissionsResult.rows });
        return;
      }

      // Return default permissions for other roles based on their access
      const defaultPermissions: any[] = [];

      // Common permissions for all non-admin roles
      const commonModules = ['upload', 'matching', 'labeling', 'analytics', 'settings'];
      commonModules.forEach(module => {
        defaultPermissions.push({ module, name: 'view' });
      });

      // Role-specific permissions
      if (req.user.role === 'recruiter') {
        defaultPermissions.push({ module: 'candidates', name: 'view' });
        defaultPermissions.push({ module: 'jobs', name: 'view' });
        defaultPermissions.push({ module: 'dashboard', name: 'view' });
        defaultPermissions.push({ module: 'interviews', name: 'view_own' });
      } else if (req.user.role === 'team_lead') {
        defaultPermissions.push({ module: 'candidates', name: 'view' });
        defaultPermissions.push({ module: 'jobs', name: 'view' });
        defaultPermissions.push({ module: 'dashboard', name: 'view' });
        defaultPermissions.push({ module: 'requirements', name: 'view' });
        defaultPermissions.push({ module: 'interviews', name: 'view_own' });
      } else if (req.user.role === 'client_manager') {
        defaultPermissions.push({ module: 'clients', name: 'view_own' });
        defaultPermissions.push({ module: 'communications', name: 'view' });
        defaultPermissions.push({ module: 'dashboard', name: 'view' });
        defaultPermissions.push({ module: 'submissions', name: 'view_own_clients' });
        defaultPermissions.push({ module: 'interviews', name: 'view_own' });
      }

      res.json({ permissions: defaultPermissions });
      return;
    }

    const result = await query(
      `SELECT p.module, p.name
       FROM role_permissions rp
       JOIN permissions p ON rp.permission_id = p.id
       WHERE rp.role = $1
       ORDER BY p.module, p.name`,
      [req.user.roleId]
    );

    res.json({ permissions: result.rows });
  } catch (error) {
    console.error("Get user permissions error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve user permissions" });
  }
};

/**
 * @swagger
 * /api/permissions:
 *   get:
 *     summary: Get full permission catalog
 *     tags: [Permissions]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Permission catalog retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 permissions:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       id:
 *                         type: string
 *                         format: uuid
 *                       module:
 *                         type: string
 *                       name:
 *                         type: string
 *                       description:
 *                         type: string
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Internal server error
 */
export const getAllPermissions = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const result = await query(
      "SELECT id, module, name, description FROM permissions ORDER BY module, name"
    );

    res.json({ permissions: result.rows });
  } catch (error) {
    console.error("Get all permissions error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve permission catalog" });
  }
};

/**
 * @swagger
 * /api/role-permissions/{roleId}:
 *   get:
 *     summary: Get permissions for a specific role
 *     tags: [Permissions]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: roleId
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Role ID
 *     responses:
 *       200:
 *         description: Role permissions retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 role:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: string
 *                       format: uuid
 *                     name:
 *                       type: string
 *                     description:
 *                       type: string
 *                 permissions:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       id:
 *                         type: string
 *                         format: uuid
 *                       module:
 *                         type: string
 *                       name:
 *                         type: string
 *                       description:
 *                         type: string
 *                       granted_at:
 *                         type: string
 *                         format: date-time
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Insufficient permissions
 *       404:
 *         description: Role not found
 *       500:
 *         description: Internal server error
 */
export const getRolePermissions = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { roleId } = req.params;
    const roleIdString = Array.isArray(roleId) ? roleId[0] : roleId;

    if (!roleIdString) {
      res.status(400).json({ error: "Bad Request", message: "Role ID is required" });
      return;
    }

    // Since we're using string-based roles, create a mock role object
    const role = {
      id: roleIdString,
      name: roleIdString,
      description: `${roleIdString.charAt(0).toUpperCase() + roleIdString.slice(1)} role`
    };

    // Get role permissions - role_id in role_permissions table stores the role name as string
    const permissionsResult = await query(
      `SELECT p.id, p.module, p.name, p.description
       FROM role_permissions rp
       JOIN permissions p ON rp.permission_id = p.id
       WHERE rp.role = $1
       ORDER BY p.module, p.name`,
      [roleIdString]
    );

    res.json({
      role: role,
      permissions: permissionsResult.rows
    });
  } catch (error) {
    console.error("Get role permissions error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve role permissions" });
  }
};

/**
 * @swagger
 * /api/role-permissions/{roleId}:
 *   put:
 *     summary: Update permissions for a specific role
 *     tags: [Permissions]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: roleId
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Role ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - permissionIds
 *             properties:
 *               permissionIds:
 *                 type: array
 *                 items:
 *                   type: string
 *                   format: uuid
 *                 description: Array of permission IDs to assign to the role
 *     responses:
 *       200:
 *         description: Role permissions updated successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 *                 role:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: string
 *                       format: uuid
 *                     name:
 *                       type: string
 *                 permissions:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       id:
 *                         type: string
 *                         format: uuid
 *                       module:
 *                         type: string
 *                       name:
 *                         type: string
 *       400:
 *         description: Bad Request
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Insufficient permissions
 *       404:
 *         description: Role not found
 *       500:
 *         description: Internal server error
 */
export const updateRolePermissions = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const { roleId } = req.params;
    const roleIdString = Array.isArray(roleId) ? roleId[0] : roleId;
    const { permissionIds } = req.body;

    if (!roleIdString) {
      res.status(400).json({ error: "Bad Request", message: "Role ID is required" });
      return;
    }

    if (!Array.isArray(permissionIds)) {
      res.status(400).json({ error: "Bad Request", message: "permissionIds must be an array" });
      return;
    }

    // Validate that all permission IDs exist
    if (permissionIds.length > 0) {
      const validPermissionsResult = await query(
        "SELECT id FROM permissions WHERE id = ANY($1)",
        [permissionIds]
      );

      if (validPermissionsResult.rows.length !== permissionIds.length) {
        res.status(400).json({ error: "Bad Request", message: "One or more permission IDs are invalid" });
        return;
      }
    }

    // Since we're using string-based roles, verify the role is valid by checking if it exists in users table
    const validRoleResult = await query(
      "SELECT DISTINCT role FROM users WHERE role = $1 LIMIT 1",
      [roleIdString]
    );

    if (validRoleResult.rows.length === 0) {
      res.status(404).json({ error: "Not Found", message: "Role not found" });
      return;
    }

    // Start transaction
    await query("BEGIN");

    try {
      // Delete existing role permissions
      await query(
        "DELETE FROM role_permissions WHERE role = $1",
        [roleIdString]
      );

      // Insert new role permissions if any provided
      if (permissionIds.length > 0) {
        const values = permissionIds.map((permissionId: string, index: number) => 
          `($1, $${index + 2}, NOW())`
        ).join(', ');

        const insertQuery = `
          INSERT INTO role_permissions (role, permission_id, created_at)
          VALUES ${values}
        `;

        const params = [roleIdString, ...permissionIds];
        await query(insertQuery, params);
      }

      // Commit transaction
      await query("COMMIT");

      // Get updated permissions for response
      const updatedPermissionsResult = await query(
        `SELECT p.id, p.module, p.name
         FROM role_permissions rp
         JOIN permissions p ON rp.permission_id = p.id
         WHERE rp.role = $1
         ORDER BY p.module, p.name`,
        [roleIdString]
      );

      // Write audit log
      await writePermissionsAuditLog(
        req.user!.id,
        "UPDATE_ROLE_PERMISSIONS",
        {
          role_id: roleIdString,
          role_name: roleIdString,
          new_permissions: permissionIds,
          updated_by: req.user!.email,
        },
        req.ip
      );

      res.json({
        message: "Role permissions updated successfully",
        role: {
          id: roleIdString,
          name: roleIdString,
          description: `${roleIdString.charAt(0).toUpperCase() + roleIdString.slice(1)} role`
        },
        permissions: updatedPermissionsResult.rows
      });
    } catch (error) {
      // Rollback on error
      await query("ROLLBACK");
      throw error;
    }
  } catch (error) {
    console.error("Update role permissions error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to update role permissions" });
  }
};

export const getAllRoles = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    // Get unique roles from users table
    const result = await query(
      "SELECT DISTINCT role as name, role as id FROM users WHERE role IS NOT NULL ORDER BY role"
    );

    // Format roles for frontend
    const roles = result.rows.map((row: any) => ({
      id: row.id,
      name: row.name,
      description: `${row.name.charAt(0).toUpperCase() + row.name.slice(1)} role`
    }));

    res.json({ roles });
  } catch (error) {
    console.error("Get all roles error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve roles" });
  }
};