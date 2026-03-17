import pytest
from app.services.parser.work_experience_sanitizer import (
    deduplicate_work_entries,
    sanitize_work_experience_entries,
)
from app.services.parser.normalize import clean_summary_and_skills_sections
from app.services.parser.contact_extractor import ContactExtractor
from app.workers.extract_clients_task import _extract_all_clients
from app.workers.pipeline import _parse_date_str, clean_summary, _dedup_text_lines


# --- Work history ---
def test_sanitizer_keeps_entry_with_company_title_no_dates():
    out = sanitize_work_experience_entries(
        [{"company": "Google", "title": "SWE", "start_date": None, "end_date": None}]
    )
    assert len(out) == 1


def test_deduplicate_work_entries_removes_duplicates_by_company_title_start():
    """Same company+title+start_date -> keep one with more filled fields."""
    entries = [
        {"company": "Acme", "title": "Engineer", "start_date": "2020-01", "description": ""},
        {"company": "Acme", "title": "Engineer", "start_date": "2020-01", "bullets": ["Built APIs"]},
    ]
    out = deduplicate_work_entries(entries)
    assert len(out) == 1
    assert out[0].get("bullets") == ["Built APIs"]


def test_sanitizer_drops_fully_empty():
    out = sanitize_work_experience_entries(
        [{"company": "", "title": "", "start_date": None, "end_date": None}]
    )
    assert len(out) == 0


# --- Date parsing ---
def test_date_q1():
    assert _parse_date_str("Q1 2020") is not None


def test_date_seasonal():
    assert _parse_date_str("Spring 2021") is not None


def test_date_apostrophe():
    assert _parse_date_str("Jan '20") is not None


def test_date_dmy_format():
    assert _parse_date_str("15.01.2020") is not None


def test_date_ym_format():
    assert _parse_date_str("2020/01") is not None


# --- Summary dedup ---
def test_summary_no_duplicates():
    sections = {
        "summary": {"content": "Experienced engineer\nExperienced engineer\nLeads teams", "confidence": 0.9},
        "skills": {"content": "Python\nJava", "confidence": 0.8},
    }
    result, _ = clean_summary_and_skills_sections(sections)
    content = result["summary"]["content"]
    lines = content.splitlines()
    assert len(lines) == len(set(l.strip().lower() for l in lines if l.strip()))


def test_dedup_text_lines():
    text = "Line one\nLine one\nLine two"
    result = _dedup_text_lines(text)
    assert result.count("Line one") == 1


def test_clean_summary_removes_repeated_paragraphs():
    """clean_summary produces single, clean summary with no repeated paragraphs."""
    text = "Experienced engineer. Experienced engineer. Leads teams."
    result = clean_summary(text)
    assert result.count("Experienced engineer") == 1
    assert "Leads teams" in result


def test_dedup_text_lines_sentence_level():
    """Duplicate sentences removed."""
    text = "Experienced engineer. Experienced engineer. Leads teams."
    result = _dedup_text_lines(text)
    assert result.count("Experienced engineer") == 1
    assert "Leads teams" in result


def test_dedup_text_lines_trim_over_1500_chars():
    """Summary over 1500 chars trimmed to first 6 sentences."""
    # 8 long sentences, each ~250 chars, total > 1500
    parts = [chr(65 + i) * 240 + "." for i in range(8)]
    long_text = " ".join(parts)
    result = _dedup_text_lines(long_text)
    # Trim only when > 1500 and > 6 sentences, so result is first 6 sentences
    assert len(result) <= 1600
    assert "A" in result and "F" in result


# --- Name extraction ---
def test_name_from_first_line():
    extractor = ContactExtractor()
    raw = "John Smith\njohn@example.com\nSoftware Engineer"
    result = extractor.extract_name(raw)
    assert result.name == "John Smith"


def test_name_all_caps_fallback():
    """ALL CAPS 2-4 words on line 1 treated as name."""
    extractor = ContactExtractor()
    raw = "JOHN ROBERT SMITH\nSoftware Engineer\nAcme Corp"
    result = extractor.extract_name(raw)
    assert result.name is not None
    assert "John" in result.name and "Smith" in result.name


def test_name_returns_empty_string_not_none():
    """When no name found, return '' not None."""
    extractor = ContactExtractor()
    raw = "Summary\n\nBuilt APIs with Python. Led team of 5. Delivered projects."
    result = extractor.extract_name(raw)
    assert result.name == ""
    assert result.name is not None


# --- Work history (BUG 4) ---
def test_extract_individual_jobs_single_chunk_splits_by_company_date():
    """When only 1 block found, split by company name before date pattern."""
    from app.services.parser.work_experience_parser import WorkExperienceParser

    text = """
Acme Corp Jan 2020 - Dec 2021
Software Engineer
- Built APIs

Beta Inc 2019 - 2020
Data Analyst
- Analyzed data
"""
    parser = WorkExperienceParser()
    chunks = parser.extract_individual_jobs(text)
    assert len(chunks) >= 2


def test_has_date_anchor_ocr_lenient():
    """OCR resumes: bare 4-digit year treated as date anchor."""
    from app.services.parser.work_experience_parser import WorkExperienceParser

    parser = WorkExperienceParser()
    assert parser._has_date_anchor("Some Company 2020", source_format="ocr") is True
    assert parser._has_date_anchor("Some Company 2020", source_format=None) is False


# --- Cert dedup (BUG 5) ---
def test_deduplicate_certificates_exact_match():
    """Exact cert_name + issuer match -> keep one."""
    from app.services.parser.certification_validator import deduplicate_certificates

    certs = [
        {"name": "AWS Certified Solutions Architect", "issuing_organization": "Amazon"},
        {"name": "AWS Certified Solutions Architect", "issuing_organization": "Amazon"},
    ]
    out = deduplicate_certificates(certs)
    assert len(out) == 1


def test_deduplicate_certificates_fuzzy_match():
    """Similar cert names (>90%) -> keep one with more fields."""
    from app.services.parser.certification_validator import deduplicate_certificates

    certs = [
        {"name": "AWS Certified Solutions Architect Associate", "issuing_organization": ""},
        {"name": "AWS Certified Solutions Architect - Associate", "issuing_organization": "Amazon"},
    ]
    out = deduplicate_certificates(certs)
    assert len(out) == 1


def test_deduplicate_certificates_keeps_richer_entry():
    """When duplicate, keep entry with more fields (e.g. date)."""
    from app.services.parser.certification_validator import deduplicate_certificates

    certs = [
        {"name": "PMP", "issuing_organization": "PMI"},
        {"name": "Project Management Professional", "issuing_organization": "PMI", "issue_date": "2020-01"},
    ]
    out = deduplicate_certificates(certs)
    assert len(out) == 1
    assert out[0].get("issue_date") == "2020-01"


# --- Pipeline dedup guard ---
def test_sanitize_final_output_dedups_and_logs():
    """sanitize_final_output deduplicates work, certs, cleans summary, validates name."""
    from app.workers.pipeline import sanitize_final_output

    parsed = {
        "work_experience": [
            {"company": "Acme", "title": "Engineer", "start_date": "2020-01"},
            {"company": "Acme", "title": "Engineer", "start_date": "2020-01"},
        ],
        "certifications": [
            {"name": "AWS Certified", "issuing_organization": "Amazon"},
            {"name": "AWS Certified", "issuing_organization": "Amazon"},
        ],
        "sections": {
            "summary": {"content": "Experienced engineer\nExperienced engineer\nLeads teams"},
        },
        "contact": {"name": {"name": "John Doe", "confidence": 0.9}},
    }
    out = sanitize_final_output(parsed)
    assert len(out["work_experience"]) == 1
    assert len(out["certifications"]) == 1
    # Paragraph-level dedup removes duplicate lines
    assert out["sections"]["summary"]["content"].count("Experienced engineer") == 1
    assert out["contact"]["name"]["name"] == "John Doe"


# --- Multi-client ---
def test_all_clients_extracted():
    text = "Client: Acme Corp\nworking for Beta Inc\nclient: Gamma LLC"
    clients = _extract_all_clients(text)
    names = [c[0] for c in clients]
    assert len(names) >= 2
