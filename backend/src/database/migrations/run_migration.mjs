import { Pool } from 'pg';
import { config } from 'dotenv';

// Load environment variables
config();

// Database connection config
const poolConfig = {
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
};

const pool = new Pool(poolConfig);

async function runMigration() {
  const client = await pool.connect();
  
  try {
    console.log('Starting migration to fix parsing_job_status enum...');
    
    // First, update any existing invalid status values to valid ones
    await client.query(`
      UPDATE parsing_jobs 
      SET status = 'pending' 
      WHERE status NOT IN ('pending', 'processing', 'completed', 'failed')
    `);
    console.log('Updated existing invalid status values');

    // Check if there's an enum type that needs to be updated
    const enumCheck = await client.query(`
      SELECT 1 FROM pg_type WHERE typname = 'parsing_job_status'
    `);
    
    if (enumCheck.rows.length > 0) {
      console.log('Found parsing_job_status enum, adding missing values...');
      
      // Add 'completed' to the enum if it doesn't exist
      try {
        await client.query(`ALTER TYPE parsing_job_status ADD VALUE 'completed'`);
        console.log('Added "completed" to enum');
      } catch (err) {
        if (err.code !== '42710') { // Ignore "duplicate key value" error
          console.log('Error adding completed:', err.message);
        }
      }
      
      // Add 'failed' to the enum if it doesn't exist
      try {
        await client.query(`ALTER TYPE parsing_job_status ADD VALUE 'failed'`);
        console.log('Added "failed" to enum');
      } catch (err) {
        if (err.code !== '42710') { // Ignore "duplicate key value" error
          console.log('Error adding failed:', err.message);
        }
      }
      
      // Add 'processing' to the enum if it doesn't exist
      try {
        await client.query(`ALTER TYPE parsing_job_status ADD VALUE 'processing'`);
        console.log('Added "processing" to enum');
      } catch (err) {
        if (err.code !== '42710') { // Ignore "duplicate key value" error
          console.log('Error adding processing:', err.message);
        }
      }
      
      // Add 'pending' to the enum if it doesn't exist
      try {
        await client.query(`ALTER TYPE parsing_job_status ADD VALUE 'pending'`);
        console.log('Added "pending" to enum');
      } catch (err) {
        if (err.code !== '42710') { // Ignore "duplicate key value" error
          console.log('Error adding pending:', err.message);
        }
      }
    }

    // Drop and recreate the constraint to be sure
    await client.query(`ALTER TABLE parsing_jobs DROP CONSTRAINT IF EXISTS parsing_jobs_status_check`);
    await client.query(`
      ALTER TABLE parsing_jobs 
      ADD CONSTRAINT parsing_jobs_status_check 
      CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
    `);
    console.log('Recreated parsing_jobs_status_check constraint');

    // Ensure the table structure is correct
    // Make sure status column exists
    await client.query(`
      DO $$
      BEGIN
        IF NOT EXISTS (
          SELECT 1 FROM information_schema.columns 
          WHERE table_name = 'parsing_jobs' AND column_name = 'status'
        ) THEN
          ALTER TABLE parsing_jobs ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'pending';
        END IF;
      END $$;
    `);
    console.log('Ensured status column exists');

    console.log('Migration completed successfully!');
    
    // Show current enum values
    if (enumCheck.rows.length > 0) {
      const enumValues = await client.query(`
        SELECT enumlabel FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'parsing_job_status')
        ORDER BY enumlabel
      `);
      console.log('Current enum values:', enumValues.rows.map(r => r.enumlabel));
    }
    
  } catch (error) {
    console.error('Migration failed:', error);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

runMigration()
  .then(() => {
    console.log('Migration completed');
    process.exit(0);
  })
  .catch((err) => {
    console.error('Migration failed:', err);
    process.exit(1);
  });
