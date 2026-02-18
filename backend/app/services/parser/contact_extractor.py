from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable

import phonenumbers
from email_validator import EmailNotValidError, validate_email
import unicodedata

try:
    import spacy
except Exception:  # noqa: BLE001
    spacy = None

logger = logging.getLogger(__name__)


# FREE_EMAIL_DOMAINS = {
#     "gmail.com",
#     "yahoo.com",
#     "outlook.com",
#     "hotmail.com",
#     "icloud.com",
#     "aol.com",
#     "proton.me",
#     "protonmail.com",
# }

# INVALID_CITY_TOKENS = {
#     "team",
#     "hr",
#     "project",
#     "organization",
#     "institution",
#     "designation",
#     "responsibility",
#     "summary",
#     "skills",
#     "experience",
#     "education",
#     "declaration",
# }

# COUNTRY_HINTS = {
#     "usa": "United States",
#     "united states": "United States",
#     "us": "United States",
#     "india": "India",
#     "canada": "Canada",
#     "uk": "United Kingdom",
#     "united kingdom": "United Kingdom",
#     "germany": "Germany",
#     "france": "France",
#     "spain": "Spain",
# }

# STATE_ABBREVIATIONS = {
#     "AL",
#     "AK",
#     "AZ",
#     "AR",
#     "CA",
#     "CO",
#     "CT",
#     "DE",
#     "FL",
#     "GA",
#     "HI",
#     "ID",
#     "IL",
#     "IN",
#     "IA",
#     "KS",
#     "KY",
#     "LA",
#     "ME",
#     "MD",
#     "MA",
#     "MI",
#     "MN",
#     "MS",
#     "MO",
#     "MT",
#     "NE",
#     "NV",
#     "NH",
#     "NJ",
#     "NM",
#     "NY",
#     "NC",
#     "ND",
#     "OH",
#     "OK",
#     "OR",
#     "PA",
#     "RI",
#     "SC",
#     "SD",
#     "TN",
#     "TX",
#     "UT",
#     "VT",
#     "VA",
#     "WA",
#     "WV",
#     "WI",
#     "WY",
# }







FREE_EMAIL_DOMAINS = {
    # Google
    "gmail.com",
    "googlemail.com",
    
    # Microsoft
    "outlook.com",
    "hotmail.com",
    "live.com",
    "msn.com",
    "passport.com",
    
    # Yahoo
    "yahoo.com",
    "yahoo.co.uk",
    "yahoo.co.in",
    "yahoo.fr",
    "yahoo.de",
    "ymail.com",
    "rocketmail.com",
    
    # Apple
    "icloud.com",
    "me.com",
    "mac.com",
    
    # AOL
    "aol.com",
    "aim.com",
    
    # Proton
    "proton.me",
    "protonmail.com",
    "protonmail.ch",
    "pm.me",
    
    # Other Popular Free Services
    "mail.com",
    "gmx.com",
    "gmx.net",
    "zoho.com",
    "zohomail.com",
    "yandex.com",
    "yandex.ru",
    "mail.ru",
    "inbox.com",
    "fastmail.com",
    "tutanota.com",
    "tutanota.de",
    "tuta.io",
    "rediffmail.com",
    "rediff.com",
    
    # Regional Services
    "163.com",
    "126.com",
    "qq.com",
    "sina.com",
    "sohu.com",
    "naver.com",
    "hanmail.net",
    "daum.net",
    "libero.it",
    "virgilio.it",
    "alice.it",
    "tiscali.it",
    "free.fr",
    "laposte.net",
    "orange.fr",
    "web.de",
    "t-online.de",
    "arcor.de",
    
    # Disposable/Temporary
    "tempmail.com",
    "guerrillamail.com",
    "10minutemail.com",
    "throwaway.email",
    "mailinator.com",
}

INVALID_CITY_TOKENS = {
    # Resume Section Headers
    "team",
    "hr",
    "human resources",
    "project",
    "projects",
    "organization",
    "institution",
    "company",
    "designation",
    "position",
    "role",
    "responsibility",
    "responsibilities",
    "summary",
    "objective",
    "profile",
    "skills",
    "skill",
    "technical skills",
    "experience",
    "work experience",
    "professional experience",
    "education",
    "educational background",
    "qualification",
    "qualifications",
    "declaration",
    "references",
    "achievements",
    "awards",
    "certifications",
    "certification",
    "publications",
    "languages",
    "hobbies",
    "interests",
    
    # Common Resume Keywords
    "resume",
    "cv",
    "curriculum vitae",
    "portfolio",
    "contact",
    "contact information",
    "personal details",
    "professional summary",
    "career objective",
    "about me",
    
    # Job-Related Terms
    "employee",
    "employer",
    "manager",
    "director",
    "engineer",
    "developer",
    "analyst",
    "consultant",
    "intern",
    "trainee",
    
    # Generic Terms
    "page",
    "document",
    "file",
    "name",
    "email",
    "phone",
    "address",
    "location",
    "date",
    "present",
    "current",
    "till",
    "ongoing",
}

COUNTRY_HINTS = {
    # United States
    "usa": "United States",
    "united states": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "america": "United States",
    "united states of america": "United States",
    
    # India
    "india": "India",
    "bharat": "India",
    "in": "India",
    
    # Canada
    "canada": "Canada",
    "ca": "Canada",
    
    # United Kingdom
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    "britain": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "northern ireland": "United Kingdom",
    
    # Germany
    "germany": "Germany",
    "deutschland": "Germany",
    "de": "Germany",
    
    # France
    "france": "France",
    "fr": "France",
    
    # Spain
    "spain": "Spain",
    "españa": "Spain",
    "es": "Spain",
    
    # Italy
    "italy": "Italy",
    "italia": "Italy",
    "it": "Italy",
    
    # China
    "china": "China",
    "prc": "China",
    "people's republic of china": "China",
    "cn": "China",
    
    # Japan
    "japan": "Japan",
    "jp": "Japan",
    "nippon": "Japan",
    
    # Australia
    "australia": "Australia",
    "au": "Australia",
    "aus": "Australia",
    
    # Brazil
    "brazil": "Brazil",
    "brasil": "Brazil",
    "br": "Brazil",
    
    # Mexico
    "mexico": "Mexico",
    "méxico": "Mexico",
    "mx": "Mexico",
    
    # Netherlands
    "netherlands": "Netherlands",
    "holland": "Netherlands",
    "nl": "Netherlands",
    
    # Sweden
    "sweden": "Sweden",
    "se": "Sweden",
    
    # Switzerland
    "switzerland": "Switzerland",
    "schweiz": "Switzerland",
    "suisse": "Switzerland",
    "ch": "Switzerland",
    
    # Singapore
    "singapore": "Singapore",
    "sg": "Singapore",
    
    # UAE
    "uae": "United Arab Emirates",
    "united arab emirates": "United Arab Emirates",
    "emirates": "United Arab Emirates",
    
    # Russia
    "russia": "Russia",
    "russian federation": "Russia",
    "ru": "Russia",
    
    # South Korea
    "south korea": "South Korea",
    "korea": "South Korea",
    "kr": "South Korea",
    
    # Poland
    "poland": "Poland",
    "polska": "Poland",
    "pl": "Poland",
    
    # Ireland
    "ireland": "Ireland",
    "eire": "Ireland",
    "ie": "Ireland",
    
    # Pakistan
    "pakistan": "Pakistan",
    "pk": "Pakistan",
    
    # Bangladesh
    "bangladesh": "Bangladesh",
    "bd": "Bangladesh",
    
    # South Africa
    "south africa": "South Africa",
    "za": "South Africa",
}

STATE_ABBREVIATIONS = {
    # US States
    "AL", "Alabama",
    "AK", "Alaska",
    "AZ", "Arizona",
    "AR", "Arkansas",
    "CA", "California",
    "CO", "Colorado",
    "CT", "Connecticut",
    "DE", "Delaware",
    "FL", "Florida",
    "GA", "Georgia",
    "HI", "Hawaii",
    "ID", "Idaho",
    "IL", "Illinois",
    "IN", "Indiana",
    "IA", "Iowa",
    "KS", "Kansas",
    "KY", "Kentucky",
    "LA", "Louisiana",
    "ME", "Maine",
    "MD", "Maryland",
    "MA", "Massachusetts",
    "MI", "Michigan",
    "MN", "Minnesota",
    "MS", "Mississippi",
    "MO", "Missouri",
    "MT", "Montana",
    "NE", "Nebraska",
    "NV", "Nevada",
    "NH", "New Hampshire",
    "NJ", "New Jersey",
    "NM", "New Mexico",
    "NY", "New York",
    "NC", "North Carolina",
    "ND", "North Dakota",
    "OH", "Ohio",
    "OK", "Oklahoma",
    "OR", "Oregon",
    "PA", "Pennsylvania",
    "RI", "Rhode Island",
    "SC", "South Carolina",
    "SD", "South Dakota",
    "TN", "Tennessee",
    "TX", "Texas",
    "UT", "Utah",
    "VT", "Vermont",
    "VA", "Virginia",
    "WA", "Washington",
    "WV", "West Virginia",
    "WI", "Wisconsin",
    "WY", "Wyoming",
    
    # US Territories
    "DC", "District of Columbia",
    "PR", "Puerto Rico",
    "VI", "Virgin Islands",
    "GU", "Guam",
    "AS", "American Samoa",
    "MP", "Northern Mariana Islands",
    
    # Canadian Provinces
    "AB", "Alberta",
    "BC", "British Columbia",
    "MB", "Manitoba",
    "NB", "New Brunswick",
    "NL", "Newfoundland and Labrador",
    "NS", "Nova Scotia",
    "NT", "Northwest Territories",
    "NU", "Nunavut",
    "ON", "Ontario",
    "PE", "Prince Edward Island",
    "QC", "Quebec",
    "SK", "Saskatchewan",
    "YT", "Yukon",
    
    # Australian States
    "NSW", "New South Wales",
    "VIC", "Victoria",
    "QLD", "Queensland",
    "WA", "Western Australia",
    "SA", "South Australia",
    "TAS", "Tasmania",
    "ACT", "Australian Capital Territory",
    "NT", "Northern Territory",
}

NAME_SUFFIXES = {
    # Generational
    "jr",
    "jr.",
    "junior",
    "sr",
    "sr.",
    "senior",
    "i",
    "ii",
    "iii",
    "iv",
    "v",
    "vi",
    "1st",
    "2nd",
    "3rd",
    "4th",
    "5th",
    
    # Academic Degrees
    "phd",
    "ph.d",
    "ph.d.",
    "dphil",
    "edd",
    "ed.d",
    "dsc",
    "dba",
    "md",
    "m.d",
    "m.d.",
    "do",
    "d.o.",
    "dds",
    "d.d.s.",
    "dvm",
    "d.v.m.",
    "jd",
    "j.d",
    "j.d.",
    "llm",
    "ll.m",
    "scd",
    "sc.d",
    
    # Master's Degrees
    "mba",
    "m.b.a",
    "m.b.a.",
    "ms",
    "m.s",
    "m.s.",
    "ma",
    "m.a",
    "m.a.",
    "msc",
    "m.sc",
    "meng",
    "m.eng",
    "mfa",
    "m.f.a",
    "mpa",
    "m.p.a",
    "mph",
    "m.p.h",
    "msw",
    "m.s.w",
    "med",
    "m.ed",
    
    # Bachelor's Degrees
    "ba",
    "b.a",
    "b.a.",
    "bs",
    "b.s",
    "b.s.",
    "bsc",
    "b.sc",
    "beng",
    "b.eng",
    "bba",
    "b.b.a",
    "bfa",
    "b.f.a",
    
    # Professional Titles
    "esq",
    "esq.",
    "esquire",
    "cpa",
    "cfa",
    "pmp",
    "pe",
    "p.e.",
    "rn",
    "r.n.",
    "lpn",
    "l.p.n.",
    "pa",
    "p.a.",
    "aprn",
    "dds",
    
    # Religious/Honorary
    "rev",
    "rev.",
    "reverend",
    "fr",
    "fr.",
    "father",
    "dr",
    "dr.",
    "doctor",
    "prof",
    "prof.",
    "professor",
    "sir",
    "dame",
    "lord",
    "lady",
    
    # Military
    "ret",
    "ret.",
    "retired",
    "usn",
    "usaf",
    "usmc",
    "usa",
}



NAME_SUFFIXES = {"jr", "sr", "phd", "md", "mba", "ii", "iii", "iv"}

EMAIL_REGEX = re.compile(
    r"(?P<email>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
)

URL_REGEX = re.compile(
    r"(?P<url>https?://[^\s)]+|www\.[^\s)]+)", re.IGNORECASE
)

LINKEDIN_REGEX = re.compile(
    r"(https?://)?(www\.)?linkedin\.com/(in|pub)/[A-Za-z0-9\-_%]+",
    re.IGNORECASE,
)
GITHUB_REGEX = re.compile(
    r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_%]+",
    re.IGNORECASE,
)

LOCATION_LABEL_REGEX = re.compile(
    r"\b(location|address|based in)\b\s*[:\-]\s*(?P<value>.+)$",
    re.IGNORECASE,
)

NAME_LABEL_REGEX = re.compile(
    r"\bname\b\s*[:\-]\s*(?P<value>.+)$",
    re.IGNORECASE,
)

SECTION_HINTS = {
    "summary",
    "professional summary",
    "profile",
    "objective",
    "experience",
    "work experience",
    "education",
    "skills",
    "technical skills",
    "certifications",
    "projects",
    "awards",
    "publications",
}


@dataclass(frozen=True)
class EmailResult:
    email: str
    is_primary: bool
    confidence: float


@dataclass(frozen=True)
class PhoneResult:
    phone: str
    confidence: float


@dataclass(frozen=True)
class UrlResult:
    linkedin: str | None
    github: str | None
    websites: list[str]


@dataclass(frozen=True)
class LocationResult:
    city: str | None
    state: str | None
    country: str | None
    confidence: float


@dataclass(frozen=True)
class NameResult:
    name: str | None
    confidence: float


@dataclass(frozen=True)
class ContactResult:
    emails: list[EmailResult]
    phones: list[PhoneResult]
    urls: UrlResult
    location: LocationResult
    name: NameResult


class ContactExtractor:
    def __init__(self, default_region: str | None = "IN") -> None:
        self.default_region = default_region
        self._nlp = None
        if spacy is not None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except Exception:  # noqa: BLE001
                self._nlp = spacy.blank("en")

    @staticmethod
    def _contains_country_hint(text: str, hint: str) -> bool:
        return re.search(rf"\b{re.escape(hint)}\b", text) is not None

    def extract_all(self, raw_text: str) -> ContactResult:
        emails = self.extract_emails(raw_text)
        phones = self.extract_phones(raw_text)
        urls = self.extract_urls(raw_text)
        location = self.extract_location(raw_text)
        name = self.extract_name(raw_text)
        return ContactResult(
            emails=emails,
            phones=phones,
            urls=urls,
            location=location,
            name=name,
        )

    def extract_emails(self, text: str) -> list[EmailResult]:
        repaired = self._repair_common_emails(text)
        candidates = [m.group("email") for m in EMAIL_REGEX.finditer(repaired)]
        normalized = []
        for email in candidates:
            try:
                validated = validate_email(email, check_deliverability=False)
            except EmailNotValidError:
                continue
            normalized.append(validated.email)

        unique_emails = []
        seen = set()
        for email in normalized:
            if email.lower() not in seen:
                unique_emails.append(email)
                seen.add(email.lower())

        scored = [(email, self._email_score(email)) for email in unique_emails]
        scored.sort(key=lambda item: item[1], reverse=True)

        results = []
        for idx, (email, score) in enumerate(scored):
            results.append(
                EmailResult(email=email, is_primary=idx == 0, confidence=score)
            )
        return results

    def extract_phones(self, text: str) -> list[PhoneResult]:
        phones: list[PhoneResult] = []
        seen = set()
        normalized_text = self._normalize_phone_text(text)
        for match in phonenumbers.PhoneNumberMatcher(normalized_text, self.default_region):
            number = match.number
            if not phonenumbers.is_possible_number(number):
                continue
            if not phonenumbers.is_valid_number(number):
                continue
            formatted = phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.E164
            )
            if formatted in seen:
                continue
            seen.add(formatted)
            phones.append(PhoneResult(phone=formatted, confidence=0.8))
        return phones

    def extract_urls(self, text: str) -> UrlResult:
        linkedin = None
        github = None
        websites = []

        for match in LINKEDIN_REGEX.finditer(text):
            linkedin = self._normalize_url(match.group(0))
            break

        for match in GITHUB_REGEX.finditer(text):
            github = self._normalize_url(match.group(0))
            break

        for match in URL_REGEX.finditer(text):
            url = self._normalize_url(match.group("url"))
            if linkedin and url == linkedin:
                continue
            if github and url == github:
                continue
            if url not in websites:
                websites.append(url)

        return UrlResult(linkedin=linkedin, github=github, websites=websites)

    def extract_location(self, text: str) -> LocationResult:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        top_block = lines[:12]
        city = state = country = None
        confidence = 0.0

        for line in top_block:
            match = LOCATION_LABEL_REGEX.search(line)
            if match:
                value = match.group("value").strip()
                city, state, country, confidence = self._parse_location_string(value)
                if city or country:
                    return LocationResult(
                        city=city, state=state, country=country, confidence=confidence
                    )

        for line in top_block:
            match = re.search(r"([A-Za-z .]+),\s*([A-Z]{2})\b", line)
            if match and match.group(2) in STATE_ABBREVIATIONS:
                city = match.group(1).strip()
                state = match.group(2)
                confidence = 0.7
                break

        if not city:
            for line in top_block:
                if self._looks_like_section_header(line):
                    continue
                if len(line) > 60:
                    continue
                tokens = line.split(",")
                if len(tokens) >= 2:
                    candidate_city = tokens[0].strip()
                    country_guess = tokens[-1].strip().lower()
                    country = COUNTRY_HINTS.get(country_guess)
                    if (
                        candidate_city
                        and country
                        and candidate_city.strip().lower() not in INVALID_CITY_TOKENS
                    ):
                        city = candidate_city
                        confidence = 0.6
                        break

        if not country:
            for line in top_block:
                if self._looks_like_section_header(line):
                    continue
                lowered = line.lower()
                for key, value in COUNTRY_HINTS.items():
                    if self._contains_country_hint(lowered, key):
                        country = value
                        confidence = max(confidence, 0.5)
                        break

        if (not country or country == "United States") and re.search(r"\+\s*91\b", text):
            country = "India"
            confidence = max(confidence, 0.6)

        return LocationResult(city=city, state=state, country=country, confidence=confidence)

    def extract_name(self, text: str) -> NameResult:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        top_lines = lines[:30]
        contact_label_re = re.compile(r"\b(?:email|phone|linkedin|github)\b\s*:?", re.IGNORECASE)

        for line in top_lines:
            match = NAME_LABEL_REGEX.search(line)
            if match:
                candidate = match.group("value").strip()
                if self._is_probable_name(candidate):
                    return NameResult(
                        name=self._normalize_name_case(candidate), confidence=0.72
                    )

        if self._nlp:
            doc = self._nlp("\n".join(top_lines))
            for ent in doc.ents:
                if ent.label_ in {"PERSON", "PER"}:
                    name = ent.text.strip()
                    if len(name.split()) <= 5:
                        return NameResult(name=name, confidence=0.75)

        for line in top_lines:
            if self._looks_like_section_header(line):
                continue
            if line.lstrip().startswith(("-", "•", "*", "|")):
                continue
            lowered_line = line.lower()
            if "http" in lowered_line or "www." in lowered_line:
                continue

            # PDFs commonly put name + email/phone on the same line. Strip contact parts and
            # re-evaluate the remaining left segment.
            candidate_line = line
            candidate_line = contact_label_re.sub("", candidate_line).strip()
            candidate_line = EMAIL_REGEX.sub("", candidate_line).strip()
            candidate_line = re.sub(r"\+?\d[\d\s().-]{6,}", "", candidate_line).strip()
            candidate_line = re.sub(r"\b(linkedin|github)\b\s*[:\-]?\s*\S+", "", candidate_line, flags=re.IGNORECASE).strip()

            # If the header line contains separators (common in PDFs), attempt to use the left side.
            if "|" in candidate_line or "·" in candidate_line:
                split_parts = [p.strip() for p in re.split(r"[|·]", candidate_line) if p.strip()]
                if split_parts:
                    candidate_line = split_parts[0]
            candidate_line = candidate_line.strip(" |-·")

            verb_check = re.sub(r"^[^A-Za-z0-9]+", "", candidate_line.strip().lower())
            if re.match(
                r"^(implemented|designed|developed|managed|led|built|created|migrated|deployed|optimized|configured|maintained|delivered)\b",
                verb_check,
            ):
                continue

            words = [w for w in re.split(r"\s+", candidate_line) if w]
            if 2 <= len(words) <= 4:
                cleaned = self._normalize_name_case(" ".join(words))
                cleaned = self._normalize_name_suffix(cleaned)
                if self._is_probable_name(cleaned):
                    return NameResult(name=cleaned, confidence=0.6)

        if len(top_lines) >= 2:
            first = top_lines[0]
            second = top_lines[1]
            if (
                re.match(r"^[A-Za-z.'-]{2,}$", first)
                and re.match(r"^[A-Za-z.'-]{2,}$", second)
                and (first.isupper() or second.isupper())
            ):
                combined = self._normalize_name_case(f"{first} {second}")
                if self._is_probable_name(combined):
                    return NameResult(name=combined, confidence=0.62)

        return NameResult(name=None, confidence=0.0)

    @staticmethod
    def _normalize_url(url: str) -> str:
        if url.startswith("www."):
            return f"https://{url}"
        if not url.startswith("http"):
            return f"https://{url}"
        return url

    def _email_score(self, email: str) -> float:
        domain = email.split("@")[-1].lower()
        if domain == "gmail.com":
            return 0.9
        if domain not in FREE_EMAIL_DOMAINS:
            return 0.8
        return 0.6

    @staticmethod
    def _normalize_name_suffix(name: str) -> str:
        parts = name.split()
        if parts and parts[-1].lower().strip(".") in NAME_SUFFIXES:
            parts[-1] = parts[-1].upper()
        return " ".join(parts)

    @staticmethod
    def _normalize_phone_text(text: str) -> str:
        cleaned = unicodedata.normalize("NFKC", text)
        cleaned = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", cleaned)
        cleaned = re.sub(r"[\u200e\u200f\u202a-\u202e]", "", cleaned)
        return cleaned

    @staticmethod
    def _is_probable_name(value: str) -> bool:
        if not value or "@" in value:
            return False
        if len(value) > 60:
            return False
        words = [w for w in re.split(r"\s+", value.strip()) if w]
        if not (2 <= len(words) <= 4):
            return False
        lowered = value.lower()
        if "," in value or "/" in value or "|" in value or "·" in value:
            return False
        if re.search(
            r"\b(engineer|developer|devops|sre|architect|administrator|admin|manager|lead|analyst|consultant|director|specialist|qa|tester|product|data|scientist|intern)\b",
            lowered,
        ):
            return False
        if re.search(r"\b(and|with|for|to|in|across|optimizing|automating)\b", lowered):
            return False
        if re.match(
            r"^(implemented|designed|developed|managed|led|built|created|migrated|deployed|optimized|configured|maintained|delivered)\b",
            re.sub(r"^[^A-Za-z0-9]+", "", lowered),
        ):
            return False
        if any(word.lower() in {"linkedin", "github", "email", "phone"} for word in words):
            return False
        return all(re.match(r"^[A-Za-z.'-]+$", word) for word in words)

    @staticmethod
    def _repair_common_emails(text: str) -> str:
        # PDF text extraction often inserts whitespace around separators.
        cleaned = str(text or "")
        cleaned = re.sub(r"\s+@\s+", "@", cleaned)
        cleaned = re.sub(r"\s+\.\s+", ".", cleaned)
        cleaned = re.sub(r"\s+\+\s+", "+", cleaned)
        return cleaned

    @staticmethod
    def _normalize_name_case(value: str) -> str:
        if value.isupper():
            return value.title()
        return value

    @staticmethod
    def _looks_like_section_header(line: str) -> bool:
        cleaned = re.sub(r"[^A-Za-z ]+", " ", line).strip().lower()
        cleaned = " ".join(cleaned.split())
        return cleaned in SECTION_HINTS

    def _parse_location_string(
        self, value: str
    ) -> tuple[str | None, str | None, str | None, float]:
        city = state = country = None
        confidence = 0.0
        if not value:
            return city, state, country, confidence
        match = re.search(r"([A-Za-z .]+),\s*([A-Z]{2})\b", value)
        if match and match.group(2) in STATE_ABBREVIATIONS:
            city = match.group(1).strip()
            state = match.group(2)
            confidence = 0.7
            return city, state, country, confidence
        tokens = [token.strip() for token in value.split(",") if token.strip()]
        if len(tokens) >= 2:
            city = tokens[0]
            country_guess = tokens[-1].lower()
            country = COUNTRY_HINTS.get(country_guess)
            if country:
                confidence = 0.6
                return city, state, country, confidence
        lowered = value.lower()
        for key, mapped in COUNTRY_HINTS.items():
            if self._contains_country_hint(lowered, key):
                country = mapped
                confidence = 0.5
                break
        if country:
            return city, state, country, confidence
        return city, state, country, confidence
