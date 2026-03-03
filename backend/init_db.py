#!/usr/bin/env python3
"""
Initialize SQLite database with basic schema
"""
import sqlite3
import os
import uuid
from datetime import datetime

def init_db():
    db_path = "resume_parser.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create candidates table
    cursor.execute("""
        CREATE TABLE candidates (
            id TEXT PRIMARY KEY,
            email TEXT,
            email_hash TEXT,
            full_name TEXT,
            phone TEXT,
            ssn TEXT,
            location TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            summary TEXT,
            years_experience REAL,
            years_experience_confidence REAL,
            current_title TEXT,
            current_company TEXT,
            status TEXT DEFAULT 'pending',
            consent_given BOOLEAN DEFAULT 0,
            consent_date TIMESTAMP,
            tenant_id TEXT DEFAULT 'default',
            review_status TEXT DEFAULT 'pending',
            review_assigned_to TEXT,
            review_notes TEXT,
            review_flagged_at TIMESTAMP,
            review_confidence REAL,
            review_flags TEXT,  -- JSON as TEXT for SQLite
            review_approved_at TIMESTAMP,
            review_approved_by TEXT,
            review_rejected_at TIMESTAMP,
            review_rejected_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create parsing_jobs table
    cursor.execute("""
        CREATE TABLE parsing_jobs (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            original_file_copy_path TEXT,
            extracted_text_path TEXT,
            parsed_json_path TEXT,
            status TEXT DEFAULT 'pending',
            task_id TEXT,
            last_stage TEXT,
            raw_text TEXT,
            parsed_data TEXT,  -- JSON as TEXT for SQLite
            confidence_score REAL,
            ocr_confidence REAL,
            error_message TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)
    
    # Create skills table
    cursor.execute("""
        CREATE TABLE skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT,
            name TEXT,
            proficiency_level TEXT,
            confidence REAL,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)
    
    # Create users table for authentication
    cursor.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            role TEXT DEFAULT 'recruiter',
            tenant_id TEXT DEFAULT 'default',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create revoked_tokens table for JWT token management
    cursor.execute("""
        CREATE TABLE revoked_tokens (
            id TEXT PRIMARY KEY,
            jti TEXT UNIQUE NOT NULL,
            subject TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            revoked_at TIMESTAMP NOT NULL
        )
    """)
    
    # Create audit_logs table for audit trail
    cursor.execute("""
        CREATE TABLE audit_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT,
            resource_type TEXT,
            resource_id TEXT,
            ip_address TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create work_history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_history (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            company_name TEXT,
            client_name TEXT,
            job_title TEXT,
            start_date TEXT,
            end_date TEXT,
            is_current INTEGER DEFAULT 0,
            location TEXT,
            description TEXT,
            display_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)
    
    # Create education table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS education (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            institution TEXT,
            degree TEXT,
            field_of_study TEXT,
            start_date TEXT,
            end_date TEXT,
            gpa TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)
    
    # Create candidate_skills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_skills (
            candidate_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            proficiency_level TEXT,
            years_experience TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (candidate_id, skill_id),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id),
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        )
    """)
    
    # Create certifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            name TEXT,
            issuing_organization TEXT,
            issue_date TEXT,
            expiry_date TEXT,
            credential_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)
    
    # Create candidate_achievements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_achievements (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            title TEXT,
            year TEXT,
            confidence REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    """)
    
    # Insert a default admin user (password: admin)
    admin_uuid = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO users (id, email, hashed_password, is_active, role, tenant_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        admin_uuid,
        "admin@example.com", 
        "$2b$12$m/ZaTHUM8baJYA0WE1hTdOXrrtyiC9ugjOPCB79AgNcG6XWStxuiK",  # password: admin
        1,
        "admin",
        "default"
    ))
    
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {db_path}")

if __name__ == "__main__":
    init_db()
