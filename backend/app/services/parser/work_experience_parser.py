from __future__ import annotations

import logging
import re
from dataclasses import dataclass, replace
from datetime import date
from typing import Iterable

import dateparser
from app.core.config import get_settings
from app.services.llm_service import LLMParsingService

try:
    import spacy
except ImportError:
    spacy = None


logger = logging.getLogger(__name__)


MONTH_TOKEN = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_TOKEN = (
    r"(?:"
    r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
    r"|\d{4}[/-]\d{1,2}"  # YYYY-MM or YYYY/MM
    r"|\d{1,2}[/-]\d{2}"  # MM/YY
    r"|\d{1,2}[/-]\d{4}"  # MM/YYYY
    r"|\d{4}"  # YYYY
    r"|Q[1-4]\s+\d{4}"  # Q1 2020, Q4 2019
    r"|(?:Spring|Fall|Summer|Winter)\s+\d{4}"  # Seasonal
    rf"|{MONTH_TOKEN}\s*[\'\u2019]\d{{2}}"  # Jan '20, Feb '19
    r"|\d{4}\.\d{2}|\d{2}\.\d{4}"  # 2020.01, 01.2020
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{4}}"  # MMM YYYY
    rf"|{MONTH_TOKEN}\s*[\u2019']\s*\d{{2}}"  # MMM 'YY
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{2}}"  # MMM YY
    r"|\b\d{4}\b" # Standalone 4-digit year
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>{DATE_TOKEN})\s*(?:\s*(?:[-–—→]|to|until|thru|through)\s*)\s*(?P<end>present|current|till\s+date|now|{DATE_TOKEN})",
    re.IGNORECASE,
)

PRESENT_RE = re.compile(r"\b(present|current|till\s+date|now)\b", re.IGNORECASE)
DATE_ANCHOR_RE = re.compile(rf"\b(?:{DATE_TOKEN})\b", re.IGNORECASE)
COMPANY_LINE_RE = re.compile(
    r"(?P<company>.+?)\s*(?:[-–—|,])\s*(?P<title>.+)"
)
# Title at Company (e.g. 'Senior Dev at Acme Corp')
TITLE_AT_COMPANY_RE = re.compile(
    r"^(?P<title>[A-Z][\w\s,\.]+?)\s+at\s+(?P<company>[A-Z][\w\s,\.&]+)$",
    re.IGNORECASE,
)
# Title | Company (pipe-separated, no date)
TITLE_PIPE_COMPANY_RE = re.compile(
    r"^(?P<title>[^|]{3,60})\s*\|\s*(?P<company>[^|]{3,60})$",
)
LOCATION_RE = re.compile(r"\b([A-Za-z .]+,\s*(?:[A-Z]{2,3}|[A-Z][a-z]+(?:\s[A-Z][a-z]+)*))\b")
TITLE_HINT_RE = re.compile(r"\b(engineer|developer|architect|manager|lead|analyst|consultant|director|specialist|scientist|administrator|admin|designer|researcher|expert|lead|head|vp|president|ceo|coo|cto|devops|dev\s*ops)\b", re.IGNORECASE)
# Job title keywords for splitting single-chunk experience (capitalized at line start)
TITLE_SPLIT_KEYWORDS = (
    "engineer", "manager", "developer", "analyst", "designer", "consultant",
    "director", "lead", "specialist", "architect", "coordinator", "administrator",
)
RESPONSIBILITY_MARKERS = {"responsibilities", "key responsibilities", "responsibility"}
COMPANY_HINT_RE = re.compile(r"\b(inc|llc|ltd|corp|corporation|company|technologies|systems|health|bank|solutions|services|labs|group|industries|associates|global|partner|partners|enterprise|ventures|consulting)\b", re.IGNORECASE)
ENVIRONMENT_LINE_RE = re.compile(
    r"^(?:environments?|environment|tools?|technologies|tech\s*stack)\s*[:\-–—]",
    re.IGNORECASE,
)
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
EMAIL_RE = re.compile(r"\b[^\s@]+@[^\s@]+\b")
SOCIAL_RE = re.compile(r"\b(linkedin|github|portfolio)\b", re.IGNORECASE)
EDU_KEYWORD_RE = re.compile(
    r"\b(bachelor|master|ph\s*d|b\.?tech|m\.?tech|b\.?sc|m\.?sc|degree|university|college|school)\b",
    re.IGNORECASE,
)
CERT_KEYWORD_RE = re.compile(r"\b(certified|certification|certificate)\b", re.IGNORECASE)
PLACEHOLDER_ORG_RE = re.compile(
    r"^(company|client|organization|employer|designation|title|role|CKA|CKAD|PMP|CISA|CISM|CISSP|duration|key\s+contributions|responsibilities|summary)\b",
    re.IGNORECASE,
)

LOCATION_BLACKLIST = {
    "india", "usa", "uk", "united states", "america", "canada", "australia",
    "atlanta", "austin", "dallas", "houston", "charlotte", "columbus", "deerfield",
    "bellevue", "redmond", "seattle", "pune", "hyderabad", "bangalore", "bengaluru",
    "chennai", "mumbai", "delhi", "noida", "gurgaon", "gurugram", "new york", "ny",
    "london", "dubai", "singapore", "tokyo", "paris", "berlin", "toronto", "vancouver"
}
CLIENT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(?:end\s+client|client)\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
    re.compile(r"\bproject\s*[:\-–—]\s*(?P<client>.+)$", re.IGNORECASE),
    re.compile(r"\bworked\s+for\s+(?P<client>[A-Za-z0-9][A-Za-z0-9 &.,()/-]{2,})", re.IGNORECASE),
    re.compile(r"\bproject\s+for\s+(?P<client>[A-Za-z0-9][A-Za-z0-9 &.,()/-]{2,})", re.IGNORECASE),
]

CLIENT_HEADER_RE = re.compile(
    r"^(?:end\s+client|client|project)\s*[:\-–—]",
    re.IGNORECASE,
)

LOCATION_MARKER_RE = re.compile(
    r"\(?\b(?:location|loc)\b\s*[:\-–—]\s*(?P<loc>[^\n\r\t\)\|\u2022]{2,120})\)?",
    re.IGNORECASE,
)

LOCATION_TAG_RE = re.compile(r"^(?P<tag>[A-Za-z]{2,20})\)$")

LABELED_ORG_RE = re.compile(
    r"\b(organization|company|employer)\b\s*[:\-–—]\s*(?P<value>.+)$",
    re.IGNORECASE,
)
LABELED_TITLE_RE = re.compile(
    r"\b(designation|title|role|position)\b\s*[:\-–—]\s*(?P<value>.+)$",
    re.IGNORECASE,
)
LABELED_RESP_RE = re.compile(
    r"\b(responsibilities|responsibility|roles?\s*&\s*responsibilities)\b\s*[:\-–—]?\s*(?P<value>.*)$",
    re.IGNORECASE,
)

TITLE_NORMALIZATION = {
    # Seniority
    "sr": "senior",
    "sr.": "senior",
    "sen": "senior",
    "jr": "junior",
    "jr.": "junior",
    "assoc": "associate",
    "asst": "assistant",
    "lead": "lead",
    "principal": "principal",
    "head": "head",
    "exec": "executive",
    "vp": "vice president",
    "svp": "senior vice president",
    "evp": "executive vice president",
    "avp": "assistant vice president",
    "cto": "chief technology officer",
    "ceo": "chief executive officer",
    "coo": "chief operating officer",
    "cfo": "chief financial officer",
    "cpo": "chief product officer",
    "ciso": "chief information security officer",
    "dir": "director",
    "coord": "coordinator",
    "spec": "specialist",
    "cons": "consultant",
    "intern": "intern",
    "trainee": "trainee",
    "stf": "staff",

    # Engineer / Developer
    "swe": "software engineer",
    "sde": "software development engineer",
    "sdet": "software development engineer in test",
    "dev": "developer",
    "engr": "engineer",
    "eng": "engineer",
    "software engr": "software engineer",
    "web dev": "web developer",
    "app dev": "application developer",
    "mob dev": "mobile developer",
    "sys eng": "systems engineer",
    "sys admin": "system administrator",
    "sysadmin": "system administrator",
    "devops eng": "devops engineer",
    "ml eng": "machine learning engineer",
    "ai eng": "artificial intelligence engineer",
    "data eng": "data engineer",
    "sol arch": "solutions architect",
    "sa": "solutions architect",
    "arch": "architect",

    # Managerial
    "mgr": "manager",
    "pm": "project manager",
    "pmo": "project management office",
    "po": "product owner",
    "ba": "business analyst",
    "scrum m": "scrum master",
    "sm": "scrum master",
    "em": "engineering manager",
    "tl": "team lead",
    "tech lead": "technical lead",

    # Tech roles short forms
    "qa": "quality assurance",
    "qe": "quality engineer",
    "ui": "ui",
    "ux": "ux",
    "ui/ux": "ui ux",
    "fe": "frontend",
    "be": "backend",
    "fs": "full stack",
    "hr": "human resources",
    "it": "information technology",
    "dba": "database administrator",
    "db admin": "database administrator",
    "net admin": "network administrator",
    "infosec": "information security",
    "sec eng": "security engineer",
    "cloud eng": "cloud engineer",
    "bi": "business intelligence",
    "ds": "data scientist",
    "da": "data analyst",
    "nlp eng": "natural language processing engineer",
    "cv eng": "computer vision engineer",
    "ios dev": "ios developer",
    "android dev": "android developer",
    "rpa dev": "rpa developer",
    "erp cons": "erp consultant",
    "crm cons": "crm consultant",
}

COMPANY_NORMALIZATION = {
    # Google / Alphabet
    "google inc": "Google",
    "google inc.": "Google",
    "google llc": "Google",
    "google india pvt ltd": "Google",
    "alphabet inc": "Google",
    "alphabet inc.": "Google",
    "google india": "Google",

    # Amazon / AWS
    "amazon.com": "Amazon",
    "amazon inc": "Amazon",
    "amazon inc.": "Amazon",
    "amazon web services": "Amazon",
    "amazon web services india": "Amazon",
    "aws": "Amazon",
    "amazon india": "Amazon",

    # Microsoft
    "microsoft corporation": "Microsoft",
    "microsoft corp": "Microsoft",
    "microsoft corp.": "Microsoft",
    "microsoft india pvt ltd": "Microsoft",
    "microsoft india": "Microsoft",
    "ms": "Microsoft",

    # Meta / Facebook
    "facebook": "Meta",
    "facebook inc": "Meta",
    "facebook inc.": "Meta",
    "meta platforms": "Meta",
    "meta platforms inc": "Meta",
    "meta platforms inc.": "Meta",
    "instagram": "Meta",
    "whatsapp": "Meta",

    # Apple
    "apple inc": "Apple",
    "apple inc.": "Apple",
    "apple computer": "Apple",
    "apple india": "Apple",

    # Netflix
    "netflix inc": "Netflix",
    "netflix inc.": "Netflix",
    "netflix india": "Netflix",

    # Uber
    "uber technologies": "Uber",
    "uber technologies inc": "Uber",
    "uber india": "Uber",

    # Airbnb
    "airbnb inc": "Airbnb",
    "airbnb inc.": "Airbnb",

    # Salesforce
    "salesforce.com": "Salesforce",
    "salesforce inc": "Salesforce",
    "salesforce inc.": "Salesforce",

    # Oracle
    "oracle corporation": "Oracle",
    "oracle corp": "Oracle",
    "oracle india pvt ltd": "Oracle",
    "oracle india": "Oracle",

    # IBM
    "ibm": "IBM",
    "international business machines": "IBM",
    "ibm india pvt ltd": "IBM",
    "ibm india": "IBM",

    # SAP
    "sap se": "SAP",
    "sap india pvt ltd": "SAP",
    "sap india": "SAP",
    "sap labs india": "SAP",

    # Accenture
    "accenture plc": "Accenture",
    "accenture india": "Accenture",
    "accenture india pvt ltd": "Accenture",

    # Cognizant
    "cognizant": "Cognizant",
    "cognizant technology solutions": "Cognizant",
    "cts": "Cognizant",
    "cognizant india": "Cognizant",

    # HCL
    "hcl": "HCL Technologies",
    "hcl technologies": "HCL Technologies",
    "hcl technologies ltd": "HCL Technologies",
    "hcl tech": "HCL Technologies",
    "hcl infosystems": "HCL Technologies",

    # Capgemini
    "capgemini india": "Capgemini",
    "capgemini india pvt ltd": "Capgemini",

    # Tech Mahindra
    "tech mahindra": "Tech Mahindra",
    "tech mahindra ltd": "Tech Mahindra",
    "tech m": "Tech Mahindra",

    # Mindtree
    "mindtree ltd": "Mindtree",
    "mindtree limited": "Mindtree",

    # Mphasis
    "mphasis ltd": "Mphasis",
    "mphasis limited": "Mphasis",

    # Hexaware
    "hexaware technologies": "Hexaware",
    "hexaware technologies ltd": "Hexaware",

    # Persistent Systems
    "persistent systems ltd": "Persistent Systems",
    "persistent systems limited": "Persistent Systems",

    # L&T
    "l&t infotech": "LTIMindtree",
    "larsen & toubro infotech": "LTIMindtree",
    "lti": "LTIMindtree",
    "ltimindtree": "LTIMindtree",
    "ltimindtree ltd": "LTIMindtree",

    # Indian formats
    "tcs": "Tata Consultancy Services",
    "tata consultancy services": "Tata Consultancy Services",
    "tata consultancy services ltd": "Tata Consultancy Services",
    "tata consultancy services limited": "Tata Consultancy Services",
    "infosys": "Infosys",
    "infosys ltd": "Infosys",
    "infosys limited": "Infosys",
    "infosys bpo": "Infosys",
    "wipro": "Wipro",
    "wipro ltd": "Wipro",
    "wipro limited": "Wipro",
    "wipro technologies": "Wipro",

    # Startups / Others
    "flipkart internet pvt ltd": "Flipkart",
    "flipkart pvt ltd": "Flipkart",
    "flipkart india": "Flipkart",
    "myntra": "Myntra",
    "myntra designs pvt ltd": "Myntra",
    "paytm": "Paytm",
    "one97 communications": "Paytm",
    "zomato ltd": "Zomato",
    "zomato india": "Zomato",
    "swiggy": "Swiggy",
    "bundl technologies": "Swiggy",
    "ola": "Ola",
    "ani technologies": "Ola",
    "byju's": "BYJU'S",
    "think & learn pvt ltd": "BYJU'S",
    "razorpay": "Razorpay",
    "razorpay software pvt ltd": "Razorpay",
    "freshworks": "Freshworks",
    "freshworks inc": "Freshworks",
    "zoho": "Zoho",
    "zoho corporation": "Zoho",
    "zoho corp": "Zoho",
    "phonepe": "PhonePe",
    "phonepe pvt ltd": "PhonePe",
    "meesho": "Meesho",
    "fashnear technologies pvt ltd": "Meesho",
    "cred": "CRED",
    "dreamplug technologies pvt ltd": "CRED",
    "sharechat": "ShareChat",
    "mohalla tech pvt ltd": "ShareChat",
}

TITLE_RANKS = {
    "intern": 1,
    "junior": 2,
    "engineer": 3,
    "senior": 4,
    "lead": 5,
    "manager": 6,
    "director": 7,
    "vp": 8,
}


@dataclass(frozen=True)
class JobEntry:
    company: str | None
    title: str | None
    start_date: date | None
    end_date: date | None
    is_current: bool
    location: str | None
    description: str
    bullets: list[str]
    duration_months: int | None
    client: str | None
    employment_type: str | None
    confidence: float
    designation: str | None = None
    date_flag: str | None = None


class WorkExperienceParser:
    _nlp = None

    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = LLMParsingService()
        self._init_spacy()

    def _init_spacy(self) -> None:
        if spacy and WorkExperienceParser._nlp is None:
            try:
                # Load large model for better accuracy as requested by user
                logger.info("Loading SpaCy en_core_web_lg...")
                try:
                    WorkExperienceParser._nlp = spacy.load("en_core_web_lg")
                except OSError:
                    logger.info("SpaCy model 'en_core_web_lg' not found. Attempting to download...")
                    from spacy.cli import download
                    download("en_core_web_lg")
                    WorkExperienceParser._nlp = spacy.load("en_core_web_lg")
                logger.info("SpaCy en_core_web_lg loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load SpaCy model: {e}")

    @property
    def nlp(self):
        return WorkExperienceParser._nlp



    @staticmethod
    def build_date_anchor_excerpt(text: str, *, context_lines: int = 5) -> str:
        raw_lines = [ln.rstrip() for ln in (text or "").splitlines()]
        if not raw_lines:
            return ""

        anchor_indexes: list[int] = []
        for idx, ln in enumerate(raw_lines):
            if not ln.strip():
                continue
            if DATE_RANGE_RE.search(ln):
                anchor_indexes.append(idx)
                continue
            if PRESENT_RE.search(ln) and DATE_ANCHOR_RE.search(ln):
                anchor_indexes.append(idx)
                continue
            if DATE_ANCHOR_RE.search(ln) and re.search(r"(?:[-–—→]|\bto\b)", ln, flags=re.IGNORECASE):
                anchor_indexes.append(idx)

        if not anchor_indexes:
            return ""

        windows: list[tuple[int, int]] = []
        n = len(raw_lines)
        for idx in sorted(set(anchor_indexes)):
            start = max(0, idx - context_lines)
            end = min(n, idx + context_lines + 1)
            windows.append((start, end))

        windows.sort(key=lambda t: (t[0], t[1]))
        merged: list[tuple[int, int]] = []
        cur_start, cur_end = windows[0]
        for start, end in windows[1:]:
            if start <= cur_end:
                cur_end = max(cur_end, end)
                continue
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end
        merged.append((cur_start, cur_end))

        chunks: list[str] = []
        for start, end in merged:
            block_lines = [ln for ln in raw_lines[start:end] if ln.strip()]
            if not block_lines:
                continue
            chunks.append("\n".join(block_lines).strip())

        return "\n\n".join([c for c in chunks if c]).strip()

    @staticmethod
    def _looks_like_skillish_header(value: str | None) -> bool:
        cleaned = str(value or "").strip()
        if not cleaned:
            return False
        lowered = cleaned.lower()

        if re.match(r"^(environment|env|technologies|tools)\s*[:\-–—]", lowered):
            return True

        if re.fullmatch(
            r"(?:django|flask|fastapi|spring|react|node|docker|kubernetes|terraform|jenkins|gitlab|github|aws|azure|gcp|sql|python|java|postgres|postgresql|mysql|redis|kafka|elasticsearch|splunk|datadog|prometheus|grafana)",
            lowered,
        ) and len(cleaned) <= 40:
            return True
        if ("·" in cleaned or "•" in cleaned) and len(cleaned) <= 160:
            return True
        if cleaned.count(",") >= 2 and len(cleaned) <= 160:
            return True
        if re.search(
            r"\b(django|flask|fastapi|spring|react|node|docker|kubernetes|terraform|jenkins|gitlab|github|aws|azure|gcp|sql|python|java|postgres|postgresql|mysql|redis|kafka|elasticsearch|splunk|datadog|prometheus|grafana)\b",
            lowered,
        ):
            parts = [
                p.strip()
                for p in re.split(r"[,/|·•\u2022]", lowered)
                if p.strip()
            ]
            if len(parts) >= 3 and len(cleaned) <= 180:
                return True
        return False

    def parse_experience_section(self, text: str, source_format: str | None = None) -> list[JobEntry]:
        all_lines = [l for l in (text or "").splitlines() if l.strip()]
        pipe_lines = [l for l in all_lines if "|" in l]
        if all_lines and len(pipe_lines) / max(len(all_lines), 1) > 0.4:
            jobs = self._parse_table_formatted_experience(text)
            chunks = []  # table format has no chunks
        else:
            chunks = self.extract_individual_jobs(text, source_format=source_format)
            jobs = []
            for chunk in chunks:
                job = self._parse_chunk(chunk)
                if job.confidence < 0.8:
                    llm_job = self._llm_fallback(chunk)
                    if llm_job:
                        job = llm_job
                if self._is_plausible_job(job):
                    jobs.append(job)

        # Length check: if experience > 300 chars but 0 jobs, force LLM fallback
        mode = (self.settings.PARSING_MODE or "").lower()
        if (
            len(jobs) == 0
            and len(text or "") > 300
            and self.settings.LLM_PROVIDER != "none"
            and mode == "full"
            and self.llm
        ):
            llm_entries = self.llm.extract_work_experience(text) or []
            for payload in llm_entries or []:
                start_date = self._parse_date(payload.get("start_date", ""))
                end_date = self._parse_date(payload.get("end_date", ""))
                is_current = payload.get("is_current", False)
                duration_months = self._calc_duration_months(start_date, end_date, is_current)
                bullets = payload.get("responsibilities") or payload.get("bullets") or []
                job = JobEntry(
                    company=self.normalize_company_names(payload.get("company_name") or payload.get("company")),
                    title=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
                    start_date=start_date,
                    end_date=end_date,
                    is_current=is_current,
                    location=payload.get("location"),
                    description="\n".join(bullets) if bullets else payload.get("description", ""),
                    bullets=bullets,
                    duration_months=duration_months,
                    client=payload.get("client") or payload.get("client_name"),
                    employment_type=payload.get("employment_type"),
                    confidence=payload.get("confidence", 0.85),
                    designation=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
                )
                if self._is_plausible_job(job):
                    jobs.append(job)

        jobs = self._validate_dates(jobs)
        jobs = self._detect_overlaps(jobs)
        if chunks:
            logger.info("Work experience: %d chunks, %d jobs", len(chunks), len(jobs))
        else:
            logger.info("Work experience: %d jobs (table format)", len(jobs))
        return jobs

    def _parse_table_formatted_experience(self, text: str) -> list[JobEntry]:
        lines = [l.strip() for l in (text or "").splitlines() if l.strip() and "|" in l]
        if len(lines) < 2:
            return []
        entries: list[JobEntry] = []
        for line in lines:
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) < 2:
                continue
            entry = self._map_table_cols_to_job(cols)
            if entry and self._is_plausible_job(entry):
                entries.append(entry)
        return entries

    def _map_table_cols_to_job(self, cols: list[str]) -> JobEntry | None:
        date_col_idx: int | None = None
        for i, c in enumerate(cols):
            if DATE_RANGE_RE.search(c):
                date_col_idx = i
                break
        if date_col_idx is None:
            for i, c in enumerate(cols):
                if DATE_ANCHOR_RE.search(c) or re.search(r"\b(19|20)\d{2}\b", c):
                    date_col_idx = i
                    break
        start_date, end_date, is_current = None, None, False
        if date_col_idx is not None:
            start_date, end_date, is_current = self._parse_dates(cols[date_col_idx])

        non_date_cols = [c for i, c in enumerate(cols) if i != date_col_idx and c]
        location: str | None = None
        company: str | None = None
        title: str | None = None

        for c in non_date_cols:
            loc_m = LOCATION_RE.search(c)
            if loc_m:
                location = loc_m.group(1).strip()
                non_date_cols = [x for x in non_date_cols if x != c]
                break
        if location is None and len(non_date_cols) >= 3:
            last = non_date_cols[-1]
            if 2 <= len(last) <= 25 and not any(ch.isdigit() for ch in last):
                location = last.strip()
                non_date_cols = non_date_cols[:-1]

        if len(non_date_cols) >= 2:
            first, second = non_date_cols[0], non_date_cols[1]
            if self._looks_like_company(first) and self._looks_like_title(second):
                company, title = first, second
            elif self._looks_like_company(second) and self._looks_like_title(first):
                company, title = second, first
            else:
                company, title = first, second
        elif len(non_date_cols) == 1:
            c = non_date_cols[0]
            if self._looks_like_company(c):
                company = c
            else:
                title = c

        if not company and not title:
            return None
        duration_months = self._calc_duration_months(start_date, end_date, is_current)
        confidence = self._score_confidence(company, title, start_date, end_date, is_current, None, None)
        return JobEntry(
            company=self.normalize_company_names(company),
            title=self.normalize_job_titles(title),
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            location=location,
            description="",
            bullets=[],
            duration_months=duration_months,
            client=None,
            employment_type=None,
            confidence=confidence,
            designation=self.normalize_job_titles(title),
        )

    @staticmethod
    def _is_plausible_job(job: JobEntry) -> bool:
        company = str(job.company or "").strip()
        title = str(job.title or "").strip()
        if not company and not title:
            return False
        if PLACEHOLDER_ORG_RE.match(company) or PLACEHOLDER_ORG_RE.match(title):
            return False
        if PHONE_RE.search(company) or PHONE_RE.search(title):
            return False
        if EMAIL_RE.search(company) or EMAIL_RE.search(title):
            return False
        if SOCIAL_RE.search(company) or SOCIAL_RE.search(title):
            return False
        if EDU_KEYWORD_RE.search(company) or EDU_KEYWORD_RE.search(title):
            return False
        if CERT_KEYWORD_RE.search(company) or CERT_KEYWORD_RE.search(title):
            return False
        if "@" in company or "@" in title:
            return False
        if "http" in company.lower() or "http" in title.lower():
            return False
        if company and len(company) > 120:
            return False
        if title and len(title) > 120:
            return False

        # Reject skill/tool lists accidentally promoted into a "job" header (common PDF failure mode).
        if WorkExperienceParser._looks_like_skillish_header(company) or WorkExperienceParser._looks_like_skillish_header(title):
            return False

        # Reject if title or company is a lone location word
        if company.lower() in LOCATION_BLACKLIST or title.lower() in LOCATION_BLACKLIST:
            return False
            
        # Reject generic non-role titles found in audit
        if title.lower() in {"india", "mobile", "location", "city", "state"}:
            return False

        has_dates = bool(job.start_date) or bool(job.end_date)
        has_body = bool(job.bullets) or bool(str(job.description or "").strip())
        if not has_dates and not has_body:
            return False

        # Jobs without dates are extremely noisy in PDF extractions (contact/summary/skills). Only allow
        # them if we have a strong header signal.
        if not has_dates:
            if not company or not title:
                return False
            if not job.bullets or len(job.bullets) < 2:
                return False
        return job.confidence >= 0.5

    def _validate_dates(self, jobs: list[JobEntry]) -> list[JobEntry]:
        today = date.today()
        out: list[JobEntry] = []
        for job in jobs:
            s, e = job.start_date, job.end_date
            flag = job.date_flag
            if s and s > today:
                flag = "future_start"
            if s and e and e < s:
                flag = "end_before_start"
            if s and e and not flag:
                months = (e.year - s.year) * 12 + (e.month - s.month)
                if months > 480:
                    flag = "suspicious_duration"
            if flag:
                out.append(replace(job, date_flag=flag))
            else:
                out.append(job)
        return out

    def _detect_overlaps(self, jobs: list[JobEntry]) -> list[JobEntry]:
        sorted_jobs = sorted(
            [j for j in jobs if j.start_date and j.end_date],
            key=lambda j: j.start_date,
        )
        out = list(jobs)
        for i in range(len(sorted_jobs) - 1):
            a, b = sorted_jobs[i], sorted_jobs[i + 1]
            if b.start_date < a.end_date:
                overlap_days = (a.end_date - b.start_date).days
                if overlap_days > 30:
                    b_idx = out.index(b)
                    out[b_idx] = replace(b, date_flag=f"overlap_{overlap_days}d_with_prev")
        return out

    def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:
        # Pre-split: when resume uses CLIENT:/ROLE:/Location format, split by CLIENT: blocks first.
        # Handles consulting resumes where multiple roles are in one section.
        _client_split_re = re.compile(
            r"\n\s*(?=(?:CLIENT|client|project)\s*[:\-–—])",
            re.IGNORECASE,
        )
        if _client_split_re.search(text):
            parts = _client_split_re.split(text)
            # parts[0] may be preamble; parts[1:] each start with "CLIENT: X\n..."
            client_blocks = [p.strip() for p in parts[1:] if p.strip()]
            if len(client_blocks) > 1:
                return client_blocks

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []

        boundaries: list[int] = []
        for idx, line in enumerate(lines):
            if CLIENT_HEADER_RE.match(line):
                boundaries.append(idx)
                continue
            if DATE_ANCHOR_RE.search(line) and idx + 1 < len(lines) and PRESENT_RE.search(lines[idx + 1]):
                boundaries.append(idx)
                continue
            if PRESENT_RE.search(line) and idx > 0 and DATE_ANCHOR_RE.search(lines[idx - 1]):
                boundaries.append(idx - 1)
                continue
            if self._has_date_anchor(line, source_format=source_format):
                boundaries.append(idx)

        if not boundaries:
            chunks = ["\n".join(lines)]
            if len(lines) >= 4 and len(text) > 200:
                fallback = self._split_single_chunk_fallback(lines)
                if len(fallback) > 1:
                    logger.warning(
                        "Only 1 block found in experience section — possible miss; split by heuristics into %d chunks",
                        len(fallback),
                    )
                    return fallback
            return chunks

        starts: list[int] = []
        last_start = -1
        for idx in boundaries:
            start = idx
            if CLIENT_HEADER_RE.match(lines[idx]):
                if start <= last_start:
                    start = idx
                starts.append(start)
                last_start = start
                continue
            for back in range(1, 4):
                j = idx - back
                if j < 0:
                    break
                prev = lines[j]
                if ENVIRONMENT_LINE_RE.match(prev) or prev.strip().lower() in RESPONSIBILITY_MARKERS:
                    break
                if DATE_RANGE_RE.search(prev):
                    break
                if prev.startswith(("-", "•", "*")):
                    break
                if self._looks_like_skillish_header(prev):
                    break
                
                # If we find a line that looks like a title or company, expand the chunk start
                is_title = self._looks_like_title(prev)
                is_company = self._looks_like_company(prev)
                if is_title or is_company:
                    start = j
                    # If it's a company, we might be at the very top of the header, but keep looking back 
                    # one more line in case there's a title above it (or vice versa)
                    continue
                else:
                    # If it's neither, we've hit the body of the PREVIOUS job or some preamble
                    break
            
            if start <= last_start:
                start = idx
            starts.append(start)
            last_start = start

        chunks: list[str] = []
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else len(lines)
            if end <= start:
                continue
            chunks.append("\n".join(lines[start:end]))

        if len(chunks) == 1 and len(lines) >= 4 and len(text) > 200:
            fallback = self._split_single_chunk_fallback(lines)
            if len(fallback) > 1:
                logger.warning(
                    "Only 1 block found in experience section — possible miss; split by heuristics into %d chunks",
                    len(fallback),
                )
                return fallback

        return chunks

    def _split_single_chunk_fallback(self, lines: list[str]) -> list[str]:
        """Split lines by company name or job title patterns when date-based boundaries failed."""
        split_indices: list[int] = [0]
        for idx in range(1, len(lines)):
            line = lines[idx]
            if not line or line.startswith(("-", "•", "*")):
                continue
            # CLIENT: / project: at line start = new consulting engagement — always split
            if CLIENT_HEADER_RE.match(line):
                split_indices.append(idx)
                continue
            # Skip labeled fields (Role:, Designation:, Company:, etc.) — not job boundaries
            if LABELED_TITLE_RE.match(line) or LABELED_ORG_RE.match(line):
                continue
            # Company name (2-4 capitalized words) before a date
            date_match = DATE_RANGE_RE.search(line) or DATE_ANCHOR_RE.search(line)
            if date_match:
                prefix = line[: date_match.start()].strip().strip(" -–—|,·")
                words = prefix.split()
                if 2 <= len(words) <= 4 and prefix and prefix[0].isupper():
                    if not any(w.lower() in TITLE_SPLIT_KEYWORDS for w in words[:2]):
                        split_indices.append(idx)
                        continue
            # Job title at line start (e.g. "Senior Software Engineer") — not "Role: X"
            if TITLE_HINT_RE.search(line) and len(line.split()) <= 6:
                if idx > 0 and not lines[idx - 1].startswith(("-", "•", "*")):
                    is_preceded_by_company = False
                    # Check up to 3 lines back for a company
                    for b in range(1, 4):
                        if idx - b >= 0:
                            prev_line = lines[idx - b]
                            if self._looks_like_company(prev_line) and not self._looks_like_title(prev_line):
                                is_preceded_by_company = True
                                break
                    if not is_preceded_by_company:
                        split_indices.append(idx)

        if len(split_indices) <= 1:
            return ["\n".join(lines)]

        split_indices = sorted(set(split_indices))
        chunks: list[str] = []
        for i, start in enumerate(split_indices):
            end = split_indices[i + 1] if i + 1 < len(split_indices) else len(lines)
            if end > start:
                chunks.append("\n".join(lines[start:end]))
        return chunks if len(chunks) > 1 else ["\n".join(lines)]

    def _has_date_anchor(self, line: str, source_format: str | None = None) -> bool:
        if DATE_RANGE_RE.search(line):
            return True
        if PRESENT_RE.search(line) and DATE_ANCHOR_RE.search(line):
            return True
        if DATE_ANCHOR_RE.search(line) and re.search(r"(?:[-–—→]|\bto\b)", line, flags=re.IGNORECASE):
            return True
        # OCR lenient: bare 4-digit year (e.g. 2020, or 2O2O after OCR fixes)
        if source_format == "ocr":
            if re.search(r"\b(19|20)[0-9O]{2}\b", line):
                return True
        return False

    def normalize_company_names(self, name: str | None) -> str | None:
        if not name:
            return None
        key = name.strip().lower()
        return COMPANY_NORMALIZATION.get(key, name.strip())

    def normalize_job_titles(self, title: str | None) -> str | None:
        if not title:
            return None
        # Remove markdown headers and noise
        title = re.sub(r"^[#*>\-\s]{1,4}", "", title)
        normalized = title.strip().lower()
        normalized = re.sub(r"[./]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        for short, long in TITLE_NORMALIZATION.items():
            normalized = re.sub(rf"\b{re.escape(short)}\b", long, normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized.title()

    def calculate_total_experience(self, jobs: Iterable[JobEntry]) -> int:
        return sum(job.duration_months or 0 for job in jobs)

    def detect_career_progression(self, jobs: list[JobEntry]) -> bool:
        ranks = []
        for job in jobs:
            if not job.title:
                continue
            title = job.title.lower()
            rank = max((score for key, score in TITLE_RANKS.items() if key in title), default=0)
            ranks.append(rank)
        return ranks == sorted(ranks) if ranks else False

    def _parse_chunk(self, chunk: str) -> JobEntry:
        # Pre-clean the chunk from markdown headers
        cleaned_chunk = re.sub(r"^##+\s*", "", chunk, flags=re.MULTILINE)
        lines = [line.strip() for line in cleaned_chunk.splitlines() if line.strip()]
        header = lines[0] if lines else ""
        
        # SpaCy NER check for the header lines primarily
        spacy_orgs = []
        nlp = self.nlp
        if nlp:
            # Industry-level optimization: Only process first few lines for header detection
            # to avoid performance degradation on large chunks.
            header_sample = "\n".join(lines[:3])
            doc = nlp(header_sample)
            spacy_orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]

        company, title, location, start_date, end_date, is_current, body_start = self._parse_header_lines(lines)

        if not company and spacy_orgs:
            # Check if any detected ORG is in the header line
            for org in spacy_orgs:
                if org.lower() in header.lower():
                    company = org
                    break


        location, company, title = self._extract_and_clean_location(location, company, title, chunk)

        labeled_company, labeled_title, labeled_desc = self._parse_labeled_fields(lines[1:])
        if labeled_company and not company:
            company = labeled_company
        if labeled_title:
            title_clean = str(title or "").strip()
            title_is_locationish = bool(self._parse_location(title_clean))
            should_override = (
                (not title_clean)
                or title_clean.lower() in {"organization", "designation"}
                or PLACEHOLDER_ORG_RE.match(title_clean)
                or title_is_locationish
                or not self._looks_like_title(title_clean)
            )
            if should_override:
                title = labeled_title
        if labeled_desc:
            body_start = max(body_start, 1)

        if not start_date and not end_date:
            start_date, end_date, is_current = self._parse_dates(chunk)
        if not location:
            location = self._parse_location(chunk)

        body_lines = lines[body_start:]
        bullets = self._extract_bullets(body_lines)
        description_source = labeled_desc or (bullets if bullets else body_lines)
        description = "\n".join(description_source)
        duration_months = self._calc_duration_months(start_date, end_date, is_current)
        client = self._extract_client(chunk)
        if client:
            company_clean = str(company or "").strip()
            if not company_clean:
                company = client
            else:
                company_l = company_clean.lower().strip(":").strip()
                if PLACEHOLDER_ORG_RE.match(company_l) or company_l.startswith("client") or company_l.startswith("end client"):
                    company = client
        if client and company and self._client_looks_embedded_in_company(company, client):
            cleaned = self._remove_embedded_client(company, client)
            company = cleaned or company
        employment_type = self._detect_employment_type(chunk)

        confidence = self._score_confidence(company, title, start_date, end_date, is_current, client, bullets)
        if labeled_company or labeled_title:
            confidence = max(confidence, 0.85 if (company and title and start_date) else 0.75)

        def final_scrub(val: str | None) -> str | None:
            if not val: return None
            # Strip markdown headers and common list markers
            s = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", val).strip()
            # Strip anything matching LOCATION_RE or DATE patterns that might have survived
            s = self._strip_dates(s)
            loc_match = LOCATION_RE.search(s)
            if loc_match:
                s = s.replace(loc_match.group(1), "").strip(" -–—|,;:")
            # Remove trailing generic location words
            s = re.sub(r"\s+(?:location|city|loc|state|province|duration)\b\.?$", "", s, flags=re.IGNORECASE).strip()
            # Strip remaining noise characters
            s = s.strip(" -–—|,;:#*")
            return s or None

        company = final_scrub(company)
        title = final_scrub(title)
        client = final_scrub(client)

        # If client found is identical to company, null it to avoid redundancy
        if client and company and client.lower() == company.lower():
            client = None

        return JobEntry(
            company=self.normalize_company_names(company),
            title=self.normalize_job_titles(title),
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            location=location,
            description=description.strip(),
            bullets=bullets,
            duration_months=duration_months,
            client=client,
            employment_type=employment_type,
            confidence=confidence,
            designation=self.normalize_job_titles(title),
        )

    @staticmethod
    def _normalize_location_tag(tag: str) -> str:
        cleaned = re.sub(r"\s+", " ", (tag or "").strip())
        if len(cleaned) == 2:
            return cleaned.upper()
        return cleaned.title()

    def _extract_and_clean_location(
        self,
        location: str | None,
        company: str | None,
        title: str | None,
        chunk: str,
    ) -> tuple[str | None, str | None, str | None]:
        chunk_loc = None
        match = LOCATION_MARKER_RE.search(chunk or "")
        if match:
            chunk_loc = (match.group("loc") or "").strip().strip("-–—|,;:")
            chunk_loc = re.split(r"\s{2,}|\||\u2022", chunk_loc)[0].strip()
            if chunk_loc and len(chunk_loc) > 120:
                chunk_loc = None

        tag = None
        title_stripped = (title or "").strip()
        tag_match = LOCATION_TAG_RE.match(title_stripped)
        if tag_match:
            tag = self._normalize_location_tag(tag_match.group("tag"))

        company_clean = (company or "").strip() or None
        title_clean = (title or "").strip() or None

        def strip_location_marker(value: str | None) -> str | None:
            if not value:
                return None
            next_value = LOCATION_MARKER_RE.sub("", value).strip(" -–—|,;:")
            next_value = re.sub(r"\s+", " ", next_value).strip()
            return next_value or None

        company_clean = strip_location_marker(company_clean)
        title_clean = strip_location_marker(title_clean)

        final_location = (location or "").strip() or None
        if not final_location:
            final_location = chunk_loc

        if tag:
            if final_location:
                if "," in final_location:
                    final_location = final_location
                else:
                    final_location = f"{final_location}, {tag}"
            else:
                final_location = tag
            title_clean = None

        if company_clean and len(company_clean) <= 4 and company_clean.endswith(")"):
            company_clean = None

        # Post-clean: Strip generic "Location" or "City" trailing words often picked up in PDF headers
        if company_clean:
            company_clean = re.sub(r"\s+(?:location|city|loc|state|province)\b\.?$", "", company_clean, flags=re.IGNORECASE).strip()
        if title_clean:
            title_clean = re.sub(r"\s+(?:location|city|loc|state|province)\b\.?$", "", title_clean, flags=re.IGNORECASE).strip()

        return final_location, company_clean, title_clean

    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:
        cleaned = (header or "").strip()
        # Strip common markdown prefix noise
        cleaned = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", cleaned).strip()
        if not cleaned:
            return None, None
            
        def _validate_split(c: str, t: str) -> tuple[str | None, str | None]:
            c_val, t_val = c.strip(), t.strip()
            # Remove noise from split results
            c_val = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", c_val).strip()
            t_val = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", t_val).strip()
            
            is_c = self._looks_like_company(c_val)
            is_t = self._looks_like_title(t_val)
            if is_c and is_t:
                return c_val, t_val
            if is_c:
                return c_val, None
            if is_t:
                return None, t_val
            return None, cleaned

        # 1. Title at Company (e.g. 'Software Engineer at Google')
        match = TITLE_AT_COMPANY_RE.match(cleaned)
        if match:
            return _validate_split(match.group("company"), match.group("title"))
        # 2. Title | Company (e.g. 'Product Manager | Stripe')
        match = TITLE_PIPE_COMPANY_RE.match(cleaned)
        if match:
            return _validate_split(match.group("company"), match.group("title"))
        # 3. Company - Title (existing)
        match = COMPANY_LINE_RE.search(cleaned)
        if match:
            return _validate_split(match.group("company"), match.group("title"))
            
        if self._looks_like_company(cleaned):
            if COMPANY_HINT_RE.search(cleaned) or not TITLE_HINT_RE.search(cleaned):
                return cleaned, None
                
        if self._looks_like_title(cleaned):
            return None, cleaned
            
        return None, cleaned

    def _parse_header_lines(
        self, lines: list[str]
    ) -> tuple[
        str | None,
        str | None,
        str | None,
        date | None,
        date | None,
        bool,
        int,
    ]:
        if not lines:
            return None, None, None, None, None, False, 0

        header_window = lines[: min(len(lines), 6)]
        date_idx = None
        start_date = None
        end_date = None
        is_current = False
        for i, line in enumerate(header_window):
            sd, ed, cur = self._parse_dates(line)
            if sd or ed or cur:
                date_idx = i
                start_date, end_date, is_current = sd, ed, cur
                break

        location = None
        for line in header_window:
            location = self._parse_location(line) or location

        body_start = 1
        title: str | None = None
        company: str | None = None

        pre_lines = header_window[:date_idx] if date_idx is not None else header_window[:3]
        pre_lines = [
            ln.strip()
            for ln in pre_lines
            if ln
            and not ln.startswith(("-", "•", "*"))
            and not ENVIRONMENT_LINE_RE.match(ln)
            and ln.strip().lower().rstrip(":") not in RESPONSIBILITY_MARKERS
        ]
        
        # Handle fragmented multiline header (e.g. "Retail & E" \n "Commerce Labs")
        if len(pre_lines) >= 2 and not company and not title:
            first, second = pre_lines[0], pre_lines[1]
            if first.endswith(("&", "and", ",", "-", "at")) or second.startswith(("&", "and", "Commerce")):
                combined = f"{first} {second}"
                c_split, t_split = self._parse_company_title(combined)
                if c_split or t_split:
                    company, title = c_split, t_split
                    pre_lines = pre_lines[2:] # consume both

        post_lines = header_window[(date_idx + 1) : (date_idx + 4)] if date_idx is not None else header_window[1:3]
        post_lines = [
            ln
            for ln in post_lines
            if ln
            and not ln.startswith(("-", "•", "*"))
            and not ENVIRONMENT_LINE_RE.match(ln)
            and ln.strip().lower().rstrip(":") not in RESPONSIBILITY_MARKERS
        ]

        header_line = pre_lines[0] if pre_lines else (lines[0] if lines else "")
        date_line = header_window[date_idx] if date_idx is not None else None

        # Prefer extracting org/title from the line that contains the dates.
        if date_line:
            title_from_role = None
            role_match = LABELED_TITLE_RE.search(date_line)
            if role_match:
                raw_val = (role_match.group("value") or "").strip()
                # Strip date range (e.g. "January 2023 – Current") from "Role: Senior Developer January 2023 – Current"
                title_from_role = self._strip_dates(raw_val).strip() or raw_val

            company_from_date = None
            date_span = DATE_RANGE_RE.search(date_line)
            if date_span:
                prefix_raw = date_line[: date_span.start()]
            else:
                anchor = DATE_ANCHOR_RE.search(date_line)
                prefix_raw = date_line[: anchor.start()] if anchor else ""

            if prefix_raw:
                prefix = prefix_raw.strip().strip(" -–—|,·")
                prefix = re.sub(r"\s+", " ", prefix).strip()
                prefix = prefix.rstrip(":").strip()
                if prefix and not ENVIRONMENT_LINE_RE.match(prefix):
                    c_split, t_split = self._parse_company_title(prefix)
                    if not c_split and not t_split:
                        c_split, t_split = self._split_company_title(prefix)

                    if c_split or t_split:
                        company_from_date = c_split
                        if t_split and not title_from_role:
                            title_from_role = t_split
                    elif self._looks_like_company(prefix):
                        company_from_date = prefix

            if company_from_date:
                company = company or company_from_date
                if title_from_role and self._looks_like_title(title_from_role):
                    title = title or title_from_role

        if pre_lines and not (company and title):
            for candidate in pre_lines:
                c, t = self._split_company_title(candidate)
                if c and not company and self._looks_like_company(c):
                    company = c
                if t and not title and self._looks_like_title(t):
                    title = t
                    
            for candidate in pre_lines:
                if not title and self._looks_like_title(candidate) and not self._looks_like_company(candidate):
                    title = candidate
                elif not company and self._looks_like_company(candidate) and not self._looks_like_title(candidate):
                    company = candidate

        # If we have title but no company, and pre_lines has something unused
        if title and not company and len(pre_lines) > 0:
            for cand in pre_lines:
                if cand != title and self._looks_like_company(cand):
                    company = cand
                    break

        for candidate in post_lines:
            lowered = candidate.lower().strip(":")
            if lowered in RESPONSIBILITY_MARKERS:
                continue
            if not title and (TITLE_HINT_RE.search(candidate) or candidate.istitle()) and len(candidate.split()) <= 10:
                title = candidate
            elif not company and self._looks_like_company(candidate) and len(candidate.split()) <= 6:
                company = candidate

        if company and ENVIRONMENT_LINE_RE.match(company):
            company = None

        if company and title and self._looks_like_title(company) and not self._looks_like_company(company):
            # Potential swap or misidentification: If company looks like a title and title looks like a company
            if self._looks_like_company(title):
                company, title = title, company
            else:
                # If company is definitely a title (e.g. "Software Engineer") and we have no other title
                # we might have picked up a company name in the next lines or title is just better as company
                pass

        # Further refinement: If we have two things and one is explicitly an ORG via SpaCy
        if company and title and self.nlp:
            c_doc = self.nlp(company)
            t_doc = self.nlp(title)
            c_has_org = any(e.label_ == "ORG" for e in c_doc.ents)
            t_has_org = any(e.label_ == "ORG" for e in t_doc.ents)
            
            # If ONLY the title has an ORG label, and company doesn't, it's a very strong swap signal
            if t_has_org and not c_has_org:
                if self._looks_like_title(company) or not self._looks_like_company(company):
                    company, title = title, company
            
            # Disambiguation: If they seem swapped based on strong title keywords
            c_has_title_hint = bool(TITLE_HINT_RE.search(company))
            t_has_title_hint = bool(TITLE_HINT_RE.search(title))
            if c_has_title_hint and not t_has_title_hint:
                if not self._looks_like_company(company) or self._looks_like_company(title):
                    company, title = title, company

        if company and date_idx is not None:
            body_start = max(body_start, date_idx + 1)
        elif len(lines) > 1:
            body_start = 2

        title = self.normalize_job_titles(title)
        company = self.normalize_company_names(company)
        return company, title, location, start_date, end_date, is_current, body_start

    @staticmethod
    def _looks_like_company(text: str) -> bool:
        if not text:
            return False
        # Strip markdown noise
        cleaned = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", text).strip().strip(" -–—|,;:")
        if not cleaned or len(cleaned) < 2:
            return False
        if WorkExperienceParser._looks_like_skillish_header(cleaned):
            return False
        # Do not accept strings that are clearly sentences disguised as companies
        if len(cleaned.split()) > 6 or len(cleaned) > 80:
            return False
        # Reject if the entire string perfectly matches a Location
        loc_match = LOCATION_RE.search(cleaned)
        if loc_match and loc_match.group(1).strip() == cleaned:
            return False
        # Blacklist check
        if cleaned.lower() in LOCATION_BLACKLIST:
            return False
            
        if WorkExperienceParser._nlp:
            doc = WorkExperienceParser._nlp(cleaned)
            # Industry-level: Using SpaCy ORG entity for strong company signal
            if any(ent.label_ == "ORG" for ent in doc.ents):
                return True
            # Check for company-like suffix or hint
            if COMPANY_HINT_RE.search(cleaned):
                return True

        if 2 <= len(cleaned) <= 40 and cleaned.isupper() and not TITLE_HINT_RE.search(cleaned):
            return True
        if COMPANY_HINT_RE.search(text):
            return True
        if cleaned.istitle() and len(cleaned.split()) <= 4 and not TITLE_HINT_RE.search(cleaned):
            # Check if it's a generic word like "India" (title-cased)
            if cleaned.lower() in LOCATION_BLACKLIST:
                return False
            return True
        # If the string contains a distinct location abbreviation at the end.
        if re.search(r",\s*[A-Z]{2}\b", text) and len(cleaned.split()) <= 6:
            return True
        return False

    @staticmethod
    def _looks_like_title(text: str) -> bool:
        if not text:
            return False
        # Strip markdown noise before evaluating
        cleaned = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", text).strip().strip(" -–—|,;:")
        if not cleaned or len(cleaned) < 3:
            return False
        if WorkExperienceParser._looks_like_skillish_header(cleaned):
            return False
        # Blacklist check
        if cleaned.lower() in LOCATION_BLACKLIST:
            return False

        # 1. Regex hint check (strong signal)
        if TITLE_HINT_RE.search(cleaned):
            return True

        # 2. SpaCy POS check (if available) - looking for noun phrases at start
        if WorkExperienceParser._nlp:
            # POS-based refining: Job titles are usually noun phrases or specific patterns
            # Industry-level: Using POS tagging to filter out nonsensical lines
            doc = WorkExperienceParser._nlp(cleaned)
            
            # If line is primarily verbs or has no nouns, it's likely a responsibility, not a title
            # and job titles shouldn't start with verbs like "Developed", "Managed"
            first_token = doc[0].text.lower()
            if doc[0].pos_ == "VERB" and first_token.endswith(("ed", "ing")):
                return False
                
            has_noun = any(token.pos_ in {"NOUN", "PROPN"} for token in doc)
            if not has_noun:
                return False
                
            # Title candidates usually have a high density of nouns/adjectives
            pos_tags = [token.pos_ for token in doc]
            if pos_tags.count("VERB") > pos_tags.count("NOUN") + pos_tags.count("PROPN"):
                return False

        # Existing regex-based patterns as fallback/complement
        if TITLE_HINT_RE.search(cleaned):
            return True

        if 2 <= len(cleaned.split()) <= 8:
            # 3. Fallback: capitalization check for title-case strings
            return len(cleaned.split()) <= 6 and (cleaned.istitle() or any(w[0].isupper() for w in cleaned.split())) and len(cleaned) >= 4
        return False


    def _parse_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        match = DATE_RANGE_RE.search(text)
        if not match:
            return None, None, False

        start_raw = (match.group("start") or "").strip()
        end_raw = (match.group("end") or "").strip()

        start_date = self._parse_date(start_raw)
        if end_raw.lower() in {"present", "current", "till date", "till  date", "now"}:
            return start_date, None, True
        end_date = self._parse_date(end_raw)
        return start_date, end_date, False

    def _parse_date(self, value: str) -> date | None:
        raw = (value or "").strip()
        if not raw:
            return None
        raw = re.sub(r"\s+", " ", raw)
        raw = raw.replace("\u2019", "'")
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

        m = re.match(r"^(?P<year>\d{4})-(?P<month>\d{2})(?:-(?P<day>\d{2}))?$", raw)
        if m:
            y = int(m.group("year"))
            mo = int(m.group("month"))
            d = int(m.group("day") or "1")
            try:
                return date(y, mo, d)
            except ValueError:
                return date(y, mo, 1)

        m = re.match(r"^(?P<year>\d{4})[/-](?P<month>\d{1,2})$", raw)
        if m:
            y = int(m.group("year"))
            mo = int(m.group("month"))
            try:
                return date(y, mo, 1)
            except ValueError:
                return None

        m = re.match(r"^(?P<month>\d{1,2})[/-](?P<year>\d{4})$", raw)
        if m:
            y = int(m.group("year"))
            mo = int(m.group("month"))
            try:
                return date(y, mo, 1)
            except ValueError:
                return None

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
                },
            )
            return parsed.date() if parsed else None

        m = re.match(r"^(?P<year>\d{4})$", raw)
        if m:
            return date(int(m.group("year")), 1, 1)

        parsed = dateparser.parse(
            raw,
            settings={
                "PREFER_DAY_OF_MONTH": "first",
                "PREFER_DATES_FROM": "past",
            },
        )
        return parsed.date() if parsed else None

    @staticmethod
    def _strip_dates(text: str) -> str:
        s = DATE_RANGE_RE.sub("", text)
        s = DATE_ANCHOR_RE.sub("", s)
        s = re.sub(r"\b(19|20)\d{2}\b", "", s)
        return s.strip(" -–—,|·")

    def _split_company_title(self, line: str) -> tuple[str | None, str | None]:
        cleaned = line.strip()
        if not cleaned:
            return None, None
        cleaned = cleaned.replace("·", "|")
        if "|" in cleaned:
            parts = [p.strip() for p in cleaned.split("|") if p.strip()]
            if len(parts) >= 2:
                left, right = parts[0], parts[1]
                if not self._looks_like_company(left) and not self._looks_like_company(right):
                    return None, None
                right_l = right.lower().strip(":")
                left_l = left.lower()
                if PLACEHOLDER_ORG_RE.match(right_l) or right_l in {"role", "client"}:
                    if "," in left or "/" in left or (left_l and not TITLE_HINT_RE.search(left)):
                        return None, None
                    return None, None
                return left, right
        match = COMPANY_LINE_RE.search(cleaned)
        if match:
            company = match.group("company").strip()
            title = match.group("title").strip()
            if not self._looks_like_company(company) and not self._looks_like_title(title):
                return None, None
            title_l = title.lower().strip(":")
            if title_l in {"company", "role", "title", "designation", "client"}:
                if PLACEHOLDER_ORG_RE.match(title_l):
                    return company, None
                if "," in company or "/" in company or (company.lower() and not TITLE_HINT_RE.search(company)):
                    return None, None
            return company, title
        return None, None

    @staticmethod
    def _client_looks_embedded_in_company(company: str, client: str) -> bool:
        company_l = company.lower()
        client_l = client.lower()
        return client_l in company_l and len(client_l) >= 4

    @staticmethod
    def _remove_embedded_client(company: str, client: str) -> str:
        cleaned = re.sub(re.escape(client), "", company, flags=re.IGNORECASE).strip(" -–—|,:")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _parse_location(self, text: str) -> str | None:
        if not text:
            return None
            
        # 1. SpaCy NER check (strong signal for GPE/LOC)
        if self.nlp:
            doc = self.nlp(text)
            locs = [ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC"}]
            if locs:
                # Return the longest/most specific location found
                return max(locs, key=len).strip()

        # 2. Regex fallback
        match = LOCATION_RE.search(text)
        return match.group(1).strip() if match else None


    def _extract_bullets(self, lines: list[str]) -> list[str]:
        bullets = []
        for line in lines:
            if line.startswith(("-", "•", "*", "")):
                bullets.append(line.lstrip("-•* ").strip())
        return bullets

    def _extract_client(self, text: str) -> str | None:
        lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
        if not lines:
            return None

        # Only extract if explicit CLIENT markers are used at the start of the line
        for i, line in enumerate(lines[:8]):
            if not CLIENT_HEADER_RE.match(line):
                continue
                
            for pattern in CLIENT_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                raw = (match.group("client") or "").strip().strip("-–—| ")
                raw = re.split(r"\s{2,}|\||\u2022", raw)[0].strip()

                date_anchor = DATE_ANCHOR_RE.search(raw)
                if date_anchor:
                    raw = raw[: date_anchor.start()].strip().strip(" -–—|,:")
                raw = DATE_RANGE_RE.sub("", raw).strip(" -–—|,:")

                loc_match = LOCATION_RE.search(raw)
                if loc_match:
                    raw = raw.replace(loc_match.group(1), "").strip(" -–—|,:")
                    raw = re.sub(r"\s+", " ", raw).strip()

                if not raw or len(raw) < 2:
                    continue
                if len(raw) > 120 or raw.lower() in LOCATION_BLACKLIST:
                    continue
                return raw
        return None

    def _detect_employment_type(self, text: str) -> str | None:
        lowered = text.lower()
        if "contract" in lowered:
            return "contract"
        if "consultant" in lowered or "consulting" in lowered:
            return "consulting"
        if "part-time" in lowered or "part time" in lowered:
            return "part_time"
        return "full_time"

    def _calc_duration_months(
        self, start: date | None, end: date | None, is_current: bool
    ) -> int | None:
        if not start:
            return None
        end_date = end or date.today()
        if end_date < start:
            logger.warning("Date inconsistency detected", extra={"start": start, "end": end})
            return None
        return (end_date.year - start.year) * 12 + (end_date.month - start.month) + 1

    def _score_confidence(
        self,
        company: str | None,
        title: str | None,
        start_date: date | None,
        end_date: date | None,
        is_current: bool,
        client: str | None,
        bullets: list[str] | None,
    ) -> float:
        score = 0.0
        if company:
            score += 0.28
        if title:
            score += 0.22
        if start_date:
            score += 0.28
        if end_date or is_current:
            score += 0.12
        if client:
            score += 0.05
        if bullets and len(bullets) >= 2:
            score += 0.05
        return min(score, 1.0)

    @staticmethod
    def normalize_company_names(name: str | None) -> str | None:
        if not name or not isinstance(name, str):
            return None
        # Strip common noise
        cleaned = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", name).strip().strip(" -–—|,;:")
        # Strip trailing generic words picked up in headers
        cleaned = re.sub(r"\s+(?:location|city|loc|state|province|duration)\b\.?$", "", cleaned, flags=re.IGNORECASE).strip()
        # Remove noisy punctuation patterns like "(RTO)."
        cleaned = re.sub(r"^\([^)]+\)\.?$", "", cleaned).strip()
        cleaned = cleaned.strip(" .")
        if len(cleaned) < 2 or len(cleaned) > 150:
            return None
        return cleaned or None

    @staticmethod
    def normalize_job_titles(title: str | None) -> str | None:
        if not title or not isinstance(title, str):
            return None
        cleaned = re.sub(r"^[#*>\-\s\u2022]{1,4}", "", title).strip().strip(" -–—|,;:")
        cleaned = re.sub(r"\s+(?:location|city|loc|state|province|duration)\b\.?$", "", cleaned, flags=re.IGNORECASE).strip()
        # Title case standard job titles if they are all caps and not abbreviations
        if cleaned.isupper() and len(cleaned.split()) > 1:
            cleaned = cleaned.title()
        if len(cleaned) < 3 or len(cleaned) > 150:
            return None
        return cleaned or None

    def _is_plausible_job(self, job: JobEntry) -> bool:
        if not job.company and not job.title:
            return False
        # Require at least one of company/title/date or some description
        if not job.company and not job.title and not job.start_date:
            return False
        # Filter out obvious noise company names
        if job.company and (len(job.company) < 2 or job.company.lower() in LOCATION_BLACKLIST):
            return False
        return True

    def _parse_labeled_fields(self, lines: list[str]) -> tuple[str | None, str | None, list[str]]:
        company: str | None = None
        title: str | None = None
        responsibilities: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            match = LABELED_ORG_RE.search(line)
            if match:
                candidate = match.group("value").strip().strip("-–— ")
                if candidate:
                    company = candidate
                i += 1
                continue

            match = LABELED_TITLE_RE.search(line)
            if match:
                candidate = match.group("value").strip().strip("-–— ")
                if candidate:
                    title = candidate
                i += 1
                continue

            match = LABELED_RESP_RE.search(line)
            if match:
                first = (match.group("value") or "").strip().strip("-–— ")
                if first:
                    responsibilities.append(first)
                i += 1
                while i < len(lines):
                    nxt = lines[i].strip()
                    if not nxt:
                        i += 1
                        continue
                    if LABELED_ORG_RE.search(nxt) or LABELED_TITLE_RE.search(nxt):
                        break
                    responsibilities.append(nxt.lstrip("-•* ").strip())
                    i += 1
                continue

            lowered = line.lower().strip(":-–— ")
            if lowered in {"organization", "company", "employer"} and i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if nxt.startswith(("-", "–", "—")):
                    company = nxt.lstrip("-–— ").strip() or company
                    i += 2
                    continue
            if lowered in {"designation", "title", "role", "position"} and i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if nxt.startswith(("-", "–", "—")):
                    title = nxt.lstrip("-–— ").strip() or title
                    i += 2
                    continue

            i += 1

        title = self.normalize_job_titles(title)
        company = self.normalize_company_names(company)
        return company, title, responsibilities

    def _llm_fallback(self, chunk: str) -> JobEntry | None:
        mode = (self.settings.PARSING_MODE or "").lower()
        if self.settings.LLM_PROVIDER == "none" or mode != "full":
            return None

        entries = self.llm.extract_work_experience(chunk)
        if not entries:
            return None

        payload = entries[0]
        start_date = self._parse_date(payload.get("start_date", ""))
        end_date = self._parse_date(payload.get("end_date", ""))
        is_current = payload.get("is_current", False)
        duration_months = self._calc_duration_months(start_date, end_date, is_current)
        bullets = payload.get("responsibilities") or payload.get("bullets") or []

        return JobEntry(
            company=self.normalize_company_names(payload.get("company_name") or payload.get("company")),
            title=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            location=payload.get("location"),
            description="\n".join(bullets) if bullets else payload.get("description", ""),
            bullets=bullets,
            duration_months=duration_months,
            client=payload.get("client"),
            employment_type=payload.get("employment_type"),
            confidence=payload.get("confidence", 0.85),
            designation=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
        )

    def _call_llm(self, prompt: str) -> str | None:
        return self.llm._call_llm(prompt, task="work_experience").content

# --- Sanitization and Deduplication Logic (Consolidated from work_experience_sanitizer.py) ---

_PLACEHOLDER_RE = re.compile(
    r"^(company|client|organization|organisation|employer|designation|title|role|position|"
    r"job\s*title|professional\s+experience\b|n/a|na\b|tbd|tbc|unknown|none|null)\b",
    re.IGNORECASE,
)


def _collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_text_sanitizer(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return _collapse_spaces(value)


def _clean_bullet(value: str) -> str:
    cleaned = _normalize_text_sanitizer(value)
    cleaned = re.sub(r"^[\-\*•\u2022\u00b7\u25aa\u25cf\u25e6]+\s*", "", cleaned).strip()
    return cleaned


def _normalize_date_token_sanitizer(value: Any) -> str:
    raw = _normalize_text_sanitizer(value)
    return raw


def _strip_environment_skill_lines(text: str) -> str:
    """Remove Environment:/Tools:/Technologies: lines — those belong in Skills, not work description."""
    if not text or not isinstance(text, str):
        return text
    lines = text.splitlines()
    kept: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        if ENVIRONMENT_LINE_RE.match(stripped):
            continue
        kept.append(ln)
    return "\n".join(kept).strip()


def _normalize_description(value: Any) -> str:
    raw = _normalize_text_sanitizer(value)
    if not raw:
        return ""
    raw = _strip_environment_skill_lines(raw)
    raw = re.sub(r"(?m)^\|\s*", "", raw)
    raw = re.sub(r"\s*\|\s*", " - ", raw)
    raw = _collapse_spaces(raw)
    return raw


def _is_placeholder(value: Any) -> bool:
    cleaned = _normalize_text_sanitizer(value).lower()
    if not cleaned:
        return False
    return bool(_PLACEHOLDER_RE.match(cleaned))


def _is_skillish(value: Any) -> bool:
    cleaned = _normalize_text_sanitizer(value)
    if not cleaned:
        return False
    return WorkExperienceParser._looks_like_skillish_header(cleaned)


def _has_any_date(entry: dict[str, Any]) -> bool:
    return bool(_normalize_date_token_sanitizer(entry.get("start_date")) or _normalize_date_token_sanitizer(entry.get("end_date")))


def _has_any_body(entry: dict[str, Any]) -> bool:
    bullets = entry.get("bullets")
    if isinstance(bullets, list):
        if any(_clean_bullet(b) for b in bullets if isinstance(b, str)):
            return True
    if _normalize_description(entry.get("description")):
        return True
    return False


def _get_title(entry: dict[str, Any]) -> str:
    """Extract title from entry, checking role/job_title/designation as fallbacks."""
    return _normalize_text_sanitizer(
        entry.get("title") or entry.get("role") or entry.get("job_title") or entry.get("designation")
    )


def _merge_entries(primary: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    out = dict(primary)

    for key in ("company", "client", "location", "employment_type"):
        if not _normalize_text_sanitizer(out.get(key)) and _normalize_text_sanitizer(incoming.get(key)):
            out[key] = _normalize_text_sanitizer(incoming.get(key))
    # Title: also check role, job_title, designation
    if not _get_title(out) and _get_title(incoming):
        out["title"] = _get_title(incoming)

    out["is_current"] = bool(out.get("is_current")) or bool(incoming.get("is_current"))

    if not _normalize_date_token_sanitizer(out.get("start_date")) and _normalize_date_token_sanitizer(incoming.get("start_date")):
        out["start_date"] = _normalize_date_token_sanitizer(incoming.get("start_date"))
    if not _normalize_date_token_sanitizer(out.get("end_date")) and _normalize_date_token_sanitizer(incoming.get("end_date")):
        out["end_date"] = _normalize_date_token_sanitizer(incoming.get("end_date"))

    p_desc = _normalize_description(out.get("description"))
    i_desc = _normalize_description(incoming.get("description"))
    if i_desc and (not p_desc or len(i_desc) > len(p_desc)):
        out["description"] = i_desc

    merged_bullets: list[str] = []
    seen: set[str] = set()

    def _add_bullets(items: Any) -> None:
        if not isinstance(items, list):
            return
        for b in items:
            if not isinstance(b, str):
                continue
            cleaned = _clean_bullet(b)
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            merged_bullets.append(cleaned)

    _add_bullets(primary.get("bullets"))
    _add_bullets(incoming.get("bullets"))
    out["bullets"] = merged_bullets

    try:
        p_conf = float(out.get("confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        p_conf = 0.0
    try:
        i_conf = float(incoming.get("confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        i_conf = 0.0
    out["confidence"] = max(p_conf, i_conf)

    return out


def _count_filled_fields(entry: dict[str, Any]) -> int:
    """Score entry by number of filled fields (prefer description/bullets)."""
    score = 0
    if _normalize_description(entry.get("description")):
        score += 10
    bullets = entry.get("bullets")
    if isinstance(bullets, list):
        score += len([b for b in bullets if isinstance(b, str) and _clean_bullet(b)])
    if _normalize_date_token_sanitizer(entry.get("end_date")):
        score += 2
    if _normalize_text_sanitizer(entry.get("client")):
        score += 1
    if _normalize_text_sanitizer(entry.get("location")):
        score += 1
    if _normalize_text_sanitizer(entry.get("employment_type")):
        score += 1
    return score


def deduplicate_work_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove duplicate work entries. Two entries are duplicates if
    company + job_title + start_date match. Keep the entry with more filled fields.
    """
    if not isinstance(entries, list) or not entries:
        return list(entries) if isinstance(entries, list) else []

    seen: dict[tuple[str, str, str], dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        company = _normalize_text_sanitizer(entry.get("company")).lower()
        title = _normalize_text_sanitizer(entry.get("title")).lower()
        start_date = _normalize_date_token_sanitizer(entry.get("start_date")).lower()
        key = (company, title, start_date)

        if key not in seen:
            seen[key] = entry
            continue

        existing = seen[key]
        if _count_filled_fields(entry) > _count_filled_fields(existing):
            seen[key] = entry

    result = list(seen.values())
    removed = len(entries) - len(result)
    if removed > 0:
        logger.info("deduplicate_work_entries removed %d duplicate(s)", removed)
    return result


def sanitize_work_experience_entries(entries: Any) -> list[dict[str, Any]]:
    if not isinstance(entries, list) or not entries:
        return []

    cleaned: list[dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue

        company = _normalize_text_sanitizer(item.get("company"))
        title = _normalize_text_sanitizer(item.get("title") or item.get("role") or item.get("job_title") or item.get("designation"))
        # Use client as company when company is empty (e.g. "CLIENT: Home Depot" format)
        if not company:
            company = _normalize_text_sanitizer(item.get("client"))

        if not company and not title:
            continue

        if _is_placeholder(company) or _is_placeholder(title):
            continue

        if _is_skillish(company) or _is_skillish(title):
            continue

        if len(company) > 180 or len(title) > 180:
            continue

        normalized: dict[str, Any] = dict(item)
        normalized["company"] = company or None
        normalized["title"] = title or None
        normalized["client"] = _normalize_text_sanitizer(item.get("client")) or None
        normalized["location"] = _normalize_text_sanitizer(item.get("location")) or None
        normalized["employment_type"] = _normalize_text_sanitizer(item.get("employment_type")) or None
        normalized["start_date"] = _normalize_date_token_sanitizer(item.get("start_date")) or None
        normalized["end_date"] = _normalize_date_token_sanitizer(item.get("end_date")) or None
        normalized["description"] = _normalize_description(item.get("description")) or None
        normalized["is_current"] = bool(item.get("is_current", False))

        bullets_raw = item.get("bullets")
        bullets_out: list[str] = []
        if isinstance(bullets_raw, list):
            for b in bullets_raw:
                if not isinstance(b, str):
                    continue
                bb = _clean_bullet(b)
                if bb and not ENVIRONMENT_LINE_RE.match(bb):
                    bullets_out.append(bb)
        normalized["bullets"] = bullets_out

        company = str(normalized.get("company") or "").strip()
        title = str(normalized.get("title") or "").strip()
        has_date = _has_any_date(normalized)
        has_body = _has_any_body(normalized)

        # Drop only if we have nothing at all
        if not company and not title and not has_date and not has_body:
            continue

        # Allow through if company+title exist, even without date/body
        if not has_date and not has_body:
            if not company or not title:
                continue
            normalized["_needs_review"] = True  # flag for QA but keep it

        cleaned.append(normalized)

    deduped: dict[tuple[str, str, str, str, str, bool], dict[str, Any]] = {}
    order: list[tuple[str, str, str, str, str, bool]] = []

    for entry in cleaned:
        key = (
            _normalize_text_sanitizer(entry.get("company")).lower(),
            _normalize_text_sanitizer(entry.get("title")).lower(),
            _normalize_text_sanitizer(entry.get("client")).lower(),
            _normalize_date_token_sanitizer(entry.get("start_date")).lower(),
            _normalize_date_token_sanitizer(entry.get("end_date")).lower(),
            bool(entry.get("is_current")),
        )

        if key not in deduped:
            deduped[key] = entry
            order.append(key)
            continue

        deduped[key] = _merge_entries(deduped[key], entry)

    merged_list = [deduped[k] for k in order]
    return deduplicate_work_entries(merged_list)
