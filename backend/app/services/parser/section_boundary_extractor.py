"""
Strict boundary-based extraction for resume sections.

This module provides production-safe extractors that use rigid boundary detection
to extract summary and certifications from resume text without over-extraction.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# Section heading patterns
SUMMARY_HEADINGS = {
    r"^PROFESSIONAL\s+SUMMARY\s*$",
    r"^PROFESSIONAL\s+PROFILE\s*$",
    r"^EXECUTIVE\s+SUMMARY\s*$",
    r"^SUMMARY\s*$",
    r"^OBJECTIVE\s*$",
    r"^CAREER\s+SUMMARY\s*$",
    r"^CAREER\s+OVERVIEW\s*$",
    r"^PROFILE\s*$",
    r"^ABOUT\s+ME\s*$",
    r"^PERSONAL\s+STATEMENT\s*$",
    r"^INTRODUCTION\s*$",
    r"^OVERVIEW\s*$",
}

CERTIFICATION_HEADINGS = {
    r"^CERTIFICATIONS?\s*[:\-–—]?\s*$",
    r"^CERTIFICATION\s*[:\-–—]?\s*$",
    r"^LICENSES?\s*[:\-–—]?\s*$",
    r"^PROFESSIONAL\s+CREDENTIALS?\s*[:\-–—]?\s*$",
    r"^CREDENTIALS?\s*[:\-–—]?\s*$",
    r"^CERTIFICATES\s*&\s*GRANTS\b.*$",
    r"^PROFESSIONAL\s+CERTIFICATIONS?\s*[:\-–—]?\s*$",
    r"^LICENSES?\s+AND\s+CERTIFICATIONS?\s*[:\-–—]?\s*$",
    r"^CERTIFICATIONS?\s+AND\s+LICENSES?\s*[:\-–—]?\s*$",
    r"^PROFESSIONAL\s+QUALIFICATIONS?\s*[:\-–—]?\s*$",
    r"^ACCREDITATIONS?\s*[:\-–—]?\s*$",
    r"^TRAINING\s+&?\s*CERTIFICATIONS?\s*[:\-–—]?\s*$",
    r"^CERTIFICATIONS?\s+&?\s*TRAINING\s*[:\-–—]?\s*$",
}

# Stop headings - immediately terminate extraction
STOP_HEADINGS = {
    r"(?i)^\s*certification\s*[:\-–—]",
    r"(?i)^\s*certifications?\s*[:\-–—]?",
    r"(?i)^\s*certification\s*[:\-–—]",       
    r"(?i)^\s*certifications?\s*[:\-–—]?",
    r"^TECHNICAL\s+SKILLS?",
    r"^SKILLS?\s*$",
    r"^PROFESSIONAL\s+EXPERIENCE",
    r"^WORK\s+EXPERIENCE",
    r"^EXPERIENCE\s*$",
    r"^EMPLOYMENT\s+HISTORY",
    r"^JOBS?\s*$",
    r"^EDUCATION",
    r"^ACADEMIC",
    r"^CERTIFICATIONS?",
    r"^LICENSES?",
    r"^AWARDS?",
    r"^ACHIEVEMENTS?",
    r"^PROJECTS?",
    r"^PUBLICATIONS?",
    r"^LANGUAGES?",
    r"^HOBBIES?",
    r"^INTERESTS?",
    r"^REFERENCES?",
    r"^PORTFOLIO",
    r"^PUBLICATIONS?",
    r"^VOLUNTEER",
    r"^PAGE\s+\d+",
}


@dataclass
class ExtractionResult:
    """Result from section extraction."""
    content: str
    confidence: float  # 1.0 = strict boundary match, 0.0 = not found
    section_found: bool
    extracted_lines: list[str]


def _normalize_heading(text: str) -> str:
    """Normalize heading text for matching."""
    return re.sub(r"\s+", " ", text.strip().upper())


def _is_heading(line: str, heading_patterns: set[str]) -> bool:
    normalized = _normalize_heading(line)

    # 🔥 NEW FIX: Handle "Page X - Section Name"
    page_match = re.match(r"^PAGE\s+\d+\s*[-–—]\s*(.+)$", normalized)
    if page_match:
        normalized = page_match.group(1).strip()

    for pattern in heading_patterns:
        if re.match(pattern, normalized):
            return True
    return False


def _is_stop_heading(line: str) -> bool:
    """Check if line is a stop heading (should terminate extraction)."""
    normalized = _normalize_heading(line)
    for pattern in STOP_HEADINGS:
        if re.match(pattern, normalized):
            return True
    return False


def _is_blank_or_whitespace(line: str) -> bool:
    """Check if line is empty or whitespace only."""
    return not line.strip()


def _is_environment_line(line: str) -> bool:
    """
    Filter out environment/technical stack lines.
    Patterns: "Environment: Java, Python, AWS"
    """
    normalized = line.strip()
    return bool(re.match(r"^ENVIRONMENT\s*[:–—-]", normalized, re.IGNORECASE))


def _is_skills_line(line: str) -> bool:
    """Filter out technical skills block lines."""
    normalized = line.strip().upper()
    patterns = [
        r"^TECHNOLOGIES?\s*[:–—-]",
        r"^TECH\s*STACK\s*[:–—-]",
        r"^TOOLS?\s*[:–—-]",
        r"^TECH\s*[:–—-]",
    ]
    return any(re.match(p, normalized) for p in patterns)


def _is_job_title_with_dates(line: str) -> bool:
    """
    Filter out job title and date lines like:
    - "Senior Developer | Company - 2020-2022"
    - "Manager (2018 – Present)"
    """
    # Check for date patterns
    if not re.search(r"\b(20\d{2}|19\d{2}|present|current|now)\b", line, re.IGNORECASE):
        return False
    
    # Check for job-related keywords
    job_keywords_pattern = r"\b(developer|engineer|manager|director|analyst|consultant|architect|lead|specialist|officer|executive|associate|coordinator|administrator)\b"
    return bool(re.search(job_keywords_pattern, line, re.IGNORECASE))


def _is_experience_description(line: str) -> bool:
    """
    Filter out experience description lines like:
    - "Developed REST APIs using Python and FastAPI"
    - "Led team of 8 developers"
    """
    experience_verbs = [
        "developed", "designed", "implemented", "created", "built", "engineered",
        "led", "managed", "directed", "coordinated", "organized", "planned",
        "analyzed", "evaluated", "assessed", "identified", "solved",
        "improved", "optimized", "increased", "reduced", "enhanced",
        "collaborated", "contributed", "participated", "worked",
    ]
    
    pattern = r"\b(" + "|".join(experience_verbs) + r")\b"
    return bool(re.search(pattern, line, re.IGNORECASE))


def extract_certifications(text: str) -> ExtractionResult:
    """
    Strict + inline-safe certification extraction.

    Supports:
    - Standard section:
        CERTIFICATIONS
        AWS Solutions Architect
    - Inline format:
        Certification: Azure DevOps Engineer Expert (AZ-400)
    - Inline inside summary paragraph
    """

    if not text or not isinstance(text, str):
        return ExtractionResult(
            content="",
            confidence=0.0,
            section_found=False,
            extracted_lines=[],
        )

    lines = text.splitlines()
    extracted_lines: list[str] = []
    cert_start_idx = -1

    # =====================================================
    # 1️⃣ INLINE DETECTION (WORKS EVEN INSIDE SUMMARY)
    #    Matches: Certifications:, Licenses:, Credentials:, etc.
    # =====================================================
    inline_pattern = re.compile(
        r"(?i)(?:certifications?|licenses?|credentials?|professional\s+certifications?|licenses?\s*&\s*certifications?)\s*[:\-–—]\s*(.+)"
    )

    inline_lines: list[str] = []
    for line in lines:
        match = inline_pattern.search(line)
        if match:
            inline_content = match.group(1).strip()
            parts = re.split(r"\s*,\s*", inline_content)
            for part in parts:
                if part and len(part) < 200:
                    inline_lines.append(part.strip())

    # =====================================================
    # 2️⃣ STRICT BOUNDARY SECTION DETECTION
    # =====================================================
    for idx, line in enumerate(lines):
        if _is_heading(line, CERTIFICATION_HEADINGS):
            cert_start_idx = idx
            logger.debug(f"Certification section found at line {idx}")
            break

    if cert_start_idx == -1:
        # No strict section; return inline content if found
        if inline_lines:
            inline_lines = list(dict.fromkeys(inline_lines))
            return ExtractionResult(
                content="\n".join(inline_lines),
                confidence=0.9,
                section_found=True,
                extracted_lines=inline_lines,
            )
        return ExtractionResult(
            content="",
            confidence=0.0,
            section_found=False,
            extracted_lines=[],
        )

    # =====================================================
    # 3️⃣ EXTRACT LINES UNDER SECTION
    # =====================================================
    for idx in range(cert_start_idx + 1, len(lines)):
        line = lines[idx]

        if _is_stop_heading(line):
            break

        clean_line = line.strip()

        if re.match(r"^Page\s+\d+", clean_line, re.IGNORECASE):
            break

        if not clean_line:
            continue

        clean_line = re.sub(r"^[•\-\*\u2022]\s*", "", clean_line)

        if _is_environment_line(clean_line):
            break

        if _is_skills_line(clean_line):
            break

        if _is_job_title_with_dates(clean_line):
            break

        if _is_experience_description(clean_line):
            continue

        if clean_line.lower() in ("certifications", "licenses"):
            continue

        # Prevent paragraph bleeding
        if len(clean_line) > 200:
            continue

        extracted_lines.append(clean_line)

    # Merge inline + strict boundary content (preserve order, dedupe)
    merged = list(dict.fromkeys(inline_lines + extracted_lines))

    if not merged:
        return ExtractionResult(
            content="",
            confidence=0.5,
            section_found=True,
            extracted_lines=[],
        )

    return ExtractionResult(
        content="\n".join(merged),
        confidence=1.0,
        section_found=True,
        extracted_lines=merged,
    )



# JSON Structure Examples for Reference
EXAMPLE_JSON_STRUCTURES = {
    "summary": {
        "description": "Professional summary extraction result",
        "example": {
            "content": "High-achieving software engineer with 8+ years of experience in full-stack development, cloud architecture, and team leadership. Proven expertise in designing scalable microservices, mentoring junior developers, and delivering projects on time.",
            "confidence": 1.0,
            "section_found": True,
            "extracted_lines": [
                "High-achieving software engineer with 8+ years of experience in full-stack development, cloud architecture, and team leadership.",
                "Proven expertise in designing scalable microservices, mentoring junior developers, and delivering projects on time."
            ]
        }
    },
    "certifications": {
        "description": "Certifications extraction result",
        "example": {
            "content": "AWS Solutions Architect Professional\nCertified Kubernetes Administrator (CKA)\nGoogle Cloud Professional Data Engineer",
            "confidence": 1.0,
            "section_found": True,
            "extracted_lines": [
                "AWS Solutions Architect Professional",
                "Certified Kubernetes Administrator (CKA)",
                "Google Cloud Professional Data Engineer"
            ]
        }
    },
    "combined_candidate_example": {
        "description": "Full candidate data structure after parsing",
        "candidate": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "full_name": "John Smith",
            "email": "john.smith@example.com",
            "summary": "High-achieving software engineer with 8+ years of experience...",
            "certifications": [
                {
                    "name": "AWS Solutions Architect Professional",
                    "issuing_organization": "Amazon Web Services",
                    "issue_date": "2022-06-15",
                    "expiry_date": None,
                    "credential_id": "AQJQ9MKJ3K2K1K0K"
                },
                {
                    "name": "Certified Kubernetes Administrator",
                    "issuing_organization": "Cloud Native Computing Foundation",
                    "issue_date": "2021-09-20",
                    "expiry_date": "2024-09-20",
                    "credential_id": "LF-ABC123DEF456"
                }
            ],
            "work_experience": [
                {
                    "company_name": "Tech Corp",
                    "job_title": "Senior Software Engineer",
                    "start_date": "2020-01-15",
                    "end_date": None,
                    "is_current": True,
                    "location": "San Francisco, CA",
                    "description": "Led architecture design for microservices platform..."
                }
            ],
            "skills": [
                {
                    "name": "Python",
                    "normalized_name": "python",
                    "category": "Programming Language",
                    "years_experience": 8,
                    "proficiency": "advanced"
                }
            ]
        }
    }
}