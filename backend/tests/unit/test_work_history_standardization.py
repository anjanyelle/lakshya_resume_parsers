import pytest
from datetime import date
from app.services.parser.work_experience_parser import WorkExperienceParser, JobEntry

@pytest.fixture
def parser():
    return WorkExperienceParser()

def test_date_iso_normalization(parser):
    text = """
    Software Engineer
    Google
    Jan 2020 - Present
    """
    res = parser.parse_to_standardized_json(text)
    job = res["work_history"][0]
    assert job["start_date"] == "2020-01-01"
    assert job["end_date"] is None
    assert job["currently_working"] is True

def test_split_multi_role_same_company(parser):
    text = """
    Google
    Senior Software Engineer | Jan 2022 - Present
    - Leading the search team.
    Software Engineer | Jan 2020 - Dec 2021
    - Working on search algorithms.
    """
    res = parser.parse_to_standardized_json(text)
    assert len(res["work_history"]) == 2
    assert res["work_history"][0]["role"] == "Senior Software Engineer"
    assert res["work_history"][1]["role"] == "Software Engineer"
    assert res["work_history"][0]["company"]["name"] == "Google"
    assert res["work_history"][1]["company"]["name"] == "Google"

def test_client_flag_detection(parser):
    text = """
    Tata Consultancy Services
    Senior Consultant | Jan 2021 - Present
    - Worked for End Client: Cigna Healthcare
    """
    res = parser.parse_to_standardized_json(text)
    job = res["work_history"][0]
    assert job["company"]["client_flag"] is True
    assert job["company"]["name"] == "Tata Consultancy Services"

def test_location_normalization(parser):
    text = """
    Google
    Software Engineer
    Bloomfield, CT, USA
    Jan 2020 - Present
    """
    res = parser.parse_to_standardized_json(text)
    loc = res["work_history"][0]["location"]
    assert loc["city"] == "Bloomfield"
    assert loc["region"] == "CT"
    assert loc["country"] == "USA"

def test_bullet_limit_and_conciseness(parser):
    bullets = [f"Bullet point number {i}" for i in range(15)]
    text = "Google\nSoftware Engineer\nJan 2020 - Present\n" + "\n".join(["- " + b for b in bullets])
    res = parser.parse_to_standardized_json(text)
    assert len(res["work_history"][0]["bullets"]) <= 8

def test_technology_extraction(parser):
    text = """
    Software Engineer at Google
    Built a system using Java, Spring Boot, and AWS.
    Implemented CI/CD pipelines with Docker and Kubernetes.
    """
    res = parser.parse_to_standardized_json(text)
    techs = res["work_history"][0]["technologies"]
    assert "java" in techs
    assert "spring boot" in techs
    assert "aws" in techs
    assert "docker" in techs
    assert "kubernetes" in techs

def test_deduplication_overlap(parser):
    # Overlapping jobs with same company/title
    text = """
    Senior Software Engineer
    Google
    Jan 2020 - Present
    
    Senior Software Engineer
    Google
    Feb 2020 - Present
    """
    res = parser.parse_to_standardized_json(text)
    # They overlap heavily (>60%), so they should be merged.
    assert len(res["work_history"]) == 1
