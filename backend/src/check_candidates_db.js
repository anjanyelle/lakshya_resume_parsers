const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'resume_parser',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
});

async function checkSchema() {
  try {
    const result = await pool.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns 
      WHERE table_name = 'candidates' 
      ORDER BY ordinal_position
    `);
    
    console.log('Candidates table schema:');
    result.rows.forEach(row => {
      console.log(`- ${row.column_name}: ${row.data_type} (${row.is_nullable}) ${row.column_default || ''}`);
    });

    const statusCounts = await pool.query(`
      SELECT status, count(*) FROM candidates GROUP BY status
    `);
    console.log('\nStatus counts:');
    statusCounts.rows.forEach(row => {
      console.log(`- ${row.status}: ${row.count}`);
    });

  } catch (error) {
    console.error('Error checking schema:', error);
  } finally {
    await pool.end();
  }
}

checkSchema();
