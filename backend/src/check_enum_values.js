const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function checkEnumValues() {
  try {
    console.log("🔍 Checking enum values for candidate_status...");
    
    // Check the enum type definition
    const enumQuery = `
      SELECT unnest(enum_range(NULL::candidate_status)) as status_values;
    `;
    
    try {
      const result = await pool.query(enumQuery);
      console.log("📋 Valid candidate_status values:");
      result.rows.forEach(row => {
        console.log(`  - '${row.status_values}'`);
      });
    } catch (error) {
      console.log("🔍 Checking actual status values in the database...");
      
      // Get distinct status values from the candidates table
      const distinctQuery = `
        SELECT DISTINCT status, COUNT(*) as count 
        FROM candidates 
        WHERE status IS NOT NULL 
        GROUP BY status 
        ORDER BY count DESC
      `;
      
      const result = await pool.query(distinctQuery);
      console.log("📋 Actual status values in database:");
      result.rows.forEach(row => {
        console.log(`  - '${row.status}': ${row.count} candidates`);
      });
    }
    
    // Test a simple query with valid status values
    console.log("\n🔍 Testing query with valid status values...");
    const testQuery = `
      SELECT COUNT(*) as count 
      FROM candidates 
      WHERE status IS NOT NULL
      LIMIT 1
    `;
    
    const testResult = await pool.query(testQuery);
    console.log(`✅ Found ${testResult.rows[0].count} candidates with valid status`);
    
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await pool.end();
  }
}

checkEnumValues();