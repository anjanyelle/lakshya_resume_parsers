"""
Tests for company and job_title search filters in candidate search.
"""

import pytest


@pytest.mark.integration
def test_search_by_company(client, cleanup_db, monkeypatch):
    """Test company search in work_history."""
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

    # Create candidate with work history
    candidate = client.post(
        "/api/v1/candidates",
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
            "current_company": "Google",
            "current_title": "Software Engineer",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert candidate.status_code == 200
    candidate_id = candidate.json()["id"]

    # Add work history
    work_history = client.post(
        f"/api/v1/candidates/{candidate_id}/work-history",
        json={
            "company_name": "Google",
            "job_title": "Software Engineer",
            "start_date": "2020-01-01",
            "is_current": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert work_history.status_code == 200

    # Search by company
    search = client.get(
        "/api/v1/search?company=Google",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search.status_code == 200
    results = search.json()
    assert len(results) >= 1


@pytest.mark.integration
def test_search_by_job_title(client, cleanup_db, monkeypatch):
    """Test job_title search in work_history."""
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
        json={"email": "recruiter2@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter2@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    # Create candidate with work history
    candidate = client.post(
        "/api/v1/candidates",
        json={
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "current_company": "Microsoft",
            "current_title": "Senior Developer",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert candidate.status_code == 200
    candidate_id = candidate.json()["id"]

    # Add work history
    work_history = client.post(
        f"/api/v1/candidates/{candidate_id}/work-history",
        json={
            "company_name": "Microsoft",
            "job_title": "Senior Developer",
            "start_date": "2019-01-01",
            "is_current": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert work_history.status_code == 200

    # Search by job title
    search = client.get(
        "/api/v1/search?job_title=Senior Developer",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search.status_code == 200
    results = search.json()
    assert len(results) >= 1


@pytest.mark.integration
def test_candidates_list_company_filter(client, cleanup_db, monkeypatch):
    """Test company filter in candidates list endpoint."""
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
        json={"email": "recruiter3@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter3@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    # Create candidate with work history
    candidate = client.post(
        "/api/v1/candidates",
        json={
            "full_name": "Bob Johnson",
            "email": "bob@example.com",
            "current_company": "Amazon",
            "current_title": "Data Scientist",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert candidate.status_code == 200
    candidate_id = candidate.json()["id"]

    # Add work history
    work_history = client.post(
        f"/api/v1/candidates/{candidate_id}/work-history",
        json={
            "company_name": "Amazon",
            "job_title": "Data Scientist",
            "start_date": "2021-01-01",
            "is_current": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert work_history.status_code == 200

    # Search candidates by company
    search = client.get(
        "/api/v1/candidates?company=Amazon",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search.status_code == 200
    results = search.json()
    assert len(results) >= 1


@pytest.mark.integration
def test_candidates_list_job_title_filter(client, cleanup_db, monkeypatch):
    """Test job_title filter in candidates list endpoint."""
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
        json={"email": "recruiter4@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter4@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    # Create candidate with work history
    candidate = client.post(
        "/api/v1/candidates",
        json={
            "full_name": "Alice Brown",
            "email": "alice@example.com",
            "current_company": "Meta",
            "current_title": "Product Manager",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert candidate.status_code == 200
    candidate_id = candidate.json()["id"]

    # Add work history
    work_history = client.post(
        f"/api/v1/candidates/{candidate_id}/work-history",
        json={
            "company_name": "Meta",
            "job_title": "Product Manager",
            "start_date": "2022-01-01",
            "is_current": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert work_history.status_code == 200

    # Search candidates by job title
    search = client.get(
        "/api/v1/candidates?job_title=Product Manager",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search.status_code == 200
    results = search.json()
    assert len(results) >= 1


@pytest.mark.integration
def test_search_no_results(client, cleanup_db, monkeypatch):
    """Test search with no matching results."""
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
        json={"email": "recruiter5@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter5@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    # Search for non-existent company
    search = client.get(
        "/api/v1/search?company=NonExistentCompany12345",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search.status_code == 200
    results = search.json()
    assert len(results) == 0


@pytest.mark.integration
def test_search_empty_parameters(client, cleanup_db, monkeypatch):
    """Test search with empty parameters (should be ignored)."""
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
        json={"email": "recruiter6@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "recruiter6@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    # Search with empty company parameter
    search = client.get(
        "/api/v1/search?company=",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search.status_code == 200
    # Should return all candidates (no filter applied)
