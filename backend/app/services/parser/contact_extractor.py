from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable

import phonenumbers
from email_validator import EmailNotValidError, validate_email

try:
    import spacy
except Exception:  # noqa: BLE001
    spacy = None

logger = logging.getLogger(__name__)


FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "aol.com",
    "proton.me",
    "protonmail.com",
}

COUNTRY_HINTS = {
    "usa": "United States",
    "united states": "United States",
    "us": "United States",
    "india": "India",
    "canada": "Canada",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "germany": "Germany",
    "france": "France",
    "spain": "Spain",
}

STATE_ABBREVIATIONS = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
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
    def __init__(self, default_region: str | None = "US") -> None:
        self.default_region = default_region
        self._nlp = None
        if spacy is not None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except Exception:  # noqa: BLE001
                self._nlp = spacy.blank("en")

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
        candidates = [m.group("email") for m in EMAIL_REGEX.finditer(text)]
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
        for match in phonenumbers.PhoneNumberMatcher(text, self.default_region):
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
            match = re.search(r"([A-Za-z .]+),\s*([A-Z]{2})\b", line)
            if match and match.group(2) in STATE_ABBREVIATIONS:
                city = match.group(1).strip()
                state = match.group(2)
                confidence = 0.7
                break

        if not city:
            for line in top_block:
                tokens = line.split(",")
                if len(tokens) >= 2:
                    city = tokens[0].strip()
                    country_guess = tokens[-1].strip().lower()
                    country = COUNTRY_HINTS.get(country_guess)
                    if city and country:
                        confidence = 0.6
                        break

        if not country:
            for line in top_block:
                lowered = line.lower()
                for key, value in COUNTRY_HINTS.items():
                    if key in lowered:
                        country = value
                        confidence = max(confidence, 0.5)
                        break

        return LocationResult(city=city, state=state, country=country, confidence=confidence)

    def extract_name(self, text: str) -> NameResult:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        top_lines = lines[:8]

        if self._nlp:
            doc = self._nlp("\n".join(top_lines))
            for ent in doc.ents:
                if ent.label_ in {"PERSON", "PER"}:
                    name = ent.text.strip()
                    if len(name.split()) <= 5:
                        return NameResult(name=name, confidence=0.75)

        for line in top_lines:
            if "@" in line or re.search(r"\d", line):
                continue
            words = [w for w in re.split(r"\s+", line) if w]
            if 2 <= len(words) <= 4:
                cleaned = " ".join(words)
                cleaned = self._normalize_name_suffix(cleaned)
                return NameResult(name=cleaned, confidence=0.6)

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
