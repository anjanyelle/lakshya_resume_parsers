import jwt from "jsonwebtoken";
import { Request, Response, NextFunction } from "express";
import { query } from "../database/db";

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;        // Legacy role for backward compatibility
    roleId?: string;     // New role UUID
    roleName?: string;   // New role name
  };
}

type AuthRequest = AuthenticatedRequest;

export const authenticateToken = (
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): void => {
  const authHeader = req.headers["authorization"];
  const token = authHeader && authHeader.split(" ")[1]; // Bearer TOKEN

  if (!token) {
    res.status(401).json({ error: "Access token required" });
    return;
  }

  jwt.verify(
    token,
    process.env.JWT_SECRET || "fallback-secret",
    (err, decoded) => {
      if (err) {
        res.status(403).json({ error: "Invalid or expired token" });
        return;
      }

      req.user = {
        id: (decoded as any).id,
        email: (decoded as any).email,
        role: (decoded as any).role,
        roleId: (decoded as any).roleId,
        roleName: (decoded as any).roleName,
      };
      next();
    },
  );
};

export const requireRole = (roles: string[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({ error: "Authentication required" });
      return;
    }

    if (!roles.includes(req.user.role)) {
      res.status(403).json({ error: "Insufficient permissions" });
      return;
    }

    next();
  };
};

export const requirePermission = (moduleName: string, actionName: string) => {
  return async (req: AuthRequest, res: Response, next: NextFunction): Promise<void> => {
    if (!req.user) {
      res.status(401).json({ error: "Authentication required" });
      return;
    }

    // If user doesn't have roleId, fall back to legacy role check
    if (!req.user.roleId) {
      // For backward compatibility, allow admin users to access everything
      if (req.user.role === 'admin') {
        return next();
      }
      
      // For other users without roleId, deny access to permission-protected routes
      res.status(403).json({ error: "Insufficient permissions - role not assigned" });
      return;
    }

    try {
      // Check if the user's role has the required permission
      const permissionCheck = await query(
        `SELECT 1 
         FROM role_permissions rp
         JOIN permissions p ON rp.permission_id = p.id
         WHERE rp.role_id = $1 
         AND p.module_name = $2 
         AND p.action_name = $3`,
        [req.user.roleId, moduleName, actionName]
      );

      if (permissionCheck.rows.length === 0) {
        res.status(403).json({ 
          error: "Insufficient permissions",
          details: `Missing permission: ${moduleName}.${actionName}`
        });
        return;
      }

      next();
    } catch (error) {
      console.error("Permission check error:", error);
      res.status(500).json({ error: "Internal server error during permission check" });
    }
  };
};
