const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

async function runMigration() {
  const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'resume_parser',
    password: 'Surya@123',
    port: 5432,
  });

  try {
    console.log('Running migration: 007_fix_parsing_job_status_v2.sql');
    
    // Read the migration file
    const migrationPath = path.join(__dirname, 'migrations', '007_fix_parsing_job_status_v2.sql');
    const migrationSQL = fs.readFileSync(migrationPath, 'utf8');
    
    // Execute the migration
    await pool.query(migrationSQL);
    
    console.log('Migration completed successfully!');
  } catch (error) {
    console.error('Migration failed:', error);
  } finally {
    await pool.end();
  }
}

runMigration();
