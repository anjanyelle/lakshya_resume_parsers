import io

import pytest


@pytest.mark.integration
def test_upload_and_search_flow(client, cleanup_db, monkeypatch):
    monkeypatch.setattr(
        "app.services.storage.upload_bytes_to_s3",
        lambda data, key: None,
    )
    monkeypatch.setattr(
        "app.services.storage.generate_presigned_url",
        lambda uri: "https://example.com/download",
    )
    monkeypatch.setattr(
        "app.workers.pipeline.start_parsing_workflow",
        lambda job_id: job_id,
    )

    register = client.post(
        "/api/v1/auth/register",
        json={"email": "recruiter@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    files = {
        "file": (
            "resume.pdf",
            io.BytesIO(b"%PDF-1.4\n% test resume"),
            "application/pdf",
        )
    }
    upload = client.post(
        "/api/v1/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload.status_code == 200

    candidates = client.get(
        "/api/v1/candidates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert candidates.status_code == 200
    assert len(candidates.json()) == 1

    candidate_id = candidates.json()[0]["id"]
    client.put(
        f"/api/v1/candidates/{candidate_id}",
        json={"full_name": "Recruiter Test", "email": "recruiter@test.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    download = client.get(
        f"/api/v1/candidates/{candidate_id}/resume",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert download.status_code == 200

    search = client.get(
        "/api/v1/search?q=Recruiter",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search.status_code == 200
    assert len(search.json()) >= 1
