from __future__ import annotations

import re
from dataclasses import dataclass


_KNOWN_HEADERS: dict[str, str] = {
    "EXPERIENCE": "experience",
    "WORK EXPERIENCE": "experience",
    "PROFESSIONAL EXPERIENCE": "experience",
    "EMPLOYMENT": "experience",
    "EMPLOYMENT HISTORY": "experience",
    "EDUCATION": "education",
    "ACADEMIC BACKGROUND": "education",
    "SKILLS": "skills",
    "TECHNICAL SKILLS": "skills",
    "TECHNICAL": "skills",
    "SUMMARY": "summary",
    "PROFESSIONAL SUMMARY": "summary",
    "OBJECTIVE": "summary",
    "CERTIFICATIONS": "certifications",
    "CERTIFICATION": "certifications",
    "LICENSES": "certifications",
    "PROJECTS": "projects",
    "ACHIEVEMENTS": "achievements",
    "ACCOMPLISHMENTS": "achievements",
    "LANGUAGES": "languages",
    "REFERENCES": "references",
    "PUBLICATIONS": "publications",
    "AWARDS": "awards",
    "VOLUNTEER": "volunteer",
    "VOLUNTEER EXPERIENCE": "volunteer",
}

_DATE_HINT_RE = re.compile(
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b|\b(19|20)\d{2}\b|\b\d{1,2}[\-/]\d{2,4}\b|\bpresent\b",
    re.IGNORECASE,
)

_TECH_HINT_RE = re.compile(
    r"\b(python|java|javascript|typescript|react|node|docker|kubernetes|aws|azure|gcp|sql|postgres|mysql|redis|kafka|spark|terraform|jenkins|git|linux)\b",
    re.IGNORECASE,
)

_DEGREE_HINT_RE = re.compile(
    r"\b(bachelor|master|ph\s*d|b\.?tech|m\.?tech|b\.?sc|m\.?sc|mba|university|college|school)\b",
    re.IGNORECASE,
)

_CERT_HINT_RE = re.compile(
    r"\b(certified|certification|certificate|license|licence|credential|pmp|cka|ckad|aws certified|azure fundamentals)\b",
    re.IGNORECASE,
)


def _normalize_heading(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", value or "").strip().upper()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _is_all_caps_heading(line: str) -> bool:
    stripped = (line or "").strip()
    if not (3 <= len(stripped) <= 50):
        return False
    letters = [c for c in stripped if c.isalpha()]
    if not letters:
        return False
    return all(c.isupper() for c in letters)


def _heading_to_section_key(line: str) -> str | None:
    normalized = _normalize_heading(line)
    if not normalized:
        return None
    if normalized in _KNOWN_HEADERS:
        return _KNOWN_HEADERS[normalized]

    for k, v in _KNOWN_HEADERS.items():
        if normalized == k:
            return v
        if normalized.startswith(k + " ") or (k + " ") in normalized:
            return v

    return None


@dataclass(frozen=True)
class Boundary:
    section_key: str
    line_index: int
    evidence_heading: str
    method: str


class FallbackSegmenter:
    def segment(self, text: str) -> dict[str, dict]:
        raw_lines = (text or "").split("\n")
        if not raw_lines:
            return {}

        boundaries: list[Boundary] = []

        for idx, ln in enumerate(raw_lines):
            candidate = (ln or "").strip()
            if not candidate:
                continue
            if _is_all_caps_heading(candidate):
                section_key = _heading_to_section_key(candidate)
                if section_key:
                    boundaries.append(
                        Boundary(
                            section_key=section_key,
                            line_index=idx,
                            evidence_heading=candidate,
                            method="fallback_allcaps",
                        )
                    )

        if not boundaries:
            for idx, ln in enumerate(raw_lines):
                candidate = (ln or "").strip()
                if not candidate or not candidate.endswith(":"):
                    continue
                head = candidate[:-1].strip()
                section_key = _heading_to_section_key(head)
                if section_key:
                    boundaries.append(
                        Boundary(
                            section_key=section_key,
                            line_index=idx,
                            evidence_heading=candidate,
                            method="fallback_colon",
                        )
                    )

        if not boundaries:
            boundaries = self._density_guess(raw_lines)

        if not boundaries:
            return {}

        boundaries = sorted(boundaries, key=lambda b: b.line_index)

        out: dict[str, dict] = {}
        for i, b in enumerate(boundaries):
            start_idx = b.line_index
            next_start = boundaries[i + 1].line_index if i + 1 < len(boundaries) else len(raw_lines)
            content_lines = raw_lines[start_idx + 1 : next_start]
            content = "\n".join(content_lines).strip()
            start_line = start_idx + 1
            end_line = max(start_line, next_start)

            confidence = 0.6
            if b.method == "fallback_allcaps":
                confidence = 0.75
            elif b.method == "fallback_colon":
                confidence = 0.7
            elif b.method == "fallback_density":
                confidence = 0.62

            out[b.section_key] = {
                "content": content,
                "confidence": confidence,
                "start_line": int(start_line),
                "end_line": int(end_line),
                "evidence_heading": b.evidence_heading,
                "method": b.method,
            }

        return out

    def _density_guess(self, raw_lines: list[str]) -> list[Boundary]:
        window = 10
        best: dict[str, tuple[int, float]] = {}

        def score_slice(lines: list[str]) -> dict[str, float]:
            joined = "\n".join([ln for ln in lines if ln and ln.strip()])
            if not joined.strip():
                return {}
            return {
                "experience": float(len(_DATE_HINT_RE.findall(joined))),
                "skills": float(len(_TECH_HINT_RE.findall(joined))),
                "education": float(len(_DEGREE_HINT_RE.findall(joined))),
                "certifications": float(len(_CERT_HINT_RE.findall(joined))),
            }

        for start in range(0, max(1, len(raw_lines) - 1)):
            end = min(len(raw_lines), start + window)
            scores = score_slice(raw_lines[start:end])
            for key, sc in scores.items():
                if sc <= 0:
                    continue
                prev = best.get(key)
                if prev is None or sc > prev[1]:
                    best[key] = (start, sc)

        if not best:
            return []

        boundaries: list[Boundary] = []
        for key, (start_idx, _) in best.items():
            evidence = raw_lines[start_idx].strip() if raw_lines[start_idx].strip() else key.upper()
            boundaries.append(
                Boundary(
                    section_key=key,
                    line_index=start_idx,
                    evidence_heading=evidence,
                    method="fallback_density",
                )
            )

        boundaries = sorted(boundaries, key=lambda b: b.line_index)
        dedup: list[Boundary] = []
        seen: set[str] = set()
        for b in boundaries:
            if b.section_key in seen:
                continue
            seen.add(b.section_key)
            dedup.append(b)
        return dedup
