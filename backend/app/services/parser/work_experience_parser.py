from __future__ import annotations

import logging
import re
from dataclasses import dataclass, replace
from datetime import date
from typing import Iterable

import dateparser
from app.core.config import get_settings
from app.services.llm_service import LLMParsingService 

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
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>{DATE_TOKEN})\s*(?:\s*(?:[-–—→]|to|until|thru|through)\s*)\s*(?P<end>present|current|till\s+date|now|{DATE_TOKEN})",
    re.IGNORECASE,
)

PRESENT_RE = re.compile(r"\b(present|current|till\s+date|now)\b", re.IGNORECASE)
DATE_ANCHOR_RE = re.compile(rf"\b(?:{DATE_TOKEN})\b", re.IGNORECASE)
COMPANY_LINE_RE = re.compile(
    r"(?P<company>.+?)\s*(?:[-–—|])\s*(?P<title>.+)"
)
# Title at Company (e.g. 'Senior Dev at Acme Corp')
TITLE_AT_COMPANY_RE = re.compile(
    r"^(?P<title>[A-Z][\w\s,\.]+?)\s+at\s+(?P<company>[A-Z][\w\s,\.&]+)$",
    re.IGNORECASE,
)
# Title | Company (pipe-separated, no date)
TITLE_PIPE_COMPANY_RE = re.compile(
    r"^(?P<title>[^|]{3,80})\s*\|\s*(?P<company>[^|]{3,80})$",
)
LOCATION_RE = re.compile(r"\b([A-Za-z \.]{2,40},\s*[A-Z]{2})\b")
TITLE_HINT_RE = re.compile(r"\b(engineer|developer|architect|manager|lead|analyst|consultant|director|specialist|officer|associate|head|executive|technician|representative|administrator|coordinator|principal|scientist|researcher|expert|intern|partner|programmer|coder|tester|qa|quality assurance|support|scrum master|product owner|founder|co-founder|vp|cto|cio|cfo|ceo)\b", re.IGNORECASE)
# Job title keywords for splitting single-chunk experience (capitalized at line start)
TITLE_SPLIT_KEYWORDS = (
    "engineer", "manager", "developer", "analyst", "designer", "consultant",
    "director", "lead", "specialist", "architect", "coordinator", "administrator",
    "officer", "associate", "head", "executive", "principal", "scientist", "partner",
)
RESPONSIBILITY_MARKERS = {"responsibilities", "key responsibilities", "responsibility"}
COMPANY_HINT_RE = re.compile(r"\b(inc|llc|ltd|corp|corporation|company|technologies|systems|health|bank|solutions|services)\b", re.IGNORECASE)
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
    r"^(?:company(?:\s*name)?|client(?:\s*name)?|organization|employer|designation|title(?:\s*role)?|role(?:\s*title)?|position|description)\b",
    re.IGNORECASE,
)
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
    r"\b(designation|title|role|position)\b\s*(?:[:–—]|(?:\s+[-]))\s*(?P<value>.+)$",
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
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = LLMParsingService()

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
                    client=payload.get("client"),
                    employment_type=payload.get("employment_type"),
                    confidence=payload.get("confidence", 0.85),
                    designation=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
                )
                if self._is_plausible_job(job):
                    jobs.append(job)

        jobs = self._validate_dates(jobs)
        jobs = self._detect_overlaps(jobs)

        # STRICT SORTING: Prioritize current jobs, then sort by start date descending
        def sort_key(j: JobEntry):
            is_curr = 1 if j.is_current else 0
            # Convert date to string for robust comparison, handling None
            # Current jobs come first (is_curr=1), then most recent start date
            s_date = j.start_date.isoformat() if j.start_date else "0000-01-01"
            return (is_curr, s_date)

        jobs.sort(key=sort_key, reverse=True)

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
            r"(?:\n|^)\s*(?=(?:CLIENT|client|project)\s*[:\-–—])",
            re.IGNORECASE,
        )
        if _client_split_re.search(text):
            parts = _client_split_re.split(text)
            # parts[0] might be empty if match was at index 0, or it might be preamble or the first job
            client_blocks = []
            for p in parts:
                p_strip = p.strip()
                if not p_strip:
                    continue
                # If it's the first part and doesn't contain a client header, it might be preamble.
                # But if it contains a Role: or designation, it's likely the first job.
                if p == parts[0] and not CLIENT_HEADER_RE.search(p_strip):
                    if not (LABELED_TITLE_RE.search(p_strip) or DATE_RANGE_RE.search(p_strip)):
                        continue
                client_blocks.append(p_strip)
            
            if len(client_blocks) >= 1:
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
            line = lines[idx]
            if CLIENT_HEADER_RE.match(line):
                if start <= last_start:
                    start = idx
                starts.append(start)
                last_start = start
                continue
            
            # Look back to see if the company name or title is on the lines ABOVE the date line
            for back in range(1, 4):
                j = idx - back
                if j < 0:
                    break
                prev = lines[j]
                
                # Stop if we hit a boundary marker or bullet
                if ENVIRONMENT_LINE_RE.match(prev) or prev.strip().lower() in RESPONSIBILITY_MARKERS:
                    break
                if DATE_RANGE_RE.search(prev):
                    break
                if prev.startswith(("-", "•", "*")):
                    break
                if self._looks_like_skillish_header(prev):
                    break
                if prev.startswith("##"): # Section header
                    break
                    
                # If the line looks like a title/company, it might be the start
                p_is_title = self._looks_like_title(prev)
                p_is_company = self._looks_like_company(prev)
                
                if p_is_company or p_is_title:
                    start = j
                else:
                    # If it doesn't look like anything, stop going back
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
            chunk = "\n".join(lines[start:end])
            if chunk.strip():
                chunks.append(chunk)

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
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        header = lines[0] if lines else ""
        company, title, location, start_date, end_date, is_current, body_start = self._parse_header_lines(lines)

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
        
        # IMPROVEMENT: Instead of choosing between bullets OR body_lines,
        # we combine them to ensure no content (like plain text paragraphs) is lost.
        # But we prioritize labeled_desc if it exists.
        if labeled_desc:
            description_lines = labeled_desc
        else:
            description_lines = body_lines

        description = "\n".join(description_lines)
        duration_months = self._calc_duration_months(start_date, end_date, is_current)
        
        # Robust Client extraction
        client = self._extract_client(chunk)
        
        # CONSULTING FIRMS: If company is a known consulting firm, preserve it as company
        # even if end-client is found.
        CONSULTING_FIRMS = {
            "tcs", "tata consultancy services", "accenture", "cognizant", "cts", 
            "infosys", "wipro", "hcl", "capgemini", "deloitte", "ey", "pwc", "kpmg",
            "ibm", "tech mahindra", "mindtree", "l&t infotech", "lti", "persistent systems",
            "ust global", "virtusa", "syntel", "mphasis", "zensar", "hexaware", "itc infotech"
        }
        
        company_clean = str(company or "").strip()
        company_l = company_clean.lower().strip(":").strip()
        
        if client:
            if not company_clean or PLACEHOLDER_ORG_RE.match(company_l) or company_l.startswith("client") or company_l.startswith("end client"):
                company = client
            elif company_l in CONSULTING_FIRMS:
                # Keep consulting firm as company, client as client
                pass
            elif self._client_looks_embedded_in_company(company_clean, client):
                cleaned = self._remove_embedded_client(company_clean, client)
                if cleaned:
                    company = cleaned
            else:
                # If we have both a company and a client, and company isn't consulting,
                # we might have them swapped or both valid. For now, keep as is.
                pass

        employment_type = self._detect_employment_type(chunk)

        confidence = self._score_confidence(company, title, start_date, end_date, is_current, client, bullets)
        if labeled_company or labeled_title:
            confidence = max(confidence, 0.85 if (company and title and start_date) else 0.75)

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
        
        # Additional cleanup for title if it still contains "Location: ..."
        title_loc_match = LOCATION_MARKER_RE.search(title_clean or "")
        if title_loc_match:
            chunk_loc = chunk_loc or title_loc_match.group("loc").strip()
            title_clean = title_clean[:title_loc_match.start()].strip(" -–—|,;:")

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

        return final_location, company_clean, title_clean

    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:
        cleaned = (header or "").strip().strip(": ")
        if not cleaned:
            return None, None

        # Robust splitting logic handles |, -, --, ·, etc.
        c_split, t_split = self._split_company_title(cleaned)
        if c_split or t_split:
            return c_split, t_split

        # 1. Title at Company (fallback for specific pattern)
        match = TITLE_AT_COMPANY_RE.match(cleaned)
        if match:
            return match.group("company").strip(), match.group("title").strip()

        # Fallback: if it contains a colon, it might be a label "Role: Senior Dev"
        if ":" in cleaned:
            parts = [p.strip() for p in cleaned.split(":", 1)]
            if len(parts) == 2:
                label_l = parts[0].lower()
                val = parts[1]
                # Check if label matches or contains placeholder keywords
                if any(kw in label_l for kw in {"company", "client", "organization", "employer"}):
                    return val, None
                if any(kw in label_l for kw in {"designation", "title", "role", "position"}):
                    return None, val
                
                # Content-based check if label is not a standard keyword
                if self._looks_like_company(parts[0]) and self._looks_like_title(parts[1]):
                    return parts[0], parts[1]

        # Fallback: if no delimiter found, check whether the string looks like a company or a title.
        looks_like_company = self._looks_like_company(cleaned)
        looks_like_title = self._looks_like_title(cleaned)

        if looks_like_company and not looks_like_title:
            return cleaned, None
        if looks_like_title and not looks_like_company:
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
            ln
            for ln in pre_lines
            if ln
            and not ln.startswith(("-", "•", "*"))
            and not ENVIRONMENT_LINE_RE.match(ln)
            and ln.strip().lower().rstrip(":") not in RESPONSIBILITY_MARKERS
        ]
        post_lines = header_window[(date_idx + 1) : (date_idx + 3)] if date_idx is not None else header_window[1:3]
        post_lines = [
            ln
            for ln in post_lines
            if ln
            and not ln.startswith(("-", "•", "*"))
            and not ENVIRONMENT_LINE_RE.match(ln)
            and ln.strip().lower().rstrip(":") not in RESPONSIBILITY_MARKERS
        ]

        header_line = pre_lines[0] if pre_lines else lines[0]
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
                if prefix and not ENVIRONMENT_LINE_RE.match(prefix) and self._looks_like_company(prefix):
                    company_from_date = prefix

            if not company:
                company = company_from_date

            if title_from_role and self._looks_like_title(title_from_role):
                title = title_from_role
            
            if not company:
                for ln in pre_lines:
                    m = LABELED_ORG_RE.search(ln)
                    if m:
                        company = m.group("value").strip()
                        break
            
            if not company:
                company, fallback_title = self._parse_company_title(self._strip_dates(header_line))
                if not title:
                    title = fallback_title
        else:
            # No date found, try labeled fields first
            for ln in pre_lines:
                m_c = LABELED_ORG_RE.search(ln)
                if m_c:
                    company = m_c.group("value").strip()
                m_t = LABELED_TITLE_RE.search(ln)
                if m_t:
                    title = m_t.group("value").strip()
            
            if not company or not title:
                c, t = self._parse_company_title(self._strip_dates(header_line))
                company = company or c
                title = title or t

        if pre_lines:
            for candidate in pre_lines:
                c, t = self._split_company_title(candidate)
                if c and not company and self._looks_like_company(c):
                    company = c
                if t and (not title or self._looks_like_title(t)):
                    title = t

            for j, candidate in enumerate(pre_lines):
                if self._parse_location(candidate) and j > 0:
                    prev = pre_lines[j - 1]
                    if self._looks_like_company(prev):
                        company = company or prev

        for candidate in post_lines:
            lowered = candidate.lower().strip(":")
            if lowered in RESPONSIBILITY_MARKERS:
                continue
            if not title and (TITLE_HINT_RE.search(candidate) or candidate.istitle()) and len(candidate.split()) <= 10:
                title = candidate

        if company and ENVIRONMENT_LINE_RE.match(company):
            company = None

        # Only null company if it has a strong job-title keyword AND does NOT look like a company.
        # Do NOT null for short single-word names like "Humana", "TCS", "Verizon" — those are valid companies.
        if company and title and TITLE_HINT_RE.search(company) and not self._looks_like_company(company):
            # One last check: if title is empty, maybe what we thought was company is actually title
            if not title:
                title = company
            company = None

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
        cleaned = text.strip()
        if cleaned.startswith("##"): # Explicitly reject markdown headers
            return False
            
        if WorkExperienceParser._looks_like_skillish_header(cleaned):
            return False

        # Length check: company names are rarely very long sentences
        words = cleaned.split()
        if len(words) > 8:
            return bool(COMPANY_HINT_RE.search(text))

        # 1-word all-caps (TCS, IBM, WIPRO, HCL) or common known short names
        if len(words) == 1:
            if cleaned.isupper() and 2 <= len(cleaned) <= 10:
                return True
            # Single word Title Case (e.g. "Humana", "Amazon", "Flipkart")
            # But only if it's not a title keyword
            if cleaned.istitle() and not TITLE_HINT_RE.search(cleaned):
                return True

        if 2 <= len(cleaned) <= 40 and cleaned.isupper() and not TITLE_HINT_RE.search(cleaned):
            return True
            
        # 2-4 words Title Case without title hints (e.g. "Acme Corp", "Morgan Stanley")
        if cleaned.istitle() and 2 <= len(words) <= 4 and not TITLE_HINT_RE.search(cleaned):
            return True
            
        if COMPANY_HINT_RE.search(text):
            return True

        # State/Location pattern (e.g. "Louisville, KY") is NOT a company
        if re.search(r",\s*[A-Z]{2}\b", text):
            return False
            
        # Reject labels (Role:, Designation:, etc.) as part of company name
        if PLACEHOLDER_ORG_RE.match(text):
            return False

        # If it has 2-5 words and none are title hints, be lenient
        if 2 <= len(words) <= 5 and not TITLE_HINT_RE.search(text):
            return True

        return False


    @staticmethod
    def _looks_like_title(text: str) -> bool:
        if not text:
            return False
        cleaned = text.strip()
        if cleaned.startswith("##"):
            return False
            
        lowered = cleaned.lower()
        if len(lowered) < 2:
            return False
        if PLACEHOLDER_ORG_RE.match(lowered):
            return False

        # Reject location patterns like "Minneapolis, Mn" or "Boston, MA" from being titles
        if re.search(r"^[A-Za-z ]+,\s*[A-Z][a-z]?$", cleaned):
            return False

        # If it contains common title keywords, it's very likely a title
        if TITLE_HINT_RE.search(cleaned):
            # But not if it's 10+ words (likely a description line)
            if len(cleaned.split()) > 10:
                return False
            return True

        # If no keywords, it must be short and reasonably formatted (Title Case)
        words = cleaned.split()
        if len(words) <= 4 and cleaned.istitle():
            # Avoid single word generic things that might be companies
            if len(words) == 1 and not TITLE_HINT_RE.search(cleaned):
                return False
            return True

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
        return DATE_RANGE_RE.sub("", text).strip(" -–—,|·")

    def _split_company_title(self, line: str) -> tuple[str | None, str | None]:
        cleaned = line.strip()
        if not cleaned:
            return None, None
        
        # Priority 1: Parenthetical Company (Client) Role
        # Match "Some Company (Some Client) Some Role"
        paren_match = re.match(r"^(?P<company>[^\(]+)\s*\((?P<client>[^\)]+)\)\s*(?P<title>.+)$", cleaned)
        if paren_match:
            return paren_match.group("company").strip(), paren_match.group("title").strip()

        cleaned = cleaned.replace("·", "|")
        
        if "|" in cleaned:
            parts = [p.strip() for p in cleaned.split("|") if p.strip()]
            if len(parts) >= 2:
                left, right = parts[0], parts[1]
                right_l = right.lower().strip(":")
                left_l = left.lower().strip(":")
                
                # Check for placeholders on either side - discard the placeholder or strip label
                if PLACEHOLDER_ORG_RE.search(left_l) and ":" in left:
                    left = left.split(":", 1)[1].strip()
                    left_l = left.lower()
                if PLACEHOLDER_ORG_RE.search(right_l) and ":" in right:
                    right = right.split(":", 1)[1].strip()
                    right_l = right.lower()

                # If after stripping one side is still a placeholder, discard it
                if PLACEHOLDER_ORG_RE.fullmatch(right_l.strip(":- ")) or right_l.strip(":- ") in {"role", "client"}:
                    return left, None
                if PLACEHOLDER_ORG_RE.fullmatch(left_l.strip(":- ")) or left_l.strip(":- ") in {"role", "client"}:
                    return right, None
                
                # Verify plausibility
                l_is_title = self._looks_like_title(left)
                r_is_title = self._looks_like_title(right)
                l_is_company = self._looks_like_company(left)
                r_is_company = self._looks_like_company(right)
                
                if r_is_title and l_is_company and not l_is_title:
                    return left, right
                if l_is_title and r_is_company and not r_is_title:
                    return right, left
                
                # If one part looks like a sentence (contains a period mid-sentence), reject it as header part
                if "." in left and not left.endswith((".", "Inc.", "Corp.", "Ltd.")):
                    return None, None
                
                return left, right

        match = COMPANY_LINE_RE.search(cleaned)
        if match:
            company = match.group("company").strip()
            title = match.group("title").strip()
            title_l = title.lower().strip(" :")
            company_l = company.lower().strip(" :")
            
            if PLACEHOLDER_ORG_RE.fullmatch(title_l) or title_l in {"role", "client"}:
                return company, None
            if PLACEHOLDER_ORG_RE.fullmatch(company_l) or company_l in {"role", "client"}:
                return title, None
                
            if self._looks_like_title(title) and self._looks_like_company(company):
                return company, title
            if self._looks_like_title(company) and self._looks_like_company(title):
                return title, company
                
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
        match = LOCATION_RE.search(text)
        return match.group(1).strip() if match else None

    def _extract_bullets(self, lines: list[str]) -> list[str]:
        bullets = []
        # common bullet points including those seen in some PDFs/Word docs
        bullet_chars = ("-", "•", "*", "", "", "▪", "▫", "‣", "◦")
        for line in lines:
            trimmed = line.lstrip()
            if trimmed.startswith(bullet_chars):
                # found a bullet; strip the bullet character and whitespace
                # find exactly where the bullet ends
                content = trimmed
                for char in bullet_chars:
                    if content.startswith(char):
                        content = content[len(char):].strip()
                        break
                bullets.append(content)
        return bullets

    def _extract_client(self, text: str) -> str | None:
        lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
        if not lines:
            return None

        for i, line in enumerate(lines[:8]):
            for pattern in CLIENT_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                raw = (match.group("client") or "").strip().strip("-–—| ")
                raw = re.split(r"\s{2,}|\||\u2022", raw)[0].strip()

                # Clean location markers and following text
                loc_marker = LOCATION_MARKER_RE.search(raw)
                if loc_marker:
                    raw = raw[: loc_marker.start()].strip().strip(" -–—|,:")

                date_anchor = DATE_ANCHOR_RE.search(raw)
                if date_anchor:
                    raw = raw[: date_anchor.start()].strip().strip(" -–—|,:")
                raw = DATE_RANGE_RE.sub("", raw).strip(" -–—|,:")

                loc_match = LOCATION_RE.search(raw)
                if loc_match:
                    raw = raw.replace(loc_match.group(1), "").strip(" -–—|,:")
                    raw = re.sub(r"\s+", " ", raw).strip()

                if not raw:
                    continue
                if len(raw) > 120:
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
