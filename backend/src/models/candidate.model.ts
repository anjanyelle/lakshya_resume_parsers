import { Pool } from "pg";
import { getClient } from "../database/db";

export interface Candidate {
  id: string;
  email?: string;
  phone?: string;
  name?: string;
  full_name?: string;
  status?: string;
  resume_path?: string;
  created_at?: Date;
  updated_at?: Date;
  summary?: string;
}

export interface CandidateWithDetails extends Candidate {
  work_experience?: any[];
  education?: any[];
  certifications?: any[];
  projects?: any[];
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
      // Get candidate
      const candidateResult = await client.query(
        "SELECT * FROM candidates WHERE id = $1",
        [id]
      );
      
      if (candidateResult.rows.length === 0) {
        return null;
      }
      
      const candidate = candidateResult.rows[0];
      
      // Get work experience
      const workExperienceResult = await client.query(
        "SELECT * FROM work_experience WHERE candidate_id = $1 ORDER BY start_date DESC",
        [id]
      );
      
      // Get education
      const educationResult = await client.query(
        "SELECT * FROM education WHERE candidate_id = $1 ORDER BY end_date DESC",
        [id]
      );
      
      // Get certifications (graceful fallback if table doesn't exist yet)
      let certificationRows: any[] = [];
      try {
        const certificationsResult = await client.query(
          "SELECT * FROM certifications WHERE candidate_id = $1 ORDER BY issue_date DESC",
          [id]
        );
        certificationRows = certificationsResult.rows;
      } catch (certErr: any) {
        // Table may not exist yet — return empty array
        console.warn("certifications table not found, returning empty array:", certErr.message);
      }

      // Get skills
      let skillRows: any[] = [];
      try {
        const skillsResult = await client.query(
          `SELECT s.*, cs.proficiency_level, cs.years_experience 
           FROM skills s 
           JOIN candidate_skills cs ON s.id = cs.skill_id 
           WHERE cs.candidate_id = $1`,
          [id]
        );
        skillRows = skillsResult.rows;
      } catch (skillErr: any) {
        console.warn("candidate_skills/skills query failed:", skillErr.message);
      }

      // Get projects from candidates.projects JSONB column (graceful fallback)
      let projectRows: any[] = [];
      try {
        if (candidate.projects) {
          projectRows = Array.isArray(candidate.projects) ? candidate.projects : JSON.parse(candidate.projects);
        }
      } catch (projErr) {
        projectRows = [];
      }

      return {
        ...candidate,
        work_experience: workExperienceResult.rows,
        education: educationResult.rows,
        certifications: certificationRows,
        projects: projectRows,
        skills: skillRows
      };
    } catch (error) {
      console.error("Error fetching candidate with details:", error);
      throw error;
    }
  }

  static async create(client: any, data: Partial<Candidate>): Promise<Candidate> {
    const result = await client.query(
      "INSERT INTO candidates (email, phone, full_name, status, summary, resume_path) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
      [
        data.email,
        data.phone,
        data.full_name || data.name,
        data.status || "pending",
        data.summary,
        data.resume_path
      ]
    );
    return result.rows[0];
  }

  static async update(client: any, id: string, data: Partial<Candidate>): Promise<Candidate | null> {
    const result = await client.query(
      "UPDATE candidates SET email = COALESCE($1, email), phone = COALESCE($2, phone), full_name = COALESCE($3, full_name), status = COALESCE($4, status), summary = COALESCE($5, summary), updated_at = NOW() WHERE id = $6 RETURNING *",
      [
        data.email,
        data.phone,
        data.full_name || data.name,
        data.status,
        data.summary,
        id
      ]
    );
    return result.rows[0] || null;
  }

  static async softDelete(client: any, id: string): Promise<boolean> {
    const result = await client.query(
      "UPDATE candidates SET deleted_at = NOW(), status = 'deleted' WHERE id = $1 RETURNING *",
      [id]
    );
    return result.rowCount > 0;
  }

  static async getParsingStatus(client: any, candidateId: string): Promise<any | null> {
    const result = await client.query(
      "SELECT * FROM parsing_jobs WHERE candidate_id = $1 ORDER BY created_at DESC LIMIT 1",
      [candidateId]
    );
    return result.rows[0] || null;
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
      let whereClause = "WHERE status = 'success'";
      const queryParams: any[] = [];
      
      if (search) {
        queryParams.push(`%${search}%`);
        whereClause += ` AND (full_name ILIKE $${queryParams.length} OR email ILIKE $${queryParams.length})`;
      }
      
      // Get total count
      const countQuery = `SELECT COUNT(*) FROM candidates ${whereClause}`;
      const countResult = await client.query(countQuery, queryParams);
      const total = parseInt(countResult.rows[0].count);
      
      // Get paginated candidates
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
