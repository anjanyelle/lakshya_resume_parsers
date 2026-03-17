import { Request, Response } from "express";
import { transaction, getClient } from "../database/db";
import {
  CandidateModel,
  Candidate,
  CandidateWithDetails,
} from "../models/candidate.model";
import { addParsingJob } from "../queues/parseQueue";

interface CreateCandidateRequest {
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  summary?: string;
  raw_resume_text?: string;
  file_path?: string;
  file_type?: string;
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
      const candidate = await CandidateModel.create(client, candidateData);

      // If file_path is provided, add parsing job to queue
      if (candidateData.file_path && candidateData.file_type) {
        try {
          const jobId = await addParsingJob(
            candidate.id,
            candidateData.file_path,
            candidateData.file_type,
            userId,
          );

          // Create parsing job record
          await client.query(
            `INSERT INTO parsing_jobs (candidate_id, status, created_at) 
             VALUES ($1, 'pending', NOW())`,
            [candidate.id],
          );

          console.log(
            `📋 Added parsing job ${jobId} for candidate ${candidate.id}`,
          );

          res.status(201).json({
            message:
              "Candidate created successfully and resume parsing initiated",
            candidate,
            parsing_job_id: jobId,
          });
        } catch (queueError) {
          console.error("Failed to add parsing job:", queueError);

          // Still create candidate but notify about parsing issue
          res.status(201).json({
            message:
              "Candidate created successfully but resume parsing failed to start",
            candidate,
            warning: "Resume parsing could not be initiated",
          });
        }
      } else {
        res.status(201).json({
          message: "Candidate created successfully",
          candidate,
        });
      }
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
