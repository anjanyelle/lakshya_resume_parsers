const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function checkEducationTable() {
  try {
    console.log("🔍 Checking education table structure...");
    
    // Check education table structure
    const tableCheck = await pool.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns 
      WHERE table_name = 'education' AND table_schema = 'public'
      ORDER BY ordinal_position
    `);
    
    if (tableCheck.rows.length === 0) {
      console.log("❌ education table doesn't exist");
    } else {
      console.log("📋 education table columns:");
      tableCheck.rows.forEach(column => {
        const nullable = column.is_nullable === 'YES' ? 'NULL' : 'NOT NULL';
        const default_val = column.column_default ? `DEFAULT ${column.column_default}` : '';
        console.log(`  - ${column.column_name}: ${column.data_type} (${nullable}) ${default_val}`);
      });
    }
    
    // Check for any constraints
    const constraintsCheck = await pool.query(`
      SELECT constraint_name, constraint_type
      FROM information_schema.table_constraints 
      WHERE table_name = 'education' AND table_schema = 'public'
    `);
    
    if (constraintsCheck.rows.length > 0) {
      console.log("📋 education table constraints:");
      constraintsCheck.rows.forEach(constraint => {
        console.log(`  - ${constraint.constraint_name}: ${constraint.constraint_type}`);
      });
    }
    
    // Check if there are any recent education entries
    const recentEntries = await pool.query(`
      SELECT COUNT(*) as count FROM education 
      WHERE created_at > NOW() - INTERVAL '1 hour'
    `);
    
    console.log(`📊 Recent education entries (last hour): ${recentEntries.rows[0].count}`);
    
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await pool.end();
  }
}

checkEducationTable();