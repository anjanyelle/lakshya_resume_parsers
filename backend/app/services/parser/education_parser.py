from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date

import dateparser

from app.data.taxonomy.degree_taxonomy import DEGREE_ALIASES, DEGREE_KEYWORDS
from app.data.taxonomy.universities_top import TOP_UNIVERSITIES

logger = logging.getLogger(__name__)


MONTH_TOKEN = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_TOKEN = (
    r"(?:"
    r"\d{4}-\d{2}-\d{2}"
    r"|\d{4}[/-]\d{1,2}"
    r"|\d{1,2}[/-]\d{2}"
    r"|\d{1,2}[/-]\d{4}"
    r"|\d{4}"
    r"|Q[1-4]\s+\d{4}"
    r"|(?:Spring|Fall|Summer|Winter)\s+\d{4}"
    rf"|{MONTH_TOKEN}\s*[\'\u2019]\d{{2}}"
    r"|\d{4}\.\d{2}|\d{2}\.\d{4}"
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{4}}"
    rf"|{MONTH_TOKEN}\s*[\u2019']\s*\d{{2}}"
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{2}}"
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>{DATE_TOKEN})\s*(?:\s*(?:[-–—]|to|until|thru|through)\s*)\s*(?P<end>present|current|expected|ongoing|{DATE_TOKEN})",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
GPA_RE = re.compile(
    r"\b(?P<gpa>\d(?:\.\d{1,2})?)\s*(?:/|of|out of)\s*(?P<scale>\d(?:\.\d)?)\b|\b(?P<pct>\d{2,3})%\b|"
    r"\b(?P<cgpa>cgpa|gpa)[\s:]*(?P<cgpa_val>\d(?:\.\d{1,2})?)\b",
    re.IGNORECASE,
)
HONORS_RE = re.compile(
    r"\b(cum laude|magna cum laude|summa cum laude|dean'?s list|honors|honour|distinction|"
    r"first class|second class|merit|gold medal(?:ist)?|valedictorian|salutatorian)\b",
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
            # Start new block if we find a year or institution marker
            is_new_entry = (
                YEAR_RE.search(line) or
                any(keyword in line.lower() for keyword in ["university", "college", "institute"])
            )
            
            if is_new_entry and current:
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
        
        # First pass: check for exact matches in TOP_UNIVERSITIES
        for line in lines:
            line_clean = line.strip()
            lowered = line_clean.lower()
            
            # Exact match against TOP_UNIVERSITIES
            if lowered in TOP_UNIVERSITIES:
                return line_clean
            
            # Partial match for universities with common variations
            for top_uni in TOP_UNIVERSITIES:
                if top_uni in lowered and len(lowered) - len(top_uni) < 20:
                    return line_clean
        
        # Second pass: look for institution keywords
        institution_keywords = [
            "university", "college", "institute", "school of", "academy",
            "bootcamp", "conservatory", "seminary", "polytechnic"
        ]
        
        for line in lines:
            line_clean = line.strip()
            lowered = line_clean.lower()
            
            if any(keyword in lowered for keyword in institution_keywords):
                # Filter out lines that are too short or likely false positives
                if len(line_clean) > 5 and not re.match(r"^\d{4}$", line_clean):
                    return line_clean
        
        return None

    def _extract_degree(self, text: str) -> str | None:
        """
        Extract degree/qualification from text.
        
        Args:
            text: Input text containing potential degree information
            
        Returns:
            Standardized degree name or None if not found
        """
        if not text:
            return None
            
        lowered = text.lower()
        
        # Check for common degree abbreviations first (highest priority)
        for abbr, full in DEGREE_ALIASES.items():
            # Use word boundaries to avoid partial matches
            if re.search(rf"\b{re.escape(abbr)}\b", lowered):
                return full
        
        # Expanded allowed markers for degree identification
        allowed_markers = (
            "bachelor", "bachelors", "bachelor's", "b.a.", "b.s.", "b.sc.",
            "undergraduate", "ug", "u.g.",
            "master", "masters", "master's", "m.a.", "m.s.", "m.sc.",
            "postgraduate", "pg", "p.g.",
            "doctorate", "phd", "ph.d.", "doctoral", "d.phil",
            "associate", "assoc.", "a.a.", "a.s.",
            "diploma", "advanced diploma", "pgd", "post graduate diploma",
            "certificate", "certification", "cert.",
            "high school", "higher secondary", "senior secondary", "secondary",
            "graduate", "grad",
            "professional", "professional degree",
            "licentiate", "fellow", "fellowship",
            "mba", "mca", "mtech", "btech", "be", "me",
            "mbbs", "md", "llb", "llm", "bba", "bca"
        )
        
        # Keywords that should be skipped (fields of study, not degrees)
        field_keywords = {
            "engineering", "technology", 
            "computer science", "information technology", "information systems",
            "management", "commerce", "business", "administration",
            "medicine", "pharmacy", "nursing", "healthcare", "medical",
            "law", "legal",
            "science", "arts", "humanities", "liberal arts",
            "education", "teaching",
            "economics", "finance", "accounting",
            "mathematics", "statistics", "physics", "chemistry", "biology",
            "psychology", "sociology", "anthropology",
            "architecture", "design",
            "journalism", "communications", "media"
        }
        
        # Search through DEGREE_KEYWORDS
        for keyword in DEGREE_KEYWORDS:
            keyword_l = (keyword or "").strip().lower()
            
            if not keyword_l:
                continue
                
            # Skip field-only keywords
            if keyword_l in field_keywords:
                continue
                
            # Only consider if it contains a degree marker
            if not any(marker in keyword_l for marker in allowed_markers):
                continue
                
            if keyword_l in lowered:
                return keyword.title()
        
        # Pattern-based extraction for common degree formats
        degree_patterns = [
            # "Bachelor of Science" style with optional field
            r"\b(bachelor|master|doctor)(?:'?s)?\s+of\s+(science|arts|engineering|business|medicine|laws?|philosophy|education|fine arts|social work|public health)\b",
            # "Associate in Arts" style
            r"\b(associate)(?:'?s)?\s+(?:of|in)\s+(science|arts|applied science|business)\b",
            # B.Sc., M.Sc., Ph.D. style with period
            r"\b([BbMmDdPp])\.([A-Z][a-z]+\.?)\b",
            # MBA, MCA, BBA, MBBS style (2-5 letter acronyms starting with B, M, P, D)
            r"\b([BMPD][A-Z]{1,4})\b",
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                full_match = match.group(0)
                # For acronym patterns, validate length and starting letter
                if re.match(r"\b[BMPD][A-Z]{1,4}\b", full_match):
                    # Common degree acronyms
                    common_degrees = {
                        "MBA", "MCA", "BBA", "BCA", "MBBS", "MD", "MS",
                        "LLB", "LLM", "BSC", "MSC", "BE", "ME", "BTECH", "MTECH"
                    }
                    if full_match.upper() in common_degrees:
                        return full_match.upper()
                else:
                    return full_match.title()
        
        # Check for year-based qualifications (e.g., "12th grade", "10+2")
        year_patterns = [
            r"\b(10th|12th|tenth|twelfth)\b",
            r"\b10\+2\b",
            r"\bgrade\s+(10|12|ten|twelve)\b",
            r"\b(ssc|hsc|cbse|icse)\b",  # Indian boards
        ]
        
        for pattern in year_patterns:
            if re.search(pattern, lowered):
                if any(marker in lowered for marker in ["12", "twelfth", "hsc", "higher"]):
                    return "High School"
                elif any(marker in lowered for marker in ["10", "tenth", "ssc"]):
                    return "Secondary School"
        
        # Check for international qualifications
        intl_qualifications = {
            "a level": "A Level",
            "a-level": "A Level",
            "o level": "O Level", 
            "o-level": "O Level",
            "ib diploma": "IB Diploma",
            "international baccalaureate": "IB Diploma",
            "gcse": "GCSE",
            "abitur": "Abitur",
            "baccalauréat": "Baccalauréat",
            "baccalaureate": "Baccalaureate",
            "maturita": "Maturita",
        }
        
        for qual_key, qual_value in intl_qualifications.items():
            if qual_key in lowered:
                return qual_value
        
        # Check for vocational/technical qualifications
        vocational_patterns = [
            r"\biti\b",  # Industrial Training Institute
            r"\bpolytechnic\s+diploma\b",
            r"\btrade\s+(?:certificate|qualification)\b",
            r"\btechnical\s+diploma\b",
            r"\bvocational\s+(?:training|certificate|diploma)\b",
            r"\bapprentice(?:ship)?\b",
        ]
        
        for pattern in vocational_patterns:
            match = re.search(pattern, lowered)
            if match:
                return match.group(0).title()
        
        return None

    def _extract_field(self, text: str) -> str | None:
        """Extract field of study from text."""
        # Common patterns for field of study
        field_patterns = [
            r"\b(?:in|major in|specialization in|concentration in|focus in)\s+([A-Za-z &/\-]+)",
            r"\b(?:degree|bachelor|master|diploma)\s+(?:of|in)\s+([A-Za-z &/\-]+)",
        ]
        
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                field = match.group(1).strip()
                # Remove trailing year or comma
                field = re.split(r"\b(19\d{2}|20\d{2})\b|,|\(", field)[0].strip()
                # Validate field length
                if 2 <= len(field.split()) <= 8 and len(field) > 3:
                    # Remove common stopwords at the end
                    field = re.sub(r"\s+(and|with|from|at|the)$", "", field, flags=re.IGNORECASE)
                    return field.strip()
        
        return None

    def _extract_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        """Extract start and end dates from text."""
        match = DATE_RANGE_RE.search(text)
        in_progress = False
        
        if match:
            start_raw = match.group("start")
            end_raw = match.group("end")
            start_date = self._parse_date(start_raw)
            
            if end_raw.lower() in {"present", "current", "expected", "ongoing"}:
                in_progress = True
                return start_date, None, True
                
            end_date = self._parse_date(end_raw)
            return start_date, end_date, False

        # Fallback: look for single year or year range (handles table layout: dates in separate columns)
        years = YEAR_RE.findall(text)
        if len(years) >= 2:
            # If we have multiple years, assume first is start, last is end
            start_year = int(years[0])
            end_year = int(years[-1])
            return date(start_year, 1, 1), date(end_year, 1, 1), False
        elif len(years) == 1:
            # Single year likely means graduation year
            end_year = int(years[0])
            return None, date(end_year, 1, 1), False
            
        return None, None, False

    def _parse_date(self, value: str) -> date | None:
        """Parse a date string into a date object."""
        if not value:
            return None

        raw = str(value).strip().replace("\u2019", "'")
        raw = (
            raw.replace("Q1", "January")
            .replace("Q2", "April")
            .replace("Q3", "July")
            .replace("Q4", "October")
            .replace("Spring", "March")
            .replace("Fall", "September")
            .replace("Summer", "June")
            .replace("Winter", "December")
        )
        raw = re.sub(
            r"[\'\u2019](\d{2})\b",
            lambda m: " 20" + m.group(1) if int(m.group(1)) <= 50 else " 19" + m.group(1),
            raw,
        )
        m_dot = re.match(r"^(?P<y>\d{4})\.(?P<m>\d{2})$", raw)
        if m_dot:
            raw = f"{m_dot.group('y')}-{m_dot.group('m')}"
        m_dot2 = re.match(r"^(?P<m>\d{2})\.(?P<y>\d{4})$", raw)
        if m_dot2:
            raw = f"{m_dot2.group('y')}-{m_dot2.group('m')}"

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
                    "RETURN_AS_TIMEZONE_AWARE": False,
                },
            )
            return parsed.date() if parsed else None
            
        parsed = dateparser.parse(
            raw, 
            settings={
                "PREFER_DAY_OF_MONTH": "first",
                "PREFER_DATES_FROM": "past",
                "RETURN_AS_TIMEZONE_AWARE": False
            }
        )
        return parsed.date() if parsed else None

    def _extract_gpa(self, text: str) -> str | None:
        """Extract GPA or grade information from text."""
        match = GPA_RE.search(text)
        if not match:
            return None
            
        # Format: X/Y or X out of Y
        if match.group("gpa") and match.group("scale"):
            gpa_val = match.group("gpa")
            scale_val = match.group("scale")
            return f"{gpa_val}/{scale_val}"
            
        # Format: XX%
        if match.group("pct"):
            return f"{match.group('pct')}%"
            
        # Format: CGPA: X.XX or GPA: X.XX
        if match.group("cgpa") and match.group("cgpa_val"):
            return f"GPA: {match.group('cgpa_val')}"
            
        return None

    def _extract_honors(self, text: str) -> str | None:
        """Extract honors and distinctions from text."""
        match = HONORS_RE.search(text)
        if match:
            honor = match.group(1).title()
            # Normalize common variations
            honor = honor.replace("'S", "'s")
            return honor
        return None

    def _score_confidence(
        self, institution: str | None, degree: str | None, date_value: date | None
    ) -> float:
        """Calculate confidence score for the education entry."""
        score = 0.0
        
        if institution:
            # Higher score for top universities
            if institution.lower() in TOP_UNIVERSITIES:
                score += 0.5
            else:
                score += 0.4
                
        if degree:
            score += 0.3
            
        if date_value:
            # Check if date is reasonable (between 1950 and current year + 10)
            current_year = date.today().year
            if 1950 <= date_value.year <= current_year + 10:
                score += 0.3
            else:
                score += 0.1  # Lower confidence for unusual dates
                
        return min(score, 1.0)