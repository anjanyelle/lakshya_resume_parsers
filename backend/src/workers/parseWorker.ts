import { Worker, Job, Processor } from "bullmq";
import IORedis from "ioredis";
import path from "path";
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
}

import { redisConfig, createRedisConnection } from "../config/redisConfig";

// Create Redis connection
const connection = createRedisConnection();



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
      SET status = $1,
          confidence_score = COALESCE($2, confidence_score),
          parsed_data = COALESCE($3, parsed_data),
          error_message = COALESCE($4, error_message),
          completed_at = CASE WHEN $1 IN ('completed', 'failed') THEN NOW() ELSE completed_at END
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
          updated_at = NOW()
      WHERE id = $8
      RETURNING *
    `;

    // Extract location from locations array or use first location
    const location =
      parsedData.locations && Array.isArray(parsedData.locations)
        ? parsedData.locations[0]
        : null;

    const values = [
      truncateString(parsedData.name || null, 255),
      truncateString(parsedData.email || null, 255),
      truncateString(parsedData.phone || null, 50),
      truncateString(location || null, 255),
      truncateString(parsedData.linkedin || null, 500),
      truncateString(parsedData.github || null, 500),
      truncateString(parsedData.summary || null, 2000),
      candidateId,
    ];

    const result = await client.query(updateQuery, values);

    // Insert skills if provided (using skills table from setup.sql)
    if (parsedData.skills && Array.isArray(parsedData.skills)) {
      // First, delete existing skills for this candidate
      await client.query("DELETE FROM skills WHERE candidate_id = $1", [candidateId]);

      // Insert new skills
      for (const skill of parsedData.skills) {
        const skillName = typeof skill === "string" ? skill : (skill as any).name || (skill as any).skill_name;
        
        await client.query(
          "INSERT INTO skills (candidate_id, skill_name, category, proficiency_level) VALUES ($1, $2, $3, $4)",
          [candidateId, truncateString(skillName, 255), "technical", "intermediate"]
        );
      }
    }

    // Insert work experience if provided
    if (parsedData.work_experience && Array.isArray(parsedData.work_experience)) {
      // First, delete existing work experience
      await client.query("DELETE FROM work_experience WHERE candidate_id = $1", [candidateId]);

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
          truncateString(work.description || null, 2000),
          truncateString(work.location || null, 255),
        ]);
      }
    }

    // Insert education if provided
    if (parsedData.education && Array.isArray(parsedData.education)) {
      // First, delete existing education
      await client.query("DELETE FROM education WHERE candidate_id = $1", [candidateId]);

      // Insert new education
      for (const edu of parsedData.education) {
        const eduQuery = `
          INSERT INTO education (candidate_id, degree, institution, field_of_study, start_date, end_date, gpa)
          VALUES ($1, $2, $3, $4, $5, $6, $7)
        `;
        await client.query(eduQuery, [
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
): Promise<AIServiceResponse> => {
  try {
    const requestBody: any = {
      file_path: path.resolve(filePath),
      candidate_id: candidateId,
    };
    
    if (llmProvider) {
      requestBody.llm_provider = llmProvider;
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
  const { candidateId, filePath, fileType, userId, llmProvider } = job.data;

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
    const aiResult = await callAIService(filePath, fileType, candidateId, llmProvider);

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
    await updateCandidateWithParsedData(client, candidateId, aiResult);

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
    connection,
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
