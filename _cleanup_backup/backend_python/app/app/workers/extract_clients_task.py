from __future__ import annotations

import logging
import re
import time
from pathlib import Path

import structlog
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.observability import CLIENT_EXTRACTION_TOTAL, CLIENT_EXTRACTIONS_TOTAL
from app.models.parsing_job import ParsingJob
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


_STRONG_CLIENT_RE = re.compile(
    r"client[s]?\s*[:–\-]\s*(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})",
    re.IGNORECASE,
)

_MEDIUM_CLIENT_RES = [
    re.compile(
        r"worked\s+(for|with|at|on-?site\s+at)\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})",
        re.IGNORECASE,
    ),
    re.compile(r"working\s+(at|for|with)\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"project\s+for\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"on-?site\s+at\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"deployed\s+at\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"assigned\s+to\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"engagement\s+with\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"(?:at|@)\s+(?P<name>[A-Za-z0-9][^\n,;\.]{2,40})(?=\s|$)", re.IGNORECASE),
]

_FALSE_POSITIVES = {
    "the team",
    "my team",
    "internal",
    "internal team",
    "project team",
    "our team",
    "client",
    "clients",
    "customer",
    "customers",
}


def _clean_client_name(value: str) -> str:
    name = str(value or "").strip().title()
    name = name.strip(" \t\r\n\"'()[]{}")
    name = re.sub(r"\s+", " ", name).strip()
    name = name.rstrip(" .,:;\u2013\u2014-|")

    lowered = name.lower()
    if not name:
        return ""
    if lowered in _FALSE_POSITIVES:
        return ""
    if lowered.startswith("the ") and lowered[4:] in _FALSE_POSITIVES:
        return ""
    if len(name) < 3:
        return ""
    if len(name) > 200:
        return ""

    return name


def _iter_text_sources(item: dict[str, object]) -> list[str]:
    sources: list[str] = []
    desc = item.get("description")
    if isinstance(desc, str) and desc.strip():
        sources.append(desc)

    bullets = item.get("bullets")
    if isinstance(bullets, list):
        for b in bullets:
            if isinstance(b, str) and b.strip():
                sources.append(b)

    return sources


def _extract_all_clients(text: str) -> list[tuple[str, str]]:
    """Return list of (client_name, confidence) for all clients in text."""
    results = []
    seen = set()

    for m in _STRONG_CLIENT_RE.finditer(text):
        raw = m.group("name").strip().title()
        name = _clean_client_name(raw)
        if name and name.lower() not in seen and len(name) >= 3:
            seen.add(name.lower())
            results.append((name, "high"))

    for pattern in _MEDIUM_CLIENT_RES:
        for m in pattern.finditer(text):
            raw = m.group("name").strip().title()
            name = _clean_client_name(raw)
            if name and name.lower() not in seen and len(name) >= 3:
                seen.add(name.lower())
                results.append((name, "medium"))

    return results


def _extract_first_client(text: str) -> tuple[str, str] | None:
    for line in (text or "").splitlines() or [text]:
        line2 = str(line or "").strip()
        if not line2:
            continue

        m = _STRONG_CLIENT_RE.search(line2)
        if m:
            cleaned = _clean_client_name(m.group("name"))
            if cleaned:
                return cleaned, "high"

        for rx in _MEDIUM_CLIENT_RES:
            m2 = rx.search(line2)
            if m2:
                cleaned = _clean_client_name(m2.group("name"))
                if cleaned:
                    return cleaned, "medium"

    return None


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    queue="parse",
    name="app.workers.extract_clients_task.task_extract_clients",
)
def task_extract_clients(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    CLIENT_EXTRACTIONS_TOTAL.labels(method="deterministic").inc()
    CLIENT_EXTRACTION_TOTAL.labels(method="deterministic").inc()

    structlog.contextvars.bind_contextvars(job_id=job_id)

    session = SessionLocal()
    try:
        job = session.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
        if not job:
            return job_id

        parsed = job.parsed_data or {}
        work_items = parsed.get("work_experience")
        if not isinstance(work_items, list) or not work_items:
            job.last_stage = "extract_clients"
            session.add(job)
            session.commit()
            return job_id

        all_found_clients: list[tuple[str, str]] = []
        updated_work: list[dict[str, object]] = []

        for item in work_items:
            if not isinstance(item, dict):
                continue

            item2: dict[str, object] = dict(item)
            parts = [
                item2.get("description", "") or "",
                "\n".join(item2.get("bullets", []) or []),
                item2.get("company", "") or "",
            ]
            item_text = "\n".join(p for p in parts if p)

            clients = _extract_all_clients(item_text)
            if clients:
                item2["client"] = clients[0][0]
                item2["client_confidence"] = clients[0][1]
                all_found_clients.extend(clients)
            else:
                existing_client = _clean_client_name(str(item2.get("client") or ""))
                if existing_client:
                    all_found_clients.append((
                        existing_client,
                        str(item2.get("client_confidence") or "medium").strip().lower(),
                    ))

            updated_work.append(item2)

        final_clients = list(dict.fromkeys(name for name, _ in all_found_clients))

        sections = parsed.get("sections")
        experience_section = sections.get("experience") if isinstance(sections, dict) else None
        experience_text = ""
        if isinstance(experience_section, dict):
            experience_text = str(experience_section.get("content") or "")
        elif experience_section is not None and hasattr(experience_section, "content"):
            experience_text = str(getattr(experience_section, "content", "") or "")
        if not experience_text and work_items:
            experience_text = "\n".join(
                p
                for item in work_items
                for p in [
                    item.get("description", "") or "",
                    "\n".join(item.get("bullets", []) or []),
                    item.get("company", "") or "",
                ]
                if p
            )
        if experience_text:
            for name, _ in _extract_all_clients(experience_text):
                if name not in final_clients:
                    final_clients.append(name)

        if isinstance(sections, dict):
            projects = sections.get("projects")
            if isinstance(projects, dict):
                proj_text = projects.get("content")
                if isinstance(proj_text, str) and proj_text.strip():
                    for name, _ in _extract_all_clients(proj_text):
                        if name not in final_clients:
                            final_clients.append(name)

        parsed["work_experience"] = updated_work
        parsed["clients"] = final_clients

        debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        debug_bundle = dict(debug_bundle)
        debug_bundle["clients"] = {
            "count": len(final_clients),
            "unique_clients": final_clients[:50],
            "duration_seconds": time.perf_counter() - start_time,
        }
        parsed["debug"] = debug_bundle

        job.parsed_data = parsed
        job.last_stage = "extract_clients"
        session.add(job)
        session.commit()

        logger.info(
            "Deterministic client extraction completed",
            extra={"job_id": job_id, "client_count": len(final_clients)},
        )
        return job_id
    finally:
        session.close()
