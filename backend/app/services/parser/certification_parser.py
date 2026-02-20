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

    def parse(self, text: str) -> list[CertificationEntry]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        entries: list[CertificationEntry] = []

        for line in lines:
            
            #Remove bullets / dashes from beginning
            line = re.sub(r"^[\-\*•\u2022\–\—]+\s*", "", line)
            #Normalize spacing (VERY IMPORTANT for PDF)
            line = re.sub(r"\s*-\s*", " - ", line)
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

    # @staticmethod
    # def _split_candidate_lines(line: str) -> list[str]:
    #     """
    #     Enterprise-level multi-cert splitter.
    #     Handles:
    #     - Bullet lists
    #     - Dash-separated certs
    #     - Colon-based prefixes
    #     - Inline chained certs
    #    """

    #     if not line:
    #        return []

    # # Normalize whitespace
    #     normalized = re.sub(r"\s+", " ", line).strip()

    # # Remove leading bullets
    #     normalized = re.sub(r"^[\-\*•\u2022]+\s*", "", normalized)

    #     if not normalized:
    #         return []


    # # --------------------------------------------------
    # # 2️⃣ Split when new cert starts after colon prefix
    # # Example:
    # #   PMP: Project Management Professional LSSBB: Lean Six Sigma
    # # --------------------------------------------------
    #     normalized = re.sub(
    #     r"(?<=\))\s+(?=[A-Z]{2,}[:\-])",
    #     "\n",
    #     normalized,
    # )

    # # --------------------------------------------------
    # # 3️⃣ Split on bullet or newline
    # # --------------------------------------------------
    #     parts = re.split(r"\s*(?:•|\n|\|)\s*", normalized)

    #     final_parts: list[str] = []

    #     for part in parts:
    #         if not part:
    #             continue

    #         part = part.strip()

    #     # --------------------------------------------------
    #     # 4️⃣ Split chained colon prefixes
    #     # Example:
    #     #   PMP: Project Management Professional – PMI – LSSBB: ...
    #     # --------------------------------------------------
    #         sub_parts = re.split(r"\s+(?=[A-Z]{2,}:\s)", part)

    #         for sub in sub_parts:
    #             sub = sub.strip()
    #             if sub:
    #                 final_parts.append(sub)

    # # Final clean
    #     cleaned = [p.strip() for p in final_parts if p.strip()]
    #     return cleaned

    @staticmethod
    def _split_candidate_lines(line: str) -> list[str]:
        if not line:
            return []

        normalized = re.sub(r"\s+", " ", line).strip()
        normalized = re.sub(r"^[\-\*•\u2022]+\s*", "", normalized)

        if not normalized:
            return []

    # Only split on bullet or newline (NOT dash)
        parts = re.split(r"\s*(?:•|\n)\s*", normalized)

        final_parts: list[str] = []

        for part in parts:
            if not part:
                continue

        # Split only first pipe — rest treated as metadata
            main = part.split("|")[0].strip()

            if main:
                final_parts.append(main)

        return final_parts

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

    # def _extract_name(self, line: str) -> str | None:
    #     lowered = line.lower().strip()
    #     if not lowered:
    #         return None
        
    #     cleaned = line.strip()
    #     lowered = cleaned.lower()

    #     #Reject obvious section labels / skill lines
    #     if self._looks_like_section_label(line):
    #         return None

        
    #     if self._looks_like_skill_list(line):
    #         return None
    #      # Reject experience bullets (action verbs)
    #     verb_check = re.sub(r"^[^A-Za-z0-9]+", "", lowered)
    #     if ACTION_VERB_RE.search(verb_check) and not EXAM_CODE_RE.search(cleaned):
    #         return None
        

    #     #  Exam codes (AZ-104, SAA-C03, etc.)
    #     if EXAM_CODE_RE.search(cleaned):
    #         return cleaned
        
    #     # B) Strong certification markers
    #     if any(marker in lowered for marker in CERT_LINE_MARKERS):
    #         return cleaned

    #     # Alias Match (High Confidence)
    #     for alias in CERTIFICATION_ALIASES:
    #         if alias in lowered:
    #             return cleaned

    #     # Known Certification Keywords (AWS, ISTQB, PMP etc.)
    #     keyword_hits = sum(
    #         1 for keyword in KNOWN_CERT_KEYWORDS
    #         if keyword in lowered
    #     )

    #     if keyword_hits >= 1:
    #         if 2 <= len(cleaned.split()) <= 12 and len(cleaned) <= 150:
    #             return cleaned

    # #Short Abbreviation Certifications (CKA, CSM, PMP etc.)
    #     COMMON_SHORT_CERTS = {
    #     "cka", "ckad", "cks", "csm",
    #     "pmp", "cissp", "cism", "cisa",
    #     "rhce", "rhcsa", "ccna", "ccnp",
    #     "oscp", "ceh", "gicsp", "grid",
    #     "cssa", "lssbb"
    #     }

    #     if lowered in COMMON_SHORT_CERTS:
    #         return cleaned

    
    # # Controlled Fallback (Enterprise Guardrail)
    #     token_count = len(cleaned.split())

    #     if (
    #         3 <= token_count <= 10
    #         and len(cleaned) <= 120
    #         and not ACTION_VERB_RE.search(lowered)
    #     ):
    #         return cleaned

    #     return None

    def _extract_name(self, line: str) -> str | None:
        if not line:
            return None

        cleaned = line.strip()
        lowered = cleaned.lower()
        token_count = len(cleaned.split())

    # -------------------------------------------------
    # 1️⃣ Reject obvious section labels / skill lists
    # -------------------------------------------------
        if self._looks_like_section_label(cleaned):
            return None

        if self._looks_like_skill_list(cleaned):
            return None
        
        if any(word in lowered for word in TRAINING_FALSE_POSITIVES):
            return None

        if re.search(r"\b(valid through|valid until|license|expires|expiry)\b", lowered):
            return None
        if (
            re.match(r"^(the\s+)?[A-Z][A-Za-z\s&]+$", cleaned)
            and token_count <= 2
            and not any(marker in lowered for marker in ["certified", "certification"])
        ):
            return None

        # if re.match(r"^(the\s+)?[A-Z][A-Za-z\s&]+$", cleaned) and token_count <= 4:
            # return None

        
        # if token_count <= 2:
        #     return None

        COMMON_SHORT_CERTS = {
           "pmp", "cism", "cisa", "cissp", "cissp-issap",
           "ceh", "ccsp", "crisc", "gicsp", "grid",
           "cssa"
        }

        if re.match(r"^[A-Z0-9/\-]{2,}:\s+", cleaned):
            return cleaned

        if any(lowered.startswith(cert) for cert in COMMON_SHORT_CERTS):
            return cleaned
        
        # Reject other short generic lines
        if token_count <= 2 and not EXAM_CODE_RE.search(cleaned):
            return None

        if re.match(r"^[A-Z0-9/\-]{2,}\s*[-:]\s+", cleaned):
            return cleaned

        if EXAM_CODE_RE.search(cleaned):
            return cleaned
        
        if ":" in cleaned:
            left_part = cleaned.split(":")[0].strip()
            left_lower = left_part.lower()

            if (
                left_lower in COMMON_SHORT_CERTS
                or left_lower in CERTIFICATION_ALIASES
                or (len(left_part) <= 12 and left_part.isupper())
            ):
                return cleaned
 
        # if EXAM_CODE_RE.search(cleaned) or ":" in cleaned:
        #     return cleaned    

    # -------------------------------------------------
    # 6️⃣ Accept strong certification markers
    # -------------------------------------------------
        strong_markers = [
        "certified",
        "certification",
        "professional",
        "associate",
        "expert",
        "specialist",
        "practitioner",
        "architect",
        "engineer",
        "administrator",
        "analyst",
        "security",
        "manager"
       ]

        if any(marker in lowered for marker in strong_markers):
            return cleaned

    # -------------------------------------------------
    # 7️⃣ Alias Match (High Confidence)
    # -------------------------------------------------
        for alias in CERTIFICATION_ALIASES:
            if alias in lowered:
                return cleaned

    # -------------------------------------------------
    # 8️⃣ Known Certification Keywords (≥3 tokens required)
    # -------------------------------------------------
        keyword_hits = sum(
            1 for keyword in KNOWN_CERT_KEYWORDS
            if keyword in lowered
        )

        if keyword_hits >= 1 and token_count >= 3 and len(cleaned) <= 150:
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
        if not name:
            return 0.0

        lowered = name.lower()
        score = 0.0

    # Alias boost
        for alias in CERTIFICATION_ALIASES:
            if alias in lowered:
                score += 0.5
                break

    # Exam code boost
        if EXAM_CODE_RE.search(name):
            score += 0.4

    # Marker boost
        if any(marker in lowered for marker in CERT_LINE_MARKERS):
            score += 0.3

    # Keyword boost
        if any(keyword in lowered for keyword in KNOWN_CERT_KEYWORDS):
            score += 0.2

        if org:
            score += 0.1

        if issue_date:
            score += 0.1

        if score == 0:
            score = 0.5  # strict fallback floor

        return min(round(score, 2), 1.0)
        