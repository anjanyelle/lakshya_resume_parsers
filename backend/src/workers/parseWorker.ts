import { Worker, Job, Processor } from "bullmq";
import crypto from "crypto";
import IORedis from "ioredis";
import path from "path";
import fs from "fs";
import { getClient } from "../database/db";
import { ParseJobData } from "../queues/parseQueue";
import {
  emitParsingProgress,
  emitParsingComplete,
  emitParsingFailed,
} from "../socket";

// Helper function to parse date strings to YYYY-MM-DD format
function parseDateString(dateStr: string | null | undefined | Date | number): string | null {
  if (!dateStr) return null;

  // Trim whitespace if it's a string
  if (typeof dateStr === 'string') {
    dateStr = dateStr.trim();
    if (!dateStr) return null;
  }

  // Convert to string if it's a Date object or number
  let dateString: string;
  if (dateStr instanceof Date) {
    // If it's already a Date object, format it
    const year = dateStr.getFullYear();
    const month = String(dateStr.getMonth() + 1).padStart(2, '0');
    const day = String(dateStr.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } else if (typeof dateStr === 'number') {
    // If it's a year number, ensure it's 4 digits
    const yearNum = dateStr;
    if (yearNum < 100) {
      // Handle 2-digit years: 00-29 -> 2000-2029, 30-99 -> 1930-1999
      const fullYear = yearNum < 30 ? 2000 + yearNum : 1900 + yearNum;
      return `${fullYear}-01-01`;
    } else if (yearNum >= 1900 && yearNum <= 2100) {
      return `${yearNum}-01-01`;
    } else {
      // Invalid year number
      return null;
    }
  } else if (typeof dateStr !== 'string') {
    // If it's not a string, Date, or number, convert to string
    dateString = String(dateStr);
  } else {
    dateString = dateStr;
  }

  // Handle formats like "March 2023", "Jan 2020", etc.
  const monthYearMatch = dateString.match(
    /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})$/i,
  );
  if (monthYearMatch) {
    const monthMap: { [key: string]: string } = {
      Jan: "01",
      Feb: "02",
      Mar: "03",
      Apr: "04",
      May: "05",
      Jun: "06",
      Jul: "07",
      Aug: "08",
      Sep: "09",
      Oct: "10",
      Nov: "11",
      Dec: "12",
    };
    const month = monthMap[monthYearMatch[1].substring(0, 3)];
    const year = monthYearMatch[2];
    return `${year}-${month}-01`; // Use first day of the month
  }

  // Handle formats like "2020-2023", "2018 - 2021"
  const yearRangeMatch = dateString.match(/^(\d{4})\s*-\s*(\d{4})$/);
  if (yearRangeMatch) {
    return `${yearRangeMatch[1]}-01-01`; // Use start of the range
  }

  // Handle formats like "2023", "2020", or "20", "23"
  const yearOnlyMatch = dateString.match(/^(\d{2,4})$/);
  if (yearOnlyMatch) {
    const yearStr = yearOnlyMatch[1];
    let year: number;
    
    if (yearStr.length === 2) {
      // Handle 2-digit years: 00-29 -> 2000-2029, 30-99 -> 1930-1999
      const yearNum = parseInt(yearStr, 10);
      year = yearNum < 30 ? 2000 + yearNum : 1900 + yearNum;
    } else {
      year = parseInt(yearStr, 10);
    }
    
    // Validate year is in reasonable range
    if (year >= 1900 && year <= 2100) {
      return `${year}-01-01`;
    }
  }

  // Try to parse as a regular date (YYYY-MM-DD, MM/DD/YYYY, etc.)
  const date = new Date(dateString);
  if (!isNaN(date.getTime())) {
    const year = date.getFullYear();
    // Validate year is reasonable (not 0001, 0020, etc.)
    if (year >= 1900 && year <= 2100) {
      return date.toISOString().split("T")[0];
    }
  }

  return null; // Return null if unable to parse
}

// Validate date format before using it
function validateDateFormat(dateStr: string | null): string | null {
  if (!dateStr) return null;
  
  // Check if it matches YYYY-MM-DD format
  const dateFormatMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!dateFormatMatch) return null;
  
  const year = parseInt(dateFormatMatch[1], 10);
  const month = parseInt(dateFormatMatch[2], 10);
  const day = parseInt(dateFormatMatch[3], 10);
  
  // Validate ranges
  if (year < 1900 || year > 2100) return null;
  if (month < 1 || month > 12) return null;
  if (day < 1 || day > 31) return null;
  
  return dateStr;
}

// Helper function to truncate strings to fit database constraints
function truncateString(
  str: string | null | undefined,
  maxLength: number = 255,
): string | null {
  if (!str) return null;
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength - 3) + "...";
}

// Type definitions for AI service response
interface AIServiceResponse {
  status: string;
  candidate_id: string;
  name?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  summary?: string;
  websites?: string[];
  skills?: string[];
  work_experience?: Array<{
    job_title?: string;
    title?: string;
    company_name?: string;
    company?: string;
    start_date?: string;
    end_date?: string;
    is_current?: boolean;
    description?: string;
    location?: string;
  }>;
  education?: Array<{
    degree?: string;
    degree_name?: string;
    institution?: string;
    institution_name?: string;
    field_of_study?: string;
    start_year?: string;
    end_year?: string;
    start_date?: string;
    end_date?: string;
    gpa?: number;
  }>;
  locations?: string[];
  certifications?: string[];
  projects?: string[];
  confidence?: {
    overall: number;
    [key: string]: any;
  };
  model_results?: {
    deberta_extraction?: {
      work_experience?: any[];
      education?: any[];
      companies?: string[];
      job_titles?: string[];
      institutions?: string[];
      degrees?: string[];
      source?: string;
    };
  };
  error?: string;
  extraction_quality?: {
    extraction_quality_percentage?: number;
  };
}

// Redis connection configuration
const redisConfig = {
  host: process.env.REDIS_HOST || "localhost",
  port: parseInt(process.env.REDIS_PORT || "6379"),
  password: process.env.REDIS_PASSWORD || undefined,
  maxRetriesPerRequest: null,
  retryDelayOnFailover: 100,
  lazyConnect: true,
};

// Create Redis connection
const connection = new IORedis(redisConfig);

// AI Service URL
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || "http://localhost:8000";

// Helper function to update parsing job status in database
const updateParsingJobStatus = async (
  client: any,
  candidateId: string,
  status: string,
  confidenceScore?: number,
  parsedData?: any,
  errorMessage?: string,
): Promise<any> => {
  try {
    // Validate status value to prevent enum errors
    const validStatuses = ["pending", "processing", "completed", "failed"];
    const safeStatus = validStatuses.includes(status) ? status : "pending";

    const updateQuery = `
      UPDATE parsing_jobs 
      SET status = $1::parsing_job_status,
          confidence_score = COALESCE($2, confidence_score),
          parsed_data = COALESCE($3, parsed_data),
          error_message = COALESCE($4, error_message),
          completed_at = CASE WHEN $1::parsing_job_status IN ('completed', 'failed') THEN NOW() ELSE completed_at END
      WHERE candidate_id = $5
      RETURNING *
    `;

    const values = [
      safeStatus,
      confidenceScore || null,
      parsedData ? JSON.stringify(parsedData) : null,
      errorMessage || null,
      candidateId,
    ];

    const result = await client.query(updateQuery, values);
    return result.rows[0];
  } catch (error) {
    console.error("Error updating parsing job status:", error);
    throw error;
  }
};

// Helper function to update candidate with parsed data
const updateCandidateWithParsedData = async (
  client: any,
  candidateId: string,
  parsedData: AIServiceResponse,
  filePath?: string,
): Promise<any> => {
  try {
    // First check if raw_resume_text column exists
    const columnCheckQuery = `
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_name = 'candidates' 
      AND column_name = 'raw_resume_text'
    `;

    const columnCheck = await client.query(columnCheckQuery);
    const hasRawResumeText = columnCheck.rows.length > 0;

    // Calculate email hash
    const emailHash = parsedData.email
      ? crypto.createHash("md5").update(parsedData.email.trim().toLowerCase()).digest("hex")
      : null;

    // Calculate resume file hash (resume_hash)
    let resumeHash: string | null = null;
    if (filePath && fs.existsSync(filePath)) {
      try {
        const fileContent = fs.readFileSync(filePath);
        resumeHash = crypto.createHash("sha256").update(fileContent).digest("hex");
      } catch (err: any) {
        console.error("Failed to calculate file hash:", err.message);
      }
    }

    // Duplicate Detection logic: check if another parsed candidate has the same email hash or resume hash
    let reviewStatus = "pending";
    let duplicateCandidateId: string | null = null;

    if (emailHash) {
      const emailDupCheck = await client.query(
        "SELECT id FROM candidates WHERE email_hash = $1 AND id != $2 AND status = 'success'",
        [emailHash, candidateId]
      );
      if (emailDupCheck.rows.length > 0) {
        reviewStatus = "duplicate";
        duplicateCandidateId = emailDupCheck.rows[0].id;
        console.log(`[DUPLICATE] Candidate ${candidateId} has matching email hash with candidate ${duplicateCandidateId}`);
      }
    }

    if (!duplicateCandidateId && resumeHash) {
      const hashDupCheck = await client.query(
        "SELECT id FROM candidates WHERE resume_hash = $1 AND id != $2 AND status = 'success'",
        [resumeHash, candidateId]
      );
      if (hashDupCheck.rows.length > 0) {
        reviewStatus = "duplicate";
        duplicateCandidateId = hashDupCheck.rows[0].id;
        console.log(`[DUPLICATE] Candidate ${candidateId} has matching resume hash with candidate ${duplicateCandidateId}`);
      }
    }

    // Record relationship in duplicate_candidates table if duplicate is found
    if (duplicateCandidateId) {
      try {
        const [c1, c2] = [duplicateCandidateId, candidateId].sort();
        await client.query(
          `INSERT INTO duplicate_candidates (candidate_id_1, candidate_id_2, similarity_score, status)
           VALUES ($1, $2, $3, 'pending')
           ON CONFLICT (candidate_id_1, candidate_id_2) DO NOTHING`,
          [c1, c2, 1.0]
        );
      } catch (dupErr: any) {
        console.error("Failed to insert duplicate candidate relationship:", dupErr.message);
      }
    }

    const updateQuery = `
      UPDATE candidates 
      SET full_name = COALESCE($1, full_name),
          email = COALESCE($2, email),
          phone = COALESCE($3, phone),
          location = COALESCE($4, location),
          linkedin_url = COALESCE($5, linkedin_url),
          github_url = COALESCE($6, github_url),
          summary = COALESCE($7, summary),
          status = 'success',
          review_status = $8,
          email_hash = COALESCE($9, email_hash),
          resume_hash = COALESCE($10, resume_hash),
          resume_quality_score = COALESCE($11, resume_quality_score),
          confidence_score = COALESCE($12, confidence_score)${
            hasRawResumeText
              ? `,
          raw_resume_text = COALESCE($13, raw_resume_text)`
              : ""
          },
          updated_at = NOW()
      WHERE id = $${hasRawResumeText ? "14" : "13"}
      RETURNING *
    `;

    // Extract location from locations array or use first location
    const location =
      parsedData.locations && Array.isArray(parsedData.locations)
        ? parsedData.locations[0]
        : null;

    // Quality and confidence calculations
    const qualityScore = parsedData.extraction_quality?.extraction_quality_percentage
      ? Math.round(parsedData.extraction_quality.extraction_quality_percentage)
      : null;
    const confidenceScore = parsedData.confidence?.overall || null;

    const values = [
      truncateString(parsedData.name || null, 255),
      truncateString(parsedData.email || null, 255),
      truncateString(parsedData.phone || null, 50),
      truncateString(location || null, 255),
      truncateString(parsedData.linkedin || null, 500),
      truncateString(parsedData.github || null, 500),
      truncateString(parsedData.summary || null, 2000), // Summary might be TEXT
      reviewStatus,
      emailHash,
      resumeHash,
      qualityScore,
      confidenceScore,
    ];

    // Add raw_resume_text if column exists
    if (hasRawResumeText) {
      values.push(null); // raw_resume_text - not stored as a separate field
    }

    values.push(candidateId);

    const result = await client.query(updateQuery, values);

    // Insert skills if provided
    if (parsedData.skills && Array.isArray(parsedData.skills)) {
      // Check if candidate_skills table exists
      const tableCheck = await client.query(`
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'candidate_skills'
      `);

      if (tableCheck.rows.length > 0) {
        // First, delete existing skill associations for this candidate
        await client.query(
          "DELETE FROM candidate_skills WHERE candidate_id = $1",
          [candidateId],
        );

        // Insert new skill associations
        for (const skill of parsedData.skills) {
          const skillName =
            typeof skill === "string"
              ? skill
              : (skill as any).name || (skill as any).skill_name;

          // Check if skill already exists in global skills table
          const existingSkill = await client.query(
            "SELECT id FROM skills WHERE name = $1",
            [skillName],
          );

          let skillId: string;
          if (existingSkill.rows.length > 0) {
            // Use existing skill
            skillId = existingSkill.rows[0].id;
          } else {
            // Create new skill
            const newSkill = await client.query(
              "INSERT INTO skills (id, name, category) VALUES ($1, $2, $3) RETURNING id",
              [crypto.randomUUID(), skillName, "technical"],
            );
            skillId = newSkill.rows[0].id;
          }

          // Associate skill with candidate
          await client.query(
            "INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level) VALUES ($1, $2, $3)",
            [candidateId, skillId, "intermediate"],
          );
        }
      }
    }

    // Insert work experience if provided
    if (
      parsedData.work_experience &&
      Array.isArray(parsedData.work_experience)
    ) {
      // Check if work_experience table has candidate_id column
      const workColumnCheck = await client.query(`
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'work_experience' 
        AND column_name = 'candidate_id'
      `);

      if (workColumnCheck.rows.length > 0) {
        // First, delete existing work experience
        await client.query(
          "DELETE FROM work_experience WHERE candidate_id = $1",
          [candidateId],
        );

        // Insert new work experience
        for (const work of parsedData.work_experience) {
          const workQuery = `
          INSERT INTO work_experience (candidate_id, job_title, company_name, start_date, end_date, is_current, description, location)
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        `;
          await client.query(workQuery, [
            candidateId,
            truncateString(work.job_title || work.title, 255),
            truncateString(work.company_name || work.company, 255),
            validateDateFormat(parseDateString(work.start_date || null)),
            validateDateFormat(parseDateString(work.end_date || null)),
            work.is_current || false,
            truncateString(work.description || null, 1000), // Assuming description might be TEXT type
            truncateString(work.location || null, 255),
          ]);
        }
      }
    }

    // Insert education if provided
    if (parsedData.education && Array.isArray(parsedData.education)) {
      // Check if education table has candidate_id column
      const eduColumnCheck = await client.query(`
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'education' 
        AND column_name = 'candidate_id'
      `);

      if (eduColumnCheck.rows.length > 0) {
        // First, delete existing education
        await client.query("DELETE FROM education WHERE candidate_id = $1", [
          candidateId,
        ]);

        // Insert new education
        for (const edu of parsedData.education) {
          const eduQuery = `
            INSERT INTO education (id, candidate_id, degree, institution, field_of_study, start_date, end_date, gpa)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
          `;
          await client.query(eduQuery, [
            crypto.randomUUID(), // Generate UUID for education id
            candidateId,
            truncateString(edu.degree || edu.degree_name, 255),
            truncateString(edu.institution || edu.institution_name, 255),
            truncateString(edu.field_of_study || null, 255),
            validateDateFormat(parseDateString(edu.start_year || edu.start_date || null)),
            validateDateFormat(parseDateString(edu.end_year || edu.end_date || null)),
            edu.gpa || null,
          ]);
        }
      }
    }

    // Insert certifications if provided
    if (parsedData.certifications && Array.isArray(parsedData.certifications)) {
      try {
        // First delete existing certifications
        await client.query(
          "DELETE FROM certifications WHERE candidate_id = $1",
          [candidateId],
        );

        // Insert new certifications
        for (const certName of parsedData.certifications) {
          if (!certName || typeof certName !== "string") continue;
          await client.query(
            `INSERT INTO certifications (id, candidate_id, name) VALUES ($1, $2, $3)
             ON CONFLICT DO NOTHING`,
            [crypto.randomUUID(), candidateId, certName.trim()]
          );
        }
      } catch (certInsertErr: any) {
        console.warn("Could not save certifications:", certInsertErr.message);
      }
    }

    // Insert projects if provided
    if (parsedData.projects && Array.isArray(parsedData.projects) && parsedData.projects.length > 0) {
      try {
        await client.query(
          "UPDATE candidates SET projects = $1 WHERE id = $2",
          [JSON.stringify(parsedData.projects), candidateId]
        );
      } catch (projUpdateErr: any) {
        console.warn("Could not save projects:", projUpdateErr.message);
      }
    }

    return result.rows[0];
  } catch (error) {
    console.error("Error updating candidate with parsed data:", error);
    throw error;
  }
};

// Call AI service for resume parsing
const callAIService = async (
  filePath: string,
  fileType: string,
  candidateId: string,
  llmProvider?: string,
  forceOcr?: boolean,
): Promise<AIServiceResponse> => {
  try {
    const requestBody: any = {
      file_path: path.resolve(filePath),
      candidate_id: candidateId,
    };
    
    if (llmProvider) {
      requestBody.llm_provider = llmProvider;
    }
    
    if (forceOcr !== undefined) {
      requestBody.force_ocr = forceOcr;
    }
    
    console.log("=" + "=".repeat(79));
    console.log("🚀 CALLING AI SERVICE");
    console.log("URL:", `${AI_SERVICE_URL}/parse`);
    console.log("Request Body:", JSON.stringify(requestBody, null, 2));
    console.log("llmProvider value:", llmProvider);
    console.log("llmProvider type:", typeof llmProvider);
    console.log("llmProvider truthy:", !!llmProvider);
    console.log("=" + "=".repeat(79));
    
    const apiResponse = await fetch(`${AI_SERVICE_URL}/parse`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();
      throw new Error(
        `AI service returned ${apiResponse.status}: ${errorText}`,
      );
    }

    const result: AIServiceResponse =
      (await apiResponse.json()) as AIServiceResponse;
    return result;
  } catch (error) {
    console.error("Error calling AI service:", error);
    throw error;
  }
};

// The processor function for the worker
const processor: Processor<ParseJobData> = async (job: Job<ParseJobData>) => {
  const { candidateId, filePath, fileType, userId, llmProvider, forceOcr } = job.data;

  console.log(`🔄 Starting resume parsing for candidate ${candidateId}`);
  if (llmProvider) {
    console.log(`🤖 Using LLM provider: ${llmProvider}`);
  }

  const client = await getClient();

  try {
    // Update initial status and emit Socket.io event
    await updateParsingJobStatus(client, candidateId, "processing");
    await job.updateProgress(0);

    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 0,
        message: "Starting resume parsing...",
      });
    }

    // Step 1: Validate file exists (10%)
    await job.updateProgress(10);
    await updateParsingJobStatus(client, candidateId, "processing");

    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 10,
        message: "Validating resume file...",
      });
    }

    // Simulate file validation
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Step 2: Call AI service (10% - 70%)
    await updateParsingJobStatus(client, candidateId, "processing");
    await job.updateProgress(25);

    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 25,
        message: "Sending resume to AI service for analysis...",
      });
    }

    console.log(`🤖 Calling AI service for ${filePath}`);
    const aiResult = await callAIService(filePath, fileType, candidateId, llmProvider, forceOcr);

    // Log parse trace to verify which fields came from which source
    console.log('[PARSE TRACE]', 
      Object.entries(aiResult).map(([k, v]) => ({
        field: k,
        source: (aiResult as any)[`_${k}_source`] || 'unknown',
        hasValue: !!v
      }))
    );

    await updateParsingJobStatus(client, candidateId, "processing");
    await job.updateProgress(50);

    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 50,
        message: "AI analysis complete, processing results...",
      });
    }

    // Step 3: Process AI results (50% - 80%)
    if (!aiResult || aiResult.status !== "success") {
      throw new Error(
        `AI service returned ${aiResult?.status || "unknown"} status: ${aiResult?.error || "Unknown error"}`,
      );
    }

    await updateParsingJobStatus(client, candidateId, "processing");
    await job.updateProgress(75);

    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 75,
        message: "Updating candidate profile with parsed data...",
      });
    }

    // Step 4: Update database with parsed data (80% - 100%)
    const confidenceScore: number = aiResult.confidence?.overall || 0.8;

    // Update candidate with parsed information
    await updateCandidateWithParsedData(client, candidateId, aiResult, filePath);

    await updateParsingJobStatus(client, candidateId, "processing");
    await job.updateProgress(90);

    if (userId) {
      emitParsingProgress(userId, {
        candidateId,
        progress: 90,
        message: "Finalizing resume parsing...",
      });
    }

    // Mark as success
    await updateParsingJobStatus(
      client,
      candidateId,
      "completed",
      confidenceScore,
      aiResult,
    );

    await job.updateProgress(100);

    console.log(`✅ Successfully parsed resume for candidate ${candidateId}`);

    // Emit completion event
    if (userId) {
      emitParsingComplete(userId, {
        candidateId,
        data: aiResult,
      });
    }

    return {
      success: true,
      candidateId,
      confidenceScore,
      parsedData: aiResult,
    };
  } catch (error) {
    console.error(
      `❌ Failed to parse resume for candidate ${candidateId}:`,
      error,
    );

    // Update with error status
    await updateParsingJobStatus(
      client,
      candidateId,
      "failed",
      undefined,
      undefined,
      error instanceof Error ? error.message : "Unknown error",
    );

    // Emit failure event
    if (userId) {
      emitParsingFailed(userId, {
        candidateId,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }

    // Re-throw the error to mark job as failed
    throw error;
  } finally {
    client.release();
  }
};

// Create the worker
export const parseWorker = new Worker<ParseJobData>(
  "resume-parsing",
  processor,
  {
    connection: redisConfig,
    concurrency: parseInt(process.env.PARSE_WORKER_CONCURRENCY || "2"), // Process 2 jobs concurrently
    limiter: {
      max: 10,
      duration: 60000, // Max 10 jobs per minute
    },
  },
);

// Worker event handlers
parseWorker.on("completed", (job: Job, result: any) => {
  console.log(
    `🎉 Job ${job.id} completed for candidate ${job.data.candidateId}`,
  );
});

parseWorker.on("failed", (job: Job | undefined, err: Error) => {
  const candidateId = job?.data.candidateId || "unknown";
  console.error(
    `💥 Job ${job?.id} failed for candidate ${candidateId}:`,
    err.message,
  );
});

parseWorker.on("error", (err) => {
  console.error("❌ Worker error:", err);
});

parseWorker.on("ready", () => {
  console.log("🚀 Parse worker is ready and listening for jobs");
});

// Progress updates
parseWorker.on("progress", (job: Job<ParseJobData>, progress: any) => {
  const progressNum =
    typeof progress === "number" ? progress : parseInt(progress.toString());
  console.log(
    `📊 Job ${job.id} progress: ${progressNum}% for candidate ${job.data.candidateId}`,
  );
});

// Graceful shutdown
export const closeWorker = async () => {
  console.log("🔄 Closing parse worker...");
  await parseWorker.close();
  await connection.quit();
  console.log("🔌 Parse worker and Redis connection closed");
};

// Handle process termination
process.on("SIGTERM", async () => {
  console.log("🔄 SIGTERM received, shutting down worker gracefully");
  await closeWorker();
  process.exit(0);
});

process.on("SIGINT", async () => {
  console.log("🔄 SIGINT received, shutting down worker gracefully");
  await closeWorker();
  process.exit(0);
});

export default parseWorker;
