const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function checkTables() {
  try {
    console.log("🔍 Checking database tables...");
    
    const result = await pool.query(`
      SELECT table_name, table_schema 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name
    `);
    
    console.log("📋 Available tables:");
    result.rows.forEach(row => {
      console.log(`  - ${row.table_name}`);
    });
    
    // Check if candidates table exists and get its structure
    const candidatesTable = result.rows.find(row => row.table_name === 'candidates');
    if (candidatesTable) {
      console.log("\n🔍 Checking candidates table structure...");
      const columnsResult = await pool.query(`
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'candidates' 
        ORDER BY ordinal_position
      `);
      
      console.log("📋 Candidates table columns:");
      columnsResult.rows.forEach(row => {
        console.log(`  - ${row.column_name}: ${row.data_type} (${row.is_nullable})`);
      });
    }
    
    // Check if there are any candidates in the table
    const countResult = await pool.query("SELECT COUNT(*) as count FROM candidates");
    console.log(`\n📊 Total candidates in database: ${countResult.rows[0].count}`);
    
  } catch (error) {
    console.error("❌ Error checking tables:", error.message);
  } finally {
    await pool.end();
  }
}

checkTables();