const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function checkCandidateSkillsTable() {
  try {
    console.log("🔍 Checking candidate_skills table structure...");
    
    // Check if candidate_skills table exists
    const tableCheck = await pool.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'candidate_skills' AND table_schema = 'public'
      ORDER BY ordinal_position
    `);
    
    if (tableCheck.rows.length === 0) {
      console.log("❌ candidate_skills table doesn't exist");
    } else {
      console.log("📋 candidate_skills table columns:");
      tableCheck.rows.forEach(column => {
        console.log(`  - ${column.column_name}: ${column.data_type} (${column.is_nullable})`);
      });
    }
    
    // Check skills table structure
    const skillsTableCheck = await pool.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'skills' AND table_schema = 'public'
      ORDER BY ordinal_position
    `);
    
    if (skillsTableCheck.rows.length === 0) {
      console.log("❌ skills table doesn't exist");
    } else {
      console.log("📋 skills table columns:");
      skillsTableCheck.rows.forEach(column => {
        console.log(`  - ${column.column_name}: ${column.data_type} (${column.is_nullable})`);
      });
    }
    
    // Check certifications table
    const certTableCheck = await pool.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'certifications' AND table_schema = 'public'
      ORDER BY ordinal_position
    `);
    
    if (certTableCheck.rows.length === 0) {
      console.log("❌ certifications table doesn't exist");
    } else {
      console.log("📋 certifications table columns:");
      certTableCheck.rows.forEach(column => {
        console.log(`  - ${column.column_name}: ${column.data_type} (${column.is_nullable})`);
      });
    }
    
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await pool.end();
  }
}

checkCandidateSkillsTable();