import pytest


@pytest.mark.integration
def test_api_key_auth(client, cleanup_db):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "admin@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Secret123"},
    )
    token = login.json()["access_token"]

    key_resp = client.post(
        "/api/v1/auth/api-keys",
        json={"subject": "admin@example.com", "role": "viewer"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert key_resp.status_code == 200
    api_key = key_resp.json()["api_key"]

    candidates = client.get(
        "/api/v1/candidates",
        headers={"X-API-Key": api_key},
    )
    assert candidates.status_code == 200
