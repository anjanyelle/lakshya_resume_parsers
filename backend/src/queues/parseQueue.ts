import { Queue, QueueOptions } from "bullmq";
import IORedis from "ioredis";

// Redis connection configuration
const redisConfig = {
  host: process.env.REDIS_HOST || "localhost",
  port: parseInt(process.env.REDIS_PORT || "6379"),
  password: process.env.REDIS_PASSWORD || undefined,
  maxRetriesPerRequest: null, // BullMQ requires null
  retryDelayOnFailover: 100,
  lazyConnect: true,
};

// Create Redis connection
const connection = new IORedis(redisConfig);

// Queue options with retry and timeout configuration
const queueOptions: QueueOptions = {
  connection: redisConfig,
  defaultJobOptions: {
    removeOnComplete: 50, // Keep last 50 completed jobs
    removeOnFail: 100, // Keep last 100 failed jobs
    attempts: 3, // 3 retry attempts
    backoff: {
      type: "exponential",
      delay: 2000, // Start with 2 seconds, then exponential
    },
    delay: 0, // No initial delay
  },
};

// Create the resume parsing queue
export const parseQueue = new Queue("resume-parsing", queueOptions);

// Job data interface
export interface ParseJobData {
  candidateId: string;
  filePath: string;
  fileType: string;
  userId?: string;
}

// Add a new parsing job to the queue
export const addParsingJob = async (
  candidateId: string,
  filePath: string,
  fileType: string,
  userId?: string,
): Promise<string> => {
  const jobData: ParseJobData = {
    candidateId,
    filePath,
    fileType,
    userId,
  };

  const job = await parseQueue.add("parse-resume", jobData, {
    // Job-specific options can override defaults
    attempts: 3,
    backoff: {
      type: "exponential",
      delay: 2000,
    },
    // Add job identifier for tracking
    jobId: `parse-${candidateId}-${Date.now()}`,
  });

  console.log(`📋 Added parsing job ${job.id} for candidate ${candidateId}`);
  return job.id!;
};

// Get job status and progress
export const getJobStatus = async (jobId: string) => {
  const job = await parseQueue.getJob(jobId);
  if (!job) {
    return null;
  }

  return {
    id: job.id,
    name: job.name,
    data: job.data,
    progress: job.progress,
    processedOn: job.processedOn,
    finishedOn: job.finishedOn,
    failedReason: job.failedReason,
    returnvalue: job.returnvalue,
    state: await job.getState(),
  };
};

// Get all jobs for a candidate
export const getCandidateJobs = async (candidateId: string) => {
  const jobs = await parseQueue.getJobs(
    ["waiting", "active", "completed", "failed"],
    0,
    -1,
    true,
  );
  return jobs.filter((job) => job.data.candidateId === candidateId);
};

// Pause the queue (useful for maintenance)
export const pauseQueue = async () => {
  await parseQueue.pause();
  console.log("⏸️  Resume parsing queue paused");
};

// Resume the queue
export const resumeQueue = async () => {
  await parseQueue.resume();
  console.log("▶️  Resume parsing queue resumed");
};

// Clean up completed jobs older than specified age
export const cleanCompletedJobs = async (age: number = 24 * 60 * 60 * 1000) => {
  const deleted = await parseQueue.clean(age, 0, "completed");
  console.log(`🧹 Cleaned ${deleted} completed jobs older than ${age}ms`);
  return deleted;
};

// Clean up failed jobs older than specified age
export const cleanFailedJobs = async (
  age: number = 7 * 24 * 60 * 60 * 1000,
) => {
  const deleted = await parseQueue.clean(age, 0, "failed");
  console.log(`🧹 Cleaned ${deleted} failed jobs older than ${age}ms`);
  return deleted;
};

// Get queue statistics
export const getQueueStats = async () => {
  const [waiting, active, completed, failed, delayed] = await Promise.all([
    parseQueue.getWaiting(),
    parseQueue.getActive(),
    parseQueue.getCompleted(),
    parseQueue.getFailed(),
    parseQueue.getDelayed(),
  ]);

  return {
    waiting: waiting.length,
    active: active.length,
    completed: completed.length,
    failed: failed.length,
    delayed: delayed.length,
    total:
      waiting.length +
      active.length +
      completed.length +
      failed.length +
      delayed.length,
  };
};

// Graceful shutdown
export const closeQueue = async () => {
  await parseQueue.close();
  await connection.quit();
  console.log("🔌 Parse queue and Redis connection closed");
};

// Error handling
parseQueue.on("error", (err) => {
  console.error("❌ Queue error:", err);
});

connection.on("error", (err) => {
  console.error("❌ Redis connection error:", err);
});

connection.on("connect", () => {
  console.log("🔗 Redis connected successfully");
});

export default parseQueue;
