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
        "SELECT *, name as full_name FROM candidates WHERE id = $1",
        [id]
      );
      return result.rows[0] || null;
    } finally {
      client.release();
    }
  }

  static async findByIdWithDetails(client: any, id: string): Promise<CandidateWithDetails | null> {
    try {
      // Get candidate
      const candidateResult = await client.query(
        "SELECT *, name as full_name FROM candidates WHERE id = $1",
        [id]
      );
      
      if (candidateResult.rows.length === 0) {
        return null;
      }
      
      const candidate = candidateResult.rows[0];
      
      // Get work history
      const workHistoryResult = await client.query(
        "SELECT * FROM work_history WHERE candidate_id = $1 ORDER BY start_date DESC",
        [id]
      );
      
      // Get education
      const educationResult = await client.query(
        "SELECT * FROM education WHERE candidate_id = $1 ORDER BY end_date DESC",
        [id]
      );
      
      // Get certifications
      const certificationsResult = await client.query(
        "SELECT * FROM certifications WHERE candidate_id = $1 ORDER BY issue_date DESC",
        [id]
      );
      
      // Get skills
      const skillsResult = await client.query(
        `SELECT s.*, cs.proficiency_level, cs.years_experience 
         FROM skills s 
         JOIN candidate_skills cs ON s.id = cs.skill_id 
         WHERE cs.candidate_id = $1`,
        [id]
      );
      
      return {
        ...candidate,
        work_experience: workHistoryResult.rows,
        education: educationResult.rows,
        certifications: certificationsResult.rows,
        skills: skillsResult.rows
      };
    } catch (error) {
      console.error("Error fetching candidate with details:", error);
      throw error;
    }
  }

  static async create(data: Partial<Candidate>): Promise<Candidate> {
    const client = await getClient();
    try {
      const result = await client.query(
        "INSERT INTO candidates (email, phone, name, status) VALUES ($1, $2, $3, $4) RETURNING *",
        [data.email, data.phone, data.name, data.status || "pending"]
      );
      return result.rows[0];
    } finally {
      client.release();
    }
  }

  static async update(id: string, data: Partial<Candidate>): Promise<Candidate | null> {
    const client = await getClient();
    try {
      const result = await client.query(
        "UPDATE candidates SET email = COALESCE($1, email), phone = COALESCE($2, phone), name = COALESCE($3, name), status = COALESCE($4, status), updated_at = NOW() WHERE id = $5 RETURNING *",
        [data.email, data.phone, data.name, data.status, id]
      );
      return result.rows[0] || null;
    } finally {
      client.release();
    }
  }

  static async findAll(
    client: any,
    page: number = 1,
    limit: number = 20,
    search?: string
  ): Promise<{ candidates: CandidateWithDetails[]; total: number }> {
    try {
      const offset = (page - 1) * limit;
      
      // Build WHERE clause for search
      let whereClause = "WHERE 1=1";
      const queryParams: any[] = [];
      
      if (search) {
        queryParams.push(`%${search}%`);
        whereClause += ` AND (name ILIKE $${queryParams.length} OR email ILIKE $${queryParams.length})`;
      }
      
      // Get total count
      const countQuery = `SELECT COUNT(*) FROM candidates ${whereClause}`;
      const countResult = await client.query(countQuery, queryParams);
      const total = parseInt(countResult.rows[0].count);
      
      // Get paginated candidates
      queryParams.push(limit, offset);
      const candidatesQuery = `
        SELECT *, name as full_name FROM candidates 
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
