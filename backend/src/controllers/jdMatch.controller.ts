import { Request, Response } from "express";
import { getClient } from "../database/db";
import { callAIService } from "../services/aiService";

export const matchJobDescription = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const { jobDescription } = req.body;

    if (!jobDescription || typeof jobDescription !== 'string') {
      res.status(400).json({
        success: false,
        error: "INVALID_REQUEST",
        message: "A valid jobDescription string is required",
      });
      return;
    }

    const client = await getClient();

    try {
      // 1. Parse JD using AI service
      console.log("🤖 Parsing raw JD using AI service");
      const parsedJd = await callAIService("/parse-jd-raw", {
        jobDescription: jobDescription,
      });
      
      const jobData = {
        title: parsedJd.job_title,
        required_skills: parsedJd.required_skills || [],
        preferred_skills: parsedJd.preferred_skills || [],
        min_experience_years: parsedJd.min_experience_years || 0,
        max_experience_years: parsedJd.max_experience_years,
        education_requirement: parsedJd.education_requirement,
        employment_type: parsedJd.employment_type,
        seniority_level: parsedJd.seniority_level,
        domain: parsedJd.domain,
        key_responsibilities: parsedJd.key_responsibilities || []
      };

      // 2. SQL Prefilter & Load Candidate Profiles
      // For now, load top candidates by recency, or filter by minimum experience
      console.log("💾 Fetching candidates from database");
      let candidatesQuery = `
        SELECT c.*, 
               array_agg(DISTINCT s.skill_name) as skills,
               COALESCE(c.years_of_experience, 0) as years_of_experience
        FROM candidates c
        LEFT JOIN skills s ON c.id = s.candidate_id
      `;
      
      const queryParams: any[] = [];
      let whereClause = "WHERE 1=1";
      
      if (jobData.min_experience_years > 0) {
        // Just a soft filter: get candidates with at least some experience if required
        whereClause += ` AND COALESCE(c.years_of_experience, 0) >= $1`;
        queryParams.push(Math.max(0, jobData.min_experience_years - 2)); // Allow 2 years gap
      }
      
      candidatesQuery += ` ${whereClause} GROUP BY c.id ORDER BY c.created_at DESC LIMIT 50`;
      
      const candidatesResult = await client.query(candidatesQuery, queryParams);
      const candidates = candidatesResult.rows;

      if (candidates.length === 0) {
        res.json({
          success: true,
          message: "No candidates found matching the preliminary criteria",
          parsedJob: jobData,
          matches: [],
        });
        return;
      }

      // 3. Prepare detailed data for AI matching
      const candidatesData = candidates.map((candidate) => ({
        id: candidate.id,
        name: candidate.full_name,
        email: candidate.email,
        phone: candidate.phone,
        location: candidate.location,
        skills: candidate.skills || [],
        years_of_experience: candidate.years_of_experience,
        // The backend DB might store job titles or education. 
        // We'll pass what we have; ideally work_experience JSON could be pulled if we update the query.
        job_titles: candidate.current_company ? [candidate.current_company] : [], // fallback
        projects: [],
        certifications: []
      }));

      // 4. Match candidates using AI service
      console.log(`🤖 Requesting AI matching for ${candidates.length} candidates`);
      const batchResponse = await callAIService("/match-jd-candidates", {
        candidates_data: candidatesData,
        job_data: jobData,
      });

      // Map the results back to the expected structure
      const matches = batchResponse.results.map((matchResult: any) => {
        const candidate = candidates.find((c) => c.id === matchResult.candidate_id);
        return {
          candidate_id: matchResult.candidate_id,
          candidate_name: candidate?.full_name || "",
          candidate_email: candidate?.email || "",
          candidate_location: candidate?.location || "",
          candidate_title: candidate?.current_company || "Unknown",
          candidate_experience: candidate?.years_of_experience || 0,
          ...matchResult,
        };
      });

      // Sort by overall_score descending
      const sortedMatches = matches.sort((a: any, b: any) => b.overall_score - a.overall_score);

      // Return results
      res.json({
        success: true,
        parsedJob: jobData,
        matches: sortedMatches,
      });

    } catch (err: any) {
      console.error("Error during JD matching workflow:", err);
      res.status(500).json({
        success: false,
        error: "MATCHING_FAILED",
        message: err.message || "An error occurred during matching",
      });
    } finally {
      client.release();
    }
  } catch (error: any) {
    console.error("Outer error in matchJobDescription:", error);
    res.status(500).json({
      success: false,
      error: "SERVER_ERROR",
      message: "Internal server error",
    });
  }
};
