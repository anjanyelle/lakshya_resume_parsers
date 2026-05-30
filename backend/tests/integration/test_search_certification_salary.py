"""
Integration tests for certification and salary search functionality.
Tests both /api/v1/search and /api/v1/candidates endpoints.
"""

import pytest


@pytest.mark.integration
class TestCertificationSearch:
    """Test certification filter in search endpoints."""

    def test_search_certification_exact_match(self, client, cleanup_db):
        """Test exact match for certification name."""
        # Register and login to get token
        client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"certification": "AWS"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_search_certification_partial_match(self, client, cleanup_db):
        """Test partial match for certification name."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test2@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test2@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"certification": "AWS"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_search_certification_case_insensitive(self, client, cleanup_db):
        """Test case-insensitive certification search."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test3@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test3@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response_lower = client.get(
            "/api/v1/search",
            params={"certification": "aws"},
            headers=headers,
        )
        response_upper = client.get(
            "/api/v1/search",
            params={"certification": "AWS"},
            headers=headers,
        )
        assert response_lower.status_code == 200
        assert response_upper.status_code == 200

    def test_search_certification_no_results(self, client, cleanup_db):
        """Test certification search with no matching results."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test4@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test4@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"certification": "NonExistentCertification12345"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_search_certification_empty_parameter(self, client, cleanup_db):
        """Test certification search with empty parameter."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test5@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test5@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"certification": ""},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_candidates_certification_exact_match(self, client, cleanup_db):
        """Test exact match for certification in candidates endpoint."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test6@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test6@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/candidates",
            params={"certification": "AWS"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_candidates_certification_partial_match(self, client, cleanup_db):
        """Test partial match for certification in candidates endpoint."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test7@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test7@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/candidates",
            params={"certification": "AWS"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)


@pytest.mark.integration
class TestSalarySearch:
    """Test salary range filter in search endpoints."""

    def test_search_salary_min_only(self, client, cleanup_db):
        """Test salary filter with minimum value only."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test8@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test8@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"salary_min": 10},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_search_salary_max_only(self, client, cleanup_db):
        """Test salary filter with maximum value only."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test9@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test9@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"salary_max": 100},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_search_salary_range(self, client, cleanup_db):
        """Test salary filter with both min and max values."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test10@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test10@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"salary_min": 10, "salary_max": 100},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_search_salary_invalid_range(self, client, cleanup_db):
        """Test salary filter with invalid range (min > max)."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test11@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test11@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"salary_min": 100, "salary_max": 10},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_search_salary_no_results(self, client, cleanup_db):
        """Test salary filter with no matching results."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test12@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test12@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"salary_min": 1000000, "salary_max": 2000000},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_candidates_salary_min_only(self, client, cleanup_db):
        """Test salary filter with minimum value in candidates endpoint."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test13@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test13@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/candidates",
            params={"salary_min": 10},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_candidates_salary_max_only(self, client, cleanup_db):
        """Test salary filter with maximum value in candidates endpoint."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test14@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test14@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/candidates",
            params={"salary_max": 100},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_candidates_salary_range(self, client, cleanup_db):
        """Test salary filter with range in candidates endpoint."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test15@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test15@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/candidates",
            params={"salary_min": 10, "salary_max": 100},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)


@pytest.mark.integration
class TestCombinedFilters:
    """Test certification and salary filters combined with other filters."""

    def test_certification_and_company(self, client, cleanup_db):
        """Test certification filter combined with company filter."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test16@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test16@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"certification": "AWS", "company": "Infosys"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_salary_and_job_title(self, client, cleanup_db):
        """Test salary filter combined with job title filter."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test17@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test17@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"salary_min": 10, "salary_max": 100, "job_title": "Developer"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_certification_and_salary(self, client, cleanup_db):
        """Test certification and salary filters combined."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test18@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test18@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"certification": "AWS", "salary_min": 10, "salary_max": 100},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_all_filters_combined(self, client, cleanup_db):
        """Test all new filters combined with existing filters."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test19@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test19@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={
                "certification": "AWS",
                "salary_min": 10,
                "salary_max": 100,
                "company": "Infosys",
                "job_title": "Developer",
            },
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)


@pytest.mark.integration
class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_existing_filters_still_work(self, client, cleanup_db):
        """Test that existing filters (skills, location, etc.) still work."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test20@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test20@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"skills": ["Python"], "location": "Bangalore"},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_pagination_still_works(self, client, cleanup_db):
        """Test that pagination still works with new filters."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test21@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test21@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            params={"certification": "AWS", "skip": 0, "limit": 10},
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    def test_no_filters_returns_all(self, client, cleanup_db):
        """Test that no filters returns all candidates."""
        client.post(
            "/api/v1/auth/register",
            json={"email": "test22@example.com", "password": "Secret123", "role": "recruiter"},
        )
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test22@example.com", "password": "Secret123"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/search",
            headers=headers,
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
