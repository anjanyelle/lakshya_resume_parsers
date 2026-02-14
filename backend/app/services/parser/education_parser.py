from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date

import dateparser

from app.data.taxonomy.degree_taxonomy import DEGREE_ALIASES, DEGREE_KEYWORDS
from app.data.taxonomy.universities_top import TOP_UNIVERSITIES

logger = logging.getLogger(__name__)


DATE_RANGE_RE = re.compile(
    r"(?P<start>[\w./\- ]{3,20})\s*(?:[-–—]|to)\s*(?P<end>present|current|expected|[\w./\- ]{3,20})",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
GPA_RE = re.compile(
    r"\b(?P<gpa>\d(?:\.\d{1,2})?)\s*(?:/|of)\s*(?P<scale>\d(?:\.\d)?)\b|\b(?P<pct>\d{2,3})%\b",
    re.IGNORECASE,
)
HONORS_RE = re.compile(
    r"\b(cum laude|magna cum laude|summa cum laude|dean'?s list|honors|distinction)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EducationEntry:
    institution: str | None
    degree: str | None
    field_of_study: str | None
    start_date: date | None
    end_date: date | None
    gpa: str | None
    honors: str | None
    in_progress: bool
    confidence: float


class EducationParser:
    def parse(self, text: str) -> list[EducationEntry]:
        blocks = self._split_blocks(text)
        entries: list[EducationEntry] = []
        for block in blocks:
            entry = self._parse_block(block)
            if entry:
                entries.append(entry)
        return entries

    def _split_blocks(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        blocks: list[str] = []
        current: list[str] = []
        for line in lines:
            if YEAR_RE.search(line) and current:
                blocks.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append("\n".join(current))
        return blocks or [text]

    def _parse_block(self, block: str) -> EducationEntry | None:
        institution = self._extract_institution(block)
        degree = self._extract_degree(block)
        field = self._extract_field(block)
        start, end, in_progress = self._extract_dates(block)
        gpa = self._extract_gpa(block)
        honors = self._extract_honors(block)
        confidence = self._score_confidence(institution, degree, end or start)

        if not any([institution, degree, field, gpa, honors, start, end]):
            return None

        return EducationEntry(
            institution=institution,
            degree=degree,
            field_of_study=field,
            start_date=start,
            end_date=end,
            gpa=gpa,
            honors=honors,
            in_progress=in_progress,
            confidence=confidence,
        )

    def _extract_institution(self, text: str) -> str | None:
        lines = text.splitlines()
        for line in lines:
            lowered = line.lower()
            if lowered in TOP_UNIVERSITIES:
                return line.strip()
            if any(keyword in lowered for keyword in ["university", "college", "institute", "school", "bootcamp"]):
                return line.strip()
        return None

    def _extract_degree(self, text: str) -> str | None:
        lowered = text.lower()
        for abbr, full in DEGREE_ALIASES.items():
            if re.search(rf"\b{re.escape(abbr)}\b", lowered):
                return full
        for keyword in DEGREE_KEYWORDS:
            if keyword in lowered:
                return keyword.title()
        return None

    def _extract_field(self, text: str) -> str | None:
        match = re.search(r"(?:in|of)\s+([A-Za-z &/]+)", text, re.IGNORECASE)
        if match:
            field = match.group(1).strip()
            if len(field.split()) <= 6:
                return field
        return None

    def _extract_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        match = DATE_RANGE_RE.search(text)
        in_progress = False
        if match:
            start_raw = match.group("start")
            end_raw = match.group("end")
            start_date = self._parse_date(start_raw)
            if end_raw.lower() in {"present", "current", "expected"}:
                in_progress = True
                return start_date, None, True
            end_date = self._parse_date(end_raw)
            return start_date, end_date, False

        years = YEAR_RE.findall(text)
        if years:
            end_year = int(years[-1])
            return None, date(end_year, 1, 1), False
        return None, None, False

    def _parse_date(self, value: str) -> date | None:
        parsed = dateparser.parse(value, settings={"PREFER_DAY_OF_MONTH": "first"})
        return parsed.date() if parsed else None

    def _extract_gpa(self, text: str) -> str | None:
        match = GPA_RE.search(text)
        if not match:
            return None
        if match.group("gpa") and match.group("scale"):
            return f"{match.group('gpa')}/{match.group('scale')}"
        if match.group("pct"):
            return f"{match.group('pct')}%"
        return None

    def _extract_honors(self, text: str) -> str | None:
        match = HONORS_RE.search(text)
        return match.group(1).title() if match else None

    def _score_confidence(
        self, institution: str | None, degree: str | None, date_value: date | None
    ) -> float:
        score = 0.0
        if institution:
            score += 0.4
        if degree:
            score += 0.3
        if date_value:
            score += 0.3
        return min(score, 1.0)
