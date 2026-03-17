import json
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models import Skill


def load_taxonomy() -> list[dict]:
    path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("skills", [])


def main() -> None:
    settings = get_settings()
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    session = SessionLocal()
    try:
        existing = {
            row[0].lower()
            for row in session.execute(select(Skill.name)).all()
            if row[0]
        }
        inserted = 0
        for item in load_taxonomy():
            name = item.get("name", "").strip()
            normalized = item.get("normalized_name", "").strip().lower()
            if not name or normalized in existing:
                continue
            session.add(
                Skill(
                    name=name,
                    category=item.get("category"),
                    normalized_name=normalized or name.lower(),
                )
            )
            existing.add(normalized or name.lower())
            inserted += 1
        session.commit()
        print(f"Seeded {inserted} skills.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
