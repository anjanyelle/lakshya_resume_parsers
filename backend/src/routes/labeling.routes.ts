import { Router, Response } from "express";
import { query } from "../database/db";
import { AuthenticatedRequest } from "../middleware/auth.middleware";

const router = Router();

// GET /api/labeling/next - Get next unlabeled candidate
router.get("/next", async (req: AuthenticatedRequest, res: Response) => {
  try {
    // Get next candidate with confidence < 0.90 that hasn't been labeled yet
    const sql = `
      SELECT c.* 
      FROM candidates c
      LEFT JOIN labeled_data ld ON c.id = ld.candidate_id
      WHERE (c.parsing_status->>'confidence_score')::float < 0.90 
      AND ld.id IS NULL
      ORDER BY c.created_at ASC
      LIMIT 1
    `;

    const result = await query(sql);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "No more candidates to label" });
    }

    const candidate = result.rows[0];

    // Extract arrays from JSON fields if they exist
    if (candidate.skills && typeof candidate.skills === "string") {
      try {
        candidate.skills = JSON.parse(candidate.skills);
      } catch (e) {
        candidate.skills = [];
      }
    }

    if (candidate.companies && typeof candidate.companies === "string") {
      try {
        candidate.companies = JSON.parse(candidate.companies);
      } catch (e) {
        candidate.companies = [];
      }
    }

    if (candidate.job_titles && typeof candidate.job_titles === "string") {
      try {
        candidate.job_titles = JSON.parse(candidate.job_titles);
      } catch (e) {
        candidate.job_titles = [];
      }
    }

    if (
      candidate.education_degrees &&
      typeof candidate.education_degrees === "string"
    ) {
      try {
        candidate.education_degrees = JSON.parse(candidate.education_degrees);
      } catch (e) {
        candidate.education_degrees = [];
      }
    }

    if (candidate.universities && typeof candidate.universities === "string") {
      try {
        candidate.universities = JSON.parse(candidate.universities);
      } catch (e) {
        candidate.universities = [];
      }
    }

    return res.json(candidate);
  } catch (error) {
    console.error("Error fetching next candidate:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
});

// POST /api/labeling/save - Save corrected labels
router.post("/save", async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { candidate_id, corrected_fields, action } = req.body;

    if (!candidate_id || !action) {
      return res.status(400).json({ message: "Missing required fields" });
    }

    const userId = req.user!.id;

    // Check if candidate exists
    const candidateCheck = await query(
      "SELECT id FROM candidates WHERE id = $1",
      [candidate_id],
    );

    if (candidateCheck.rows.length === 0) {
      return res.status(404).json({ message: "Candidate not found" });
    }

    // Insert or update labeled data
    const insertQuery = `
      INSERT INTO labeled_data (candidate_id, corrected_fields, labeled_by, labeled_at, action)
      VALUES ($1, $2, $3, NOW(), $4)
      ON CONFLICT (candidate_id) 
      DO UPDATE SET 
        corrected_fields = EXCLUDED.corrected_fields,
        labeled_by = EXCLUDED.labeled_by,
        labeled_at = EXCLUDED.labeled_at,
        action = EXCLUDED.action
    `;

    await query(insertQuery, [
      candidate_id,
      JSON.stringify(corrected_fields || {}),
      userId,
      action,
    ]);

    // If action is 'corrected' or 'approved', update the original candidate data
    if (action === "corrected" && corrected_fields) {
      const updateQuery = `
        UPDATE candidates 
        SET 
          full_name = COALESCE($1, full_name),
          email = COALESCE($2, email),
          phone = COALESCE($3, phone),
          skills = COALESCE($4, skills),
          companies = COALESCE($5, companies),
          job_titles = COALESCE($6, job_titles),
          education_degrees = COALESCE($7, education_degrees),
          universities = COALESCE($8, universities),
          updated_at = NOW()
        WHERE id = $9
      `;

      await query(updateQuery, [
        corrected_fields.name,
        corrected_fields.email,
        corrected_fields.phone,
        JSON.stringify(corrected_fields.skills || []),
        JSON.stringify(corrected_fields.companies || []),
        JSON.stringify(corrected_fields.job_titles || []),
        JSON.stringify(corrected_fields.education_degrees || []),
        JSON.stringify(corrected_fields.universities || []),
        candidate_id,
      ]);
    }

    return res.json({ message: "Label data saved successfully" });
  } catch (error) {
    console.error("Error saving label data:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
});

// GET /api/labeling/progress - Get labeling progress
router.get("/progress", async (req: AuthenticatedRequest, res) => {
  try {
    // Get total candidates with confidence < 0.90
    const totalQuery = `
      SELECT COUNT(*) as total
      FROM candidates c
      WHERE (c.parsing_status->>'confidence_score')::float < 0.90
    `;

    // Get labeled candidates count
    const labeledQuery = `
      SELECT COUNT(*) as labeled
      FROM labeled_data ld
      JOIN candidates c ON ld.candidate_id = c.id
      WHERE (c.parsing_status->>'confidence_score')::float < 0.90
    `;

    // Calculate accuracy estimate (approved vs corrected ratio)
    const accuracyQuery = `
      SELECT 
        COUNT(*) FILTER (WHERE action = 'approved') as approved,
        COUNT(*) FILTER (WHERE action = 'corrected') as corrected
      FROM labeled_data ld
      JOIN candidates c ON ld.candidate_id = c.id
      WHERE (c.parsing_status->>'confidence_score')::float < 0.90
    `;

    const [totalResult, labeledResult, accuracyResult] = await Promise.all([
      query(totalQuery),
      query(labeledQuery),
      query(accuracyQuery),
    ]);

    const total = parseInt(totalResult.rows[0].total);
    const labeled = parseInt(labeledResult.rows[0].labeled);
    const { approved, corrected } = accuracyResult.rows[0];

    // Calculate accuracy estimate
    let accuracy_estimate = 0;
    const totalProcessed = parseInt(approved) + parseInt(corrected);
    if (totalProcessed > 0) {
      accuracy_estimate = parseInt(approved) / totalProcessed;
    }

    return res.json({
      labeled,
      total,
      accuracy_estimate,
    });
  } catch (error) {
    console.error("Error fetching progress:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
});

// GET /api/labeling/queue - Get unlabeled candidates queue
router.get("/queue", async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const offset = (parseInt(page as string) - 1) * parseInt(limit as string);

    const candidatesQuery = `
      SELECT 
        c.id,
        c.full_name,
        c.email,
        (c.parsing_status->>'confidence_score')::float as confidence_score,
        c.created_at
      FROM candidates c
      LEFT JOIN labeled_data ld ON c.id = ld.candidate_id
      WHERE (c.parsing_status->>'confidence_score')::float < 0.90 
      AND ld.id IS NULL
      ORDER BY c.created_at ASC
      LIMIT $1 OFFSET $2
    `;

    const countQuery = `
      SELECT COUNT(*) as total
      FROM candidates c
      LEFT JOIN labeled_data ld ON c.id = ld.candidate_id
      WHERE (c.parsing_status->>'confidence_score')::float < 0.90 
      AND ld.id IS NULL
    `;

    const [candidatesResult, countResult] = await Promise.all([
      query(candidatesQuery, [limit, offset]),
      query(countQuery),
    ]);

    const total = parseInt(countResult.rows[0].total);

    return res.json({
      candidates: candidatesResult.rows,
      pagination: {
        page: parseInt(page as string),
        limit: parseInt(limit as string),
        total,
        pages: Math.ceil(total / parseInt(limit as string)),
      },
    });
  } catch (error) {
    console.error("Error fetching queue:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
});

export default router;
