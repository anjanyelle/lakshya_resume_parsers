import pytest

from app.services.parser.work_experience_sanitizer import sanitize_work_experience_entries
from app.workers.pipeline import _parse_date_str


def test_sanitizer_keeps_company_title_without_dates():
    entries = [
        {
            "company": "Google",
            "title": "SWE",
            "start_date": None,
            "end_date": None,
        }
    ]
    out = sanitize_work_experience_entries(entries)
    assert len(out) == 1


def test_sanitizer_drops_truly_empty():
    entries = [
        {
            "company": "",
            "title": "",
            "start_date": None,
            "end_date": None,
        }
    ]
    out = sanitize_work_experience_entries(entries)
    assert len(out) == 0


def test_parse_date_q1():
    d = _parse_date_str("Q1 2020")
    assert d is not None
    assert d.year == 2020


def test_parse_date_apostrophe():
    d = _parse_date_str("Jan '20")
    assert d is not None
    assert d.year == 2020


def test_parse_date_seasonal():
    d = _parse_date_str("Spring 2021")
    assert d is not None
