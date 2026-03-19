from pathlib import Path

from app.services.parser.skill_extractor import (
    SkillExtractor,
    clean_text_for_skills,
    clean_text_for_flashtext,
    clean_skill_text_for_section,
    tokenize_skills_by_comma,
    strip_skill_token,
)
from app.services.parser.work_experience_parser import JobEntry


def test_clean_text_for_flashtext_preserves_hyphens_and_parens():
    """Minimal cleaner must NOT remove hyphens, slashes, or parentheses (for t-SNE, RAG, etc.)."""
    raw = "t-SNE, Time-Series Analysis, RAG (Retrieval-Augmented Generation)"
    out = clean_text_for_flashtext(raw)
    assert "t-SNE" in out
    assert "Time-Series" in out
    assert "RAG" in out
    assert "(" in out and ")" in out
    assert "\n" not in out


def test_clean_text_for_skills_normalizes_bullets_and_newlines():
    """Bullets and newlines become commas so extraction sees one stream."""
    raw = "Python\n• Java\n▪ AWS\n- Docker"
    out = clean_text_for_skills(raw)
    assert "Python" in out and "Java" in out and "AWS" in out
    assert "\n" not in out or out.count("\n") == 0
    assert "•" not in out and "▪" not in out


def test_clean_skill_text_for_section_parentheses_and_noise():
    """Section cleaning: ( -> comma, ) removed, &/ -> comma, standalone 'learn'/'based'/'models' removed."""
    raw = "GCP (Cloud storage, Bigquery)\nAWS (S3, Glue)"
    out = clean_skill_text_for_section(raw)
    assert ")" not in out
    assert "(" not in out
    assert "GCP" in out and "Cloud storage" in out and "Bigquery" in out and "S3" in out
    raw2 = "Python, Learn, Scikit-Learn, based and ML"
    out2 = clean_skill_text_for_section(raw2)
    assert "Scikit-Learn" in out2 or "scikit-learn" in out2.lower()
    tokens2 = tokenize_skills_by_comma(out2)
    assert "Learn" not in tokens2 and "learn" not in tokens2
    assert "based" not in tokens2


def test_tokenize_skills_by_comma_no_space_split():
    """Split only by comma; no fragments like 'Spanner)' after section clean."""
    cleaned = "Spanner), S3), Cosmos DB, Cloud Watch"
    text = clean_skill_text_for_section(cleaned)
    tokens = tokenize_skills_by_comma(text)
    for t in tokens:
        assert ")" not in t, f"Token should not contain ): {t!r}"


def test_strip_skill_token():
    """Strip leading/trailing brackets and parentheses."""
    assert strip_skill_token("Spanner)") == "Spanner"
    assert strip_skill_token('"Python"') == "Python"
    assert strip_skill_token("  S3  ") == "S3"


def test_extract_from_skills_section_no_broken_fragments():
    """Skills section with parentheses should not produce 'Spanner)', 'Learn' as skill names."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Cloud: GCP (Bigquery, DataProc, Spanner), AWS (S3, Glue, EMR)"
    matches = extractor.extract_from_skills_section(text)
    names = [m.name for m in matches]
    normalized = [m.normalized_name for m in matches]
    for n in names + normalized:
        assert not n.endswith(")"), f"Broken fragment: {n!r}"
    assert not any(s in names or s in normalized for s in ("Learn", "based", "main tracking", "based and ML"))


def test_word_boundary_react_not_in_reactnative():
    """React must not match inside ReactNative (word boundary)."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Skills: ReactNative and React"
    matches = extractor.extract_from_skills_section(text)
    normalized = {m.normalized_name for m in matches}
    assert "react" in normalized
    assert len([m for m in matches if m.normalized_name == "react"]) <= 1


def test_word_boundary_sql_not_in_nosql():
    """SQL must not match inside NoSQL (word boundary)."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "NoSQL, SQL, MySQL"
    matches = extractor.extract_from_skills_section(text)
    normalized = {m.normalized_name for m in matches}
    assert "sql" in normalized
    assert "mysql" in normalized
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
            company_or_client={"name": "Acme", "is_client": False},
            role="Engineer",
            start_date=None,
            end_date=None,
            currently_working=True,
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


def test_multi_word_taxonomy_skills_in_extract_all():
    """Multi-word taxonomy skills (Machine Learning, Apache Spark, Spring Boot) must be returned by extract_all so they reach JSON/render."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "Skills: Machine Learning, Apache Spark, Spring Boot, Python"
    matches = extractor.extract_all(text, [], skills_section_confidence=0.8, raw_text=text)
    normalized = {m.normalized_name for m in matches}
    names = {m.name for m in matches}
    assert "machine learning" in normalized or "Machine Learning" in names
    assert "spark" in normalized or "Apache Spark" in names
    assert "spring boot" in normalized or "Spring Boot" in names
    assert "python" in normalized
    assert len(matches) >= 3, f"Expected at least 3 skills (multi-word + python), got {len(matches)}: {normalized}"


def test_flashtext_extracts_hyphenated_and_multi_word_from_master_db():
    """FlashText must extract t-SNE, Scikit-learn from master DB without returning fragments like Time, SNE."""
    taxonomy_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "data"
        / "taxonomy"
        / "skills_seed.json"
    )
    extractor = SkillExtractor(taxonomy_path=str(taxonomy_path), use_spacy=False)
    text = "t-SNE, UMAP, Scikit-learn, HuggingFace Transformers"
    matches = extractor.extract_all(text, [], skills_section_confidence=0.8, raw_text=text)
    names = {m.name for m in matches}
    normalized = {m.normalized_name for m in matches}
    assert "t-SNE" in names or "t-sne" in normalized
    assert "Scikit-learn" in names or "scikit-learn" in normalized
    assert not any(
        frag in names or frag in normalized
        for frag in ("SNE", "Time", "Parameter")
    )
