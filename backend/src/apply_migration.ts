import { query } from "./database/db";

async function runMigration() {
  console.log("Starting migration...");
  try {
    await query(`ALTER TABLE candidates ADD COLUMN total_years_exp JSONB;`);
    console.log("Added total_years_exp to candidates.");
  } catch (e: any) {
    console.log("Error or already exists (total_years_exp):", e.message);
  }

  try {
    await query(`ALTER TABLE work_history ADD COLUMN duration_string VARCHAR(100);`);
    console.log("Added duration_string to work_history.");
  } catch (e: any) {
    console.log("Error or already exists (duration_string):", e.message);
  }
  
  console.log("Migration complete.");
  process.exit(0);
}

runMigration();
