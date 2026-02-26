"""Pretrained NER fallback when regex fails.

Uses spacy.load("en_core_web_sm") for:
- PERSON → Name
- ORG → Company
- DATE → Date
- GPE → Location (Geo-Political Entity: cities, countries, etc.)

Install: python -m spacy download en_core_web_sm
"""
from __future__ import annotations

import logging
from typing import Literal

logger = logging.getLogger(__name__)

_NLP = None
_NLP_LOAD_FAILED = False

EntityLabel = Literal["PERSON", "ORG", "DATE", "GPE"]


def get_nlp():
    """Load en_core_web_sm once. Returns None if unavailable."""
    global _NLP, _NLP_LOAD_FAILED
    if _NLP_LOAD_FAILED:
        return None
    if _NLP is not None:
        return _NLP
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        _NLP = nlp
        return _NLP
    except Exception as exc:  # noqa: BLE001
        logger.debug("spacy en_core_web_sm not available: %s", exc)
        _NLP_LOAD_FAILED = True
        return None


def extract_entities(
    text: str,
    labels: tuple[EntityLabel, ...] = ("PERSON", "ORG", "DATE", "GPE"),
    max_chars: int = 100_000,
) -> dict[str, list[str]]:
    """Extract named entities as fallback when regex fails.

    Returns dict mapping label to list of entity texts, e.g.:
    {"PERSON": ["John Doe"], "GPE": ["San Francisco", "California"], ...}
    """
    nlp = get_nlp()
    if nlp is None or not text or not text.strip():
        return {lb: [] for lb in labels}

    # Truncate to avoid memory issues on huge resumes
    truncated = text[:max_chars] if len(text) > max_chars else text
    doc = nlp(truncated)

    result: dict[str, list[str]] = {lb: [] for lb in labels}
    seen: dict[str, set[str]] = {lb: set() for lb in labels}

    for ent in doc.ents:
        if ent.label_ not in result:
            continue
        val = ent.text.strip()
        if not val or val in seen[ent.label_]:
            continue
        seen[ent.label_].add(val)
        result[ent.label_].append(val)

    return result


def extract_first(
    text: str,
    label: EntityLabel,
) -> str | None:
    """Return first entity of given label, or None."""
    entities = extract_entities(text, labels=(label,))
    vals = entities.get(label, [])
    return vals[0] if vals else None
