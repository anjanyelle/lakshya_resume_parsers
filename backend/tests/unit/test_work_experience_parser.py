from datetime import date

from app.services.parser.work_experience_parser import WorkExperienceParser


def test_extract_individual_jobs_splits_on_date_ranges():
    text = "Jan 2020 - Dec 2021\nCompany A - Engineer\n\nFeb 2022 - Present\nCompany B - Senior Engineer"
    parser = WorkExperienceParser()
    chunks = parser.extract_individual_jobs(text)
    assert len(chunks) == 2


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
