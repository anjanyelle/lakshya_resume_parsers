const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool();

async function checkRawText() {
  const email = 'j.beaumont@learningculture.org';
  try {
    const res = await pool.query('SELECT name, raw_resume_text FROM candidates WHERE email = $1', [email]);
    if (res.rows.length > 0) {
      console.log('--- NAME IN DB ---');
      console.log(res.rows[0].name);
      console.log('\n--- RAW TEXT ---');
      console.log(res.rows[0].raw_resume_text.substring(0, 5000));
    } else {
      console.log('No candidate found');
    }
  } catch (e) {
    console.error(e);
  } finally {
    await pool.end();
  }
}

checkRawText();
