from __future__ import annotations

import re
from typing import Any

from app.services.parser.work_experience_parser import JobEntry, WorkExperienceParser


def score_work_experience_jobs(jobs: list[JobEntry]) -> float:
    score = 0.0
    if not jobs:
        return score

    for j in jobs:
        company = str(j.company or "").strip()
        title = str(j.title or "").strip()

        if not company and not title:
            continue

        if WorkExperienceParser._looks_like_skillish_header(company) or WorkExperienceParser._looks_like_skillish_header(title):
            score -= 1.5
            continue

        score += 1.0
        if company:
            score += 0.6
        if title:
            score += 0.4

        if j.start_date or j.end_date:
            score += 0.8
        if j.bullets:
            score += min(0.6, 0.1 * len(j.bullets))
        if str(j.description or "").strip():
            score += 0.2

    if len(jobs) >= 12:
        score -= 0.8

    return score


_CERT_SUSPICIOUS_RE = re.compile(r"\b(responsibilities|experience|skills|project|projects|developed|built|designed)\b", re.IGNORECASE)


def score_certifications(validated_items: Any) -> float:
    if not isinstance(validated_items, list) or not validated_items:
        return 0.0

    score = 0.0
    for item in validated_items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        if len(name) > 220:
            score -= 1.0
            continue
        if _CERT_SUSPICIOUS_RE.search(name):
            score -= 0.6
            continue

        score += 1.0

        issuer = str(item.get("issuer") or item.get("provider") or "").strip()
        if issuer:
            score += 0.3

        if item.get("issue_date") or item.get("expiry_date"):
            score += 0.2

    return score
