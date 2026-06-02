const { Client } = require("pg");
require("dotenv").config();

async function run() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL
  });
  try {
    await client.connect();
    const res = await client.query(`
      SELECT full_name, match_score 
      FROM candidates 
      WHERE match_score IS NOT NULL 
      LIMIT 10
    `);
    console.log("Candidates with match_score:");
    console.log(res.rows);
    
    const countRes = await client.query("SELECT COUNT(*)::int as total, COUNT(*) FILTER (WHERE match_score = 1.0)::int as perfect FROM candidates");
    console.log("Summary:", countRes.rows[0]);
  } catch (err) {
    console.error(err);
  } finally {
    await client.end();
  }
}
run();
