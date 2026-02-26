from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date

import dateparser

from app.data.taxonomy.degree_taxonomy import DEGREE_ALIASES, DEGREE_KEYWORDS
from app.data.taxonomy.universities_top import TOP_UNIVERSITIES
from app.services.parser.normalize import fix_concatenated_words

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
# "Expected Dec 2019" or "Expected December 2019" → in-progress graduation
_EXPECTED_DATE_RE = re.compile(
    r"Expected\s+(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z.]*\s+)?\d{2,4}",
    re.IGNORECASE,
)
# Full date range with month names (e.g. July-2010 to June 2014, Aug. 2018 – May 2021)
_DATE_RANGE_FULL_RE = re.compile(
    rf"(?P<start>{MONTH_TOKEN}[.,]?\s*\d{{2,4}})\s*(?:[-–—]|to)\s*(?P<end>{MONTH_TOKEN}[.,]?\s*\d{{2,4}}|\d{{4}}|present|current|expected|ongoing)",
    re.IGNORECASE,
)
# "Graduated: 2017", "Graduated: 2019"
GRADUATED_RE = re.compile(r"graduated\s*:\s*(\d{4})", re.IGNORECASE)
# "Year of passed: 2014" or "Year of passed:"
YEAR_PASSED_RE = re.compile(r"year\s+of\s+passed\s*:\s*(\d{4})?", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
GPA_RE = re.compile(
    r"\b(?P<gpa>\d(?:\.\d{1,2})?)\s*(?:/|of|out of)\s*(?P<scale>\d{1,2}(?:\.\d{1,2})?)\b|"
    r"\b(?P<pct>\d{2,3})%|"
    r"\b(?:cum\.?\s*)?(?P<cgpa>cgpa|gpa)[\s:]*(?P<cgpa_val>\d(?:\.\d{1,2})?)\s*(?:/|of|out of)\s*(?P<scale2>\d{1,2}(?:\.\d{1,2})?)?|"
    r"\b(?:cum\.?\s*)?(?P<cgpa2>cgpa|gpa)[\s:]*(?P<cgpa_val2>\d(?:\.\d{1,2})?)\b",
    re.IGNORECASE,
)
HONORS_RE = re.compile(
    r"\b(cum laude|magna cum laude|summa cum laude|dean'?s list|honors|honour|distinction|"
    r"first class|second class|merit|gold medal(?:ist)?|valedictorian|salutatorian)\b",
    re.IGNORECASE,
)
# Full "Honors: ..." line for description
HONORS_FULL_RE = re.compile(r"honors\s*:\s*([^\n•·▪\-]+?)(?=\n|$|•|·)", re.IGNORECASE)
THESIS_RE = re.compile(r'thesis\s*:\s*["\']?([^"\'\n]+)["\']?', re.IGNORECASE)
SPECIALIZATION_RE = re.compile(r"specialization\s+in\s+([^\n.,]+)", re.IGNORECASE)
# Trailing month names that wrongly attach to degree/field (strip from field_of_study)
_TRAILING_MONTH_RE = re.compile(
    r"\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*$", re.IGNORECASE
)

# Regex to detect a degree keyword at the START of a line (anchor for block splitting)
_DEGREE_LINE_RE = re.compile(
    r"(?:^|\b)(?:"
    r"bachelor(?:'?s)?|master(?:'?s)?|doctor(?:ate)?|"
    r"associate(?:'?s)?|diploma|certificate|"
    r"b\.?(?:tech|sc|a|s|e|com|ca|ba)|"
    r"m\.?(?:tech|sc|a|s|e|com|ca|ba|bbs)|"
    r"ph\.?d|mba|"
    r"high school|secondary|"
    r"degree\s*:|"
    r"hsc\s*\(|sslc\s*\(|10th|12th|tenth|twelfth"
    r")\b",
    re.IGNORECASE,
)

# Institution keywords used in splitting and extraction
_INSTITUTION_KEYWORDS = (
    "university", "college", "institute", "school of", "academy",
    "bootcamp", "conservatory", "seminary", "polytechnic",
)

# Label prefixes commonly found before institution names
_INSTITUTION_PREFIX_RE = re.compile(
    r"^\s*(?:college|university|institution|school|institute)\s*:\s*",
    re.IGNORECASE,
)
# Strip from institution display: degree text, Graduated:, Thesis:, Specialization (keep only actual institution name)
_INSTITUTION_STOP_RE = re.compile(
    r"\s*(?:Graduated\s*:.*|Thesis\s*:.*|Specialization\s+in\s+.*|Honors\s*:.*)$",
    re.IGNORECASE,
)
# Degree keywords that must not start the institution line (find first University/College/Institute after these)
_DEGREE_START_RE = re.compile(
    r"^\s*(?:Bachelor|Master|B\.?Tech|M\.?Tech|B\.?E|M\.?E|MBA|B\.?S|M\.?S|B\.?A|M\.?A|Doctor|Ph\.?D)\b",
    re.IGNORECASE,
)

_INSTITUTION_LEADING_STOP = re.compile(
    r"^\s*(?:Master|Bachelor|Science|Business|Administration|University|College|Institute|School|Academy|Project|Summary|Objective|Skills|Certifications?|Experience|Work|Employment)\b",
    re.IGNORECASE,
)
# Common typos in display (e.g. OCR, space-restoration splits)
_INSTITUTION_TYPO_FIXES = (("technoloav", "Technology"), ("at lanta", "Atlanta"), ("at lanta,", "Atlanta,"))
# Words that are degree/field terms and must not start institution name (e.g. "Engineering University of X" -> "University of X")
_INSTITUTION_LEADING_STOP = re.compile(
    r"^\s*(?:Engineering|Research|Assurance|Information|Computer|Cybersecurity|Operations|Industrial|Technology|Management|Business|Science|Arts)\s+",
    re.IGNORECASE,
)
# Noise / test artifacts to strip from end of extracted fields (e.g. "TestCase3.3", "Test Case 1.1")
_NOISE_SUFFIX_RE = re.compile(
    r"\s*(?:[-–—]\s*)?(?:TestCase|Test\s*Case)\s*\d*\.?\d*\s*$",
    re.IGNORECASE,
)
# PDF (cid:NN) character reference artifacts from text extraction (e.g. "(cid:17) Karpagam College")
_CID_RE = re.compile(r"\(cid:\d+\)")


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


def _strip_delimiter_artifacts(s: str) -> str:
    """Remove pipe and delimiter artifacts from extracted strings (e.g. trailing ' |', '| ')."""
    if not s:
        return s
    s = s.strip()
    s = re.sub(r"\s*\|\s*$", "", s).strip()
    s = re.sub(r"^\s*\|\s*", "", s).strip()
    s = re.sub(r"\s*\|\s*$", "", s).strip()
    return s


def _strip_noise_from_field(s: str) -> str:
    """Remove test/noise suffixes like TestCase3.3 from extracted fields."""
    if not s:
        return s
    s = _NOISE_SUFFIX_RE.sub("", s).strip()
    return s


def _apply_typo_fixes(s: str) -> str:
    """Apply common typos (e.g. OCR 'At lanta' -> 'Atlanta') to any display string."""
    if not s:
        return s
    for wrong, right in _INSTITUTION_TYPO_FIXES:
        s = re.sub(re.escape(wrong), right, s, flags=re.IGNORECASE)
    return s


def _normalize_text_for_display(s: str | None) -> str | None:
    """Restore spaces in concatenated text, strip delimiters and noise. Use for all string outputs."""
    if not s or not s.strip():
        return s
    t = fix_concatenated_words(s.strip())
    t = _strip_delimiter_artifacts(t)
    t = _strip_noise_from_field(t)
    t = _apply_typo_fixes(t)
    return t if t else s


class EducationParser:
    def parse(self, text: str) -> list[EducationEntry]:
        # Strip PDF (cid:NN) artifacts so e.g. "(cid:17) Karpagam College" -> " Karpagam College"
        text = _CID_RE.sub(" ", text)
        # Normalize bullet/symbol before institution (½, ·, •) to a single space so "2020 ½ Karpagam" is parseable
        text = re.sub(r"([\d\s\-–—])\s*[½·•]\s*", r"\1 ", text)
        # Normalize input: restore spaces in concatenated words (PDF/OCR often strip spaces)
        text = fix_concatenated_words(text)
        blocks = self._split_blocks(text)
        entries: list[EducationEntry] = []
        for block in blocks:
            entry = self._parse_block(block)
            if entry:
                entries.append(entry)

        # Post-parse merge: merge adjacent entries where one has institution
        # but no degree and the other has degree but no institution.
        entries = self._merge_adjacent_entries(entries)
        return entries

    # ------------------------------------------------------------------
    # Block splitting
    # ------------------------------------------------------------------
    def _split_blocks(self, text: str) -> list[str]:
        """Split education text into blocks, one per degree entry.

        The strategy: a new block starts when we encounter a line that
        contains a degree keyword (bachelor, master, etc.) AND the current
        block already has content.  Lines with only institution names,
        GPA, honors, or minor details are absorbed into the current block.
        """
        # Pre-pass: split a single line that contains two institutions (e.g. "... 2014. Vellore Institute...")
        def split_line_two_institutions(line: str) -> list[str]:
            parts: list[str] = []
            # Match ". " followed by capital and later an institution keyword (start of second entry)
            pattern = r"\.\s+(?=[A-Z][a-z]+[^.]*?\b(?:University|College|Institute|School of|Academy)\b)"
            for i, part in enumerate(re.split(pattern, line)):
                part = part.strip()
                if part:
                    parts.append(part)
            return parts if len(parts) > 1 else [line]

        raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
        lines: list[str] = []
        for line in raw_lines:
            if re.search(r"\b(?:University|College|Institute)\b", line, re.IGNORECASE) and re.search(r"\.\s+[A-Z]", line):
                for part in split_line_two_institutions(line):
                    lines.append(part)
            else:
                lines.append(line)
        if not lines:
            return [text] if text.strip() else []

        blocks: list[str] = []
        current: list[str] = []

        for line in lines:
            is_degree_line = bool(_DEGREE_LINE_RE.search(line))
            is_degree_label = bool(re.match(r"^\s*degree\s*:", line, re.IGNORECASE))
            current_text = "\n".join(current) if current else ""
            current_has_degree = bool(_DEGREE_LINE_RE.search(current_text)) if current_text else False
            current_has_institution = (
                any(kw in current_text.lower() for kw in _INSTITUTION_KEYWORDS)
                if current_text else False
            )
            # New block when this line looks like a second institution (e.g. "Vellore Institute... Bachelors")
            # ENTERPRISE FIX: Don't split if the current line or previous line ends with 'of' or 'at'
            # (handles "University of \n Colorado Boulder")
            prev_line_ends_with_prep = bool(current and current[-1].lower().endswith((" of", " at")))
            line_starts_with_prep = bool(line.lower().startswith(("of ", "at ")))

            line_starts_with_institution = bool(
                re.match(r"^[A-Za-z][a-z]+.*?\b(?:University|College|Institute|School of|Academy)\b", line)
            )
            is_second_institution_line = (
                bool(current)
                and current_has_institution
                and not prev_line_ends_with_prep
                and not line_starts_with_prep
                and (
                    (current_has_degree and not is_degree_line and not is_degree_label)
                    or (line_starts_with_institution and _DEGREE_LINE_RE.search(line))
                )
                and bool(re.search(
                    r"\b(?:University|College|Institute|School of|Academy)\b",
                    line,
                    re.IGNORECASE,
                ))
            )
            if is_second_institution_line:
                blocks.append(current_text)
                current = [line]
            elif (is_degree_line or is_degree_label) and current and current_has_degree:
                blocks.append(current_text)
                current = [line]
            elif (is_degree_line or is_degree_label) and current:
                current.append(line)
            else:
                current.append(line)

        if current:
            blocks.append("\n".join(current))
        return blocks or [text]

    # ------------------------------------------------------------------
    # Post-parse merge
    # ------------------------------------------------------------------
    def _merge_adjacent_entries(self, entries: list[EducationEntry]) -> list[EducationEntry]:
        """Merge adjacent entries when one has degree but no institution
        and the neighboring one has institution but no degree."""
        if len(entries) < 2:
            return entries

        merged: list[EducationEntry] = []
        skip_next = False
        for i in range(len(entries)):
            if skip_next:
                skip_next = False
                continue

            current = entries[i]
            if i + 1 < len(entries):
                nxt = entries[i + 1]
                # Case 1: current has degree but no institution, next has institution but no degree
                if current.degree and not current.institution and nxt.institution and not nxt.degree:
                    merged.append(self._combine_entries(current, nxt))
                    skip_next = True
                    continue
                # Case 2: current has institution but no degree, next has degree but no institution
                if current.institution and not current.degree and nxt.degree and not nxt.institution:
                    merged.append(self._combine_entries(nxt, current))
                    skip_next = True
                    continue

            merged.append(current)

        return merged

    def _combine_entries(self, degree_entry: EducationEntry, inst_entry: EducationEntry) -> EducationEntry:
        """Combine two entries, preferring the degree_entry for degree/field/dates
        and inst_entry for institution. Merge all other fields."""
        return EducationEntry(
            institution=inst_entry.institution or degree_entry.institution,
            degree=degree_entry.degree or inst_entry.degree,
            field_of_study=degree_entry.field_of_study or inst_entry.field_of_study,
            start_date=degree_entry.start_date or inst_entry.start_date,
            end_date=degree_entry.end_date or inst_entry.end_date,
            gpa=degree_entry.gpa or inst_entry.gpa,
            honors=degree_entry.honors or inst_entry.honors,
            in_progress=degree_entry.in_progress or inst_entry.in_progress,
            confidence=max(degree_entry.confidence, inst_entry.confidence),
        )

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

        institution = self._clean_institution_for_display(institution)
        # ENTERPRISE FIX: If institution is a date artifact ("- 2018"), reject it
        if institution and re.match(r"^[-–—]?\s*\d{4}\s*\.?$", institution.strip()):
            institution = None
        field = self._normalize_field_of_study(field, degree, institution)
        # Normalize all string outputs: restore spaces in concatenated text, strip pipes/noise (multi-format/PDF-safe)
        institution = _normalize_text_for_display(institution)
        degree = _normalize_text_for_display(degree)
        field = _normalize_text_for_display(field)
        honors = _normalize_text_for_display(honors)
        # Never emit the literal placeholder "Institution" as institution name
        if institution and institution.strip().lower() == "institution":
            institution = None

        # When resume has no education section, avoid emitting a placeholder entry
        if institution is None and degree and degree.strip().lower() == "degree":
            return None
        # Reject entry with no institution and only a short acronym as field (e.g. "EMR" from unrelated text)
        if institution is None and field and len(field.strip()) <= 4 and not (gpa or honors or (start or end)):
            return None
        # Reject entry with only dates (no institution, degree, or field) — e.g. date picked up from experience
        if not institution and not degree and not field:
            return None
        # ENTERPRISE FIX: Reject ghost entries that have ONLY dates and no substantive content
        # (prevents 2013-2015 date-only rows from secondary education sections)
        if not degree and not field and not gpa and not honors and institution is None:
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

    def _clean_institution_for_display(self, inst: str | None) -> str | None:
        """Ensure institution contains only the institution name, not degree text, Graduated:, Thesis:, etc."""
        if not inst or not inst.strip():
            return inst
        s = inst.strip()
        # ENTERPRISE FIX: Reject pure date-artifact strings like "- 2018"
        if re.match(r"^[-–—]?\s*\d{4}\s*\.?$", s):
            return None
        # Fix common typos (e.g. truncation "Technoloav")
        for wrong, right in _INSTITUTION_TYPO_FIXES:
            s = re.sub(re.escape(wrong), right, s, flags=re.IGNORECASE)
        # ENTERPRISE FIX: Strip duplicate "| Graduated: Month YYYY" patterns (appears when single-line has two Graduated markers)
        s = re.sub(r"(\|\s*Graduated\s*:\s*[A-Za-z]*\s*\d{4})(?:\s*\|\s*Graduated\s*:\s*[A-Za-z]*\s*\d{4})+", r"\1", s, flags=re.IGNORECASE)
        # ENTERPRISE FIX: Strip all "| Graduated: ..." entries from institution (should be in end_date, not institution)
        s = re.sub(r"\s*\|?\s*Graduated\s*:\s*[A-Za-z]*\s*\d{4}\s*", " ", s, flags=re.IGNORECASE).strip()
        # ENTERPRISE FIX: Strip trailing GPA from institution
        s = re.sub(r"\s*\|\s*(?:CG?PA|GPA)\s*[:\s]*[\d./]+[%]?\.?\s*$", "", s, flags=re.IGNORECASE).strip()
        # ENTERPRISE FIX: Strip trailing pipe+location chain ("| Meerut, Uttar Pradesh - |")
        for _ in range(3):
            prev = s
            s = re.sub(r"\s*[|]\s*[A-Za-z][A-Za-z\s,.-]*(?:,\s*[A-Za-z]{2,})?\s*$", "", s).strip()
            s = re.sub(r"\s*[-–—]\s*$", "", s).strip()
            if s == prev:
                break
        # Strip trailing "Graduated: ...", "Thesis: ...", "Specialization in ...", "Honors: ..."
        s = _INSTITUTION_STOP_RE.sub("", s).strip()
        # If line starts with degree keyword, keep only from (last) University/College/Institute and optional preceding name
        if _DEGREE_START_RE.match(s):
            pattern = r"\b(" + "|".join(re.escape(k) for k in _INSTITUTION_KEYWORDS) + r")\b"
            matches = list(re.finditer(pattern, s, re.IGNORECASE))
            if matches:
                m = matches[-1]
                start_idx = m.start()
                rev = s[:start_idx].rstrip()
                # Include up to 8 preceding words if they look like institution name (e.g. "Georgia", "Leeds School", "Technology Management")
                if rev and len(rev.split()) <= 8 and not _DEGREE_START_RE.match(rev):
                    start_idx = 0
                else:
                    # Include leading capitalized words that might be part of the name
                    rev_parts = rev.split()
                    lookback = 0
                    for part in reversed(rev_parts):
                        if part[0].isupper() or part.lower() in {"of", "at", "in", "for", "&", "and", "the"}:
                            lookback += 1
                        else:
                            break
                    if lookback > 0:
                        if lookback < len(rev_parts):
                            start_idx = len(" ".join(rev_parts[:-lookback])) + 1
                        else:
                            # rev is all degree/field words (e.g. "Bachelor of Science in Computer Science Purdue"); keep only from last institution name word
                            _DEGREE_FIELD_WORDS = {
                                "bachelor", "master", "of", "in", "science", "arts", "engineering",
                                "technology", "computer", "business", "administration", "&",
                            }
                            start_idx = 0
                            for i in range(len(rev_parts) - 1, -1, -1):
                                w = rev_parts[i].lower().rstrip(".'")
                                if w not in _DEGREE_FIELD_WORDS and len(w) > 1:
                                    pos = s.find(rev_parts[i])
                                    if pos >= 0:
                                        start_idx = pos
                                        break
                    else:
                        # Fallback: at least the last word
                        last_word_start = rev.rfind(" ") + 1 if " " in rev else 0
                        start_idx = last_word_start
                s = s[start_idx:].strip()
        # Strip trailing " - YYYY." or " - City, ST" that might remain
        s = re.sub(r"\s*[-–—]\s*\d{4}\s*\.?\s*$", "", s).strip()
        # ENTERPRISE FIX: Only strip " - City, ST" if it follows a DASH or PIPE
        s = re.sub(r"\s*[-–—|]\s*[A-Za-z\s,]{4,}\s*$", "", s).strip()
        # Strip leading degree/field words wrongly prepended to institution (e.g. "Engineering University of Texas" -> "University of Texas at Austin")
        # ENTERPRISE FIX: Broader strip but stop if University/College keyword is found anywhere in the line
        # This prevents stripping "University of" from "Technology Management University of..."
        while _INSTITUTION_LEADING_STOP.match(s) or re.match(r"^\s*(?:Emphasis|Major|Concentration|Focus)\s+(?:in|of)\s+", s, re.IGNORECASE):
            # If word is a keyword, don't strip it if it's the start of the core name
            if re.match(r"^\s*(?:University|College|Institute|School of|Academy)\b", s, re.IGNORECASE):
                break
            # Also don't strip if stripping would leave a name fragment (e.g. "of Colorado Boulder")
            if re.match(r"^\s*(?:of|at|in|for)\s+", s, re.IGNORECASE):
                break
                
            s = re.sub(r"^\s*(?:Emphasis|Major|Concentration|Focus)\s+(?:in|of)\s+", "", s, flags=re.IGNORECASE).strip()
            s = _INSTITUTION_LEADING_STOP.sub("", s, count=1).strip()
        return s if s and len(s) > 2 else inst

    def _normalize_field_of_study(
        self, field: str | None, degree: str | None, institution: str | None = None
    ) -> str | None:
        """Remove redundant degree word from field; strip institution name when duplicated in field."""
        if not field:
            return field
        f = field.strip()
        # Strip trailing/leading dashes and garbage like "- - B" (e.g. from "B.Tech (Computer Science)" misparse)
        f = re.sub(r"\s*[-–—]\s*$", "", f).strip()
        f = re.sub(r"^\s*[-–—]\s*", "", f).strip()
        if re.match(r"^[-–—]\s*\w*\s*$", f) or (len(f) <= 3 and f[0] in "-–—"):
            return None
        # Strip institution name and location from end of field (e.g. "Computer Science Purdue University - West Lafayette" -> "Computer Science")
        if institution:
            inst_kw = re.search(r"\b(?:University|College|Institute|School)\b", institution, re.IGNORECASE)
            if inst_kw:
                core_inst = institution[:inst_kw.end()].strip()
                f = re.sub(re.escape(core_inst), "", f, flags=re.IGNORECASE).strip().rstrip("&,.-")
            # Also strip the whole institution if it's there
            f = re.sub(re.escape(institution), "", f, flags=re.IGNORECASE).strip().rstrip("&,.-")
            # Strip trailing first word(s) of institution when field accidentally ends with it (e.g. "Computer Science Purdue" -> "Computer Science")
            inst_parts = institution.split()
            if inst_parts and len(f) > 3:
                first_word = inst_parts[0]
                if len(first_word) >= 2 and first_word.isalnum():
                    f = re.sub(r"\s+" + re.escape(first_word) + r"\s*$", "", f, flags=re.IGNORECASE).strip()
        
        # ENTERPRISE FIX: Specific check for honors leakage
        if re.search(r"\b(?:All Semesters|Dean'?s List|Honors|Distinction)\b", f, re.IGNORECASE):
            return None
            
        # Strip trailing "X University - City" or "University of X - City" when not the institution param
        f = re.sub(
            r"\s+(?:[A-Za-z]+\s+)?(?:University|College|Institute)\s+[A-Za-z\s&.,'()-]*(?:\s*[-–—]\s*[A-Za-z\s,]+)?\s*$",
            "", f, flags=re.IGNORECASE,
        ).strip()
        if not f:
            return field
        if not degree:
            return f
        d = degree.lower()
        # Strip leading "Technology " when degree already contains Technology/B.Tech
        if ("technology" in d or "b.tech" in d or "btech" in d) and re.match(r"^technology\s+", f, re.IGNORECASE):
            f = re.sub(r"^technology\s+", "", f, flags=re.IGNORECASE).strip()
        # Strip leading "Engineering " when degree already contains Engineering/B.E/M.Tech etc.
        if ("engineering" in d or "b.e" in d or "m.tech" in d) and re.match(r"^engineering\s+", f, re.IGNORECASE):
            f = re.sub(r"^engineering\s+", "", f, flags=re.IGNORECASE).strip()
        return f if f else field

    def _extract_institution(self, text: str) -> str | None:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        # Pass 0: labeled lines "College: MRCET", "University: X"
        for line in lines:
            label_match = re.match(
                r"^\s*(?:college|university|institution|school|institute)\s*:\s*(.+)",
                line,
                re.IGNORECASE,
            )
            if label_match:
                value = label_match.group(1).strip().rstrip(".,").strip()
                if value and len(value) > 1 and value.lower() != "institution":
                    return value
        # Pass 0b: "College: MRCET" anywhere in block (allow newlines after colon; capture until newline, 2+ spaces, or GPA)
        college_in_text = re.search(
            r"(?:^|\s)(?:College|University|Institution)\s*:\s*(?:\s|\n)*([A-Za-z][^\n]+?)(?=\s*\n|\s{2,}|\bGPA\b|$)",
            text,
            re.IGNORECASE,
        )
        if college_in_text:
            value = college_in_text.group(1).strip().rstrip(".,").strip()
            if value and len(value) > 1 and value.lower() != "institution":
                return value

        # Pass 0c: line starts with year or year range then institution (e.g. "2016 – 2020  Karpagam College", "2016  S.B.O.A MHSS CBE")
        for line in lines:
            m = re.match(r"^\s*\d{4}(?:\s*[-–—]\s*\d{4})?\s{1,}(.+)$", line)
            if m:
                candidate = m.group(1).strip().rstrip(".,")
                if len(candidate) > 3 and not re.match(r"^\d", candidate) and candidate.lower() != "institution":
                    return candidate

        # Pass 1: "from <Institution>" e.g. "from Gokaraju Rangaraju Institute of Engineering & Technology"
        from_match = re.search(
            r"\bfrom\s+([A-Za-z][A-Za-z0-9\s&.,'()\-]+?(?:"
            + "|".join(re.escape(k) for k in _INSTITUTION_KEYWORDS)
            + r")[A-Za-z0-9\s&.,'()\-]*)",
            text,
            re.IGNORECASE,
        )
        if from_match:
            inst = from_match.group(1).strip()
            inst = re.sub(r"\s*[-–—]\s*\d{4}\s*\.?\s*$", "", inst).strip().rstrip(".,")
            if len(inst) > 3 and inst.lower() != "institution":
                return inst

        # Pass 2: TOP_UNIVERSITIES and lines with institution keywords
        for line in lines:
            lowered = line.lower()
            for top_uni in TOP_UNIVERSITIES:
                if top_uni in lowered:
                    cleaned = self._clean_institution_line(line)
                    if cleaned and cleaned.lower() != "institution":
                        return cleaned

        # Pass 3: lines with institution keywords (university, college, institute, etc.)
        for line in lines:
            lowered = line.lower()
            if any(kw in lowered for kw in _INSTITUTION_KEYWORDS):
                if _DEGREE_LINE_RE.search(line):
                    inst = self._extract_inline_institution(line)
                    if inst and inst.lower() != "institution":
                        return inst
                    inst = self._extract_institution_from_degree_line(line)
                    if inst:
                        return inst
                    continue
                cleaned = self._clean_institution_line(line)
                # ENTERPRISE FIX: If name ends in 'of' or 'at', it's likely split across lines
                if re.search(r"\b(?:of|at)\s*$", cleaned, re.IGNORECASE):
                    current_idx = -1
                    for idx, candidate_line in enumerate(lines):
                        if candidate_line.strip() == line.strip():
                            current_idx = idx
                            break
                    if current_idx != -1 and current_idx + 1 < len(lines):
                        next_line = lines[current_idx + 1]
                        # Don't append if next line STARTS with a year or degree
                        if not re.match(r"^\s*(?:19|20)\d{2}\b", next_line) and not _DEGREE_LINE_RE.search(next_line):
                            # Append the name part of the next line (don't split by dash here, keep name like Colorado Boulder - Leeds)
                            name_part = next_line.strip().split("|")[0].strip()
                            if name_part:
                                cleaned += " " + name_part

                if (
                    len(cleaned) > 5
                    and not re.match(r"^\d{4}$", cleaned)
                    and cleaned.strip().lower() != "institution"
                ):
                    return cleaned

        # Pass 4: any line or span containing institution keyword (avoid generic "Institution")
        candidate = self._extract_institution_from_any_line(text)
        if candidate and candidate.lower() != "institution":
            return candidate
        return None

    def _extract_inline_institution(self, line: str) -> str | None:
        """Extract institution from within a line like
        'Bachelor of Technology in CS at Koneru Lakshmaiah University 2010-2014'
        """
        match = re.search(
            r"\bat\s+([A-Z][A-Za-z\s&,.'()-]+(?:"
            + "|".join(re.escape(kw) for kw in _INSTITUTION_KEYWORDS)
            + r")[A-Za-z\s&,.'()-]*)",
            line,
            re.IGNORECASE,
        )
        if match:
            inst = match.group(1).strip()
            inst = re.sub(r"\s+\d{4}\s*[-–—]\s*\d{4}\s*$", "", inst).strip()
            inst = re.sub(r"\s+\d{4}\s*$", "", inst).strip()
            inst = inst.rstrip(".,").strip()
            if inst and len(inst) > 3 and inst.lower() != "institution":
                return inst
        return None

    def _extract_institution_from_degree_line(self, line: str) -> str | None:
        """When degree and institution are on same line (e.g. '... MLWE college - June 2010'),
        extract the institution part; include preceding name (e.g. 'MLWE college')."""
        # Prefer "X college" / "X university" (include " of Y at Z" after keyword), then strip trailing dates
        pattern_with_prefix = (
            r"\b([A-Za-z][A-Za-z0-9\s&.,'()\-]*?\s+(?:"
            + "|".join(re.escape(k) for k in _INSTITUTION_KEYWORDS)
            + r")[A-Za-z0-9\s&.,'()\-]*?)(?=\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-/.]*\d{0,4}|\s+Graduated\s*:|\s*\d{4}\s*$|$)"
        )
        matches = list(re.finditer(pattern_with_prefix, line, re.IGNORECASE))
        if not matches:
            pattern = (
                r"(\b(?:"
                + "|".join(re.escape(k) for k in _INSTITUTION_KEYWORDS)
                + r")\b[A-Za-z0-9\s&.,'()\-]*)"
            )
            matches = list(re.finditer(pattern, line, re.IGNORECASE))
        if not matches:
            return None
        inst = matches[-1].group(1).strip()
        inst = re.sub(r"\s+Graduated\s*:.*$", "", inst, flags=re.IGNORECASE).strip()
        inst = re.sub(r"\s*\|\s*[A-Za-z\s,]+$", "", inst).strip()
        inst = re.sub(
            r"\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-/.]*\d{0,4}(\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-/.]*\d{0,4})?\s*$",
            "", inst, flags=re.IGNORECASE,
        ).strip()
        inst = re.sub(r"\s+\d{4}\s*[-–—]\s*\d{4}\s*$", "", inst).strip()
        inst = re.sub(r"\s+\d{4}\s*$", "", inst).strip()
        inst = inst.rstrip(".,").strip()
        if len(inst) > 5 and inst.lower() != "institution":
            return inst
        return None

    def _extract_institution_from_any_line(self, text: str) -> str | None:
        """Scan full text for any phrase containing institution keyword (e.g. 'University of Washington')."""
        # Match phrases like "University of Washington", "Georgia Institute of Technology"
        pattern = (
            r"\b([A-Za-z][A-Za-z0-9\s&.,'()\-]*(?:"
            + "|".join(re.escape(k) for k in _INSTITUTION_KEYWORDS)
            + r")[A-Za-z0-9\s&.,'()\-]*)\b"
        )
        best: str | None = None
        for m in re.finditer(pattern, text, re.IGNORECASE):
            cand = m.group(1).strip()
            # ENTERPRISE FIX: Reject candidates starting with dash/pipe (date artifacts like "- 2018")
            if re.match(r"^[-–—|]", cand):
                continue
            cand = re.sub(r"\s+Graduated\s*:.*$", "", cand, flags=re.IGNORECASE).strip()
            # ENTERPRISE FIX: Strip all pipe-separated suffixes (| Graduated: ..., | City, ST)
            cand = re.sub(r"\s*\|.*$", "", cand).strip()
            cand = re.sub(r"\s*[-–—]\s*[A-Za-z\s,]+$", "", cand).strip()  # " – Seattle, WA"
            # Strip trailing date parts: " - June 2010 - July 2014" or " - June 2010 - July"
            cand = re.sub(
                r"\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-/.]*\d{0,4}(\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-/.]*\d{0,4})?\s*$",
                "", cand, flags=re.IGNORECASE,
            ).strip()
            cand = cand.rstrip(".,").strip()
            if not cand or cand.lower() == "institution" or len(cand) < 6:
                continue
            if re.match(r"^\d", cand) or re.search(r"\d{4}\s*[-–—]\s*\d{4}", cand):
                continue
            # Prefer names that don't look like date fragments (e.g. "college - June 2010 - July")
            if re.search(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b", cand, re.IGNORECASE):
                continue
            if best is None or len(cand) > len(best):
                best = cand
        return best

    def _clean_institution_line(self, line: str) -> str:
        """Clean an institution line by removing label prefixes and trailing dates.
        Uses a safer date-stripping approach that won't eat institution names."""
        cleaned = line.strip()
        # Reject pure date-artifact lines like "- 2018" or "- 2025"
        if re.match(r"^[-–—]\s*\d{4}\s*$", cleaned):
            return ""
        # Remove bullet markers
        cleaned = re.sub(r"^[•·▪\-\*]\s*", "", cleaned).strip()
        # Remove label prefix like "College:", "University:", "Institution:"
        cleaned = _INSTITUTION_PREFIX_RE.sub("", cleaned).strip()
        # ENTERPRISE FIX: Strip "| GPA: X" or "| GPA: X/Y" from institution line
        cleaned = re.sub(r"\s*\|\s*(?:CG?PA|GPA)\s*[:\s]*[\d./]+[%]?\.?\s*$", "", cleaned, flags=re.IGNORECASE).strip()
        # ENTERPRISE FIX: Strip trailing "- | City, ST" or "- | Location" chains (pipe+dash combos)
        cleaned = re.sub(r"\s*[-–—]\s*\|\s*[A-Za-z][A-Za-z\s,]+\s*$", "", cleaned).strip()
        # ENTERPRISE FIX: Strip trailing " | City, ST" multiple times (handles double-pipes)
        for _ in range(3):
            prev = cleaned
            cleaned = re.sub(r"\s*\|\s*[A-Za-z][A-Za-z\s,.-]*(?:,\s*[A-Za-z]{2,})?\s*$", "", cleaned).strip()
            if cleaned == prev:
                break
        # ENTERPRISE FIX: Strip remaining trailing " - " when nothing follows
        cleaned = re.sub(r"\s*[-–—]\s*$", "", cleaned).strip()
        # Remove trailing "Graduated: YYYY" or "Graduated:"
        cleaned = re.sub(r"\s+Graduated\s*:\s*\d*\s*$", "", cleaned, flags=re.IGNORECASE).strip()
        # Remove trailing " – 2014." or " - 2014." (single year with dash)
        cleaned = re.sub(r"\s*[-–—]\s*\d{4}\s*\.?\s*$", "", cleaned).strip()
        # Remove trailing standalone month (e.g. "Vellore July" when July is date part -> "Vellore")
        cleaned = re.sub(
            r"\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*$",
            "", cleaned, flags=re.IGNORECASE,
        ).strip()
        # Remove trailing month-year to month-year (with hyphen in month-year e.g. July-2010)
        cleaned = re.sub(
            r"\s*,?\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z\-]*\s*\d{2,4}"
            r"\s*(?:to|[-–—])\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?[a-z\-]*\s*\d{2,4}\s*$",
            "", cleaned, flags=re.IGNORECASE,
        ).strip()
        # Remove trailing standalone year ranges (e.g., "2010-2014", "2010 - 2014")
        cleaned = re.sub(r"\s+\d{4}\s*[-–—]\s*\d{4}\s*$", "", cleaned).strip()
        # Remove trailing standalone years (e.g., "2014")
        cleaned = re.sub(r"\s+\d{4}\s*\.?\s*$", "", cleaned).strip()
        # Remove trailing month-year date patterns (e.g., "Aug 2010 – May 2014")
        cleaned = re.sub(
            r"\s*,?\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}"
            r"\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}\s*$",
            "", cleaned, flags=re.IGNORECASE,
        ).strip()
        # Remove trailing commas and periods
        cleaned = cleaned.rstrip(".,").strip()
        return cleaned

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
            if not re.search(rf"\b{re.escape(abbr)}\b", lowered):
                continue
            # Do not treat "MIT" as "Master of Information Technology" when it's institution abbreviation (e.g. "(MIT), Cambridge")
            if abbr in ("mit", "m.i.t.", "m.i.t") and re.search(r"\(\s*mit\s*\)|,\s*mit\s*,|mit\s*,", lowered):
                continue
            return full

        # Expanded allowed markers for degree identification
        allowed_markers = (
            "bachelor", "bachelors", "bachelor's", "b.a.", "b.s.", "b.sc.",
            "undergraduate", "u.g.",
            "master", "masters", "master's", "m.a.", "m.s.", "m.sc.",
            "postgraduate", "p.g.",
            "doctorate", "phd", "ph.d.", "doctoral", "d.phil",
            "associate", "assoc.", "a.a.", "a.s.",
            "diploma", "advanced diploma", "pgd", "post graduate diploma",
            "certificate", "certification", "cert.",
            "high school", "higher secondary", "senior secondary", "secondary",
            "graduate", "grad",
            "professional", "professional degree",
            "licentiate", "fellow", "fellowship",
            "mba", "mca", "mtech", "btech",
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

            # Use word-boundary regex to avoid substring matches
            # (e.g., "ug" matching inside "Douglas")
            if re.search(rf"\b{re.escape(keyword_l)}\b", lowered):
                # ENTERPRISE FIX: Reject generic placeholder "Degree"
                if keyword_l == "degree" or keyword_l.lower() == "degree":
                    continue
                return keyword.title()

        # Pattern-based extraction for common degree formats
        degree_patterns = [
            # "Bachelor of Science" style with optional field
            r"\b(bachelor|master|doctor)(?:'?s)?\s+of\s+(science|arts|engineering|business|medicine|laws?|philosophy|education|fine arts|social work|public health)\b",
            # "Associate in Arts" style
            r"\b(associate)(?:'?s)?\s+(?:of|in)\s+(science|arts|applied science|business)\b",
            # B.Sc., M.Sc., Ph.D. style with period
            r"\b([BbMmDdPp])\.([A-Z][a-z]+\.?)\b",
        ]

        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).title()

        # MBA, MCA, BBA, MBBS style (2-5 letter acronyms starting with B, M, P, D)
        # ONLY return if the match is a known degree acronym to avoid false positives like "Doe"
        acronym_match = re.search(r"\b([BMPD][A-Z]{1,4})\b", text)
        if acronym_match:
            common_degrees = {
                "MBA", "MCA", "BBA", "BCA", "MBBS", "MD", "MS",
                "LLB", "LLM", "BSC", "MSC", "BE", "ME", "BTECH", "MTECH",
                "MA", "BA", "PHD", "DBA", "MPA", "MPH", "MSW", "MFA",
            }
            if acronym_match.group(1).upper() in common_degrees:
                # ENTERPRISE FIX: Additional blacklist for "Degree" placeholder
                if acronym_match.group(1).upper() == "DEGREE":
                    return None
                return acronym_match.group(1).upper()

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
        """Extract field of study from text. Strips trailing date fragments and month names."""
        # Parenthetical field e.g. "B.Tech (Computer Science)" — prefer field-like content over institution abbrev (JNTUH) or institution name (Scheller College of Business)
        for paren_match in re.finditer(r"\(\s*([A-Za-z][A-Za-z\s&/\-]{2,50})\s*\)", text):
            f = paren_match.group(1).strip()
            if re.match(r"^(?:MBA|B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?S|M\.?S|B\.?A|M\.?A|Ph\.?D|B\.?Sc|M\.?Sc|LLB|LLM|MBBS|JNTUH|JNTU|IIT|AIIMS)$", f, re.IGNORECASE):
                continue
            # Reject institution-style paren (e.g. "Scheller College of Business")
            if re.search(r"\b(?:College|School|Institute|University|Academy)\s+of\b", f, re.IGNORECASE):
                continue
            if len(f) > 2 and not re.match(r"^[-–—]?\s*\w\s*$", f):
                if re.search(r"\b(?:computer|science|engineering|arts|commerce|technology|mathematics|statistics)\b", f, re.IGNORECASE) or len(f.split()) <= 6:
                    return f
        # "BACHELOR OF SCIENCE IN X WITH MINORS IN Y" or "Minor in X" — capture main field and append minors to honors later
        with_minors = re.search(
            r"\b(?:bachelor|master|b\.?s|m\.?s|b\.?a|m\.?a)\s+(?:of\s+)?\w+\s+in\s+([A-Za-z\s&,]+?)\s+with\s+minors?\s+in\s+([A-Za-z\s,&]+?)(?=\s*Expected|\s*\d{4}|\s*$|\n)",
            text,
            re.IGNORECASE,
        )
        if with_minors:
            main = with_minors.group(1).strip().rstrip(".,")
            if len(main) > 2:
                return main
        # "Bachelor of Technology in X - " or "B.Tech in X - " (field before institution on same line)
        btech_in_dash = re.search(
            r"\b(?:b\.?tech|bachelor\s+of\s+technology)\s+in\s+([A-Za-z\s&,/\-]+?)\s*[-–—]\s*(?=[A-Z])",
            text,
            re.IGNORECASE,
        )
        if btech_in_dash:
            field = btech_in_dash.group(1).strip().rstrip(".,")
            if 2 <= len(field.split()) <= 12 and len(field) > 3:
                if not re.search(r"\b(?:All Semesters|Dean'?s List|Honors|Distinction)\b", field, re.IGNORECASE):
                    return field
        # Degree: Field form e.g. "Bachelor of Technology: Computer Science Engineering"
        colon_match = re.search(
            r"\b(?:bachelor|master|b\.?tech|m\.?tech|degree)\s+(?:of\s+)?\w+\s*:\s*([A-Za-z][A-Za-z\s&./\-]+?)(?:\s+from\s+|\s*[-–—]\s*|\s*\(|\s*$)",
            text,
            re.IGNORECASE,
        )
        if colon_match:
            field = colon_match.group(1).strip()
            field = re.split(r"\b(19\d{2}|20\d{2})\b", field)[0].strip().rstrip(".,")
            field = _TRAILING_MONTH_RE.sub("", field).strip()
            if 2 <= len(field.split()) <= 12 and len(field) > 3:
                return field
        # "BACHELOR OF SCIENCE IN Computer Science" — stop AT the institution keyword (not after it)
        # ENTERPRISE FIX: Use institution-keyword as hard stop so field never includes university name
        _INST_KW_STOP = r"(?:University|College|Institute|School\s+of|Academy|Polytechnic)"
        in_field = re.search(
            r"\b(?:bachelor|master)\s+of\s+(?:science|arts|engineering)\s+in\s+([A-Za-z\s&,/\-]+?)\s+" + _INST_KW_STOP + r"\b",
            text,
            re.IGNORECASE,
        )
        if not in_field:
            # Fallback: capture up to EOL/digit/with-minors without institution keywords
            in_field = re.search(
                r"\b(?:bachelor|master)\s+of\s+(?:science|arts|engineering)\s+in\s+([A-Za-z\s&,/\-]+?)(?:\s+with\s+minors|\s*Expected|\s*\d{4}|\s*$|\n)",
                text,
                re.IGNORECASE,
            )
        if in_field:
            field = in_field.group(1).strip().rstrip(".,")
            # Final safety strip of any remaining university keyword tail
            m_inst = re.search(r"\b(?:University|College|Institute)\b", field, re.IGNORECASE)
            if m_inst:
                field = field[:m_inst.start()].strip().rstrip("&,.-")
            if 1 <= len(field.split()) <= 15 and len(field) > 2:
                # ENTERPRISE FIX: Blacklist honors noise from field
                if re.search(r"\b(?:All Semesters|Dean'?s List|Honors|Distinction|First Class)\b", field, re.IGNORECASE):
                    field = None
                if field:
                    # Strip trailing abbreviations like "- PSG", "- IIT", "- MIT"
                    field = re.sub(r"\s*[-–—]\s*[A-Z]{2,6}\s*$", "", field).strip()
                    return field
        field_patterns = [
            r"\b(?:in|major in|specialization in|concentration in|focus in|emphasis in)\s+([A-Za-z &/\-]+)",
            r"\b(?:degree|bachelor|master|diploma)\s+(?:of|in)\s+([A-Za-z &/\-]+)",
            r"\b(?:b\.?tech|b\.?e|m\.?tech|m\.?e)\s+[.\s\-–—]*([A-Za-z][A-Za-z\s&/\-]{2,40})",  # avoid capturing "B" from "– B.Tech"
        ]
        for i, pattern in enumerate(field_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                field = match.group(1).strip()
                # ENTERPRISE FIX: Truncate at first newline to prevent multi-line contamination
                field = field.split("\n")[0].strip()
                field = re.split(r"\b(19\d{2}|20\d{2})\b|,|\(", field)[0].strip()
                field = re.sub(r"\s+(?:at|from)\s+.*$", "", field, flags=re.IGNORECASE).strip()
                field = _TRAILING_MONTH_RE.sub("", field).strip()
                field = re.sub(r"\s+(?:CGPA|GPA|Graduated)\s*:?\s*.*$", "", field, flags=re.IGNORECASE).strip()
                # ENTERPRISE FIX: Strip trailing university name — find first institution keyword and cut there
                m_inst = re.search(r"\b(?:University|College|Institute)\b", field, re.IGNORECASE)
                if m_inst:
                    field = field[:m_inst.start()].strip().rstrip("&,.-")
                # ENTERPRISE FIX: Strip trailing abbreviations like "- PSG", "- IIT", "- MIT"
                # Use a more flexible regex for abbreviations (2-6 letters)
                field = re.sub(r"\s*[-–—]\s*[A-Z]{2,6}\s*$", "", field).strip()
                if 2 <= len(field.split()) <= 12 and len(field) > 3:
                    # ENTERPRISE FIX: Blacklist honors noise from field (ignore substrings like 'of')
                    if re.search(r"\b(?:All Semesters|Dean'?s List|Honors|Distinction|First Class)\b", field, re.IGNORECASE):
                        continue
                    field = re.sub(r"\s+(and|with|from|at|the|for)$", "", field, flags=re.IGNORECASE)
                    return field.strip()
        return None

    def _extract_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        """Extract start and end dates from text. Supports full ranges, Graduated: YYYY, Expected Mon YYYY, and year-only."""
        in_progress = False

        # 1) "Graduated: 2017" or "Graduated: 2019" → end_date only
        grad_match = GRADUATED_RE.search(text)
        if grad_match:
            y = int(grad_match.group(1))
            end_d = self._clamp_end_date(date(y, 1, 1))
            return None, end_d, False

        # 2) "Expected Dec 2019" or "Expected December 2019" → end_date, in_progress
        expected_match = _EXPECTED_DATE_RE.search(text)
        if expected_match:
            end_raw = expected_match.group(0).replace("Expected", "").strip()
            end_date = self._parse_date(end_raw)
            if end_date:
                return None, self._clamp_end_date(end_date), True

        # 3) Full date range with month names first (e.g. July-2010 to June 2014, Aug. 2018 – May 2021)
        match = _DATE_RANGE_FULL_RE.search(text)
        if not match:
            match = DATE_RANGE_RE.search(text)
        if match:
            start_raw = match.group("start").strip()
            end_raw = match.group("end").strip()
            start_date = self._parse_date(start_raw)
            if end_raw.lower() in {"present", "current", "expected", "ongoing"}:
                in_progress = True
                return start_date, None, True
            end_date = self._parse_date(end_raw)
            if end_date and not in_progress:
                end_date = self._clamp_end_date(end_date)
            return start_date, end_date, False

        # 3) "Year of passed: 2014"
        year_passed = YEAR_PASSED_RE.search(text)
        if year_passed and year_passed.group(1):
            y = int(year_passed.group(1))
            return None, self._clamp_end_date(date(y, 1, 1)), False

        # 4) Fallback: single year or year range
        years = YEAR_RE.findall(text)
        if len(years) >= 2:
            start_year = int(years[0])
            end_year = int(years[-1])
            return date(start_year, 1, 1), self._clamp_end_date(date(end_year, 1, 1)), False
        elif len(years) == 1:
            end_year = int(years[0])
            return None, self._clamp_end_date(date(end_year, 1, 1)), False

        return None, None, False

    def _clamp_end_date(self, d: date) -> date:
        """Prevent future graduation dates; completed education should not show future years."""
        today = date.today()
        if d.year > today.year:
            return date(today.year, min(d.month, 12), min(d.day, 28))
        return d

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
        if parsed:
            return parsed.date()
        # Fallback for "July-2010", "June 2014", "Aug. 2018", "Dec 2019" when dateparser fails (allow period after month)
        month_year = re.match(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z.]*[\s\-/.]*(\d{2,4})",
            value,
            re.IGNORECASE,
        )
        if month_year:
            y = int(month_year.group(1))
            if y < 100:
                y = 2000 + y if y < 50 else 1900 + y
            month_str = value[:3].lower()
            months = "jan feb mar apr may jun jul aug sep oct nov dec".split()
            for i, m in enumerate(months, 1):
                if month_str == m:
                    return date(y, i, 1)
        year_only = re.match(r"^(\d{4})$", value)
        if year_only:
            return date(int(year_only.group(1)), 1, 1)
        return None

    def _extract_gpa(self, text: str) -> str | None:
        """Extract GPA or grade information from text (e.g. Cum. GPA: 4.0 / 4.0)."""
        match = GPA_RE.search(text)
        if not match:
            return None

        # Format: X/Y or X out of Y (prefer preserving decimal e.g. 4.0/4.0)
        gpa_val = match.group("gpa")
        scale_val = match.group("scale")
        if gpa_val and scale_val:
            return f"{gpa_val}/{scale_val}"

        # Format: CGPA/GPA: X.XX / Y.Y with optional scale (Cum. GPA: 4.0 / 4.0)
        scale2 = match.group("scale2")
        cgpa_val = match.group("cgpa_val")
        cgpa_val2 = match.group("cgpa_val2")
        if scale2 and (cgpa_val or cgpa_val2):
            return f"{cgpa_val or cgpa_val2}/{scale2}"
        if cgpa_val:
            return cgpa_val
        if cgpa_val2:
            return cgpa_val2

        # Format: XX%
        if match.group("pct"):
            return f"{match.group('pct')}%"

        return None

    def _extract_honors(self, text: str) -> str | None:
        """Extract honors, thesis, specialization, minors. Combined for description."""
        parts: list[str] = []
        # Full "Honors: ..." line
        for m in HONORS_FULL_RE.finditer(text):
            part = m.group(1).strip().rstrip(".;")
            if part and part not in parts:
                parts.append(part)
        # "Dean's List (All Semesters)" or "Dean's List (Fall 2020)" — capture full phrase
        deans_list = re.search(r"Dean'?s\s+List\s*(?:\([^)]+\))?", text, re.IGNORECASE)
        if deans_list:
            honor = deans_list.group(0).strip().title().replace("'S", "'s")
            if honor not in parts:
                parts.append(honor)
        # "With minors in Mathematics and Statistics" for inclusion in honors when present
        minors_match = re.search(
            r"\bwith\s+minors?\s+in\s+([A-Za-z\s,&]+?)(?=\s*Expected|\s*\d{4}|\s*Cum\.|\s*$|\n)",
            text,
            re.IGNORECASE,
        )
        if minors_match:
            minors_phrase = "Minors: " + minors_match.group(1).strip().rstrip(".,")
            if minors_phrase not in parts:
                parts.append(minors_phrase)
        # "Graduated Cum Laude" / "Graduated Magna Cum Laude" etc.
        graduated_honor = re.search(
            r"Graduated\s+(?:Cum\s+Laude|Magna\s+Cum\s+Laude|Summa\s+Cum\s+Laude)\b",
            text,
            re.IGNORECASE,
        )
        if graduated_honor and graduated_honor.group(0) not in (p for p in parts):
            parts.append(graduated_honor.group(0).strip())
        # Short honor keywords (cum laude, etc.) if not already added
        if not parts or not any(HONORS_RE.search(p) for p in parts):
            match = HONORS_RE.search(text)
            if match:
                honor = match.group(0).strip().title().replace("'S", "'s")
                if honor not in parts:
                    parts.append(honor)
        # Thesis
        thesis_m = THESIS_RE.search(text)
        if thesis_m:
            parts.append('Thesis: "' + thesis_m.group(1).strip().rstrip('"') + '"')
        # Specialization
        spec_m = SPECIALIZATION_RE.search(text)
        if spec_m:
            parts.append("Specialization: " + spec_m.group(1).strip().rstrip(".;"))
        # Research Focus / Focus Areas (multi-format)
        research_focus = re.search(
            r"(?:Research\s+Focus|Focus\s+Areas)\s*:\s*([^\n•·▪\-]+?)(?=\n|•|·|\bHonors\s*:|\bMinor\s*:|\bThesis\s*:|$)",
            text,
            re.IGNORECASE,
        )
        if research_focus:
            phrase = (research_focus.group(0).split(":")[0] + ": " + research_focus.group(1).strip().rstrip(".;")).strip()
            if phrase not in parts:
                parts.append(phrase)
        # Minor: ... (bullet or line)
        minor_match = re.search(
            r"Minor\s*:\s*([^\n•·▪\-;]+?)(?=\n|•|·|;|$)",
            text,
            re.IGNORECASE,
        )
        if minor_match:
            minor_phrase = "Minor: " + minor_match.group(1).strip().rstrip(".,")
            if minor_phrase not in parts:
                parts.append(minor_phrase)
        # "Recipient of the ... Scholarship" / "Recipient of ... Award"
        recipient = re.search(
            r"Recipient\s+of\s+(?:the\s+)?(?:[A-Za-z\s']+(?:Scholarship|Award|Fellowship))\s*\.?",
            text,
            re.IGNORECASE,
        )
        if recipient:
            phrase = recipient.group(0).strip().rstrip(".")
            if phrase not in parts:
                parts.append(phrase)
        if not parts:
            return None
        result = "; ".join(parts)
        # Remove redundant trailing "; Honors" when it adds no information
        result = re.sub(r";\s*Honors\s*$", "", result, flags=re.IGNORECASE).strip()
        return result if result else None

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