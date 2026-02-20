from __future__ import annotations

import json
import logging
import re
import shutil
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from celery import chain
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

import structlog

from app.core.config import get_settings
from app.core.encryption import set_current_tenant
import dateparser
from app.core.database import SessionLocal
from app.core.observability import (
    increment_jobs_total,
    observe_parsing_failure,
    observe_parsing_success,
    observe_stage_duration,
)
from app.models import (
    Candidate,
    CandidateAchievement,
    CandidateSkill,
    Certification,
    Education,
    ParsingJob,
    ReviewStatus,
    Skill,
    WorkHistory,
)
from app.models.candidate import CandidateStatus
from app.models.parsing_job import ParsingJobStatus
from app.models.candidate_skill import ProficiencyLevel
from app.data.taxonomy.certifications_top import CERTIFICATION_ALIASES
from app.data.taxonomy.degree_taxonomy import DEGREE_ALIASES
from app.services.parser.certification_parser import CertificationParser
from app.services.parser.contact_extractor import ContactExtractor
from app.services.parser.education_parser import EducationParser
from app.services.parser.normalize import normalize_resume_text
from app.services.parser.section_parser import SectionParser
from app.services.parser.achievements_extractor import AchievementsExtractor
from app.services.parser.certification_validator import CertificationValidator
from app.services.parser.skill_extractor import SkillExtractor, SkillMatch
from app.services.parser.work_experience_parser import JobEntry, WorkExperienceParser
from app.services.llm_service import LLMParsingService
from app.utils.pii import hash_value
from app.utils.review import apply_correction_patterns, compute_review_flags, find_date_overlaps
from app.services.storage import copy_s3_object, save_bytes_to_local, upload_bytes_to_s3
from app.workers.celery_app import celery_app
from app.workers.extract_text_task import extract_text_task
from app.services.parser.section_boundary_extractor import extract_certifications
from app.services.parser.section_boundary_extractor import _clean_summary_text

_EXAM_CODE_PATTERN = re.compile(
    r"\b("
    r"(AZ|DP|SC|PL|AI|MB)-\d{2,3}"
    r"|SAA-[A-Z0-9]+"
    r"|DVA-[A-Z0-9]+"
    r"|SOA-[A-Z0-9]+"
    r"|1Z0-\d{2,4}"
    r"|SY0-\d{3}"
    r"|200-\d{3}"
    r"|CKA|CKAD|PMP|CISA|CISM|CISSP"
    r")\b",
    re.IGNORECASE,
)

logger = logging.getLogger(__name__)


def start_parsing_workflow(job_id: str) -> str:
    structlog.contextvars.bind_contextvars(job_id=job_id)
    try:
        import sentry_sdk

        sentry_sdk.set_tag("job_id", job_id)
    except Exception:
        pass
    increment_jobs_total()
    settings = get_settings()

    if settings.PARSING_MODE.lower() == "text_only":
        workflow = chain(
            task_extract_text.s(job_id),
            task_clean_text.s(),
            task_finalize_text_only.s(),
        )
    elif settings.PARSING_MODE.lower() == "deterministic":
        workflow = chain(
            task_extract_text.s(job_id),
            task_clean_text.s(),
            task_detect_sections.s(),
            task_extract_contact_info.s(),
            task_parse_work_experience.s(),
            task_parse_education.s(),
            task_parse_certifications.s(),
            task_extract_achievements.s(),
            task_extract_skills.s(),
            task_taxonomy_mapping.s(),
            task_calculate_confidence.s(),
            task_save_to_database.s(),
        )
    else:
        workflow = chain(
            task_extract_text.s(job_id),
            task_clean_text.s(),
            # Pass 1 → Section Detection
            task_detect_sections.s(),
            task_detect_resume_sections.s(),
            # Pass 2 → Entity Extraction
            task_extract_contact_info.s(),
            task_parse_work_experience.s(),
            task_parse_education.s(),
            task_parse_certifications.s(),
            task_extract_achievements.s(),
            task_extract_personal_info.s(),
            task_extract_structured_resume.s(),
            task_normalize_structured_resume.s(),
            task_extract_work_experience_details.s(),
            task_llm_resume_parse.s(),
            task_classify_resume_type.s(),
            # Pass 3 → Skill Inference
            task_extract_skills.s(),
            task_extract_experience_skills.s(),
            # Pass 4 → Normalization
            task_normalize_education_details.s(),
            task_normalize_skills_llm.s(),
            task_taxonomy_mapping.s(),
            # Pass 5 → Confidence Scoring
            task_calculate_total_experience.s(),
            task_evaluate_extraction_confidence.s(),
            task_calculate_confidence.s(),
            # Pass 6 → Validation
            task_verify_extracted_data.s(),
            task_save_to_database.s(),
        )

    force_local = settings.ENVIRONMENT.lower() in {"development", "local"}
    session = SessionLocal()
    try:
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == job_id)
        ).scalar_one_or_none()
        if job:
            job.status = ParsingJobStatus.PROCESSING
            job.started_at = datetime.now(timezone.utc)
            job.completed_at = None
            job.error_message = None
            if force_local:
                job.task_id = f"local-{job_id}"
                job.last_stage = "local"
            else:
                job.task_id = None
                job.last_stage = "queued"
            session.commit()
    finally:
        session.close()

    def _run_local() -> str:
        current_job_id = job_id
        tasks = [task_extract_text, task_clean_text]
        if settings.PARSING_MODE.lower() == "text_only":
            tasks.append(task_finalize_text_only)
        elif settings.PARSING_MODE.lower() == "deterministic":
            tasks.extend(
                [
                    task_detect_sections,
                    task_extract_contact_info,
                    task_parse_work_experience,
                    task_parse_education,
                    task_parse_certifications,
                    task_extract_achievements,
                    task_extract_skills,
                    task_taxonomy_mapping,
                    task_calculate_confidence,
                    task_save_to_database,
                ]
            )
        else:
            tasks.extend(
                [
                    # Pass 1 → Section Detection
                    task_detect_sections,
                    task_detect_resume_sections,
                    # Pass 2 → Entity Extraction
                    task_extract_contact_info,
                    task_parse_work_experience,
                    task_parse_education,
                    task_parse_certifications,
                    task_extract_achievements,
                    task_extract_personal_info,
                    task_extract_structured_resume,
                    task_normalize_structured_resume,
                    task_extract_work_experience_details,
                    task_llm_resume_parse,
                    task_classify_resume_type,
                    # Pass 3 → Skill Inference
                    task_extract_skills,
                    task_extract_experience_skills,
                    # Pass 4 → Normalization
                    task_normalize_education_details,
                    task_normalize_skills_llm,
                    task_taxonomy_mapping,
                    # Pass 5 → Confidence Scoring
                    task_calculate_total_experience,
                    task_evaluate_extraction_confidence,
                    task_calculate_confidence,
                    # Pass 6 → Validation
                    task_verify_extracted_data,
                    task_save_to_database,
                ]
            )

        for task in tasks:
            result = task.apply(args=[current_job_id])
            current_job_id = result.get() if result else current_job_id
        return f"local-{job_id}"

    if force_local:
        return _run_local()

    try:
        result = workflow.apply_async()
        result_id = result.id
        session = SessionLocal()
        try:
            job = session.execute(
                select(ParsingJob).where(ParsingJob.id == job_id)
            ).scalar_one_or_none()
            if job and job.status == ParsingJobStatus.PROCESSING:
                job.task_id = result_id
                job.last_stage = "queued"
                session.commit()
        finally:
            session.close()
        return result_id
    except Exception as exc:
        logger.warning(
            "Celery unavailable; running workflow locally",
            extra={"job_id": job_id, "error": str(exc)},
        )
        session = SessionLocal()
        try:
            job = session.execute(
                select(ParsingJob).where(ParsingJob.id == job_id)
            ).scalar_one_or_none()
            if job and job.status == ParsingJobStatus.PROCESSING:
                job.task_id = f"local-{job_id}"
                job.last_stage = "local"
                session.commit()
        finally:
            session.close()
        return _run_local()


def _load_job(job_id: str) -> ParsingJob:
    session = SessionLocal()
    try:
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == job_id)
        ).scalar_one_or_none()
        if not job:
            raise ValueError(f"ParsingJob not found: {job_id}")
        session.expunge(job)
        return job
    finally:
        session.close()


def _update_job(
    job_id: str,
    *,
    status: ParsingJobStatus | None = None,
    last_stage: str | None = None,
    parsed_data: dict | None = None,
    raw_text: str | None = None,
    confidence_score: float | None = None,
    error_message: str | None = None,
    completed: bool = False,
) -> None:
    session = SessionLocal()
    try:
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == job_id)
        ).scalar_one_or_none()
        if not job:
            return
        if status:
            job.status = status
        if last_stage:
            job.last_stage = last_stage
        if raw_text is not None:
            job.raw_text = raw_text
        if parsed_data is not None:
            job.parsed_data = parsed_data
        if confidence_score is not None:
            job.confidence_score = confidence_score
        if error_message is not None:
            job.error_message = error_message
        if completed:
            job.completed_at = datetime.now(timezone.utc)
        session.commit()
    finally:
        session.close()


def _merge_parsed(job: ParsingJob, updates: dict[str, Any]) -> dict[str, Any]:
    base = job.parsed_data or {}
    base.update(updates)
    return base


def _coerce_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_skill_name(value: str) -> str:
    return " ".join(value.lower().strip().split())


def _get_first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def _apply_llm_resume(parsed: dict[str, Any]) -> dict[str, Any]:
    llm_resume = parsed.get("llm_resume")
    if not isinstance(llm_resume, dict):
        llm_resume = {}

    merged = dict(parsed)
    personal_info = merged.get("personal_info") or {}
    candidate_info = (
        llm_resume.get("candidate_information")
        or llm_resume.get("candidate_info")
        or llm_resume.get("candidate")
        or {}
    )
    if isinstance(candidate_info, dict):
        contact = merged.get("contact") or {}
        if not contact:
            contact = {}

        name = _get_first(candidate_info, "full_name", "name")
        email = _get_first(candidate_info, "email")
        phone = _get_first(candidate_info, "phone")
        location = _get_first(candidate_info, "location")
        linkedin = _get_first(candidate_info, "linkedin", "linkedin_url")
        github = _get_first(candidate_info, "github", "github_url")

        contact.setdefault("name", {})
        if name and not contact["name"].get("name"):
            contact["name"] = {"name": name, "confidence": 0.7}

        if email and not contact.get("emails"):
            contact["emails"] = [{"email": email, "confidence": 0.7}]
        if phone and not contact.get("phones"):
            contact["phones"] = [{"phone": phone, "confidence": 0.7}]

        contact.setdefault("location", {})
        if location and not contact["location"].get("city"):
            contact["location"] = {"city": location, "confidence": 0.6}

        contact.setdefault("urls", {})
        if linkedin and not contact["urls"].get("linkedin"):
            contact["urls"]["linkedin"] = linkedin
        if github and not contact["urls"].get("github"):
            contact["urls"]["github"] = github

        merged["contact"] = contact

    if isinstance(personal_info, dict) and personal_info:
        contact = merged.get("contact") or {}
        contact.setdefault("name", {})
        contact.setdefault("location", {})
        contact.setdefault("urls", {})

        if personal_info.get("full_name") and not contact["name"].get("name"):
            contact["name"] = {"name": personal_info.get("full_name"), "confidence": 0.7}
        if personal_info.get("email") and not contact.get("emails"):
            contact["emails"] = [
                {"email": personal_info.get("email"), "confidence": 0.7}
            ]
        if personal_info.get("phone") and not contact.get("phones"):
            contact["phones"] = [
                {"phone": personal_info.get("phone"), "confidence": 0.7}
            ]
        if personal_info.get("location") and not contact["location"].get("city"):
            contact["location"] = {
                "city": personal_info.get("location"),
                "confidence": 0.6,
            }
        if personal_info.get("linkedin") and not contact["urls"].get("linkedin"):
            contact["urls"]["linkedin"] = personal_info.get("linkedin")
        if personal_info.get("github") and not contact["urls"].get("github"):
            contact["urls"]["github"] = personal_info.get("github")

        merged["contact"] = contact

    if "skills" not in merged or not merged.get("skills"):
        technical_skills = llm_resume.get("technical_skills") or {}
        skills: dict[str, dict[str, Any]] = {}
        if isinstance(technical_skills, dict):
            for category, items in technical_skills.items():
                for item in _coerce_list(items):
                    if not item:
                        continue
                    if isinstance(item, dict):
                        name = item.get("name") or item.get("skill_name")
                    else:
                        name = str(item)
                    if not name:
                        continue
                    normalized = _normalize_skill_name(name)
                    skills[normalized] = {
                        "name": name,
                        "normalized_name": normalized,
                        "category": category,
                    }
        if skills:
            merged["skills"] = list(skills.values())

    if "work_experience" not in merged or not merged.get("work_experience"):
        experience = (
            llm_resume.get("project_client_experience")
            or llm_resume.get("client_experience")
            or llm_resume.get("projects")
            or []
        )
        work_items = []
        for entry in _coerce_list(experience):
            if not isinstance(entry, dict):
                continue
            responsibilities = entry.get("responsibilities")
            if isinstance(responsibilities, list):
                description = "; ".join([str(item) for item in responsibilities if item])
            else:
                description = str(responsibilities) if responsibilities else None
            work_items.append(
                {
                    "company": _get_first(entry, "client_name", "company", "client"),
                    "title": _get_first(entry, "role", "title"),
                    "start_date": _get_first(entry, "start_date"),
                    "end_date": _get_first(entry, "end_date"),
                    "is_current": entry.get("is_current", False),
                    "location": _get_first(entry, "location"),
                    "description": description,
                }
            )
        if work_items:
            merged["work_experience"] = work_items

    if "education" not in merged or not merged.get("education"):
        education = llm_resume.get("education") or []
        edu_items = []
        for entry in _coerce_list(education):
            if not isinstance(entry, dict):
                continue
            edu_items.append(
                {
                    "institution": entry.get("institution"),
                    "degree": entry.get("degree"),
                    "field_of_study": entry.get("field_of_study"),
                    "start_date": entry.get("start_date"),
                    "end_date": entry.get("end_date"),
                    "gpa": entry.get("gpa"),
                    "honors": entry.get("honors"),
                }
            )
        if edu_items:
            merged["education"] = edu_items

    if "certifications" not in merged or not merged.get("certifications"):
        certifications = llm_resume.get("certifications") or []
        cert_items = []
        for entry in _coerce_list(certifications):
            if not isinstance(entry, dict):
                continue
            cert_name = (entry.get("name") or entry.get("certification"))
            if not str(cert_name or "").strip():
                continue
            cert_items.append(
                {
                    "name": cert_name,
                    "issuing_organization": entry.get("issuing_organization"),
                    "issue_date": entry.get("issue_date"),
                    "expiry_date": entry.get("expiry_date"),
                    "credential_id": entry.get("credential_id"),
                }
            )
        if cert_items:
            merged["certifications"] = cert_items

    return merged


def _parse_date_str(value: str | None) -> date | None:
    if not value:
        return None
    parsed = dateparser.parse(value, settings={"PREFER_DAY_OF_MONTH": "first"})
    return parsed.date() if parsed else None


def _looks_like_present(value: str | None) -> bool:
    if not value:
        return False
    lowered = str(value).strip().lower()
    return lowered in {"present", "current", "now", "till date", "till  date"}


def _month_index(value: date) -> int:
    return (value.year * 12) + value.month


def _merge_month_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []

    ranges_sorted = sorted(ranges, key=lambda r: (r[0], r[1]))
    merged: list[tuple[int, int]] = [ranges_sorted[0]]
    for start_idx, end_idx in ranges_sorted[1:]:
        prev_start, prev_end = merged[-1]
        if start_idx <= prev_end + 1:
            merged[-1] = (prev_start, max(prev_end, end_idx))
        else:
            merged.append((start_idx, end_idx))
    return merged


def _is_short_internship(entry: dict[str, Any], duration_months: int) -> bool:
    if duration_months >= 3:
        return False

    employment_type = str(entry.get("employment_type") or "").strip().lower()
    if employment_type in {"intern", "internship"}:
        return True

    title = str(
        entry.get("title")
        or entry.get("designation")
        or entry.get("job_title")
        or ""
    ).strip().lower()
    return "intern" in title or "internship" in title


def _calculate_total_experience_payload(work_items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not work_items:
        return None

    today = date.today()
    considered = 0
    used = 0
    ranges: list[tuple[int, int]] = []
    job_confidences: list[float] = []

    for raw in work_items:
        if not isinstance(raw, dict):
            continue
        considered += 1

        start_raw = raw.get("start_date") or raw.get("from") or raw.get("start")
        end_raw = raw.get("end_date") or raw.get("to") or raw.get("end")
        is_current = bool(raw.get("is_current"))

        start = _parse_date_str(str(start_raw)) if start_raw else None
        if not start:
            continue

        end: date | None
        if is_current or _looks_like_present(str(end_raw) if end_raw else None):
            end = today
        elif end_raw:
            end = _parse_date_str(str(end_raw))
        else:
            end = today
            is_current = True

        if not end or end < start:
            continue

        start_idx = _month_index(start)
        end_idx = _month_index(end)
        duration_months = (end_idx - start_idx) + 1
        if _is_short_internship(raw, duration_months):
            continue

        used += 1
        ranges.append((start_idx, end_idx))

        try:
            job_confidences.append(float(raw.get("confidence", 0.75)))
        except (TypeError, ValueError):
            job_confidences.append(0.75)

    if not ranges:
        return None

    merged = _merge_month_ranges(ranges)
    total_months = sum((end_idx - start_idx) + 1 for start_idx, end_idx in merged)
    total_years = round(total_months / 12.0, 1)

    coverage = (used / considered) if considered else 0.0
    avg_job_conf = (sum(job_confidences) / len(job_confidences)) if job_confidences else 0.0
    confidence = 0.4 + (0.4 * avg_job_conf) + (0.2 * coverage)
    confidence = max(0.0, min(1.0, round(confidence, 2)))

    return {"total_years": total_years, "confidence": confidence}


def _parse_gpa(value: str | None) -> float | None:
    if not value:
        return None
    if "/" in value:
        num = value.split("/")[0]
        try:
            return float(num)
        except ValueError:
            return None
    if value.endswith("%"):
        try:
            return float(value.strip("%"))
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


def _to_proficiency(value: str | None) -> ProficiencyLevel | None:
    if not value:
        return None
    normalized = value.lower()
    for level in ProficiencyLevel:
        if level.value == normalized:
            return level
    return None


def _handle_task_error(job_id: str, exc: Exception, stage: str) -> None:
    logger.exception("Stage failed", extra={"job_id": job_id, "stage": stage})
    observe_parsing_failure()
    _update_job(
        job_id,
        status=ParsingJobStatus.FAILED,
        last_stage=stage,
        error_message=str(exc),
        completed=True,
    )


def _log_retry_exhausted(task, job_id: str, stage: str) -> None:  # noqa: ANN001
    try:
        if task.request.retries >= task.max_retries:
            logger.error(
                "Max retries exceeded",
                extra={"job_id": job_id, "stage": stage},
            )
    except Exception:  # noqa: BLE001
        return


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_extract_text",
)
def task_extract_text(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        try:
            import sentry_sdk

            sentry_sdk.set_tag("job_id", job_id)
        except Exception:
            pass
        job = _load_job(job_id)
        if job.raw_text:
            return job_id
        _update_job(job_id, last_stage="extract_text")
        extract_text_task(job_id)
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_text")
        _log_retry_exhausted(self, job_id, "extract_text")
        raise
    finally:
        observe_stage_duration("extract_text", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_clean_text",
)
def task_clean_text(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        if not job.raw_text:
            return job_id
        parsed = job.parsed_data or {}
        if parsed.get("text_cleaned"):
            return job_id
        cleaned = normalize_resume_text(job.raw_text)
        _update_job(
            job_id,
            last_stage="clean_text",
            raw_text=cleaned,
            parsed_data=_merge_parsed(job, {"text_cleaned": True}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "clean_text")
        _log_retry_exhausted(self, job_id, "clean_text")
        raise
    finally:
        observe_stage_duration("clean_text", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_finalize_text_only",
)
def task_finalize_text_only(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    session = SessionLocal()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == job_id)
        ).scalar_one_or_none()
        if not job:
            return job_id

        parsed = job.parsed_data or {}
        parsed["parsing_mode"] = "text_only"
        parsed["text_only_complete"] = True
        job.parsed_data = parsed

        if not job.extracted_text_path and job.raw_text:
            settings = get_settings()
            tenant_id = settings.DEFAULT_TENANT_ID
            try:
                candidate = session.execute(
                    select(Candidate).where(Candidate.id == job.candidate_id)
                ).scalar_one_or_none()
                if candidate and candidate.tenant_id:
                    tenant_id = candidate.tenant_id
            except Exception:
                pass
            base_key = f"resumes/{tenant_id}/{job.candidate_id}/{job.id}"
            text_key = f"{base_key}/resume.txt"
            text_bytes = job.raw_text.encode("utf-8", errors="replace")
            if settings.S3_BUCKET:
                try:
                    stored = upload_bytes_to_s3(text_bytes, text_key)
                    job.extracted_text_path = stored.uri
                except RuntimeError:
                    job.extracted_text_path = save_bytes_to_local(text_bytes, text_key)
            else:
                job.extracted_text_path = save_bytes_to_local(text_bytes, text_key)

        job.status = ParsingJobStatus.SUCCESS
        job.last_stage = "finalize_text_only"
        job.completed_at = datetime.now(timezone.utc)
        session.commit()
        observe_parsing_success(job.confidence_score, job.started_at)
        return job_id
    except Exception as exc:
        session.rollback()
        _handle_task_error(job_id, exc, "finalize_text_only")
        _log_retry_exhausted(self, job_id, "finalize_text_only")
        raise
    finally:
        observe_stage_duration("finalize_text_only", time.perf_counter() - start_time)
        session.close()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_llm_resume_parse",
)
def task_llm_resume_parse(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        try:
            import sentry_sdk

            sentry_sdk.set_tag("job_id", job_id)
        except Exception:
            pass
        job = _load_job(job_id)
        if not job.raw_text:
            return job_id
        parsed = job.parsed_data or {}
        if parsed.get("llm_resume"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id
        llm = LLMParsingService()
        payload = llm.extract_resume_intelligence(job.raw_text)
        _update_job(
            job_id,
            last_stage="llm_resume_parse",
            parsed_data=_merge_parsed(job, {"llm_resume": payload}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "llm_resume_parse")
        _log_retry_exhausted(self, job_id, "llm_resume_parse")
        raise
    finally:
        observe_stage_duration("llm_resume_parse", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_classify_resume_type",
)
def task_classify_resume_type(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        if not job.raw_text:
            return job_id
        parsed = job.parsed_data or {}
        if parsed.get("resume_type"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id
        llm = LLMParsingService()
        payload = llm.classify_resume_type(job.raw_text)
        if isinstance(payload, dict):
            _update_job(
                job_id,
                last_stage="classify_resume_type",
                parsed_data=_merge_parsed(job, {"resume_type": payload.get("resume_type")}),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "classify_resume_type")
        _log_retry_exhausted(self, job_id, "classify_resume_type")
        raise
    finally:
        observe_stage_duration("classify_resume_type", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_detect_resume_sections",
)
def task_detect_resume_sections(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        if not job.raw_text:
            return job_id
        parsed = job.parsed_data or {}
        if parsed.get("sections_detected"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id
        llm = LLMParsingService()
        payload = llm.detect_resume_sections(job.raw_text)
        if isinstance(payload, dict):
            _update_job(
                job_id,
                last_stage="detect_resume_sections",
                parsed_data=_merge_parsed(
                    job, {"sections_detected": payload.get("sections_detected", [])}
                ),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "detect_resume_sections")
        _log_retry_exhausted(self, job_id, "detect_resume_sections")
        raise
    finally:
        observe_stage_duration("detect_resume_sections", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_extract_personal_info",
)
def task_extract_personal_info(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        if not job.raw_text:
            return job_id
        parsed = job.parsed_data or {}
        if parsed.get("personal_info"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id
        llm = LLMParsingService()
        payload = llm.extract_personal_information(job.raw_text)
        if isinstance(payload, dict):
            _update_job(
                job_id,
                last_stage="extract_personal_info",
                parsed_data=_merge_parsed(job, {"personal_info": payload.get("personal_info")}),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_personal_info")
        _log_retry_exhausted(self, job_id, "extract_personal_info")
        raise
    finally:
        observe_stage_duration("extract_personal_info", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_extract_structured_resume",
)
def task_extract_structured_resume(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        if not job.raw_text:
            return job_id
        parsed = job.parsed_data or {}
        if parsed.get("llm_structured") or parsed.get("structured_resume"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id
        llm = LLMParsingService()
        payload = llm.extract_structured_resume(job.raw_text)
        if isinstance(payload, dict):
            _update_job(
                job_id,
                last_stage="extract_structured_resume",
                parsed_data=_merge_parsed(
                    job,
                    {
                        "llm_structured": payload,
                        "structured_resume": payload,
                    },
                ),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_structured_resume")
        _log_retry_exhausted(self, job_id, "extract_structured_resume")
        raise
    finally:
        observe_stage_duration("extract_structured_resume", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_normalize_structured_resume",
)
def task_normalize_structured_resume(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if parsed.get("llm_structured_normalized") or parsed.get("structured_resume_normalized"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id
        structured = parsed.get("llm_structured") or parsed.get("structured_resume")
        if not isinstance(structured, dict) or not structured:
            return job_id

        llm = LLMParsingService()
        normalized = llm.normalize_structured_resume(structured)
        if isinstance(normalized, dict):
            _update_job(
                job_id,
                last_stage="normalize_structured_resume",
                parsed_data=_merge_parsed(
                    job,
                    {
                        "llm_structured_normalized": normalized,
                        "structured_resume_normalized": normalized,
                        "llm_structured": normalized,
                        "structured_resume": normalized,
                    },
                ),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "normalize_structured_resume")
        _log_retry_exhausted(self, job_id, "normalize_structured_resume")
        raise
    finally:
        observe_stage_duration(
            "normalize_structured_resume", time.perf_counter() - start_time
        )


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_extract_experience_skills",
)
def task_extract_experience_skills(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        existing = parsed.get("experience_skills")
        if isinstance(existing, list) and existing:
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id

        sections = parsed.get("sections", {})
        experience_text = sections.get("experience", {}).get("content", "") if isinstance(sections, dict) else ""
        if not experience_text:
            work_items = parsed.get("work_experience", [])
            lines: list[str] = []
            for item in work_items:
                if not isinstance(item, dict):
                    continue
                for value in (item.get("title"), item.get("company"), item.get("description")):
                    if value:
                        lines.append(str(value))
            experience_text = "\n".join(lines).strip()
        if not experience_text:
            experience_text = (job.raw_text or "").strip()
        if not experience_text:
            return job_id

        llm = LLMParsingService()
        payload = llm.extract_experience_skills(experience_text)
        if isinstance(payload, dict):
            _update_job(
                job_id,
                last_stage="extract_experience_skills",
                parsed_data=_merge_parsed(job, {"experience_skills": payload.get("skills", [])}),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_experience_skills")
        _log_retry_exhausted(self, job_id, "extract_experience_skills")
        raise
    finally:
        observe_stage_duration("extract_experience_skills", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_normalize_education_details",
)
def task_normalize_education_details(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        existing_normalized = parsed.get("education_normalized")
        if isinstance(existing_normalized, list) and existing_normalized:
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id

        sections = parsed.get("sections", {})
        education_text = (
            sections.get("education", {}).get("content", "") if isinstance(sections, dict) else ""
        )
        if not education_text:
            education_items = parsed.get("education", [])
            if isinstance(education_items, list) and education_items:
                education_text = "\n".join(
                    [
                        " ".join(
                            [
                                str(item.get("degree") or ""),
                                str(item.get("field_of_study") or ""),
                                str(item.get("institution") or ""),
                                str(item.get("end_date") or item.get("graduation_year") or ""),
                                str(item.get("gpa") or ""),
                            ]
                        ).strip()
                        for item in education_items
                        if isinstance(item, dict)
                    ]
                ).strip()
        if not education_text:
            return job_id

        llm = LLMParsingService()
        normalized_entries = llm.normalize_education_entries(education_text)
        if isinstance(normalized_entries, list) and normalized_entries:
            _update_job(
                job_id,
                last_stage="normalize_education_details",
                parsed_data=_merge_parsed(
                    job,
                    {
                        "education_normalized": normalized_entries,
                        "education": normalized_entries,
                    },
                ),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "normalize_education_details")
        _log_retry_exhausted(self, job_id, "normalize_education_details")
        raise
    finally:
        observe_stage_duration(
            "normalize_education_details", time.perf_counter() - start_time
        )


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_extract_work_experience_details",
)
def task_extract_work_experience_details(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if parsed.get("work_experience_llm"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id

        sections = parsed.get("sections", {})
        experience_text = (
            sections.get("experience", {}).get("content", "") if isinstance(sections, dict) else ""
        )
        if not experience_text:
            return job_id

        llm = LLMParsingService()
        payload = llm.extract_work_experience_details(experience_text)
        if payload:
            _update_job(
                job_id,
                last_stage="extract_work_experience_details",
                parsed_data=_merge_parsed(job, {"work_experience_llm": payload}),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_work_experience_details")
        _log_retry_exhausted(self, job_id, "extract_work_experience_details")
        raise
    finally:
        observe_stage_duration(
            "extract_work_experience_details", time.perf_counter() - start_time
        )


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_calculate_total_experience",
)
def task_calculate_total_experience(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if parsed.get("total_experience"):
            return job_id
        settings = get_settings()

        work_items = (
            parsed.get("work_experience_llm")
            or parsed.get("work_experience")
            or []
        )
        if not work_items:
            return job_id

        deterministic_payload = _calculate_total_experience_payload(
            [item for item in work_items if isinstance(item, dict)]
        )
        if deterministic_payload:
            _update_job(
                job_id,
                last_stage="calculate_total_experience",
                parsed_data=_merge_parsed(job, {"total_experience": deterministic_payload}),
            )
            # Deterministic result is always preferred; use LLM only if you want to overwrite.
            if settings.LLM_PROVIDER == "none":
                return job_id

        if settings.LLM_PROVIDER == "none":
            return job_id

        llm = LLMParsingService()
        payload = llm.calculate_total_experience(json.dumps(work_items))
        if isinstance(payload, dict):
            years_raw = payload.get("total_years") or payload.get("total_experience_years")
            months_raw = payload.get("total_experience_months")
            total_years: float | None = None
            try:
                if years_raw is not None and str(years_raw).strip() != "":
                    total_years = float(str(years_raw).strip())
            except ValueError:
                total_years = None

            if total_years is None:
                try:
                    y = float(str(years_raw or 0).strip() or 0)
                    m = float(str(months_raw or 0).strip() or 0)
                    total_years = round(y + (m / 12.0), 1)
                except ValueError:
                    total_years = None

            normalized_payload = {
                "total_years": float(total_years) if total_years is not None else 0.0,
                "confidence": float(payload.get("confidence", 0.75)),
            }
            _update_job(
                job_id,
                last_stage="calculate_total_experience",
                parsed_data=_merge_parsed(job, {"total_experience": normalized_payload}),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "calculate_total_experience")
        _log_retry_exhausted(self, job_id, "calculate_total_experience")
        raise
    finally:
        observe_stage_duration(
            "calculate_total_experience", time.perf_counter() - start_time
        )


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_evaluate_extraction_confidence",
)
def task_evaluate_extraction_confidence(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if parsed.get("extraction_confidence"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id

        payload = {
            "personal_info": parsed.get("personal_info"),
            "skills": parsed.get("skills"),
            "experience": parsed.get("work_experience_llm") or parsed.get("work_experience"),
            "education": parsed.get("education"),
            "certifications": parsed.get("certifications"),
        }

        llm = LLMParsingService()
        result = llm.evaluate_extraction_confidence(payload)
        if isinstance(result, dict):
            _update_job(
                job_id,
                last_stage="evaluate_extraction_confidence",
                parsed_data=_merge_parsed(job, {"extraction_confidence": result}),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "evaluate_extraction_confidence")
        _log_retry_exhausted(self, job_id, "evaluate_extraction_confidence")
        raise
    finally:
        observe_stage_duration(
            "evaluate_extraction_confidence", time.perf_counter() - start_time
        )


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_normalize_skills_llm",
)
def task_normalize_skills_llm(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if parsed.get("skills_normalized"):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id

        skills = parsed.get("experience_skills") or parsed.get("skills") or []
        if not isinstance(skills, list) or not skills:
            return job_id

        llm = LLMParsingService()
        result = llm.normalize_deduplicate_skills(skills)
        if isinstance(result, dict):
            _update_job(
                job_id,
                last_stage="normalize_skills_llm",
                parsed_data=_merge_parsed(job, {"skills_normalized": result.get("normalized_skills", [])}),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "normalize_skills_llm")
        _log_retry_exhausted(self, job_id, "normalize_skills_llm")
        raise
    finally:
        observe_stage_duration("normalize_skills_llm", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_verify_extracted_data",
)
def task_verify_extracted_data(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        structured_present = bool(
            parsed.get("llm_structured")
            or parsed.get("llm_structured_normalized")
            or parsed.get("structured_resume")
            or parsed.get("structured_resume_normalized")
        )
        structured_verified_present = bool(
            parsed.get("llm_structured_verified") or parsed.get("structured_resume_verified")
        )
        if parsed.get("verified_data") and (not structured_present or structured_verified_present):
            return job_id
        settings = get_settings()
        if settings.LLM_PROVIDER == "none":
            return job_id
        if not job.raw_text:
            return job_id

        llm = LLMParsingService()

        extracted_payload = {
            "personal_info": parsed.get("personal_info"),
            "skills": parsed.get("skills_normalized") or parsed.get("skills"),
            "experience": parsed.get("work_experience_llm") or parsed.get("work_experience"),
            "education": parsed.get("education_normalized") or parsed.get("education"),
            "certifications": parsed.get("certifications"),
            "projects": parsed.get("projects"),
            "resume_type": parsed.get("resume_type"),
        }

        result = llm.verify_extracted_data(job.raw_text, extracted_payload)

        structured = (
            parsed.get("llm_structured_normalized")
            or parsed.get("llm_structured")
            or parsed.get("structured_resume_normalized")
            or parsed.get("structured_resume")
            or {}
        )
        structured_verified = None
        if isinstance(structured, dict) and structured:
            structured_verified = llm.verify_structured_resume(job.raw_text, structured)

        deterministic_contact = parsed.get("contact") if isinstance(parsed.get("contact"), dict) else {}
        if isinstance(structured_verified, dict) and deterministic_contact:
            verified_contact = (
                structured_verified.get("contact")
                if isinstance(structured_verified.get("contact"), dict)
                else {}
            )
            verified_emails = (
                verified_contact.get("emails")
                if isinstance(verified_contact.get("emails"), list)
                else []
            )
            verified_phones = (
                verified_contact.get("phones")
                if isinstance(verified_contact.get("phones"), list)
                else []
            )
            has_email = any(
                isinstance(item, dict) and str(item.get("email", "")).strip()
                for item in verified_emails
            )
            has_phone = any(
                isinstance(item, dict) and str(item.get("phone", "")).strip()
                for item in verified_phones
            )

            det_emails = (
                deterministic_contact.get("emails")
                if isinstance(deterministic_contact.get("emails"), list)
                else []
            )
            det_phones = (
                deterministic_contact.get("phones")
                if isinstance(deterministic_contact.get("phones"), list)
                else []
            )
            if not has_email and any(
                isinstance(item, dict) and str(item.get("email", "")).strip() for item in det_emails
            ):
                verified_contact["emails"] = det_emails
            if not has_phone and any(
                isinstance(item, dict) and str(item.get("phone", "")).strip() for item in det_phones
            ):
                verified_contact["phones"] = det_phones

            det_name = (
                deterministic_contact.get("name")
                if isinstance(deterministic_contact.get("name"), dict)
                else {}
            )
            if isinstance(det_name, dict) and str(det_name.get("name") or "").strip():
                verified_name = (
                    verified_contact.get("name")
                    if isinstance(verified_contact.get("name"), dict)
                    else {}
                )
                if not str(verified_name.get("name") or "").strip():
                    verified_contact["name"] = det_name

            det_location = (
                deterministic_contact.get("location")
                if isinstance(deterministic_contact.get("location"), dict)
                else {}
            )
            if isinstance(det_location, dict) and any(
                str(det_location.get(field) or "").strip()
                for field in ("city", "state", "country")
            ):
                verified_location = (
                    verified_contact.get("location")
                    if isinstance(verified_contact.get("location"), dict)
                    else {}
                )
                if not any(
                    str(verified_location.get(field) or "").strip()
                    for field in ("city", "state", "country")
                ):
                    verified_contact["location"] = det_location

            det_urls = (
                deterministic_contact.get("urls")
                if isinstance(deterministic_contact.get("urls"), dict)
                else {}
            )
            if isinstance(det_urls, dict) and any(
                str(det_urls.get(field) or "").strip()
                for field in ("linkedin", "github")
            ):
                verified_urls = (
                    verified_contact.get("urls")
                    if isinstance(verified_contact.get("urls"), dict)
                    else {}
                )
                if not str(verified_urls.get("linkedin") or "").strip() and str(
                    det_urls.get("linkedin") or ""
                ).strip():
                    verified_urls["linkedin"] = det_urls.get("linkedin")
                if not str(verified_urls.get("github") or "").strip() and str(
                    det_urls.get("github") or ""
                ).strip():
                    verified_urls["github"] = det_urls.get("github")
                verified_urls.setdefault("websites", det_urls.get("websites") or [])
                verified_contact["urls"] = verified_urls

            structured_verified["contact"] = verified_contact

        updates: dict[str, Any] = {"verified_data": result} if isinstance(result, dict) else {}
        if isinstance(structured_verified, dict):
            updates["llm_structured_verified"] = structured_verified
            updates["structured_resume_verified"] = structured_verified
            updates["llm_structured"] = structured_verified
            updates["structured_resume"] = structured_verified

            for key in ("contact", "work_experience", "education", "skills", "certifications"):
                if key in structured_verified:
                    incoming = structured_verified.get(key)
                    existing = parsed.get(key)
                    if key == "contact" and isinstance(incoming, dict):
                        updates[key] = incoming
                        continue
                    if isinstance(incoming, list):
                        if incoming:
                            updates[key] = incoming
                        elif not existing:
                            updates[key] = incoming
                        continue
                    if isinstance(incoming, dict):
                        if incoming or not existing:
                            updates[key] = incoming
                        continue
                    if incoming is not None:
                        updates[key] = incoming
        if updates:
            _update_job(
                job_id,
                last_stage="verify_extracted_data",
                parsed_data=_merge_parsed(job, updates),
            )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "verify_extracted_data")
        _log_retry_exhausted(self, job_id, "verify_extracted_data")
        raise
    finally:
        observe_stage_duration("verify_extracted_data", time.perf_counter() - start_time)


def _normalize_certification_name(name: str | None) -> str | None:
    if not name:
        return None
    key = " ".join(name.lower().split())
    return CERTIFICATION_ALIASES.get(key, name)


def _normalize_degree_name(name: str | None) -> str | None:
    if not name:
        return None
    key = " ".join(name.lower().replace(".", "").split())
    return DEGREE_ALIASES.get(key, name)

def _compute_certification_taxonomy_score(name: str | None) -> float:
    """
    Score certification strength based on taxonomy aliases.
    Boost confidence if it matches known enterprise certifications.
    """
    if not name:
        return 0.0

    key = " ".join(name.lower().split())

    # Strong match in certification alias taxonomy
    if key in CERTIFICATION_ALIASES:
        return 1.0

    # Partial match
    for alias in CERTIFICATION_ALIASES.keys():
        if alias in key:
            return 0.8

    # Weak keyword fallback
    if re.search(
        r"\b(certified|certification|professional|associate|expert|architect|specialist)\b",
        key,
    ):
        return 0.6

    return 0.3


def _normalize_skills(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extractor = SkillExtractor()
    matches: list[SkillMatch] = []
    for entry in payload:
        name = entry.get("name") or entry.get("skill_name")
        normalized = entry.get("normalized_name") or (
            " ".join(str(name).lower().strip().split()) if name else ""
        )
        if not normalized:
            continue
        matches.append(
            SkillMatch(
                name=name or normalized,
                normalized_name=normalized,
                category=entry.get("category"),
                confidence=entry.get("confidence", 0.5),
                years_experience=entry.get("years_experience"),
                proficiency=entry.get("proficiency"),
            )
        )

    mapped = extractor.categorize_skills(extractor.normalize_skills(matches))
    return [
        {
            "name": match.name,
            "normalized_name": match.normalized_name,
            "category": match.category,
            "confidence": match.confidence,
            "years_experience": match.years_experience,
            "proficiency": match.proficiency,
        }
        for match in mapped
    ]


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.pipeline.task_taxonomy_mapping",
)
def task_taxonomy_mapping(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if parsed.get("taxonomy_mapped"):
            return job_id

        updates: dict[str, Any] = {"taxonomy_mapped": True}

        skills = parsed.get("skills")
        if isinstance(skills, list) and skills:
            updates["skills"] = _normalize_skills(skills)

        certifications = parsed.get("certifications")
        if isinstance(certifications, list) and certifications:
            normalized_certs = []
            for cert in certifications:
                if isinstance(cert, dict):
                    name = _normalize_certification_name(cert.get("name"))
                    normalized_certs.append({**cert, "name": name})
                else:
                    normalized_certs.append(_normalize_certification_name(str(cert)))
            updates["certifications"] = normalized_certs

        education = parsed.get("education")
        if isinstance(education, list) and education:
            normalized_edu = []
            for entry in education:
                if not isinstance(entry, dict):
                    normalized_edu.append(entry)
                    continue
                degree = _normalize_degree_name(entry.get("degree"))
                normalized_edu.append({**entry, "degree": degree})
            updates["education"] = normalized_edu

        _update_job(
            job_id,
            last_stage="taxonomy_mapping",
            parsed_data=_merge_parsed(job, updates),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "taxonomy_mapping")
        _log_retry_exhausted(self, job_id, "taxonomy_mapping")
        raise
    finally:
        observe_stage_duration("taxonomy_mapping", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_detect_sections",
)
def task_detect_sections(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if "sections" in parsed:
            return job_id

        parser = SectionParser(use_spacy=True)
        sections = parser.parse(job.raw_text or "")
        payload = {
            key: {"content": value.content, "confidence": value.confidence}
            for key, value in sections.items()
        }
        _update_job(
            job_id,
            last_stage="detect_sections",
            parsed_data=_merge_parsed(job, {"sections": payload}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "detect_sections")
        _log_retry_exhausted(self, job_id, "detect_sections")
        raise
    finally:
        observe_stage_duration("detect_sections", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_extract_contact_info",
)
def task_extract_contact_info(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if "contact" in parsed:
            return job_id

        extractor = ContactExtractor()
        contact = extractor.extract_all(job.raw_text or "")
        payload = {
            "emails": [item.__dict__ for item in contact.emails],
            "phones": [item.__dict__ for item in contact.phones],
            "urls": contact.urls.__dict__,
            "location": contact.location.__dict__,
            "name": contact.name.__dict__,
        }
        _update_job(
            job_id,
            last_stage="extract_contact_info",
            parsed_data=_merge_parsed(job, {"contact": payload}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_contact_info")
        _log_retry_exhausted(self, job_id, "extract_contact_info")
        raise
    finally:
        observe_stage_duration("extract_contact_info", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_parse_work_experience",
)
def task_parse_work_experience(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        existing = parsed.get("work_experience")
        if isinstance(existing, list) and existing:
            return job_id

        sections = parsed.get("sections", {})
        experience_text = sections.get("experience", {}).get("content", job.raw_text or "")
        parser = WorkExperienceParser()
        jobs = parser.parse_experience_section(experience_text)
        payload = [
            {
                **job_entry.__dict__,
                "start_date": job_entry.start_date.isoformat()
                if job_entry.start_date
                else None,
                "end_date": job_entry.end_date.isoformat() if job_entry.end_date else None,
            }
            for job_entry in jobs
        ]
        _update_job(
            job_id,
            last_stage="parse_work_experience",
            parsed_data=_merge_parsed(job, {"work_experience": payload}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "parse_work_experience")
        _log_retry_exhausted(self, job_id, "parse_work_experience")
        raise
    finally:
        observe_stage_duration("parse_work_experience", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_parse_education",
)
def task_parse_education(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        existing_education = parsed.get("education")
        if isinstance(existing_education, list) and existing_education:
            return job_id

        sections = parsed.get("sections", {})
        education_text = sections.get("education", {}).get("content", job.raw_text or "")
        parser = EducationParser()
        entries = parser.parse(education_text)
        payload = [
            {
                **entry.__dict__,
                "start_date": entry.start_date.isoformat()
                if entry.start_date
                else None,
                "end_date": entry.end_date.isoformat() if entry.end_date else None,
            }
            for entry in entries
        ]
        _update_job(
            job_id,
            last_stage="parse_education",
            parsed_data=_merge_parsed(job, {"education": payload}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "parse_education")
        _log_retry_exhausted(self, job_id, "parse_education")
        raise
    finally:
        observe_stage_duration("parse_education", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_extract_skills",
)
def task_extract_skills(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        existing_skills = parsed.get("skills")
        if isinstance(existing_skills, list) and existing_skills:
            return job_id

        sections = parsed.get("sections", {})
        skills_block = sections.get("skills") if isinstance(sections, dict) else None
        skills_section = (
            skills_block.get("content", "")
            if isinstance(skills_block, dict)
            else ""
        )
        skills_section_conf: float | None = None
        if isinstance(skills_block, dict):
            try:
                skills_section_conf = float(skills_block.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                skills_section_conf = None

        jobs_payload = parsed.get("work_experience", [])
        jobs = [
            JobEntry(
                company=item.get("company"),
                title=item.get("title"),
                start_date=None,
                end_date=None,
                is_current=item.get("is_current", False),
                location=item.get("location"),
                description=item.get("description", ""),
                bullets=item.get("bullets", []),
                duration_months=item.get("duration_months"),
                client=item.get("client"),
                employment_type=item.get("employment_type"),
                confidence=item.get("confidence", 0.0),
            )
            for item in jobs_payload
        ]

        extractor = SkillExtractor()
        fallback_guard = bool(
            skills_section_conf is not None and skills_section_conf < 0.6
        )
        matches = extractor.extract_all(
            skills_section,
            jobs,
            skills_section_confidence=skills_section_conf,
            raw_text=job.raw_text or None,
        )
        payload = [match.__dict__ for match in matches]

        if not payload:
            settings = get_settings()
            if settings.LLM_PROVIDER != "none" and settings.PARSING_MODE.lower() != "deterministic":
                llm = LLMParsingService()
                grouped = llm.extract_all_skills_grouped(job.raw_text or "")
                grouped_skills = grouped.get("skills") if isinstance(grouped, dict) else None
                if isinstance(grouped_skills, dict):
                    flattened: dict[str, dict[str, Any]] = {}
                    for category, values in grouped_skills.items():
                        if not isinstance(values, list):
                            continue
                        for value in values:
                            if not isinstance(value, str):
                                continue
                            name = value.strip()
                            if not name:
                                continue
                            lowered = name.lower()
                            if re.search(r"\b(developed|built|designed)\b", lowered):
                                continue
                            normalized = _normalize_skill_name(name)
                            flattened[normalized] = {
                                "name": name,
                                "normalized_name": normalized,
                                "category": str(category),
                                "confidence": 0.7,
                                "years_experience": None,
                                "proficiency": None,
                            }
                    if flattened:
                        payload = list(flattened.values())

        alias_map = {
            "reactjs": "react",
            "react.js": "react",
            "react js": "react",
        }

        def _canonical_skill(normalized: str, name: str) -> str:
            raw = normalized or name or ""
            lowered = raw.lower().strip()
            if lowered in alias_map:
                return alias_map[lowered]
            alias_key = lowered.replace(".", "").replace(" ", "").replace("-", "")
            if alias_key in alias_map:
                return alias_map[alias_key]
            return lowered

        cleaned_payload: list[dict[str, Any]] = []
        for item in payload if isinstance(payload, list) else []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            if re.search(r"\b(developed|built|designed)\b", name.lower()):
                continue
            normalized = str(item.get("normalized_name") or "").strip()
            canonical = _canonical_skill(normalized, name)
            cleaned_payload.append({**item, "normalized_name": canonical})

        merged: dict[str, dict[str, Any]] = {}
        for item in cleaned_payload:
            key = str(item.get("normalized_name") or "").strip().lower()
            if not key:
                continue
            existing = merged.get(key)
            if not existing:
                merged[key] = item
                continue
            try:
                existing_conf = float(existing.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                existing_conf = 0.0
            try:
                incoming_conf = float(item.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                incoming_conf = 0.0
            if incoming_conf > existing_conf:
                merged[key] = item

        payload = list(merged.values())
        fallback_used = fallback_guard or (not skills_section.strip() and bool(job.raw_text))
        avg_conf = 0.0
        if payload:
            vals: list[float] = []
            for item in payload:
                if not isinstance(item, dict):
                    continue
                try:
                    vals.append(float(item.get("confidence", 0.0) or 0.0))
                except (TypeError, ValueError):
                    continue
            avg_conf = (sum(vals) / len(vals)) if vals else 0.0
        section_bonus = 0.05 if (skills_section_conf is not None and skills_section_conf >= 0.6) else 0.0
        fallback_penalty = -0.05 if fallback_used else 0.0
        count_bonus = min(0.1, (len(payload) / 40.0) * 0.1) if payload else 0.0
        skills_extraction_confidence = max(
            0.0,
            min(
                1.0,
                round(float(avg_conf + section_bonus + fallback_penalty + count_bonus), 4),
            ),
        )
        _update_job(
            job_id,
            last_stage="extract_skills",
            parsed_data=_merge_parsed(
                job,
                {
                    "skills": payload,
                    "skills_extraction_confidence": skills_extraction_confidence,
                    "skills_fallback_used": fallback_used,
                },
            ),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_skills")
        _log_retry_exhausted(self, job_id, "extract_skills")
        raise
    finally:
        observe_stage_duration("extract_skills", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_extract_achievements",
)
def task_extract_achievements(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        existing = parsed.get("achievements")
        if isinstance(existing, list) and existing:
            return job_id

        sections = parsed.get("sections", {})
        section_text = ""
        section_confidence: float | None = None
        if isinstance(sections, dict):
            candidates: list[tuple[str, float]] = []
            for key in ("achievements", "awards"):
                block = sections.get(key)
                if not isinstance(block, dict):
                    continue
                text = str(block.get("content") or "").strip()
                if not text:
                    continue
                try:
                    conf = float(block.get("confidence", 0.0) or 0.0)
                except (TypeError, ValueError):
                    conf = 0.0
                candidates.append((text, conf))
            if candidates:
                candidates.sort(key=lambda item: (item[1], len(item[0])), reverse=True)
                section_text, section_confidence = candidates[0]

        extractor = AchievementsExtractor()
        items = extractor.extract(
            section_text=section_text or None,
            raw_text=job.raw_text or None,
            section_confidence=section_confidence,
        )
        payload = [item.__dict__ for item in items]
        _update_job(
            job_id,
            last_stage="extract_achievements",
            parsed_data=_merge_parsed(job, {"achievements": payload}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "extract_achievements")
        _log_retry_exhausted(self, job_id, "extract_achievements")
        raise
    finally:
        observe_stage_duration("extract_achievements", time.perf_counter() - start_time)



@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_parse_certifications",
)
def task_parse_certifications(self, job_id: str) -> str:
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}

        # Skip if already extracted
        existing_certs = parsed.get("certifications")
        if isinstance(existing_certs, list) and existing_certs:
            return job_id

        sections = parsed.get("sections", {})
        cert_text = ""
        cert_section_conf: float | None = None

        # ====================================================
        # 1️⃣ STRICT BOUNDARY EXTRACTION (PRIMARY SOURCE)
        # ====================================================
        boundary_result = extract_certifications(job.raw_text or "")

        if boundary_result.section_found and boundary_result.extracted_lines:
            cert_text = boundary_result.content
            cert_section_conf = boundary_result.confidence

        # ====================================================
        # 2️⃣ FALLBACK TO SECTION PARSER (SECONDARY)
        # ====================================================
        if not cert_text:
            cert_section = sections.get("certifications") if isinstance(sections, dict) else None

            if isinstance(cert_section, dict):
                try:
                    cert_section_conf = float(cert_section.get("confidence", 0.0) or 0.0)
                except (TypeError, ValueError):
                    cert_section_conf = None

                content = str(cert_section.get("content") or "").strip()

                # Safety: ignore if too long (likely full resume)
                if content and len(content) < 3000:
                    cert_text = content

        

        # ====================================================
        # 4️⃣ STILL NOTHING? → SAVE EMPTY SAFELY
        # ====================================================
        if not cert_text:
            _update_job(
                job_id,
                last_stage="parse_certifications",
                parsed_data=_merge_parsed(
                    job,
                    {
                        "certifications": [],
                        "certifications_validation": {
                            "reason": "No certification section detected safely"
                        },
                    },
                ),
            )
            return job_id

        # ====================================================
        # 5️⃣ PARSE USING YOUR HYBRID CERTIFICATION PARSER
        # ====================================================
        parser = CertificationParser()
        entries = parser.parse(cert_text)

        payload = [
            {
                **entry.__dict__,
                "issue_date": entry.issue_date.isoformat() if entry.issue_date else None,
                "expiry_date": entry.expiry_date.isoformat() if entry.expiry_date else None,
            }
            for entry in entries
        ]

        # Remove empty names
        payload = [
            item
            for item in payload
            if isinstance(item, dict)
            and str(item.get("name") or "").strip()
            and len(str(item.get("name"))) <= 200  # 🔒 DB Safety Guard
        ]

        # ====================================================
        # 6️⃣ LLM FALLBACK (ONLY IF SAFE + EMPTY)
        # ====================================================
        if not payload:
            settings = get_settings()
            if (
                settings.LLM_PROVIDER != "none"
                and settings.PARSING_MODE.lower() != "deterministic"
            ):
                llm = LLMParsingService()
                llm_payload = llm.extract_certifications(cert_text)

                if isinstance(llm_payload, list):
                    payload = [
                        item
                        for item in llm_payload
                        if isinstance(item, dict)
                        and str(item.get("name") or "").strip()
                        and len(str(item.get("name"))) <= 200
                    ]

        # ====================================================
        # 7️⃣ VALIDATION LAYER (SIR STRENGTH RETAINED)
        # ====================================================
        validator = CertificationValidator()
        validated = validator.normalize_providers(payload)
        validated = validator.remove_false_positives(validated)
        validated = validator.deduplicate_certifications(validated)

        validation_info = validator.detect_mismatches(
            section_confidence=cert_section_conf,
            extracted_items=validated,
        )



        for item in validated:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            if not name:
                continue

            lowered = " ".join(name.lower().split())
            taxonomy_score = _compute_certification_taxonomy_score(name)
            

            alias_matched = False
            for alias_key in CERTIFICATION_ALIASES.keys():
                if alias_key in lowered:
                   alias_matched = True
                   taxonomy_score = 1.0  # Full strength if alias matched
                   break

            # EXAM CODE BOOST
            exam_code_detected = False
            if _EXAM_CODE_PATTERN.search(name):
                exam_code_detected = True
                taxonomy_score = max(taxonomy_score, 0.95)    

            #base conifdence
            try:
                base_conf = float(item.get("confidence", 0.7))
            except (TypeError, ValueError):
                base_conf = 0.7
    
            #FINAL CONFIDENCE CALCULATION
            boosted_conf = min(
                1.0,
                round((base_conf * 0.6) + (taxonomy_score * 0.4), 3)
            )
            
            if alias_matched:
               boosted_conf = min(1.0, round(boosted_conf + 0.1, 3))

            item["taxonomy_score"] = taxonomy_score
            item["alias_matched"] = alias_matched
            item["confidence"] = boosted_conf

        # ====================================================
        # 8️⃣ SAVE
        # ====================================================
        _update_job(
            job_id,
            last_stage="parse_certifications",
            parsed_data=_merge_parsed(
                job,
                {
                    "certifications": validated,
                    "certifications_validation": validation_info,
                },
            ),
        )

        return job_id

    except Exception as exc:
        _handle_task_error(job_id, exc, "parse_certifications")
        _log_retry_exhausted(self, job_id, "parse_certifications")
        raise
    finally:
        observe_stage_duration("parse_certifications", time.perf_counter() - start_time)




@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_calculate_confidence",
)
def task_calculate_confidence(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        settings = get_settings()
        sections = parsed.get("sections") if isinstance(parsed.get("sections"), dict) else {}

        def _clamp(value: float) -> float:
            return max(0.0, min(1.0, float(value)))

        def _to_float(value: Any, default: float = 0.0) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return float(default)

        def _section_conf(section_key: str) -> float:
            block = sections.get(section_key) if isinstance(sections, dict) else None
            if not isinstance(block, dict):
                return 0.0
            return _clamp(_to_float(block.get("confidence", 0.0), 0.0))

        def _mean(values: list[float]) -> float:
            vals = [v for v in values if isinstance(v, (int, float))]
            return (sum(vals) / len(vals)) if vals else 0.0

        def _list_extraction_conf(items: Any) -> float:
            if not isinstance(items, list) or not items:
                return 0.0
            vals: list[float] = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                if "confidence" in item:
                    vals.append(_clamp(_to_float(item.get("confidence", 0.0), 0.0)))
            if vals:
                return _mean(vals)
            return 0.6

        def _contact_extraction_conf(contact: Any) -> float:
            if not isinstance(contact, dict) or not contact:
                return 0.0
            vals: list[float] = []
            name = contact.get("name")
            if isinstance(name, dict):
                vals.append(_clamp(_to_float(name.get("confidence", 0.0), 0.0)))
            location = contact.get("location")
            if isinstance(location, dict):
                vals.append(_clamp(_to_float(location.get("confidence", 0.0), 0.0)))
            emails = contact.get("emails") if isinstance(contact.get("emails"), list) else []
            if emails:
                email_conf = max(
                    (
                        _to_float(e.get("confidence", 0.0), 0.0)
                        for e in emails
                        if isinstance(e, dict)
                    ),
                    default=0.0,
                )
                vals.append(_clamp(email_conf))
            phones = contact.get("phones") if isinstance(contact.get("phones"), list) else []
            if phones:
                phone_conf = max(
                    (
                        _to_float(p.get("confidence", 0.0), 0.0)
                        for p in phones
                        if isinstance(p, dict)
                    ),
                    default=0.0,
                )
                vals.append(_clamp(phone_conf))
            return _mean(vals) if vals else 0.0

        def _contact_pattern_strength(contact: Any) -> float:
            if not isinstance(contact, dict) or not contact:
                return 0.0
            name_ok = bool(isinstance(contact.get("name"), dict) and str(contact.get("name", {}).get("name") or "").strip())
            emails_ok = bool(
                isinstance(contact.get("emails"), list)
                and any(isinstance(e, dict) and str(e.get("email") or "").strip() for e in contact.get("emails", []))
            )
            phones_ok = bool(
                isinstance(contact.get("phones"), list)
                and any(isinstance(p, dict) and str(p.get("phone") or "").strip() for p in contact.get("phones", []))
            )
            location_ok = bool(
                isinstance(contact.get("location"), dict)
                and any(str(contact.get("location", {}).get(k) or "").strip() for k in ("city", "state", "country"))
            )
            linkedin_ok = bool(
                isinstance(contact.get("urls"), dict)
                and str(contact.get("urls", {}).get("linkedin") or "").strip()
            )
            github_ok = bool(
                isinstance(contact.get("urls"), dict)
                and str(contact.get("urls", {}).get("github") or "").strip()
            )
            return sum(int(v) for v in (name_ok, emails_ok, phones_ok, location_ok, linkedin_ok, github_ok)) / 6.0

        def _work_pattern_strength(work_items: Any) -> float:
            if not isinstance(work_items, list) or not work_items:
                return 0.0
            scores: list[float] = []
            for item in work_items:
                if not isinstance(item, dict):
                    continue
                company_ok = bool(str(item.get("company") or "").strip())
                title_ok = bool(str(item.get("title") or "").strip())
                start_ok = bool(str(item.get("start_date") or "").strip())
                end_ok = bool(str(item.get("end_date") or "").strip()) or bool(item.get("is_current"))
                scores.append(sum(int(v) for v in (company_ok, title_ok, start_ok, end_ok)) / 4.0)
            return _mean(scores)

        def _education_pattern_strength(items: Any) -> float:
            if not isinstance(items, list) or not items:
                return 0.0
            scores: list[float] = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                inst_ok = bool(str(item.get("institution") or "").strip())
                degree_ok = bool(str(item.get("degree") or "").strip())
                end_ok = bool(str(item.get("end_date") or item.get("graduation_year") or "").strip())
                scores.append(sum(int(v) for v in (inst_ok, degree_ok, end_ok)) / 3.0)
            return _mean(scores)

        def _skills_pattern_strength(items: Any) -> float:
            if not isinstance(items, list) or not items:
                return 0.0
            count = len([it for it in items if isinstance(it, dict) and str(it.get("normalized_name") or it.get("name") or "").strip()])
            if count >= 12:
                return 1.0
            if count >= 6:
                return 0.85
            if count >= 3:
                return 0.7
            if count >= 1:
                return 0.55
            return 0.0

        def _simple_count_strength(items: Any, thresholds: tuple[int, int, int] = (1, 2, 4)) -> float:
            if not isinstance(items, list) or not items:
                return 0.0
            count = len([it for it in items if isinstance(it, dict) and any(str(v or "").strip() for v in it.values())])
            low, mid, high = thresholds
            if count >= high:
                return 1.0
            if count >= mid:
                return 0.8
            if count >= low:
                return 0.6
            return 0.0

        structured_verified = parsed.get("llm_structured_verified") if isinstance(parsed.get("llm_structured_verified"), dict) else None

        def _llm_validation_strength(field: str) -> float:
            if settings.LLM_PROVIDER == "none":
                return 0.0
            if not isinstance(structured_verified, dict):
                return 0.0
            if field == "contact":
                return 1.0 if isinstance(structured_verified.get("contact"), dict) and structured_verified.get("contact") else 0.0
            if field == "work_experience":
                return 1.0 if isinstance(structured_verified.get("work_experience"), list) and structured_verified.get("work_experience") else 0.0
            if field == "education":
                return 1.0 if isinstance(structured_verified.get("education"), list) and structured_verified.get("education") else 0.0
            if field == "skills":
                return 1.0 if isinstance(structured_verified.get("skills"), list) and structured_verified.get("skills") else 0.0
            if field == "certifications":
                return 0.0
            if field == "achievements":
                return 0.0
            return 0.0

        llm_weight = 0.1 if settings.LLM_PROVIDER != "none" else 0.0
        base_weights = {
            "section": 0.35,
            "extraction": 0.35,
            "pattern": 0.2,
            "llm": llm_weight,
        }
        total_w = base_weights["section"] + base_weights["extraction"] + base_weights["pattern"] + base_weights["llm"]
        weights = {k: (v / total_w) for k, v in base_weights.items() if total_w > 0}

        contact = parsed.get("contact")
        work_items = parsed.get("work_experience")
        education_items = parsed.get("education")
        skills_items = parsed.get("skills")
        cert_items = parsed.get("certifications")
        achievement_items = parsed.get("achievements")

        fields: dict[str, dict[str, float]] = {}

        def _field_score(*, section: float, extraction: float, pattern: float, llm: float) -> float:
            return _clamp(
                (weights.get("section", 0.0) * section)
                + (weights.get("extraction", 0.0) * extraction)
                + (weights.get("pattern", 0.0) * pattern)
                + (weights.get("llm", 0.0) * llm)
            )

        fields["contact"] = {
            "section": _section_conf("contact"),
            "extraction": _contact_extraction_conf(contact),
            "pattern": _contact_pattern_strength(contact),
            "llm": _llm_validation_strength("contact"),
        }
        fields["contact"]["score"] = _field_score(
            section=fields["contact"]["section"],
            extraction=fields["contact"]["extraction"],
            pattern=fields["contact"]["pattern"],
            llm=fields["contact"]["llm"],
        )

        fields["work_experience"] = {
            "section": _section_conf("experience"),
            "extraction": _list_extraction_conf(work_items),
            "pattern": _work_pattern_strength(work_items),
            "llm": _llm_validation_strength("work_experience"),
        }
        fields["work_experience"]["score"] = _field_score(
            section=fields["work_experience"]["section"],
            extraction=fields["work_experience"]["extraction"],
            pattern=fields["work_experience"]["pattern"],
            llm=fields["work_experience"]["llm"],
        )

        fields["skills"] = {
            "section": _section_conf("skills"),
            "extraction": _list_extraction_conf(skills_items),
            "pattern": _skills_pattern_strength(skills_items),
            "llm": _llm_validation_strength("skills"),
        }
        fields["skills"]["score"] = _field_score(
            section=fields["skills"]["section"],
            extraction=fields["skills"]["extraction"],
            pattern=fields["skills"]["pattern"],
            llm=fields["skills"]["llm"],
        )

        fields["education"] = {
            "section": _section_conf("education"),
            "extraction": _list_extraction_conf(education_items),
            "pattern": _education_pattern_strength(education_items),
            "llm": _llm_validation_strength("education"),
        }
        fields["education"]["score"] = _field_score(
            section=fields["education"]["section"],
            extraction=fields["education"]["extraction"],
            pattern=fields["education"]["pattern"],
            llm=fields["education"]["llm"],
        )

        fields["certifications"] = {
            "section": _section_conf("certifications"),
            "extraction": _list_extraction_conf(cert_items),
            "pattern": _simple_count_strength(cert_items, thresholds=(1, 2, 3)),
            "llm": _llm_validation_strength("certifications"),
        }
        fields["certifications"]["score"] = _field_score(
            section=fields["certifications"]["section"],
            extraction=fields["certifications"]["extraction"],
            pattern=fields["certifications"]["pattern"],
            llm=fields["certifications"]["llm"],
        )

        awards_conf = max(_section_conf("achievements"), _section_conf("awards"))
        fields["achievements"] = {
            "section": awards_conf,
            "extraction": _list_extraction_conf(achievement_items),
            "pattern": _simple_count_strength(achievement_items, thresholds=(1, 2, 4)),
            "llm": _llm_validation_strength("achievements"),
        }
        fields["achievements"]["score"] = _field_score(
            section=fields["achievements"]["section"],
            extraction=fields["achievements"]["extraction"],
            pattern=fields["achievements"]["pattern"],
            llm=fields["achievements"]["llm"],
        )

        field_importance = {
            "contact": 0.22,
            "work_experience": 0.28,
            "skills": 0.18,
            "education": 0.16,
            "certifications": 0.08,
            "achievements": 0.08,
        }
        total_importance = sum(field_importance.values()) or 1.0
        score = sum(
            (field_importance.get(name, 0.0) / total_importance) * float(values.get("score", 0.0))
            for name, values in fields.items()
        )
        score = _clamp(round(score, 4))

        breakdown: dict[str, Any] = {
            "weights": weights,
            "fields": fields,
            "overall": score,
        }

        _update_job(
            job_id,
            last_stage="calculate_confidence",
            confidence_score=score,
            parsed_data=_merge_parsed(job, {"confidence": score, "confidence_breakdown": breakdown}),
        )
        return job_id
    except Exception as exc:
        _handle_task_error(job_id, exc, "calculate_confidence")
        _log_retry_exhausted(self, job_id, "calculate_confidence")
        raise
    finally:
        observe_stage_duration("calculate_confidence", time.perf_counter() - start_time)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    name="app.workers.pipeline.task_save_to_database",
)
def task_save_to_database(self, job_id: str) -> str:  # noqa: ANN001
    session = SessionLocal()
    start_time = time.perf_counter()
    try:
        structlog.contextvars.bind_contextvars(job_id=job_id)
        try:
            import sentry_sdk

            sentry_sdk.set_tag("job_id", job_id)
        except Exception:
            pass
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == job_id)
        ).scalar_one_or_none()
        if not job:
            return job_id

        parsed_data = job.parsed_data or {}
        structured = (
            parsed_data.get("llm_structured_verified")
            or parsed_data.get("llm_structured_normalized")
            or parsed_data.get("llm_structured")
        )
        parsed = _apply_llm_resume(parsed_data)
        if isinstance(structured, dict):
            for key in ("contact", "work_experience", "education", "skills"):
                value = structured.get(key)
                if value is None:
                    continue
                existing = parsed.get(key)
                if key == "contact" and isinstance(value, dict):
                    if not isinstance(existing, dict) or not existing:
                        parsed[key] = value
                    else:
                        merged_contact = dict(existing)
                        for subkey, incoming in value.items():
                            if subkey not in merged_contact or merged_contact.get(subkey) in (None, "", [], {}):
                                merged_contact[subkey] = incoming
                        parsed[key] = merged_contact
                    continue
                if isinstance(value, list):
                    if value:
                        parsed[key] = value
                    elif not existing:
                        parsed[key] = value
                    continue
                if isinstance(value, dict):
                    if value or not existing:
                        parsed[key] = value
                    continue
                parsed[key] = value
        contact = parsed.get("contact", {})
        name = contact.get("name", {}).get("name")
        emails = contact.get("emails", [])
        phones = contact.get("phones", [])
        location = contact.get("location", {}).get("city") or contact.get("location", {}).get("country")
        linkedin = contact.get("urls", {}).get("linkedin")
        github = contact.get("urls", {}).get("github")
        raw_summary = (
            parsed.get("sections", {}).get("summary", {}).get("content")
            if isinstance(parsed.get("sections"), dict)
            else None
        )
        summary_section = _clean_summary_text(raw_summary) if raw_summary else None

        candidate = session.execute(
            select(Candidate).where(Candidate.id == job.candidate_id)
        ).scalar_one_or_none()
        if candidate:
            set_current_tenant(candidate.tenant_id)
            settings = get_settings()

            total_experience = parsed.get("total_experience") if isinstance(parsed, dict) else None
            det_years: float | None = None
            det_conf: float | None = None
            if isinstance(total_experience, dict):
                try:
                    raw_years = total_experience.get("total_years")
                    if raw_years is not None and str(raw_years).strip() != "":
                        det_years = float(raw_years)
                except (TypeError, ValueError):
                    det_years = None
                try:
                    raw_conf = total_experience.get("confidence")
                    if raw_conf is not None and str(raw_conf).strip() != "":
                        det_conf = float(raw_conf)
                except (TypeError, ValueError):
                    det_conf = None

            llm_years: float | None = None
            llm_resume = parsed.get("llm_resume") if isinstance(parsed, dict) else None
            if isinstance(llm_resume, dict):
                professional = llm_resume.get("professional_summary") or {}
                years = professional.get("years_of_experience")
                try:
                    llm_years = float(years) if years is not None else None
                except (TypeError, ValueError):
                    llm_years = None
                if not candidate.current_title:
                    candidate.current_title = professional.get("primary_role") or candidate.current_title

            det_ok = det_years is not None
            det_low_conf = (det_conf is not None and det_conf < 0.6)
            llm_enabled = settings.LLM_PROVIDER != "none"
            allow_llm_override = llm_enabled and (not det_ok or det_low_conf)

            final_years: float | None
            final_conf: float | None
            if allow_llm_override and llm_years is not None:
                final_years = llm_years
                final_conf = 0.65
            elif det_years is not None:
                final_years = det_years
                final_conf = det_conf if det_conf is not None else 0.7
            else:
                final_years = llm_years if llm_enabled else None
                final_conf = 0.65 if (final_years is not None) else None

            if final_years is not None:
                candidate.years_experience = final_years
                if final_conf is not None:
                    candidate.years_experience_confidence = max(
                        0.0, min(1.0, float(final_conf))
                    )
            candidate.full_name = name or candidate.full_name
            if emails:
                candidate.email = emails[0].get("email")
                if candidate.email:
                    candidate.email_hash = hash_value(candidate.email)
            if phones:
                candidate.phone = phones[0].get("phone")
            candidate.location = location or candidate.location
            candidate.linkedin_url = linkedin or candidate.linkedin_url
            candidate.github_url = github or candidate.github_url
            if summary_section and not candidate.summary:
                candidate.summary = summary_section
            candidate.status = CandidateStatus.SUCCESS

        session.execute(delete(WorkHistory).where(WorkHistory.candidate_id == job.candidate_id))
        session.execute(delete(Education).where(Education.candidate_id == job.candidate_id))
        session.execute(delete(Certification).where(Certification.candidate_id == job.candidate_id))
        session.execute(delete(CandidateSkill).where(CandidateSkill.candidate_id == job.candidate_id))
        session.execute(
            delete(CandidateAchievement).where(
                CandidateAchievement.candidate_id == job.candidate_id
            )
        )

        work_entries = parsed.get("work_experience", [])
        for entry in work_entries:
            session.add(
                WorkHistory(
                    candidate_id=job.candidate_id,
                    company_name=entry.get("company"),
                    client_name=entry.get("client"),
                    job_title=entry.get("title"),
                    start_date=_parse_date_str(entry.get("start_date")),
                    end_date=_parse_date_str(entry.get("end_date")),
                    is_current=entry.get("is_current", False),
                    location=entry.get("location"),
                    description=entry.get("description"),
                    display_order=None,
                )
            )

        if candidate and work_entries:
            first = work_entries[0] if isinstance(work_entries, list) else None
            if isinstance(first, dict):
                if not candidate.current_title:
                    candidate.current_title = first.get("title")
                if not candidate.current_company:
                    candidate.current_company = first.get("company")

        for entry in parsed.get("education", []):
            session.add(
                Education(
                    candidate_id=job.candidate_id,
                    institution=entry.get("institution"),
                    degree=entry.get("degree"),
                    field_of_study=entry.get("field_of_study"),
                    start_date=_parse_date_str(entry.get("start_date")),
                    end_date=_parse_date_str(entry.get("end_date")),
                    gpa=_parse_gpa(entry.get("gpa")),
                    description=entry.get("honors"),
                )
            )

        for entry in parsed.get("certifications", []):
            cert_name = entry.get("name") if isinstance(entry, dict) else None
            if not str(cert_name or "").strip():
                continue
            session.add(
                Certification(
                    candidate_id=job.candidate_id,
                    name=cert_name,
                    issuing_organization=entry.get("issuing_organization") if isinstance(entry, dict) else None,
                    issue_date=_parse_date_str(entry.get("issue_date")) if isinstance(entry, dict) else None,
                    expiry_date=_parse_date_str(entry.get("expiry_date")) if isinstance(entry, dict) else None,
                    credential_id=entry.get("credential_id") if isinstance(entry, dict) else None,
                )
            )

        seen_skill_ids: set[str] = set()
        for entry in parsed.get("skills", []):
            if not isinstance(entry, dict):
                continue

            raw_name = str(entry.get("name") or "").strip()
            normalized_raw = entry.get("normalized_name")
            normalized = (
                str(normalized_raw).strip().lower()
                if normalized_raw is not None and str(normalized_raw).strip()
                else None
            )
            if not raw_name:
                continue

            skill: Skill | None = None
            if normalized:
                skill = session.execute(
                    select(Skill).where(Skill.normalized_name == normalized)
                ).scalar_one_or_none()
            if not skill:
                skill = session.execute(select(Skill).where(Skill.name == raw_name)).scalar_one_or_none()

            if not skill:
                stmt = (
                    pg_insert(Skill)
                    .values(
                        name=raw_name,
                        category=entry.get("category"),
                        normalized_name=normalized,
                    )
                    .on_conflict_do_nothing(index_elements=["name"])
                    .returning(Skill.id)
                )
                inserted_id = session.execute(stmt).scalar_one_or_none()
                if inserted_id is not None:
                    skill = session.get(Skill, inserted_id)
                if not skill:
                    skill = session.execute(
                        select(Skill).where(Skill.name == raw_name)
                    ).scalar_one_or_none()
                if not skill and normalized:
                    skill = session.execute(
                        select(Skill).where(Skill.normalized_name == normalized)
                    ).scalar_one_or_none()

            if not skill:
                continue

            if normalized and not (skill.normalized_name or "").strip():
                skill.normalized_name = normalized
            if entry.get("category") and not skill.category:
                skill.category = entry.get("category")

            skill_id_key = str(skill.id)
            if skill_id_key in seen_skill_ids:
                continue
            seen_skill_ids.add(skill_id_key)

            session.add(
                CandidateSkill(
                    candidate_id=job.candidate_id,
                    skill_id=skill.id,
                    proficiency_level=_to_proficiency(entry.get("proficiency")),
                    years_experience=entry.get("years_experience"),
                )
            )

        achievements = parsed.get("achievements", [])
        if isinstance(achievements, list):
            for item in achievements:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("text") or item.get("title") or "").strip()
                if not title:
                    continue
                year_val: int | None = None
                m = re.search(r"\b(19\d{2}|20\d{2})\b", title)
                if m:
                    try:
                        year_val = int(m.group(1))
                    except ValueError:
                        year_val = None
                conf_val: float | None = None
                try:
                    if item.get("confidence") is not None:
                        conf_val = float(item.get("confidence"))
                except (TypeError, ValueError):
                    conf_val = None
                session.add(
                    CandidateAchievement(
                        candidate_id=job.candidate_id,
                        title=title,
                        year=year_val,
                        confidence=conf_val,
                    )
                )

        if candidate:
            discrepancies = find_date_overlaps(session, candidate.id)
            settings = get_settings()
            review_flags = compute_review_flags(
                job.parsed_data,
                job.confidence_score,
                settings.REVIEW_FIELD_THRESHOLD,
                discrepancies,
            )
            candidate.review_flags = review_flags
            if (
                job.confidence_score is not None
                and job.confidence_score < settings.REVIEW_CONFIDENCE_THRESHOLD
            ):
                candidate.review_status = ReviewStatus.PENDING
                candidate.review_flagged_at = datetime.now(timezone.utc)
                candidate.review_confidence = job.confidence_score

            applied_fields = apply_correction_patterns(session, candidate)
            if applied_fields:
                if "email" in applied_fields and candidate.email:
                    candidate.email_hash = hash_value(candidate.email)
                note = f"Auto-applied corrections: {', '.join(applied_fields)}"
                if candidate.review_notes:
                    candidate.review_notes = f"{candidate.review_notes}\n{note}"
                else:
                    candidate.review_notes = note

        if not job.original_file_copy_path or not job.extracted_text_path or not job.parsed_json_path:
            settings = get_settings()
            tenant_id = candidate.tenant_id if candidate else settings.DEFAULT_TENANT_ID
            base_key = f"resumes/{tenant_id}/{job.candidate_id}/{job.id}"

            if not job.original_file_copy_path:
                ext = Path(job.filename).suffix.lstrip(".").lower() or "bin"
                original_key = f"{base_key}/original.{ext}"
                if job.file_path.startswith("s3://") and settings.S3_BUCKET:
                    copied = copy_s3_object(job.file_path, original_key)
                    job.original_file_copy_path = copied.uri
                else:
                    src = Path(job.file_path)
                    dst = Path(settings.STORAGE_DIR) / original_key
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if src.exists():
                        shutil.copy2(src, dst)
                        job.original_file_copy_path = str(dst)

            if not job.extracted_text_path and job.raw_text:
                text_key = f"{base_key}/resume.txt"
                text_bytes = job.raw_text.encode("utf-8", errors="replace")
                if settings.S3_BUCKET:
                    try:
                        stored = upload_bytes_to_s3(text_bytes, text_key)
                        job.extracted_text_path = stored.uri
                    except RuntimeError as exc:
                        if settings.ENVIRONMENT.lower() in {"development", "local"}:
                            logger.warning(
                                "S3 upload failed; falling back to local storage",
                                extra={"error": str(exc), "key": text_key, "job_id": job_id},
                            )
                            job.extracted_text_path = save_bytes_to_local(text_bytes, text_key)
                        else:
                            raise
                else:
                    job.extracted_text_path = save_bytes_to_local(text_bytes, text_key)

            if not job.parsed_json_path and parsed is not None:
                json_key = f"{base_key}/resume.json"
                json_bytes = json.dumps(parsed, ensure_ascii=False, indent=2).encode(
                    "utf-8", errors="replace"
                )
                if settings.S3_BUCKET:
                    try:
                        stored = upload_bytes_to_s3(json_bytes, json_key)
                        job.parsed_json_path = stored.uri
                    except RuntimeError as exc:
                        if settings.ENVIRONMENT.lower() in {"development", "local"}:
                            logger.warning(
                                "S3 upload failed; falling back to local storage",
                                extra={"error": str(exc), "key": json_key, "job_id": job_id},
                            )
                            job.parsed_json_path = save_bytes_to_local(json_bytes, json_key)
                        else:
                            raise
                else:
                    job.parsed_json_path = save_bytes_to_local(json_bytes, json_key)

        job.status = ParsingJobStatus.SUCCESS
        job.last_stage = "save_to_database"
        job.completed_at = datetime.now(timezone.utc)
        session.commit()
        observe_parsing_success(job.confidence_score, job.started_at)
        return job_id
    except Exception as exc:
        session.rollback()
        _handle_task_error(job_id, exc, "save_to_database")
        _log_retry_exhausted(self, job_id, "save_to_database")
        raise
    finally:
        observe_stage_duration("save_to_database", time.perf_counter() - start_time)
        session.close()


@celery_app.task(name="app.workers.pipeline.retry_failed_jobs")
def retry_failed_jobs() -> None:
    session = SessionLocal()
    try:
        failed_jobs = session.execute(
            select(ParsingJob).where(ParsingJob.status == ParsingJobStatus.FAILED)
        ).scalars()
        for job in failed_jobs:
            logger.info("Retrying failed job", extra={"job_id": str(job.id)})
            start_parsing_workflow(str(job.id))
    finally:
        session.close()


@celery_app.task(name="app.workers.pipeline.cleanup_old_jobs")
def cleanup_old_jobs() -> None:
    settings = get_settings()
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.PARSING_JOB_RETENTION_DAYS)
    session = SessionLocal()
    try:
        session.execute(
            delete(ParsingJob).where(ParsingJob.completed_at.isnot(None)).where(
                ParsingJob.completed_at < cutoff
            )
        )
        session.commit()
    finally:
        session.close()


@celery_app.task(name="app.workers.pipeline.generate_accuracy_report")
def generate_accuracy_report() -> None:
    logger.info("Generating accuracy report (placeholder)")