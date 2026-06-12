from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, enforce_rate_limit
from app.core.config import get_settings
from app.models.candidate import Candidate
from app.models.parsing_job import ParsingJob, ParsingJobStatus
from app.workers.pipeline import start_parsing_workflow

router = APIRouter(prefix="/admin")


def _require_admin_key(request: Request) -> None:
    settings = get_settings()
    expected = settings.ADMIN_API_KEY
    if not expected:
        raise HTTPException(status_code=403, detail="Admin API disabled")

    provided = request.headers.get("X-Admin-API-Key") or request.headers.get("X-API-Key")
    if not provided or provided != expected:
        raise HTTPException(status_code=403, detail="Forbidden")


def _admin_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "anonymous"
    enforce_rate_limit(f"admin:{ip}", limit=100, per_seconds=60)


def _admin_guard(request: Request) -> None:
    _require_admin_key(request)
    _admin_rate_limit(request)


def _file_type_from_filename(filename: str | None) -> str:
    if not filename:
        return "unknown"
    try:
        ext = Path(filename).suffix.lower().lstrip(".")
        return ext or "unknown"
    except Exception:
        return "unknown"


def _safe_get(parsed: dict[str, Any] | None, key: str, default: Any) -> Any:
    if not isinstance(parsed, dict):
        return default
    return parsed.get(key, default)


@router.get("/jobs/{job_id}/debug")
def admin_job_debug(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_admin_guard),
) -> dict[str, Any]:
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Parsing job not found")

    candidate = db.execute(select(Candidate).where(Candidate.id == job.candidate_id)).scalar_one_or_none()

    parsed = job.parsed_data or {}
    debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}

    sections = parsed.get("sections") if isinstance(parsed.get("sections"), dict) else {}
    sections_detected = [
        str(k)
        for k, v in sections.items()
        if isinstance(v, dict) and str(v.get("content") or "").strip()
    ]

    section_debug = debug_bundle.get("sections") if isinstance(debug_bundle.get("sections"), dict) else {}
    section_map = section_debug.get("section_map") if isinstance(section_debug.get("section_map"), list) else []

    we_debug = debug_bundle.get("work_experience") if isinstance(debug_bundle.get("work_experience"), dict) else {}
    exp_quality_raw = we_debug.get("primary_quality_score")
    experience_quality_score: float | None
    try:
        experience_quality_score = float(exp_quality_raw) if exp_quality_raw is not None else None
        if experience_quality_score is not None and experience_quality_score > 1.0:
            experience_quality_score = max(0.0, min(1.0, experience_quality_score / 2.0))
    except (TypeError, ValueError):
        experience_quality_score = None

    clients: list[str] = []
    work_items = parsed.get("work_experience") if isinstance(parsed.get("work_experience"), list) else []
    for item in work_items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("client") or "").strip()
        if name:
            clients.append(name)
    client_names_found = sorted(set(clients))

    review_flags: list[str] = []
    if candidate and isinstance(candidate.review_flags, dict):
        rf = candidate.review_flags
        for flag in rf.get("rule_flags") or []:
            if flag:
                review_flags.append(str(flag))
        flagged_fields = rf.get("flagged_fields")
        if isinstance(flagged_fields, dict):
            for field_name in flagged_fields.keys():
                review_flags.append(str(field_name))
    review_flags = sorted(set(review_flags))

    confidence_breakdown = parsed.get("confidence_breakdown") if isinstance(parsed.get("confidence_breakdown"), dict) else {}
    weakest_fields = (
        confidence_breakdown.get("weakest_fields")
        if isinstance(confidence_breakdown.get("weakest_fields"), list)
        else []
    )

    status = job.status.value
    if job.status == ParsingJobStatus.SUCCESS:
        status = "completed"

    text_extraction_debug = debug_bundle.get("text_extraction") if isinstance(debug_bundle.get("text_extraction"), dict) else {}

    return {
        "job_id": str(job.id),
        "status": status,
        "file_type": _file_type_from_filename(job.filename),
        "confidence": job.confidence_score,
        "confidence_breakdown": confidence_breakdown,
        "sections_detected": sections_detected,
        "section_map": section_map,
        "experience_quality_score": experience_quality_score,
        "client_names_found": client_names_found,
        "review_flags": review_flags,
        "debug": {
            "text_extraction": text_extraction_debug,
            "sections": section_debug,
            "work_experience": we_debug,
        },
        "weakest_fields": [str(x) for x in weakest_fields if str(x or "").strip()],
    }


@router.get("/jobs/{job_id}/raw_text")
def admin_job_raw_text(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_admin_guard),
) -> PlainTextResponse:
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Parsing job not found")
    text = job.raw_text or ""
    return PlainTextResponse(content=text)


@router.get("/jobs/{job_id}/sections")
def admin_job_sections(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_admin_guard),
) -> dict[str, Any]:
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Parsing job not found")

    parsed = job.parsed_data or {}
    sections = parsed.get("sections") if isinstance(parsed.get("sections"), dict) else {}
    debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
    section_debug = debug_bundle.get("sections") if isinstance(debug_bundle.get("sections"), dict) else {}

    return {
        "job_id": str(job.id),
        "sections": sections,
        "section_map": section_debug.get("section_map") if isinstance(section_debug.get("section_map"), list) else [],
        "detected_headers": section_debug.get("detected_headers") if isinstance(section_debug.get("detected_headers"), list) else [],
    }


@router.post("/jobs/{job_id}/reparse")
def admin_job_reparse(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(_admin_guard),
) -> dict[str, str]:
    job = db.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Parsing job not found")

    new_job = ParsingJob(
        candidate_id=job.candidate_id,
        filename=job.filename,
        file_path=job.file_path,
        original_file_copy_path=job.original_file_copy_path,
        status=ParsingJobStatus.PENDING,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    start_parsing_workflow(str(new_job.id))
    return {"job_id": str(new_job.id)}
