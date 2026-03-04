#!/usr/bin/env python3
"""
Create admin user in PostgreSQL database on Render.
If the users table does not exist, runs Alembic migrations first and retries.
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db_url
from app.models.user import User
from app.core.security import get_password_hash


def _run_migrations() -> None:
    """Run Alembic migrations so that the users table exists."""
    print("Users table missing; running migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        cwd=Path(__file__).parent,
    )
    if result.returncode != 0:
        print(result.stdout or "")
        print(result.stderr or "", file=sys.stderr)
        raise RuntimeError(
            "Migrations failed. Ensure DATABASE_URL is set and the database is reachable."
        )
    print("Migrations completed.")


async def create_admin_user() -> None:
    """Create admin user in the database. Runs migrations first if users table is missing."""
    database_url = os.getenv("DATABASE_URL", get_db_url())
    print(
        f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'local'}"
    )

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)

    for attempt in range(2):
        db = SessionLocal()
        try:
            existing_admin = db.query(User).filter(User.email == "admin1@example.com").first()
            if existing_admin:
                print("✅ Admin user already exists: admin1@example.com")
                return

            admin_user = User(
                email="admin1@example.com",
                hashed_password=get_password_hash("Test@123"),
                is_active=True,
                role="admin",
                tenant_id="default",
            )
            db.add(admin_user)
            db.commit()

            print("✅ Admin user created successfully!")
            print("   Email: admin1@example.com")
            print("   Password: Test@123")
            print("   Role: admin")
            return

        except ProgrammingError as e:
            db.rollback()
            err_msg = str(e.orig) if e.orig else str(e)
            if attempt == 0 and "users" in err_msg.lower() and "does not exist" in err_msg.lower():
                db.close()
                _run_migrations()
                continue
            print(f"❌ Error creating admin user: {e}")
            raise
        except Exception as e:
            db.rollback()
            print(f"❌ Error creating admin user: {e}")
            raise
        finally:
            db.close()

    print("❌ Could not create admin user after running migrations.")
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_admin_user())
