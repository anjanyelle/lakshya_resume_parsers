const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5432"),
  database: process.env.DB_NAME || "resume_parser",
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "",
});

async function analyzeUpdateIssue() {
  try {
    console.log("🔍 Analyzing candidate update issue...");
    
    // Check if there's a specific candidate with the ID from the error
    const candidateId = "43b1bfe0-61ff-4aa1-a2d3-a82c6af69171";
    
    // Check main candidate table
    const candidateQuery = `
      SELECT id, full_name, email, phone, summary, years_experience, 
             current_title, current_company, status, created_at, updated_at
      FROM candidates 
      WHERE id = $1
    `;
    
    const candidateResult = await pool.query(candidateQuery, [candidateId]);
    
    if (candidateResult.rows.length > 0) {
      const candidate = candidateResult.rows[0];
      console.log("📋 Main candidate record:");
      console.log(`  Name: ${candidate.full_name}`);
      console.log(`  Email: ${candidate.email}`);
      console.log(`  Summary: ${candidate.summary || 'NULL'}`);
      console.log(`  Years Experience: ${candidate.years_experience || 'NULL'}`);
      console.log(`  Current Title: ${candidate.current_title || 'NULL'}`);
      console.log(`  Current Company: ${candidate.current_company || 'NULL'}`);
      console.log(`  Updated: ${candidate.updated_at}`);
    }
    
    // Check work_history for this candidate
    const workHistoryQuery = `
      SELECT id, company_name, job_title, start_date, end_date, is_current
      FROM work_history 
      WHERE candidate_id = $1
      ORDER BY start_date DESC
    `;
    
    const workHistoryResult = await pool.query(workHistoryQuery, [candidateId]);
    console.log(`\n💼 Work History (${workHistoryResult.rows.length} records):`);
    workHistoryResult.rows.forEach((work, index) => {
      console.log(`  ${index + 1}. ${work.job_title} at ${work.company_name} (${work.start_date} - ${work.end_date || 'Current'})`);
    });
    
    // Check skills for this candidate
    const skillsQuery = `
      SELECT s.name, cs.proficiency_level, cs.years_experience
      FROM candidate_skills cs
      JOIN skills s ON cs.skill_id = s.id
      WHERE cs.candidate_id = $1
      ORDER BY s.name
    `;
    
    const skillsResult = await pool.query(skillsQuery, [candidateId]);
    console.log(`\n🛠️ Skills (${skillsResult.rows.length} records):`);
    skillsResult.rows.slice(0, 10).forEach((skill, index) => {
      console.log(`  ${index + 1}. ${skill.name} (${skill.proficiency_level || 'N/A'})`);
    });
    if (skillsResult.rows.length > 10) {
      console.log(`  ... and ${skillsResult.rows.length - 10} more`);
    }
    
    // Check education for this candidate
    const educationQuery = `
      SELECT degree, institution, field_of_study, start_date, end_date, gpa
      FROM education 
      WHERE candidate_id = $1
      ORDER BY start_date DESC
    `;
    
    const educationResult = await pool.query(educationQuery, [candidateId]);
    console.log(`\n🎓 Education (${educationResult.rows.length} records):`);
    educationResult.rows.forEach((edu, index) => {
      console.log(`  ${index + 1}. ${edu.degree} in ${edu.field_of_study} at ${edu.institution}`);
    });
    
    // Check certifications for this candidate
    const certQuery = `
      SELECT name, issuing_organization, issue_date, expiry_date
      FROM certifications 
      WHERE candidate_id = $1
      ORDER BY issue_date DESC
    `;
    
    const certResult = await pool.query(certQuery, [candidateId]);
    console.log(`\n🏆 Certifications (${certResult.rows.length} records):`);
    certResult.rows.forEach((cert, index) => {
      console.log(`  ${index + 1}. ${cert.name} (${cert.issuing_organization || 'N/A'})`);
    });
    
    // Check projects in the main candidate record (JSONB)
    const projectsQuery = `
      SELECT projects FROM candidates WHERE id = $1
    `;
    
    const projectsResult = await pool.query(projectsQuery, [candidateId]);
    if (projectsResult.rows.length > 0) {
      const projects = projectsResult.rows[0].projects || [];
      console.log(`\n🚀 Projects (${projects.length} records):`);
      projects.forEach((project, index) => {
        console.log(`  ${index + 1}. ${project.substring(0, 100)}...`);
      });
    }
    
  } catch (error) {
    console.error("❌ Error:", error.message);
  } finally {
    await pool.end();
  }
}

analyzeUpdateIssue();