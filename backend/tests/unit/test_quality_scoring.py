from __future__ import annotations

from datetime import date

from app.services.parser.quality_scoring import score_certifications, score_work_experience_jobs
from app.services.parser.work_experience_parser import JobEntry


def test_score_work_experience_jobs_prefers_plausible_jobs_with_dates():
    jobs = [
        JobEntry(
            company="Acme Corp",
            title="Software Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2021, 1, 1),
            is_current=False,
            location=None,
            description="",
            bullets=["Built APIs"],
            duration_months=None,
            client=None,
            employment_type=None,
            confidence=0.9,
        ),
        JobEntry(
            company="Python, AWS, Docker",
            title="Kubernetes",
            start_date=None,
            end_date=None,
            is_current=False,
            location=None,
            description="",
            bullets=[],
            duration_months=None,
            client=None,
            employment_type=None,
            confidence=0.9,
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
