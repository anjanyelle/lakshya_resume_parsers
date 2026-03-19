from __future__ import annotations

from datetime import date

from app.services.parser.quality_scoring import score_certifications, score_work_experience_jobs
from app.services.parser.work_experience_parser import JobEntry


def test_score_work_experience_jobs_prefers_plausible_jobs_with_dates():
    jobs = [
        JobEntry(
            company_or_client={"name": "Acme Corp", "is_client": False},
            role="Software Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2021, 1, 1),
            currently_working=False,
            location=None,
            description="",
            bullets=["Built APIs"],
            duration_months=None,
            client=None,
            employment_type=None,
            confidence_score=0.9,
        ),
        JobEntry(
            company_or_client={"name": "Python, AWS, Docker", "is_client": False},
            role="Kubernetes",
            start_date=None,
            end_date=None,
            currently_working=False,
            location=None,
            description="",
            bullets=[],
            duration_months=None,
            client=None,
            employment_type=None,
            confidence_score=0.9,
        ),
    ]

    score = score_work_experience_jobs(jobs)
    assert score > 0.5


def test_score_certifications_rewards_named_certs_and_penalizes_suspicious_lines():
    good = [
        {"name": "AWS Certified Solutions Architect – Associate", "issuer": "Amazon"},
        {"name": "Certified Kubernetes Administrator (CKA)", "issuer": "CNCF"},
    ]
    bad = [
        {"name": "Responsibilities: Built APIs in Python"},
        {"name": "Skills: AWS, Docker, Kubernetes"},
    ]

    assert score_certifications(good) > score_certifications(bad)
