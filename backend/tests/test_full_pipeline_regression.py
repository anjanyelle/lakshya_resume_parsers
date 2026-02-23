import pytest
from app.services.parser.work_experience_sanitizer import sanitize_work_experience_entries
from app.services.parser.normalize import clean_summary_and_skills_sections
from app.services.parser.contact_extractor import ContactExtractor
from app.workers.extract_clients_task import _extract_all_clients
from app.workers.pipeline import _parse_date_str, _dedup_text_lines


# --- Work history ---
def test_sanitizer_keeps_entry_with_company_title_no_dates():
    out = sanitize_work_experience_entries(
        [{"company": "Google", "title": "SWE", "start_date": None, "end_date": None}]
    )
    assert len(out) == 1


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


# --- Name extraction ---
def test_name_from_first_line():
    extractor = ContactExtractor()
    raw = "John Smith\njohn@example.com\nSoftware Engineer"
    result = extractor.extract_name(raw)
    assert result.name == "John Smith"


# --- Multi-client ---
def test_all_clients_extracted():
    text = "Client: Acme Corp\nworking for Beta Inc\nclient: Gamma LLC"
    clients = _extract_all_clients(text)
    names = [c[0] for c in clients]
    assert len(names) >= 2
