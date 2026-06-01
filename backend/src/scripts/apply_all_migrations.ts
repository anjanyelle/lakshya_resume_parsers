import fs from "fs";
import path from "path";
import pool from "../database/db";

async function main() {
  const migrationsDir = path.join(__dirname, "../database/migrations");
  
  if (!fs.existsSync(migrationsDir)) {
    console.error(`Migrations directory not found at: ${migrationsDir}`);
    process.exit(1);
  }

  // Get and sort migration files
  const files = fs.readdirSync(migrationsDir)
    .filter(file => file.endsWith(".sql"))
    .sort();

  console.log(`Found ${files.length} migration files.`);

  const client = await pool.connect();
  try {
    for (const file of files) {
      const filePath = path.join(migrationsDir, file);
      console.log(`Applying migration: ${file}...`);
      const sql = fs.readFileSync(filePath, "utf8");
      
      // Execute migration
      await client.query(sql);
      console.log(`Successfully applied: ${file}`);
    }
    console.log("All migrations applied successfully.");
  } catch (error) {
    console.error("Migration execution failed:", error);
    process.exit(1);
  } finally {
    client.release();
    await pool.end();
  }
}

main();
