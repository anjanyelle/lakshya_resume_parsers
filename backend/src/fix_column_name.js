const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'resume_parser',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
});

async function fixColumnName() {
  try {
    // Rename password_hash to hashed_password
    await pool.query('ALTER TABLE users RENAME COLUMN password_hash TO hashed_password');
    console.log('Successfully renamed password_hash to hashed_password');
    
    // Verify the change
    const result = await pool.query(`
      SELECT column_name, data_type
      FROM information_schema.columns 
      WHERE table_name = 'users' AND column_name IN ('password_hash', 'hashed_password')
      ORDER BY column_name
    `);
    
    console.log('Updated columns:');
    result.rows.forEach(row => {
      console.log(`- ${row.column_name}: ${row.data_type}`);
    });
  } catch (error) {
    console.error('Error fixing column name:', error);
  } finally {
    await pool.end();
  }
}

fixColumnName();
