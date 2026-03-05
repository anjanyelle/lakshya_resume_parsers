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
    # Core words
    "certified",
    "certification",
    "certifications",
    "certificate",
    "certificates",
    "licensed",
    "license",
    "licence",
    "credential",
    "credentials",
    "professional designation",
    "board certified",

    # Validity related
    "expires",
    "expiry",
    "valid until",
    "valid through",
    "issued",
    "issued on",
    "date of issue",
    "credential id",
    "license number",
    "registration number",

    # Abbreviations
    "cert.",
    "lic.",
    "reg.",

    # Professional common phrases
    "accredited",
    "chartered",
    "authorized",
    "recognized by",
    "member of",

    # Exam based
    "exam passed",
    "qualified",
    "qualified in",
    "cleared",
    "passed",

    # Government / Medical / Legal
    "state licensed",
    "nationally certified",
    "federally certified",
    "board eligible",

    # Tech cert keywords (high signal)
    "aws certified",
    "microsoft certified",
    "oracle certified",
    "google certified",
    "pmp",
    "csm",
    "cspo",
    "itil",
    "ccna",
    "ccnp",
    "cissp",
    "ceh",
    "scrum master",
    
    # Testing certifications
    "istqb",
    "test analyst",
    "advanced level",
    "foundation level",
    "certified tester",
    "cste",
    "cstae",
    "cmst",
    "test manager",
)

TRAINING_FALSE_POSITIVES = (
    "training",
    "workshop",
    "bootcamp",
    "seminar",
    "course",
    "courses",
    "online course",
    "short course",
    "module",
    "program",
    "orientation",
    "induction",
    "internship training",
    "industrial training",

    # Learning platforms
    "coursera",
    "udemy",
    "edx",
    "udacity",
    "simplilearn",
    "great learning",
    "linkedin learning",
    "pluralsight",
    "skillshare",

    # Participation-only
    "certificate of attendance",
    "certificate of participation",
    "participated in",
    "attended",
    "completion of workshop",
    "seminar participation",
    "webinar",
    "masterclass",

    # Academic signals
    "bachelor",
    "master",
    "degree",
    "diploma",
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
            r"\b(?:certified|certification|certificate|certificates|license|licence|credentials?|aws|azure|google\s+cloud|gcp|scrum|pmp|project\s+management\s+professional|istqb|test\s+analyst|advanced\s+level|foundation\s+level|certified\s+tester)\b",
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
            
            # Don't split on dashes within certification names - only split on clear separators
            # line = re.sub(r"\s*[–—]\s*(?=[A-Z])", "\n", line)
            #Remove bullets / dashes from beginning
            line = re.sub(r"^[\-\*•\u2022\–\—]+\s*", "", line)
            #Normalize spacing (VERY IMPORTANT for PDF)
            # Don't replace dashes with spaces - they're part of certification names
            # line = re.sub(r"\s*-\s*", " - ", line)
            line = re.sub(r"\s*:\s*", ": ", line)
            line = re.sub(r"\s+", " ", line).strip()

            if not line:
                continue
            # Split comma-separated certifications
            # (Sir originally split only by bullet/pipe)
            candidates = self._split_candidate_lines(line)

            for candidate in candidates:

                if not candidate:
                    continue

                # Skip skill lists accidentally inside section
                if self._looks_like_skill_list(candidate):
                    continue

                # Skip section labels accidentally captured
                if self._looks_like_section_label(candidate):
                    continue

                entry = self._parse_line(candidate)
                if entry:
                    entries.append(entry)

        return entries

    @staticmethod
    def _split_candidate_lines(line: str) -> list[str]:
        """
        Enterprise-level multi-cert splitter.
        Handles:
        - Bullet lists
        - Dash-separated certs
        - Colon-based prefixes
        - Inline chained certs
       """

        if not line:
           return []

    # Normalize whitespace
        normalized = re.sub(r"\s+", " ", line).strip()

    # Remove leading bullets
        normalized = re.sub(r"^[\-\*•\u2022]+\s*", "", normalized)

        if not normalized: 
            return []

    # --------------------------------------------------
    # 1️⃣ Split when dash is followed by CAPITAL letter
    # Example:
    #   ASCM – LSSBB: Lean Six Sigma
    # DISABLED: This breaks certification names like "PMP: Project Management Professional- Project Management Institute"
    # normalized = re.sub(r"\s*[-–—]\s*(?=[A-Z])", "\n", normalized)

    # --------------------------------------------------
    # 2️⃣ Split when new cert starts after colon prefix
    # Example:
    #   PMP: Project Management Professional LSSBB: Lean Six Sigma
    # --------------------------------------------------
        normalized = re.sub(
        r"(?<=\))\s+(?=[A-Z]{2,}[:\-])",
        "\n",
        normalized,
    )

    # --------------------------------------------------
    # 3️⃣ Split on bullet or newline
    # --------------------------------------------------
        parts = re.split(r"\s*(?:•|\n|\|)\s*", normalized)

        final_parts: list[str] = []

        for part in parts:
            if not part:
                continue

            part = part.strip()

        # --------------------------------------------------
        # 4️⃣ Split chained colon prefixes
        # Example:
        #   PMP: Project Management Professional – PMI – LSSBB: ...
        # --------------------------------------------------
            sub_parts = re.split(r"\s+(?=[A-Z]{2,}:\s)", part)

            for sub in sub_parts:
                sub = sub.strip()
            if sub:
                final_parts.append(sub)

    # Final clean
        cleaned = [p.strip() for p in final_parts if p.strip()]
        return cleaned



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


    def _safe_split_camel_case(self, text: str) -> str:
       if not text:
           return text

    # Split lowercase → Uppercase
       text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

    # Split digit → Uppercase (TOGAF9.2Certified)
       text = re.sub(r'(?<=\d)(?=[A-Z])', ' ', text)

       return text.strip()

    def _parse_line(self, line: str) -> CertificationEntry | None:
        
        line = self._safe_split_camel_case(line)
        line = re.sub(r"\s+", " ", line).strip()
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
        
        cleaned = line.strip()
        lowered = cleaned.lower()

        #Reject obvious section labels / skill lines
        if self._looks_like_section_label(line):
            return None

        
        if self._looks_like_skill_list(line):
            return None
         # Reject experience bullets (action verbs)
        verb_check = re.sub(r"^[^A-Za-z0-9]+", "", lowered)
        if ACTION_VERB_RE.search(verb_check) and not EXAM_CODE_RE.search(cleaned):
            return None
        

        #  Exam codes (AZ-104, SAA-C03, etc.)
        if EXAM_CODE_RE.search(cleaned):
            return cleaned
        
        # B) Strong certification markers
        if any(marker in lowered for marker in CERT_LINE_MARKERS):
            return cleaned

        # Alias Match (High Confidence)
        for alias in CERTIFICATION_ALIASES:
            if alias in lowered:
                return cleaned

        # Known Certification Keywords (AWS, ISTQB, PMP etc.)
        keyword_hits = sum(
            1 for keyword in KNOWN_CERT_KEYWORDS
            if keyword in lowered
        )

        if keyword_hits >= 1:
            if 2 <= len(cleaned.split()) <= 12 and len(cleaned) <= 150:
                return cleaned

    #Short Abbreviation Certifications (CKA, CSM, PMP etc.)
        COMMON_SHORT_CERTS = {
        "cka", "ckad", "cks", "csm",
        "pmp", "cissp", "cism", "cisa",
        "rhce", "rhcsa", "ccna", "ccnp",
        "oscp", "ceh", "gicsp", "grid",
        "cssa", "lssbb"
        }

        if lowered in COMMON_SHORT_CERTS:
            return cleaned

    
    # Controlled Fallback (Enterprise Guardrail)
        token_count = len(cleaned.split())

        if (
            3 <= token_count <= 10
            and len(cleaned) <= 120
            and not ACTION_VERB_RE.search(lowered)
        ):
            return cleaned

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