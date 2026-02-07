from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import spacy
    from spacy.matcher import PhraseMatcher
except Exception:  # noqa: BLE001
    spacy = None
    PhraseMatcher = None

from app.services.parser.work_experience_parser import JobEntry

logger = logging.getLogger(__name__)


SKILL_CONTEXT_KEYWORDS = {
    "expert": 0.9,
    "advanced": 0.8,
    "proficient": 0.75,
    "experienced": 0.7,
    "led": 0.7,
    "built": 0.65,
    "used": 0.6,
}

RELATED_SKILLS = {
    "react": ["javascript", "html", "css"],
    "node.js": ["javascript"],
    "aws": ["cloud", "devops"],
}


@dataclass(frozen=True)
class SkillMatch:
    name: str
    normalized_name: str
    category: str | None
    confidence: float
    years_experience: int | None
    proficiency: str | None


class SkillExtractor:
    def __init__(self, taxonomy_path: str | None = None, use_spacy: bool = True) -> None:
        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.normalized_map = {
            item["normalized_name"]: item for item in self.taxonomy
        }
        self.synonym_map = self._build_synonym_map(self.taxonomy)
        self.use_spacy = use_spacy and spacy is not None
        self._nlp = None
        self._matcher = None
        if self.use_spacy:
            self._nlp = spacy.blank("xx")
            self._matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
            patterns = [self._nlp.make_doc(item["name"]) for item in self.taxonomy]
            patterns += [self._nlp.make_doc(syn) for syn in self.synonym_map.keys()]
            self._matcher.add("SKILL", patterns)

    def extract_from_skills_section(self, text: str) -> list[SkillMatch]:
        return self._extract_skills(text, base_confidence=0.85)

    def extract_from_work_history(self, jobs: Iterable[JobEntry]) -> list[SkillMatch]:
        matches: list[SkillMatch] = []
        for job in jobs:
            matches.extend(self._extract_skills(job.description, base_confidence=0.6))
        return matches

    def normalize_skills(self, matches: Iterable[SkillMatch]) -> list[SkillMatch]:
        merged: dict[str, SkillMatch] = {}
        for match in matches:
            key = match.normalized_name
            existing = merged.get(key)
            if not existing or match.confidence > existing.confidence:
                merged[key] = match
        return list(merged.values())

    def categorize_skills(self, matches: Iterable[SkillMatch]) -> list[SkillMatch]:
        categorized = []
        for match in matches:
            taxonomy = self.normalized_map.get(match.normalized_name)
            category = taxonomy.get("category") if taxonomy else match.category
            categorized.append(
                SkillMatch(
                    name=match.name,
                    normalized_name=match.normalized_name,
                    category=category,
                    confidence=match.confidence,
                    years_experience=match.years_experience,
                    proficiency=match.proficiency,
                )
            )
        return categorized

    def infer_proficiency(self, text: str, skill: str) -> str | None:
        lowered = text.lower()
        for keyword, score in SKILL_CONTEXT_KEYWORDS.items():
            if keyword in lowered and skill in lowered:
                if score >= 0.8:
                    return "expert"
                if score >= 0.7:
                    return "advanced"
                return "intermediate"
        return None

    def calculate_skill_years(
        self, jobs: Iterable[JobEntry], skill: str
    ) -> int | None:
        months = 0
        for job in jobs:
            if skill.lower() in job.description.lower():
                if job.duration_months:
                    months += job.duration_months
        return int(months / 12) if months else None

    def infer_related_skills(self, matches: Iterable[SkillMatch]) -> list[SkillMatch]:
        related: list[SkillMatch] = []
        present = {match.normalized_name for match in matches}
        for match in matches:
            for rel in RELATED_SKILLS.get(match.normalized_name, []):
                if rel in present:
                    continue
                taxonomy = self.normalized_map.get(rel)
                if taxonomy:
                    related.append(
                        SkillMatch(
                            name=taxonomy["name"],
                            normalized_name=taxonomy["normalized_name"],
                            category=taxonomy.get("category"),
                            confidence=0.4,
                            years_experience=None,
                            proficiency=None,
                        )
                    )
        return related

    def extract_all(
        self, skills_section: str, jobs: Iterable[JobEntry]
    ) -> list[SkillMatch]:
        section_matches = self.extract_from_skills_section(skills_section)
        history_matches = self.extract_from_work_history(jobs)
        all_matches = self.normalize_skills(section_matches + history_matches)

        enriched = []
        for match in all_matches:
            years = self.calculate_skill_years(jobs, match.normalized_name)
            proficiency = self.infer_proficiency(skills_section, match.normalized_name)
            enriched.append(
                SkillMatch(
                    name=match.name,
                    normalized_name=match.normalized_name,
                    category=match.category,
                    confidence=match.confidence,
                    years_experience=years,
                    proficiency=proficiency,
                )
            )
        enriched = self.categorize_skills(enriched)
        enriched.extend(self.infer_related_skills(enriched))
        return self.normalize_skills(enriched)

    def _extract_skills(self, text: str, base_confidence: float) -> list[SkillMatch]:
        matches: list[SkillMatch] = []
        lowered = text.lower()

        for canonical, item in self.normalized_map.items():
            if re.search(rf"\b{re.escape(canonical)}\b", lowered):
                matches.append(
                    SkillMatch(
                        name=item["name"],
                        normalized_name=item["normalized_name"],
                        category=item.get("category"),
                        confidence=base_confidence,
                        years_experience=None,
                        proficiency=None,
                    )
                )

        for synonym, canonical in self.synonym_map.items():
            if re.search(rf"\b{re.escape(synonym)}\b", lowered):
                item = self.normalized_map[canonical]
                matches.append(
                    SkillMatch(
                        name=item["name"],
                        normalized_name=item["normalized_name"],
                        category=item.get("category"),
                        confidence=base_confidence - 0.1,
                        years_experience=None,
                        proficiency=None,
                    )
                )

        if self.use_spacy and self._nlp and self._matcher:
            doc = self._nlp(text)
            for _, start, end in self._matcher(doc):
                span = doc[start:end].text.lower()
                canonical = self.synonym_map.get(span, span)
                item = self.normalized_map.get(canonical)
                if not item:
                    continue
                matches.append(
                    SkillMatch(
                        name=item["name"],
                        normalized_name=item["normalized_name"],
                        category=item.get("category"),
                        confidence=base_confidence,
                        years_experience=None,
                        proficiency=None,
                    )
                )

        return matches

    def _load_taxonomy(self, taxonomy_path: str | None) -> list[dict]:
        path = (
            Path(taxonomy_path)
            if taxonomy_path
            else Path(__file__).resolve().parents[2]
            / "data"
            / "taxonomy"
            / "skills_seed.json"
        )
        if not path.exists():
            logger.warning("Skill taxonomy not found", extra={"path": str(path)})
            return []
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data.get("skills", [])

    @staticmethod
    def _build_synonym_map(taxonomy: list[dict]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for item in taxonomy:
            canonical = item["normalized_name"]
            for synonym in item.get("synonyms", []):
                mapping[synonym.lower()] = canonical
            mapping[item["name"].lower()] = canonical
        return mapping
