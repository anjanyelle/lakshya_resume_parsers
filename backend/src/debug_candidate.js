const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'resume_parser',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
});

async function debugCandidate() {
  const email = 'j.beaumont@learningculture.org';
  try {
    console.log(`🔍 Debugging candidate with email: ${email}`);
    
    // 1. Check candidate record
    const candidateRes = await pool.query('SELECT * FROM candidates WHERE email = $1', [email]);
    if (candidateRes.rows.length === 0) {
      console.log('❌ No candidate found with this email.');
      return;
    }
    const candidate = candidateRes.rows[0];
    console.log('Candidate record:', JSON.stringify(candidate, null, 2));

    // 2. Check parsing jobs
    const jobRes = await pool.query('SELECT * FROM parsing_jobs WHERE candidate_id = $1', [candidate.id]);
    console.log('\nParsing jobs:', JSON.stringify(jobRes.rows, null, 2));

    // 3. Check work history
    const workRes = await pool.query('SELECT * FROM work_history WHERE candidate_id = $1', [candidate.id]);
    console.log('\nWork history count:', workRes.rows.length);
    console.log('Work history sample:', JSON.stringify(workRes.rows, null, 2));

    // 4. Check skills
    const skillsRes = await pool.query(`
      SELECT s.name as skill_name 
      FROM candidate_skills cs 
      JOIN skills s ON cs.skill_id = s.id 
      WHERE cs.candidate_id = $1
    `, [candidate.id]);
    console.log('\nSkills:', skillsRes.rows.map(r => r.skill_name).join(', '));

  } catch (error) {
    console.error('Error debugging candidate:', error);
  } finally {
    await pool.end();
  }
}

debugCandidate();
