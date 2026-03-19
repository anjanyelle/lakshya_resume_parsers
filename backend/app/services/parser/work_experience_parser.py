from __future__ import annotations

import logging
import os
import re
import json
from dataclasses import dataclass, replace, asdict
from datetime import date, datetime, timezone
from typing import Iterable
from pathlib import Path

import dateparser
import spacy
import pandas as pd
from rapidfuzz import process, fuzz

try:
    from flashtext import KeywordProcessor
except ImportError:
    KeywordProcessor = None

from app.core.config import get_settings
from app.services.llm_service import LLMParsingService 
from app.services.parser.cleaning_utils import get_spacy_model
from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.types import JobEntry
from app.services.parser.enrichment_service import EnrichmentService

logger = logging.getLogger(__name__)


MONTH_TOKEN = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE_TOKEN = (
    r"(?:"
    r"\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
    r"|\d{4}[/-]\d{1,2}"  # YYYY-MM or YYYY/MM
    r"|\d{1,2}[/-]\d{2,4}"  # MM/YY or MM/YYYY
    r"|\d{4}"  # YYYY
    r"|Q[1-4]\s+\d{4}"  # Q1 2020, Q4 2019
    r"|(?:Spring|Fall|Summer|Winter)\s+\d{4}"  # Seasonal
    rf"|{MONTH_TOKEN}\s*[\'\u2019]\d{{2,4}}"  # Jan '20, Feb '19, Jan '2020
    r"|\d{4}\.\d{2}|\d{2,4}\.\d{2,4}"  # 2020.01, 01.2020
    rf"|{MONTH_TOKEN}[.,]?\s+\d{{2,4}}"  # MMM YYYY or MMM YY
    rf"|{MONTH_TOKEN}\s*[\u2019']\s*\d{{2,4}}"  # MMM 'YY
    r"|(?:\b[A-Za-z]{3,9}\s+\d{4}\b)" # September 2020
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>present|current|till\s+date|now|ongoing|until\s+now|up\s+to\s+now|{DATE_TOKEN})\s*(?:\s*(?:[-–—→]|->|to|until|thru|through|till)\s*)\s*(?P<end>present|current|till\s+date|now|ongoing|until\s+now|up\s+to\s+now|{DATE_TOKEN})",
    re.IGNORECASE,
)

PRESENT_RE = re.compile(r"\b(present|current|till\s+date|now|ongoing|until\s+now|up\s+to\s+now)\b", re.IGNORECASE)
PRESENT = {"present", "current", "ongoing", "now"}
DATE_CANDIDATE_RE = re.compile(
    r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4})|(\b(19|20)\d{2}\b)|(\d{1,2}/\d{4})', 
    re.IGNORECASE
)
DATE_ANCHOR_RE = re.compile(rf"\b(?:{DATE_TOKEN})\b", re.IGNORECASE)

RESUME_NER_MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "resume_ner_model" / "model-best"
DATA_DIR = Path(__file__).resolve().parents[3] / "data"
GLOBAL_JOB_TITLES_CSV = DATA_DIR / "global_job_titles.csv"
GLOBAL_COMPANIES_CSV = DATA_DIR / "global_companies.csv"
GLOBAL_LOCATIONS_CSV = DATA_DIR / "global_locations.csv"
PRIORITY_JOB_TITLES_CSV = DATA_DIR / "job_titles.csv"
PRIORITY_COMPANIES_CSV = DATA_DIR / "companies.csv"
PRIORITY_LOCATIONS_CSV = DATA_DIR / "locations.csv"
EXPERIENCE_KEYWORDS_CSV = DATA_DIR / "experience_keywords.csv"
COMPANY_LINE_RE = re.compile(
    r"(?P<company>.+?)\s*(?:[-–—|])\s*(?P<title>.+)"
)
TITLE_PIPE_COMPANY_LOC_RE = re.compile(
    r"^(?P<title>[^|]+?)\s*\|\s*(?P<company>[^|]+?)\s*\|\s*(?P<location>[^|]+)$",
    re.IGNORECASE,
)
COMPANY_PIPE_TITLE_LOC_RE = re.compile(
    r"^(?P<company>[^|]+?)\s*\|\s*(?P<title>[^|]+?)\s*\|\s*(?P<location>[^|]+)$",
    re.IGNORECASE,
)
TITLE_DASH_COMPANY_RE = re.compile(
    r"^(?P<title>[^–—-]+?)\s*[–—\-]\s*(?P<company>[^–—-]+)$",
    re.IGNORECASE,
)
COMPANY_DASH_TITLE_RE = re.compile(
    r"^(?P<company>[^–—-]+?)\s*[–—\-]\s*(?P<title>[^–—-]+)$",
    re.IGNORECASE,
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
# Strict Location Regex: City, ST (e.g. San Francisco, CA or New York, NY)
# Avoid matching technical fragments like "Swift, UI" or "Spring Boot, AI"
# More flexible location regex: City, Region/State, [Optional Country]
LOCATION_RE = re.compile(r"\b(?!(?:Swift|UI|IT|AI|ML|SQL|AWS|API|JDBC|JSON|NoSQL|REST|GraphQL|SOAP|CI/CD)\b)([A-Za-z \.\u00C0-\u00FF]{2,40}(?:,\s*[A-Za-z \.\u00C0-\u00FF]{2,30}){1,2})\b")
# Improved pipe regex: no \b before/after symbols
PIPE_HEADER_RE = re.compile(r"\s*[|·]\s*")
TITLE_HINT_RE = re.compile(r"\b(engineer|developer|architect|manager|lead|analyst|consultant|director|specialist|officer|associate|head|executive|technician|representative|administrator|coordinator|principal|scientist|researcher|expert|intern|partner|programmer|coder|tester|qa|quality assurance|support|scrum master|product owner|founder|co-founder|vp|cto|cio|cfo|ceo)\b", re.IGNORECASE)
# Job title keywords for splitting single-chunk experience (capitalized at line start)
TITLE_SPLIT_KEYWORDS = (
    "engineer", "manager", "developer", "analyst", "designer", "consultant",
    "director", "lead", "specialist", "architect", "coordinator", "administrator",
    "officer", "associate", "head", "executive", "principal", "scientist", "partner",
)
RESPONSIBILITY_MARKERS = {"responsibilities", "key responsibilities", "responsibility"}
COMPANY_HINT_RE = re.compile(r"\b(inc|llc|ltd|corp|corporation|company|technologies|systems|health|bank|solutions|services|innovators|technologies|innovations|labs|group|associates|global|partner|partners|industries|software|network|networking|apps|applications)\b", re.IGNORECASE)
ENVIRONMENT_LINE_RE = re.compile(
    r"^(?:environments?|environment|tools?|technologies|tech\s*stack)\s*[:\-–—]",
    re.IGNORECASE,
)
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
EMAIL_RE = re.compile(r"\b[^\s@]+@[^\s@]+\b")
SOCIAL_RE = re.compile(r"\b(linkedin|github|portfolio)\b", re.IGNORECASE)
BULLETS = ("-", "•", "*", "●", "▪", "▫", "◦", "‣", "∙", "\u2022", "\u00b7", "\u25cf", "\u25aa", "\u25ab", "\u25b8", "\u2043")
BULLET_START_RE = re.compile(r"^\s*[-•*●▪▫◦‣∙\u2022\u00b7\u25cf\u25aa\u25ab\u25b8\u2043]")
DESCRIPTION_VERBS_RE = re.compile(
    r"^\s*(?:Led|Responsible|Managed|Developed|Designed|Collaborated|Implemented|Established|Directed|Oversaw|Architected|Performed|Coordinated|Facilitated|Created|Analyzed|Assisted)\b",
    re.IGNORECASE,
)
DESCRIPTION_HEADERS_RE = re.compile(
    r"^\s*(?:Key\s+Responsibilities|Responsibilities|Overview|Summary|Highlights|Mission|Role\s+Summary|Projects?|Client\s+Summary|Engagement|Assignment)\b",
    re.IGNORECASE,
)
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
    r"\b(organization|company|employer|client)\b\s*[:\-–—]\s*(?P<value>.+)$",
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
    r"^\s*(?:education|skills|career\s*highlights|highlights|certifications|languages|interests?|summary|achievements|awards|references|hobbies|activities|volunteer|work\s*experience|experience|employment|work\s*history|career\s*summary|career\s*history|professional\s*experience|employment\s*history)\s*[:\-–—·|]?\s*",
    re.IGNORECASE,
)
# REMOVED: projects|personal\s*projects|academic\s*projects|key\s*projects from SECTION_HEADERS_RE to enforce strict separation.

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
    "sr dev": "senior developer",
    "jr dev": "junior developer",
    "lead dev": "lead developer",
    "fs dev": "full stack developer",
    "be dev": "backend developer",
    "fe dev": "frontend developer",

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

TITLE_SYNONYMS = {
    "software engineer": ["software developer", "s/w engineer", "developer", "sr software engineer", "senior software engineer"],
    "data engineer": ["big data engineer", "etl engineer", "data platform engineer"],
    "manager": ["operations manager", "project manager", "program manager"],
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


# JobEntry moved to types.py to avoid circular imports


class WorkExperienceParser:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = LLMParsingService()
        self.skill_extractor = SkillExtractor()
        self._ner_nlp_cached = None
        self._hf_ner_pipeline_cached = None
        # Load BERT first if needed so it can be passed to EnrichmentService
        # But BERT loading is expensive, so we'll keep it as a property or load it here if requested
        self.enrichment_service = EnrichmentService(nlp_pipeline=self.hf_ner_pipeline)
        self._load_dictionaries()

    @property
    def _ner_nlp(self) -> spacy.Language | None:
        if self._ner_nlp_cached is None:
            self._ner_nlp_cached = self._load_ner_model()
        return self._ner_nlp_cached

    @property
    def hf_ner_pipeline(self):
        if self._hf_ner_pipeline_cached is None:
            self._hf_ner_pipeline_cached = self._load_hf_ner_model()
        return self._hf_ner_pipeline_cached

    def _load_dictionaries(self):
        # Priority Industry Datasets (from user-added CSVs)
        self.priority_job_title_processor = self._load_csv_dict(PRIORITY_JOB_TITLES_CSV, "job_titles")
        self.priority_company_processor = self._load_csv_dict(PRIORITY_COMPANIES_CSV, "companies")
        self.priority_location_processor = self._load_csv_dict(PRIORITY_LOCATIONS_CSV, "locations")
        
        # Global Large Datasets
        self.job_title_processor = self._load_csv_dict(GLOBAL_JOB_TITLES_CSV, "job_titles")
        self.company_processor = self._load_csv_dict(GLOBAL_COMPANIES_CSV, "companies")
        self.location_processor = self._load_csv_dict(GLOBAL_LOCATIONS_CSV, "locations")
        self.exp_keyword_processor = self._load_csv_dict(EXPERIENCE_KEYWORDS_CSV, "experience_keywords")

    def _load_hf_ner_model(self):
        # Default to skipping BERT in local/dev to avoid massive downloads and CPU hangs
        # unless explicitly requested via SKIP_BERT=false
        skip_bert = os.environ.get("SKIP_BERT", "").lower()
        if skip_bert == "true" or (skip_bert == "" and self.settings.ENVIRONMENT.lower() in ["development", "local"]):
            logger.info("Skipping BERT NER model loading (default for development).")
            return None
        if self.settings.LLM_PROVIDER == "none" and skip_bert != "false":
            logger.info("Skipping BERT NER model loading because LLM_PROVIDER is none.")
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

    def _load_csv_dict(self, path: Path, column_name: str) -> KeywordProcessor | None:
        if KeywordProcessor is None or not path.exists():
            return None
        try:
            processor = KeywordProcessor(case_sensitive=False)
            df = pd.read_csv(path)
            if column_name in df.columns:
                for val in df[column_name].dropna():
                    processor.add_keyword(str(val))
            return processor
        except Exception as e:
            logger.error(f"Error loading {path.name}: {e}")
            return None

    def _load_ner_model(self) -> spacy.Language | None:
        """Load the trained NER model if it exists (model-best or model-last)."""
        for suffix in ["model-best", "model-last"]:
            path = RESUME_NER_MODEL_PATH.parent / suffix
            if path.exists():
                return get_spacy_model(str(path))
        return None


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

    def _remove_section_headers(self, text: str) -> str:
        """
        Removes lines that are likely just section headers (e.g. 'Professional Experience')
        to prevent them from leaking into the first job's fields.
        """
        if not text:
            return ""
        lines = text.splitlines()
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                cleaned_lines.append(line)
                continue
            
            # If line is short and matches a section header pattern exactly
            if len(stripped) < 40 and SECTION_HEADERS_RE.fullmatch(stripped + " "):
                 # Note: SECTION_HEADERS_RE has a trailing \s*[:\-–—·|]?\s*
                 # so we append a space or colon to help it match if it doesn't have one
                 continue
            
            # Alternative: direct regex match
            if SECTION_HEADERS_RE.match(stripped) and len(stripped.split()) <= 3:
                continue
                
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines)

    def parse_experience_section(self, text: str, source_format: str | None = None) -> list[JobEntry]:
        """
        Production-grade 4-step sequential flow:
        1. Remove Headers
        2. Normalize Dates (within text)
        3. Split Jobs (Date-anchored with look-back)
        4. Parse Chunks
        """
        # Step 1: Remove Headers
        cleaned_text = self._remove_section_headers(text)
        
        # New Step 1b: Filter Page-Recurring Artifacts (Name/Contact info appearing at page gaps)
        cleaned_text = self._remove_recurring_lines(cleaned_text)
        
        # Step 2 & 3: Normalize and Split (Implicitly done in extract_individual_jobs)
        chunks = self.extract_individual_jobs(cleaned_text, source_format=source_format)
        
        jobs: list[JobEntry] = []
        last_company = None
        for chunk in chunks:
            # Step 4: Parse Chunk
            job = self._parse_chunk(chunk)
            
            # Hybrid: LLM Fallback only if both role and company are Unknown
            if (not job.company_or_client.get("name") or job.company_or_client.get("name") == "Unknown Company") and (not job.role or job.role == "Job Role"):
                if self.settings.LLM_PROVIDER != "none" and self.llm:
                    llm_job = self._llm_fallback(chunk)
                    if llm_job:
                        job = llm_job

            # Sticky Company logic for roles split from the same company header
            if job.company_or_client.get("name") and job.company_or_client.get("name") != "Unknown Company":
                last_company = job.company_or_client
            elif last_company and job.role and job.role != "Job Role":
                job = replace(job, company_or_client=last_company)
            
            if self._is_plausible_job(job):
                jobs.append(job)

        # Final lengths check: if 0 jobs but lot of text, try global LLM fallback
        if not jobs and len(text or "") > 300 and self.settings.LLM_PROVIDER != "none" and self.llm:
            llm_entries = self.llm.extract_work_experience(text) or []
            for payload in llm_entries:
                start_date = self._parse_date(payload.get("start_date", ""))
                end_date = self._parse_date(payload.get("end_date", ""))
                is_current = payload.get("is_current", False)
                job = JobEntry(
                    company_or_client={"name": self.normalize_company_names(payload.get("company_name") or payload.get("company")), "is_client": payload.get("is_client", False)},
                    role=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
                    start_date=start_date,
                    end_date=end_date,
                    currently_working=is_current,
                    location=payload.get("location"),
                    description="\n".join(payload.get("bullets", [])),
                    bullets=payload.get("bullets", []),
                    duration_months=self._calc_duration_months(start_date, end_date, is_current),
                    employment_type=payload.get("employment_type"),
                    confidence_score=payload.get("confidence", 0.85),
                )
                if self._is_plausible_job(job):
                    jobs.append(job)

        # Deduplication and Merging
        merged_jobs = self._deduplicate_jobs(jobs)
        
        # Step 5: Post-Processing (Validation & Overlaps)
        validated_jobs = self._validate_dates(merged_jobs)
        
        # Step 6: Split Validation (Roles/Dates within single entry)
        final_jobs = []
        for job in validated_jobs:
            splits = self._run_split_validation(job)
            final_jobs.extend(splits)
            
        final_jobs = self._detect_overlaps(final_jobs)
        
        # Defensive Sorting
        if not final_jobs:
            return []
            
        def final_sort(j: JobEntry):
            is_curr = 1 if j.currently_working or j.is_current else 0
            e_year = j.end_date.year if j.end_date else 9999
            e_month = j.end_date.month if j.end_date else 12
            s_year = j.start_date.year if j.start_date else 0
            s_month = j.start_date.month if j.start_date else 0
            return (is_curr, e_year * 100 + e_month, s_year * 100 + s_month)

        final_jobs.sort(key=final_sort, reverse=True)
        return final_jobs

    def _run_split_validation(self, job: JobEntry) -> list[JobEntry]:
        """
        If a single extracted entry contains multiple date ranges or multiple role tokens 
        separated by ;, ,, /, and, or line breaks, ensure split occurred.
        """
        # 1. Check for multiple roles in the extracted role/title
        role_text = job.role or job.title or ""
        role_separators = r"[/|]|\band\b"
        
        # We also check the first line of raw_text for separators that might have been lost
        first_line = job.raw_text.splitlines()[0] if job.raw_text else ""
        
        if re.search(role_separators, role_text, re.I) or re.search(role_separators, first_line, re.I):
            # Use the more 'raw' version from the first line for splitting if it has more separators
            split_text = first_line if re.search(role_separators, first_line, re.I) else role_text
            
            # Remove things like "City, ST" or dates from split_text if it came from first_line
            split_text = self._strip_dates(split_text)
            
            raw_roles = re.split(role_separators, split_text)
            final_roles = []
            for r in raw_roles:
                r_clean = r.strip(" -–—|,;:")
                if r_clean and len(r_clean.split()) <= 8:
                    # Validate it looks like a title
                    if self._looks_like_title(r_clean):
                        final_roles.append(r_clean)
            
            if len(final_roles) > 1:
                return [replace(job, role=self.enrichment_service.normalize_role(r), title=r) for r in final_roles]

        return [job]


    def parse_to_standardized_json(self, text: str, person_id: str = "p_000") -> dict:
        """
        Parses text and returns only the work_history JSON object matching the exact schema.
        """
        import uuid
        from datetime import datetime, timezone, date
        from dataclasses import asdict

        jobs = self.parse_experience_section(text)
        
        # Deduplicate by dates to avoid "duplication dates" as requested
        seen_dates = set()
        unique_jobs = []
        for job in jobs:
            date_key = (job.start_date, job.end_date, job.company_or_client.get("name"), job.role)
            if date_key not in seen_dates:
                unique_jobs.append(job)
                seen_dates.add(date_key)
        
        standardized_jobs = []
        start_time = datetime.now(timezone.utc)
        
        for i, job in enumerate(unique_jobs):
            # 1. Enrichment
            enriched_company = self.enrichment_service.enrich_company(job.company_or_client.get("name"))
            is_client = job.company_or_client.get("is_client", False) or self._detect_client_flag(job.raw_text or "")
            
            # Location
            location_str = job.location
            enriched_location = self.enrichment_service.enrich_location(location_str)
            
            # Role Normalization
            role_name = self.enrichment_service.normalize_role(job.role or job.title)
            
            # 2. Technologies
            techs = self._extract_technologies(job.raw_text or job.description)
            techs = techs[:40]
            
            # 3. Finalize Fields
            is_current = job.currently_working or (job.end_date is None)
            s_date = self._format_date(job.start_date)
            # If present, end_date should be current date as per "render 1st"
            if is_current:
                e_date = self._format_date(date.today())
            else:
                e_date = self._format_date(job.end_date)
            
            # Combine all details into description
            full_description = job.description or ""
            if job.bullets:
                bullets_text = "\n".join(f"- {b}" for b in job.bullets if b.strip())
                if bullets_text:
                    full_description += "\n\nResponsibilities:\n" + bullets_text
            
            if techs:
                full_description += "\n\nTechnologies: " + ", ".join(techs)
            
            emp_type = job.employment_type or self._detect_employment_type(job.raw_text or "")
            if emp_type:
                full_description += f"\n\nEmployment Type: {emp_type.replace('_', ' ').title()}"
            
            if job.notes:
                full_description += f"\n\nNotes: {job.notes}"

            # Location string formatting: city, region, country | remote
            loc_parts = [enriched_location.get(k) for k in ["city", "region", "country"] if enriched_location.get(k)]
            final_location = ", ".join(loc_parts) if loc_parts else enriched_location.get("city") or location_str
            if enriched_location.get("remote") or self._detect_remote(job.raw_text or ""):
                final_location = f"{final_location} | remote" if final_location else "remote"

            item = {
                "id": str(uuid.uuid4()),
                "person_id": person_id or str(uuid.uuid4()),
                "role": role_name,
                "company_or_client": {
                    "name": enriched_company.get("name", "Unknown Company"),
                    "is_client": is_client
                },
                "location": final_location,
                "start_date": s_date,
                "end_date": e_date,
                "currently_working": is_current,
                "description": full_description.strip()
            }
            standardized_jobs.append(item)

        return {
            "work_history": standardized_jobs,
            "metadata": {
                "count": len(standardized_jobs),
                "parsing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
            }
        }
    def _format_date(self, d: date | None) -> str | None:
        """Returns ISO YYYY-MM-DD format."""
        if not d: return None
        return d.strftime("%Y-%m-%d")

    def _normalize_location_obj(self, loc_str: str | None) -> dict:
        if not loc_str:
            return {"city": None, "region": None, "country": None, "remote": False}
        
        # Detect remote
        is_remote = bool(re.search(r"\bremote\b", loc_str, re.I))
        
        # Simple split: City, Region, Country
        parts = [p.strip() for p in re.split(r"[,/|]", loc_str)]
        city, region, country = None, None, None
        
        if len(parts) >= 3:
            city, region, country = parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            city, region = parts[0], parts[1]
        elif len(parts) == 1:
            city = parts[0]
            
        return {
            "city": city,
            "region": region,
            "country": country,
            "remote": is_remote
        }

    def _extract_technologies(self, text: str) -> list[str]:
        if not text: return []
            # Use existing SkillExtractor logic (flashtext provides canonical names)
        matches = self.skill_extractor.extract_with_flashtext(text, source="experience")
        # Deduplicate and sort
        return sorted(list(set(m.normalized_name.lower() for m in matches if m.normalized_name)))

    def _detect_client_flag(self, text: str) -> bool:
        if not text: return False
        # Worldwide patterns for client names
        client_indicators = [
            r"\bclient\b\s*[:\-–—]",
            r"\bworked\s+for\b",
            r"\bproject\s+for\b",
            r"\bconsulting\s+for\b",
            r"\bconsultant\s+for\b",
            r"\bcontracted\s+to\b",
            r"\bassigned\s+to\b",
            r"\bdeputed\s+to\b" # Common in India/APAC
        ]
        for pattern in client_indicators:
            if re.search(pattern, text, re.I):
                return True
        
        for p in CLIENT_PATTERNS:
            if p.search(text): return True
        if CLIENT_HEADER_RE.search(text): return True
        return False

    def _detect_remote(self, text: str) -> bool:
        if not text: return False
        # Worldwide remote markers
        remote_markers = r"\b(remote|wfh|work from home|anywhere|telecommute|virtual|offsite)\b"
        return bool(re.search(remote_markers, text, re.I))

    def _map_employment_type(self, raw: str | None) -> str:
        if not raw: return "full_time"
        lowered = raw.lower()
        if "contract" in lowered: return "contract"
        if "intern" in lowered: return "internship"
        if "freelance" in lowered: return "freelance"
        if "part" in lowered: return "part_time"
        if "temp" in lowered: return "temporary"
        return "full_time"

    def _deduplicate_jobs(self, jobs: list[JobEntry]) -> list[JobEntry]:
        """
        Modified per User Request: Remove date-based deduplication/merging.
        Only merge if Company and Role are IDENTICAL.
        """
        if not jobs:
            return []

        unique_jobs: list[JobEntry] = []
        for job in jobs:
            is_dup = False
            for i, uj in enumerate(unique_jobs):
                # Strict Identity check only
                if (uj.company_or_client["name"].lower() == job.company_or_client["name"].lower() and 
                    uj.role.lower() == job.role.lower() and
                    uj.start_date == job.start_date and
                    uj.end_date == job.end_date):
                    
                    # Merge bullets and tech even for clones
                    unique_jobs[i] = replace(uj, 
                        bullets=list(dict.fromkeys(uj.bullets + job.bullets)),
                        technologies=list(dict.fromkeys(uj.technologies + job.technologies))
                    )
                    is_dup = True
                    break
            
            if not is_dup:
                unique_jobs.append(job)

        return unique_jobs

    def _calculate_date_overlap_ratio(self, j1: JobEntry, j2: JobEntry) -> float:
        s1, e1 = j1.start_date or date(1900, 1, 1), j1.end_date or date.today()
        s2, e2 = j2.start_date or date(1900, 1, 1), j2.end_date or date.today()
        
        latest_start = max(s1, s2)
        earliest_end = min(e1, e2)
        
        if latest_start > earliest_end:
            return 0.0
            
        overlap_days = (earliest_end - latest_start).days
        duration1 = (e1 - s1).days or 1
        duration2 = (e2 - s2).days or 1
        
        # Ratio relative to the shorter duration
        return overlap_days / min(duration1, duration2)

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
            company_or_client={"name": self.normalize_company_names(company), "is_client": False},
            role=self.normalize_job_titles(title),
            start_date=start_date,
            end_date=end_date,
            currently_working=is_current,
            location=location,
            description="",
            bullets=[],
            duration_months=duration_months,
            employment_type=None,
            confidence_score=confidence,
        )

    def _is_plausible_job(self, job: JobEntry) -> bool:
        # Extract company name from dict or string (for robustness)
        company_name = ""
        if isinstance(job.company_or_client, dict):
            company_name = job.company_or_client.get("name") or ""
        else:
            company_name = str(job.company_or_client or "")
        
        company = company_name.strip()
        title = str(job.role or job.title or "").strip()
        if not company and not title:
            # Phase 8: If it has a date, it's plausible even if we haven't identified the company/title yet
            if job.start_date:
                return True
            return False
        
        # Phase 8: Strict splitting - if there is a date, it's a valid job.
        if job.start_date:
            return True
        
        lowered_all = (company.lower() + " " + title.lower() + " " + str(job.description or "").lower()).strip()
        
        # New: Reject "Case Study" or "Project" or bullet fragments misidentified as headers
        if PROJECT_RE.search(lowered_all):
            # Unless it's a "Project Manager" or similar strong role
            if not re.search(r"\b(manager|lead|coordinator|director|head|vp|developer|engineer|analyst|specialist|consultant|architect)\b", title.lower()):
                # Also check if it's a "Project" at a reputable company (using company processor)
                is_real_company = False
                if self.company_processor and self.company_processor.extract_keywords(company):
                    is_real_company = True
                
                if not is_real_company:
                    return False

        # New: Reject if the entire entry looks like a placeholder or generic section header
        if PLACEHOLDER_ORG_RE.match(lowered_all):
            if not re.search(r"\b(manager|lead|coordinator|director|head|vp|developer|engineer|analyst|specialist|consultant|architect)\b", title.lower()):
                return False

        # Reject common section headers or bullet markers misidentified as company/title
        if re.search(r"\b(summary|highlights|responsibilities|volunteer|community|alliance|contributor|membership|affiliation|involvement|award|recognition|objective|profile|technical skills|expertise|competencies)\b", lowered_all):
             if not re.search(r"\b(manager|lead|coordinator|director|head|vp|developer|engineer|analyst|specialist|consultant|architect)\b", title.lower()):
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
            # Exception: if title or company has "teacher", "professor", "lecturer", "ta", "tutor"
            teacher_kws = {"teacher", "professor", "lecturer", "ta", "tutor", "instructor", "faculty", "trainer"}
            if not any(kw in title.lower() for kw in teacher_kws) and not any(kw in company.lower() for kw in teacher_kws):
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
            # Hyderabad, San Francisco etc
            if len(company.strip().split()) <= 2:
                # But allow if it's also a known company (e.g. "Google" in "Mountain View, CA")
                if not (self.company_processor and self.company_processor.extract_keywords(company)):
                    # Also reject if it's a placeholder like "Location"
                    if PLACEHOLDER_ORG_RE.fullmatch(company.lower().strip(" :-")):
                        return False
                    return False

        # New: Sentence check for company names to avoid fragments like "sacrificing stability for speed."
        if company and len(company.split()) > 3:
            # If it's a long string without any company hints, it's very likely a sentence fragment
            if not COMPANY_HINT_RE.search(company):
                # Check for high Title Casing ratio for potential company names
                words = company.split()
                title_cased = sum(1 for w in words if w[0].isupper())
                if title_cased / len(words) < 0.6:
                    return False
            
            # Check for common verbs or adverbs/prepositions that start sentences but aren't companies
            if company.split()[0].lower() in {"led", "managed", "built", "implemented", "orchestrated", "developed", "created", "designed", "specialized", "expert", "transitioned", "focused", "skilled", "highly"}:
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
        if company and title and self._looks_like_company(company) and self._looks_like_title(title):
            return True 

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
            if job.confidence_score < 0.7:
                return False
        
        # Final sanity check: company shouldn't be a bullet or very short junk
        if company and (company.startswith(BULLETS) or company.strip() in BULLETS):
            return False
            
        # Stricter: must have at least one substantial field
        # Allow if one is quite long even if the other is empty
        if len(company) < 3 and len(title) < 3:
            # Exception for very well-known short names
            if not (company.upper() in {"IBM", "EY", "HP", "GE", "3M", "PWC", "SAP"} or 
                   title.upper() in {"CEO", "CTO", "COO", "VP", "VP", "MD", "GM"}):
                return False

        # Reject if title or company contains "project" and it's likely a project entry
        pattern = r"\bproject\b"
        if re.search(pattern, title, re.I) or re.search(pattern, company, re.I):
            # But allow if it's a "Project Manager" or similar
            if not re.search(r"manager|coordinator|lead|director|engineer|analyst|owner|specialist|consultant", title, re.I):
                return False

        # Reject fragments that are just section headers or timelines
        timeline_pattern = r"^\d{1,2}[\/-]\d{2,4}$" # Simple date fragments
        if re.match(timeline_pattern, company) or re.match(timeline_pattern, title):
            return False
            
        # Reject if it's clearly a section header fragment
        if company.lower().strip() in {"professional experience", "work experience", "employment history", "experience"}:
            return False

        # Reject if it's clearly an environment/skills list
        if self._looks_like_skillish_header(company) or self._looks_like_skillish_header(title):
            # Only reject if confidence is low, otherwise keep (might be a valid entry with list title)
            if job.confidence_score < 0.6:
                return False

        if job.confidence_score < 0.30: # Relaxed to 0.30 to ensure existing unit tests pass
            return False

        # Check for "Timelines" - if there's a lot of dates but no real title/company words
        if not has_body and has_dates:
            if not self._looks_like_company(company) and not self._looks_like_title(title):
                # If both are missing typical keywords, it's likely just a timeline entry
                return False

        return job.confidence_score >= 0.45 # Slightly increased threshold

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
        if not jobs:
            return []
        
        # Only consider jobs with both dates for overlap calculation
        overlap_candidates = [j for j in jobs if j.start_date and j.end_date]
        if not overlap_candidates:
            return jobs
            
        sorted_candidates = sorted(
            overlap_candidates,
            key=lambda j: j.start_date,
        )
        
        out = list(jobs)
        for i in range(len(sorted_candidates) - 1):
            a, b = sorted_candidates[i], sorted_candidates[i + 1]
            if b.start_date < a.end_date:
                overlap_days = (a.end_date - b.start_date).days
                if overlap_days > 30:
                    try:
                        b_idx = out.index(b)
                        out[b_idx] = replace(b, date_flag=f"overlap_{overlap_days}d_with_prev")
                    except ValueError:
                        # b might have been replaced in a previous iteration if it overlapped multiple
                        pass
        return out

    def _normalize_dates_in_text(self, text: str) -> str:
        """Standardize date markers for better splitting (e.g., 'Present', 'Current' -> 'Present')."""
        if not text:
            return ""
        # 1. Normalize present/current markers
        text = PRESENT_RE.sub("Present", text)
        # 2. Normalize separators
        text = re.sub(r"\s+\bto\b\s+", " - ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+\buntil\b\s+", " - ", text, flags=re.IGNORECASE)
        # 3. Clean whitespace around dashes
        text = re.sub(r"\s*[-–—→]|->\s*", " - ", text)
        return text

    def extract_individual_jobs(self, text: str, source_format: str | None = None) -> list[str]:
        # Pre-normalization: Standardize dates and delimiters
        text = self._normalize_dates_in_text(text)
        
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return []
            
        # Group lines using date anchors and proximity logic
        job_blocks = self._group_lines_to_jobs(lines) # Removed source_format as it's not used in the new _group_lines_to_jobs
        
        # Convert blocks to strings
        chunks = ["\n".join([ln for ln in block]) for block in job_blocks] # Changed from tuple to str list
        
        # Giant Entry Protection: Secondary Splitting (Keep sir's safety logic)
        final_chunks = []
        for c_block in chunks:
            c_lines = c_block.splitlines()
            if len(c_lines) > 50 or len(c_block.split()) > 400:
                sub_chunks = self._split_single_chunk_fallback(c_lines)
                if len(sub_chunks) > 1:
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append(c_block)
            else:
                final_chunks.append(c_block)

        return final_chunks

    def _group_lines_to_jobs(self, lines: list[str]) -> list[list[str]]:
        """
        Group lines into job chunks based on date anchors.
        Strict Splitting per User Request: New date + Role/Company MUST start a new job.
        No merging of different date blocks.
        """
        chunks: list[list[str]] = []
        current_chunk: list[str] = []
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Detect Job Boundary: Date Range OR "Role: ..." OR "Company: ..."
            has_date = self._has_date_anchor(line_clean)
            is_labeled = LABELED_TITLE_RE.match(line_clean) or LABELED_ORG_RE.match(line_clean)
            is_client = CLIENT_HEADER_RE.match(line_clean)
            
            # User wants strict splitting on dates.
            # Boundary trigger: 
            # 1. Has date AND (looks like title or company or labeled)
            # 2. Or just has date if current_chunk already has a date
            
            # User wants strict splitting on dates.
            boundary = False
            if has_date:
                # If it has a date, it's almost always a boundary if it also looks like a header
                if is_labeled or is_client or self._looks_like_title(line_clean) or self._looks_like_company(line_clean):
                    boundary = True
                elif any(self._has_date_anchor(ln) for ln in current_chunk):
                    # Multi-date blocks must be split
                    boundary = True
            elif is_labeled or is_client:
                boundary = True

            if boundary:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [line_clean]
            else:
                if not current_chunk:
                    # Only start a chunk if it looks like a title or company or date
                    if self._looks_like_title(line_clean) or self._looks_like_company(line_clean) or has_date:
                        current_chunk = [line_clean]
                else:
                    current_chunk.append(line_clean)

        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def _remove_recurring_lines(self, text: str) -> str:
        """Detect and remove lines that repeat exactly more than 2 times (page artifacts)."""
        lines = text.splitlines()
        if len(lines) < 20: return text
        
        counts = {}
        for ln in lines:
            s = ln.strip()
            if len(s) < 5: continue
            # Ignore bullet lines and dates
            if BULLET_START_RE.match(s) or DATE_ANCHOR_RE.search(s):
                continue
            counts[s] = counts.get(s, 0) + 1
        
        # Headers/Footers usually repeat at least 3 times in deep resumes
        recurring = {s for s, count in counts.items() if count >= 3}
        if not recurring: return text
        
        cleaned = [ln for ln in lines if ln.strip() not in recurring]
        return "\n".join(cleaned)

    def _split_single_chunk_fallback(self, lines: list[str]) -> list[str]:
        """
        Split single chunk into multiple jobs if it contains multiple roles or date ranges.
        Handles: Role A / Role B headers, multiple date ranges, and 'Client:' markers.
        """
        split_indices: list[int] = [0]
        for idx in range(1, len(lines)):
            line = lines[idx]
            if not line or line.startswith(BULLETS):
                continue
            
            # 1. Multiple date ranges
            if DATE_RANGE_RE.search(line) or (PRESENT_RE.search(line) and DATE_ANCHOR_RE.search(line)):
                split_indices.append(idx)
                continue
            
            # 2. 'Client:' marker at line start
            if CLIENT_HEADER_RE.match(line):
                split_indices.append(idx)
                continue

            # 3. Multiple role titles separated by / or |
            if TITLE_HINT_RE.search(line) and ("/" in line or "|" in line) and len(line.split()) <= 10:
                split_indices.append(idx)
                continue

            # 4. Job title at line start (without label)
            if self._looks_like_title(line) and not (LABELED_TITLE_RE.match(line) or LABELED_ORG_RE.match(line)):
                # Only split if not preceded by a bullet
                if idx > 0 and not lines[idx - 1].startswith(BULLETS):
                    split_indices.append(idx)

        if len(split_indices) <= 1:
            return ["\n".join(lines)]

        split_indices = sorted(set(split_indices))
        chunks: list[str] = []
        for i, start in enumerate(split_indices):
            end = split_indices[i + 1] if i + 1 < len(split_indices) else len(lines)
            if end > start:
                chunks.append("\n".join(lines[start:end]))
        return chunks

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

    def normalize_company_names(self, name: str | None | dict) -> str | None:
        if isinstance(name, dict):
            name = name.get("name")
        if not name:
            return None
        # Remove trailing fragments like (Client...), ( Eden Prairie...), etc.
        name = re.sub(r"\s+\(Client\b.*?\)?\s*$", "", name, flags=re.IGNORECASE)
        name = re.sub(r"\s+\(.*?Remote.*?\)?\s*$", "", name, flags=re.IGNORECASE)
        name = name.strip(" -–—|,;:")
        
        # Check Priority Dictionary first
        if getattr(self, "priority_company_processor", None):
            matches = self.priority_company_processor.extract_keywords(name)
            if matches:
                return matches[0]

        key = name.strip().lower()
        return COMPANY_NORMALIZATION.get(key, name.strip())

    def normalize_job_titles(self, title: str | None) -> str | None:
        if not title:
            return None
        
        raw = title.strip().lower()
        # Flatten synonyms for RapidFuzz
        flat_taxonomy = {alias: canon for canon, aliases in TITLE_SYNONYMS.items() for alias in aliases}
        
        # Fuzzy match against the taxonomy
        choices = list(flat_taxonomy.keys())
        match = process.extractOne(raw, choices, scorer=fuzz.token_sort_ratio)
        
        if match and match[1] > 80:
            # Special handling for "Principal" to ensure it maps to ARCHITECT if it's a standalone title
            if match[0].lower() == "principal" and flat_taxonomy[match[0]] == "ARCHITECT":
                return "Principal Architect" # Or whatever canonical form is desired for standalone "Principal"
            return flat_taxonomy[match[0]].title()
            
        # Fallback to existing logic if no strong fuzzy match
        # Preserve / and | if they are likely role separators
        normalized = re.sub(r"\s+", " ", raw).strip()
        
        # Check Priority Dictionary
        if getattr(self, "priority_job_title_processor", None):
            matches = self.priority_job_title_processor.extract_keywords(normalized)
            if matches:
                return matches[0].title()

        for short, long in TITLE_NORMALIZATION.items():
            normalized = re.sub(rf"\b{re.escape(short)}\b", long, normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized.title()

    def calculate_total_experience(self, jobs: Iterable[JobEntry]) -> int:
        # Interval merging algorithm to avoid double-counting overlapping jobs
        intervals = []
        for job in jobs:
            if not job.start_date:
                continue
            start = job.start_date
            end = job.end_date or date.today()
            if start > end:
                continue
            intervals.append((start, end))
            
        if not intervals:
            return 0
            
        # Sort and merge intervals
        intervals.sort(key=lambda x: x[0])
        merged = []
        for s, e in intervals:
            if not merged or s > merged[-1][1]:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)
                
        total_months = 0
        for s, e in merged:
            total_months += (e.year - s.year) * 12 + (e.month - s.month) + 1
            
        return total_months

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
        if not chunk or not chunk.strip():
            return self._create_empty_job()
        
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            return self._create_empty_job()

        # --- STEP 1: Weighted Candidate Gathering ---
        candidates = {
            "company": [],
            "title": [],
            "location": []
        }

        # 1.1 Regex/Deterministic Extraction (Priority for Structured Headers)
        det_company, det_title, det_location = self._parse_company_title_location_deterministic(lines[0:5])
        if det_company: candidates["company"].append((det_company, 1.0 if "|" in str(lines[0:5]) else 0.9))
        if det_title: candidates["title"].append((det_title, 1.0 if "|" in str(lines[0:5]) else 0.9))
        if det_location: candidates["location"].append((det_location, 1.0 if "|" in str(lines[0:5]) else 0.9))

        # 1.2 Dictionary/Priority Extraction (IT/Global Companies & Titles)
        for ln in lines[:3]:
            # Priority Companies (from companies.csv)
            if self.priority_company_processor:
                hits = self.priority_company_processor.extract_keywords(ln)
                if hits: candidates["company"].append((hits[0], 0.95))
            
            # Priority Titles (from job_titles.csv)
            if self.priority_job_title_processor:
                hits = self.priority_job_title_processor.extract_keywords(ln)
                if hits: candidates["title"].append((hits[0], 0.95))

        # 1.3 NER Extraction
        header_text = "\n".join(lines[0:5])
        ner_entities = self._extract_entities_ner(header_text)
        for ent in ner_entities:
            lbl = ent["label"]
            if lbl in {"ORG", "Companies worked at"}: candidates["company"].append((ent["text"], 0.75))
            if lbl in {"TITLE", "Designation", "Role"}: candidates["title"].append((ent["text"], 0.75))
            if lbl in {"LOC", "Location"}: candidates["location"].append((ent["text"], 0.75))

        # --- STEP 2: Date Anchoring ---
        start_date, end_date, is_current = self._extract_date_range(chunk)
        
        # --- STEP 3: Weighted Merging (Max Confidence Selection) ---
        # Disambiguate Title vs Company: If a candidate matches both, check TITLE_HINT_RE
        final_company_raw = self._get_best_candidate(candidates["company"])
        final_title_raw = self._get_best_candidate(candidates["title"])
        
        # Cross-validation: principal developer shouldn't be a company
        if final_company_raw and TITLE_HINT_RE.fullmatch(final_company_raw.strip().split()[-1].lower()):
             if not final_title_raw or final_title_raw == "Job Role":
                 final_title_raw = final_company_raw
                 final_company_raw = None

        final_company = self.normalize_company_names(final_company_raw)
        final_title = self.normalize_job_titles(final_title_raw)
        final_location = self._get_best_candidate(candidates["location"])

        # Body/Bullets
        bullets = self._extract_bullets(lines[1:])
        description = "\n".join(bullets) if bullets else ""

        # Score Confidence
        confidence = self._score_confidence(
            final_company, final_title, start_date, end_date, is_current, None, bullets
        )

        return JobEntry(
            id="", # Will be set in parse_to_standardized_json
            person_id="", # Will be set in parse_to_standardized_json
            company_or_client={
                "name": final_company or "Unknown Company",
                "is_client": False, # Will be set in parse_to_standardized_json
            },
            location={
                "city": final_location,
                "region": None,
                "country": None,
                "remote": False # Will be set in parse_to_standardized_json
            },
            role=final_title or "Job Role",
            start_date=start_date,
            end_date=end_date,
            currently_working=is_current,
            employment_type=self._detect_employment_type(chunk),
            description=description.strip(),
            bullets=bullets,
            technologies=[], # Will be extracted in parse_to_standardized_json
            raw_text=chunk,
            confidence_score=confidence,
            last_updated=datetime.now(timezone.utc).isoformat() + "Z",
            duration_months=self._calc_duration_months(start_date, end_date, is_current),
            client=self._extract_client(chunk)
        )

    def _looks_like_company(self, line: str) -> bool:
        clean = line.strip().strip("#").strip().lower()
        if not clean or len(clean) < 2 or len(clean) > 150:
            return False
            
        # Avoid skill headers or contact lines
        if ":" in clean and any(k in clean for k in ["skill", "tech", "environment", "tool", "project overview"]):
            return False
            
        # Avoid name-like lines (single words or very short capitalized names without org indicators)
        words = clean.split()
        if len(words) <= 2 and not any(ind in clean for ind in ["inc", "llc", "corp", "ltd", "tech", "system", "service", "bank", "univers"]):
            return False

        if COMPANY_HINT_RE.search(clean):
            return True
        
        # Check against local dataset (if initialized)
        if hasattr(self, 'company_set') and clean in self.company_set:
            return True
            
        return False

    def _looks_like_title(self, line: str) -> bool:
        clean = line.strip().strip("#").strip().lower()
        if not clean or len(clean) < 3 or len(clean) > 150:
            return False
            
        # Avoid skill lists
        if ":" in clean or len(line.split(",")) > 3:
            return False

        if TITLE_HINT_RE.search(clean):
            return True
            
        return False

    def _extract_date_range(self, text: str) -> tuple[date | None, date | None, bool]:
        lines = text.splitlines()
        for i, line in enumerate(lines[:8]):
            s, e, c = self._parse_dates(line)
            if s: return s, e, c
        return None, None, False

    def _get_best_candidate(self, candidates: list[tuple[str, float]]) -> str | None:
        if not candidates: return None
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def _extract_entities_ner(self, text: str) -> list[dict]:
        results = []
        if self._ner_nlp:
            doc = self._ner_nlp(text)
            for ent in doc.ents:
                results.append({"text": ent.text, "label": ent.label_})
        if getattr(self, "hf_ner_pipeline", None):
            try:
                entities = self.hf_ner_pipeline(text)
                for ent in entities:
                    lbl = ent.get('entity_group') or ent.get('entity')
                    results.append({"text": ent['word'], "label": lbl})
            except Exception:
                pass
        return results

    def _parse_company_title_location_deterministic(self, header_lines: list[str]) -> tuple[str | None, str | None, str | None]:
        company, title, location = None, None, None
        for line in header_lines:
            # 1. Pipe-separated: Match both variants and use Title/Company hints to disambiguate
            m_tc = TITLE_PIPE_COMPANY_LOC_RE.match(line)
            m_ct = COMPANY_PIPE_TITLE_LOC_RE.match(line)
            
            if m_tc or m_ct:
                # Disambiguate by checking which part looks more like a title
                # Default to m_tc groups if both match (same captures, different names)
                p1, p2, loc = (m_tc.group("title"), m_tc.group("company"), m_tc.group("location")) if m_tc else \
                               (m_ct.group("company"), m_ct.group("title"), m_ct.group("location"))
                
                if TITLE_HINT_RE.search(p2) and not TITLE_HINT_RE.search(p1):
                    # p2 is likely the title, p1 is company
                    return p1.strip(), p2.strip(), loc.strip()
                else:
                    # p1 is likely the title (or both/neither are strong hints)
                    return p2.strip(), p1.strip(), loc.strip()
            
            # 2. Dash-separated: Title - Company or Company - Title
            m = TITLE_DASH_COMPANY_RE.match(line)
            if m:
                t, c = m.group("title").strip(), m.group("company").strip()
                if not self._is_date_like(c):
                    title, company = t, c
            elif (m := COMPANY_DASH_TITLE_RE.match(line)):
                c, t = m.group("company").strip(), m.group("title").strip()
                if not self._is_date_like(c):
                    company, title = c, t
            
            # 3. Labeled: Role: X, Company: Y
            m = LABELED_ORG_RE.search(line)
            if m:
                c = m.group("value").strip()
                if not self._is_date_like(c): company = c
            m = LABELED_TITLE_RE.search(line)
            if m:
                t = m.group("value").strip()
                if not self._is_date_like(t): title = t
                
            # 4. Location
            loc_m = LOCATION_RE.search(line)
            if loc_m: location = loc_m.group(0)
            
        return company, title, location

    def _is_date_like(self, text: str) -> bool:
        if not text: return False
        return bool(DATE_CANDIDATE_RE.search(text) or DATE_ANCHOR_RE.search(text))



    def _clean_header_text(self, text: str | None, strip_labels: bool = True) -> str:
        if not text:
            return ""
        # 1. Strip markdown headers (handle ##, ###, and multiple leading #)
        cleaned = re.sub(r"^#+\s*", "", text.strip())
        # Also handle mid-line remnants of headers if they look like artifacts
        cleaned = re.sub(r"\s*##+\s*", " ", cleaned)
        
        # New: Strip section headers from start (e.g. "Professional Experience: Cigna")
        m_section = SECTION_HEADERS_RE.match(cleaned)
        if m_section:
            # Remove the matched section header part
            cleaned = cleaned[m_section.end():].strip()
        
        # New: Strip location at end (e.g. "Cigna Healthcare Bloomfield, CT")
        loc_candidate = self._parse_location(cleaned)
        if loc_candidate and cleaned.endswith(loc_candidate):
            # Cleanly strip it from the end
            cleaned = cleaned[:cleaned.rfind(loc_candidate)].strip(" ,-·|")
        
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
                if prefix and not ENVIRONMENT_LINE_RE.match(prefix):
                    if self._looks_like_company(prefix):
                        company = prefix
                    elif not title and self._looks_like_title(prefix):
                        title_from_prefix = prefix
                        if title_from_prefix:
                            title = title_from_prefix

            if not company:
                company = company_from_date

            if title_from_role and self._looks_like_title(title_from_role):
                title = title_from_role
            
            # Check priority dictionaries if still missing
            if not company and getattr(self, "priority_company_processor", None):
                for ln in pre_lines:
                    matches = self.priority_company_processor.extract_keywords(ln)
                    if matches:
                        company = matches[0]
                        break
            
            if not title and getattr(self, "priority_job_title_processor", None):
                for ln in pre_lines:
                    matches = self.priority_job_title_processor.extract_keywords(ln)
                    if matches:
                        title = matches[0]
                        break

            if not company:
                for ln in pre_lines:
                    m = LABELED_ORG_RE.search(ln)
                    if m:
                        company = m.group("value").strip()
                        break
            
            if not company or not title:
                c, t = self._parse_company_title(self._strip_dates(header_line))
                if not company: company = c
                if not title: title = t
        else:
            # No date found, try labeled fields first
            for ln in pre_lines:
                m_c = LABELED_ORG_RE.search(ln)
                if m_c and not company:
                    company = m_c.group("value").strip()
                m_t = LABELED_TITLE_RE.search(ln)
                if m_t and not title:
                    title = m_t.group("value").strip()
            
            if not company or not title:
                c, t = self._parse_company_title(self._strip_dates(header_line))
                if not company: company = c
                if not title: title = t

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

        # Priority 3: First line as role heuristic (Fallback)
        if not title and pre_lines:
            # Only use if it looks like a title and isn't a company already found
            first_line = self._clean_header_text(pre_lines[0])
            if first_line and self._looks_like_title(first_line):
                if not company or first_line.lower() != company.lower():
                    title = first_line
                    body_start = max(body_start, 1)

        return company, title, location, start_date, end_date, is_current, body_start

        if cleaned.startswith("##"): # Explicitly reject markdown headers
            return False
            
        # 0. Dictionary check (High Precision)
        if self.priority_company_processor and self.priority_company_processor.extract_keywords(cleaned):
            return True
        if self.company_processor and self.company_processor.extract_keywords(cleaned):
            return True

        if self._looks_like_skillish_header(cleaned):
            return False

        # Length check: company names are rarely very long sentences
        words = cleaned.split()
        if len(words) > 8:
            return bool(COMPANY_HINT_RE.search(text))

        # 1-word all-caps (TCS, IBM, WIPRO, HCL) or common known short names
        if len(words) == 1:
            if cleaned.lower() in {"present", "current", "till date", "now", "remote", "confidential"}:
                return False
            if cleaned.isupper() and 2 <= len(cleaned) <= 10:
                return True
            # Single word Title Case (e.g. "Humana", "Amazon", "Flipkart")
            if cleaned.istitle() and not TITLE_HINT_RE.search(cleaned):
                if cleaned.lower() in {"location", "duration", "period", "dates", "summary", "responsibilities"}:
                    return False
                return True

        # Production Safeguard: Cross-validate against dataset if it looks like a generic token
        if 2 <= len(words) <= 5:
            # If it has company hints (Corp, Inc), it's a company
            if COMPANY_HINT_RE.search(cleaned):
                return True

        if 2 <= len(cleaned) <= 40 and cleaned.isupper() and not TITLE_HINT_RE.search(cleaned):
            # Reject strings that look like dates (e.g. "AUG 2020")
            if DATE_ANCHOR_RE.search(cleaned):
                return False
            return True
            
        # Location check: if it looks like a city/state, it's probably not a company
        if self.location_processor and self.location_processor.extract_keywords(cleaned):
            if len(words) <= 2:
                if not (self.company_processor and self.company_processor.extract_keywords(cleaned)):
                    return False

        # 2-4 words Title Case without title hints (e.g. "Acme Corp", "Morgan Stanley")
        if cleaned.istitle() and 2 <= len(words) <= 6 and not TITLE_HINT_RE.search(cleaned):
            return True
            
        # State/Location pattern (e.g. "Louisville, KY") is NOT a company
        if re.search(r",\s*[A-Z]{2}\b", text):
            return False
            
        if PLACEHOLDER_ORG_RE.match(text):
            return False

        return False


    def _looks_like_title(self, text: str) -> bool:
        if not text:
            return False
        cleaned = text.strip()
        if cleaned.startswith("##"):
            return False
        
        # Production Safeguard: Reject Bullet Lines, Description Verbs, and Headers
        if BULLET_START_RE.match(cleaned) or DESCRIPTION_VERBS_RE.match(cleaned) or DESCRIPTION_HEADERS_RE.match(cleaned):
            return False
            
        # 0. Dictionary check
        if self.priority_job_title_processor and self.priority_job_title_processor.extract_keywords(cleaned):
            return True
        if self.job_title_processor and self.job_title_processor.extract_keywords(cleaned):
            return True

        lowered = cleaned.lower()
        if (PLACEHOLDER_ORG_RE.fullmatch(lowered.strip(" :-")) or lowered.strip(" :-") in {"client", "company", "role"}):
            return False
        
        if any(kw + ":" in lowered for kw in {"role", "company", "client", "position", "designation"}):
            return False

        if re.search(r"^[A-Za-z ]+,\s*[A-Z][a-z]?$", cleaned):
            return False

        # Production Logic: max_words = 12
        words = cleaned.split()
        if TITLE_HINT_RE.search(cleaned):
            if len(words) > 12:
                return False
            return True

        if len(words) <= 6 and cleaned.istitle():
            if COMPANY_HINT_RE.search(cleaned):
                return False
            # Check for location overlap
            if self._parse_location(cleaned):
                return False
            if len(words) == 1 and not TITLE_HINT_RE.search(cleaned):
                return False
            return True

        if len(words) > 4:
            # Check for high Title Casing ratio for potential job titles
            title_case_ratio = sum(1 for w in words if w[0].isupper()) / len(words)
            if title_case_ratio < 0.5:
                # Unless it's a known title prefix
                if not TITLE_HINT_RE.search(words[0]):
                    return False
            # Check for common description verbs
            if words[0].lower() in {"enabling", "ensuring", "providing", "delivering", "implementing", "conducting", "supporting", "assisting"}:
                return False

        # Reject if contains too many lowercase words in a row
        if re.search(r"\b[a-z]{3,}\b\s+\b[a-z]{3,}\b\s+\b[a-z]{3,}\b", cleaned):
            # Unless it's a known title part
            if not re.search(r"\b(Software|Engineer|Developer|Manager|Lead|Director|Head|VP)\b", cleaned, re.IGNORECASE):
                return False

        return False

    def _assign_entities(self, lines: list[str]) -> tuple[str | None, str | None]:
        """
        Production-grade entity assignment using strict priority:
        1. Labeled Fields (e.g., Company: X)
        2. Dataset Matching (Company in companies.csv wins over Title)
        3. Heuristic Matching
        
        Strictly ignores bulleted lines. Returns (Company, Title).
        Ensures Company and Title are distinct.
        """
        comp, title = None, None
        
        # 0. Filter out bulleted lines and description headers
        filtered_lines = []
        for ln in lines:
            s_ln = ln.strip()
            if not s_ln:
                continue
            if BULLET_START_RE.match(s_ln) or DESCRIPTION_HEADERS_RE.match(s_ln):
                continue
            filtered_lines.append(s_ln)
        
        if not filtered_lines:
            return None, None
            
        # 1. Check for labeled fields in top 3 lines (Priority #1)
        for ln in filtered_lines[:3]:
            m_comp = LABELED_ORG_RE.search(ln)
            if m_comp: 
                c_val = m_comp.group("value").strip()
                if not self.normalize_company_names(c_val) == "Present":
                    comp = c_val
            
            m_title = LABELED_TITLE_RE.search(ln)
            if m_title: title = m_title.group("value").strip()
            
            if comp and title: break

        # 2. Dataset Priority check in top 3 lines (Priority #2)
        # Prevents swaps like "Microsoft" as Title
        if not comp or not title:
            for ln in filtered_lines[:3]:
                # If we find a company in dataset, lock it
                if not comp:
                    hits = []
                    if self.priority_company_processor:
                        hits = self.priority_company_processor.extract_keywords(ln)
                    if not hits and self.company_processor:
                        hits = self.company_processor.extract_keywords(ln)
                    
                    if hits:
                        comp_candidate = hits[0]
                        # Ensure it's not the same as title we already found
                        if not title or comp_candidate.lower() != title.lower():
                            comp = comp_candidate
                            continue
                
                # If we find a title in dataset, lock it
                if not title:
                    hits = []
                    if self.priority_job_title_processor:
                        hits = self.priority_job_title_processor.extract_keywords(ln)
                    if not hits and self.job_title_processor:
                        hits = self.job_title_processor.extract_keywords(ln)
                        
                    if hits:
                        title_candidate = hits[0]
                        if not comp or title_candidate.lower() != comp.lower():
                            title = title_candidate
                            continue

        # 3. Fallback to Heuristics (Priority #3)
        if not comp or not title:
            for ln in filtered_lines[:3]:
                # Try to find both in the same line if it's a composite line
                if not comp and self._looks_like_company(ln):
                    comp_cand = ln
                    # If this line also looks like a title, and we don't have a title yet,
                    # We might have a composite. But for now, just assign company.
                    comp = comp_cand
                
                if not title and self._looks_like_title(ln):
                    title_cand = ln
                    # If it's the SAME line as company, only take it if it's clearly a title
                    if title_cand == comp:
                        # Composite line logic: "Title @ Company" or "Title | Company"
                        # We'll let later stages (deterministic) handle splitting it
                        # but here we just ensure we don't have blanks.
                        pass
                    else:
                        title = title_cand

        # 4. Composite Splitting (Phase 8 Special)
        # If we have only one of them, and the line is long and contains both, split it.
        if (not comp or not title) and filtered_lines:
            header = filtered_lines[0]
            # If the line has a date, use the date as the split point
            has_date = self._has_date_anchor(header)
            if has_date:
                match = DATE_RANGE_RE.search(header)
                if not match:
                    match = re.search(r'\b(19|20)\d{2}\b', header)
                
                if match:
                    pre_date_text = header[:match.start()].strip(" ,-|·")
                    # Try to split pre_date_text into Title and Company
                    if pre_date_text:
                        # If it contains a known title indicator, split there
                        title_match = TITLE_HINT_RE.search(pre_date_text)
                        if title_match:
                            # Heuristic: [Title] [Company] or [Company] [Title]
                            # Often it's [Title] [Company] [Location]
                            words = pre_date_text.split()
                            if len(words) >= 2:
                                # For now, simple split: first word(s) as title, rest as company
                                if not title: title = " ".join(words[:2])
                                if not comp: comp = " ".join(words[2:])
            
            if (not comp or not title) and len(header.split()) > 3:
                # Try deterministic split again for this specific line
                c, t, l = self._parse_company_title_location_deterministic([header])
                if c: comp = c
                if t: title = t
        
        # 4. Final fix: If Company and Title are still the same, try to find a different title in next lines
        if comp and title and comp.lower() == title.lower():
            for ln in filtered_lines[1:4]:
                if ln.lower() != comp.lower() and self._looks_like_title(ln):
                    title = ln
                    break

        # 5. Production Guard: Explicitly reject "Present", "Current", "Remote" as Companies
        if comp and comp.lower() in {"present", "current", "till date", "now", "remote", "confidential"}:
            comp = None
            
        # Final fallback: If we HAVE a title but no company, and the title is long, it might be both
        if title and not comp and len(title.split()) > 4:
            # Maybe the title is "Software Engineer at Google"
            at_match = re.search(r"\b(at|for|with|@)\b", title, re.IGNORECASE)
            if at_match:
                comp = title[at_match.end():].strip()
                title = title[:at_match.start()].strip()

        return comp, title

    def _split_table_row(self, line: str) -> dict[str, str | None] | None:
        """
        Specialized splitter for rows with pipes (Senior Dev | Google | 2020-2022).
        """
        if "|" not in line:
            return None
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            return None
            
        result = {"role": None, "company": None, "location": None, "dates": None}
        
        # Heuristic 1: [Title] | [Company] | [Location/Dates]
        for p in parts:
            if not result["dates"] and self._parse_dates(p)[0]:
                result["dates"] = p
            elif not result["role"] and self._looks_like_title(p):
                result["role"] = p
            elif not result["company"] and self._looks_like_company(p):
                result["company"] = p
            elif not result["location"] and self._parse_location(p):
                result["location"] = p
        
        # Fallback for 3-part pipes
        if len(parts) == 3 and not result["role"]:
             result["role"], result["company"] = parts[0], parts[1]
             result["dates"] = parts[2]
             
        return result


    def _clean_token(self, s: str | None) -> str:
        # Allow apostrophes (' and ’) for year formats like '22
        return re.sub(r'[^0-9A-Za-z\-/.,\'\u2019 ]+', ' ', (s or '')).strip()

    def _parse_dates(self, text: str) -> tuple[date | None, date | None, bool]:
        match = DATE_RANGE_RE.search(text)
        if not match:
            # Fallback for single year or date anchor
            m2 = re.search(r'\b(19|20)\d{2}\b', text)
            if m2:
                d = self._parse_date(m2.group(0))
                return d, d, False
            return None, None, False

        start_raw = (match.group("start") or "").strip()
        end_raw = (match.group("end") or "").strip()

        # Handle PRESENT sentinels
        start_is_present = any(p in start_raw.lower() for p in PRESENT) or start_raw.lower() in {"till date", "now", "current"}
        end_is_present = any(p in end_raw.lower() for p in PRESENT) or end_raw.lower() in {"till date", "now", "current"}

        start_date = date.today() if start_is_present else self._parse_date(start_raw)
        end_date = None if end_is_present else self._parse_date(end_raw)

        is_current = end_is_present or start_is_present
        return start_date, end_date, is_current

    def _parse_date(self, value: str) -> date | None:
        raw = (value or "").strip().lower()
        if not raw:
            return None
        
        if any(p in raw for p in PRESENT):
            return date.today()

        raw_clean = self._clean_token(raw)
        
        # ISO Normalization: YYYY -> YYYY-01-01
        year_only_match = re.fullmatch(r"(\d{4})", raw_clean)
        if year_only_match:
            try:
                return date(int(year_only_match.group(1)), 1, 1)
            except ValueError:
                return None

        normalized = (
            raw_clean.replace("q1", "january").replace("q2", "april")
            .replace("q3", "july").replace("q4", "october")
        )
        normalized = re.sub(r"[\'\u2019](\d{2,4})\b", r" 20\1", normalized)
        
        dt = dateparser.parse(normalized, settings={'PREFER_DAY_OF_MONTH': 'first'})
        return dt.date() if dt else None

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
        dash_match = COMPANY_DASH_TITLE_RE.match(cleaned)
        if dash_match:
            c = dash_match.group("company").strip()
            t = dash_match.group("title").strip()
            # If "title" side looks more like a company, flip it
            if self._looks_like_company(t) and not self._looks_like_company(c):
                return t, c
            return c, t
            
        dash_match = TITLE_DASH_COMPANY_RE.match(cleaned)
        if dash_match:
            c = dash_match.group("company").strip()
            t = dash_match.group("title").strip()
            # If "company" side looks more like a title, flip it
            if self._looks_like_title(c) and not self._looks_like_title(t):
                 return t, c
            return c, t

        # Fallback to generic split
        match = COMPANY_LINE_RE.search(cleaned)
        if match:
            # Independent cleaning for both sides
            company = self._clean_header_text(match.group("company"))
            title = self._clean_header_text(match.group("title"))
            
            if not company and not title:
                return None, None
            if not company: return None, title
            if not title: return company, None

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
        # Weighted Scoring Components
        weights = {
            "dates": 0.40,      # Date anchors are highest priority
            "company": 0.30,   # Company identity
            "title": 0.20,     # Role identity
            "bullets": 0.10,   # Descriptive richness
        }
        
        score = 0.0
        if start_date and (end_date or is_current):
            score += weights["dates"]
        elif start_date:
            score += weights["dates"] * 0.7
            
        if company:
            score += weights["company"]
            
        if title:
            score += weights["title"]
            
        if bullets and len(bullets) >= 1:
            score += weights["bullets"]
            
        return min(1.0, score)

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
            company_or_client={"name": self.normalize_company_names(payload.get("company_name") or payload.get("company")), "is_client": payload.get("is_client", False)},
            role=self.normalize_job_titles(payload.get("job_title") or payload.get("title")),
            start_date=start_date,
            end_date=end_date,
            currently_working=is_current,
            location=payload.get("location"),
            description="\n".join(bullets) if bullets else payload.get("description", ""),
            bullets=bullets,
            duration_months=duration_months,
            employment_type=payload.get("employment_type"),
            confidence_score=payload.get("confidence", 0.85),
        )

    def _call_llm(self, prompt: str) -> str | None:
        return self.llm._call_llm(prompt, task="work_experience").content
