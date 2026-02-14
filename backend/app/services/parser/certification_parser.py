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
ISSUED_BY_RE = re.compile(
    r"\b(?:issued\s+by|issuer|issuing\s+authority|certified\s+by)\b\s*[:\-–—]?\s*(?P<org>.+)$",
    re.IGNORECASE,
)
EXPIRY_RE = re.compile(r"(expires|expiry|valid until)\s*[:\-]?\s*(.+)", re.IGNORECASE)
CREDENTIAL_RE = re.compile(r"(credential id|license id|cert id)\s*[:\-]?\s*(\w+)", re.IGNORECASE)

CERT_LINE_MARKERS = (
    "certified",
    "certification",
    "certificate",
    "license",
    "licence",
    "issued by",
    "accredited",
    "accreditation",
    "credential",
    "credentials",
    "qualified",
    "registration",
    "registered",
    "authorized",
    "authorised",
    "approved by",
    "endorsed by",
    "chartered",
    "diploma",
    "awarded by",
    "granted by",
    "conferred by",
    "board certified",
    "professional designation",
    "competency",
    "attested",
    "valid through",
    "expires",
    "expiry",
)
TRAINING_FALSE_POSITIVES = (
    "training",
    "workshop",
    "bootcamp",
    "seminar",
    "course",
    "coursera",
    "udemy",
    "edx",
    "webinar",
    "masterclass",
    "tutorial",
    "lesson",
    "class",
    "session",
    "program",
    "learning path",
    "online course",
    "mooc",
    "linkedin learning",
    "pluralsight",
    "skillshare",
    "khan academy",
    "codecademy",
    "datacamp",
    "udacity",
    "attended",
    "participated",
    "completed training",
    "training program",
    "educational program",
    "professional development",
    "continuing education",
    "workshop series",
    "certificate of completion",
    "certificate of attendance",
    "certificate of participation",
)


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
            for candidate in self._split_candidate_lines(line):
                entry = self._parse_line(candidate)
                if entry:
                    entries.append(entry)
        return entries

    def parse_with_fallback(self, text: str, extra_texts: list[str] | None = None) -> list[CertificationEntry]:
        entries = self.parse(text)
        if entries:
            return entries

        candidates: list[str] = []
        for source in [text, *(extra_texts or [])]:
            if not source:
                continue
            for line in (line.strip() for line in source.splitlines() if line.strip()):
                if self._is_cert_candidate_line(line):
                    candidates.append(line)

        seen: set[tuple[str, str | None]] = set()
        recovered: list[CertificationEntry] = []
        for line in candidates:
            entry = self._parse_line(line)
            if not entry:
                continue
            key = (entry.name.strip().lower(), (entry.issuing_organization or "").strip().lower() or None)
            if key in seen:
                continue
            seen.add(key)
            recovered.append(entry)
        return recovered

    @staticmethod
    def _split_candidate_lines(line: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", (line or "")).strip()
        if not normalized:
            return []
        parts = re.split(r"\s*[•|]\s*", normalized)
        cleaned = [p.strip() for p in parts if p.strip()]
        return cleaned or [normalized]

    def _is_cert_candidate_line(self, line: str) -> bool:
        lowered = line.lower().strip()
        if not lowered:
            return False
        if len(line) > 200:
            return False
        if len(line.split()) > 20:
            return False

        if any(marker in lowered for marker in CERT_LINE_MARKERS):
            return True

        for alias in CERTIFICATION_ALIASES.keys():
            if alias in lowered:
                return True

        if any(keyword in lowered for keyword in KNOWN_CERT_KEYWORDS):
            return True

        return False

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
        lowered = line.lower().strip()
        if not lowered:
            return None

        for alias, canonical in CERTIFICATION_ALIASES.items():
            if alias in lowered:
                return canonical

        if len(line) > 200:
            return None
        if len(line.split()) > 20:
            return None

        has_cert_marker = any(marker in lowered for marker in CERT_LINE_MARKERS) or (
            "cert " in lowered or "cert." in lowered
        )

        looks_like_training = any(token in lowered for token in TRAINING_FALSE_POSITIVES)
        if looks_like_training and not has_cert_marker:
            return None

        if has_cert_marker:
            return line.strip()

        if any(keyword in lowered for keyword in KNOWN_CERT_KEYWORDS):
            return line.strip()

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
        match = ISSUED_BY_RE.search(line)
        if match:
            candidate = str(match.group("org") or "").strip().strip("-–—|, ")
            candidate = re.split(r"\s{2,}|\||•", candidate)[0].strip()
            provider = self._normalize_provider(candidate)
            return provider or candidate or None

        if "aws" in lowered:
            return "Amazon Web Services"
        if "amazon web services" in lowered:
            return "Amazon Web Services"
        if "azure" in lowered:
            return "Microsoft"
        if "microsoft" in lowered:
            return "Microsoft"
        if "google" in lowered:
            return "Google"
        if "gcp" in lowered:
            return "Google"
        if "pmp" in lowered:
            return "PMI"
        if "pmi" in lowered:
            return "PMI"
        if "oracle" in lowered:
            return "Oracle"
        if name and name in line:
            return None
        return None

    @staticmethod
    def _normalize_provider(value: str) -> str | None:
        lowered = (value or "").lower().strip()
        if not lowered:
            return None
        if "aws" in lowered or "amazon web services" in lowered:
            return "Amazon Web Services"
        if "microsoft" in lowered or "azure" in lowered:
            return "Microsoft"
        if "google" in lowered or "gcp" in lowered:
            return "Google"
        if "pmi" in lowered or "pmp" in lowered:
            return "PMI"
        if "oracle" in lowered:
            return "Oracle"
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
