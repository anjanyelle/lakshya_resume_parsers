const { Client } = require('pg');
const bcrypt = require('bcryptjs');
const fs = require('fs');
const path = require('path');

async function fixDatabase() {
    const connectionString = "postgresql://postgres1:nX9Jz3hdMjWUcg9pTo9OBzGNrNE8fIhC@dpg-d7u99m9kh4rs738jsrm0-a.oregon-postgres.render.com/resume_parser_rvk9";
    
    const client = new Client({
        connectionString,
        ssl: {
            rejectUnauthorized: false
        }
    });

    try {
        console.log("Connecting to Render database...");
        await client.connect();
        console.log("Connected successfully!");

        // 1. Run Setup SQL
        console.log("Running setup.sql...");
        const setupSqlPath = path.join(__dirname, '../src/database/setup.sql');
        const setupSql = fs.readFileSync(setupSqlPath, 'utf8');
        await client.query(setupSql);
        console.log("Setup SQL executed!");

        // 2. Check if we need to rename the column (the setup.sql might have old name)
        console.log("Checking schema for password column name...");
        const res = await client.query(`
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'password_hash'
        `);

        if (res.rows.length > 0) {
            console.log("Renaming column password_hash to hashed_password...");
            await client.query("ALTER TABLE users RENAME COLUMN password_hash TO hashed_password");
            console.log("Column renamed!");
        }

        // 3. Create the admin user
        console.log("Creating admin user...");
        const saltRounds = 12;
        const passwordHash = await bcrypt.hash("password", saltRounds);
        
        await client.query(`
            INSERT INTO users (email, hashed_password, role) 
            VALUES ($1, $2, $3)
            ON CONFLICT (email) DO UPDATE SET 
                hashed_password = EXCLUDED.hashed_password,
                role = 'admin'
        `, ['admin@example.com', passwordHash, 'admin']);

        console.log("✅ Database initialized and Admin user 'admin@example.com' created!");
        
    } catch (err) {
        console.error("❌ Error during fix:", err);
    } finally {
        await client.end();
    }
}

fixDatabase();
