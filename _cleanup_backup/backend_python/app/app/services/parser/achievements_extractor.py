from __future__ import annotations

import re
from dataclasses import dataclass


KEYWORD_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bawarded\b", flags=re.IGNORECASE),
    re.compile(r"\bachieved\b", flags=re.IGNORECASE),
    re.compile(r"\brecognized\b", flags=re.IGNORECASE),
    re.compile(r"\btop performer\b", flags=re.IGNORECASE),
    re.compile(r"\bwon\b", flags=re.IGNORECASE),
]


@dataclass(frozen=True)
class AchievementItem:
    text: str
    confidence: float
    source: str


class AchievementsExtractor:
    def extract(
        self,
        *,
        section_text: str | None,
        raw_text: str | None,
        section_confidence: float | None = None,
    ) -> list[AchievementItem]:
        section_text = (section_text or "").strip()
        raw_text = (raw_text or "").strip()

        items: list[AchievementItem] = []

        if section_text and (section_confidence is None or section_confidence >= 0.6):
            items.extend(self._extract_from_section(section_text))

        if not items and raw_text:
            items.extend(self._extract_from_raw_text(raw_text))

        merged: dict[str, AchievementItem] = {}
        for item in items:
            key = self._normalize_key(item.text)
            existing = merged.get(key)
            if not existing or item.confidence > existing.confidence:
                merged[key] = item

        return sorted(merged.values(), key=lambda it: it.confidence, reverse=True)

    def _extract_from_section(self, text: str) -> list[AchievementItem]:
        lines = [self._clean_line(line) for line in text.splitlines()]
        lines = [line for line in lines if line]
        items: list[AchievementItem] = []
        for line in lines:
            if len(line) < 6:
                continue
            items.append(AchievementItem(text=line, confidence=0.85, source="section"))
        return items

    def _extract_from_raw_text(self, raw_text: str) -> list[AchievementItem]:
        lines = [self._clean_line(line) for line in raw_text.splitlines()]
        lines = [line for line in lines if line]

        matches: list[AchievementItem] = []
        for line in lines:
            if len(line) < 8:
                continue
            if self._contains_keyword(line):
                matches.append(
                    AchievementItem(text=line, confidence=0.65, source="fallback")
                )
        return matches

    @staticmethod
    def _clean_line(line: str) -> str:
        cleaned = (line or "").strip()
        cleaned = cleaned.lstrip("-•*\u2022 ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = cleaned.strip(";,. ")
        return cleaned

    @staticmethod
    def _normalize_key(value: str) -> str:
        lowered = (value or "").lower().strip()
        lowered = re.sub(r"\s+", " ", lowered)
        return lowered

    @staticmethod
    def _contains_keyword(line: str) -> bool:
        return any(p.search(line) for p in KEYWORD_PATTERNS)
