import { PoolClient } from 'pg'

// TypeScript interfaces
export interface Candidate {
  id: string
  full_name?: string
  email?: string
  phone?: string
  location?: string
  linkedin_url?: string
  github_url?: string
  summary?: string
  raw_resume_text?: string
  file_path?: string
  file_type?: string
  created_at: Date
  updated_at: Date
  deleted_at?: Date
}

export interface WorkExperience {
  id: string
  candidate_id: string
  job_title?: string
  company_name?: string
  start_date?: Date
  end_date?: Date
  is_current: boolean
  description?: string
  location?: string
}

export interface Education {
  id: string
  candidate_id: string
  degree?: string
  institution?: string
  field_of_study?: string
  start_date?: Date
  end_date?: Date
  gpa?: number
}

export interface Skill {
  id: string
  candidate_id: string
  skill_name: string
  category: 'technical' | 'soft' | 'certification' | 'language' | 'tool'
  proficiency_level?: 'beginner' | 'intermediate' | 'advanced' | 'expert'
  years_experience?: number
  confidence_score?: number
}

export interface CandidateWithDetails extends Candidate {
  work_experience: WorkExperience[]
  education: Education[]
  skills: Skill[]
}

export interface ParsingJob {
  id: string
  candidate_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  confidence_score?: number
  parsed_data?: any
  error_message?: string
  created_at: Date
  completed_at?: Date
}

// Database query functions
export class CandidateModel {
  static async create(client: PoolClient, candidate: Partial<Candidate>): Promise<Candidate> {
    const query = `
      INSERT INTO candidates (full_name, email, phone, location, linkedin_url, github_url, 
                             summary, raw_resume_text, file_path, file_type)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING *
    `
    const values = [
      candidate.full_name,
      candidate.email,
      candidate.phone,
      candidate.location,
      candidate.linkedin_url,
      candidate.github_url,
      candidate.summary,
      candidate.raw_resume_text,
      candidate.file_path,
      candidate.file_type
    ]
    
    const result = await client.query(query, values)
    return result.rows[0]
  }

  static async findAll(client: PoolClient, page: number = 1, limit: number = 20, search?: string): Promise<{ candidates: Candidate[], total: number }> {
    let whereClause = 'WHERE deleted_at IS NULL'
    let queryParams: any[] = []
    let paramIndex = 1

    if (search) {
      whereClause += ` AND (full_name ILIKE $${paramIndex} OR email ILIKE $${paramIndex} OR location ILIKE $${paramIndex})`
      queryParams.push(`%${search}%`)
      paramIndex++
    }

    // Get total count
    const countQuery = `SELECT COUNT(*) FROM candidates ${whereClause}`
    const countResult = await client.query(countQuery, queryParams)
    const total = parseInt(countResult.rows[0].count)

    // Get paginated results
    const offset = (page - 1) * limit
    const query = `
      SELECT * FROM candidates 
      ${whereClause} 
      ORDER BY created_at DESC 
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `
    queryParams.push(limit, offset)
    
    const result = await client.query(query, queryParams)
    
    return {
      candidates: result.rows,
      total
    }
  }

  static async findById(client: PoolClient, id: string): Promise<Candidate | null> {
    const query = 'SELECT * FROM candidates WHERE id = $1 AND deleted_at IS NULL'
    const result = await client.query(query, [id])
    return result.rows[0] || null
  }

  static async findByIdWithDetails(client: PoolClient, id: string): Promise<CandidateWithDetails | null> {
    // Get candidate
    const candidate = await this.findById(client, id)
    if (!candidate) return null

    // Get work experience
    const workQuery = 'SELECT * FROM work_experience WHERE candidate_id = $1 ORDER BY start_date DESC'
    const workResult = await client.query(workQuery, [id])

    // Get education
    const educationQuery = 'SELECT * FROM education WHERE candidate_id = $1 ORDER BY start_date DESC'
    const educationResult = await client.query(educationQuery, [id])

    // Get skills
    const skillsQuery = 'SELECT * FROM skills WHERE candidate_id = $1 ORDER BY skill_name'
    const skillsResult = await client.query(skillsQuery, [id])

    return {
      ...candidate,
      work_experience: workResult.rows,
      education: educationResult.rows,
      skills: skillsResult.rows
    }
  }

  static async update(client: PoolClient, id: string, updates: Partial<Candidate>): Promise<Candidate | null> {
    const fields = Object.keys(updates).filter(key => key !== 'id' && key !== 'created_at' && key !== 'updated_at')
    if (fields.length === 0) return null

    const setClause = fields.map((field, index) => `${field} = $${index + 2}`).join(', ')
    const values = [id, ...fields.map(field => (updates as any)[field])]

    const query = `
      UPDATE candidates 
      SET ${setClause}, updated_at = NOW() 
      WHERE id = $1 AND deleted_at IS NULL 
      RETURNING *
    `
    
    const result = await client.query(query, values)
    return result.rows[0] || null
  }

  static async softDelete(client: PoolClient, id: string): Promise<boolean> {
    const query = 'UPDATE candidates SET deleted_at = NOW() WHERE id = $1 AND deleted_at IS NULL'
    const result = await client.query(query, [id])
    return (result.rowCount ?? 0) > 0
  }

  static async getParsingStatus(client: PoolClient, candidateId: string): Promise<ParsingJob | null> {
    const query = `
      SELECT * FROM parsing_jobs 
      WHERE candidate_id = $1 
      ORDER BY created_at DESC 
      LIMIT 1
    `
    const result = await client.query(query, [candidateId])
    return result.rows[0] || null
  }
}
