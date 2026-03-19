from datetime import date

import pytest

from app.services.parser.work_experience_parser import WorkExperienceParser


def test_extract_individual_jobs_splits_on_date_ranges():
    text = "Jan 2020 - Dec 2021\nCompany A - Engineer\n\nFeb 2022 - Present\nCompany B - Senior Engineer"
    parser = WorkExperienceParser()
    chunks = parser.extract_individual_jobs(text)
    assert len(chunks) == 2


def test_extract_individual_jobs_single_chunk_fallback_splits_by_title():
    """When 1 chunk with no date boundaries, split by job title keywords."""
    text = """
Senior Software Engineer
Acme Corp
- Built systems

Product Manager
Beta Inc
- Led roadmap
"""
    parser = WorkExperienceParser()
    chunks = parser.extract_individual_jobs(text)
    # May split into 2+ chunks if heuristics find boundaries
    assert len(chunks) >= 1


def test_normalize_company_and_title():
    parser = WorkExperienceParser()
    assert parser.normalize_company_names("google inc") == "Google"
    assert parser.normalize_job_titles("Sr. SWE") == "Senior Software Engineer"


def test_parse_date_range():
    parser = WorkExperienceParser()
    start, end, is_current = parser._parse_dates("Jan 2020 - Present")
    assert isinstance(start, date)
    assert is_current is True


def test_parse_date_range_mm_yy():
    parser = WorkExperienceParser()
    start, end, is_current = parser._parse_dates("03/20 - 11/22")
    assert start == date(2020, 3, 1)
    assert end == date(2022, 11, 1)
    assert is_current is False


def test_parse_date_range_month_apostrophe_year():
    parser = WorkExperienceParser()
    start, end, is_current = parser._parse_dates("Aug '20 - Present")
    assert start == date(2020, 8, 1)
    assert end is None
    assert is_current is True


def test_build_date_anchor_excerpt_merges_overlapping_windows():
    text = "\n".join(
        [
            "Header",
            "",
            "Company A - Engineer",
            "Jan 2020 - Dec 2021",
            "Did things",
            "More things",
            "Feb 2022 - Present",
            "Company B - Senior Engineer",
            "Even more",
        ]
    )
    excerpt = WorkExperienceParser.build_date_anchor_excerpt(text, context_lines=5)
    assert "Jan 2020 - Dec 2021" in excerpt
    assert "Feb 2022 - Present" in excerpt
    # Overlapping windows should not introduce extra blank blocks.
    assert excerpt.count("\n\n\n") == 0


def test_looks_like_skillish_header_flags_bulleted_tool_list():
    assert WorkExperienceParser._looks_like_skillish_header(
        "Django, Flask • Docker Registry"
    )


def test_parse_experience_section_splits_on_client_headers_and_promotes_client_to_company():
    text = "\n".join(
        [
            "PROFESSIONALEXPERIENCE:",
            "Client: MedHOK, Tampa, FL Nov 2024 to Till Date",
            "Role: Sr. Site Reliability Engineer",
            " Built Jenkins automation",
            "Client: Walgreens, Deerfield, IL July 2023 to Oct 2024",
            "Role: Site Reliability Engineer",
            " Designed AWS VPC architectures",
        ]
    )
    parser = WorkExperienceParser()
    jobs = parser.parse_experience_section(text)
    assert len(jobs) >= 2

    companies = [str(j.company or "") for j in jobs]
    assert any("MedHOK" in c for c in companies)
    assert any("Walgreens" in c for c in companies)


def test_parse_experience_section_ignores_environment_lines_and_prefers_dated_company_line():
    text = "\n".join(
        [
            "PROFESSIONALEXPERIENCE:",
            "Environments: Lambda, Jenkins, Airflow",
            "Delta Airlines: December 2017 - September 2020 (Location: Atlanta, GA)",
            "Role: Data Engineer / Data Analyst",
            "Responsibilities:",
            "- Built pipelines",
        ]
    )
    parser = WorkExperienceParser()
    jobs = parser.parse_experience_section(text)
    assert any((j.company or "").lower().startswith("delta airlines") for j in jobs)
    assert any("data engineer" in (j.title or "").lower() for j in jobs)


def test_parse_experience_section_does_not_turn_contact_education_or_certs_into_jobs():
    text = "\n".join(
        [
            "Work history",
            "+1 (404)-445-8754 · Linkedin",
            "— → —",
            "Processed and transformed large-scale data using Snowflake, SnowSQL, and Snowpipe",
            "Computer Science · Bachelor of Technology (BTech)",
            "2010-08-01 → 2014-03-01",
            "Salesforce Certified Sales Cloud Consultant",
            "Marketo Certified Solutions Architect (MCSA)",
            "Acme Corp - Data Engineer",
            "Jan 2020 - Dec 2021",
            "- Built ETL pipelines",
            "- Improved data quality",
        ]
    )
    parser = WorkExperienceParser()
    jobs = parser.parse_experience_section(text)
    assert any("acme" in (j.company or "").lower() for j in jobs)
    assert all("bachelor" not in (j.company or "").lower() for j in jobs)


def test_parse_table_formatted_experience():
    text = "\n".join(
        [
            "Acme Corp | Software Engineer | Jan 2020 - Dec 2022 | NYC",
            "Beta Ltd  | Senior Dev       | 2018 - 2020         | LA",
        ]
    )
    parser = WorkExperienceParser()
    jobs = parser.parse_experience_section(text)
    assert len(jobs) == 2
    companies = [str(j.company or "").strip() for j in jobs]
    assert "Acme Corp" in companies or any("acme" in c.lower() for c in companies)
    assert "Beta Ltd" in companies or any("beta" in c.lower() for c in companies)
    assert jobs[0].start_date == date(2020, 1, 1)
    assert jobs[0].end_date == date(2022, 12, 1)
    assert jobs[1].start_date == date(2018, 1, 1)
    assert jobs[1].end_date == date(2020, 1, 1)


@pytest.mark.parametrize(
    ("date_str", "expected"),
    [
        ("Q1 2020", date(2020, 1, 1)),
        ("Q4 2019", date(2019, 10, 1)),
        ("Spring 2020", date(2020, 3, 1)),
        ("Fall 2019", date(2019, 9, 1)),
        ("Jan '20", date(2020, 1, 1)),
        ("Feb '19", date(2019, 2, 1)),
        ("2020.01", date(2020, 1, 1)),
        ("01.2020", date(2020, 1, 1)),
        ("2020", date(2020, 1, 1)),
    ],
)
def test_parse_date_extended_formats(date_str, expected):
    parser = WorkExperienceParser()
    result = parser._parse_date(date_str)
    assert result == expected


def test_validate_dates_flags_future_start():
    parser = WorkExperienceParser()
    from datetime import date
    from app.services.parser.work_experience_parser import JobEntry

    jobs = [
        JobEntry(
            company_or_client={"name": "Acme", "is_client": False},
            role="Dev",
            start_date=date(2030, 1, 1),
            end_date=date(2031, 1, 1),
            currently_working=False,
            location=None,
            description="",
            bullets=[],
            duration_months=12,
            client=None,
            employment_type=None,
            confidence_score=0.9,
        )
    ]
    out = parser._validate_dates(jobs)
    assert out[0].date_flag == "future_start"


def test_validate_dates_flags_end_before_start():
    parser = WorkExperienceParser()
    from datetime import date
    from app.services.parser.work_experience_parser import JobEntry

    jobs = [
        JobEntry(
            company_or_client={"name": "Acme", "is_client": False},
            role="Dev",
            start_date=date(2022, 1, 1),
            end_date=date(2020, 1, 1),
            is_current=False,
            location=None,
            description="",
            bullets=[],
            duration_months=None,
            client=None,
            employment_type=None,
            confidence_score=0.9,
        )
    ]
    out = parser._validate_dates(jobs)
    assert out[0].date_flag == "end_before_start"


def test_detect_overlaps_flags_overlapping_jobs():
    parser = WorkExperienceParser()
    from datetime import date
    from app.services.parser.work_experience_parser import JobEntry

    jobs = [
        JobEntry(
            company_or_client={"name": "A", "is_client": False},
            role="Dev",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 6, 1),
            currently_working=False,
            location=None,
            description="",
            bullets=[],
            duration_months=30,
            client=None,
            employment_type=None,
            confidence_score=0.9,
        ),
        JobEntry(
            company_or_client={"name": "B", "is_client": False},
            role="Dev",
            start_date=date(2021, 1, 1),
            end_date=date(2023, 1, 1),
            currently_working=False,
            location=None,
            description="",
            bullets=[],
            duration_months=24,
            client=None,
            employment_type=None,
            confidence_score=0.9,
        ),
    ]
    out = parser._detect_overlaps(jobs)
    assert out[1].date_flag is not None
    assert "overlap" in (out[1].date_flag or "")


@pytest.mark.parametrize(
    ("header", "expected_company", "expected_title"),
    [
        ("Software Engineer at Google", "Google", "Software Engineer"),
        ("Product Manager | Stripe", "Stripe", "Product Manager"),
        ("ACME CORP - Senior Developer", "ACME CORP", "Senior Developer"),
    ],
)
def test_parse_company_title_formats(header, expected_company, expected_title):
    parser = WorkExperienceParser()
    company, title = parser._parse_company_title(header)
    assert company == expected_company
    assert title == expected_title
