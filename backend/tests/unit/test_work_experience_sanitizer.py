from __future__ import annotations


def test_sanitize_work_experience_drops_skillish_headers():
    from app.services.parser.work_experience_parser import sanitize_work_experience_entries

    entries = [
        {
            "company": "Django, Flask • Docker",
            "title": "Engineer",
            "start_date": "2020-01",
            "end_date": "2021-01",
            "bullets": ["Did thing"],
        },
        {
            "company": "Acme Corp",
            "title": "Software Engineer",
            "start_date": "2020-01",
            "end_date": "2021-01",
            "bullets": ["Built APIs"],
        },
    ]

    out = sanitize_work_experience_entries(entries)
    assert len(out) == 1
    assert out[0].get("company") == "Acme Corp"


def test_sanitize_work_experience_drops_empty_low_signal_entries():
    from app.services.parser.work_experience_parser import sanitize_work_experience_entries

    entries = [
        {"company": "Acme", "title": "Engineer"},
        {"company": "Acme", "title": "Engineer", "description": ""},
        {"company": "Acme", "title": "Engineer", "bullets": []},
        {"company": "Acme", "title": "Engineer", "start_date": "2020-01"},
    ]

    out = sanitize_work_experience_entries(entries)
    # All 4 have company+title; first 3 dedupe to one (_needs_review), 4th has date so separate key
    assert len(out) == 2
    with_date = [e for e in out if e.get("start_date") == "2020-01"]
    assert len(with_date) == 1
    assert with_date[0].get("company") == "Acme"


def test_sanitize_work_experience_drops_placeholders():
    from app.services.parser.work_experience_parser import sanitize_work_experience_entries

    entries = [
        {"company": "Company", "title": "Engineer", "start_date": "2020-01"},
        {"company": "Acme", "title": "Role", "start_date": "2020-01"},
        {"company": "Acme", "title": "Engineer", "start_date": "2020-01"},
    ]

    out = sanitize_work_experience_entries(entries)
    assert len(out) == 1
    assert out[0].get("company") == "Acme"


def test_sanitize_work_experience_merges_duplicates_and_dedupes_bullets():
    from app.services.parser.work_experience_parser import sanitize_work_experience_entries

    entries = [
        {
            "company": "Acme  Corp ",
            "client": "Client A",
            "title": "Software   Engineer",
            "start_date": "2020-01",
            "end_date": "2021-01",
            "bullets": ["- Built APIs", "Built APIs ", "Improved latency"],
            "description": "| One | Two",
            "confidence": 0.6,
        },
        {
            "company": "Acme Corp",
            "client": "Client A",
            "title": "Software Engineer",
            "start_date": "2020-01",
            "end_date": "2021-01",
            "bullets": ["Improved latency", "Wrote tests"],
            "description": "Better description",
            "confidence": 0.8,
        },
    ]

    out = sanitize_work_experience_entries(entries)
    assert len(out) == 1
    merged = out[0]

    assert merged.get("company") == "Acme Corp"
    assert merged.get("title") == "Software Engineer"

    bullets = merged.get("bullets")
    assert isinstance(bullets, list)
    assert "Built APIs" in bullets
    assert "Improved latency" in bullets
    assert "Wrote tests" in bullets
    assert len([b for b in bullets if b.lower().strip() == "built apis"]) == 1

    assert merged.get("description") == "Better description"
    assert merged.get("confidence") == 0.8


def test_sanitize_keeps_entry_with_company_title_without_dates():
    from app.services.parser.work_experience_parser import sanitize_work_experience_entries

    entries = [
        {
            "company": "Acme Corp",
            "title": "Software Engineer",
            "start_date": None,
            "end_date": None,
            "description": "",
        }
    ]
    out = sanitize_work_experience_entries(entries)
    assert len(out) == 1, f"Expected 1, got {len(out)}"
    assert out[0].get("company") == "Acme Corp"
    assert out[0].get("title") == "Software Engineer"
    assert out[0].get("_needs_review") is True
    print("PASS: Entry with company+title kept even without dates")
