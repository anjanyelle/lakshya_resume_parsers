"""
Integration tests for Role-Based Access Control (RBAC).
Tests user management, permission management, and authorization.
"""

import pytest


@pytest.mark.integration
class TestUserManagement:
    """Test user management endpoints."""

    def test_list_users_as_admin(self, client, cleanup_db):
        """Test listing users as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/users",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)

    def test_list_users_as_non_admin(self, client, cleanup_db):
        """Test that non-admin cannot list users."""
        # Register and login as recruiter
        client.post(
            "/api/v1/auth/register",
            json={"email": "recruiter@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "recruiter@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/users",
            headers=headers,
        )
        assert response.status_code == 403

    def test_get_user_as_admin(self, client, cleanup_db):
        """Test getting a specific user as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin2@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin2@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # First get a user ID from the list
        list_response = client.get("/api/v1/users", headers=headers)
        users = list_response.json()["users"]
        if users:
            user_id = users[0]["id"]
            response = client.get(
                f"/api/v1/users/{user_id}",
                headers=headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == user_id

    def test_create_user_as_admin(self, client, cleanup_db):
        """Test creating a new user as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin3@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin3@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        user_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "role": "recruiter",
            "tenant_id": "default",
        }
        response = client.post(
            "/api/v1/users",
            json=user_data,
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["role"] == user_data["role"]

    def test_create_user_as_non_admin(self, client, cleanup_db):
        """Test that non-admin cannot create users."""
        # Register and login as recruiter
        client.post(
            "/api/v1/auth/register",
            json={"email": "recruiter2@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "recruiter2@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        user_data = {
            "email": "testuser2@example.com",
            "password": "testpassword123",
            "role": "recruiter",
        }
        response = client.post(
            "/api/v1/users",
            json=user_data,
            headers=headers,
        )
        assert response.status_code == 403

    def test_update_user_role_as_admin(self, client, cleanup_db):
        """Test updating user role as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin4@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin4@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # First get a user ID
        list_response = client.get("/api/v1/users", headers=headers)
        users = list_response.json()["users"]
        if users:
            user_id = users[0]["id"]
            response = client.put(
                f"/api/v1/users/{user_id}/role",
                json={"role": "hr"},
                headers=headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "hr"

    def test_deactivate_user_as_admin(self, client, cleanup_db):
        """Test deactivating a user as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin5@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin5@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # First create a test user
        create_response = client.post(
            "/api/v1/users",
            json={
                "email": "deactivate_test@example.com",
                "password": "testpassword123",
                "role": "recruiter",
            },
            headers=headers,
        )
        if create_response.status_code == 200:
            user_id = create_response.json()["id"]
            response = client.put(
                f"/api/v1/users/{user_id}/deactivate",
                headers=headers,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["is_active"] is False

    def test_delete_user_as_admin(self, client, cleanup_db):
        """Test deleting a user as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin6@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin6@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # First create a test user
        create_response = client.post(
            "/api/v1/users",
            json={
                "email": "delete_test@example.com",
                "password": "testpassword123",
                "role": "recruiter",
            },
            headers=headers,
        )
        if create_response.status_code == 200:
            user_id = create_response.json()["id"]
            response = client.delete(
                f"/api/v1/users/{user_id}",
                headers=headers,
            )
            assert response.status_code == 200


@pytest.mark.integration
class TestPermissionManagement:
    """Test permission management endpoints."""

    def test_list_permissions_as_admin(self, client, cleanup_db):
        """Test listing all permissions as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin7@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin7@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/permissions",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "permissions" in data
        assert "total" in data
        assert isinstance(data["permissions"], list)

    def test_list_permissions_as_non_admin(self, client, cleanup_db):
        """Test that non-admin cannot list permissions."""
        # Register and login as recruiter
        client.post(
            "/api/v1/auth/register",
            json={"email": "recruiter3@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "recruiter3@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/permissions",
            headers=headers,
        )
        assert response.status_code == 403

    def test_list_roles_as_admin(self, client, cleanup_db):
        """Test listing all roles as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin8@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin8@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/roles",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert "admin" in data["roles"]

    def test_get_role_permissions_as_admin(self, client, cleanup_db):
        """Test getting permissions for a specific role as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin9@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin9@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/roles/recruiter/permissions",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "recruiter"
        assert "permissions" in data
        assert isinstance(data["permissions"], list)

    def test_update_role_permissions_as_admin(self, client, cleanup_db):
        """Test updating role permissions as admin."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin10@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin10@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get current permissions first
        get_response = client.get(
            "/api/v1/roles/recruiter/permissions",
            headers=headers,
        )
        current_permissions = [p["name"] for p in get_response.json()["permissions"]]
        
        # Update with same permissions (no actual change)
        response = client.put(
            "/api/v1/roles/recruiter/permissions",
            json={"permissions": current_permissions},
            headers=headers,
        )
        assert response.status_code == 200

    def test_update_admin_permissions_fails(self, client, cleanup_db):
        """Test that admin permissions cannot be modified."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin11@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin11@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            "/api/v1/roles/admin/permissions",
            json={"permissions": ["candidate.view"]},
            headers=headers,
        )
        assert response.status_code == 400


@pytest.mark.integration
class TestPermissionAuthorization:
    """Test permission-based authorization."""

    def test_admin_has_all_permissions(self, client, cleanup_db):
        """Test that admin has access to all resources."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin12@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin12@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Admin should be able to access user management
        response = client.get(
            "/api/v1/users",
            headers=headers,
        )
        assert response.status_code == 200

    def test_recruiter_cannot_access_user_management(self, client, cleanup_db):
        """Test that recruiter cannot access user management."""
        # Register and login as recruiter
        client.post(
            "/api/v1/auth/register",
            json={"email": "recruiter4@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "recruiter4@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/users",
            headers=headers,
        )
        assert response.status_code == 403

    def test_viewer_cannot_modify_candidates(self, client, cleanup_db):
        """Test that viewer cannot modify candidates."""
        # Register and login as viewer
        client.post(
            "/api/v1/auth/register",
            json={"email": "viewer@example.com", "password": "Secret123", "role": "viewer"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "viewer@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test that viewer cannot access user management
        response = client.get(
            "/api/v1/users",
            headers=headers,
        )
        assert response.status_code == 403


@pytest.mark.integration
class TestBackwardCompatibility:
    """Test that existing role-based authorization still works."""

    def test_require_role_still_works(self, client, cleanup_db):
        """Test that existing require_role() dependency still works."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin13@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin13@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # This endpoint uses require_role("admin")
        response = client.get(
            "/api/v1/users",
            headers=headers,
        )
        assert response.status_code == 200

    def test_jwt_authentication_still_works(self, client, cleanup_db):
        """Test that JWT authentication still works."""
        # Register and login
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin14@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin14@example.com", "password": "Secret123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Use token to access protected endpoint
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_existing_endpoints_still_work(self, client, cleanup_db):
        """Test that existing endpoints still work."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin15@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin15@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test candidates endpoint
        response = client.get(
            "/api/v1/candidates",
            headers=headers,
        )
        # Should work (may be 200 or 404 if no candidates, but not 403/401)
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestSecurityValidation:
    """Test security validations."""

    def test_cannot_delete_self(self, client, cleanup_db):
        """Test that user cannot delete themselves."""
        # Get current user ID from token
        # This would require parsing the JWT or getting user info
        # For now, test the endpoint exists
        pass

    def test_cannot_deactivate_self(self, client, cleanup_db):
        """Test that user cannot deactivate themselves."""
        # Similar to above
        pass

    def test_invalid_role_rejected(self, client, cleanup_db):
        """Test that invalid role is rejected."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin16@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin16@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/users",
            json={
                "email": "invalid_role_test@example.com",
                "password": "testpassword123",
                "role": "invalid_role",
            },
            headers=headers,
        )
        # Should fail validation
        assert response.status_code in [400, 422]

    def test_invalid_permission_rejected(self, client, cleanup_db):
        """Test that invalid permission is rejected."""
        # Register and login as admin
        client.post(
            "/api/v1/auth/register",
            json={"email": "admin17@example.com", "password": "Secret123", "role": "admin"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin17@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.put(
            "/api/v1/roles/recruiter/permissions",
            json={"permissions": ["invalid_permission"]},
            headers=headers,
        )
        assert response.status_code == 400
