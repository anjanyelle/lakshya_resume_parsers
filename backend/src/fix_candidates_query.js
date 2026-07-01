const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function testCandidatesQuery() {
  try {
    console.log("🔍 Testing basic candidates query...");
    
    // Simple query that should work
    const basicQuery = `
      SELECT 
        id, 
        full_name, 
        email, 
        phone, 
        location, 
        status, 
        created_at, 
        updated_at
      FROM candidates 
      WHERE status IN ('success', 'completed', 'pending', 'processing', 'failed')
      ORDER BY created_at DESC 
      LIMIT 20
    `;
    
    const result = await pool.query(basicQuery);
    
    console.log(`✅ Query successful! Found ${result.rows.length} candidates`);
    
    if (result.rows.length > 0) {
      console.log("📋 Sample candidate data:");
      console.log(JSON.stringify(result.rows[0], null, 2));
    }
    
    // Test the problematic query from the model
    console.log("\n🔍 Testing the model's complex query...");
    
    const modelQuery = `
      SELECT 
        candidates.*,
        pj.status as pj_status,
        pj.confidence_score as pj_confidence_score,
        pj.error_message as pj_error_message
      FROM candidates
      LEFT JOIN parsing_jobs pj ON candidates.id = pj.candidate_id
      WHERE candidates.status IN ('success', 'completed', 'pending', 'processing', 'failed')
      ORDER BY candidates.created_at DESC
      LIMIT 20
    `;
    
    try {
      const modelResult = await pool.query(modelQuery);
      console.log(`✅ Model query successful! Found ${modelResult.rows.length} candidates`);
    } catch (modelError) {
      console.error("❌ Model query failed:", modelError.message);
      console.log("🔧 This is likely the cause of the 500 error");
    }
    
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await pool.end();
  }
}

testCandidatesQuery();