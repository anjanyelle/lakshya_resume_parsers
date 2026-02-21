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
    r"client[s]?\s*[:–\-]\s*(?P<name>[A-Z][^\n,;\.]{2,50})",
    re.IGNORECASE,
)

_MEDIUM_CLIENT_RES = [
    re.compile(
        r"worked\s+(for|with|at|on-?site\s+at)\s+(?P<name>[A-Z][^\n,;\.]{2,50})",
        re.IGNORECASE,
    ),
    re.compile(r"project\s+for\s+(?P<name>[A-Z][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"on-?site\s+at\s+(?P<name>[A-Z][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"deployed\s+at\s+(?P<name>[A-Z][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"assigned\s+to\s+(?P<name>[A-Z][^\n,;\.]{2,50})", re.IGNORECASE),
    re.compile(r"engagement\s+with\s+(?P<name>[A-Z][^\n,;\.]{2,50})", re.IGNORECASE),
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
    name = str(value or "").strip()
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

        all_clients: list[str] = []
        all_clients_set: set[str] = set()

        updated_work: list[dict[str, object]] = []
        for item in work_items:
            if not isinstance(item, dict):
                continue

            item2: dict[str, object] = dict(item)
            existing_client = _clean_client_name(str(item2.get("client") or ""))
            existing_conf = str(item2.get("client_confidence") or "").strip().lower()

            best: tuple[str, str] | None = None
            for src in _iter_text_sources(item2):
                match = _extract_first_client(src)
                if not match:
                    continue
                if best is None:
                    best = match
                    if match[1] == "high":
                        break

            if best and (not existing_client or existing_conf not in {"high", "medium"}):
                item2["client"] = best[0]
                item2["client_confidence"] = best[1]
                existing_client = best[0]

            if existing_client:
                key = existing_client.lower()
                if key not in all_clients_set:
                    all_clients_set.add(key)
                    all_clients.append(existing_client)

            updated_work.append(item2)

        sections = parsed.get("sections")
        if isinstance(sections, dict):
            projects = sections.get("projects")
            if isinstance(projects, dict):
                proj_text = projects.get("content")
                if isinstance(proj_text, str) and proj_text.strip():
                    proj_match = _extract_first_client(proj_text)
                    if proj_match:
                        candidate = proj_match[0]
                        key = candidate.lower()
                        if key not in all_clients_set:
                            all_clients_set.add(key)
                            all_clients.append(candidate)

        parsed["work_experience"] = updated_work
        parsed["clients"] = all_clients

        debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        debug_bundle = dict(debug_bundle)
        debug_bundle["clients"] = {
            "count": len(all_clients),
            "unique_clients": all_clients[:50],
            "duration_seconds": time.perf_counter() - start_time,
        }
        parsed["debug"] = debug_bundle

        job.parsed_data = parsed
        job.last_stage = "extract_clients"
        session.add(job)
        session.commit()

        logger.info(
            "Deterministic client extraction completed",
            extra={"job_id": job_id, "client_count": len(all_clients)},
        )
        return job_id
    finally:
        session.close()
