#!/usr/bin/env python3
"""
Check JSON Storage Location
"""

import sqlite3
from pathlib import Path

def check_json_storage():
    """Check exactly where JSON is stored"""
    db_path = Path("resume_parser.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check database schema
        cursor.execute("PRAGMA table_info(parsing_jobs)")
        columns = cursor.fetchall()
        
        print("🗄️ DATABASE SCHEMA:")
        print("=" * 50)
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, is_pk = col
            print(f"   Column {col_id}: {col_name} ({col_type})")
        print()
        
        # Check all jobs with their JSON data
        cursor.execute("""
            SELECT id, filename, status, 
                   CASE WHEN parsed_data IS NULL THEN 0 ELSE LENGTH(parsed_data) END as json_size,
                   LENGTH(raw_text) as raw_text_length
            FROM parsing_jobs 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        
        print("📊 ALL JOBS WITH JSON STATUS:")
        print("=" * 50)
        print(f"{'ID':<10} {'FILENAME':<30} {'STATUS':<12} {'JSON_SIZE':<10} {'RAW_TEXT':<10}")
        print("-" * 80)
        
        for job_id, filename, status, json_size, raw_text_length in results:
            json_status = "✅ STORED" if json_size and json_size > 100 else "❌ EMPTY"
            raw_status = "✅ EXTRACTED" if raw_text_length and raw_text_length > 100 else "❌ EMPTY"
            json_size_display = json_size if json_size else 0
            raw_text_display = raw_text_length if raw_text_length else 0
            print(f"{job_id:<10} {filename[:28]:<30} {status:<12} {json_size_display:<10} {raw_status}")
        
        print()
        print("🎯 JSON STORAGE CONFIRMATION:")
        print("=" * 50)
        print("✅ JSON is stored in: parsing_jobs.parsed_data column")
        print("✅ Database file: resume_parser.db")
        print("✅ Location: backend/resume_parser.db")
        
        # Check if any job has JSON data
        cursor.execute("SELECT COUNT(*) FROM parsing_jobs WHERE parsed_data IS NOT NULL AND LENGTH(parsed_data) > 100")
        json_count = cursor.fetchone()[0]
        
        if json_count > 0:
            print(f"✅ Found {json_count} jobs with JSON data")
        else:
            print("❌ No jobs with JSON data found")
            print("💡 Jobs are stuck in 'pending' status")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 CHECKING JSON STORAGE LOCATION")
    print("=" * 60)
    check_json_storage()
