import { Request, Response } from "express";
import crypto from "crypto";
import { transaction, getClient } from "../database/db";
import {
  CandidateModel,
  Candidate,
  CandidateWithDetails,
} from "../models/candidate.model";
import { addParsingJob } from "../queues/parseQueue";

interface CreateCandidateRequest {
  full_name?: string;
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  summary?: string;
  raw_resume_text?: string;
  file_path?: string;
  file_type?: string;
  skills?: string[];
  work_experience?: any[];
  education?: any[];
  certifications?: string[];  // Array of certification names from AI parsing
  projects?: string[];        // Array of project descriptions from AI parsing
}

interface UpdateCandidateRequest {
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  summary?: string;
}

export const createCandidate = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const candidateData: CreateCandidateRequest = req.body;
    const userId = (req as any).user?.id;

    const client = await getClient();
    try {
      // Begin transaction
      await client.query("BEGIN");

      const candidate = await CandidateModel.create(client, candidateData);

      // Save nested skills if provided
      if (candidateData.skills && Array.isArray(candidateData.skills)) {
        for (const skillName of candidateData.skills) {
          if (!skillName || typeof skillName !== "string") continue;
          
          const existingSkill = await client.query(
            "SELECT id FROM skills WHERE name = $1",
            [skillName],
          );

          let skillId: string;
          if (existingSkill.rows.length > 0) {
            skillId = existingSkill.rows[0].id;
          } else {
            const newSkill = await client.query(
              "INSERT INTO skills (id, name, category) VALUES ($1, $2, $3) RETURNING id",
              [crypto.randomUUID(), skillName, "technical"],
            );
            skillId = newSkill.rows[0].id;
          }

          // Check if association already exists
          const linkCheck = await client.query(
            "SELECT 1 FROM candidate_skills WHERE candidate_id = $1 AND skill_id = $2",
            [candidate.id, skillId]
          );
          if (linkCheck.rows.length === 0) {
            await client.query(
              "INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level) VALUES ($1, $2, $3)",
              [candidate.id, skillId, "intermediate"],
            );
          }
        }
      }

      // Save nested work experience if provided
      if (candidateData.work_experience && Array.isArray(candidateData.work_experience)) {
        for (const work of candidateData.work_experience) {
          const workQuery = `
            INSERT INTO work_experience (candidate_id, job_title, company_name, start_date, end_date, is_current, description, location)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
          `;
          await client.query(workQuery, [
            candidate.id,
            work.job_title || work.title || null,
            work.company_name || work.company || null,
            work.start_date || null,
            work.end_date || null,
            work.is_current || false,
            work.description || null,
            work.location || null,
          ]);
        }
      }

      // Save nested education if provided
      if (candidateData.education && Array.isArray(candidateData.education)) {
        for (const edu of candidateData.education) {
          const eduQuery = `
            INSERT INTO education (id, candidate_id, degree, institution, field_of_study, start_date, end_date, gpa)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
          `;
          await client.query(eduQuery, [
            crypto.randomUUID(),
            candidate.id,
            edu.degree || edu.degree_name || null,
            edu.institution || edu.institution_name || null,
            edu.field_of_study || null,
            edu.start_date || edu.start_year || null,
            edu.end_date || edu.end_year || null,
            edu.gpa || null,
          ]);
        }
      }

      // Save certifications if provided
      if (candidateData.certifications && Array.isArray(candidateData.certifications)) {
        for (const certName of candidateData.certifications) {
          if (!certName || typeof certName !== "string") continue;
          try {
            await client.query(
              `INSERT INTO certifications (id, candidate_id, name) VALUES ($1, $2, $3)
               ON CONFLICT DO NOTHING`,
              [crypto.randomUUID(), candidate.id, certName.trim()]
            );
          } catch (certInsertErr: any) {
            // Table may not exist yet; skip gracefully
            console.warn("Could not insert certification (table may not exist yet):", certInsertErr.message);
            break;
          }
        }
      }

      // Save projects as JSONB on the candidate record
      if (candidateData.projects && Array.isArray(candidateData.projects) && candidateData.projects.length > 0) {
        try {
          await client.query(
            "UPDATE candidates SET projects = $1 WHERE id = $2",
            [JSON.stringify(candidateData.projects), candidate.id]
          );
        } catch (projUpdateErr: any) {
          // Column may not exist yet if migration hasn't run
          console.warn("Could not save projects (column may not exist yet):", projUpdateErr.message);
        }
      }

      // Check if we are inserting already parsed data (manual profile creation or preview save)
      const hasParsedData = 
        (candidateData.skills && candidateData.skills.length > 0) ||
        (candidateData.work_experience && candidateData.work_experience.length > 0) ||
        (candidateData.education && candidateData.education.length > 0);

      if (hasParsedData) {
        // Insert completed parsing job record
        const parsedDataJson = {
          name: candidateData.full_name || candidateData.name,
          email: candidateData.email,
          phone: candidateData.phone,
          summary: candidateData.summary,
          skills: candidateData.skills || [],
          work_experience: candidateData.work_experience || [],
          education: candidateData.education || [],
          certifications: candidateData.certifications || [],
          projects: candidateData.projects || [],
        };

        await client.query(
          `INSERT INTO parsing_jobs (id, candidate_id, status, confidence_score, parsed_data, created_at, completed_at) 
           VALUES ($1, $2, 'completed', 1.0, $3, NOW(), NOW())`,
          [crypto.randomUUID(), candidate.id, JSON.stringify(parsedDataJson)],
        );

        // Update candidate status to success since parsing is complete
        await client.query(
          "UPDATE candidates SET status = 'success' WHERE id = $1",
          [candidate.id]
        );
        candidate.status = 'success';

        await client.query("COMMIT");

        res.status(201).json({
          message: "Candidate created and details saved successfully",
          candidate,
        });
      } else if (candidateData.file_path && candidateData.file_type) {
        // Fallback: if no nested data but file path is provided, queue a parsing job.
        try {
          const jobId = await addParsingJob(
            candidate.id,
            candidateData.file_path,
            candidateData.file_type,
            userId,
          );

          await client.query(
            `INSERT INTO parsing_jobs (candidate_id, status, created_at) 
             VALUES ($1, 'pending', NOW())`,
            [candidate.id],
          );

          await client.query("COMMIT");

          console.log(`📋 Added parsing job ${jobId} for candidate ${candidate.id}`);

          res.status(201).json({
            message: "Candidate created successfully and resume parsing initiated",
            candidate,
            parsing_job_id: jobId,
          });
        } catch (queueError) {
          console.error("Failed to add parsing job:", queueError);
          // Commit candidate anyway but warning
          await client.query("COMMIT");
          res.status(201).json({
            message: "Candidate created successfully but resume parsing failed to start",
            candidate,
            warning: "Resume parsing could not be initiated",
          });
        }
      } else {
        await client.query("COMMIT");
        res.status(201).json({
          message: "Candidate created successfully",
          candidate,
        });
      }
    } catch (txError) {
      await client.query("ROLLBACK");
      throw txError;
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Create candidate error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};

export const getAllCandidates = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const search = (req.query.search as string) || undefined;

    // Validate pagination
    if (page < 1 || limit < 1 || limit > 100) {
      res.status(400).json({
        error:
          "Invalid pagination parameters. Page must be ≥1, limit must be between 1-100",
      });
      return;
    }

    const client = await getClient();
    try {
      const { candidates, total } = await CandidateModel.findAll(
        client,
        page,
        limit,
        search,
      );

      const totalPages = Math.ceil(total / limit);
      const hasNextPage = page < totalPages;
      const hasPrevPage = page > 1;

      res.json({
        candidates,
        pagination: {
          current_page: page,
          total_pages: totalPages,
          total_items: total,
          items_per_page: limit,
          has_next_page: hasNextPage,
          has_prev_page: hasPrevPage,
        },
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get all candidates error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};

export const getCandidateById = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const { id } = req.params;
    const candidateId = Array.isArray(id) ? id[0] : id;

    if (!candidateId) {
      res.status(400).json({ error: "Candidate ID is required" });
      return;
    }

    const client = await getClient();
    try {
      const candidate = await CandidateModel.findByIdWithDetails(
        client,
        candidateId,
      );

      if (!candidate) {
        res.status(404).json({ error: "Candidate not found" });
        return;
      }

      res.json({ candidate });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get candidate by ID error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};

export const updateCandidate = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const { id } = req.params;
    const candidateId = Array.isArray(id) ? id[0] : id;
    const updates: UpdateCandidateRequest = req.body;

    if (!candidateId) {
      res.status(400).json({ error: "Candidate ID is required" });
      return;
    }

    if (Object.keys(updates).length === 0) {
      res
        .status(400)
        .json({ error: "At least one field must be provided for update" });
      return;
    }

    const client = await getClient();
    try {
      const candidate = await CandidateModel.update(
        client,
        candidateId,
        updates,
      );

      if (!candidate) {
        res.status(404).json({ error: "Candidate not found" });
        return;
      }

      res.json({
        message: "Candidate updated successfully",
        candidate,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Update candidate error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};

export const deleteCandidate = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const { id } = req.params;
    const candidateId = Array.isArray(id) ? id[0] : id;

    if (!candidateId) {
      res.status(400).json({ error: "Candidate ID is required" });
      return;
    }

    const client = await getClient();
    try {
      const deleted = await CandidateModel.softDelete(client, candidateId);

      if (!deleted) {
        res.status(404).json({ error: "Candidate not found" });
        return;
      }

      res.json({
        message: "Candidate deleted successfully",
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Delete candidate error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};

export const getCandidateParsingStatus = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const { id } = req.params;
    const candidateId = Array.isArray(id) ? id[0] : id;

    if (!candidateId) {
      res.status(400).json({ error: "Candidate ID is required" });
      return;
    }

    const client = await getClient();
    try {
      const parsingJob = await CandidateModel.getParsingStatus(
        client,
        candidateId,
      );

      if (!parsingJob) {
        res.status(404).json({
          error: "No parsing job found for this candidate",
          candidate_id: id,
        });
        return;
      }

      res.json({
        candidate_id: id,
        parsing_status: parsingJob,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get parsing status error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};
