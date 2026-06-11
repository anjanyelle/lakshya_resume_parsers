#!/usr/bin/env python3
"""Run SQL migration files to fix database schema issues"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import psycopg2
from app.core.config import get_settings

def run_migration():
    settings = get_settings()
    database_url = settings.DATABASE_URL
    
    # Parse database URL
    if "postgresql://" in database_url or "postgresql+psycopg2://" in database_url:
        # Remove protocol prefix
        db_url = database_url.replace("postgresql+psycopg2://", "").replace("postgresql://", "")
        parts = db_url.split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        
        user = user_pass[0]
        password = user_pass[1]
        host_port = host_db[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        database = host_db[1]
    else:
        print("❌ Unsupported database URL format")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Read migration file
        migration_file = Path(__file__).parent / "src" / "database" / "migrations" / "008_fix_remaining_issues.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            sys.exit(1)
        
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        print(f"📋 Running migration: {migration_file.name}")
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
