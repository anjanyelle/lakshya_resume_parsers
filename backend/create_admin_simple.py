#!/usr/bin/env python3
import psycopg2
import bcrypt
import uuid
from datetime import datetime

# Database connection
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "resume_parser"
DB_USER = "postgres"
DB_PASSWORD = "Surya@123"

def create_admin_user():
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Get admin user details
        print("Create Admin User")
        print("================")
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")
        
        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Insert admin user
        insert_query = """
        INSERT INTO users (id, email, hashed_password, role, is_active, tenant_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE SET
            hashed_password = EXCLUDED.hashed_password
        RETURNING id
        """
        
        user_id = str(uuid.uuid4())
        cursor.execute(insert_query, (
            user_id,
            email,
            hashed_password.decode('utf-8'),
            "admin",
            True,
            "default"
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   User ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   You can now login at: http://localhost:5173")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_admin_user()
