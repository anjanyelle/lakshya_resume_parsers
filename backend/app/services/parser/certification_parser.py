from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date

import dateparser

from app.data.taxonomy.certifications_top import CERTIFICATION_ALIASES, KNOWN_CERT_KEYWORDS

logger = logging.getLogger(__name__)


DATE_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
ISSUE_RE = re.compile(r"(issued|issue date)\s*[:\-]?\s*(.+)", re.IGNORECASE)
EXPIRY_RE = re.compile(r"(expires|expiry|valid until)\s*[:\-]?\s*(.+)", re.IGNORECASE)
CREDENTIAL_RE = re.compile(r"(credential id|license id|cert id)\s*[:\-]?\s*(\w+)", re.IGNORECASE)


@dataclass(frozen=True)
class CertificationEntry:
    name: str
    issuing_organization: str | None
    issue_date: date | None
    expiry_date: date | None
    credential_id: str | None
    is_active: bool | None
    confidence: float


class CertificationParser:
    def parse(self, text: str) -> list[CertificationEntry]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        entries: list[CertificationEntry] = []
        for line in lines:
            entry = self._parse_line(line)
            if entry:
                entries.append(entry)
        return entries

    def _parse_line(self, line: str) -> CertificationEntry | None:
        name = self._extract_name(line)
        if not name:
            return None
        issue_date = self._extract_date(line, ISSUE_RE)
        expiry_date = self._extract_date(line, EXPIRY_RE)
        credential_id = self._extract_credential_id(line)
        org = self._extract_org(line, name)
        is_active = None
        if expiry_date:
            is_active = expiry_date >= date.today()
        confidence = self._score_confidence(name, org, issue_date)

        return CertificationEntry(
            name=name,
            issuing_organization=org,
            issue_date=issue_date,
            expiry_date=expiry_date,
            credential_id=credential_id,
            is_active=is_active,
            confidence=confidence,
        )

    def _extract_name(self, line: str) -> str | None:
        lowered = line.lower()
        for alias, canonical in CERTIFICATION_ALIASES.items():
            if alias in lowered:
                return canonical
        if any(keyword in lowered for keyword in KNOWN_CERT_KEYWORDS):
            return line
        return None

    def _extract_date(self, line: str, pattern: re.Pattern[str]) -> date | None:
        match = pattern.search(line)
        if match:
            return self._parse_date(match.group(2))
        years = DATE_RE.findall(line)
        if years:
            return date(int(years[-1]), 1, 1)
        return None

    def _parse_date(self, value: str) -> date | None:
        parsed = dateparser.parse(value, settings={"PREFER_DAY_OF_MONTH": "first"})
        return parsed.date() if parsed else None

    def _extract_credential_id(self, line: str) -> str | None:
        match = CREDENTIAL_RE.search(line)
        return match.group(2) if match else None

    def _extract_org(self, line: str, name: str) -> str | None:
        lowered = line.lower()
        if "aws" in lowered:
            return "Amazon Web Services"
        if "azure" in lowered:
            return "Microsoft"
        if "google" in lowered:
            return "Google"
        if "pmp" in lowered:
            return "PMI"
        if name and name in line:
            return None
        return None

    def _score_confidence(
        self, name: str | None, org: str | None, issue_date: date | None
    ) -> float:
        score = 0.0
        if name:
            score += 0.6
        if org:
            score += 0.2
        if issue_date:
            score += 0.2
        return min(score, 1.0)
