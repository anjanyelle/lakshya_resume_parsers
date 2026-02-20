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
}

CERTIFICATION_HEADINGS = {
    # Standard
    r"^CERTIFICATIONS?\s*[:\-–—]?\s*$",
    r"^LICENSES?\s*[:\-–—]?\s*$",

    # Professional / Technical variants
    r"^PROFESSIONAL\s+CERTIFICATIONS?\s*[:\-–—]?\s*$",
    r"^TECHNICAL\s+CERTIFICATIONS?\s*[:\-–—]?\s*$",

    # Combined formats
    r"^CERTIFICATIONS?\s*(AND|&|/)\s*LICENSES?\s*[:\-–—]?\s*$",
    r"^LICENSES?\s*(AND|&|/)\s*CERTIFICATIONS?\s*[:\-–—]?\s*$",
    r"^CERTIFICATIONS?\s*(AND|&|/)\s*TRAINING\s*[:\-–—]?\s*$",

    # Credentials
    r"^PROFESSIONAL\s+CREDENTIALS?\s*[:\-–—]?\s*$",
    r"^CREDENTIALS?\s*[:\-–—]?\s*$",

    # Education & Certifications (VERY IMPORTANT – from your screenshots)
    r"^EDUCATION\s*(AND|&|/)\s*CERTIFICATIONS?\s*[:\-–—]?\s*$",

    # Certifications under education block title case
    r"^Professional\s+Certifications\s*[:\-–—]?\s*$",

    # All caps + underline style cases
    r"^CERTIFICATIONS\s*$",

    # Edge case: mixed spacing from PDF
    r"^CERTIFICATION\s+DETAILS\s*[:\-–—]?\s*$",
}
# Stop headings - immediately terminate extraction
STOP_HEADINGS = {
    r"^TECHNICAL\s+SKILLS?",
    r"^SKILLS?\s*$",
    r"^PROFESSIONAL\s+EXPERIENCE",
    r"^WORK\s+EXPERIENCE",
    r"^EXPERIENCE\s*$",
    r"^EMPLOYMENT\s+HISTORY",
    r"^JOBS?\s*$",
    r"^EDUCATION",
    r"^ACADEMIC",
    r"^AWARDS?",
    r"^ACHIEVEMENTS?",
    r"^PROJECTS?",
    r"^PUBLICATIONS?",
    r"^LANGUAGES?",
    r"^HOBBIES?",
    r"^INTERESTS?",
    r"^REFERENCES?",
    r"^PORTFOLIO",
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
    text = text.strip().upper()

    # Remove pipes used in PDF formatting
    text = re.sub(r"\s*\|\s*", " ", text)

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


# def _is_heading(line: str, heading_patterns: set[str]) -> bool:
#     normalized = _normalize_heading(line)

#     # Only treat as heading if short (1–6 words) and uppercase-like
#     if len(normalized.split()) > 8:
#         return False 
#     # NEW FIX: Handle "Page X - Section Name"
#     page_match = re.match(r"^PAGE\s+\d+\s*[-–—]\s*(.+)$", normalized)
#     if page_match:
#         normalized = page_match.group(1).strip()

#     for pattern in heading_patterns:
#         if re.search(pattern, normalized):
#             return True
#     return False

def _is_heading(line: str, heading_patterns: set[str]) -> bool:
    if not line:
        return False

    # Normalize
    text = line.strip()

    # Remove decorative underline/dash lines
    text = re.sub(r"[_\-–—]{3,}", "", text)

    # Remove trailing punctuation
    text = re.sub(r"[:\-–—]+\s*$", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Uppercase for stable matching
    normalized = text.upper()

    # Reject long lines (prevents sentence match)
    if len(normalized.split()) > 6:
        return False

    # Must not contain year (prevents experience lines)
    if re.search(r"\b(19|20)\d{2}\b", normalized):
        return False

    # Strict full-line match
    for pattern in heading_patterns:
        if re.match(pattern, normalized):
            return True

    return False


def _is_stop_heading(line: str) -> bool:
    if not line:
        return False

    text = line.strip()

    # Remove decorative lines
    text = re.sub(r"[_\-–—]{3,}", "", text)
    text = re.sub(r"[:\-–—]+\s*$", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    normalized = text.upper()

    # Reject long lines (prevents certification names from triggering stop)
    if len(normalized.split()) > 6:
        return False

    # If line contains certification keywords, do NOT treat as stop
    if re.search(
        r"\b(CERTIFIED|CERTIFICATION|PROFESSIONAL|ASSOCIATE|EXPERT|SPECIALIST|ARCHITECT|ENGINEER)\b",
        normalized,
    ):
        return False

    # Strong known section stops
    for pattern in STOP_HEADINGS:
        if re.match(pattern, normalized):
            return True

    return False


# def _is_stop_heading(line: str) -> bool:
#     """Check if line is a stop heading (should terminate extraction)."""
#     normalized = _normalize_heading(line)
#     for pattern in STOP_HEADINGS:
#         if re.match(pattern, normalized):
#             return True
#     return False

def _is_major_section_heading(line: str) -> bool:
    """
    Universal heading detector.
    Detects unknown future headings.
    """

    if not line:
        return False

    text = line.strip()

    # Remove special chars
    clean = re.sub(r"[&/,:;()\-\–\—]", "", text)
    words = clean.split()

    # 1️⃣ Heading must be short (1–6 words)
    if not (1 <= len(words) <= 6):
        return False

    # 2️⃣ Not a sentence
    if text.endswith("."):
        return False

    # 3️⃣ No year
    if re.search(r"\b(19|20)\d{2}\b", text):
        return False

    # 4️⃣ No action verbs
    if re.search(
        r"\b(developed|managed|led|designed|implemented|created|worked|analyzed)\b",
        text,
        re.IGNORECASE,
    ):
        return False

    # 5️⃣ Accept ALL CAPS
    if text.isupper():
        return True

    # 6️⃣ Accept Title Case headings
    if all(word[:1].isupper() for word in words if word):
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


def extract_summary(text: str) -> ExtractionResult:
    """
    Extract professional summary using strict regex lookahead boundary detection.
    
    Extracts only text under "Summary" or "Professional Summary" heading.
    Stops immediately when encountering stop headings (Certification, Skills, etc.).
    Does not include the stop heading line itself.
    
    Args:
        text: Full resume text
        
    Returns:
        ExtractionResult with extracted summary, confidence, and metadata
        
    Examples:
        >>> result = extract_summary("PROFESSIONAL SUMMARY\\nHigh-achieving IT...")
        >>> result.confidence
        1.0
    """
    if not text or not isinstance(text, str):
        return ExtractionResult(
            content="",
            confidence=0.0,
            section_found=False,
            extracted_lines=[],
        )
    
    lines = text.splitlines()
    
    # Find summary heading using strict regex (case-insensitive with lookahead)
    summary_idx = None
    summary_pattern = r"(?i)^\s*(professional\s*\|?\s*)?(summary|profile|objective)\s*$"
    
    for i, line in enumerate(lines):
        if re.match(summary_pattern, line):
            summary_idx = i
            break
    
    if summary_idx is None:
        logger.debug("No summary heading found")
        return ExtractionResult(
            content="",
            confidence=0.0,
            section_found=False,
            extracted_lines=[],
        )
    
    # Define stop heading patterns with lookahead boundary
    stop_patterns = [
    r"(?i)^\s*certifications?\s*:?\s*$",
    r"(?i)^\s*technical\s+skills?\s*:?\s*$",
    r"(?i)^\s*skills?\s*:?\s*$",
    r"(?i)^\s*professional\s+experience\s*:?\s*$",
    r"(?i)^\s*work\s+experience\s*:?\s*$",
    r"(?i)^\s*education\s*:?\s*$",
    r"(?i)^\s*environment\s*:?\s*$",
]
    
    # Extract lines until stop heading (do not include stop heading line)
    extracted_lines = []
    for i in range(summary_idx + 1, len(lines)):
        line = lines[i]
        
        # Check if this line matches any stop heading using lookahead patterns
        is_stop = any(re.match(pattern, line) for pattern in stop_patterns)
        if is_stop:
            logger.debug(f"Stop boundary found at line {i}: {line[:50]}")
            break

        # Stop if email detected (contact bleed)
        if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", line):
            break

    # Stop if phone detected
        if re.search(r"\+?\d[\d\s\-\(\)]{8,}", line):
           break
        # Stop if we hit a standalone name block (ALL CAPS short line)
        if re.match(r"^[A-Z]{2,}$", line.strip()) and len(line.strip()) < 20:
           break
        extracted_lines.append(line)
    
    # Remove leading/trailing blank lines
    while extracted_lines and not extracted_lines[0].strip():
        extracted_lines.pop(0)
    while extracted_lines and not extracted_lines[-1].strip():
        extracted_lines.pop()
    
    # Check if we have actual content
    has_content = any(line.strip() for line in extracted_lines)
    
    if not has_content:
        logger.debug("Summary heading found but no content after it")
        return ExtractionResult(
            content="",
            confidence=0.5,
            section_found=True,
            extracted_lines=[],
        )
    
    # Join lines with newlines to preserve structure
    # Join lines
    raw_content = "\n".join(extracted_lines).strip()

    # Clean summary text once
    content = _clean_summary_text(raw_content)

    logger.debug(f"Summary extracted: {len(content)} chars, confidence=1.0")

    return ExtractionResult(
        content=content,
        confidence=1.0,
        section_found=True,
        extracted_lines=extracted_lines,   # keep original lines
    )

def _clean_summary_text(text: str) -> str:
    if not text:
        return text

    # Remove pipe bullets
    text = re.sub(r"^\s*\|\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+\|\s+", " ", text)

    # Remove bullet characters
    text = re.sub(r"^\s*[-–—•]\s*", "", text, flags=re.MULTILINE)

    # Fix hyphen line breaks
    text = re.sub(r"-\s*\n\s*", "", text)

    # Merge wrapped lines
    text = re.sub(r"\n(?!\n)", " ", text)

    # Remove page numbers
    text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)

    # Fix camelCase joins
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)

    # Fix letter-number joins
    text = re.sub(r"(?<=[a-zA-Z])(?=\d)", " ", text)
    text = re.sub(r"(?<=\d)(?=[a-zA-Z])", " ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()



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
    # =====================================================
    inline_pattern = re.compile(
        r"(?i)certifications?\s*[:\-–—]\s*(.+)"
    )

    for line in lines:
        match = inline_pattern.search(line)
        if match:
            inline_content = match.group(1).strip()

            # Split multiple certifications separated by comma
            parts = re.split(r"\s*,\s*", inline_content)
            for part in parts:
                if part and len(part) < 200:
                    extracted_lines.append(part.strip())

    # If inline found → return immediately
    if extracted_lines:
        extracted_lines = list(dict.fromkeys(extracted_lines))
        return ExtractionResult(
            content="\n".join(extracted_lines),
            confidence=0.9,   # slightly lower than strict boundary
            section_found=True,
            extracted_lines=extracted_lines,
        )

    # 2️⃣ STRICT BOUNDARY SECTION DETECTION
    for idx, line in enumerate(lines):
        if _is_heading(line, CERTIFICATION_HEADINGS):
            cert_start_idx = idx
            logger.debug(f"Certification section found at line {idx}")
            break

    if cert_start_idx == -1:
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
        # if _is_stop_heading(line) or _is_major_section_heading(line):
        #       break
        
        clean_line = line.strip()

        if re.match(r"^Page\s+\d+", clean_line, re.IGNORECASE):
            break

        if not clean_line:
            continue
         # handles PDF bullet types
        clean_line = re.sub(r"^[\-\u2013\u2014•\*\u2022\u25CF\u25E6\u2043]+\s*", "", clean_line)

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

    extracted_lines = list(dict.fromkeys(extracted_lines))

    if not extracted_lines:
        return ExtractionResult(
            content="",
            confidence=0.5,
            section_found=True,
            extracted_lines=[],
        )

    return ExtractionResult(
        content="\n".join(extracted_lines),
        confidence=1.0,
        section_found=True,
        extracted_lines=extracted_lines,
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