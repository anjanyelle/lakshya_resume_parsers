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

# =========================
#  🆕 ADDED FROM YOUR LOGIC
#  Detect certification exam codes like AZ-104, SAA-C03, AZ-400
# =========================
EXAM_CODE_RE = re.compile(r"\b[A-Z]{2,}-\d{2,}\b")

ACTION_VERB_RE = re.compile(
    r"^\s*(managed|developed|deployed|designed|implemented|configured|monitored|supported|created|built|led|optimized|performed|established|executed|administered|guided|troubleshot|provided|maintained|orchestrated|streamlined|architected|enhanced|applied)\b",
    re.IGNORECASE,
)


CERT_LINE_MARKERS = (
    "certified",
    "certification",
    "certificate",
    "license",
    "licence",
    "credential",
    "credentials",
    "professional designation",
    "board certified",
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

    @classmethod
    def extract_candidate_lines_from_full_text(cls, text: str) -> list[str]:
        lines = [ln.strip() for ln in (text or "").splitlines()]
        if not lines:
            return []

        keyword_re = re.compile(
            r"\b(?:certified|certification|certificate|certificates|license|licence|credentials?|aws|azure|google\s+cloud|gcp|scrum|pmp|project\s+management\s+professional)\b",
            re.IGNORECASE,
        )

        out: list[str] = []
        seen: set[str] = set()

        for line in lines:
            if not line:
                continue

            normalized = re.sub(r"\s+", " ", line).strip()
            if not normalized:
                continue

            stripped = re.sub(r"^[\-\*•\u2022]+\s*", "", normalized).strip()
            if not stripped:
                continue

            lowered = stripped.lower()

            if re.match(r"^(skills?|technical\s+skills?)\s*[:\-–—]", lowered):
                continue

            labeled_cert = bool(
                re.match(
                    r"^(certifications?|certification|licenses?|licence|credentials?)\s*[:\-–—]",
                    lowered,
                )
            )
            has_strong_marker = labeled_cert or any(
                marker in lowered for marker in CERT_LINE_MARKERS
            )
            has_exam_code = bool(EXAM_CODE_RE.search(stripped))

            if cls._looks_like_section_label(stripped):
                continue
            if not (has_strong_marker or has_exam_code) and cls._looks_like_skill_list(stripped):
                continue

            if not (keyword_re.search(stripped) or EXAM_CODE_RE.search(stripped)):
                continue

            if stripped.endswith(".") and not (has_strong_marker or has_exam_code):
                continue

            if len(stripped.split()) > 24 and not (has_strong_marker or has_exam_code):
                continue

            if len(stripped) > 220:
                continue

            if any(token in lowered for token in TRAINING_FALSE_POSITIVES) and not any(
                marker in lowered for marker in CERT_LINE_MARKERS
            ):
                continue

            if stripped not in seen:
                out.append(stripped)
                seen.add(stripped)
            if len(out) >= 60:
                break

        return out

    def parse(self, text: str) -> list[CertificationEntry]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        entries: list[CertificationEntry] = []

        for line in lines:
            # =========================
            # 🆕 FROM YOUR LOGIC:
            # Split comma-separated certifications
            # (Sir originally split only by bullet/pipe)
            # =========================
            candidates = self._split_candidate_lines(line)

            for candidate in candidates:
                entry = self._parse_line(candidate)
                if entry:
                    entries.append(entry)

        return entries

    @staticmethod
    def _split_candidate_lines(line: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", (line or "")).strip()
        if not normalized:
            return []

        normalized = re.sub(r"^[\-\*•\u2022]+\s*", "", normalized).strip()
        if not normalized:
            return []

        # 🆕 Added comma splitting (your improvement)
        parts = re.split(r"\s*[•|,]\s*", normalized)
        cleaned = [p.strip() for p in parts if p.strip()]
        return cleaned or [normalized]

    @staticmethod
    def _looks_like_skill_list(line: str) -> bool:
        lowered = (line or "").lower().strip()
        if not lowered:
            return False

        # Sir's protection logic (kept unchanged)
        if ":" in lowered and re.search(
            r"\b(languages|frontend|backend|tools|testing|frameworks|databases|cloud|devops|apis|platforms)\b",
            lowered,
        ):
            return True

        if line.count(",") >= 4 and len(line) <= 140:
            return True

        return False

    @staticmethod
    def _looks_like_section_label(line: str) -> bool:
        lowered = (line or "").lower().strip().strip(":")
        if not lowered:
            return False

        if lowered in {
            "certifications",
            "certification",
            "licenses",
            "skills",
            "technical skills",
            "technologies",
            "tools",
            "education",
            "experience",
            "work experience",
        }:
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

        if self._looks_like_section_label(line):
            return None

        if self._looks_like_skill_list(line):
            return None

        verb_check = re.sub(r"^[^A-Za-z0-9]+", "", lowered)
        has_cert_marker = any(marker in lowered for marker in CERT_LINE_MARKERS)
        if ACTION_VERB_RE.search(verb_check) and not (has_cert_marker or EXAM_CODE_RE.search(line)):
            return None

        # Alias mapping (sir logic retained)
        for alias, canonical in CERTIFICATION_ALIASES.items():
            if alias in lowered:
                return canonical

        token_count = len(line.split())
        if token_count <= 2:
            return None

        looks_like_training = any(token in lowered for token in TRAINING_FALSE_POSITIVES)

        if looks_like_training and not has_cert_marker:
            return None

        # =========================
        # 🆕 FROM YOUR LOGIC:
        # Allow detection via exam code (AZ-104 style)
        # =========================
        if has_cert_marker or EXAM_CODE_RE.search(line):
            return line.strip()

        keyword_hits = sum(1 for keyword in KNOWN_CERT_KEYWORDS if keyword in lowered)
        if keyword_hits >= 1 and token_count >= 3 and len(line) <= 120:
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
            return match.group("org").strip()

        if "aws" in lowered:
            return "Amazon Web Services"
        if "azure" in lowered or "microsoft" in lowered:
            return "Microsoft"
        if "google" in lowered or "gcp" in lowered:
            return "Google"
        if "oracle" in lowered:
            return "Oracle"
        if "pmp" in lowered or "pmi" in lowered:
            return "PMI"

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
