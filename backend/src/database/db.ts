import { Pool, PoolClient } from "pg";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Check if connection string is provided
const connectionString = process.env.DATABASE_URL;

const poolConfig = connectionString 
  ? { 
      connectionString,
      ssl: connectionString.includes("localhost") || connectionString.includes("127.0.0.1")
        ? false
        : { rejectUnauthorized: false }
    }
  : {
      host: process.env.DB_HOST || "localhost",
      port: parseInt(process.env.DB_PORT || "5432"),
      database: process.env.DB_NAME || "resume_parser",
      user: process.env.DB_USER || "postgres",
      password: process.env.DB_PASSWORD || "",
      max: 10,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 5000,
    };

// Debug: Log the config (without password)
console.log("🔍 DB Config:", connectionString ? "Using DATABASE_URL" : {
  host: poolConfig.host,
  port: poolConfig.port,
  database: poolConfig.database,
  user: poolConfig.user,
});

if (connectionString) {
  console.log("🔍 DATABASE_URL is set");
}

const pool = new Pool(poolConfig);

pool.on("error", (err: Error) => {
  console.error("Unexpected error on idle PostgreSQL client", err);
  process.exit(-1);
});

export const query = (text: string, params?: unknown[]) =>
  pool.query(text, params);

export const getClient = (): Promise<PoolClient> => pool.connect();

export const transaction = async <T>(
  fn: (client: PoolClient) => Promise<T>,
): Promise<T> => {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await fn(client);
    await client.query("COMMIT");
    return result;
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
};

// Auto-migration function to ensure production DB has correct schema
const ensureSchema = async () => {
  try {
    const client = await pool.connect();
    try {
      console.log("🚀 Running auto-migrations...");
      
      // Add status column if missing
      await client.query(`
        ALTER TABLE candidates 
        ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending',
        ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255) DEFAULT 'default',
        ADD COLUMN IF NOT EXISTS consent_given BOOLEAN DEFAULT TRUE,
        ADD COLUMN IF NOT EXISTS review_status VARCHAR(50) DEFAULT 'pending';
      `);
      
      // Fix work_history / work_experience mismatch
      // First check if work_experience exists
      const expTableCheck = await client.query(`
        SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_experience');
      `);
      
      // Then check if work_history exists
      const histTableCheck = await client.query(`
        SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_history');
      `);

      if (expTableCheck.rows[0].exists && !histTableCheck.rows[0].exists) {
        await client.query("ALTER TABLE work_experience RENAME TO work_history;");
        console.log("✅ Renamed work_experience to work_history");
      }
      
      // Ensure parsing_jobs exists and has all columns
      await client.query(`
        CREATE TABLE IF NOT EXISTS parsing_jobs (
          id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
          candidate_id UUID NOT NULL REFERENCES candidates (id) ON DELETE CASCADE,
          status VARCHAR(50) NOT NULL DEFAULT 'pending',
          confidence_score DECIMAL(5,4),
          parsed_data JSONB,
          error_message TEXT,
          filename TEXT,
          file_path TEXT,
          started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          completed_at TIMESTAMP WITH TIME ZONE
        );
      `);

      // Add missing columns to parsing_jobs if it already existed
      await client.query(`
        ALTER TABLE parsing_jobs 
        ADD COLUMN IF NOT EXISTS filename TEXT,
        ADD COLUMN IF NOT EXISTS file_path TEXT,
        ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
      `);

      console.log("✅ Auto-migrations completed");
    } finally {
      client.release();
    }
  } catch (err) {
    console.error("❌ Auto-migration failed:", err);
  }
};

// Run migrations on startup
ensureSchema();

export default pool;
