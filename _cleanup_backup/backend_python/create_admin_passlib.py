#!/usr/bin/env python3
"""Create admin user using passlib (compatible with the app's security module)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db_url
from app.models.user import User
from app.core.security import get_password_hash
import uuid

def create_admin():
    database_url = get_db_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Delete existing admin@example.com if exists
        existing = db.query(User).filter(User.email == "admin@example.com").first()
        if existing:
            db.delete(existing)
            db.commit()
            print("Deleted existing admin@example.com")
        
        # Create new admin user with passlib hash
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            hashed_password=get_password_hash("Test@123"),
            is_active=True,
            role="admin",
            tenant_id="default",
        )
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("   Email: admin@example.com")
        print("   Password: Test@123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
