import asyncio
import os
from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models import Candidate, CandidateStatus, Education, Skill, WorkHistory
from app.models.base import Base


async def init_db() -> None:
    """Initialize database with tables and seed data."""
    settings = get_settings()
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

    print("Seeding skills database...")
    from app.data.skills.skills_master import SKILLS_DATABASE

    session = SessionLocal()
    try:
        existing = {
            row[0].lower()
            for row in session.execute(select(Skill.name)).all()
            if row[0]
        }
        total_skills = 0
        for category, skills in SKILLS_DATABASE.items():
            for skill in skills:
                name = skill.get("name", "").strip()
                if not name:
                    continue
                if name.lower() in existing:
                    continue
                db_skill = Skill(
                    name=name,
                    category=skill.get("category") or category,
                    normalized_name=name.lower(),
                )
                session.add(db_skill)
                existing.add(name.lower())
                total_skills += 1

        session.commit()
        print(f"✓ Inserted {total_skills} skills")

        create_candidate = os.getenv("CREATE_TEST_CANDIDATE", "false").lower() in {
            "1",
            "true",
            "yes",
        }
        if create_candidate:
            print("Creating test candidate...")
            email = "test.candidate@example.com"
            existing_candidate = session.execute(
                select(Candidate).where(Candidate.email == email)
            ).scalar_one_or_none()
            if existing_candidate is None:
                candidate = Candidate(
                    full_name="Test Candidate",
                    email=email,
                    phone="+1-555-555-0100",
                    location="San Francisco, CA, USA",
                    current_title="Software Engineer",
                    current_company="Example Corp",
                    status=CandidateStatus.SUCCESS,
                )
                session.add(candidate)
                session.flush()

                session.add(
                    WorkHistory(
                        candidate_id=candidate.id,
                        job_title="Software Engineer",
                        company_name="Example Corp",
                        start_date=date(2022, 1, 1),
                        is_current=True,
                        location="San Francisco, CA",
                        description="Build and maintain backend services.",
                        display_order=1,
                    )
                )
                session.add(
                    Education(
                        candidate_id=candidate.id,
                        institution="State University",
                        degree="B.S. Computer Science",
                        field_of_study="Computer Science",
                        gpa=3.8,
                        description="Graduated with honors.",
                    )
                )
                session.commit()
                print("✓ Test candidate created")
            else:
                print("✓ Test candidate already exists")

        print("Database initialization complete!")
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(init_db())
