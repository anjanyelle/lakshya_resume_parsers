const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');
require('dotenv').config();

// Use DATABASE_URL if available, otherwise fall back to individual parameters
const connectionString = process.env.DATABASE_URL || 
  `postgresql://${process.env.DB_USER || "postgres"}:${process.env.DB_PASSWORD || ""}@${process.env.DB_HOST || "localhost"}:${process.env.DB_PORT || "5432"}/${process.env.DB_NAME || "resume_parser"}`;

const pool = new Pool({
  connectionString: connectionString
});

async function runMigration() {
  const migrationPath = path.join(__dirname, 'database', 'migrations', '017_add_job_descriptions_columns.sql');
  
  try {
    console.log('Reading migration file...');
    const sql = fs.readFileSync(migrationPath, 'utf8');
    
    console.log('Connecting to database...');
    await pool.connect();
    
    console.log('Executing migration...');
    await pool.query(sql);
    
    console.log('✅ Migration completed successfully!');
    console.log('Added missing columns to job_descriptions table');
  } catch (error) {
    console.error('❌ Migration failed:', error);
    throw error;
  } finally {
    await pool.end();
  }
}

runMigration().catch(console.error);
