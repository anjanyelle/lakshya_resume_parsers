import pytest

from app.models import Candidate, ParsingJob
from app.models.candidate import CandidateStatus
from app.models.parsing_job import ParsingJobStatus


@pytest.mark.integration
def test_parsing_status_endpoint(client, db_session, cleanup_db):
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "admin@example.com", "password": "Secret123", "role": "admin"},
    )
    assert user.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    candidate = Candidate(
        full_name="Parsing Candidate",
        status=CandidateStatus.PENDING,
        tenant_id="default",
    )
    db_session.add(candidate)
    db_session.flush()
    job = ParsingJob(
        candidate_id=candidate.id,
        filename="resume.pdf",
        file_path="s3://test-bucket/resume.pdf",
        status=ParsingJobStatus.PENDING,
    )
    db_session.add(job)
    db_session.commit()

    response = client.get(
        f"/api/v1/parsing/{job.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["job_id"] == str(job.id)
