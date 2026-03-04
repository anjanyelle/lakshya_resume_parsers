#!/usr/bin/env python3
"""
Create admin user in PostgreSQL database on Render
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine
from app.core.database import get_db_url
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import sessionmaker

async def create_admin_user():
    """Create admin user in the database"""
    try:
        # Get database URL from environment or use default
        database_url = os.getenv("DATABASE_URL", get_db_url())
        print(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
        
        # Create engine and session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        
        # Create session
        db = SessionLocal()
        
        try:
            # Check if admin user already exists
            existing_admin = db.query(User).filter(User.email == "admin1@example.com").first()
            if existing_admin:
                print("✅ Admin user already exists: admin1@example.com")
                return
            
            # Create admin user
            admin_user = User(
                email="admin1@example.com",
                hashed_password=get_password_hash("Test@123"),
                is_active=True,
                role="admin",
                tenant_id="default"
            )
            
            db.add(admin_user)
            db.commit()
            
            print("✅ Admin user created successfully!")
            print("   Email: admin1@example.com")
            print("   Password: Test@123")
            print("   Role: admin")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error creating admin user: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_admin_user())
