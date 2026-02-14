from __future__ import annotations

from pathlib import Path

from locust import HttpUser, between, task


class ResumeParserUser(HttpUser):
    wait_time = between(0.5, 2.0)
    token: str | None = None

    def on_start(self) -> None:
        email = "loadtest@example.com"
        password = "Secret123"
        self.client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "role": "admin"},
        )
        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        if login.status_code == 200:
            self.token = login.json()["access_token"]

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(3)
    def list_candidates(self) -> None:
        self.client.get("/api/v1/candidates", headers=self._auth_headers())

    @task(2)
    def search_candidates(self) -> None:
        self.client.get("/api/v1/search?q=python", headers=self._auth_headers())

    @task(1)
    def upload_resume(self) -> None:
        sample_path = Path(__file__).resolve().parent / "tests" / "fixtures" / "resumes" / "sample_resume.pdf"
        if not sample_path.exists():
            return
        data = sample_path.read_bytes()
        files = {
            "file": ("sample_resume.pdf", data, "application/pdf")
        }
        self.client.post("/api/v1/upload", files=files, headers=self._auth_headers())
