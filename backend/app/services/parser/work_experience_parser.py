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


MONTH_TOKEN = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_TOKEN = (
    r"(?:"
    r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
    r"|\d{4}[/-]\d{1,2}"  # YYYY-MM or YYYY/MM
    r"|\d{1,2}[/-]\d{2}"  # MM/YY
    r"|\d{1,2}[/-]\d{4}"  # MM/YYYY
    r"|\d{4}"  # YYYY
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{4}}"  # MMM YYYY
    rf"|{MONTH_TOKEN}\s*[\u2019']\s*\d{{2}}"  # MMM 'YY
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{2}}"  # MMM YY
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>{DATE_TOKEN})\s*(?:\s*(?:[-–—→]|to|until|thru|through)\s*)\s*(?P<end>present|current|till\s+date|now|{DATE_TOKEN})",
    re.IGNORECASE,
)

PRESENT_RE = re.compile(r"\b(present|current|till\s+date|now)\b", re.IGNORECASE)
DATE_ANCHOR_RE = re.compile(rf"\b(?:{DATE_TOKEN})\b", re.IGNORECASE)
COMPANY_LINE_RE = re.compile(
    r"(?P<company>.+?)\s*(?:[-–—|,])\s*(?P<title>.+)"
)
LOCATION_RE = re.compile(r"\b([A-Za-z .]+,\s*[A-Z]{2})\b")
TITLE_HINT_RE = re.compile(r"\b(engineer|developer|architect|manager|lead|analyst|consultant|director|specialist)\b", re.IGNORECASE)
RESPONSIBILITY_MARKERS = {"responsibilities", "key responsibilities", "responsibility"}
COMPANY_HINT_RE = re.compile(r"\b(inc|llc|ltd|corp|corporation|company|technologies|systems|health|bank|solutions|services)\b", re.IGNORECASE)
ENVIRONMENT_LINE_RE = re.compile(
    r"^(?:environments?|environment|tools?|technologies|tech\s*stack)\s*[:\-–—]",
    re.IGNORECASE,
)
PLACEHOLDER_ORG_RE = re.compile(
    r"^(company|client|organization|employer|designation|title|role)\b",
    re.IGNORECASE,
)
CLIENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(?:end\s+client|client)\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
    re.compile(r"\bproject\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
    re.compile(r"\bworked\s+for\s+(?P<client>[A-Za-z0-9][A-Za-z0-9 &.,()/-]{2,})", re.IGNORECASE),
    re.compile(r"\bproject\s+for\s+(?P<client>[A-Za-z0-9][A-Za-z0-9 &.,()/-]{2,})", re.IGNORECASE),
]

CLIENT_HEADER_RE = re.compile(
    r"^(?:end\s+client|client|project)\s*[:\-–—]",
    re.IGNORECASE,
)

LOCATION_MARKER_RE = re.compile(
    r"\(?\b(?:location|loc)\b\s*[:\-–—]\s*(?P<loc>[^\n\r\t\)\|\u2022]{2,120})\)?",
    re.IGNORECASE,
)

LOCATION_TAG_RE = re.compile(r"^(?P<tag>[A-Za-z]{2,20})\)$")

LABELED_ORG_RE = re.compile(
    r"\b(organization|company|employer)\b\s*[:\-–—]\s*(?P<value>.+)$",
    re.IGNORECASE,
)
LABELED_TITLE_RE = re.compile(
    r"\b(designation|title|role|position)\b\s*[:\-–—]\s*(?P<value>.+)$",
    re.IGNORECASE,
)
LABELED_RESP_RE = re.compile(
    r"\b(responsibilities|responsibility|roles?\s*&\s*responsibilities)\b\s*[:\-–—]?\s*(?P<value>.*)$",
    re.IGNORECASE,
)

TITLE_NORMALIZATION = {
    "sr": "senior",
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
    designation: str | None = None


class WorkExperienceParser:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = LLMParsingService()

    @staticmethod
    def build_date_anchor_excerpt(text: str, *, context_lines: int = 5) -> str:
        raw_lines = [ln.rstrip() for ln in (text or "").splitlines()]
        if not raw_lines:
            return ""

        anchor_indexes: list[int] = []
        for idx, ln in enumerate(raw_lines):
            if not ln.strip():
                continue
            if DATE_RANGE_RE.search(ln):
                anchor_indexes.append(idx)
                continue
            if PRESENT_RE.search(ln) and DATE_ANCHOR_RE.search(ln):
                anchor_indexes.append(idx)
                continue
            if DATE_ANCHOR_RE.search(ln) and re.search(r"(?:[-–—→]|\bto\b)", ln, flags=re.IGNORECASE):
                anchor_indexes.append(idx)

        if not anchor_indexes:
            return ""

        windows: list[tuple[int, int]] = []
        n = len(raw_lines)
        for idx in sorted(set(anchor_indexes)):
            start = max(0, idx - context_lines)
            end = min(n, idx + context_lines + 1)
            windows.append((start, end))

        windows.sort(key=lambda t: (t[0], t[1]))
        merged: list[tuple[int, int]] = []
        cur_start, cur_end = windows[0]
        for start, end in windows[1:]:
            if start <= cur_end:
                cur_end = max(cur_end, end)
                continue
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end
        merged.append((cur_start, cur_end))

        chunks: list[str] = []
        for start, end in merged:
            block_lines = [ln for ln in raw_lines[start:end] if ln.strip()]
            if not block_lines:
                continue
            chunks.append("\n".join(block_lines).strip())

        return "\n\n".join([c for c in chunks if c]).strip()

    @staticmethod
    def _looks_like_skillish_header(value: str | None) -> bool:
        cleaned = str(value or "").strip()
        if not cleaned:
            return False
        lowered = cleaned.lower()

        if re.match(r"^(environment|env|technologies|tools)\s*[:\-–—]", lowered):
            return True

        if re.fullmatch(
            r"(?:django|flask|fastapi|spring|react|node|docker|kubernetes|terraform|jenkins|gitlab|github|aws|azure|gcp|sql|python|java|postgres|postgresql|mysql|redis|kafka|elasticsearch|splunk|datadog|prometheus|grafana)",
            lowered,
        ) and len(cleaned) <= 40:
            return True
        if ("·" in cleaned or "•" in cleaned) and len(cleaned) <= 160:
            return True
        if cleaned.count(",") >= 2 and len(cleaned) <= 160:
            return True
        if re.search(
            r"\b(django|flask|fastapi|spring|react|node|docker|kubernetes|terraform|jenkins|gitlab|github|aws|azure|gcp|sql|python|java|postgres|postgresql|mysql|redis|kafka|elasticsearch|splunk|datadog|prometheus|grafana)\b",
            lowered,
        ):
            parts = [
                p.strip()
                for p in re.split(r"[,/|·•\u2022]", lowered)
                if p.strip()
            ]
            if len(parts) >= 3 and len(cleaned) <= 180:
                return True
        return False

    def parse_experience_section(self, text: str) -> list[JobEntry]:
        chunks = self.extract_individual_jobs(text)
        jobs: list[JobEntry] = []
        for chunk in chunks:
            job = self._parse_chunk(chunk)
            if job.confidence < 0.8:
                llm_job = self._llm_fallback(chunk)
                if llm_job:
                    job = llm_job
            if self._is_plausible_job(job):
                jobs.append(job)
        return jobs

    @staticmethod
    def _is_plausible_job(job: JobEntry) -> bool:
        company = str(job.company or "").strip()
        title = str(job.title or "").strip()
        if not company and not title:
            return False
        if PLACEHOLDER_ORG_RE.match(company) or PLACEHOLDER_ORG_RE.match(title):
            return False
        if "@" in company or "@" in title:
            return False
        if "http" in company.lower() or "http" in title.lower():
            return False
        if company and len(company) > 120:
            return False
        if title and len(title) > 120:
            return False

        # Reject skill/tool lists accidentally promoted into a "job" header (common PDF failure mode).
        if WorkExperienceParser._looks_like_skillish_header(company) or WorkExperienceParser._looks_like_skillish_header(title):
            return False

        has_dates = bool(job.start_date) or bool(job.end_date)
        has_body = bool(job.bullets) or bool(str(job.description or "").strip())
        if not has_dates and not has_body:
            return False
        return job.confidence >= 0.5

    def extract_individual_jobs(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        boundaries: list[int] = []
        for idx, line in enumerate(lines):
            if CLIENT_HEADER_RE.match(line):
                boundaries.append(idx)
                continue
            if DATE_ANCHOR_RE.search(line) and idx + 1 < len(lines) and PRESENT_RE.search(lines[idx + 1]):
                boundaries.append(idx)
                continue
            if PRESENT_RE.search(line) and idx > 0 and DATE_ANCHOR_RE.search(lines[idx - 1]):
                boundaries.append(idx - 1)
                continue
            if self._has_date_anchor(line):
                boundaries.append(idx)

        if not boundaries:
            return ["\n".join(lines)]

        starts: list[int] = []
        last_start = -1
        for idx in boundaries:
            start = idx
            if CLIENT_HEADER_RE.match(lines[idx]):
                if start <= last_start:
                    start = idx
                starts.append(start)
                last_start = start
                continue
            for back in range(1, 4):
                j = idx - back
                if j < 0:
                    break
                prev = lines[j]
                if ENVIRONMENT_LINE_RE.match(prev) or prev.strip().lower() in RESPONSIBILITY_MARKERS:
                    break
                if DATE_RANGE_RE.search(prev):
                    break
                if prev.startswith(("-", "•", "*")):
                    break
                if self._looks_like_skillish_header(prev):
                    break
                if self._looks_like_title(prev) and not self._looks_like_company(prev):
                    continue
                if self._looks_like_company(prev):
                    start = j
            if start <= last_start:
                start = idx
            starts.append(start)
            last_start = start

        chunks: list[str] = []
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else len(lines)
            if end <= start:
                continue
            chunks.append("\n".join(lines[start:end]))
        return chunks

    def _has_date_anchor(self, line: str) -> bool:
        if DATE_RANGE_RE.search(line):
            return True
        if PRESENT_RE.search(line) and DATE_ANCHOR_RE.search(line):
            return True
        if DATE_ANCHOR_RE.search(line) and re.search(r"(?:[-–—→]|\bto\b)", line, flags=re.IGNORECASE):
            return True
        return False

    def normalize_company_names(self, name: str | None) -> str | None:
        if not name:
            return None
        key = name.strip().lower()
        return COMPANY_NORMALIZATION.get(key, name.strip())

    def normalize_job_titles(self, title: str | None) -> str | None:
        if not title:
            return None
        normalized = title.strip().lower()
        normalized = re.sub(r"[./]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        for short, long in TITLE_NORMALIZATION.items():
            normalized = re.sub(rf"\b{re.escape(short)}\b", long, normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
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
        company, title, location, start_date, end_date, is_current, body_start = self._parse_header_lines(lines)

        location, company, title = self._extract_and_clean_location(location, company, title, chunk)

        labeled_company, labeled_title, labeled_desc = self._parse_labeled_fields(lines[1:])
        if labeled_company and not company:
            company = labeled_company
        if labeled_title:
            title_clean = str(title or "").strip()
            title_is_locationish = bool(self._parse_location(title_clean))
            should_override = (
                (not title_clean)
                or title_clean.lower() in {"organization", "designation"}
                or PLACEHOLDER_ORG_RE.match(title_clean)
                or title_is_locationish
                or not self._looks_like_title(title_clean)
            )
            if should_override:
                title = labeled_title
        if labeled_desc:
            body_start = max(body_start, 1)

        if not start_date and not end_date:
            start_date, end_date, is_current = self._parse_dates(chunk)
        if not location:
            location = self._parse_location(chunk)

        body_lines = lines[body_start:]
        bullets = self._extract_bullets(body_lines)
        description_source = labeled_desc or (bullets if bullets else body_lines)
        description = "\n".join(description_source)
        duration_months = self._calc_duration_months(start_date, end_date, is_current)
        client = self._extract_client(chunk)
        if client:
            company_clean = str(company or "").strip()
            if not company_clean:
                company = client
            else:
                company_l = company_clean.lower().strip(":").strip()
                if PLACEHOLDER_ORG_RE.match(company_l) or company_l.startswith("client") or company_l.startswith("end client"):
                    company = client
        if client and company and self._client_looks_embedded_in_company(company, client):
            cleaned = self._remove_embedded_client(company, client)
            company = cleaned or company
        employment_type = self._detect_employment_type(chunk)

        confidence = self._score_confidence(company, title, start_date, end_date, is_current, client, bullets)
        if labeled_company or labeled_title:
            confidence = max(confidence, 0.85 if (company and title and start_date) else 0.75)

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
            designation=self.normalize_job_titles(title),
        )

    @staticmethod
    def _normalize_location_tag(tag: str) -> str:
        cleaned = re.sub(r"\s+", " ", (tag or "").strip())
        if len(cleaned) == 2:
            return cleaned.upper()
        return cleaned.title()

    def _extract_and_clean_location(
        self,
        location: str | None,
        company: str | None,
        title: str | None,
        chunk: str,
    ) -> tuple[str | None, str | None, str | None]:
        chunk_loc = None
        match = LOCATION_MARKER_RE.search(chunk or "")
        if match:
            chunk_loc = (match.group("loc") or "").strip().strip("-–—|,;:")
            chunk_loc = re.split(r"\s{2,}|\||\u2022", chunk_loc)[0].strip()
            if chunk_loc and len(chunk_loc) > 120:
                chunk_loc = None

        tag = None
        title_stripped = (title or "").strip()
        tag_match = LOCATION_TAG_RE.match(title_stripped)
        if tag_match:
            tag = self._normalize_location_tag(tag_match.group("tag"))

        company_clean = (company or "").strip() or None
        title_clean = (title or "").strip() or None

        def strip_location_marker(value: str | None) -> str | None:
            if not value:
                return None
            next_value = LOCATION_MARKER_RE.sub("", value).strip(" -–—|,;:")
            next_value = re.sub(r"\s+", " ", next_value).strip()
            return next_value or None

        company_clean = strip_location_marker(company_clean)
        title_clean = strip_location_marker(title_clean)

        final_location = (location or "").strip() or None
        if not final_location:
            final_location = chunk_loc

        if tag:
            if final_location:
                if "," in final_location:
                    final_location = final_location
                else:
                    final_location = f"{final_location}, {tag}"
            else:
                final_location = tag
            title_clean = None

        if company_clean and len(company_clean) <= 4 and company_clean.endswith(")"):
            company_clean = None

        return final_location, company_clean, title_clean

    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:
        match = COMPANY_LINE_RE.search(header)
        if match:
            return match.group("company").strip(), match.group("title").strip()
        return None, header.strip() if header else None

    def _parse_header_lines(
        self, lines: list[str]
    ) -> tuple[
        str | None,
        str | None,
        str | None,
        date | None,
        date | None,
        bool,
        int,
    ]:
        if not lines:
            return None, None, None, None, None, False, 0

        header_window = lines[: min(len(lines), 6)]
        date_idx = None
        start_date = None
        end_date = None
        is_current = False
        for i, line in enumerate(header_window):
            sd, ed, cur = self._parse_dates(line)
            if sd or ed or cur:
                date_idx = i
                start_date, end_date, is_current = sd, ed, cur
                break

        location = None
        for line in header_window:
            location = self._parse_location(line) or location

        body_start = 1
        title: str | None = None
        company: str | None = None

        pre_lines = header_window[:date_idx] if date_idx is not None else header_window[:3]
        pre_lines = [
            ln
            for ln in pre_lines
            if ln
            and not ln.startswith(("-", "•", "*"))
            and not ENVIRONMENT_LINE_RE.match(ln)
            and ln.strip().lower().rstrip(":") not in RESPONSIBILITY_MARKERS
        ]
        post_lines = header_window[(date_idx + 1) : (date_idx + 3)] if date_idx is not None else header_window[1:3]
        post_lines = [
            ln
            for ln in post_lines
            if ln
            and not ln.startswith(("-", "•", "*"))
            and not ENVIRONMENT_LINE_RE.match(ln)
            and ln.strip().lower().rstrip(":") not in RESPONSIBILITY_MARKERS
        ]

        header_line = pre_lines[0] if pre_lines else lines[0]
        date_line = header_window[date_idx] if date_idx is not None else None

        # Prefer extracting org/title from the line that contains the dates.
        if date_line:
            title_from_role = None
            role_match = LABELED_TITLE_RE.search(date_line)
            if role_match:
                title_from_role = (role_match.group("value") or "").strip()

            company_from_date = None
            date_span = DATE_RANGE_RE.search(date_line)
            if date_span:
                prefix_raw = date_line[: date_span.start()]
            else:
                anchor = DATE_ANCHOR_RE.search(date_line)
                prefix_raw = date_line[: anchor.start()] if anchor else ""

            if prefix_raw:
                prefix = prefix_raw.strip().strip(" -–—|,·")
                prefix = re.sub(r"\s+", " ", prefix).strip()
                prefix = prefix.rstrip(":").strip()
                if prefix and not ENVIRONMENT_LINE_RE.match(prefix) and self._looks_like_company(prefix):
                    company_from_date = prefix

            if company_from_date:
                company = company_from_date
                if title_from_role and self._looks_like_title(title_from_role):
                    title = title_from_role
                else:
                    title = None
            else:
                company, fallback_title = self._parse_company_title(self._strip_dates(header_line))
                title = fallback_title

            # If we successfully extracted a labeled role anywhere on the date line, prefer it over
            # any placeholder-ish title produced by generic splitting.
            if title_from_role and self._looks_like_title(title_from_role):
                if not title or PLACEHOLDER_ORG_RE.match(str(title).strip()):
                    title = title_from_role
        else:
            company, fallback_title = self._parse_company_title(self._strip_dates(header_line))
            title = fallback_title

        if pre_lines:
            for candidate in pre_lines:
                c, t = self._split_company_title(candidate)
                if c and not company and self._looks_like_company(c):
                    company = c
                if t and (not title or self._looks_like_title(t)):
                    title = t

            for j, candidate in enumerate(pre_lines):
                if self._parse_location(candidate) and j > 0:
                    prev = pre_lines[j - 1]
                    if self._looks_like_company(prev):
                        company = company or prev

        for candidate in post_lines:
            lowered = candidate.lower().strip(":")
            if lowered in RESPONSIBILITY_MARKERS:
                continue
            if not title and (TITLE_HINT_RE.search(candidate) or candidate.istitle()) and len(candidate.split()) <= 10:
                title = candidate

        if company and ENVIRONMENT_LINE_RE.match(company):
            company = None

        if company and title and self._looks_like_title(company) and not self._looks_like_company(company):
            company = None

        if company and date_idx is not None:
            body_start = max(body_start, date_idx + 1)
        elif len(lines) > 1:
            body_start = 2

        title = self.normalize_job_titles(title)
        company = self.normalize_company_names(company)
        return company, title, location, start_date, end_date, is_current, body_start

    @staticmethod
    def _looks_like_company(text: str) -> bool:
        if not text:
            return False
        cleaned = text.strip()
        if WorkExperienceParser._looks_like_skillish_header(cleaned):
            return False
        if 2 <= len(cleaned) <= 40 and cleaned.isupper() and not TITLE_HINT_RE.search(cleaned):
            return True
        if cleaned.istitle() and len(cleaned.split()) <= 4 and not TITLE_HINT_RE.search(cleaned):
            return True
        if COMPANY_HINT_RE.search(text):
            return True
        return bool(re.search(r",\s*[A-Z]{2}\b", text)) or len(text.split()) >= 2

    @staticmethod
    def _looks_like_title(text: str) -> bool:
        if not text:
            return False
        return bool(TITLE_HINT_RE.search(text)) or len(text.split()) <= 5

    def _parse_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        match = DATE_RANGE_RE.search(text)
        if not match:
            return None, None, False

        start_raw = (match.group("start") or "").strip()
        end_raw = (match.group("end") or "").strip()

        start_date = self._parse_date(start_raw)
        if end_raw.lower() in {"present", "current", "till date", "till  date", "now"}:
            return start_date, None, True
        end_date = self._parse_date(end_raw)
        return start_date, end_date, False

    def _parse_date(self, value: str) -> date | None:
        raw = (value or "").strip()
        if not raw:
            return None
        raw = re.sub(r"\s+", " ", raw)
        raw = raw.replace("’", "'")

        m = re.match(r"^(?P<year>\d{4})-(?P<month>\d{2})(?:-(?P<day>\d{2}))?$", raw)
        if m:
            y = int(m.group("year"))
            mo = int(m.group("month"))
            d = int(m.group("day") or "1")
            try:
                return date(y, mo, d)
            except ValueError:
                return date(y, mo, 1)

        m = re.match(r"^(?P<year>\d{4})[/-](?P<month>\d{1,2})$", raw)
        if m:
            y = int(m.group("year"))
            mo = int(m.group("month"))
            try:
                return date(y, mo, 1)
            except ValueError:
                return None

        m = re.match(r"^(?P<month>\d{1,2})[/-](?P<year>\d{4})$", raw)
        if m:
            y = int(m.group("year"))
            mo = int(m.group("month"))
            try:
                return date(y, mo, 1)
            except ValueError:
                return None

        m = re.match(r"^(?P<month>\d{1,2})[/-](?P<year>\d{2})$", raw)
        if m:
            mo = int(m.group("month"))
            yy = int(m.group("year"))
            y = 2000 + yy if yy <= 49 else 1900 + yy
            try:
                return date(y, mo, 1)
            except ValueError:
                return None

        m = re.match(
            rf"^(?P<mon>{MONTH_TOKEN})\s*[']\s*(?P<year>\d{{2}})$",
            raw,
            flags=re.IGNORECASE,
        )
        if m:
            mon_raw = m.group("mon")
            yy = int(m.group("year"))
            y = 2000 + yy if yy <= 49 else 1900 + yy
            parsed = dateparser.parse(
                f"{mon_raw} {y}",
                settings={
                    "PREFER_DAY_OF_MONTH": "first",
                    "PREFER_DATES_FROM": "past",
                },
            )
            return parsed.date() if parsed else None

        m = re.match(r"^(?P<year>\d{4})$", raw)
        if m:
            return date(int(m.group("year")), 1, 1)

        parsed = dateparser.parse(
            raw,
            settings={
                "PREFER_DAY_OF_MONTH": "first",
                "PREFER_DATES_FROM": "past",
            },
        )
        return parsed.date() if parsed else None

    @staticmethod
    def _strip_dates(text: str) -> str:
        return DATE_RANGE_RE.sub("", text).strip(" -–—,|·")

    def _split_company_title(self, line: str) -> tuple[str | None, str | None]:
        cleaned = line.strip()
        if not cleaned:
            return None, None
        cleaned = cleaned.replace("·", "|")
        if "|" in cleaned:
            parts = [p.strip() for p in cleaned.split("|") if p.strip()]
            if len(parts) >= 2:
                left, right = parts[0], parts[1]
                right_l = right.lower().strip(":")
                left_l = left.lower()
                if PLACEHOLDER_ORG_RE.match(right_l) or right_l in {"role", "client"}:
                    if "," in left or "/" in left or (left_l and not TITLE_HINT_RE.search(left)):
                        return None, None
                    return None, None
                return left, right
        match = COMPANY_LINE_RE.search(cleaned)
        if match:
            company = match.group("company").strip()
            title = match.group("title").strip()
            title_l = title.lower().strip(":")
            if title_l in {"company", "role", "title", "designation", "client"}:
                if PLACEHOLDER_ORG_RE.match(title_l):
                    return company, None
                if "," in company or "/" in company or (company.lower() and not TITLE_HINT_RE.search(company)):
                    return None, None
            return company, title
        return None, None

    @staticmethod
    def _client_looks_embedded_in_company(company: str, client: str) -> bool:
        company_l = company.lower()
        client_l = client.lower()
        return client_l in company_l and len(client_l) >= 4

    @staticmethod
    def _remove_embedded_client(company: str, client: str) -> str:
        cleaned = re.sub(re.escape(client), "", company, flags=re.IGNORECASE).strip(" -–—|,:")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _parse_location(self, text: str) -> str | None:
        match = LOCATION_RE.search(text)
        return match.group(1).strip() if match else None

    def _extract_bullets(self, lines: list[str]) -> list[str]:
        bullets = []
        for line in lines:
            if line.startswith(("-", "•", "*", "")):
                bullets.append(line.lstrip("-•* ").strip())
        return bullets

    def _extract_client(self, text: str) -> str | None:
        lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
        if not lines:
            return None

        for i, line in enumerate(lines[:8]):
            for pattern in CLIENT_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                raw = (match.group("client") or "").strip().strip("-–—| ")
                raw = re.split(r"\s{2,}|\||\u2022", raw)[0].strip()

                date_anchor = DATE_ANCHOR_RE.search(raw)
                if date_anchor:
                    raw = raw[: date_anchor.start()].strip().strip(" -–—|,:")
                raw = DATE_RANGE_RE.sub("", raw).strip(" -–—|,:")

                loc_match = LOCATION_RE.search(raw)
                if loc_match:
                    raw = raw.replace(loc_match.group(1), "").strip(" -–—|,:")
                    raw = re.sub(r"\s+", " ", raw).strip()

                if not raw:
                    continue
                if len(raw) > 120:
                    continue
                return raw
        return None

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
        self,
        company: str | None,
        title: str | None,
        start_date: date | None,
        end_date: date | None,
        is_current: bool,
        client: str | None,
        bullets: list[str] | None,
    ) -> float:
        score = 0.0
        if company:
            score += 0.28
        if title:
            score += 0.22
        if start_date:
            score += 0.28
        if end_date or is_current:
            score += 0.12
        if client:
            score += 0.05
        if bullets and len(bullets) >= 2:
            score += 0.05
        return min(score, 1.0)

    def _parse_labeled_fields(self, lines: list[str]) -> tuple[str | None, str | None, list[str]]:
        company: str | None = None
        title: str | None = None
        responsibilities: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            match = LABELED_ORG_RE.search(line)
            if match:
                candidate = match.group("value").strip().strip("-–— ")
                if candidate:
                    company = candidate
                i += 1
                continue

            match = LABELED_TITLE_RE.search(line)
            if match:
                candidate = match.group("value").strip().strip("-–— ")
                if candidate:
                    title = candidate
                i += 1
                continue

            match = LABELED_RESP_RE.search(line)
            if match:
                first = (match.group("value") or "").strip().strip("-–— ")
                if first:
                    responsibilities.append(first)
                i += 1
                while i < len(lines):
                    nxt = lines[i].strip()
                    if not nxt:
                        i += 1
                        continue
                    if LABELED_ORG_RE.search(nxt) or LABELED_TITLE_RE.search(nxt):
                        break
                    responsibilities.append(nxt.lstrip("-•* ").strip())
                    i += 1
                continue

            lowered = line.lower().strip(":-–— ")
            if lowered in {"organization", "company", "employer"} and i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if nxt.startswith(("-", "–", "—")):
                    company = nxt.lstrip("-–— ").strip() or company
                    i += 2
                    continue
            if lowered in {"designation", "title", "role", "position"} and i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if nxt.startswith(("-", "–", "—")):
                    title = nxt.lstrip("-–— ").strip() or title
                    i += 2
                    continue

            i += 1

        title = self.normalize_job_titles(title)
        company = self.normalize_company_names(company)
        return company, title, responsibilities

    def _llm_fallback(self, chunk: str) -> JobEntry | None:
        mode = (self.settings.PARSING_MODE or "").lower()
        if self.settings.LLM_PROVIDER == "none" or mode != "full":
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
            designation=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
        )

    def _call_llm(self, prompt: str) -> str | None:
        return self.llm._call_llm(prompt, task="work_experience").content
