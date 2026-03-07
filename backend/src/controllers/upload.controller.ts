import { Request, Response } from 'express'
import { getClient } from '../database/db'
import { addParsingJob } from '../queues/parseQueue'
import { validateUploadedFile, getFileInfo, getFileType, deleteUploadedFile } from '../middleware/upload.middleware'

export const uploadResume = async (req: Request, res: Response): Promise<void> => {
  let client: any = null
  
  try {
    // 1. Validate file was uploaded
    if (!req.file) {
      res.status(400).json({
        error: 'No file uploaded',
        message: 'Please upload a resume file',
        code: 'NO_FILE_UPLOADED'
      })
      return
    }

    // Validate uploaded file
    validateUploadedFile(req.file)
    
    const fileInfo = getFileInfo(req.file)
    const userId = (req as any).user?.id

    console.log(`📄 Processing resume upload: ${fileInfo.originalname} (${fileInfo.type})`)

    // 2. Create database client and start transaction
    client = await getClient()

    try {
      await client.query('BEGIN')

      // 3. Create candidate record in database (status: 'pending')
      const candidateQuery = `
        INSERT INTO candidates (file_path, file_type, raw_resume_text, created_at, updated_at)
        VALUES ($1, $2, $3, NOW(), NOW())
        RETURNING *
      `
      
      const candidateValues = [
        fileInfo.path,
        fileInfo.type,
        null // raw_resume_text will be populated by AI service
      ]
      
      const candidateResult = await client.query(candidateQuery, candidateValues)
      const candidate = candidateResult.rows[0]
      
      console.log(`✅ Created candidate record: ${candidate.id}`)

      // 4. Create parsing_job record (status: 'queued')
      const parsingJobQuery = `
        INSERT INTO parsing_jobs (candidate_id, status, progress, created_at)
        VALUES ($1, 'queued', 0, NOW())
        RETURNING *
      `
      
      const parsingJobResult = await client.query(parsingJobQuery, [candidate.id])
      const parsingJob = parsingJobResult.rows[0]
      
      console.log(`✅ Created parsing job record: ${parsingJob.id}`)

      // 5. Add job to Redis queue
      const jobId = await addParsingJob(
        candidate.id,
        fileInfo.path,
        fileInfo.type,
        userId
      )
      
      console.log(`✅ Added job to Redis queue: ${jobId}`)

      // Commit transaction
      await client.query('COMMIT')

      // 6. Return success response
      res.status(201).json({
        success: true,
        message: 'Resume uploaded successfully and processing started',
        data: {
          candidateId: candidate.id,
          jobId: jobId,
          parsingJobId: parsingJob.id,
          status: 'queued',
          fileInfo: {
            originalName: fileInfo.originalname,
            size: fileInfo.size,
            type: fileInfo.type
          }
        }
      })

    } catch (dbError) {
      // Rollback transaction on database error
      await client.query('ROLLBACK')
      
      // Delete uploaded file if database operations failed
      deleteUploadedFile(fileInfo.path)
      
      console.error('❌ Database error during upload:', dbError)
      
      res.status(500).json({
        error: 'Database error',
        message: 'Failed to save candidate information',
        code: 'DATABASE_ERROR'
      })
      return
    }

  } catch (error) {
    // Delete uploaded file if any error occurred
    if (req.file) {
      deleteUploadedFile(req.file.path)
    }
    
    console.error('❌ Upload error:', error)
    
    // Handle specific error types
    if (error instanceof Error) {
      if (error.message.includes('Invalid file type')) {
        res.status(400).json({
          error: 'Invalid file type',
          message: error.message,
          code: 'INVALID_FILE_TYPE',
          allowedTypes: ['PDF', 'DOCX', 'TXT']
        })
        return
      }
      
      if (error.message.includes('File size exceeds')) {
        res.status(400).json({
          error: 'File too large',
          message: error.message,
          code: 'FILE_TOO_LARGE'
        })
        return
      }
    }
    
    res.status(500).json({
      error: 'Upload failed',
      message: 'An unexpected error occurred while processing your upload',
      code: 'UPLOAD_FAILED'
    })

  } finally {
    if (client) {
      client.release()
    }
  }
}

// Get upload status and configuration
export const getUploadConfig = async (req: Request, res: Response): Promise<void> => {
  try {
    const maxFileSize = parseInt(process.env.MAX_FILE_SIZE_MB || '10')
    const uploadPath = process.env.FILE_UPLOAD_PATH || './uploads'
    
    res.json({
      config: {
        maxFileSizeMB: maxFileSize,
        maxFileSizeBytes: maxFileSize * 1024 * 1024,
        allowedTypes: ['PDF', 'DOCX', 'TXT'],
        allowedMimeTypes: [
          'application/pdf',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'text/plain'
        ],
        uploadPath,
        fieldName: 'resume'
      },
      instructions: {
        method: 'POST',
        endpoint: '/api/upload/resume',
        contentType: 'multipart/form-data',
        fieldName: 'resume',
        authentication: 'Bearer token required'
      }
    })
  } catch (error) {
    console.error('❌ Error getting upload config:', error)
    res.status(500).json({
      error: 'Failed to get upload configuration',
      message: 'Please try again later'
    })
  }
}

// Get upload statistics (admin only)
export const getUploadStats = async (req: Request, res: Response): Promise<void> => {
  try {
    const client = await getClient()
    
    try {
      // Get total candidates count
      const totalCandidatesResult = await client.query('SELECT COUNT(*) FROM candidates')
      const totalCandidates = parseInt(totalCandidatesResult.rows[0].count)
      
      // Get candidates with files
      const withFilesResult = await client.query(
        'SELECT COUNT(*) FROM candidates WHERE file_path IS NOT NULL'
      )
      const withFiles = parseInt(withFilesResult.rows[0].count)
      
      // Get parsing jobs statistics
      const parsingStatsResult = await client.query(`
        SELECT status, COUNT(*) as count 
        FROM parsing_jobs 
        GROUP BY status
      `)
      
      const parsingStats = parsingStatsResult.rows.reduce((acc: any, row: any) => {
        acc[row.status] = parseInt(row.count)
        return acc
      }, {})
      
      // Get file type statistics
      const fileTypeStatsResult = await client.query(`
        SELECT file_type, COUNT(*) as count 
        FROM candidates 
        WHERE file_type IS NOT NULL 
        GROUP BY file_type
      `)
      
      const fileTypeStats = fileTypeStatsResult.rows.reduce((acc: any, row: any) => {
        acc[row.file_type] = parseInt(row.count)
        return acc
      }, {})
      
      res.json({
        statistics: {
          totalCandidates,
          candidatesWithFiles: withFiles,
          candidatesWithoutFiles: totalCandidates - withFiles,
          parsingJobs: {
            queued: parsingStats.queued || 0,
            processing: parsingStats.processing || 0,
            completed: parsingStats.completed || 0,
            failed: parsingStats.failed || 0,
            total: Object.values(parsingStats).reduce((sum: number, count: any) => sum + parseInt(count.toString()), 0)
          },
          fileTypes: fileTypeStats
        }
      })
      
    } finally {
      client.release()
    }
    
  } catch (error) {
    console.error('❌ Error getting upload stats:', error)
    res.status(500).json({
      error: 'Failed to get upload statistics',
      message: 'Please try again later'
    })
  }
}
