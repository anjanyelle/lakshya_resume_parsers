import { Request, Response } from 'express'
import { getClient } from '../database/db'
import { callAIService } from '../services/aiService'

/**
 * Controller for handling candidate-job matching operations
 */

export const matchCandidatesToJob = async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params
    const { limit = 20 } = req.body
    
    const client = await getClient()
    
    try {
      // 1. Get job from database by jobId
      const jobQuery = `
        SELECT j.*, 
               array_agg(DISTINCT js.skill_name) as required_skills,
               array_agg(DISTINCT ps.skill_name) as preferred_skills
        FROM jobs j
        LEFT JOIN job_skills js ON j.id = js.job_id AND js.skill_type = 'required'
        LEFT JOIN job_skills ps ON j.id = ps.job_id AND ps.skill_type = 'preferred'
        WHERE j.id = $1
        GROUP BY j.id
      `
      
      const jobResult = await client.query(jobQuery, [jobId])
      
      if (jobResult.rows.length === 0) {
        return res.status(404).json({
          error: 'JOB_NOT_FOUND',
          message: `Job with ID ${jobId} not found`
        })
      }
      
      const job = jobResult.rows[0]
      
      // 2. Get all candidates from database
      const candidatesQuery = `
        SELECT c.*, 
               array_agg(DISTINCT s.skill_name) as skills,
               COALESCE(AVG(s.confidence_score), 0.8) as avg_skill_confidence,
               COALESCE(c.years_of_experience, 0) as years_of_experience
        FROM candidates c
        LEFT JOIN skills s ON c.id = s.candidate_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT $1
      `
      
      const candidatesResult = await client.query(candidatesQuery, [limit])
      const candidates = candidatesResult.rows
      
      if (candidates.length === 0) {
        return res.json({
          success: true,
          jobId,
          message: 'No candidates found',
          matches: []
        })
      }
      
      // 3. For each candidate, call Python AI service POST /match
      const matchPromises = candidates.map(async (candidate) => {
        try {
          const matchData = {
            candidate_data: {
              id: candidate.id,
              name: candidate.full_name,
              email: candidate.email,
              phone: candidate.phone,
              location: candidate.location,
              linkedin: candidate.linkedin_url,
              github: candidate.github_url,
              skills: candidate.skills || [],
              years_of_experience: candidate.years_of_experience,
              education: [] // Will be populated if needed
            },
            job_data: {
              id: job.id,
              title: job.title,
              description: job.description,
              required_skills: job.required_skills || [],
              preferred_skills: job.preferred_skills || [],
              min_experience_years: job.min_experience_years,
              max_experience_years: job.max_experience_years,
              education_requirement: job.education_requirement,
              employment_type: job.employment_type,
              seniority_level: job.seniority_level
            }
          }
          
          const matchResult = await callAIService('/match', matchData)
          
          return {
            candidate_id: candidate.id,
            candidate_name: candidate.full_name,
            candidate_email: candidate.email,
            candidate_location: candidate.location,
            ...matchResult
          }
        } catch (error) {
          console.error(`Error matching candidate ${candidate.id}:`, error)
          return {
            candidate_id: candidate.id,
            candidate_name: candidate.full_name,
            candidate_email: candidate.email,
            candidate_location: candidate.location,
            overall_score: 0,
            skill_score: 0,
            experience_score: 0,
            education_score: 0,
            matching_skills: [],
            missing_skills: [],
            extra_skills: [],
            experience_gap_years: 0,
            recommendation: 'Not Recommended',
            reason: 'Matching service unavailable',
            error: true
          }
        }
      })
      
      const matches = await Promise.all(matchPromises)
      
      // 4. Sort candidates by overall_score descending
      const sortedMatches = matches.sort((a, b) => b.overall_score - a.overall_score)
      
      // 5. Save scores to match_scores table
      const deleteOldScoresQuery = 'DELETE FROM match_scores WHERE job_id = $1'
      await client.query(deleteOldScoresQuery, [jobId])
      
      const insertScoreQuery = `
        INSERT INTO match_scores (
          job_id, candidate_id, overall_score, skill_score, 
          experience_score, education_score, matching_skills, 
          missing_skills, extra_skills, experience_gap_years, 
          recommendation, reason, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
      `
      
      for (const match of sortedMatches) {
        if (!match.error) {
          await client.query(insertScoreQuery, [
            jobId,
            match.candidate_id,
            match.overall_score,
            match.skill_score,
            match.experience_score,
            match.education_score,
            JSON.stringify(match.matching_skills),
            JSON.stringify(match.missing_skills),
            JSON.stringify(match.extra_skills),
            match.experience_gap_years,
            match.recommendation,
            match.reason
          ])
        }
      }
      
      // 6. Return ranked list of candidates with scores
      res.json({
        success: true,
        jobId,
        job_title: job.title,
        total_candidates: candidates.length,
        successful_matches: sortedMatches.filter(m => !m.error).length,
        matches: sortedMatches
      })
      
    } finally {
      client.release()
    }
    
  } catch (error) {
    console.error('Error in matchCandidatesToJob:', error)
    res.status(500).json({
      error: 'INTERNAL_ERROR',
      message: 'Failed to match candidates to job'
    })
  }
}

export const getMatchResultsForJob = async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params
    
    const client = await getClient()
    
    try {
      // Get cached match scores from match_scores table
      const query = `
        SELECT ms.*, 
               c.full_name as candidate_name,
               c.email as candidate_email,
               c.phone as candidate_phone,
               c.location as candidate_location,
               c.linkedin_url as candidate_linkedin,
               c.github_url as candidate_github,
               j.title as job_title
        FROM match_scores ms
        JOIN candidates c ON ms.candidate_id = c.id
        JOIN jobs j ON ms.job_id = j.id
        WHERE ms.job_id = $1
        ORDER BY ms.overall_score DESC
      `
      
      const result = await client.query(query, [jobId])
      
      if (result.rows.length === 0) {
        return res.status(404).json({
          error: 'NO_MATCH_RESULTS',
          message: `No match results found for job ${jobId}. Run matching first.`
        })
      }
      
      // Parse JSON arrays for skills
      const matches = result.rows.map(row => ({
        ...row,
        matching_skills: row.matching_skills || [],
        missing_skills: row.missing_skills || [],
        extra_skills: row.extra_skills || []
      }))
      
      res.json({
        success: true,
        jobId,
        job_title: result.rows[0].job_title,
        total_matches: matches.length,
        matches
      })
      
    } finally {
      client.release()
    }
    
  } catch (error) {
    console.error('Error in getMatchResultsForJob:', error)
    res.status(500).json({
      error: 'INTERNAL_ERROR',
      message: 'Failed to get match results'
    })
  }
}

export const matchSingleCandidate = async (req: Request, res: Response) => {
  try {
    const { candidateId, jobId } = req.params
    
    const client = await getClient()
    
    try {
      // Get candidate details
      const candidateQuery = `
        SELECT c.*, 
               array_agg(DISTINCT s.skill_name) as skills,
               COALESCE(AVG(s.confidence_score), 0.8) as avg_skill_confidence,
               COALESCE(c.years_of_experience, 0) as years_of_experience
        FROM candidates c
        LEFT JOIN skills s ON c.id = s.candidate_id
        WHERE c.id = $1
        GROUP BY c.id
      `
      
      const candidateResult = await client.query(candidateQuery, [candidateId])
      
      if (candidateResult.rows.length === 0) {
        return res.status(404).json({
          error: 'CANDIDATE_NOT_FOUND',
          message: `Candidate with ID ${candidateId} not found`
        })
      }
      
      const candidate = candidateResult.rows[0]
      
      // Get job details
      const jobQuery = `
        SELECT j.*, 
               array_agg(DISTINCT js.skill_name) as required_skills,
               array_agg(DISTINCT ps.skill_name) as preferred_skills
        FROM jobs j
        LEFT JOIN job_skills js ON j.id = js.job_id AND js.skill_type = 'required'
        LEFT JOIN job_skills ps ON j.id = ps.job_id AND ps.skill_type = 'preferred'
        WHERE j.id = $1
        GROUP BY j.id
      `
      
      const jobResult = await client.query(jobQuery, [jobId])
      
      if (jobResult.rows.length === 0) {
        return res.status(404).json({
          error: 'JOB_NOT_FOUND',
          message: `Job with ID ${jobId} not found`
        })
      }
      
      const job = jobResult.rows[0]
      
      // Prepare data for AI service
      const matchData = {
        candidate_data: {
          id: candidate.id,
          name: candidate.full_name,
          email: candidate.email,
          phone: candidate.phone,
          location: candidate.location,
          linkedin: candidate.linkedin_url,
          github: candidate.github_url,
          skills: candidate.skills || [],
          years_of_experience: candidate.years_of_experience,
          education: [] // Will be populated if needed
        },
        job_data: {
          id: job.id,
          title: job.title,
          description: job.description,
          required_skills: job.required_skills || [],
          preferred_skills: job.preferred_skills || [],
          min_experience_years: job.min_experience_years,
          max_experience_years: job.max_experience_years,
          education_requirement: job.education_requirement,
          employment_type: job.employment_type,
          seniority_level: job.seniority_level
        }
      }
      
      // Call AI service for matching
      const matchResult = await callAIService('/match', matchData)
      
      // Save single match result
      const insertScoreQuery = `
        INSERT INTO match_scores (
          job_id, candidate_id, overall_score, skill_score, 
          experience_score, education_score, matching_skills, 
          missing_skills, extra_skills, experience_gap_years, 
          recommendation, reason, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
        ON CONFLICT (job_id, candidate_id) 
        DO UPDATE SET
          overall_score = EXCLUDED.overall_score,
          skill_score = EXCLUDED.skill_score,
          experience_score = EXCLUDED.experience_score,
          education_score = EXCLUDED.education_score,
          matching_skills = EXCLUDED.matching_skills,
          missing_skills = EXCLUDED.missing_skills,
          extra_skills = EXCLUDED.extra_skills,
          experience_gap_years = EXCLUDED.experience_gap_years,
          recommendation = EXCLUDED.recommendation,
          reason = EXCLUDED.reason,
          created_at = NOW()
      `
      
      await client.query(insertScoreQuery, [
        jobId,
        candidateId,
        matchResult.overall_score,
        matchResult.skill_score,
        matchResult.experience_score,
        matchResult.education_score,
        JSON.stringify(matchResult.matching_skills),
        JSON.stringify(matchResult.missing_skills),
        JSON.stringify(matchResult.extra_skills),
        matchResult.experience_gap_years,
        matchResult.recommendation,
        matchResult.reason
      ])
      
      res.json({
        success: true,
        candidate: {
          id: candidate.id,
          name: candidate.full_name,
          email: candidate.email,
          location: candidate.location
        },
        job: {
          id: job.id,
          title: job.title
        },
        match_result: matchResult
      })
      
    } finally {
      client.release()
    }
    
  } catch (error) {
    console.error('Error in matchSingleCandidate:', error)
    res.status(500).json({
      error: 'INTERNAL_ERROR',
      message: 'Failed to match candidate to job'
    })
  }
}
