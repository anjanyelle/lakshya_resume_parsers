import { PoolClient } from 'pg'

// TypeScript interfaces
export interface JobDescription {
  id: string
  title: string
  department?: string
  location?: string
  employment_type?: 'full-time' | 'part-time' | 'contract' | 'internship' | 'temporary'
  description: string
  required_skills: string[]
  min_experience_years?: number
  max_experience_years?: number
  education_level?: 'high-school' | 'bachelor' | 'master' | 'phd' | 'any'
  salary_min?: number
  salary_max?: number
  created_at: Date
  updated_at?: Date
}

export interface JobFilter {
  department?: string
  location?: string
  employment_type?: string
  min_experience?: number
  max_experience?: number
  education_level?: string
  salary_min?: number
  salary_max?: number
  search?: string
}

// Database query functions
export class JobModel {
  static async create(client: PoolClient, job: Partial<JobDescription>): Promise<JobDescription> {
    const query = `
      INSERT INTO job_descriptions (title, department, location, employment_type, 
                                   description, required_skills, experience_years, created_at)
      VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
      RETURNING *
    `
    
    // For now, we'll use the existing schema but map our new fields
    const values = [
      job.title,
      job.department,
      job.location,
      job.employment_type,
      job.description,
      JSON.stringify(job.required_skills || []),
      job.min_experience_years
    ]
    
    const result = await client.query(query, values)
    const jobData = result.rows[0]
    
    // Transform to match our interface
    return {
      ...jobData,
      required_skills: jobData.required_skills || [],
      min_experience_years: jobData.experience_years,
      max_experience_years: jobData.experience_years,
      education_level: 'any',
      salary_min: undefined,
      salary_max: undefined
    }
  }

  static async findAll(client: PoolClient, page: number = 1, limit: number = 20, filters: JobFilter = {}): Promise<{ jobs: JobDescription[], total: number }> {
    let whereClause = 'WHERE 1=1'
    let queryParams: any[] = []
    let paramIndex = 1

    // Build WHERE clause based on filters
    if (filters.search) {
      whereClause += ` AND (title ILIKE $${paramIndex} OR description ILIKE $${paramIndex} OR department ILIKE $${paramIndex})`
      queryParams.push(`%${filters.search}%`)
      paramIndex++
    }

    if (filters.department) {
      whereClause += ` AND department = $${paramIndex}`
      queryParams.push(filters.department)
      paramIndex++
    }

    if (filters.location) {
      whereClause += ` AND location = $${paramIndex}`
      queryParams.push(filters.location)
      paramIndex++
    }

    if (filters.employment_type) {
      whereClause += ` AND employment_type = $${paramIndex}`
      queryParams.push(filters.employment_type)
      paramIndex++
    }

    if (filters.min_experience !== undefined) {
      whereClause += ` AND experience_years >= $${paramIndex}`
      queryParams.push(filters.min_experience)
      paramIndex++
    }

    if (filters.max_experience !== undefined) {
      whereClause += ` AND experience_years <= $${paramIndex}`
      queryParams.push(filters.max_experience)
      paramIndex++
    }

    // Get total count
    const countQuery = `SELECT COUNT(*) FROM job_descriptions ${whereClause}`
    const countResult = await client.query(countQuery, queryParams)
    const total = parseInt(countResult.rows[0].count)

    // Get paginated results
    const offset = (page - 1) * limit
    const query = `
      SELECT * FROM job_descriptions 
      ${whereClause} 
      ORDER BY created_at DESC 
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `
    queryParams.push(limit, offset)
    
    const result = await client.query(query, queryParams)
    
    // Transform results to match our interface
    const jobs = result.rows.map(job => ({
      ...job,
      required_skills: job.required_skills || [],
      min_experience_years: job.experience_years,
      max_experience_years: job.experience_years,
      education_level: 'any',
      salary_min: undefined,
      salary_max: undefined
    }))
    
    return {
      jobs,
      total
    }
  }

  static async findById(client: PoolClient, id: string): Promise<JobDescription | null> {
    const query = 'SELECT * FROM job_descriptions WHERE id = $1'
    const result = await client.query(query, [id])
    
    if (!result.rows[0]) return null
    
    const job = result.rows[0]
    return {
      ...job,
      required_skills: job.required_skills || [],
      min_experience_years: job.experience_years,
      max_experience_years: job.experience_years,
      education_level: 'any',
      salary_min: undefined,
      salary_max: undefined
    }
  }

  static async update(client: PoolClient, id: string, updates: Partial<JobDescription>): Promise<JobDescription | null> {
    const fields = Object.keys(updates).filter(key => key !== 'id' && key !== 'created_at')
    if (fields.length === 0) return null

    const setClause = fields.map((field, index) => {
      if (field === 'required_skills') {
        return `${field} = $${index + 2}`
      }
      return `${field} = $${index + 2}`
    }).join(', ')

    const values = [id, ...fields.map(field => {
      if (field === 'required_skills') {
        return JSON.stringify((updates as any)[field])
      }
      return (updates as any)[field]
    })]

    const query = `
      UPDATE job_descriptions 
      SET ${setClause} 
      WHERE id = $1 
      RETURNING *
    `
    
    const result = await client.query(query, values)
    
    if (!result.rows[0]) return null
    
    const job = result.rows[0]
    return {
      ...job,
      required_skills: job.required_skills || [],
      min_experience_years: job.experience_years,
      max_experience_years: job.experience_years,
      education_level: 'any',
      salary_min: undefined,
      salary_max: undefined
    }
  }

  static async delete(client: PoolClient, id: string): Promise<boolean> {
    const query = 'DELETE FROM job_descriptions WHERE id = $1'
    const result = await client.query(query, [id])
    return (result.rowCount ?? 0) > 0
  }

  static async getDepartments(client: PoolClient): Promise<string[]> {
    const query = 'SELECT DISTINCT department FROM job_descriptions WHERE department IS NOT NULL ORDER BY department'
    const result = await client.query(query)
    return result.rows.map(row => row.department)
  }

  static async getLocations(client: PoolClient): Promise<string[]> {
    const query = 'SELECT DISTINCT location FROM job_descriptions WHERE location IS NOT NULL ORDER BY location'
    const result = await client.query(query)
    return result.rows.map(row => row.location)
  }
}
