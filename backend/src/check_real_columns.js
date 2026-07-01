const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function checkRealColumns() {
  try {
    console.log("🔍 Checking actual columns in candidates table...");
    
    // Get all columns in candidates table
    const columnsQuery = `
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns 
      WHERE table_name = 'candidates' AND table_schema = 'public'
      ORDER BY ordinal_position
    `;
    
    const result = await pool.query(columnsQuery);
    
    console.log("📋 Actual columns in candidates table:");
    console.log("=====================================");
    
    result.rows.forEach(column => {
      const nullable = column.is_nullable === 'YES' ? 'NULL' : 'NOT NULL';
      const default_val = column.column_default ? `DEFAULT ${column.column_default}` : '';
      console.log(`${column.column_name}: ${column.data_type} (${nullable}) ${default_val}`);
    });
    
    // Now get a sample candidate with only existing columns
    console.log("\n🔍 Getting sample candidate data with existing columns...");
    
    const sampleQuery = `
      SELECT 
        id,
        full_name,
        email,
        phone,
        location,
        linkedin_url,
        github_url,
        portfolio_url,
        summary,
        years_experience,
        current_title,
        current_company,
        education_degrees,
        universities,
        companies,
        job_titles,
        expected_salary_min,
        expected_salary_max,
        raw_resume_text,
        file_path,
        file_type,
        projects,
        total_experience_years,
        status,
        created_at,
        updated_at
      FROM candidates 
      WHERE id = '93f067b5-33a0-426a-a296-40b10a5eef08'
    `;
    
    const sampleResult = await pool.query(sampleQuery);
    
    if (sampleResult.rows.length > 0) {
      const candidate = sampleResult.rows[0];
      console.log("📋 Sample Candidate Data:");
      console.log("=====================================");
      
      Object.keys(candidate).forEach(key => {
        const value = candidate[key];
        const status = value === null ? "❌ NULL" : 
                     value === "" ? "⚪ EMPTY" : 
                     Array.isArray(value) && value.length === 0 ? "📦 EMPTY ARRAY" : 
                     "✅ HAS DATA";
        
        console.log(`${key}: ${status}`);
        
        if (value !== null && value !== "" && (!Array.isArray(value) || value.length > 0)) {
          if (typeof value === 'object') {
            console.log(`   Value: ${JSON.stringify(value, null, 2).substring(0, 100)}...`);
          } else if (typeof value === 'string' && value.length > 50) {
            console.log(`   Value: ${value.substring(0, 100)}...`);
          } else {
            console.log(`   Value: ${value}`);
          }
        }
      });
    }
    
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await pool.end();
  }
}

checkRealColumns();