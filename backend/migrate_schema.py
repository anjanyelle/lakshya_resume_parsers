#!/usr/bin/env python3
import psycopg2
import os
from urllib.parse import urlparse

# Database connection
DB_URL = "postgresql://postgres:Surya%40123@localhost:5432/resume_parser"

def migrate_db():
    try:
        # Connect to database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        print("Running database migrations...")
        
        # 1. Add status column to candidates if it doesn't exist
        print("- Adding 'status' column to candidates table...")
        cursor.execute("""
            ALTER TABLE candidates 
            ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'pending';
        """)
        
        # 2. Rename work_experience to work_history if needed
        print("- Checking work_history table...")
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_experience');")
        exists = cursor.fetchone()[0]
        if exists:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'work_history');")
            history_exists = cursor.fetchone()[0]
            if not history_exists:
                print("  - Renaming work_experience to work_history")
                cursor.execute("ALTER TABLE work_experience RENAME TO work_history;")
            else:
                print("  - Both tables exist, keeping work_history")
        
        # 3. Fix users table column name if needed
        print("- Checking users table column name...")
        cursor.execute("""
            DO $$ 
            BEGIN 
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                           WHERE table_name='users' AND column_name='password_hash') THEN
                    ALTER TABLE users RENAME COLUMN password_hash TO hashed_password;
                END IF;
            END $$;
        """)

        # 4. Ensure parsing_jobs table exists (sometimes it's missing)
        print("- Ensuring parsing_jobs table exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parsing_jobs (
                id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                candidate_id     UUID NOT NULL REFERENCES candidates (id) ON DELETE CASCADE,
                status           VARCHAR(50) NOT NULL DEFAULT 'pending',
                confidence_score DECIMAL(5,4),
                parsed_data      JSONB,
                error_message    TEXT,
                created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at     TIMESTAMP WITH TIME ZONE
            );
        """)
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_db()
