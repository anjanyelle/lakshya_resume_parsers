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


def test_extract_from_raw_text_space_separated_skills():
    """Space-separated lines like 'Python Java SQL Oracle Redis' should yield 5 skills."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Python Java SQL Oracle Redis"
    matches = extractor.extract_from_raw_text(text)
    normalized = {match.normalized_name for match in matches}
    assert len(normalized) >= 5, f"Expected at least 5 skills, got {normalized}"
    assert "python" in normalized
    assert "java" in normalized
    assert "sql" in normalized
    assert "oracle" in normalized
    assert "redis" in normalized


def test_extract_from_raw_text_bigram_skills():
    """Bigram skills like 'Machine Learning Deep Learning NLP' should yield 3 skills."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Machine Learning Deep Learning NLP"
    matches = extractor.extract_from_raw_text(text)
    normalized = {match.normalized_name for match in matches}
    assert len(normalized) >= 3, f"Expected at least 3 skills, got {normalized}"
    assert "machine learning" in normalized
    assert "deep learning" in normalized
    assert "natural language processing" in normalized or "nlp" in normalized


def test_expand_compound_skill_slash():
    """React/Redux -> [React, Redux]."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Skills: React/Redux"
    matches = extractor.extract_from_raw_text(text)
    normalized = {match.normalized_name for match in matches}
    assert "react" in normalized
    assert "redux" in normalized


def test_expand_compound_skill_paren():
    """AWS (EC2, S3, Lambda) -> [AWS, EC2, S3, Lambda]."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Skills: AWS (EC2, S3, Lambda)"
    matches = extractor.extract_from_raw_text(text)
    normalized = {match.normalized_name for match in matches}
    assert "aws" in normalized
    assert "ec2" in normalized
    assert "s3" in normalized
    assert "lambda" in normalized


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
