import { Worker, Job, Processor } from 'bullmq'
import IORedis from 'ioredis'
import path from 'path'
import { getClient } from '../database/db'
import { ParseJobData } from '../queues/parseQueue'
import { emitParsingProgress, emitParsingComplete, emitParsingFailed } from '../socket'

// Type definitions for AI service response
interface AIServiceResponse {
  status: string
  candidate_id: string
  name?: string
  email?: string
  phone?: string
  linkedin?: string
  github?: string
  summary?: string
  websites?: string[]
  skills?: string[]
  work_experience?: Array<{
    job_title?: string
    title?: string
    company_name?: string
    company?: string
    start_date?: string
    end_date?: string
    is_current?: boolean
    description?: string
    location?: string
  }>
  education?: Array<{
    degree?: string
    degree_name?: string
    institution?: string
    institution_name?: string
    field_of_study?: string
    start_year?: string
    end_year?: string
    start_date?: string
    end_date?: string
    gpa?: number
  }>
  locations?: string[]
  confidence?: {
    overall: number
    [key: string]: any
  }
  error?: string
}

// Redis connection configuration
const redisConfig = {
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD || undefined,
  maxRetriesPerRequest: 3,
  retryDelayOnFailover: 100,
  lazyConnect: true
}

// Create Redis connection
const connection = new IORedis(redisConfig)

// AI Service URL
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000'

// Helper function to update parsing job status in database
const updateParsingJobStatus = async (
  client: any,
  candidateId: string,
  status: string,
  progress?: number,
  confidenceScore?: number,
  parsedData?: any,
  errorMessage?: string
): Promise<any> => {
  try {
    const updateQuery = `
      UPDATE parsing_jobs 
      SET status = $1, 
          confidence_score = $2,
          parsed_data = $3,
          error_message = $4
      WHERE candidate_id = $5
      RETURNING *
    `
    
    const values = [
      status,
      confidenceScore || null,
      parsedData ? JSON.stringify(parsedData) : null,
      errorMessage || null,
      candidateId
    ]
    
    const result = await client.query(updateQuery, values)
    return result.rows[0]
  } catch (error) {
    console.error('Error updating parsing job status:', error)
    throw error
  }
}

// Helper function to update candidate with parsed data
const updateCandidateWithParsedData = async (
  client: any,
  candidateId: string,
  parsedData: AIServiceResponse
): Promise<any> => {
  try {
    const updateQuery = `
      UPDATE candidates 
      SET full_name = COALESCE($1, full_name),
          email = COALESCE($2, email),
          phone = COALESCE($3, phone),
          location = COALESCE($4, location),
          linkedin_url = COALESCE($5, linkedin_url),
          github_url = COALESCE($6, github_url),
          summary = COALESCE($7, summary),
          raw_resume_text = COALESCE($8, raw_resume_text),
          updated_at = NOW()
      WHERE id = $9
      RETURNING *
    `
    
    // Extract location from locations array or use first location
    const location = parsedData.locations && Array.isArray(parsedData.locations) 
      ? parsedData.locations[0] 
      : null
    
    const values = [
      parsedData.name || null,
      parsedData.email || null,
      parsedData.phone || null,
      location || null,
      parsedData.linkedin || null,
      parsedData.github || null,
      parsedData.summary || null,
      null, // raw_resume_text - not stored as a separate field
      candidateId
    ]
    
    const result = await client.query(updateQuery, values)
    
    // Insert skills if provided
    if (parsedData.skills && Array.isArray(parsedData.skills)) {
      // First, delete existing skills for this candidate
      await client.query('DELETE FROM skills WHERE candidate_id = $1', [candidateId])
      
      // Insert new skills
      for (const skill of parsedData.skills) {
        const skillQuery = `
          INSERT INTO skills (candidate_id, skill_name, category, proficiency_level, years_experience, confidence_score)
          VALUES ($1, $2, $3, $4, $5, $6)
        `
        await client.query(skillQuery, [
          candidateId,
          typeof skill === 'string' ? skill : skill.name || skill.skill_name,
          'technical', // Default category
          'intermediate', // Default proficiency
          null, // years_experience - not provided
          null  // confidence_score - not provided
        ])
      }
    }
    
    // Insert work experience if provided
    if (parsedData.work_experience && Array.isArray(parsedData.work_experience)) {
      // First, delete existing work experience
      await client.query('DELETE FROM work_experience WHERE candidate_id = $1', [candidateId])
      
      // Insert new work experience
      for (const work of parsedData.work_experience) {
        const workQuery = `
          INSERT INTO work_experience (candidate_id, job_title, company_name, start_date, end_date, is_current, description, location)
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        `
        await client.query(workQuery, [
          candidateId,
          work.job_title || work.title,
          work.company_name || work.company,
          work.start_date || null,
          work.end_date || null,
          work.is_current || false,
          work.description || null,
          work.location || null
        ])
      }
    }
    
    // Insert education if provided
    if (parsedData.education && Array.isArray(parsedData.education)) {
      // First, delete existing education
      await client.query('DELETE FROM education WHERE candidate_id = $1', [candidateId])
      
      // Insert new education
      for (const edu of parsedData.education) {
        const eduQuery = `
          INSERT INTO education (candidate_id, degree, institution, field_of_study, start_date, end_date, gpa)
          VALUES ($1, $2, $3, $4, $5, $6, $7)
        `
        await client.query(eduQuery, [
          candidateId,
          edu.degree || edu.degree_name,
          edu.institution || edu.institution_name,
          edu.field_of_study || null,
          edu.start_year || edu.start_date || null,
          edu.end_year || edu.end_date || null,
          edu.gpa || null
        ])
      }
    }
    
    return result.rows[0]
  } catch (error) {
    console.error('Error updating candidate with parsed data:', error)
    throw error
  }
}

// Call AI service for resume parsing
const callAIService = async (filePath: string, fileType: string, candidateId: string): Promise<AIServiceResponse> => {
  try {
    const apiResponse = await fetch(`${AI_SERVICE_URL}/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_path: path.resolve(filePath),
        candidate_id: candidateId
      })
    })

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text()
      throw new Error(`AI service returned ${apiResponse.status}: ${errorText}`)
    }

    const result: AIServiceResponse = await apiResponse.json()
    return result
  } catch (error) {
    console.error('Error calling AI service:', error)
    throw error
  }
}

// The processor function for the worker
const processor: Processor<ParseJobData> = async (job: Job<ParseJobData>) => {
  const { candidateId, filePath, fileType, userId } = job.data
  
  console.log(`🔄 Starting resume parsing for candidate ${candidateId}`)
  
  const client = await getClient()
  
  try {
    // Update initial status and emit Socket.io event
    await updateParsingJobStatus(client, candidateId, 'processing')
    await job.updateProgress(0)
    
    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 0,
        message: 'Starting resume parsing...'
      })
    }
    
    // Step 1: Validate file exists (10%)
    await job.updateProgress(10)
    await updateParsingJobStatus(client, candidateId, 'processing')
    
    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 10,
        message: 'Validating resume file...'
      })
    }
    
    // Simulate file validation
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Step 2: Call AI service (10% - 70%)
    await updateParsingJobStatus(client, candidateId, 'processing')
    await job.updateProgress(25)
    
    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 25,
        message: 'Sending resume to AI service for analysis...'
      })
    }
    
    console.log(`🤖 Calling AI service for ${filePath}`)
    const aiResult = await callAIService(filePath, fileType, candidateId)
    
    await updateParsingJobStatus(client, candidateId, 'processing')
    await job.updateProgress(50)
    
    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 50,
        message: 'AI analysis complete, processing results...'
      })
    }
    
    // Step 3: Process AI results (50% - 80%)
    if (!aiResult || aiResult.status !== 'success') {
      throw new Error(`AI service returned ${aiResult?.status || 'unknown'} status: ${aiResult?.error || 'Unknown error'}`)
    }
    
    await updateParsingJobStatus(client, candidateId, 'processing')
    await job.updateProgress(75)
    
    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 75,
        message: 'Updating candidate profile with parsed data...'
      })
    }
    
    // Step 4: Update database with parsed data (80% - 100%)
    const confidenceScore: number = aiResult.confidence?.overall || 0.8
    
    // Update candidate with parsed information
    await updateCandidateWithParsedData(client, candidateId, aiResult)
    
    await updateParsingJobStatus(client, candidateId, 'processing')
    await job.updateProgress(90)
    
    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 90,
        message: 'Finalizing resume parsing...'
      })
    }
    
    // Mark as completed
    await updateParsingJobStatus(
      client, 
      candidateId, 
      'completed', 
      100, 
      confidenceScore, 
      aiResult
    )
    
    await job.updateProgress(100)
    
    console.log(`✅ Successfully parsed resume for candidate ${candidateId}`)
    
    // Emit completion event
    if (userId) {
      emitParsingComplete(userId, {
        candidateId,
        data: aiResult
      })
    }
    
    return {
      success: true,
      candidateId,
      confidenceScore,
      parsedData: aiResult
    }
    
  } catch (error) {
    console.error(`❌ Failed to parse resume for candidate ${candidateId}:`, error)
    
    // Update with error status
    await updateParsingJobStatus(
      client, 
      candidateId, 
      'failed', 
      undefined, 
      undefined, 
      undefined, 
      error instanceof Error ? error.message : 'Unknown error'
    )
    
    // Emit failure event
    if (userId) {
      emitParsingFailed(userId, {
        candidateId,
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    }
    
    // Re-throw the error to mark job as failed
    throw error
    
  } finally {
    client.release()
  }
}

// Create the worker
export const parseWorker = new Worker<ParseJobData>(
  'resume-parsing',
  processor,
  {
    connection: redisConfig,
    concurrency: parseInt(process.env.PARSE_WORKER_CONCURRENCY || '2'), // Process 2 jobs concurrently
    limiter: {
      max: 10,
      duration: 60000 // Max 10 jobs per minute
    }
  }
)

// Worker event handlers
parseWorker.on('completed', (job: Job, result: any) => {
  console.log(`🎉 Job ${job.id} completed for candidate ${job.data.candidateId}`)
})

parseWorker.on('failed', (job: Job | undefined, err: Error) => {
  const candidateId = job?.data.candidateId || 'unknown'
  console.error(`💥 Job ${job?.id} failed for candidate ${candidateId}:`, err.message)
})

parseWorker.on('error', (err) => {
  console.error('❌ Worker error:', err)
})

parseWorker.on('ready', () => {
  console.log('🚀 Parse worker is ready and listening for jobs')
})

// Progress updates
parseWorker.on('progress', (job: Job<ParseJobData>, progress: any) => {
  const progressNum = typeof progress === 'number' ? progress : parseInt(progress.toString())
  console.log(`📊 Job ${job.id} progress: ${progressNum}% for candidate ${job.data.candidateId}`)
})

// Graceful shutdown
export const closeWorker = async () => {
  console.log('🔄 Closing parse worker...')
  await parseWorker.close()
  await connection.quit()
  console.log('🔌 Parse worker and Redis connection closed')
}

// Handle process termination
process.on('SIGTERM', async () => {
  console.log('🔄 SIGTERM received, shutting down worker gracefully')
  await closeWorker()
  process.exit(0)
})

process.on('SIGINT', async () => {
  console.log('🔄 SIGINT received, shutting down worker gracefully')
  await closeWorker()
  process.exit(0)
})

export default parseWorker
