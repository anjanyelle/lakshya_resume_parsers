from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    content: str
    tokens: int | None = None
    model: str | None = None


class LLMParsingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, tuple[float, LLMResponse]] = {}
        self._rate_timestamps: list[float] = []

    def extract_resume_intelligence(self, text: str) -> dict[str, Any]:
        chunks = self._chunk_text(text)
        if len(chunks) == 1:
            prompt = self._resume_intelligence_prompt(chunks[0])
            response = self._call_llm(prompt, task="resume_intelligence")
            data = self._parse_json(response.content, expect_array=False)
            return data or {}

        partials: list[dict[str, Any]] = []
        for idx, chunk in enumerate(chunks, start=1):
            prompt = self._resume_intelligence_prompt(
                chunk,
                header=f"Chunk {idx} of {len(chunks)}",
            )
            response = self._call_llm(prompt, task=f"resume_intelligence_{idx}")
            data = self._parse_json(response.content, expect_array=False)
            if isinstance(data, dict):
                partials.append(data)
        return self._merge_resume_intelligence(partials)

    def _resume_intelligence_prompt(self, text: str, header: str | None = None) -> str:
        prefix = f"{header}\n\n" if header else ""
        return prefix + (
            "You are an AI Resume Intelligence Engine.\n\n"
            "Your task is to analyze senior-level IT resumes (5–20 pages) and extract "
            "structured information for database storage.\n\n"
            "Focus on accuracy, normalization, and enterprise-level experience detection.\n\n"
            "Extract and categorize the following details:\n\n"
            "1. Candidate Information\n"
            "   - Full Name\n"
            "   - Email\n"
            "   - Phone\n"
            "   - Location\n"
            "   - LinkedIn\n"
            "   - Visa / Work Authorization (if available)\n\n"
            "2. Professional Summary\n"
            "   - Years of Experience\n"
            "   - Primary Role (Full Stack / Data Engineer / Java / DevOps etc.)\n"
            "   - Seniority Level\n\n"
            "3. Technical Skills (Categorized)\n\n"
            "   Frontend:\n"
            "   Backend:\n"
            "   Programming Languages:\n"
            "   Frameworks:\n"
            "   Databases:\n"
            "   Cloud Platforms:\n"
            "   DevOps Tools:\n"
            "   Data Engineering Tools:\n"
            "   Testing Tools:\n"
            "   BI / Visualization:\n"
            "   Messaging / Streaming:\n"
            "   Operating Systems:\n"
            "   Other Tools:\n\n"
            "4. Project / Client Experience\n\n"
            "For each client extract:\n"
            "   - Client Name\n"
            "   - Role\n"
            "   - Duration\n"
            "   - Location\n"
            "   - Industry\n"
            "   - Responsibilities (summary)\n"
            "   - Technologies Used\n"
            "   - Environment\n\n"
            "5. Architecture & Enterprise Experience\n\n"
            "Detect experience in:\n"
            "   - Microservices\n"
            "   - Distributed Systems\n"
            "   - Data Platforms\n"
            "   - ML Pipelines\n"
            "   - Event Streaming\n"
            "   - API Gateways\n"
            "   - Security Implementations\n\n"
            "6. Cloud & DevOps Experience\n\n"
            "   - CI/CD tools\n"
            "   - Containerization\n"
            "   - Infrastructure as Code\n"
            "   - Monitoring tools\n\n"
            "7. Education\n\n"
            "8. Certifications\n\n"
            "9. Domain Experience\n\n"
            "   - Banking\n"
            "   - Retail\n"
            "   - Healthcare\n"
            "   - Telecom\n"
            "   - Finance\n"
            "   - Ecommerce\n\n"
            "Normalize all skills (example: React.js = ReactJS = React).\n\n"
            "Return output strictly in JSON format for database storage.\n\n"
            f"Resume Text:\n{text}"
        )

    def _chunk_text(self, text: str) -> list[str]:
        limit = self.settings.LLM_MAX_CHARS
        chunk_size = self.settings.LLM_CHUNK_CHARS
        overlap = self.settings.LLM_CHUNK_OVERLAP
        if len(text) <= limit:
            return [text]

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}" if current else paragraph
            if len(candidate) <= chunk_size:
                current = candidate
                continue
            if current:
                chunks.append(current)
            if len(paragraph) <= chunk_size:
                current = paragraph
            else:
                start = 0
                while start < len(paragraph):
                    end = min(start + chunk_size, len(paragraph))
                    chunks.append(paragraph[start:end])
                    start = end - overlap if overlap and end < len(paragraph) else end
                current = ""
        if current:
            chunks.append(current)
        return chunks or [text]

    def _merge_resume_intelligence(
        self, partials: list[dict[str, Any]]
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {
            "candidate_information": {},
            "professional_summary": {},
            "technical_skills": {},
            "project_client_experience": [],
            "architecture_enterprise_experience": [],
            "cloud_devops_experience": {},
            "education": [],
            "certifications": [],
            "domain_experience": [],
        }

        def first_non_empty(value: Any, existing: Any) -> Any:
            return existing if existing not in (None, "", [], {}) else value

        def merge_list(target: list[Any], items: Any) -> None:
            if items is None:
                return
            if isinstance(items, list):
                target.extend(items)
            else:
                target.append(items)

        def merge_dict(target: dict[str, Any], source: Any) -> None:
            if not isinstance(source, dict):
                return
            for key, value in source.items():
                if isinstance(value, dict) and isinstance(target.get(key), dict):
                    merge_dict(target[key], value)
                elif isinstance(value, list):
                    existing = target.get(key, [])
                    if not isinstance(existing, list):
                        existing = [existing]
                    target[key] = self._unique_list(existing + value)
                else:
                    target[key] = first_non_empty(value, target.get(key))

        for entry in partials:
            if not isinstance(entry, dict):
                continue
            candidate_info = (
                entry.get("candidate_information")
                or entry.get("candidate_info")
                or entry.get("candidate")
            )
            merge_dict(merged["candidate_information"], candidate_info)

            professional = entry.get("professional_summary") or {}
            if isinstance(professional, dict):
                existing_years = merged["professional_summary"].get("years_of_experience")
                new_years = professional.get("years_of_experience")
                try:
                    if new_years is not None:
                        new_years_val = float(new_years)
                        if existing_years is None or new_years_val > float(existing_years):
                            merged["professional_summary"]["years_of_experience"] = new_years_val
                except (TypeError, ValueError):
                    pass
                for key in ("primary_role", "seniority_level"):
                    merged["professional_summary"][key] = first_non_empty(
                        professional.get(key),
                        merged["professional_summary"].get(key),
                    )

            technical = entry.get("technical_skills")
            if isinstance(technical, dict):
                for key, value in technical.items():
                    existing = merged["technical_skills"].get(key, [])
                    merged["technical_skills"][key] = self._unique_list(
                        self._coerce_list(existing) + self._coerce_list(value)
                    )

            merge_list(
                merged["project_client_experience"],
                entry.get("project_client_experience")
                or entry.get("client_experience")
                or entry.get("projects"),
            )

            merge_list(
                merged["architecture_enterprise_experience"],
                entry.get("architecture_enterprise_experience")
                or entry.get("architecture_experience"),
            )

            merge_dict(
                merged["cloud_devops_experience"],
                entry.get("cloud_devops_experience") or entry.get("cloud_devops"),
            )

            merge_list(merged["education"], entry.get("education"))
            merge_list(merged["certifications"], entry.get("certifications"))
            merge_list(merged["domain_experience"], entry.get("domain_experience"))

        merged["project_client_experience"] = self._unique_list(
            merged["project_client_experience"]
        )
        merged["architecture_enterprise_experience"] = self._unique_list(
            merged["architecture_enterprise_experience"]
        )
        merged["domain_experience"] = self._unique_list(merged["domain_experience"])
        return merged

    def _coerce_list(self, value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _unique_list(self, values: list[Any]) -> list[Any]:
        seen: set[str] = set()
        unique: list[Any] = []
        for item in values:
            marker = json.dumps(item, sort_keys=True) if isinstance(item, dict) else str(item)
            if marker in seen:
                continue
            seen.add(marker)
            unique.append(item)
        return unique

    def extract_work_experience(self, text: str) -> list[dict[str, Any]]:
        prompt = (
            "Extract work experience from this resume section. "
            "Return JSON array of objects with: company_name, job_title, "
            "start_date, end_date, is_current, location, responsibilities (array). "
            f"Here's the text:\n{text}"
        )
        response = self._call_llm(prompt, task="work_experience")
        data = self._parse_json(response.content, expect_array=True)
        if isinstance(data, dict):
            return [data]
        return data or []

    def infer_skills(self, text: str) -> list[dict[str, Any]]:
        prompt = (
            "Analyze these job descriptions and extract technical skills, tools, "
            "and technologies mentioned. Also infer related skills. "
            "Return JSON array of {skill_name, category, proficiency_level, evidence}. "
            f"Text:\n{text}"
        )
        response = self._call_llm(prompt, task="skill_inference")
        data = self._parse_json(response.content, expect_array=True)
        return data or []

    def normalize_titles_and_companies(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Normalize these company names and job titles to standard formats. "
            f"Input: {json.dumps(raw_data, ensure_ascii=False)}. "
            "Return JSON with normalized values."
        )
        response = self._call_llm(prompt, task="normalization")
        data = self._parse_json(response.content, expect_array=False)
        return data or {}

    def _call_llm(self, prompt: str, task: str) -> LLMResponse:
        if self.settings.LLM_PROVIDER == "none":
            return LLMResponse(content="{}")

        cache_key = self._cache_key(prompt, task)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        self._enforce_rate_limit()

        primary = self.settings.LOCAL_LLM_MODEL
        response = self._call_local(prompt, primary)
        if not response and self.settings.LOCAL_LLM_FALLBACK_MODEL:
            response = self._call_local(prompt, self.settings.LOCAL_LLM_FALLBACK_MODEL)

        if not response:
            if self.settings.ENVIRONMENT.lower() in {"development", "local"} or (
                self.settings.LLM_PROVIDER == "local"
            ):
                logger.warning("LLM unavailable; returning empty response")
                return LLMResponse(content="{}")
            raise RuntimeError("LLM request failed")

        self._set_cached(cache_key, response)
        return response

    def _call_local(self, prompt: str, model: str | None) -> LLMResponse | None:
        if not model:
            return None
        options: dict[str, Any] = {"temperature": self.settings.OLLAMA_TEMPERATURE}
        if self.settings.OLLAMA_NUM_CTX is not None:
            options["num_ctx"] = self.settings.OLLAMA_NUM_CTX
        if self.settings.OLLAMA_NUM_BATCH is not None:
            options["num_batch"] = self.settings.OLLAMA_NUM_BATCH
        if self.settings.OLLAMA_NUM_THREAD is not None:
            options["num_thread"] = self.settings.OLLAMA_NUM_THREAD
        if self.settings.OLLAMA_NUM_GPU is not None:
            options["num_gpu"] = self.settings.OLLAMA_NUM_GPU

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
        if self.settings.OLLAMA_KEEP_ALIVE:
            payload["keep_alive"] = self.settings.OLLAMA_KEEP_ALIVE

        attempts = self.settings.LLM_MAX_RETRIES + 1
        for attempt in range(1, attempts + 1):
            try:
                response = httpx.post(
                    f"{self.settings.LOCAL_LLM_BASE_URL}/api/generate",
                    json=payload,
                    timeout=self.settings.LLM_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("response", "")
                tokens = data.get("eval_count")
                self._track_cost(task="local", tokens=tokens, model=model)
                return LLMResponse(content=content, tokens=tokens, model=model)
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Local LLM call failed",
                    extra={"attempt": attempt, "max_attempts": attempts},
                )
                if attempt < attempts:
                    time.sleep(1.5 * attempt)
                    continue
                return None

    def _parse_json(self, content: str, expect_array: bool) -> Any:
        extracted = self._extract_json_block(content)
        if extracted is None:
            extracted = content
        try:
            parsed = json.loads(extracted)
        except json.JSONDecodeError:
            logger.warning("Malformed LLM JSON response")
            return [] if expect_array else {}

        if expect_array and not isinstance(parsed, list):
            return [parsed] if isinstance(parsed, dict) else []
        if not expect_array and not isinstance(parsed, dict):
            return {}
        return parsed

    @staticmethod
    def _extract_json_block(text: str) -> str | None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return None

    def _enforce_rate_limit(self) -> None:
        if self.settings.LLM_PROVIDER == "local":
            return
        limit = self.settings.LLM_RATE_LIMIT_PER_MINUTE
        now = time.time()
        window_start = now - 60
        self._rate_timestamps = [t for t in self._rate_timestamps if t >= window_start]
        if len(self._rate_timestamps) >= limit:
            raise RuntimeError("LLM rate limit exceeded")
        self._rate_timestamps.append(now)

    def _track_cost(self, task: str, tokens: int | None, model: str) -> None:
        if tokens is None:
            return
        logger.info(
            "LLM usage",
            extra={"task": task, "tokens": tokens, "model": model},
        )

    def _cache_key(self, prompt: str, task: str) -> str:
        payload = f"{task}:{prompt}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _get_cached(self, key: str) -> LLMResponse | None:
        ttl = self.settings.LLM_CACHE_TTL_SECONDS
        entry = self._cache.get(key)
        if not entry:
            return None
        timestamp, response = entry
        if time.time() - timestamp > ttl:
            self._cache.pop(key, None)
            return None
        return response

    def _set_cached(self, key: str, response: LLMResponse) -> None:
        self._cache[key] = (time.time(), response)
