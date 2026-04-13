const { Pool } = require('pg');

async function fixEnum() {
  const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'resume_parser',
    password: 'Surya@123',
    port: 5432,
  });

  try {
    console.log('Fixing parsing_job_status enum...');
    
    // First, check what enum values exist
    const enumCheck = await pool.query(`
      SELECT enumlabel 
      FROM pg_enum 
      WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'parsing_job_status')
      ORDER BY enumlabel
    `);
    
    console.log('Current enum values:', enumCheck.rows.map(r => r.enumlabel));
    
    // Add 'completed' to the enum if it doesn't exist
    if (!enumCheck.rows.some(row => row.enumlabel === 'completed')) {
      console.log('Adding "completed" to enum...');
      await pool.query("ALTER TYPE parsing_job_status ADD VALUE 'completed'");
      console.log('Added "completed" to enum');
    }
    
    // Add 'failed' to the enum if it doesn't exist
    if (!enumCheck.rows.some(row => row.enumlabel === 'failed')) {
      console.log('Adding "failed" to enum...');
      await pool.query("ALTER TYPE parsing_job_status ADD VALUE 'failed'");
      console.log('Added "failed" to enum');
    }
    
    // Check final enum values
    const finalCheck = await pool.query(`
      SELECT enumlabel 
      FROM pg_enum 
      WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'parsing_job_status')
      ORDER BY enumlabel
    `);
    
    console.log('Final enum values:', finalCheck.rows.map(r => r.enumlabel));
    console.log('Enum fix completed successfully!');
    
  } catch (error) {
    console.error('Enum fix failed:', error);
  } finally {
    await pool.end();
  }
}

fixEnum();
