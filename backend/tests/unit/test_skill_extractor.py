from pathlib import Path

from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.work_experience_parser import JobEntry


def test_skill_taxonomy_matching_with_synonyms():
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Experienced with ReactJS, NodeJS, and Postgres."
    matches = extractor.extract_from_skills_section(text)
    normalized = {match.normalized_name for match in matches}
    assert "react" in normalized
    assert "node.js" in normalized
    assert "postgresql" in normalized


def test_skill_inference_and_years():
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    jobs = [
        JobEntry(
            company="Acme",
            title="Engineer",
            start_date=None,
            end_date=None,
            is_current=True,
            location=None,
            description="Built APIs in Python and AWS",
            bullets=[],
            duration_months=24,
            client=None,
            employment_type=None,
            confidence=0.9,
        )
    ]
    skills = extractor.extract_all("Python AWS", jobs)
    normalized = {match.normalized_name for match in skills}
    assert "python" in normalized
    assert "aws" in normalized
