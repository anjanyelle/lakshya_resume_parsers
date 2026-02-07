from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable

try:
    import spacy
    from spacy.matcher import PhraseMatcher
except Exception:  # noqa: BLE001
    spacy = None
    PhraseMatcher = None

logger = logging.getLogger(__name__)


SECTION_KEYS = [
    "contact",
    "summary",
    "experience",
    "education",
    "skills",
    "certifications",
    "projects",
    "awards",
    "languages",
    "publications",
]


SECTION_ALIASES: dict[str, list[str]] = {
    "contact": [
        "contact information",
        "personal details",
        "contact",
        "datos personales",
        "información de contacto",
        "detalles personales",
        "coordonnées",
        "détails personnels",
        "kontakt",
        "persönliche daten",
        "संपर्क जानकारी",
        "व्यक्तिगत विवरण",
    ],
    "summary": [
        "professional summary",
        "summary",
        "objective",
        "profile",
        "resumen profesional",
        "perfil",
        "résumé professionnel",
        "profil",
        "zusammenfassung",
        "profil",
        "सारांश",
        "उद्देश्य",
    ],
    "experience": [
        "work experience",
        "professional experience",
        "employment history",
        "experience",
        "experiencia profesional",
        "historial laboral",
        "expérience professionnelle",
        "historique professionnel",
        "berufserfahrung",
        "erfahrung",
        "अनुभव",
        "कार्य अनुभव",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "educación",
        "formación académica",
        "formation",
        "parcours académique",
        "ausbildung",
        "bildung",
        "शिक्षा",
        "शैक्षिक योग्यता",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "skills & tools",
        "habilidades",
        "competencias",
        "compétences",
        "compétences techniques",
        "fähigkeiten",
        "kenntnisse",
        "कौशल",
        "तकनीकी कौशल",
    ],
    "certifications": [
        "certifications",
        "licenses",
        "certificates",
        "certificaciones",
        "licencias",
        "certifications",
        "licences",
        "zertifizierungen",
        "lizenzen",
        "प्रमाणपत्र",
        "लाइसेंस",
    ],
    "projects": [
        "projects",
        "portfolio",
        "case studies",
        "proyectos",
        "portfolio",
        "projets",
        "portfolio",
        "projekte",
        "portfolio",
        "परियोजनाएं",
        "पोर्टफोलियो",
    ],
    "awards": [
        "awards",
        "honors",
        "achievements",
        "premios",
        "honores",
        "récompenses",
        "distinctions",
        "auszeichnungen",
        "ehrungen",
        "पुरस्कार",
        "सम्मान",
    ],
    "languages": [
        "languages",
        "language skills",
        "idiomas",
        "langues",
        "sprachen",
        "भाषाएँ",
    ],
    "publications": [
        "publications",
        "patents",
        "papers",
        "publicaciones",
        "patentes",
        "publications",
        "brevets",
        "veröffentlichungen",
        "patente",
        "प्रकाशन",
        "पेटेंट",
    ],
}


SECTION_REGEX: dict[str, re.Pattern[str]] = {
    key: re.compile(
        r"^\s*(?:"
        + "|".join(re.escape(alias) for alias in aliases)
        + r")\s*$",
        re.IGNORECASE,
    )
    for key, aliases in SECTION_ALIASES.items()
}


KEYWORD_HINTS: dict[str, list[str]] = {
    "experience": [
        "company",
        "employer",
        "responsibilities",
        "role",
        "duration",
        "project",
        "client",
    ],
    "education": ["university", "college", "degree", "gpa", "b.sc", "m.sc"],
    "skills": ["python", "java", "sql", "aws", "docker", "kubernetes"],
    "certifications": ["certified", "license", "certification"],
    "projects": ["project", "built", "developed", "implemented"],
    "awards": ["award", "honor", "achievement"],
    "languages": ["english", "spanish", "french", "german", "hindi"],
    "publications": ["publication", "paper", "journal", "patent"],
}


@dataclass(frozen=True)
class SectionResult:
    content: str
    confidence: float


class SectionParser:
    def __init__(self, use_spacy: bool = True) -> None:
        self.use_spacy = use_spacy and spacy is not None
        self._nlp = None
        self._matcher = None
        if self.use_spacy:
            self._nlp = spacy.blank("xx")
            self._matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
            for key, aliases in SECTION_ALIASES.items():
                patterns = [self._nlp.make_doc(alias) for alias in aliases]
                self._matcher.add(key, patterns)

    def parse(self, raw_text: str) -> dict[str, SectionResult]:
        lines = self._prepare_lines(raw_text)
        header_map = self._detect_headers(lines)
        sections = self._slice_sections(lines, header_map)
        scored = self._score_sections(sections)
        return scored

    def _prepare_lines(self, text: str) -> list[str]:
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in cleaned.split("\n")]
        lines = [line for line in lines if line]
        normalized_lines = [self._normalize_table_row(line) for line in lines]
        return normalized_lines

    @staticmethod
    def _normalize_table_row(line: str) -> str:
        if "  " in line:
            parts = [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]
            if len(parts) > 1:
                return " | ".join(parts)
        return line

    def _detect_headers(self, lines: list[str]) -> dict[int, str]:
        header_map: dict[int, str] = {}
        for idx, line in enumerate(lines):
            for key, pattern in SECTION_REGEX.items():
                if pattern.match(line):
                    header_map[idx] = key
                    break

        if self.use_spacy and self._nlp and self._matcher:
            doc = self._nlp("\n".join(lines))
            matches = self._matcher(doc)
            for match_id, start, end in matches:
                match_text = doc[start:end].text.strip()
                for idx, line in enumerate(lines):
                    if match_text.lower() == line.lower():
                        key = self._nlp.vocab.strings[match_id]
                        header_map.setdefault(idx, key)
        return header_map

    def _slice_sections(
        self, lines: list[str], header_map: dict[int, str]
    ) -> dict[str, list[str]]:
        if not header_map:
            return {"unknown": lines}

        sorted_headers = sorted(header_map.items(), key=lambda item: item[0])
        sections: dict[str, list[str]] = {}
        for i, (idx, key) in enumerate(sorted_headers):
            start = idx + 1
            end = sorted_headers[i + 1][0] if i + 1 < len(sorted_headers) else len(lines)
            content = lines[start:end]
            sections.setdefault(key, []).extend(content)
        return sections

    def _score_sections(
        self, sections: dict[str, list[str]]
    ) -> dict[str, SectionResult]:
        results: dict[str, SectionResult] = {}
        for key, content_lines in sections.items():
            text = "\n".join(content_lines).strip()
            confidence = self._base_confidence(key)
            confidence += self._keyword_boost(key, text)
            confidence = min(confidence, 1.0)
            results[key] = SectionResult(content=text, confidence=confidence)
        return results

    def _base_confidence(self, key: str) -> float:
        if key in SECTION_KEYS:
            return 0.6
        return 0.3

    def _keyword_boost(self, key: str, text: str) -> float:
        hints = KEYWORD_HINTS.get(key, [])
        if not hints or not text:
            return 0.0
        hits = sum(1 for hint in hints if hint.lower() in text.lower())
        return min(0.1 * hits, 0.3)
