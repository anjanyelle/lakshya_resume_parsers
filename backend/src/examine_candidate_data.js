const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function examineCandidateData() {
  try {
    console.log("🔍 Examining candidate data in database...");
    
    // Get a specific candidate to examine
    const candidateQuery = `
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
        skills,
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
        status
      FROM candidates 
      WHERE id = '93f067b5-33a0-426a-a296-40b10a5eef08'
    `;
    
    const result = await pool.query(candidateQuery);
    
    if (result.rows.length > 0) {
      const candidate = result.rows[0];
      console.log("📋 Candidate Data Analysis:");
      console.log("=====================================");
      
      // Check each field
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
      
      // Check raw resume text
      if (candidate.raw_resume_text) {
        console.log("\n📄 Raw Resume Text Sample:");
        console.log(candidate.raw_resume_text.substring(0, 500) + "...");
      }
      
      // Check work history for this candidate
      console.log("\n💼 Work History:");
      const workHistoryQuery = `
        SELECT * FROM work_history 
        WHERE candidate_id = '93f067b5-33a0-426a-a296-40b10a5eef08'
      `;
      
      const workResult = await pool.query(workHistoryQuery);
      workResult.rows.forEach((work, index) => {
        console.log(`  ${index + 1}. ${work.job_title} at ${work.company_name}`);
        console.log(`     Start: ${work.start_date}, End: ${work.end_date || 'Current'}`);
      });
      
      // Check skills for this candidate
      console.log("\n🛠️ Skills:");
      const skillsQuery = `
        SELECT cs.skill_id, s.name, s.category 
        FROM candidate_skills cs 
        JOIN skills s ON cs.skill_id = s.id 
        WHERE cs.candidate_id = '93f067b5-33a0-426a-a296-40b10a5eef08'
      `;
      
      const skillsResult = await pool.query(skillsQuery);
      if (skillsResult.rows.length > 0) {
        skillsResult.rows.forEach(skill => {
          console.log(`  - ${skill.name} (${skill.category})`);
        });
      } else {
        console.log("  ❌ No skills found in candidate_skills table");
      }
      
    } else {
      console.log("❌ Candidate not found");
    }
    
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await pool.end();
  }
}

examineCandidateData();