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
 *                       module_name:
 *                         type: string
 *                       action_name:
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

    // If user doesn't have roleId, return empty permissions (or fallback to legacy role check)
    if (!req.user.roleId) {
      // For backward compatibility, admin users get all permissions
      if (req.user.role === 'admin') {
        const allPermissionsResult = await query(
          "SELECT module_name, action_name FROM permissions ORDER BY module_name, action_name"
        );
        res.json({ permissions: allPermissionsResult.rows });
        return;
      }
      
      res.json({ permissions: [] });
      return;
    }

    const result = await query(
      `SELECT p.module_name, p.action_name
       FROM role_permissions rp
       JOIN permissions p ON rp.permission_id = p.id
       WHERE rp.role_id = $1
       ORDER BY p.module_name, p.action_name`,
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
 *                       module_name:
 *                         type: string
 *                       action_name:
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
      "SELECT id, module_name, action_name, description FROM permissions ORDER BY module_name, action_name"
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
 *                       module_name:
 *                         type: string
 *                       action_name:
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

    if (!roleId) {
      res.status(400).json({ error: "Bad Request", message: "Role ID is required" });
      return;
    }

    // Get role details
    const roleResult = await query(
      "SELECT id, name, description FROM roles WHERE id = $1",
      [roleId]
    );

    if (roleResult.rows.length === 0) {
      res.status(404).json({ error: "Not Found", message: "Role not found" });
      return;
    }

    // Get role permissions
    const permissionsResult = await query(
      `SELECT p.id, p.module_name, p.action_name, p.description, rp.granted_at
       FROM role_permissions rp
       JOIN permissions p ON rp.permission_id = p.id
       WHERE rp.role_id = $1
       ORDER BY p.module_name, p.action_name`,
      [roleId]
    );

    res.json({
      role: roleResult.rows[0],
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
 *                       module_name:
 *                         type: string
 *                       action_name:
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
    const { permissionIds } = req.body;

    if (!roleId) {
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

    // Verify role exists
    const roleResult = await query(
      "SELECT id, name FROM roles WHERE id = $1",
      [roleId]
    );

    if (roleResult.rows.length === 0) {
      res.status(404).json({ error: "Not Found", message: "Role not found" });
      return;
    }

    // Start transaction
    await query("BEGIN");

    try {
      // Delete existing role permissions
      await query(
        "DELETE FROM role_permissions WHERE role_id = $1",
        [roleId]
      );

      // Insert new role permissions if any provided
      if (permissionIds.length > 0) {
        const values = permissionIds.map((permissionId: string, index: number) => 
          `($1, $${index + 2}, NOW(), $${permissionIds.length + 2})`
        ).join(', ');

        const insertQuery = `
          INSERT INTO role_permissions (role_id, permission_id, granted_at, granted_by)
          VALUES ${values}
        `;

        const params = [roleId, ...permissionIds, req.user?.id];
        await query(insertQuery, params);
      }

      // Commit transaction
      await query("COMMIT");

      // Get updated permissions for response
      const updatedPermissionsResult = await query(
        `SELECT p.id, p.module_name, p.action_name
         FROM role_permissions rp
         JOIN permissions p ON rp.permission_id = p.id
         WHERE rp.role_id = $1
         ORDER BY p.module_name, p.action_name`,
        [roleId]
      );

      // Write audit log
      await writePermissionsAuditLog(
        req.user!.id,
        "UPDATE_ROLE_PERMISSIONS",
        {
          role_id: roleId,
          role_name: roleResult.rows[0].name,
          new_permissions: permissionIds,
          updated_by: req.user!.email,
        },
        req.ip
      );

      res.json({
        message: "Role permissions updated successfully",
        role: roleResult.rows[0],
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