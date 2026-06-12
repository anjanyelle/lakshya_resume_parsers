#!/usr/bin/env python3
"""
Create admin user in PostgreSQL database on Render.
Runs Alembic migrations first so the users table exists, then creates the admin user.
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db_url
from app.models import Base  # noqa: F401 - loads all models into Base.metadata
from app.models.user import User
from app.core.security import get_password_hash


def _run_migrations() -> None:
    """Run Alembic migrations using the same Python interpreter (avoids PATH issues in Docker)."""
    print("Running database migrations...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
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


def _ensure_all_tables(engine) -> None:
    """
    Create any missing tables from SQLAlchemy models (e.g. when Alembic reports 'at head'
    but the DB was created elsewhere or migrations didn't fully apply). Safe: checkfirst=True.
    """
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        # e.g. enum type already exists from a partial migration; don't fail startup
        print(f"Note: Could not ensure all tables: {e}")


def _ensure_users_table(engine) -> None:
    """
    If the users table is still missing (Alembic may have skipped because DB was marked at head),
    create only the users table from the SQLAlchemy model. Safe: checkfirst=True.
    """
    print("Users table still missing; creating users table...")
    Base.metadata.tables["users"].create(bind=engine, checkfirst=True)
    print("Users table created.")


async def create_admin_user() -> None:
    """Create admin user in the database. Runs migrations first so the users table exists."""
    database_url = os.getenv("DATABASE_URL", get_db_url())
    print(
        f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'local'}"
    )

    # Skip migrations since tables already exist
    # _run_migrations()

    engine = create_engine(database_url)

    # If Alembic was already "at head" but tables are missing (e.g. new DB or partial state),
    # create any missing tables from models so upload and other endpoints work.
    _ensure_all_tables(engine)

    SessionLocal = sessionmaker(bind=engine)

    for attempt in range(2):
        db = SessionLocal()
        try:
            existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
            if existing_admin:
                print("✅ Admin user already exists: admin@example.com")
                return

            admin_user = User(
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
            print("   Role: admin")
            return

        except ProgrammingError as e:
            db.rollback()
            err_msg = str(e.orig) if e.orig else str(e)
            if attempt == 0 and "users" in err_msg.lower() and "does not exist" in err_msg.lower():
                db.close()
                _run_migrations()
                _ensure_users_table(engine)
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
