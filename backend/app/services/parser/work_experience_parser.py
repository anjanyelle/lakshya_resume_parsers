from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date
from typing import Iterable

import dateparser
from app.core.config import get_settings
from app.services.llm_service import LLMParsingService

logger = logging.getLogger(__name__)


DATE_RANGE_RE = re.compile(
    r"(?P<start>[\w./\- ]{3,20})\s*[-–—]\s*(?P<end>present|current|till date|now|[\w./\- ]{3,20})",
    re.IGNORECASE,
)
COMPANY_LINE_RE = re.compile(
    r"(?P<company>.+?)\s*(?:[-–—|,])\s*(?P<title>.+)"
)
LOCATION_RE = re.compile(r"\b([A-Za-z .]+,\s*[A-Z]{2})\b")
CLIENT_RE = re.compile(r"\bclient[:\-]\s*(?P<client>.+)", re.IGNORECASE)

TITLE_NORMALIZATION = {
    "sr.": "senior",
    "swe": "software engineer",
    "dev": "developer",
    "mgr": "manager",
}

COMPANY_NORMALIZATION = {
    "google inc": "Google",
    "google llc": "Google",
    "amazon.com": "Amazon",
    "amazon inc": "Amazon",
    "microsoft corporation": "Microsoft",
}

TITLE_RANKS = {
    "intern": 1,
    "junior": 2,
    "engineer": 3,
    "senior": 4,
    "lead": 5,
    "manager": 6,
    "director": 7,
    "vp": 8,
}


@dataclass(frozen=True)
class JobEntry:
    company: str | None
    title: str | None
    start_date: date | None
    end_date: date | None
    is_current: bool
    location: str | None
    description: str
    bullets: list[str]
    duration_months: int | None
    client: str | None
    employment_type: str | None
    confidence: float


class WorkExperienceParser:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = LLMParsingService()

    def parse_experience_section(self, text: str) -> list[JobEntry]:
        chunks = self.extract_individual_jobs(text)
        jobs: list[JobEntry] = []
        for chunk in chunks:
            job = self._parse_chunk(chunk)
            if job.confidence < 0.8:
                llm_job = self._llm_fallback(chunk)
                if llm_job:
                    job = llm_job
            jobs.append(job)
        return jobs

    def extract_individual_jobs(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        boundaries: list[int] = []
        for idx, line in enumerate(lines):
            if DATE_RANGE_RE.search(line):
                boundaries.append(idx)

        if not boundaries:
            return ["\n".join(lines)]

        chunks = []
        for i, start in enumerate(boundaries):
            end = boundaries[i + 1] if i + 1 < len(boundaries) else len(lines)
            chunks.append("\n".join(lines[start:end]))
        return chunks

    def normalize_company_names(self, name: str | None) -> str | None:
        if not name:
            return None
        key = name.strip().lower()
        return COMPANY_NORMALIZATION.get(key, name.strip())

    def normalize_job_titles(self, title: str | None) -> str | None:
        if not title:
            return None
        normalized = title.strip().lower()
        for short, long in TITLE_NORMALIZATION.items():
            normalized = re.sub(rf"\b{re.escape(short)}\b", long, normalized)
        return normalized.title()

    def calculate_total_experience(self, jobs: Iterable[JobEntry]) -> int:
        return sum(job.duration_months or 0 for job in jobs)

    def detect_career_progression(self, jobs: list[JobEntry]) -> bool:
        ranks = []
        for job in jobs:
            if not job.title:
                continue
            title = job.title.lower()
            rank = max((score for key, score in TITLE_RANKS.items() if key in title), default=0)
            ranks.append(rank)
        return ranks == sorted(ranks) if ranks else False

    def _parse_chunk(self, chunk: str) -> JobEntry:
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        header = lines[0] if lines else ""
        company, title = self._parse_company_title(header)

        start_date, end_date, is_current = self._parse_dates(chunk)
        location = self._parse_location(chunk)
        bullets = self._extract_bullets(lines[1:])
        description = "\n".join(bullets) if bullets else "\n".join(lines[1:])
        duration_months = self._calc_duration_months(start_date, end_date, is_current)
        client = self._extract_client(chunk)
        employment_type = self._detect_employment_type(chunk)

        confidence = self._score_confidence(company, title, start_date)

        return JobEntry(
            company=self.normalize_company_names(company),
            title=self.normalize_job_titles(title),
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            location=location,
            description=description.strip(),
            bullets=bullets,
            duration_months=duration_months,
            client=client,
            employment_type=employment_type,
            confidence=confidence,
        )

    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:
        match = COMPANY_LINE_RE.search(header)
        if match:
            return match.group("company").strip(), match.group("title").strip()
        return None, header.strip() if header else None

    def _parse_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        match = DATE_RANGE_RE.search(text)
        if not match:
            return None, None, False

        start_raw = match.group("start")
        end_raw = match.group("end")
        start_date = self._parse_date(start_raw)
        if end_raw.lower() in {"present", "current", "till date", "now"}:
            return start_date, None, True
        end_date = self._parse_date(end_raw)
        return start_date, end_date, False

    def _parse_date(self, value: str) -> date | None:
        parsed = dateparser.parse(value, settings={"PREFER_DAY_OF_MONTH": "first"})
        return parsed.date() if parsed else None

    def _parse_location(self, text: str) -> str | None:
        match = LOCATION_RE.search(text)
        return match.group(1).strip() if match else None

    def _extract_bullets(self, lines: list[str]) -> list[str]:
        bullets = []
        for line in lines:
            if line.startswith(("-", "•", "*")):
                bullets.append(line.lstrip("-•* ").strip())
        return bullets

    def _extract_client(self, text: str) -> str | None:
        match = CLIENT_RE.search(text)
        return match.group("client").strip() if match else None

    def _detect_employment_type(self, text: str) -> str | None:
        lowered = text.lower()
        if "contract" in lowered:
            return "contract"
        if "consultant" in lowered or "consulting" in lowered:
            return "consulting"
        if "part-time" in lowered or "part time" in lowered:
            return "part_time"
        return "full_time"

    def _calc_duration_months(
        self, start: date | None, end: date | None, is_current: bool
    ) -> int | None:
        if not start:
            return None
        end_date = end or date.today()
        if end_date < start:
            logger.warning("Date inconsistency detected", extra={"start": start, "end": end})
            return None
        return (end_date.year - start.year) * 12 + (end_date.month - start.month) + 1

    def _score_confidence(
        self, company: str | None, title: str | None, start_date: date | None
    ) -> float:
        score = 0.0
        if company:
            score += 0.4
        if title:
            score += 0.3
        if start_date:
            score += 0.3
        return score

    def _llm_fallback(self, chunk: str) -> JobEntry | None:
        if self.settings.LLM_PROVIDER == "none":
            return None

        entries = self.llm.extract_work_experience(chunk)
        if not entries:
            return None

        payload = entries[0]
        start_date = self._parse_date(payload.get("start_date", ""))
        end_date = self._parse_date(payload.get("end_date", ""))
        is_current = payload.get("is_current", False)
        duration_months = self._calc_duration_months(start_date, end_date, is_current)
        bullets = payload.get("responsibilities") or payload.get("bullets") or []

        return JobEntry(
            company=self.normalize_company_names(payload.get("company_name") or payload.get("company")),
            title=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            location=payload.get("location"),
            description="\n".join(bullets) if bullets else payload.get("description", ""),
            bullets=bullets,
            duration_months=duration_months,
            client=payload.get("client"),
            employment_type=payload.get("employment_type"),
            confidence=payload.get("confidence", 0.85),
        )

    def _call_llm(self, prompt: str) -> str | None:
        return self.llm._call_llm(prompt, task="work_experience").content
