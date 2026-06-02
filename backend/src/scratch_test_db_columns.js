const { Client } = require('pg');
const crypto = require('crypto');
require('dotenv').config();

async function run() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL
  });
  
  try {
    await client.connect();
    console.log("DB connected.");
    
    // List all tables
    const tablesRes = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
    `);
    console.log("\n--- ALL TABLES ---");
    tablesRes.rows.forEach(t => console.log(t.table_name));
    
    // Check columns of skills
    const skillsCol = await client.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'skills'
    `);
    console.log("\n--- SKILLS COLUMNS ---");
    skillsCol.rows.forEach(row => {
      console.log(`${row.column_name}: ${row.data_type}`);
    });
    
    // Check columns of candidate_skills
    const candSkillsCol = await client.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'candidate_skills'
    `);
    console.log("\n--- CANDIDATE_SKILLS COLUMNS ---");
    candSkillsCol.rows.forEach(row => {
      console.log(`${row.column_name}: ${row.data_type}`);
    });
    
    // Test the transaction insert block
    console.log("\n--- RUNNING INSERT TRANSACTION MOCK ---");
    await client.query("BEGIN");
    
    const candidateId = crypto.randomUUID();
    const emailHash = crypto.createHash("md5").update("test@example.com").digest("hex");
    
    const candResult = await client.query(
      `INSERT INTO candidates (
        id, email, phone, full_name, status, summary, resume_file_path,
        consent_given, tenant_id, review_status, email_hash, created_at, updated_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW()) RETURNING *`,
      [
        candidateId,
        "test@example.com",
        "1234567890",
        "Test Candidate",
        "pending",
        "Test Summary",
        null,
        false,
        "default",
        "pending",
        emailHash
      ]
    );
    const candidate = candResult.rows[0];
    console.log("Candidate inserted successfully.");
    
    // Test inserting a skill
    const skillName = "React";
    const existingSkill = await client.query(
      "SELECT id FROM skills WHERE name = $1",
      [skillName]
    );
    console.log("Existing skill query completed. Found:", existingSkill.rows.length);
    
    let skillId;
    if (existingSkill.rows.length > 0) {
      skillId = existingSkill.rows[0].id;
    } else {
      const newSkill = await client.query(
        "INSERT INTO skills (id, name, category) VALUES ($1, $2, $3) RETURNING id",
        [crypto.randomUUID(), skillName, "technical"]
      );
      skillId = newSkill.rows[0].id;
      console.log("New skill inserted successfully.");
    }
    
    await client.query(
      "INSERT INTO candidate_skills (candidate_id, skill_id, proficiency_level) VALUES ($1, $2, $3)",
      [candidate.id, skillId, "intermediate"]
    );
    console.log("Candidate skill relation inserted successfully.");
    
    // Test inserting work history
    const workQuery = `
      INSERT INTO work_history (id, candidate_id, job_title, company_name, start_date, end_date, is_current, description, location)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    `;
    await client.query(workQuery, [
      crypto.randomUUID(),
      candidate.id,
      "Developer",
      "Company",
      "2020-01-01",
      null,
      true,
      "description",
      "location"
    ]);
    console.log("Work history inserted successfully.");
    
    // Test inserting education
    const eduQuery = `
      INSERT INTO education (id, candidate_id, degree, institution, field_of_study, start_date, end_date, gpa)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    `;
    await client.query(eduQuery, [
      crypto.randomUUID(),
      candidate.id,
      "BS",
      "University",
      "CS",
      "2016-01-01",
      "2020-01-01",
      4.0
    ]);
    console.log("Education inserted successfully.");
    
    // Test inserting parsing job
    const parsedDataJson = {
      name: "Test Candidate",
      email: "test@example.com"
    };
    await client.query(
      `INSERT INTO parsing_jobs (id, candidate_id, status, confidence_score, parsed_data, created_at, completed_at) 
       VALUES ($1, $2, 'completed', 1.0, $3, NOW(), NOW())`,
      [crypto.randomUUID(), candidate.id, JSON.stringify(parsedDataJson)],
    );
    console.log("Parsing job inserted successfully.");
    
    await client.query("COMMIT");
    console.log("COMMIT successful.");
    
  } catch (err) {
    console.error("TRANSACTION FAILED ERROR:", err.message);
    console.error("Detail:", err.detail);
    console.error("Stack:", err.stack);
    try {
      await client.query("ROLLBACK");
      console.log("ROLLBACK completed.");
    } catch (rbErr) {
      console.error("ROLLBACK failed:", rbErr.message);
    }
  } finally {
    await client.end();
  }
}

run();
