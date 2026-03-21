from __future__ import annotations

import logging
import os
import re
import json
from dataclasses import dataclass, replace
from datetime import date
from typing import Iterable

import dateparser
import spacy
from pathlib import Path
try:
    from flashtext import KeywordProcessor
except ImportError:
    KeywordProcessor = None
try:
    from rapidfuzz import process, fuzz
except ImportError:
    process, fuzz = None, None
import pandas as pd

from app.core.config import get_settings
from app.services.llm_service import LLMParsingService 
from app.services.parser.cleaning_utils import get_spacy_model

logger = logging.getLogger(__name__)


MONTH_TOKEN = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_TOKEN = (
    r"(?:"
    r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
    r"|\d{4}[/-]\d{1,2}"  # YYYY-MM or YYYY/MM
    r"|\d{1,2}[/-]\d{2,4}"  # MM/YY or MM/YYYY
    r"|\d{4}[/-]\d{2,4}"  # YYYY-YY or YYYY-YYYY range fragment
    r"|'\s*\d{2}"            # '20, '22
    r"|\b(?:19|20)\d{2}\b" # YYYY (restrictive for bare years)
    r"|Q[1-4]\s+\d{4}"    # Q1 2020, Q4 2019
    r"|(?:Spring|Fall|Summer|Winter|Autumn|Spring|Fall)\s+\d{4}"  # Seasonal
    rf"|{MONTH_TOKEN}\s*[\'\u2019]\d{{2,4}}"  # Jan '20, Feb '19
    r"|\d{4}\.\d{2}|\d{2,4}\.\d{2,4}"  # 2020.01, 01.2020
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{2,4}}"  # MMM YYYY or MMM YY
    rf"|{MONTH_TOKEN}\s*[\u2019']\s*\d{{2,4}}"  # MMM 'YY
    r"|(?:\b[A-Za-z]{3,9}\s+\d{4}\b)" # September 2020
    r"|\b\d{2}/\d{4}\b" # 06/2024
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>{DATE_TOKEN})\s*(?:\s*(?:[-–—→/]|->|to|until|thru|through|till)\s*)\s*(?P<end>present|current|till\s+date|now|ongoing|until\s+now|up\s+to\s+now|{DATE_TOKEN})",
    re.IGNORECASE,
)

PRESENT_RE = re.compile(r"\b(present|current|till\s+date|now|ongoing|until\s+now|up\s+to\s+now)\b", re.IGNORECASE)
DATE_ANCHOR_RE = re.compile(rf"\b(?:{DATE_TOKEN})\b", re.IGNORECASE)

RESUME_NER_MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "resume_ner_model" / "model-best"
DATA_DIR = Path(__file__).resolve().parents[3] / "data"
GLOBAL_JOB_TITLES_CSV = DATA_DIR / "global_job_titles.csv"
GLOBAL_COMPANIES_CSV = DATA_DIR / "global_companies.csv"
GLOBAL_LOCATIONS_CSV = DATA_DIR / "global_locations.csv"
EXPERIENCE_KEYWORDS_CSV = DATA_DIR / "experience_keywords.csv"
COMPANY_LINE_RE = re.compile(
    r"(?P<company>.+?)\s*(?:[-–—|@:]|\bat\b)\s*(?P<title>.+)"
)
TITLE_PIPE_COMPANY_LOC_RE = re.compile(
    r"^(?P<title>[^|@:]+?)\s*(?:[|@:])\s*(?P<company>[^|@:]+?)\s*[|@:]\s*(?P<location>[^|@:]+)$",
    re.IGNORECASE,
)
# Title @ Company (e.g. 'Senior Dev @ Acme Corp' or 'Architect: Company')
TITLE_AT_COMPANY_RE = re.compile(
    r"^(?P<title>[A-Z][\w\s,\.]+?)\s*(?:@|at|:)\s*(?P<company>[A-Z][\w\s,\.&]+)$",
    re.IGNORECASE,
)
# Title | Company (pipe-separated, no date)
TITLE_PIPE_COMPANY_RE = re.compile(
    r"^(?P<title>[^|@:]{3,80})\s*[|@:]\s*(?P<company>[^|@:]{3,80})$",
)
# Strict Location Regex: City, ST (e.g. San Francisco, CA or New York, NY)
# Avoid matching technical fragments like "Swift, UI" or "Spring Boot, AI"
LOCATION_RE = re.compile(r"\b(?!(?:Swift|UI|IT|AI|ML|SQL|AWS|API|JDBC|JSON|NoSQL|REST|GraphQL|SOAP|CI/CD)\b)([A-Za-z \.]{2,40},\s*[A-Z]{2})\b")
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
BULLETS = ("-", "•", "*", "●", "▪", "▫", "◦", "‣", "∙", "\u2022", "\u00b7", "\u25cf", "\u25aa", "\u25ab", "\u25b8", "\u2043")
EDU_KEYWORD_RE = re.compile(
    r"\b(bachelor|master|ph\s*d|b\.?tech|m\.?tech|b\.?sc|m\.?sc|degree|university|college|school|institute|academy|polytechnic|education|training)\b",
    re.IGNORECASE,
)
CERT_KEYWORD_RE = re.compile(r"\b(certified|certification|certificate)\b", re.IGNORECASE)
PLACEHOLDER_ORG_RE = re.compile(
    r"^(?:company(?:\s*name)?|client(?:\s*name)?|organization|employer|designation|title(?:\s*role)?|role(?:\s*title)?|position|description|location|duration|period|dates?)\b",
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

SECTION_HEADERS_RE = re.compile(
    r"^\s*(?:education|skills|projects|personal\s*projects|academic\s*projects|key\s*projects|certifications|languages|interests?|summary|achievements|awards|references|hobbies|activities|volunteer|work\s*experience|experience|employment|work\s*history|career\s*summary|career\s*history|professional\s*experience|employment\s*history)\s*[:\-–—]?\s*$",
    re.IGNORECASE,
)

PROJECT_RE = re.compile(
    r"\b(case study|project|academic project|personal project|mini project|major project|college project|university project)\b",
    re.IGNORECASE
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
    confidence_score: float
    designation: str | None = None
    date_flag: str | None = None
    provenance: dict[str, object] | None = None
    
    @property
    def confidence(self) -> float:
        """Alias for backward compatibility."""
        return self.confidence_score


class WorkExperienceParser:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = LLMParsingService()
        self._ner_nlp = self._load_ner_model()
        self.hf_ner_pipeline = self._load_hf_ner_model()
        self.job_titles_list = []
        self.companies_list = []
        self.locations_list = []
        self._load_dictionaries()

    def _load_dictionaries(self):
        self.job_title_processor, self.job_titles_list = self._load_csv_dict(GLOBAL_JOB_TITLES_CSV, "job_titles")
        self.company_processor, self.companies_list = self._load_csv_dict(GLOBAL_COMPANIES_CSV, "companies")
        self.location_processor, self.locations_list = self._load_csv_dict(GLOBAL_LOCATIONS_CSV, "locations")
        self.exp_keyword_processor, _ = self._load_csv_dict(EXPERIENCE_KEYWORDS_CSV, "experience_keywords")

    def _load_hf_ner_model(self):
        if os.environ.get("SKIP_BERT") == "true":
            logger.info("Skipping BERT NER model loading as per SKIP_BERT env var.")
            return None
        try:
            from transformers import pipeline
            import logging
            # Set logging to error to avoid noisy download bars in logs if first time
            logging.getLogger("transformers").setLevel(logging.ERROR)
            return pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
        except Exception as e:
            logger.warning(f"Could not load HuggingFace NER model: {e}")
            return None

    def _load_csv_dict(self, path: Path, column_name: str) -> tuple[KeywordProcessor | None, list[str]]:
        if not path.exists():
            return None, []
        try:
            processor = KeywordProcessor(case_sensitive=False) if KeywordProcessor else None
            df = pd.read_csv(path, on_bad_lines='skip')
            keywords = []
            if column_name in df.columns:
                keywords = [str(val) for val in df[column_name].dropna()]
                if processor:
                    for val in keywords:
                        processor.add_keyword(val)
            return processor, keywords
        except Exception as e:
            logger.error(f"Error loading {path.name}: {e}")
            return None, []

    def _load_ner_model(self) -> spacy.Language | None:
        """Load the trained NER model if it exists (model-best or model-last)."""
        for suffix in ["model-best", "model-last"]:
            path = RESUME_NER_MODEL_PATH.parent / suffix
            if path.exists():
                return get_spacy_model(str(path))
        return None

    def _fuzzy_match(self, text: str, choices: list[str], threshold: float = 85.0) -> str | None:
        """Fallback to fuzzy matching if exact keyword match fails."""
        if not text or not choices or not process:
            return None
        
        # Performance optimization: only attempt fuzzy match on short/medium strings
        if len(text) > 100:
            return None
            
        result = process.extractOne(text, choices, scorer=fuzz.token_set_ratio)
        if result and result[1] >= threshold:
            return result[0]
        return None

    def validate_job_entry(self, job: JobEntry) -> tuple[bool, str | None]:
        """Check if a job entry is plausible and meets minimum requirements."""
        if not job.company and not job.title:
            return False, "Missing both company and title"
        
        comp = str(job.company or "").strip()
        titl = str(job.title or "").strip()
        
        if comp and len(comp) < 2:
            return False, "Company name too short"
            
        if titl and len(titl) < 2:
            return False, "Job title too short"
            
        if job.start_date and job.end_date and job.start_date > job.end_date:
            return False, "Start date after end date"
            
        if job.start_date and job.start_date.year > date.today().year + 1:
            return False, "Start date too far in future"
        
        return True, None


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

    def parse_experience_section(
        self, 
        text: str, 
        source_format: str | None = None,
        layout_blocks: list[LayoutBlock] | None = None
    ) -> list[JobEntry]:
        all_lines = [l for l in (text or "").splitlines() if l.strip()]
        pipe_lines = [l for l in all_lines if "|" in l]
        if all_lines and len(pipe_lines) / max(len(all_lines), 1) > 0.4:
            jobs = self._parse_table_formatted_experience(text)
            chunks = []
        else:
            chunks = self.extract_individual_jobs(text, layout_blocks=layout_blocks)
            jobs = []
            for chunk in chunks:
                job = self._parse_chunk(chunk)
                if job.confidence_score < 0.8:
                    llm_job = self._llm_fallback(chunk)
                    if llm_job:
                        job = llm_job
                if self._is_plausible_job(job):
                    jobs.append(job)

        # 1. Deduplicate and Merge Job Entries
        merged_jobs: list[JobEntry] = []
        for job in jobs:
            is_dup = False
            for m_job in merged_jobs:
                # Merging criteria: same normalized company AND title AND overlapping/adjacent dates
                c1 = str(job.company or "").lower().strip()
                c2 = str(m_job.company or "").lower().strip()
                t1 = str(job.title or "").lower().strip()
                t2 = str(m_job.title or "").lower().strip()
                
                # Use global normalizers for more robust deduplication
                nc1 = self.normalize_company_names(c1) or ""
                nc2 = self.normalize_company_names(c2) or ""
                nt1 = self.normalize_job_titles(t1) or ""
                nt2 = self.normalize_job_titles(t2) or ""
                
                same_comp = (nc1 == nc2) or (nc1 != "" and nc1 in nc2) or (nc2 != "" and nc2 in nc1)
                same_titl = (nt1 == nt2) or (nt1 != "" and nt1 in nt2) or (nt2 != "" and nt2 in nt1)
                
                # Check for date overlap or adjacency
                dates_overlap = False
                if job.start_date and m_job.start_date:
                    # Simple overlap check
                    s1, e1 = job.start_date, (job.end_date or date.today())
                    s2, e2 = m_job.start_date, (m_job.end_date or date.today())
                    if (s1 <= e2) and (s2 <= e1):
                        dates_overlap = True
                
                if same_comp and same_titl and dates_overlap:
                    # MERGE Descriptions and Bullets
                    m_bullets = list(m_job.bullets)
                    for b in job.bullets or []:
                        if b not in m_bullets:
                            m_bullets.append(b)
                    
                    merged_desc = m_job.description.strip()
                    if job.description and job.description.strip() not in merged_desc:
                        merged_desc += "\n" + job.description.strip()
                    
                    # Update merged job (keep earliest start, latest end)
                    s_orig = m_job.start_date or date(1000, 1, 1)
                    e_orig = m_job.end_date or date(9999, 12, 31)
                    s_new = job.start_date or date(1000, 1, 1)
                    e_new = job.end_date or date(9999, 12, 31)
                    
                    final_start = job.start_date if s_new < s_orig else m_job.start_date
                    final_end = job.end_date if e_new > e_orig else m_job.end_date
                    if job.is_current or m_job.is_current:
                        final_end = None
                    
                    merged_jobs[merged_jobs.index(m_job)] = replace(
                        m_job, 
                        description=merged_desc, 
                        bullets=m_bullets,
                        start_date=final_start,
                        end_date=final_end,
                        is_current=job.is_current or m_job.is_current
                    )
                    is_dup = True
                    break
            
            if not is_dup:
                merged_jobs.append(job)
        
        jobs = merged_jobs

        # 2. Length check: if experience > 300 chars but 0 jobs, force LLM fallback
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
                    description="\n".join(bullets) if bullets else str(payload.get("description", "")),
                    bullets=bullets,
                    duration_months=duration_months,
                    client=payload.get("client"),
                    employment_type=payload.get("employment_type"),
                    confidence_score=float(payload.get("confidence", 0.85)),
                    designation=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
                    provenance={"method": "llm_bulk"}
                )
                if self._is_plausible_job(job):
                    jobs.append(job)

        # Ensure Stable Rendering: Guarantee all 6 fields are present
        stable_jobs = []
        for job in jobs:
            stable_jobs.append(replace(
                job,
                company=job.company or "Unknown Company",
                title=job.title or "Professional Experience",
                location=job.location or "",
                description=job.description or ""
            ))
        jobs = stable_jobs

        jobs = self._validate_dates(jobs)
        jobs = self._detect_overlaps(jobs)

        # STRICT SORTING: Chronological (Current first, then descending by end_date)
        def final_sort(j: JobEntry):
            is_curr = 1 if j.is_current else 0
            # Use YYYYMM integer for sorting end_date desc
            e_val = (j.end_date.year * 100 + j.end_date.month) if j.end_date else 999999
            s_val = (j.start_date.year * 100 + j.start_date.month) if j.start_date else 0
            # Higher values (current or later dates) come first
            return (is_curr, e_val, s_val)
        
        jobs.sort(key=final_sort, reverse=True)
        return jobs

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
        confidence_score = self._score_confidence(company, title, start_date, end_date, is_current, None, None)
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
            confidence_score=confidence_score,
            designation=self.normalize_job_titles(title),
            provenance={"method": "table_format"}
        )

    def _is_plausible_job(self, job: JobEntry) -> bool:
        company = str(job.company or "").strip()
        title = str(job.title or "").strip()
        if not company and not title:
            return False
        
        # New: Reject "Case Study" or "Project" or bullet fragments misidentified as headers
        lowered_all = (company.lower() + " " + title.lower()).strip()
        if PROJECT_RE.search(lowered_all):
            # Unless it's a "Project Manager" or similar strong role
            if not re.search(r"\b(manager|lead|coordinator|director|head|vp|developer|engineer|analyst|specialist|consultant|architect)\b", title.lower()):
                # Also check if it's a "Project" at a reputable company (using company processor)
                is_real_company = False
                if self.company_processor and self.company_processor.extract_keywords(company):
                    is_real_company = True
                
                if not is_real_company:
                    return False

        # Reject common section headers or bullet markers misidentified as company/title
        if re.search(r"\b(summary|highlights|responsibilities|volunteer|community|alliance|contributor|membership|affiliation|involvement|award|recognition|objective|profile|technical skills|expertise|competencies)\b", lowered_all):
             if not re.search(r"\b(manager|lead|coordinator|director|head|vp|developer|engineer|analyst|specialist|consultant|architect)\b", title.lower()):
                return False

        if PLACEHOLDER_ORG_RE.match(company) or PLACEHOLDER_ORG_RE.match(title):
            return False
        # Improved phone/contact rejection
        if re.search(r"(\+\d{1,3}[\s.\-]?)?\(?\d{3}\)?[\s.\-]?\d{3}[\s.( \-]?\d{4}", company + " " + title):
            return False
        if EMAIL_RE.search(company) or EMAIL_RE.search(title):
            return False
        if SOCIAL_RE.search(company) or SOCIAL_RE.search(title):
            return False
        if EDU_KEYWORD_RE.search(company) or EDU_KEYWORD_RE.search(title):
            # Exception: if title or company has "teacher", "professor", "lecturer", "ta", "tutor"
            teacher_kws = {"teacher", "professor", "lecturer", "ta", "tutor", "instructor", "faculty", "trainer"}
            lowered_tit = title.lower()
            lowered_comp = company.lower()
            if not any(kw in lowered_tit for kw in teacher_kws) and not any(kw in lowered_comp for kw in teacher_kws):
                return False
        if CERT_KEYWORD_RE.search(company) or CERT_KEYWORD_RE.search(title):
            return False
        if "@" in company or "@" in title:
            return False
        if "http" in company.lower() or "http" in title.lower():
            return False
        if company and len(company) > 180:
            return False
        if title and len(title) > 180:
            return False
            
        # Location filtering: if company or title is JUST a location
        if company and self.location_processor and self.location_processor.extract_keywords(company):
            if len(company.split()) <= 2:
                # E.g. "Hyderabad", "San Francisco"
                return False

        has_dates = bool(job.start_date) or bool(job.end_date)
        is_skillish_company = self._looks_like_skillish_header(company)
        is_skillish_title = self._looks_like_skillish_header(title)
        
        # If it's very skillish and lacks dates/title indicators, reject it
        if (is_skillish_company or is_skillish_title):
            if not (has_dates and title and self._looks_like_title(title)):
                return False

        has_body = bool(job.bullets) or bool(str(job.description or "").strip())
        
        # LENIENT CHECK: If we have both company and title, it's likely a job even without dates/body
        # especially helpful for resumes where some jobs are just headers or missing details.
        if company and title and self._looks_like_company(company) and self._looks_like_title(title):
            return True # Keep it!

        if not has_dates and not has_body:
            return False

        # Jobs without dates are extremely noisy. Only allow if we have body or strong header.
        if not has_dates:
            if not company or not title:
                return False
            # Summary fragment check: long text without bullets/highlights is often a paragraph
            if job.description and len(job.description) > 300 and not job.bullets:
                return False
            # Confidence check for dateless jobs
            if job.confidence < 0.7:
                return False
        
        # Final sanity check: company shouldn't be a bullet or very short junk
        if company and company.startswith(BULLETS):
            return False
            
        if company and len(company) < 2:
            return False
            # Allow if both company and title are present, even without bullets
            if company and title:
                return True
            if not job.bullets or len(job.bullets) < 2:
                return False
        
        return job.confidence >= 0.4

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

    def _normalize_date_string(self, text: str) -> str:
        """Standardize date text for anchor matching (e.g., 'Jan 2020', '2022-24')."""
        if not text:
            return ""
        # Handle 'Yr - Yr' abbreviated format: 2022-24 -> 2022-2024
        text = re.sub(r"(\d{4})\s*[-–—]\s*(\d{2})(?!\d)", r"\1-20\2", text)
        # Handle Month 'YY: Jan '20 -> Jan 2020
        text = re.sub(r"([A-Za-z]+)\s*['’](\d{2})", r"\1 20\2", text)
        # Normalize delimiters for regex simplicity
        text = text.replace("/", "-").replace(".", "-")
        return text

    def extract_individual_jobs(
        self, 
        text: str, 
        source_format: str | None = None,
        layout_blocks: list[LayoutBlock] | None = None
    ) -> list[str]:
        """
        Multi-pass job boundary detection (Ensemble):
        1. Date-first pass (Signposts)
        2. Layout/Coordinate pass (Line proximity)
        3. Title/Company anchor pass (Delimiters)
        4. Heuristic/Keyword pass
        """
        if not text.strip():
            return []

        # Pass 0: Client/Consultancy sections
        _client_split_re = re.compile(
            r"(?:\n|^)\s*(?=(?:CLIENT|client|project)\s*[:\-–—])",
            re.IGNORECASE,
        )
        if _client_split_re.search(text):
            parts = _client_split_re.split(text)
            client_blocks = [p.strip() for p in parts if p.strip()]
            if len(client_blocks) > 1:
                return client_blocks

        # Pass 1: Date-first splitting (Signposts)
        date_chunks = self._split_by_dates(text)
        if len(date_chunks) > 1:
            return date_chunks

        # Pass 2: Coordinate proximity anchoring (Layout-aware)
        if layout_blocks:
            coord_chunks = self._split_by_coordinates(text, layout_blocks)
            if len(coord_chunks) > 1:
                return coord_chunks

        # Pass 3: Header delimiter splitting (Title | Company)
        delim_chunks = self._split_by_delimiters(text)
        if len(delim_chunks) > 1:
            return delim_chunks

        # Pass 4: Title-keyword anchor (Senior Software Engineer ...)
        keyword_chunks = self._split_by_title_keywords(text)
        if len(keyword_chunks) > 1:
            return keyword_chunks

        return [text]

    def _split_by_dates(self, text: str) -> list[str]:
        """Splits text by identifying date ranges, slurping 1-2 lines above if they look like headers."""
        lines = text.split("\n")
        chunks = []
        current_chunk = []
        
        for i, line in enumerate(lines):
            # Heuristic: Date range marks a job boundary
            if DATE_RANGE_RE.search(line[:100]):
                # Look back to see if we should slurp the header into this new chunk
                slurp_count = 0
                if current_chunk:
                    # Check 1-3 lines back for header
                    for back in range(1, 4):
                        idx = i - back
                        if idx < 0: break
                        prev_line = lines[idx].strip()
                        if not prev_line: continue
                        
                        # If we hit another date range while looking back, the lines below it
                        # belong to that PREVIOUS job, not the one we just found.
                        if DATE_RANGE_RE.search(prev_line):
                            slurp_count = 0
                            break
                            
                        # If the line looks like a header, it belongs to the *next* job
                        if self._looks_like_title(prev_line) or self._looks_like_company(prev_line):
                            slurp_count = back
                        else:
                            # Stop at first non-header non-empty line
                            break
                
                if slurp_count > 0:
                    # Move slurped lines from current_chunk to the start of the next chunk
                    header_lines = current_chunk[-slurp_count:]
                    current_chunk = current_chunk[:-slurp_count]
                    if current_chunk:
                        chunks.append("\n".join(current_chunk).strip())
                    current_chunk = header_lines # Start next chunk with slurped headers
                elif current_chunk:
                    chunks.append("\n".join(current_chunk).strip())
                    current_chunk = []
            
            current_chunk.append(line)
            
        if current_chunk:
            chunks.append("\n".join(current_chunk).strip())
            
        return [c for c in chunks if c.strip()]

    def _split_by_coordinates(self, text: str, blocks: list[LayoutBlock]) -> list[str]:
        """Splits text based on vertical gaps and left-alignment of header blocks."""
        lines = text.split("\n")
        chunks = []
        current_chunk = []
        
        # We look for blocks that are left-aligned (x0 < 100) and look like titles/companies
        for i, line in enumerate(lines):
            line_blocks = [b for b in blocks if getattr(b, "line_index", None) == i]
            is_boundary = False
            if line_blocks:
                header_like = any(
                    b.x0 < 100 and (TITLE_HINT_RE.search(b.text) or COMPANY_HINT_RE.search(b.text))
                    for b in line_blocks
                )
                if header_like:
                    is_boundary = True
            
            if is_boundary and current_chunk:
                chunks.append("\n".join(current_chunk).strip())
                current_chunk = []
            current_chunk.append(line)
            
        if current_chunk:
            chunks.append("\n".join(current_chunk).strip())
        return [c for c in chunks if c]

    def _split_by_delimiters(self, text: str) -> list[str]:
        """Splits by repeating delimiters like ' — ', ' | ', ' @ '."""
        delimiters = [" — ", " – ", " | ", " @ ", " at : ", " : "]
        lines = text.split("\n")
        
        for delim in delimiters:
            chunks = []
            current_chunk = []
            delim_count = 0
            for line in lines:
                if delim in line and (TITLE_HINT_RE.search(line) or COMPANY_HINT_RE.search(line)):
                    if current_chunk:
                        chunks.append("\n".join(current_chunk).strip())
                        current_chunk = []
                    delim_count += 1
                current_chunk.append(line)
            
            if current_chunk:
                chunks.append("\n".join(current_chunk).strip())
            
            if delim_count >= 2:
                return [c for c in chunks if c]
        
        return [text]

    def _split_by_title_keywords(self, text: str) -> list[str]:
        """Splits by common job title keywords at the beginning of lines."""
        lines = text.split("\n")
        chunks = []
        current_chunk = []
        for line in lines:
            cleaned = line.strip()
            if TITLE_HINT_RE.match(cleaned) and len(cleaned) < 120:
                if current_chunk:
                    chunks.append("\n".join(current_chunk).strip())
                    current_chunk = []
            current_chunk.append(line)
        if current_chunk:
            chunks.append("\n".join(current_chunk).strip())
        return [c for c in chunks if c]

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
        # Remove trailing fragments like (Client...), ( Eden Prairie...), etc.
        name = re.sub(r"\s+\(Client\b.*?\)?\s*$", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\s+\(.*?Remote.*?\)?\s*$", "", name, flags=re.IGNORECASE)
        name = name.strip(" -–—|,;:")
        
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
        
        # 1. Dictionary-Based Extraction with Context Window (±5 lines)
        d_job_title, d_company, d_location = None, None, None
        d_start_date, d_end_date, d_is_current = None, None, False
        
        # Find all job title and date anchors
        anchor_indices = []
        if self.job_title_processor:
            for i, line in enumerate(lines):
                if self.job_title_processor.extract_keywords(line):
                    anchor_indices.append(i)
        
        # Add date anchors too
        for i, line in enumerate(lines):
            if self._has_date_anchor(line) and i not in anchor_indices:
                anchor_indices.append(i)
        
        anchor_indices.sort()

        # Context window search for entities
        for idx in anchor_indices:
            search_start = max(0, idx - 5)
            search_end = min(len(lines), idx + 6)
            window = lines[search_start:search_end]
            window_text = "\n".join(window)
            
            # Job Title search in window
            if not d_job_title:
                for ln in window:
                    titles = self.job_title_processor.extract_keywords(ln) if self.job_title_processor else []
                    if titles:
                        d_job_title = titles[0]
                        break
                    # Fuzzy match fallback for title
                    if not d_job_title and self.job_titles_list:
                         d_job_title = self._fuzzy_match(ln, self.job_titles_list, threshold=90.0)
                         if d_job_title: break
                
            # BERT NER Extraction
            bert_companies = []
            bert_locations = []
            if getattr(self, "hf_ner_pipeline", None):
                try:
                    entities = self.hf_ner_pipeline(window_text)
                    for ent in entities:
                        if ent['entity_group'] == 'ORG':
                            word = ent['word']
                            if not word.startswith("##") and len(word) > 2:
                                bert_companies.append(word)
                        elif ent['entity_group'] == 'LOC':
                            word = ent['word']
                            if not word.startswith("##") and len(word) > 2:
                                bert_locations.append(word)
                except Exception as e:
                    logger.debug(f"HF NER failed on window: {e}")
            
            # Company search in window
            if not d_company:
                for ln in window:
                    comps = self.company_processor.extract_keywords(ln) if self.company_processor else []
                    if comps:
                        d_company = comps[0]
                        break
                    # Fuzzy match fallback for company
                    if not d_company and self.companies_list:
                        potential = self._fuzzy_match(ln, self.companies_list, threshold=90.0)
                        if potential:
                            d_company = potential
                            break
                if not d_company and bert_companies:
                    d_company = bert_companies[0]
            
            # Location search in window
            if not d_location:
                for ln in window:
                    locs = self.location_processor.extract_keywords(ln) if self.location_processor else []
                    if locs:
                        d_location = locs[0]
                        break
                    # Fuzzy match fallback for location
                    if not d_location and self.locations_list:
                        potential = self._fuzzy_match(ln, self.locations_list, threshold=90.0)
                        if potential:
                             d_location = potential
                             break
                if not d_location and bert_locations:
                    d_location = bert_locations[0]
            
            # Date search in window
            if not d_start_date:
                for ln in window:
                    sd, ed, cur = self._parse_dates(ln)
                    if sd or ed or cur:
                        d_start_date, d_end_date, d_is_current = sd, ed, cur
                        break
            
            if d_job_title and d_company:
                break

        # 2. Existing Heuristic-Based Extraction (Fallback / Complement)
        # Skip section headers in header line identification
        header_idx = 0
        while header_idx < len(lines) and SECTION_HEADERS_RE.match(lines[header_idx]):
            header_idx += 1
        
        relevant_lines = lines[header_idx:]
        company, title, location, start_date, end_date, is_current, body_start = self._parse_header_lines(relevant_lines)
        body_start += header_idx # Adjust body start relative to original lines

        # Merge Logic: Dictionary entities are higher precision
        # EXCEPT for company/title when we have a strong header split
        company = company or d_company
        title = title or d_job_title
        location = location or d_location
        start_date = start_date or d_start_date
        end_date = end_date or d_end_date
        is_current = is_current or d_is_current

        # Keep existing cleaning and fallback logic
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
        
        # FALLBACK: If company or title is missing, it might be at the bottom of the chunk.
        _c_lower = str(company or "").lower()
        if body_lines and (not company or _c_lower == "company" or not title):
            bottom_line = body_lines[-1]
            if not bottom_line.startswith(("-", "•", "*", "●")):
                parts = re.split(r'(?<=[.!?])\s+', bottom_line)
                candidate_str = parts[-1].strip()

                b_company, b_title = self._parse_company_title(candidate_str)
                b_loc = self._parse_location(candidate_str)
                
                if b_loc:
                    if b_company:
                         b_company = re.sub(re.escape(b_loc) + r"[,;\s]*", "", b_company).strip(" -–—|,;:")
                    if b_title:
                         b_title = re.sub(re.escape(b_loc) + r"[,;\s]*", "", b_title).strip(" -–—|,;:")

                is_valid = False
                if b_company and self._looks_like_company(b_company):
                     is_valid = True
                if b_title and self._looks_like_title(b_title):
                     is_valid = True
                
                if is_valid:
                    if b_company and (not company or _c_lower == "company"):
                        company = b_company
                    if b_title and not title:
                        title = b_title
                    if b_loc and not location:
                        location = b_loc
                    
                    # Remove the header part from the bottom line
                    if len(parts) > 1:
                        body_lines[-1] = " ".join(parts[:-1]).strip()
                    else:
                        body_lines.pop()

        bullets = self._extract_bullets(body_lines)
        
        # IMPROVEMENT: Instead of choosing between bullets OR body_lines,
        # we combine them to ensure no content (like plain text paragraphs) is lost.
        # But we prioritize labeled_desc if it exists.
        if labeled_desc:
            description_lines = [self._clean_header_text(line) for line in labeled_desc]
        else:
            description_lines = [self._clean_header_text(line) for line in body_lines]

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
                remainder = self._remove_embedded_client(company_clean, client)
                # If the remainder looks like a location, then 'client' was likely the company name
                # and the company field just included the location.
                if remainder and not self._parse_location(remainder):
                    company = remainder
                else:
                    company = client
            else:
                # If we have both a company and a client, and company isn't consulting,
                # we might have them swapped or both valid. For now, keep as is.
                pass

        employment_type = self._detect_employment_type(chunk)

        confidence_score = self._score_confidence(company, title, start_date, end_date, is_current, client, bullets)
        if labeled_company or labeled_title:
            confidence_score = max(confidence_score, 0.85 if (company and title and start_date) else 0.75)

        provenance = {
            "method": "deterministic_ensemble",
            "has_labeled_fields": bool(labeled_company or labeled_title),
            "had_client": bool(client),
            "score_breakdown": {
                "company": bool(company),
                "title": bool(title),
                "dates": bool(start_date)
            }
        }

        entry = JobEntry(
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
            confidence_score=confidence_score,
            designation=self.normalize_job_titles(title),
            provenance=provenance
        )

        is_valid, reason = self.validate_job_entry(entry)
        if not is_valid:
            logger.info(f"Deterministic parse failed validation: {reason}. Falling back to LLM.")
            llm_entry = self._llm_fallback(chunk)
            if llm_entry:
                from dataclasses import replace
                # Update confidence_score on frozen JobEntry
                llm_entry = replace(
                    llm_entry, 
                    confidence_score=(llm_entry.confidence_score + confidence_score) / 2
                )
                return llm_entry
        
        return entry

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

    def _clean_header_text(self, text: str | None, strip_labels: bool = True) -> str:
        if not text:
            return ""
        # 1. Strip markdown headers (handle ##, ###, and multiple leading #)
        cleaned = re.sub(r"^#+\s*", "", text.strip())
        # Also handle mid-line remnants of headers if they look like artifacts
        cleaned = re.sub(r"\s*##+\s*", " ", cleaned)
        
        # 2. Strip parentheticals that look like dates or locations
        def clean_parenthetical(match):
            content = match.group(1).lower()
            if DATE_ANCHOR_RE.search(content) or LOCATION_RE.search(content) or any(kw in content for kw in {"contract", "remote", "onsite", "hybrid", "freelance"}):
                return ""
            return match.group(0)

        cleaned = re.sub(r"\(([^)]+)\)", clean_parenthetical, cleaned)
        
        # 3. Strip literal labels aggressively
        # Handles "Role: Site Reliability Engineer" or "Company Northern Trust"
        if strip_labels:
            # First handle "Label: Content" pattern
            m = PLACEHOLDER_ORG_RE.match(cleaned)
            if m:
                if ":" in cleaned:
                    cleaned = cleaned.split(":", 1)[1]
                elif "·" in cleaned:
                     cleaned = cleaned.split("·", 1)[1]
                else:
                    # Strip at start if followed by word boundary
                    cleaned = re.sub(rf"^{PLACEHOLDER_ORG_RE.pattern}\b\s*", "", cleaned, flags=re.IGNORECASE)
        
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned.strip(" -–—|,;:·")

    def _parse_company_title(self, header: str) -> tuple[str | None, str | None]:
        # Do NOT strip labels yet, as we need them for identification (Client: X, Role: Y)
        cleaned = self._clean_header_text(header, strip_labels=False)
        if not cleaned:
            return None, None

        company: str | None = None
        title: str | None = None

        # 0. NER Model extraction for primary identification
        if self._ner_nlp:
            doc = self._ner_nlp(cleaned)
            for ent in doc.ents:
                if ent.label_ == "Companies worked at" and not company:
                    company = ent.text.strip()
                elif ent.label_ == "Designation" and not title:
                    title = ent.text.strip()
            
            if company and title:
                return company, title

        # Robust splitting logic handles |, -, --, ·, etc.
        c_split, t_split = self._split_company_title(cleaned)
        if c_split or t_split:
            # If NER already found one, prioritize it but keep splits as fallback
            return company or c_split, title or t_split

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
        # Priority 1: Check for explicit "Location:" markers
        for line in header_window:
            m = LOCATION_MARKER_RE.search(line)
            if m:
                location = m.group("loc").strip()
                break
        
        # Priority 2: Fallback to implicit City, ST patterns if no explicit location found
        if not location:
            for line in header_window:
                loc = self._parse_location(line)
                if loc:
                    location = loc
                    break

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
        
        # One last check for DOCX vertical headers: "Role" as company or "Company" as title
        if company and any(kw in company.lower() for kw in {"role", "position", "title", "designation"}):
            company = None
        if title and any(kw in title.lower() for kw in {"company", "client", "employer"}):
            title = None

        return company, title, location, start_date, end_date, is_current, body_start

    def _looks_like_company(self, text: str) -> bool:
        if not text:
            return False
        cleaned = text.strip()
        if cleaned.startswith("##"): # Explicitly reject markdown headers
            return False
            
        # 0. NER Model check
        if self._ner_nlp:
            doc = self._ner_nlp(cleaned)
            for ent in doc.ents:
                if ent.label_ in {"Companies worked at", "ORG"}:
                    return True

        if self._looks_like_skillish_header(cleaned):
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
            # But only if it's not a title keyword or a metadata label
            if cleaned.istitle() and not TITLE_HINT_RE.search(cleaned):
                if cleaned.lower() in {"location", "duration", "period", "dates", "summary"}:
                    return False
                return True

        if 2 <= len(cleaned) <= 40 and cleaned.isupper() and not TITLE_HINT_RE.search(cleaned):
            # Reject strings that look like dates (e.g. "AUG 2020")
            if DATE_ANCHOR_RE.search(cleaned):
                return False
            # Reject metadata headers in ALL CAPS
            if cleaned in {"LOCATION", "DURATION", "PERIOD", "DATES", "SUMMARY"}:
                return False
            return True
            
        # Location check: if it looks like a city/state, it's probably not a company
        if self.location_processor and self.location_processor.extract_keywords(cleaned):
            # If it's ONLY a location keyword, reject it as company
            if len(words) <= 2:
                return False

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


    def _looks_like_title(self, text: str) -> bool:
        if not text:
            return False
        cleaned = text.strip()
        if cleaned.startswith("##"):
            return False
            
        # 0. Dictionary check
        if self.job_title_processor:
            if self.job_title_processor.extract_keywords(cleaned):
                return True

        # 0.5 NER Model check
        if self._ner_nlp:
            doc = self._ner_nlp(cleaned)
            for ent in doc.ents:
                if ent.label_ == "Designation":
                    return True

        lowered = cleaned.lower()
        if len(lowered) < 2:
            return False
        # Reject literal labels like "Role", "Company", etc.
        if PLACEHOLDER_ORG_RE.match(lowered.rstrip(": ")):
            return False
        
        # If the string contains "Role:" or "Company:", definitely not a title
        if any(kw + ":" in lowered for kw in {"role", "company", "client", "position", "designation"}):
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
            # If it matches a company hint, it's likely not a title
            if COMPANY_HINT_RE.search(cleaned):
                return False
            # Avoid single word generic things that might be companies
            if len(words) == 1 and not TITLE_HINT_RE.search(cleaned):
                return False
            return True

        return False


    def _parse_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        if not text:
            return None, None, False
        
        # Pre-normalize (e.g. Jan '20 -> Jan 2020, 2022-24 -> 2022-2024)
        norm_text = self._normalize_date_string(text)
        
        match = DATE_RANGE_RE.search(norm_text)
        if not match:
            # Fallback for single date anchors (e.g. "2022 - present" where split failed)
            # or just a single year on a line.
            return None, None, False

        start_raw = (match.group("start") or "").strip()
        end_raw = (match.group("end") or "").strip()

        start_date = self._parse_date(start_raw)
        
        if end_raw.lower() in {"present", "current", "till date", "till  date", "now", "ongoing", "until now", "up to now", "ongoing"}:
            return start_date, None, True
            
        end_date = self._parse_date(end_raw)
        return start_date, end_date, False

    def _parse_date(self, value: str) -> date | None:
        raw = (value or "").strip()
        if not raw:
            return None
        
        # Use centralized normalization
        raw = self._normalize_date_string(raw)
        
        raw = re.sub(r"\s+", " ", raw)
        raw = raw.replace("\u2019", "'")
        raw = (
            raw.replace("Q1", "January")
            .replace("Q2", "April")
            .replace("Q3", "July")
            .replace("Q4", "October")
            .replace("Spring", "March")
            .replace("Autumn", "September")
            .replace("Fall", "September")
            .replace("Summer", "June")
            .replace("Winter", "December")
        )
        
        # Handle MMM 'YY or MMM 'YYYY
        raw = re.sub(
            r"([\w]{3,9})\s*[\'\u2019](\d{2,4})\b",
            lambda m: m.group(1) + " " + ("20" + m.group(2) if len(m.group(2)) == 2 and int(m.group(2)) <= 50 else ("19" + m.group(2) if len(m.group(2)) == 2 else m.group(2))),
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
            return self._clean_header_text(paren_match.group("company")), self._clean_header_text(paren_match.group("title"))

        cleaned = cleaned.replace("·", "|")
        
        if "|" in cleaned:
            parts = [p.strip() for p in cleaned.split("|") if p.strip()]
            # Filter out label-only parts or metadata
            filtered_parts = []
            for p in parts:
                p_clean = self._clean_header_text(p)
                if not p_clean:
                    continue
                
                lowered_p = p.lower().strip()
                if PLACEHOLDER_ORG_RE.fullmatch(lowered_p.strip(":- ")):
                    continue
                if PLACEHOLDER_ORG_RE.match(lowered_p) and ":" in lowered_p:
                    if not any(kw in lowered_p for kw in {"company", "client", "employer", "organization"}):
                        if not any(kw in lowered_p for kw in {"role", "title", "designation", "position"}):
                            continue
                
                words = p_clean.split()
                if len(words) > 6 and not TITLE_HINT_RE.search(p_clean) and not COMPANY_HINT_RE.search(p_clean):
                    continue

                filtered_parts.append(p_clean)

            if len(filtered_parts) >= 2:
                left = filtered_parts[0]
                right = filtered_parts[1]
                
                # Verify plausibility
                l_is_title = self._looks_like_title(left)
                r_is_title = self._looks_like_title(right)
                l_is_company = self._looks_like_company(left)
                r_is_company = self._looks_like_company(right)
                
                if l_is_title and r_is_company:
                    return right, left
                if r_is_title and l_is_company:
                    return left, right
                if l_is_title:
                    return right, left
                if r_is_title:
                    return left, right
                
                return left, right # Default

        # Use dash regexes
        dash_match = COMPANY_LINE_RE.match(cleaned)
        if dash_match:
            left = dash_match.group("company").strip()
            right = dash_match.group("title").strip()
            
            l_is_title = self._looks_like_title(left)
            r_is_title = self._looks_like_title(right)
            l_is_company = self._looks_like_company(left)
            r_is_company = self._looks_like_company(right)
            
            if l_is_title and r_is_company:
                return right, left
            if r_is_title and l_is_company:
                return left, right
            if l_is_title:
                return right, left
            if r_is_title:
                return left, right
                
            return left, right
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
        # Avoid bullet points or lines that look like descriptions
        if text.lstrip().startswith(("-", "•", "*", "●")):
            return None
            
        match = LOCATION_RE.search(text)
        if match:
            candidate = match.group(1).strip()
            # Double check: if it's "Swift, UI", discard it
            if re.search(r"\b(Swift|UI|IT|AI|ML|SQL|AWS|API|JDBC|JSON|NoSQL|REST|GraphQL|SOAP|CI/CD)\b", candidate):
                return None
            return candidate
        return None

    def _extract_bullets(self, lines: list[str]) -> list[str]:
        bullets = []
        # common bullet points including those seen in some PDFs/Word docs
        bullet_chars = ("-", "•", "*", "", "", "▪", "▫", "‣", "◦")
        for line in lines:
            if not line.strip(): continue
            
            trimmed = line.lstrip()
            if trimmed.startswith(bullet_chars):
                # found a bullet; strip the bullet character and whitespace
                # find exactly where the bullet ends
                content = trimmed
                for char in bullet_chars:
                    if content.startswith(char):
                        content = content[len(char):].strip()
                        break
                # Clean the content only AFTER identifying it as a bullet
                content = self._clean_header_text(content)
                if content:
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

        # Enhanced prompt instructions for LLM fallback
        prompt_instruction = "IMPORTANT: Extract only the most likely work experience entry from this text. If multiple are present, take the one that seems most prominent. Output MUST be valid JSON matching the schema."
        
        try:
            entries = self.llm.extract_work_experience(chunk)
            if not entries:
                return None

            payload = entries[0]
            start_date = self._parse_date(payload.get("start_date", ""))
            end_date = self._parse_date(payload.get("end_date", ""))
            is_current = payload.get("is_current", False)
            duration_months = self._calc_duration_months(start_date, end_date, is_current)
            bullets = payload.get("responsibilities") or payload.get("bullets") or []

            llm_job = JobEntry(
                company=self.normalize_company_names(payload.get("company_name") or payload.get("company")),
                title=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
                start_date=start_date,
                end_date=end_date,
                is_current=is_current,
                location=payload.get("location"),
                description="\n".join(bullets) if bullets else str(payload.get("description", "")),
                bullets=bullets,
                duration_months=duration_months,
                client=payload.get("client"),
                employment_type=payload.get("employment_type"),
                confidence_score=float(payload.get("confidence", 0.8)),
                designation=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
                provenance={"method": "llm_single_fallback"}
            )
            
            # Post-LLM validation
            is_valid, _ = self.validate_job_entry(llm_job)
            return llm_job if is_valid else None
            
        except Exception as e:
            logger.error(f"LLM fallback failed: {e}")
            return None

    def _call_llm(self, prompt: str) -> str | None:
        return self.llm._call_llm(prompt, task="work_experience").content
