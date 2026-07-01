import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { Request, Response } from "express";
import { query } from "../database/db";
import { v4 as uuidv4 } from "uuid";

interface RegisterRequest {
  email: string;
  password: string;
  role?: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

export const registerUser = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const { email, password, role = "recruiter" }: RegisterRequest = req.body;

    // Validate input
    if (!email || !password) {
      res.status(400).json({ error: "Email and password are required" });
      return;
    }

    // Check if user already exists
    const existingUser = await query("SELECT id FROM users WHERE email = $1", [
      email,
    ]);

    if (existingUser.rows.length > 0) {
      res.status(409).json({ error: "User with this email already exists" });
      return;
    }

    // Hash password
    const saltRounds = 12;
    const passwordHash = await bcrypt.hash(password, saltRounds);

    // Create user
    const id = uuidv4();
    const result = await query(
      `INSERT INTO users (id, email, hashed_password, role, is_active, tenant_id, created_at) 
       VALUES ($1, $2, $3, $4, $5, $6, $7) 
       RETURNING id, email, role, created_at`,
      [id, email, passwordHash, role, true, "default", new Date()],
    );

    const user = result.rows[0];

    // Get role information from roles table
    let roleId = null;
    let roleName = user.role;
    
    try {
      const roleResult = await query(
        "SELECT id, name FROM roles WHERE name = $1",
        [user.role]
      );
      
      if (roleResult.rows.length > 0) {
        roleId = roleResult.rows[0].id;
        roleName = roleResult.rows[0].name;
      }
    } catch (error) {
      console.error("Error fetching role information:", error);
      // Continue with default role if role lookup fails
    }

    // Generate JWT token with enhanced role information
    const token = jwt.sign(
      { 
        id: user.id, 
        email: user.email, 
        role: user.role,        // Legacy role for backward compatibility
        roleId: roleId,         // New role UUID
        roleName: roleName      // New role name
      },
      process.env.JWT_SECRET || "fallback-secret",
      { expiresIn: "24h" },
    );

    res.status(201).json({
      message: "User registered successfully",
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        created_at: user.created_at,
      },
      token,
    });
  } catch (error: any) {
    console.error("Registration error:", error);
    res.status(500).json({ error: "Internal server error", details: error?.message || String(error) });
  }
};

export const loginUser = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password }: LoginRequest = req.body;

    // Validate input
    if (!email || !password) {
      res.status(400).json({ error: "Email and password are required" });
      return;
    }

    // Find user with role information
    const result = await query(
      `SELECT u.id, u.email, u.hashed_password, u.role, u.created_at, u.role_id, r.name as role_name
       FROM users u 
       LEFT JOIN roles r ON u.role_id = r.id 
       WHERE u.email = $1`,
      [email],
    );

    if (result.rows.length === 0) {
      res.status(401).json({ error: "Invalid email or password" });
      return;
    }

    const user = result.rows[0];

    // Verify password
    const isPasswordValid = await bcrypt.compare(
      password,
      user.hashed_password,
    );

    if (!isPasswordValid) {
      res.status(401).json({ error: "Invalid email or password" });
      return;
    }

    // Generate JWT token with enhanced role information
    const token = jwt.sign(
      { 
        id: user.id, 
        email: user.email, 
        role: user.role,        // Legacy role for backward compatibility
        roleId: user.role_id,   // New role UUID
        roleName: user.role_name || user.role  // New role name
      },
      process.env.JWT_SECRET || "fallback-secret",
      { expiresIn: "24h" },
    );

    res.json({
      message: "Login successful",
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        created_at: user.created_at,
      },
      token,
    });
  } catch (error) {
    console.error("Login error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};

export const getMe = async (
  req: Request & { user?: any },
  res: Response,
): Promise<void> => {
  try {
    if (!req.user) {
      res.status(401).json({ error: "Authentication required" });
      return;
    }

    const result = await query(
      "SELECT id, email, role, created_at FROM users WHERE id = $1",
      [req.user.id],
    );

    if (result.rows.length === 0) {
      res.status(404).json({ error: "User not found" });
      return;
    }

    const user = result.rows[0];

    res.json({
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        created_at: user.created_at,
      },
    });
  } catch (error) {
    console.error("Get user error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};
