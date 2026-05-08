import { Pool } from "pg";
import { getClient } from "../database/db";

export interface Candidate {
  id: string;
  email?: string;
  phone?: string;
  name?: string;
  status?: string;
  resume_path?: string;
  created_at?: Date;
  updated_at?: Date;
}

export interface CandidateWithDetails extends Candidate {
  work_history?: any[];
  education?: any[];
  certifications?: any[];
  skills?: any[];
}

export class CandidateModel {
  static async findById(id: string): Promise<CandidateWithDetails | null> {
    const client = await getClient();
    try {
      const result = await client.query(
        "SELECT * FROM candidates WHERE id = $1",
        [id]
      );
      return result.rows[0] || null;
    } finally {
      client.release();
    }
  }

  static async findByIdWithDetails(client: any, id: string): Promise<CandidateWithDetails | null> {
    try {
      const candidateResult = await client.query(
        "SELECT * FROM candidates WHERE id = $1",
        [id]
      );
      
      if (candidateResult.rows.length === 0) {
        return null;
      }
      
      const candidate = candidateResult.rows[0];
      
      const workHistoryResult = await client.query(
        "SELECT * FROM work_history WHERE candidate_id = $1 ORDER BY start_date DESC",
        [id]
      );
      
      const educationResult = await client.query(
        "SELECT * FROM education WHERE candidate_id = $1 ORDER BY end_date DESC",
        [id]
      );
      
      const certificationsResult = await client.query(
        "SELECT * FROM certifications WHERE candidate_id = $1 ORDER BY issue_date DESC",
        [id]
      );
      
      const skillsResult = await client.query(
        `SELECT s.*, cs.proficiency_level, cs.years_experience 
         FROM skills s 
         JOIN candidate_skills cs ON s.id = cs.skill_id 
         WHERE cs.candidate_id = $1`,
        [id]
      );
      
      return {
        ...candidate,
        work_history: workHistoryResult.rows,
        education: educationResult.rows,
        certifications: certificationsResult.rows,
        skills: skillsResult.rows
      };
    } catch (error) {
      console.error("Error fetching candidate with details:", error);
      throw error;
    }
  }

  static async create(client: any, data: any): Promise<any> {
    const {
      full_name, email, phone, location, linkedin_url, github_url, summary,
      file_path, file_type
    } = data;
    
    const result = await client.query(
      `INSERT INTO candidates (
        full_name, email, phone, location, linkedin_url, github_url, 
        summary, file_path, file_type, status, created_at, updated_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'pending', NOW(), NOW())
      RETURNING *`,
      [full_name, email, phone, location, linkedin_url, github_url, summary, file_path, file_type]
    );
    return result.rows[0];
  }

  static async update(client: any, id: string, data: any): Promise<any> {
    const { full_name, email, phone, location, linkedin_url, github_url, summary } = data;
    
    const result = await client.query(
      `UPDATE candidates SET 
        full_name = COALESCE($1, full_name),
        email = COALESCE($2, email),
        phone = COALESCE($3, phone),
        location = COALESCE($4, location),
        linkedin_url = COALESCE($5, linkedin_url),
        github_url = COALESCE($6, github_url),
        summary = COALESCE($7, summary),
        updated_at = NOW()
      WHERE id = $8 RETURNING *`,
      [full_name, email, phone, location, linkedin_url, github_url, summary, id]
    );
    return result.rows[0] || null;
  }

  static async softDelete(client: any, id: string): Promise<boolean> {
    const result = await client.query(
      "UPDATE candidates SET status = 'deleted', updated_at = NOW() WHERE id = $1",
      [id]
    );
    return (result.rowCount ?? 0) > 0;
  }

  static async getParsingStatus(client: any, id: string): Promise<any> {
    const result = await client.query(
      "SELECT * FROM parsing_jobs WHERE candidate_id = $1 ORDER BY created_at DESC LIMIT 1",
      [id]
    );
    return result.rows[0] || null;
  }

  static async findAll(
    client: any,
    page: number = 1,
    limit: number = 20,
    search?: string
  ): Promise<{ candidates: any[]; total: number }> {
    try {
      const offset = (page - 1) * limit;
      let whereClause = "WHERE status != 'deleted'";
      const queryParams: any[] = [];
      
      if (search) {
        queryParams.push(`%${search}%`);
        whereClause += ` AND (full_name ILIKE $${queryParams.length} OR email ILIKE $${queryParams.length})`;
      }
      
      const countQuery = `SELECT COUNT(*) FROM candidates ${whereClause}`;
      const countResult = await client.query(countQuery, queryParams);
      const total = parseInt(countResult.rows[0].count);
      
      queryParams.push(limit, offset);
      const candidatesQuery = `
        SELECT * FROM candidates 
        ${whereClause}
        ORDER BY created_at DESC
        LIMIT $${queryParams.length - 1} OFFSET $${queryParams.length}
      `;
      
      const candidatesResult = await client.query(candidatesQuery, queryParams);
      
      return {
        candidates: candidatesResult.rows,
        total
      };
    } catch (error) {
      console.error("Error fetching candidates:", error);
      throw error;
    }
  }
}
