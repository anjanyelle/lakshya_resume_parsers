import pytest

from app.core.security import decode_token


@pytest.mark.integration
def test_auth_register_login_refresh_logout(client, cleanup_db):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "admin@example.com", "password": "Secret123", "role": "admin"},
    )
    assert register.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Secret123"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    decoded = decode_token(tokens["access_token"])
    assert decoded.get("type") == "access"

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200

    logout = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert logout.status_code == 200
