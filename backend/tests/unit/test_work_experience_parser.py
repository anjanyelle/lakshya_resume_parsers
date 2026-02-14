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
