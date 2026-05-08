import { Pool, PoolClient } from "pg";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Check if connection string is provided
const connectionString = process.env.DATABASE_URL;

const poolConfig = connectionString 
  ? { 
      connectionString,
      ssl: {
        rejectUnauthorized: false
      }
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

export default pool;
