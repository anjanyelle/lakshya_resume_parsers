from __future__ import annotations

import json
import logging
import re
import shutil
import time
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from celery import chain
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

import structlog

from app.core.config import get_settings
from app.core.encryption import set_current_tenant
import dateparser
from app.core.database import SessionLocal
from app.core.observability import (
    emit_parse_metrics,
    increment_jobs_total,
    observe_parsing_failure,
    observe_parsing_success,
    observe_stage_duration,
    PARSE_ERRORS,
    REVIEW_FLAG_TOTAL,
    SECTION_DETECTION_CONFIDENCE,
    SECTION_DETECTION_FALLBACK_TOTAL,
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
from app.services.parser.normalize import fix_concatenated_words, normalize_resume_text, normalize_text_for_skills_pre
from app.services.parser.section_parser import SectionParser
from app.services.parser.achievements_extractor import AchievementsExtractor
from app.services.parser.certification_validator import (
    CertificationValidator,
    deduplicate_certificates,
)
from app.services.parser.skill_extractor import (
    HARD_SKILL_BLACKLIST,
    SQL_SUBFUNCTION_MAP,
    SkillExtractor,
    SkillMatch,
    clean_skill_text_for_section,
    clean_text_for_skills,
    filter_skills_by_resume_text,
    is_atomic_skill,
    is_generic_skill,
    is_sentence_fragment,
    map_category_to_master,
    normalize_pdf_split_words,
    normalize_skill_name as normalize_skill_name_for_dedup,
    normalize_to_canonical,
    sanitize_category,
    strip_skill_token,
    tokenize_skills_by_comma,
)
from app.services.parser.work_experience_parser import JobEntry, WorkExperienceParser, TITLE_HINT_RE, COMPANY_HINT_RE
from app.services.parser.work_experience_sanitizer import (
    deduplicate_work_entries,
    sanitize_work_experience_entries,
)
from app.services.parser.quality_scoring import score_certifications, score_work_experience_jobs
from app.services.parser.structured_sanitizers import (
    sanitize_certifications_entries,
    sanitize_education_entries,
    sanitize_skill_entries,
)
from app.services.llm_service import LLMParsingService
from app.services.parser.normalize import clean_summary_and_skills_sections
from app.utils.pii import hash_value
from app.utils.review import apply_correction_patterns, compute_review_flags, find_date_overlaps
from app.services.storage import copy_s3_object, save_bytes_to_local, upload_bytes_to_s3
from app.services.parser.fallback_segmenter import FallbackSegmenter
from app.workers.celery_app import celery_app
from app.workers.doc_convert_task import convert_doc_to_docx_task
from app.workers.extract_clients_task import task_extract_clients
from app.workers.extract_text_task import extract_text_task
from app.workers.task_calculate_confidence import (
    build_per_field_confidence,
    record_quality_metrics,
)
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


def clean_summary(text: str) -> str:
    """
    Clean summary text: remove duplicate lines/paragraphs and sentences,
    trim to 1500 chars / 6 sentences only when very long. Call before saving.
    Normalizes " | " and "- | " from section parser so summary renders as readable text.
    """
    if not (text or "").strip():
        return text or ""
    # Normalize table-row style pipes (from section_parser._normalize_table_row) to spaces
    normalized = re.sub(r"\s*-\s*\|\s*", " ", text)
    normalized = re.sub(r"\s*\|\s*", " ", normalized)
    normalized = " ".join(normalized.split())  # collapse multiple spaces
    return _dedup_text_lines(normalized)


def _dedup_text_lines(text: str) -> str:
    """
    Remove duplicate lines and sentences from summary text.
    Deduplicates at paragraph level (lines) and sentence level.
    Trims only when very long (first 6 sentences if exceeds 1500 chars) to preserve full summary.
    """
    if not text:
        return text

    # 1. Paragraph-level dedup (by line, strip + compare)
    seen_lines: set[str] = set()
    lines_out: list[str] = []
    for line in text.splitlines():
        key = line.strip().lower()
        if key and key not in seen_lines:
            seen_lines.add(key)
            lines_out.append(line)
        elif not key:
            lines_out.append(line)
    paragraph_deduped = "\n".join(lines_out)

    # 2. Sentence-level dedup (split by ". ")
    flat = paragraph_deduped.replace("\n", " ").strip()
    if not flat:
        return paragraph_deduped

    parts = flat.split(". ")
    seen_sentences: set[str] = set()
    sentences: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        key = part.lower()
        if key not in seen_sentences:
            seen_sentences.add(key)
            sentences.append(part)

    result = ". ".join(sentences)

    # 3. Trim only when very long: first 12 sentences if exceeds 2500 chars (preserve full summary)
    if len(result) > 2500 and len(sentences) > 12:
        result = ". ".join(sentences[:12])

    return result


def sanitize_final_output(parsed_data: dict[str, Any]) -> dict[str, Any]:
    """
    Pipeline dedup guard: run at the very end before saving.
    Ensures no duplicates reach the database regardless of which parser ran.
    """
    if not parsed_data:
        return parsed_data or {}

    # 1. Deduplicate work entries
    work_exp = parsed_data.get("work_experience", [])
    work_before = len(work_exp) if isinstance(work_exp, list) else 0
    if isinstance(work_exp, list):
        parsed_data["work_experience"] = deduplicate_work_entries(work_exp)
    work_after = len(parsed_data.get("work_experience") or [])
    if work_before > 0 and work_after < work_before:
        dropped = work_before - work_after
        logger.warning(
            "sanitize_final_output: work_experience reduced by %d (before=%d, after=%d)",
            dropped,
            work_before,
            work_after,
        )

    # 2. Clean summary (dedup lines/sentences, trim)
    sections = parsed_data.get("sections") or {}
    if isinstance(sections, dict):
        summary_block = sections.get("summary") or {}
        if isinstance(summary_block, dict):
            content = summary_block.get("content")
            if content and isinstance(content, str):
                sections["summary"] = {**summary_block, "content": clean_summary(content)}
                parsed_data["sections"] = sections

    # 3. Deduplicate certificates
    certs = parsed_data.get("certifications", [])
    cert_before = len(certs) if isinstance(certs, list) else 0
    if isinstance(certs, list):
        parsed_data["certifications"] = deduplicate_certificates(certs)
    cert_after = len(parsed_data.get("certifications") or [])
    if cert_before > 0 and cert_after < cert_before:
        dropped = cert_before - cert_after
        logger.warning(
            "sanitize_final_output: certifications reduced by %d (before=%d, after=%d)",
            dropped,
            cert_before,
            cert_after,
        )

    # 4. Validate name is not None or empty, and ensure it's not a massive block of text
    contact = parsed_data.get("contact") or {}
    if isinstance(contact, dict):
        name_obj = contact.get("name")
        name_val = (
            name_obj.get("name") if isinstance(name_obj, dict) else name_obj 
        )
        if type(name_val) is str and (len(name_val) > 60 or "\n" in name_val or "##" in name_val):
            name_val = None  # Force reset if obviously corrupted

        if name_val is None:
            contact.setdefault("name", {})
            if isinstance(contact["name"], dict) and "name" not in contact["name"]: 
                contact["name"] = {"name": "", "confidence": 0.0}
            elif isinstance(contact["name"], dict):
                contact["name"]["name"] = ""
            parsed_data["contact"] = contact

    # 5. Log summary; warn if name empty after parsing
    jobs_count = len(parsed_data.get("work_experience") or [])
    certs_count = len(parsed_data.get("certifications") or [])
    contact_for_log = parsed_data.get("contact") or {}
    name_val = ""
    if isinstance(contact_for_log, dict):
        no = contact_for_log.get("name")
        name_val = (no.get("name") if isinstance(no, dict) else no) or ""
    if not (name_val or "").strip():
        logger.warning("Name empty after parsing — validation rule: do not overwrite with empty from LLM")
    summary_content = (
        (sections.get("summary") or {}).get("content")
        if isinstance(sections, dict) else ""
    )
    summary_len = len(summary_content) if isinstance(summary_content, str) else 0
    logger.info(
        "Final output: %d jobs, %d certs, name=%r, summary_len=%d",
        jobs_count,
        certs_count,
        name_val or "(empty)",
        summary_len,
    )

    return parsed_data


def start_parsing_workflow(job_id: str) -> str:
    structlog.contextvars.bind_contextvars(job_id=job_id)
    try:
        import sentry_sdk

        sentry_sdk.set_tag("job_id", job_id)
    except Exception:
        pass
    increment_jobs_total()
    settings = get_settings()

    job_for_path = None
    try:
        job_for_path = _load_job(job_id)
    except Exception:
        job_for_path = None

    source_path = getattr(job_for_path, "file_path", None) if job_for_path is not None else None
    is_doc_upload = bool(source_path) and str(source_path).lower().endswith(".doc")

    if settings.PARSING_MODE.lower() == "text_only":
        first = task_extract_text.si(job_id).set(queue="extract")
        if is_doc_upload and source_path:
            first = chain(
                convert_doc_to_docx_task.si(job_id, str(source_path)).set(queue="doc_convert"),
                task_extract_text.si(job_id).set(queue="extract"),
            )
        workflow = chain(
            first,
            task_clean_text.s().set(queue="parse"),
            task_finalize_text_only.s().set(queue="persist"),
        )
    elif settings.PARSING_MODE.lower() == "deterministic":
        first = task_extract_text.si(job_id).set(queue="extract")
        if is_doc_upload and source_path:
            first = chain(
                convert_doc_to_docx_task.si(job_id, str(source_path)).set(queue="doc_convert"),
                task_extract_text.si(job_id).set(queue="extract"),
            )
        workflow = chain(
            first,
            task_clean_text.s().set(queue="parse"),
            task_detect_sections.s().set(queue="parse"),
            task_extract_contact_info.s().set(queue="parse"),
            task_parse_work_experience.s().set(queue="parse"),
            task_extract_clients.s().set(queue="parse"),
            task_parse_education.s().set(queue="parse"),
            task_parse_certifications.s().set(queue="parse"),
            task_extract_achievements.s().set(queue="parse"),
            task_extract_skills.s().set(queue="parse"),
            task_taxonomy_mapping.s().set(queue="parse"),
            task_calculate_confidence.s().set(queue="parse"),
            task_save_to_database.s().set(queue="persist"),
        )
    else:
        first = task_extract_text.si(job_id).set(queue="extract")
        if is_doc_upload and source_path:
            first = chain(
                convert_doc_to_docx_task.si(job_id, str(source_path)).set(queue="doc_convert"),
                task_extract_text.si(job_id).set(queue="extract"),
            )
        workflow = chain(
            first,
            task_clean_text.s().set(queue="parse"),
            # Pass 1 → Section Detection
            task_detect_sections.s().set(queue="parse"),
            task_detect_resume_sections.s().set(queue="llm"),
            # Pass 2 → Entity Extraction
            task_extract_contact_info.s().set(queue="parse"),
            task_parse_work_experience.s().set(queue="parse"),
            task_extract_clients.s().set(queue="parse"),
            task_parse_education.s().set(queue="parse"),
            task_parse_certifications.s().set(queue="parse"),
            task_extract_achievements.s().set(queue="parse"),
            task_extract_personal_info.s().set(queue="llm"),
            task_extract_structured_resume.s().set(queue="llm"),
            task_normalize_structured_resume.s().set(queue="llm"),
            task_extract_work_experience_details.s().set(queue="llm"),
            task_llm_resume_parse.s().set(queue="llm"),
            task_classify_resume_type.s().set(queue="llm"),
            # Pass 3 → Skill Inference
            task_extract_skills.s().set(queue="parse"),
            task_extract_experience_skills.s().set(queue="llm"),
            # Pass 4 → Normalization
            task_normalize_education_details.s().set(queue="parse"),
            task_normalize_skills_llm.s().set(queue="llm"),
            task_taxonomy_mapping.s().set(queue="parse"),
            # Pass 5 → Confidence Scoring
            task_calculate_total_experience.s().set(queue="parse"),
            task_evaluate_extraction_confidence.s().set(queue="llm"),
            task_calculate_confidence.s().set(queue="parse"),
            # Pass 6 → Validation
            task_verify_extracted_data.s().set(queue="llm"),
            task_save_to_database.s().set(queue="persist"),
        )

    force_local = settings.ENVIRONMENT.lower() in {"development", "local"}
    session = SessionLocal()
    try:
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == _to_uuid(job_id))
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
        if is_doc_upload and source_path:
            convert_doc_to_docx_task.apply(args=[job_id, str(source_path)])
        tasks = [task_extract_text, task_clean_text]
        if settings.PARSING_MODE.lower() == "text_only":
            tasks.append(task_finalize_text_only)
        elif settings.PARSING_MODE.lower() == "deterministic":
            tasks.extend(
                [
                    task_detect_sections,
                    task_extract_contact_info,
                    task_parse_work_experience,
                    task_extract_clients,
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
                    task_extract_clients,
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
                select(ParsingJob).where(ParsingJob.id == _to_uuid(job_id))
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
                select(ParsingJob).where(ParsingJob.id == _to_uuid(job_id))
            ).scalar_one_or_none()
            if job and job.status == ParsingJobStatus.PROCESSING:
                job.task_id = f"local-{job_id}"
                job.last_stage = "local"
                session.commit()
        finally:
            session.close()
        return _run_local()


def _source_format_from_path(path: str | None) -> str | None:
    """Derive source_format from file path for format-aware normalization."""
    if not path:
        return None
    ext = Path(str(path)).suffix.lower().lstrip(".")
    if ext == "pdf":
        return "pdf"
    if ext in ("docx", "doc"):
        return "docx" if ext == "docx" else "doc"
    if ext in ("png", "jpg", "jpeg"):
        return "ocr"
    if ext == "txt":
        return "txt"
    return None


def _to_uuid(job_id: str | UUID) -> UUID:
    """Ensure job_id is a UUID for SQLAlchemy PostgreSQL UUID columns."""
    return job_id if isinstance(job_id, UUID) else UUID(job_id)


def _load_job(job_id: str) -> ParsingJob:
    session = SessionLocal()
    try:
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == _to_uuid(job_id))
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
            select(ParsingJob).where(ParsingJob.id == _to_uuid(job_id))
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


def _normalize_work_description(description: str | None) -> str | None:
    """Fix PDF-style run-on text and pipe separators for work history description."""
    if description is None or not str(description).strip():
        return None
    s = str(description).strip()
    s = fix_concatenated_words(s)
    s = s.replace(" | ", "\n").replace("|", "\n")
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s if s else None


def _normalize_work_experience_company_title(work_entries: list[dict[str, Any]]) -> None:
    """Fix swapped company/title in work entries (PDF/LLM often reverse them)."""
    from app.services.parser.work_experience_parser import WorkExperienceParser
    parser = WorkExperienceParser()
    for entry in work_entries:
        if not isinstance(entry, dict):
            continue
        company = entry.get("company")
        title = entry.get("title")
        if not company or not title:
            continue
        c_str = str(company).strip()
        t_str = str(title).strip()
        if not c_str or not t_str:
            continue
        
        # IMPROVEMENT: Only swap if both heuristics are very strong.
        # title hint in company field AND company hint in title field.
        # This prevents aggressive swapping for ambiguous strings.
        is_c_title = parser._looks_like_title(c_str)
        is_t_company = parser._looks_like_company(t_str)
        
        # Also check for strong hints to be extra sure
        has_c_title_hint = bool(TITLE_HINT_RE.search(c_str))
        has_t_company_hint = bool(COMPANY_HINT_RE.search(t_str))
        
        if is_c_title and is_t_company:
            # If both directions look swapped, we are very confident
            entry["company"] = title
            entry["title"] = company
            logger.info("Swapped company/title: %r <-> %r", c_str, t_str)
        elif has_c_title_hint and is_t_company and not parser._looks_like_company(c_str):
            # Company field has a strong title hint and looks like a title, 
            # while Title field looks like a company.
            entry["company"] = title
            entry["title"] = company
            logger.info("Swapped company/title (hint-based): %r <-> %r", c_str, t_str)


def _is_raw_text_entry(entry: dict[str, Any]) -> bool:
    """Treat wrapper like {\"data\": \"raw text\"} as invalid (not a work experience object)."""
    if not isinstance(entry, dict) or len(entry) != 1:
        return False
    data_val = entry.get("data")
    return isinstance(data_val, str)


def _normalize_work_entry(entry: dict[str, Any]) -> dict[str, Any]:
    bullets = entry.get("bullets") or entry.get("responsibilities")
    if not isinstance(bullets, list):
        bullets = [b for b in (bullets or "").split("\n") if str(b).strip()] if bullets else []
    desc = entry.get("description")
    if desc is None and bullets:
        desc = "\n".join(str(b) for b in bullets)
    return {
        "title": str(entry.get("title") or entry.get("job_title") or "").strip() or "",
        "designation": str(entry.get("designation") or "").strip() or "",
        "company": str(entry.get("company") or entry.get("company_name") or "").strip() or "",
        "client": entry.get("client") if entry.get("client") else None,
        "location": str(entry.get("location") or "").strip() or "",
        "employment_type": str(entry.get("employment_type") or "").strip() or "",
        "start_date": str(entry.get("start_date") or "").strip() or "",
        "end_date": str(entry.get("end_date") or "").strip() or "",
        "is_current": bool(entry.get("is_current", False)),
        "duration_months": int(entry.get("duration_months") or 0),
        "description": str(desc or "").strip() if desc is not None else "",
        "bullets": [str(b).strip() for b in bullets if str(b).strip()],
        "confidence": float(entry.get("confidence") or 0.0),
    }


def _is_valid_work_entry(entry: dict[str, Any]) -> bool:
    """Reject entries with empty/missing company or title, contamination, or fragment fields."""
    if not isinstance(entry, dict):
        return False
    if _is_raw_text_entry(entry):
        return False
    company = str(entry.get("company") or entry.get("company_name") or "").strip()
    title = str(entry.get("title") or entry.get("job_title") or "").strip()
    if not company and not title:
        return False
    if len(company) > 120 or len(title) > 120:
        return False
    contamination = re.compile(
        r"^(?:keynote\s+speaker|featured\s+speaker|panelist|workshop\s+lead|guest\s+lecturer|"
        r"selected\s+peer|publications?)\s*[:\|]",
        re.IGNORECASE,
    )
    if contamination.search(company) or contamination.search(title):
        return False
    bad_title_company = re.compile(
        r"^(?:annual\s+revenue|private\s+cloud|\$[\d.]+\s*[bmk]?\)?|\(\s*process\s+excel)\s*$|"
        r"^\s*&\s*principal(\s*&\s*principal)*\s*$",
        re.IGNORECASE,
    )
    if bad_title_company.search(company) or bad_title_company.search(title):
        return False
    c_lower = company.lower().strip()
    t_lower = title.lower().strip()
    if c_lower in ("annual revenue", "private cloud") or t_lower in ("annual revenue", "private cloud"):
        return False
    if c_lower.startswith("annual revenue") or t_lower.startswith("annual revenue"):
        return False
    return True


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
    contact = merged.get("contact") or {}
    candidate_info = (
        llm_resume.get("candidate_information")
        or llm_resume.get("candidate_info")
        or llm_resume.get("candidate")
        or {}
    )
    if isinstance(candidate_info, dict):
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
            responsibilities = entry.get("responsibilities") or entry.get("bullets")
            if isinstance(responsibilities, list):
                description = "\n".join([str(item) for item in responsibilities if item])
            else:
                description = str(responsibilities) if responsibilities else None
            d = {
                "company": _get_first(entry, "client_name", "company", "client"),
                "title": _get_first(entry, "role", "title"),
                "start_date": _get_first(entry, "start_date"),
                "end_date": _get_first(entry, "end_date"),
                "is_current": entry.get("is_current", False),
                "location": _get_first(entry, "location"),
                "description": _normalize_work_description(description),
                "bullets": responsibilities if isinstance(responsibilities, list) else [],
            }
            if _is_valid_work_entry(d):
                work_items.append(_to_canonical_work_entry(d))
        if work_items:
            merged["work_experience"] = work_items

    work_llm = parsed.get("work_experience_llm")
    existing_work = merged.get("work_experience")
    use_llm = (
        isinstance(work_llm, list)
        and work_llm
        and (not existing_work or len(work_llm) > len(existing_work))
    )
    if use_llm:
        work_items = []
        for entry in work_llm:
            if not isinstance(entry, dict):
                continue
            responsibilities = entry.get("responsibilities") or entry.get("bullets")
            if isinstance(responsibilities, list):
                description = "\n".join([str(i) for i in responsibilities if i])
            else:
                description = str(responsibilities) if responsibilities else None
            description = _normalize_work_description(description or entry.get("description"))
            d = {
                "company": entry.get("company_name") or entry.get("company"),
                "client": entry.get("client"),
                "title": entry.get("job_title") or entry.get("title"),
                "start_date": entry.get("start_date"),
                "end_date": entry.get("end_date"),
                "is_current": entry.get("is_current", False),
                "location": entry.get("location"),
                "description": description,
                "designation": entry.get("designation"),
                "employment_type": entry.get("employment_type"),
                "duration_months": entry.get("duration_months"),
                "bullets": responsibilities if isinstance(responsibilities, list) else [],
                "confidence": entry.get("confidence"),
            }
            if _is_valid_work_entry(d):
                work_items.append(_to_canonical_work_entry(d))
        if work_items:
            merged["work_experience"] = work_items

    _normalize_work_experience_company_title(merged.get("work_experience") or [])

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
    raw = str(value).strip()
    if not raw:
        return None

    # Fallbacks for formats dateparser may not handle well
    q_match = re.match(r"Q([1-4])\s+(\d{4})", raw, re.IGNORECASE)
    if q_match:
        q, year = int(q_match.group(1)), int(q_match.group(2))
        month = (q - 1) * 3 + 1
        return date(year, month, 1)

    season_match = re.match(
        r"(Spring|Summer|Fall|Winter)\s+(\d{4})", raw, re.IGNORECASE
    )
    if season_match:
        season, year = season_match.group(1).lower(), int(season_match.group(2))
        month = {"spring": 3, "summer": 6, "fall": 9, "winter": 12}.get(season, 1)
        return date(year, month, 1)

    # MMM 'YY or MMM 'YY -> normalize to MMM 20YY for dateparser
    apostrophe_match = re.match(
        r"([A-Za-z]{3,})\s*['\u2019\u2018]\s*(\d{2})\b", raw
    )
    if apostrophe_match:
        raw = f"{apostrophe_match.group(1)} 20{apostrophe_match.group(2)}"

    # MMM YY (without ' or ') -> normalize to MMM 20YY
    mmm_yy_match = re.match(r"^([A-Za-z]{3,})\s+(\d{2})$", raw)
    if mmm_yy_match:
        raw = f"{mmm_yy_match.group(1)} 20{mmm_yy_match.group(2)}"

    # DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY (day first)
    dmy_match = re.match(r"(\d{1,2})[./\-](\d{1,2})[./\-](\d{2,4})\b", raw)
    if dmy_match:
        d, m, y = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
        if y < 100:
            y += 2000 if y < 50 else 1900
        if 1 <= d <= 31 and 1 <= m <= 12:
            try:
                return date(y, m, d)
            except ValueError:
                pass

    # YYYY.MM or YYYY/MM (year first)
    ym_match = re.match(r"(\d{4})[./\-](\d{1,2})\b", raw)
    if ym_match:
        y, m = int(ym_match.group(1)), int(ym_match.group(2))
        if 1 <= m <= 12:
            try:
                return date(y, m, 1)
            except ValueError:
                pass

    # YY.MM, YY/MM, YY-MM (year first, 2-digit year)
    yy_m_match = re.match(r"^(\d{2})[./\-](\d{1,2})\b", raw)
    if yy_m_match:
        yy, m = int(yy_m_match.group(1)), int(yy_m_match.group(2))
        y = 2000 + yy if yy < 50 else 1900 + yy
        if 1 <= m <= 12:
            try:
                return date(y, m, 1)
            except ValueError:
                pass

    parsed = dateparser.parse(
        raw,
        settings={
            "PREFER_DAY_OF_MONTH": "first",
            "PREFER_DATES_FROM": "past",
        },
    )
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


def _parse_gpa(value: str | float | int | None) -> float | None:
    """Parse GPA for DB storage. Accepts string (e.g. '7.81', '4.0/4.0', '85%'), int, or float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value < 0 or value > 100:
            return None
        return float(value)
    s = (value if isinstance(value, str) else str(value)).strip()
    if not s:
        return None
    if "/" in s:
        num = s.split("/")[0].strip()
        try:
            return float(num)
        except ValueError:
            return None
    if s.endswith("%"):
        try:
            return float(s[:-1].strip())
        except ValueError:
            return None
    try:
        return float(s)
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
        source_format = _source_format_from_path(
            getattr(job, "file_path", None) or getattr(job, "extracted_text_path", None)
        )
        raw_len = len(job.raw_text or "")
        cleaned = normalize_resume_text(job.raw_text, source_format=source_format)
        cleaned_len = len(cleaned or "")
        logger.info(
            "[DATA-LOSS CHECK] Clean text stage: job_id=%s, raw_len=%d, cleaned_len=%d, source_fmt=%s, sample_after=%s",
            job_id,
            raw_len,
            cleaned_len,
            source_format or "unknown",
            repr((cleaned or "")[: 150] + ("..." if len(cleaned or "") > 150 else ""))[: 180],
            extra={"job_id": job_id, "raw_chars": raw_len, "cleaned_chars": cleaned_len},
        )
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
            select(ParsingJob).where(ParsingJob.id == _to_uuid(job_id))
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

        sections = parsed.get("sections") if isinstance(parsed.get("sections"), dict) else {}
        detected_headers = parsed.get("detected_headers") if isinstance(parsed.get("detected_headers"), list) else []

        max_header_conf = 0.0
        for h in detected_headers:
            if not isinstance(h, dict):
                continue
            try:
                max_header_conf = max(max_header_conf, float(h.get("confidence", 0.0) or 0.0))
            except (TypeError, ValueError):
                continue

        def _sec_conf(key: str) -> float:
            block = sections.get(key) if isinstance(sections, dict) else None
            if not isinstance(block, dict):
                return 0.0
            try:
                return float(block.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                return 0.0

        exp_conf = _sec_conf("experience")
        skills_conf = _sec_conf("skills")
        edu_conf = _sec_conf("education")
        cert_conf = _sec_conf("certifications")

        deterministic_ok = (
            max_header_conf >= 0.9
            and exp_conf >= 0.6
            and (skills_conf >= 0.6 or edu_conf >= 0.6 or cert_conf >= 0.55)
        )
        if deterministic_ok:
            return job_id

        def _llm_excerpt(text: str) -> str:
            lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
            head = lines[:220]
            # Include a focused experience anchor window to help section inference on messy PDFs.
            exp_excerpt = WorkExperienceParser.build_date_anchor_excerpt(text or "", context_lines=3)
            chunks: list[str] = []
            if head:
                chunks.append("\n".join(head))
            if exp_excerpt:
                chunks.append(exp_excerpt)
            merged = "\n\n".join([c for c in chunks if c]).strip()
            if len(merged) > 12000:
                merged = merged[:12000]
            return merged

        llm = LLMParsingService()
        excerpt = _llm_excerpt(job.raw_text)
        payload = llm.detect_resume_sections(excerpt)
        if isinstance(payload, dict):
            debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
            debug_bundle = dict(debug_bundle)
            debug_bundle["section_boundary_llm"] = {
                "triggered": True,
                "reason": {
                    "max_header_confidence": max_header_conf,
                    "experience_confidence": exp_conf,
                    "skills_confidence": skills_conf,
                    "education_confidence": edu_conf,
                    "certifications_confidence": cert_conf,
                },
                "excerpt_chars": len(excerpt),
            }
            _update_job(
                job_id,
                last_stage="detect_resume_sections",
                parsed_data=_merge_parsed(
                    job,
                    {
                        "sections_detected": payload.get("sections_detected", []),
                        "sections_detected_excerpt_chars": len(excerpt),
                        "sections_detected_deterministic_max_header_conf": max_header_conf,
                        "debug": debug_bundle,
                    },
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
            # Store only education_normalized; do NOT overwrite "education" here so we keep
            # the deterministic parser's multiple entries when it found more than one.
            existing_education = parsed.get("education", [])
            existing_list = (
                existing_education
                if isinstance(existing_education, list)
                else [existing_education] if existing_education else []
            )
            # Overwrite education only when LLM found more entries than the parser
            if len(normalized_entries) >= len(existing_list):
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
            else:
                _update_job(
                    job_id,
                    last_stage="normalize_education_details",
                    parsed_data=_merge_parsed(
                        job,
                        {"education_normalized": normalized_entries},
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
            experience_text = (job.raw_text or "").strip()
        else:
            existing_work = parsed.get("work_experience")
            if not (isinstance(existing_work, list) and len(existing_work) >= 2):
                experience_text = (job.raw_text or "").strip()
        if not experience_text:
            return job_id

        experience_text = normalize_resume_text(experience_text)
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

        exp_skills = _coerce_list(parsed.get("experience_skills"))
        direct_skills = _coerce_list(parsed.get("skills"))
        skills = exp_skills + direct_skills
        if not isinstance(skills, list) or not skills:
            return job_id

        llm = LLMParsingService()
        result = llm.normalize_deduplicate_skills(skills)
        if isinstance(result, dict):
            _update_job(
                job_id,
                last_stage="normalize_skills_llm",
                parsed_data=_merge_parsed(
                    job,
                    {
                        "skills_normalized": result.get("normalized_skills", []),
                        "skills": result.get("normalized_skills", []),
                    },
                ),
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
                            if key == "work_experience" and parsed.get("work_experience_llm"):
                                continue
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
                version=entry.get("version"),
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
            "version": match.version,
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
        detected_headers = parser.get_detected_headers()
        section_meta = parser.get_section_metadata()
        section_map = parser.get_section_map()
        payload = {
            key: {
                "content": value.content,
                "confidence": value.confidence,
                "start_line": getattr(value, "start_line", 0) or 0,
                "end_line": getattr(value, "end_line", 0) or 0,
                "evidence_heading": getattr(value, "evidence_heading", "") or "",
                "method": getattr(value, "method", "") or "",
                **(section_meta.get(key) if isinstance(section_meta.get(key), dict) else {}),
            }
            for key, value in sections.items()
        }

        max_header_conf = 0.0
        for h in detected_headers:
            if not isinstance(h, dict):
                continue
            try:
                max_header_conf = max(max_header_conf, float(h.get("confidence", 0.0) or 0.0))
            except (TypeError, ValueError):
                continue

        avg_sec_conf = 0.0
        try:
            sec_confs = [
                float(val.get("confidence", 0.0) or 0.0)
                for val in payload.values()
                if isinstance(val, dict)
            ]
            avg_sec_conf = (sum(sec_confs) / len(sec_confs)) if sec_confs else 0.0
        except Exception:  # noqa: BLE001
            avg_sec_conf = 0.0

        settings = get_settings()
        fallback_activated = False
        fallback_method: str | None = None

        if settings.LLM_PROVIDER == "none" and avg_sec_conf < 0.6 and job.raw_text:
            fb = FallbackSegmenter()
            fb_sections = fb.segment(job.raw_text)
            if isinstance(fb_sections, dict) and fb_sections:
                fallback_activated = True
                SECTION_DETECTION_FALLBACK_TOTAL.inc()
                FALLBACK_SEGMENTER_TOTAL.inc()

                try:
                    methods = [
                        str(v.get("method") or "")
                        for v in fb_sections.values()
                        if isinstance(v, dict)
                    ]
                    fallback_method = methods[0] if methods else None
                except Exception:  # noqa: BLE001
                    fallback_method = None

                merged: dict[str, dict[str, object]] = {}
                for k, v in payload.items():
                    if not isinstance(v, dict):
                        continue
                    try:
                        conf = float(v.get("confidence", 0.0) or 0.0)
                    except (TypeError, ValueError):
                        conf = 0.0
                    # Keep sections with conf >= 0.45 (lowered from 0.6 to avoid discarding valid content)
                    if conf >= 0.45:
                        merged[k] = v

                for k, v in fb_sections.items():
                    if not isinstance(v, dict):
                        continue
                    if k not in merged:
                        merged[k] = v

                payload = merged
                section_map = [
                    {
                        "section_key": key,
                        "start_line": int(block.get("start_line", 0) or 0),
                        "end_line": int(block.get("end_line", 0) or 0),
                    }
                    for key, block in merged.items()
                    if isinstance(block, dict)
                ]
                section_map = sorted(
                    section_map,
                    key=lambda x: (
                        int(x.get("start_line", 0) or 0),
                        str(x.get("section_key") or ""),
                    ),
                )

        cleaned_counts = {"moved_summary_to_skills": 0, "moved_skills_to_summary": 0}
        try:
            cleaned_sections, cleaned_counts = clean_summary_and_skills_sections(payload)
            if isinstance(cleaned_sections, dict):
                payload = cleaned_sections
        except Exception:  # noqa: BLE001
            cleaned_counts = {"moved_summary_to_skills": 0, "moved_skills_to_summary": 0}

        for section_key, block in payload.items():
            if not isinstance(block, dict):
                continue
            try:
                conf_val = float(block.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                conf_val = 0.0
            SECTION_DETECTION_CONFIDENCE.labels(section=str(section_key)).observe(
                max(0.0, min(1.0, conf_val))
            )

        debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        debug_bundle = dict(debug_bundle)
        debug_bundle["sections"] = {
            "detected_headers_count": len(detected_headers) if isinstance(detected_headers, list) else 0,
            "max_header_confidence": max_header_conf,
            "avg_section_confidence": float(avg_sec_conf),
            "fallback_segmenter_activated": bool(fallback_activated),
            "fallback_segmenter_method": fallback_method,
            "moved_summary_to_skills": int(cleaned_counts.get("moved_summary_to_skills", 0) or 0),
            "moved_skills_to_summary": int(cleaned_counts.get("moved_skills_to_summary", 0) or 0),
            "section_map": section_map if isinstance(section_map, list) else [],
            "detected_headers": detected_headers if isinstance(detected_headers, list) else [],
            "section_confidences": {
                key: float(val.get("confidence", 0.0) or 0.0)
                for key, val in payload.items()
                if isinstance(val, dict)
            },
        }

        exp_block = payload.get("experience") or {}
        exp_conf = float(exp_block.get("confidence") or 0)
        logger.info(
            "Sections detected: keys=%s, experience_conf=%.2f",
            list(payload.keys()),
            exp_conf,
            extra={"job_id": job_id},
        )
        logger.info(
            "Section detection completed",
            extra={
                "job_id": job_id,
                "avg_section_confidence": float(avg_sec_conf),
                "fallback_segmenter_activated": bool(fallback_activated),
                "fallback_segmenter_method": fallback_method,
                "moved_summary_to_skills": int(cleaned_counts.get("moved_summary_to_skills", 0) or 0),
                "moved_skills_to_summary": int(cleaned_counts.get("moved_skills_to_summary", 0) or 0),
            },
        )
        logger.info(
            "DIAG sections keys=%s exp_len=%d exp_conf=%.2f",
            list(payload.keys()),
            len(str(exp_block.get("content", "") or "")),
            exp_conf,
        )
        _update_job(
            job_id,
            last_stage="detect_sections",
            parsed_data=_merge_parsed(
                job,
                {
                    "sections": payload,
                    "detected_headers": detected_headers,
                    "section_map": section_map,
                    "debug": debug_bundle,
                },
            ),
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
        name_val = (contact.name.name or "").strip() or "(empty)"
        logger.info(
            "Contact extracted: name=%s, emails=%d, phones=%d",
            name_val,
            len(contact.emails),
            len(contact.phones),
            extra={"job_id": job_id},
        )
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

        EXPERIENCE_KEYS = [
            # Standard (include space variant for section keys that may be stored with space)
            "experience",
            "work_experience",
            "professional_experience",
            "professional experience",
            "employment",
            "work_history",
            "employment_history",
            "career_history",
            "positions_held",
            "relevant_experience",
            # Variations
            "professional_background",
            "career_profile",
            "career_summary",
            "employment_record",
            "job_history",
            "work_background",
            "industry_experience",
            "technical_experience",
            "corporate_experience",
            "consulting_experience",
            # Internship related
            "internship",
            "internships",
            "internship_experience",
            "industrial_training",
            "inplant_training",
            "summer_internship",
            "apprenticeship",
            "apprenticeships",
            "traineeship",
            # Project-based (important for freshers)
            "projects",
            "project_experience",
            "academic_projects",
            "professional_projects",
            "key_projects",
            "live_projects",
            "client_projects",
            "research_projects",
            "freelance_projects",
            # Contract / freelance
            "freelance_experience",
            "contract_experience",
            "consultant_experience",
            "independent_projects",
            # Military / Govt
            "military_service",
            "armed_forces_experience",
            "government_service",
            # Other real resume headers
            "assignments",
            "engagements",
            "roles_and_responsibilities",
            "professional_assignments",
            "career_overview",
            "employment_details",
            "work_details",
        ]

        experience_text = ""
        experience_block = {}
        for key in EXPERIENCE_KEYS:
            block = sections.get(key, {}) if isinstance(sections, dict) else {}
            if not isinstance(block, dict):
                continue
            content = str(block.get("content", "") or "").strip()
            if len(content) > len(experience_text):
                experience_text = content
                experience_block = block

        try:
            exp_conf = float(experience_block.get("confidence", 0.0) or 0.0) if experience_block else 0.0
        except (TypeError, ValueError):
            exp_conf = 0.0
        has_experience_section = bool(experience_text.strip())

        parser = WorkExperienceParser()
        raw_text = job.raw_text or ""

        source_format = _source_format_from_path(
            getattr(job, "file_path", None) or getattr(job, "extracted_text_path", None)
        )

        def _parse_deterministic(text: str) -> list[JobEntry]:
            if not text.strip():
                return []
            # Avoid calling the LLM inside parse_experience_section for this quality probe.
            try:
                original_llm_fallback = getattr(parser, "_llm_fallback", None)
                setattr(parser, "_llm_fallback", lambda chunk: None)
                return parser.parse_experience_section(text, source_format=source_format)
            finally:
                if original_llm_fallback is not None:
                    setattr(parser, "_llm_fallback", original_llm_fallback)

        payload: list[dict[str, object]] = []

        excerpt = ""
        if raw_text.strip():
            excerpt = WorkExperienceParser.build_date_anchor_excerpt(raw_text, context_lines=5) or ""

        chosen_experience_text = experience_text if has_experience_section else raw_text
        primary_jobs = _parse_deterministic(experience_text) if has_experience_section else _parse_deterministic(raw_text)
        primary_score = score_work_experience_jobs(primary_jobs)
        logger.info(
            "DIAG primary_jobs count=%d first=%s",
            len(primary_jobs),
            str(primary_jobs[0])[:120] if primary_jobs else "NONE",
        )

        ambiguous_headers = 0
        for j in primary_jobs:
            company = str(j.company or "").strip().lower()
            title = str(j.title or "").strip().lower()
            if not company or not title:
                ambiguous_headers += 1
                continue
            if company in {"usa", "u.s.a", "united states", "united states of america"}:
                ambiguous_headers += 1
                continue
            if title in {"usa", "u.s.a"}:
                ambiguous_headers += 1
                continue

        excerpt_score: float | None = None
        if excerpt.strip():
            excerpt_jobs = _parse_deterministic(excerpt)
            excerpt_score = score_work_experience_jobs(excerpt_jobs)

        # Prefer the excerpt when:
        # - we had a section slice (otherwise raw_text is already the widest input), and
        # - the section slice is borderline confidence, or
        # - the primary parse quality is low (even if confidence was high)
        if excerpt_score is not None:
            borderline = 0.45 <= exp_conf <= 0.72
            low_quality = primary_score < 1.6
            if has_experience_section and (borderline or low_quality) and excerpt_score > primary_score:
                chosen_experience_text = excerpt

        chosen_source = "section" if has_experience_section else "raw_text"
        if chosen_experience_text == excerpt and excerpt.strip():
            chosen_source = "date_anchor_excerpt"

        def _cap_llm_text(value: str) -> str:
            lines = [ln for ln in (value or "").splitlines()]
            value2 = "\n".join(lines[:220]).strip()
            if len(value2) > 8000:
                value2 = value2[:8000]
            return value2

        debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        debug_bundle = dict(debug_bundle)
        llm_triggered = False
        llm_reason: list[str] = []
        llm_input_chars: int | None = None
        if exp_conf < 0.55:
            llm_reason.append("low_section_confidence")
        if primary_score < 1.2:
            llm_reason.append("low_quality_score")
        if ambiguous_headers >= 2:
            llm_reason.append("ambiguous_headers")

        if (exp_conf < 0.55 or primary_score < 1.2 or ambiguous_headers >= 2) and raw_text.strip():
            settings = get_settings()
            llm_source = _cap_llm_text(chosen_experience_text or excerpt)
            if llm_source and settings.LLM_PROVIDER != "none":
                llm_input_chars = len(llm_source)
                llm = LLMParsingService()
                llm_items = llm.extract_work_experience(llm_source) or []
                if isinstance(llm_items, list) and llm_items:
                    llm_triggered = True
                    for item in llm_items:
                        if not isinstance(item, dict):
                            continue
                        responsibilities = item.get("responsibilities")
                        bullets: list[str] = []
                        if isinstance(responsibilities, list):
                            for r in responsibilities:
                                rr = str(r or "").strip()
                                if rr:
                                    bullets.append(rr)
                        description = "\n".join(f"- {b}" for b in bullets).strip() if bullets else None
                        payload.append(
                            {
                                "company": item.get("company") or item.get("company_name"),
                                "title": item.get("title") or item.get("job_title"),
                                "start_date": item.get("start_date"),
                                "end_date": item.get("end_date"),
                                "is_current": bool(item.get("is_current", False)),
                                "location": item.get("location"),
                                "description": description,
                                "bullets": bullets,
                                "client": item.get("client") or item.get("client_name"),
                            }
                        )

        debug_bundle["work_experience"] = {
            "chosen_source": chosen_source,
            "has_experience_section": has_experience_section,
            "experience_section_confidence": exp_conf,
            "experience_section_chars": len(experience_text or ""),
            "raw_text_chars": len(raw_text or ""),
            "excerpt_chars": len(excerpt or ""),
            "primary_quality_score": primary_score,
            "excerpt_quality_score": excerpt_score,
            "ambiguous_headers": ambiguous_headers,
            "llm_triggered": llm_triggered,
            "llm_reason": llm_reason,
            "llm_input_chars": llm_input_chars,
            "method": "llm" if llm_triggered else "deterministic",
        }

        if not payload:
            if not has_experience_section and raw_text.strip():
                experience_text = raw_text
            elif exp_conf < 0.55 and raw_text.strip():
                experience_text = chosen_experience_text or excerpt or raw_text
            else:
                experience_text = chosen_experience_text or experience_text or raw_text

            jobs = parser.parse_experience_section(experience_text, source_format=source_format)
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

        today = date.today()

        def _parse_entry_date(value: object) -> date | None:
            if value is None:
                return None
            if isinstance(value, date):
                return value
            raw = str(value).strip()
            if not raw:
                return None
            try:
                return _parse_date_str(raw)
            except Exception:
                return None

        def _company_is_suspicious(value: object) -> bool:
            cleaned = str(value or "").strip()
            if not cleaned:
                return True
            lowered = cleaned.lower()
            if lowered in {"present", "current", "till", "to", "till date", "now"}:
                return True
            if len(cleaned) <= 1:
                return True
            if any(tok in lowered for tok in ("present", "current", "till", "to")) and len(cleaned) <= 18:
                return True
            if any(ch.isdigit() for ch in cleaned):
                return True
            if re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b", lowered):
                return True
            return False

        def _month_range_for(entry: dict[str, object]) -> tuple[int, int] | None:
            start = _parse_entry_date(entry.get("start_date") or entry.get("from") or entry.get("start"))
            if not start:
                return None
            end_raw = entry.get("end_date") or entry.get("to") or entry.get("end")
            is_current = bool(entry.get("is_current"))
            end: date | None
            if is_current or _looks_like_present(str(end_raw) if end_raw else None):
                end = today
            elif end_raw:
                end = _parse_entry_date(end_raw)
            else:
                end = today
            if not end:
                return None
            if end < start:
                return None
            return _month_index(start), _month_index(end)

        validation: dict[str, Any] = {
            "date_order_errors": 0,
            "date_overlap_flags": 0,
            "suspicious_company_flags": 0,
            "sorted": True,
        }

        parsed_entries: list[dict[str, object]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            entry = dict(item)
            start = _parse_entry_date(entry.get("start_date"))
            end_raw = entry.get("end_date")
            end = _parse_entry_date(end_raw)
            if bool(entry.get("is_current")) or _looks_like_present(str(end_raw) if end_raw else None):
                end = today
            entry["_start_date_parsed"] = start
            entry["_end_date_parsed"] = end

            if start is not None and end is not None and end < start:
                entry["date_order_error"] = True
                validation["date_order_errors"] = int(validation.get("date_order_errors", 0)) + 1

            company_val = entry.get("company")
            if _company_is_suspicious(company_val):
                entry["company_flag_error"] = True
                validation["suspicious_company_flags"] = int(validation.get("suspicious_company_flags", 0)) + 1

            parsed_entries.append(entry)

        def _sort_key(e: dict[str, object]) -> tuple[int, int]:
            start = e.get("_start_date_parsed")
            if isinstance(start, date):
                return 0, -_month_index(start)
            return 1, 0

        parsed_entries.sort(key=_sort_key)

        def _company_key(e: dict[str, object]) -> str:
            return str(e.get("company") or "").strip().lower()

        def _months_overlap(a: tuple[int, int], b: tuple[int, int]) -> int:
            start = max(a[0], b[0])
            end = min(a[1], b[1])
            if end < start:
                return 0
            return (end - start) + 1

        overlap_pairs: list[dict[str, object]] = []
        for i in range(len(parsed_entries)):
            a = parsed_entries[i]
            a_range = _month_range_for(a)
            if not a_range:
                continue
            a_company = _company_key(a)
            for j in range(i + 1, len(parsed_entries)):
                b = parsed_entries[j]
                b_range = _month_range_for(b)
                if not b_range:
                    continue
                b_company = _company_key(b)
                if not a_company or not b_company or a_company == b_company:
                    continue
                overlap = _months_overlap(a_range, b_range)
                if overlap > 3:
                    a["date_overlap_flag"] = True
                    b["date_overlap_flag"] = True
                    overlap_pairs.append(
                        {
                            "company_a": a.get("company"),
                            "company_b": b.get("company"),
                            "overlap_months": int(overlap),
                        }
                    )

        if overlap_pairs:
            validation["date_overlap_flags"] = len(overlap_pairs)

        ranges: list[tuple[int, int]] = []
        for entry in parsed_entries:
            r = _month_range_for(entry)
            if r:
                ranges.append(r)
        merged = _merge_month_ranges(ranges)
        total_months = int(sum((end_i - start_i) + 1 for start_i, end_i in merged))
        total_years = round(total_months / 12.0, 1)
        validation["total_experience_months"] = total_months
        validation["total_experience_years"] = total_years
        if overlap_pairs:
            validation["overlap_pairs"] = overlap_pairs[:25]

        for entry in parsed_entries:
            entry.pop("_start_date_parsed", None)
            entry.pop("_end_date_parsed", None)

        payload = parsed_entries

        _update_job(
            job_id,
            last_stage="parse_work_experience",
            parsed_data=_merge_parsed(
                job,
                {
                    "work_experience": payload,
                    "total_experience_years": total_years,
                    "total_experience_months": total_months,
                    "debug": {
                        **debug_bundle,
                        "work_experience": {
                            **(debug_bundle.get("work_experience") if isinstance(debug_bundle.get("work_experience"), dict) else {}),
                            "validation": validation,
                        },
                    },
                },
            ),
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
                **asdict(entry),
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
        # Resolve skills section: canonical key is "skills"; section_parser/fallback map "technical skills" -> "skills".
        # Support both "skills" and "technical_skills" so any code path renders skills correctly.
        skills_block = None
        if isinstance(sections, dict):
            skills_block = sections.get("skills")
            if not isinstance(skills_block, dict) or not (skills_block.get("content") or "").strip():
                skills_block = sections.get("technical_skills") or skills_block
        raw_skills_content = (
            skills_block.get("content", "")
            if isinstance(skills_block, dict)
            else ""
        )
        
        # Step 1: Industry-level section isolation via regex (Skills / Technical Skills / Key Skills / etc.)
        def _refine_skills_section(text: str) -> str:
            if not text:
                return ""
            # Focus on Skills/Competencies markers and stop at the next obvious header (TitleCase followed by colon)
            pattern = r"(?:(?:Core\s+)?Competencies|Technical\s+Skills?|Technical\s+Expertise|Relevant\s+Skills?|Key\s+Skills?|Additional\s+Skills?|Professional\s+Skills?|Skills(?:\s+&\s+Expertise)?|Competencies).*?(?=\n[A-Z][A-Za-z ]+:|\Z)"
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            return match.group(0) if match else text

        skills_section = _refine_skills_section(raw_skills_content)
        skills_section = clean_text_for_skills(skills_section)
        
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

        # FIX 4 — Apply PDF split word normalization BEFORE FlashText so 'My SQL'→'mysql',
        #          'Py Spark'→'pyspark', 'Git Hub'→'github', 'XG Boost'→'xgboost', etc.
        # STEP 2 — Pre-normalize broken tokens first (My SQL→MySQL, S 3→S3, etc.)
        if raw_skills_content:
            raw_skills_content = normalize_text_for_skills_pre(raw_skills_content)
            raw_skills_content = normalize_pdf_split_words(raw_skills_content)
        if skills_section:
            skills_section = normalize_text_for_skills_pre(skills_section)
            skills_section = normalize_pdf_split_words(skills_section)

        extractor = SkillExtractor()
        fallback_guard = bool(
            skills_section_conf is not None and skills_section_conf < 0.6
        )
        # Include work history in skill extraction to capture technologies from job descriptions
        # (e.g. Helidon, Quarkus, Prometheus from Environment lines). section_only=False when we have jobs.
        skills_section_stripped = (skills_section or "").strip()
        has_substantial_section = len(skills_section_stripped) >= 40 and len(skills_section_stripped.split()) >= 2
        section_only = has_substantial_section and not jobs
        matches = extractor.extract_all(
            skills_section,
            jobs,
            skills_section_confidence=skills_section_conf,
            raw_text=job.raw_text or None,
            section_only=section_only,
        )
        payload = [match.__dict__ for match in matches]

        # Pre-compute taxonomy lookups (needed by both section-wise extraction and the 4-layer filter below)
        known_normalized = extractor.get_known_normalized_skills()
        canonical_names = extractor.get_canonical_normalized_names()

        # --- SECTION-WISE EXTRACTION: Always parse skills section via comma-split to capture all skills,
        #     including those not in the master taxonomy (skills_seed.json). This ensures every skill
        #     explicitly listed in the resume's Skills section is rendered, regardless of taxonomy coverage.
        section_sourced_normalized: set[str] = set()
        if raw_skills_content and raw_skills_content.strip():
            _sec_cleaned = clean_skill_text_for_section(raw_skills_content)
            _sec_tokens = tokenize_skills_by_comma(_sec_cleaned)
            _existing_norm_keys = {normalize_skill_name_for_dedup(m.get("normalized_name") or m.get("name") or "") for m in payload}
            for _tok in _sec_tokens:
                _tok = strip_skill_token(_tok)
                if not _tok or len(_tok) < 2:
                    continue
                _tok_norm = normalize_skill_name_for_dedup(_tok)
                if not _tok_norm or _tok_norm in _existing_norm_keys:
                    continue
                # Skip obvious sentence fragments and noise
                if is_sentence_fragment(_tok):
                    continue
                if is_generic_skill(_tok_norm):
                    continue
                # Word count guard: valid skills are at most 4 words (same as is_atomic_skill MAX_WORDS_ATOMIC)
                _tok_words = _tok.split()
                if len(_tok_words) > 4:
                    continue
                # STRICT CASING GUARD: reject all-lowercase multi-word tokens.
                # These are almost always descriptive phrases ('clear', 'scaling', 'engineering squads'),
                # NOT actual skill names. Real skills start with uppercase (Java, Spring Boot, RESTful APIs,
                # OOPs, HTML, CSS) or are known acronyms (CSS, HTML, SQL, API).
                _first_word = _tok_words[0]
                _is_uppercase_start = bool(_first_word) and _first_word[0].isupper()
                _is_pure_acronym = bool(re.match(r'^[A-Z]{2,6}$', _tok.strip()))
                _is_mixed_case = len(_tok) >= 3 and any(c.isupper() for c in _tok[1:]) and bool(re.match(r'^[A-Za-z0-9#+./-]+$', _tok))
                if not (_is_uppercase_start or _is_pure_acronym or _is_mixed_case):
                    # Single lowercase word: only accept if is_atomic_skill confirms it's a known tech token
                    if not is_atomic_skill(_tok, known_normalized):
                        continue
                # FIX 5 — HARD SKILL BLACKLIST: reject SQL syntax keywords, generic nouns, noise
                if _tok_norm in HARD_SKILL_BLACKLIST or _tok.lower() in HARD_SKILL_BLACKLIST:
                    continue
                # FIX 5b — SQL SUBFUNCTION GROUPING: RANK/LAG/LEAD → SQL; DML keywords → drop
                _sql_parent = SQL_SUBFUNCTION_MAP.get(_tok_norm) or SQL_SUBFUNCTION_MAP.get(_tok.lower())
                if _sql_parent is not None:  # None = drop; non-None string = use parent
                    _tok_norm = normalize_skill_name_for_dedup(_sql_parent)
                    _tok = _sql_parent
                elif _tok.lower() in SQL_SUBFUNCTION_MAP and SQL_SUBFUNCTION_MAP[_tok.lower()] is None:
                    continue  # DML keyword: drop entirely
                section_sourced_normalized.add(_tok_norm)
                _existing_norm_keys.add(_tok_norm)
                payload.append({
                    "name": _tok,
                    "normalized_name": _tok_norm,
                    "category": "Technical Skills",
                    "confidence": 0.85,
                    "years_experience": None,
                    "proficiency": None,
                    "source": "technical_skills_section",
                    "version": None,
                })

        # STEP 4 — LLM fallback: validate skills not in DB; if LLM returns them, mark source='llm'
        _section_not_in_db = [
            normalize_skill_name_for_dedup(str(p.get("normalized_name") or p.get("name") or ""))
            for p in payload
            if isinstance(p, dict)
            and p.get("source") == "technical_skills_section"
            and normalize_skill_name_for_dedup(str(p.get("normalized_name") or p.get("name") or "")) not in canonical_names
        ]
        if _section_not_in_db and job.raw_text:
            try:
                llm = LLMParsingService()
                llm_skills_raw = llm.extract_technical_skills_only(job.raw_text)
                llm_skills_set = {normalize_skill_name_for_dedup(s) for s in llm_skills_raw if s}
                for _item in payload:
                    if not isinstance(_item, dict) or _item.get("source") != "technical_skills_section":
                        continue
                    _norm = normalize_skill_name_for_dedup(str(_item.get("normalized_name") or _item.get("name") or ""))
                    if _norm in canonical_names:
                        continue
                    if _norm in llm_skills_set:
                        _item["source"] = "llm"
            except Exception:  # noqa: BLE001
                pass

        # --- 4-Layer quality filter: canonical norm, sentence fragment drop, atomic validation, category sanitization ---
        filtered_payload: list[dict[str, Any]] = []
        for item in payload if isinstance(payload, list) else []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            normalized = str(item.get("normalized_name") or "").strip()
            if not name and not normalized:
                continue
            # STEP 5 — Strict: reject confidence < 0.80
            conf = float(item.get("confidence") or 0)
            if conf < 0.80:
                continue
            # STEP 5 — Reject if > 4 words
            skill_label = name or normalized
            if len(skill_label.split()) > 4:
                continue
            # STEP 5 — Reject all-lowercase multi-word (sentence fragment / garbage)
            if len(skill_label.split()) >= 2 and not any(c.isupper() for c in skill_label):
                continue
            # STEP 3: Canonical normalization (e.g. Amazon Redshift, AWS Redshift -> redshift)
            canonical_norm = normalize_to_canonical(normalized or name)
            item = {**item, "normalized_name": canonical_norm}
            if not name:
                item["name"] = canonical_norm.title()
            skill_label = name or canonical_norm
            # STEP 2: Sentence fragment cleaner
            if is_sentence_fragment(skill_label):
                continue
            # STEP 1: Allow all taxonomy skills; also allow pre-validated section-sourced skills.
            #         Section tokens were strictly validated (casing guard + fragment check) before being added.
            is_from_section = normalize_skill_name_for_dedup(normalized or name) in section_sourced_normalized
            if canonical_norm not in canonical_names and not is_atomic_skill(skill_label, known_normalized) and not is_from_section:
                continue
            # STEP 4: Category validation (reject corrupted comma-separated or tech-list categories)
            sane_cat = sanitize_category(item.get("category"))
            # FIX 7 — Rule-based category fallback: never collapse everything to 'Project Tools'.
            # Apply explicit category rules before falling back to map_category_to_master.
            _fallback_cat = None
            if not sane_cat or sane_cat == "Technical Skills":
                _cn = canonical_norm
                if _cn in {"git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
                           "jenkins", "github actions", "gitlab ci", "ci/cd", "docker",
                           "kubernetes", "terraform", "ansible", "bash", "powershell", "linux"}:
                    _fallback_cat = "DevOps & Containers"
                elif _cn in {"jest", "pytest", "selenium", "cypress", "junit", "testing",
                             "unit testing", "integration testing", "e2e testing"}:
                    _fallback_cat = "Testing"
                elif _cn in {"agile", "scrum", "kanban", "sdlc", "devops", "microservices",
                             "mvc", "oop", "restful", "rest api", "graphql"}:
                    _fallback_cat = "Methodologies"
                elif _cn in {"html", "css", "sass", "scss", "jsx", "tailwind",
                             "tailwind css", "bootstrap", "material ui", "framer motion"}:
                    _fallback_cat = "Web Technologies"
                elif _cn in {"pyspark", "spark", "hadoop", "hive", "kafka", "airflow",
                             "hbase", "zookeeper", "mapreduce", "nifi", "flink", "beam",
                             "dagster", "prefect", "control-m", "oozie", "sqoop", "flume"}:
                    _fallback_cat = "Big Data Technologies"
                elif _cn in {"numpy", "pandas", "scipy", "sklearn", "scikit-learn", "statsmodels",
                             "matplotlib", "seaborn", "plotly", "jupyter", "pytorch", "tensorflow"}:
                    _fallback_cat = "Data & ML"
                elif _cn in {"postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle",
                             "sql server", "cassandra", "dynamodb", "cosmosdb", "hbase",
                             "nosql", "aurora", "bigtable", "db2", "vertica", "greenplum",
                             "teradata", "mariadb", "cockroachdb"}:
                    _fallback_cat = "Databases"
                elif _cn in {"aws", "azure", "gcp", "heroku", "digitalocean",
                             "ec2", "s3", "lambda", "emr", "sagemaker", "redshift",
                             "glue", "snowflake", "bigquery", "databricks", "athena",
                             "dataflow", "pubsub", "cloud storage", "msk"}:
                    _fallback_cat = "Cloud Platforms"
                elif _cn in {"communication", "leadership", "teamwork", "mentoring",
                             "collaboration", "problem solving", "troubleshooting",
                             "adaptability", "critical thinking", "time management"}:
                    _fallback_cat = "Soft Skills"
                elif _cn in {"sql", "advanced sql", "window functions", "t-sql", "plsql",
                             "spark sql", "hive sql"}:
                    _fallback_cat = "Databases"
            item["category"] = sane_cat or _fallback_cat or map_category_to_master(item.get("category")) or "Technical Skills"
            # Never store generic/umbrella terms (Cloud, Backend, Security, Frontend)
            if is_generic_skill(canonical_norm):
                continue
            filtered_payload.append(item)

        payload = filtered_payload

        # STEP 6 — Deduplicate by normalized (lower + strip); preserve order.
        # FIX 6 — POST-FILTER DEDUPLICATION by normalized_name.
        # Keep the entry with highest confidence. This removes duplicates where
        # FlashText matched 'glue' and section extraction added 'AWS Glue' with same canonical.
        _seen_canonical: dict[str, dict] = {}
        for _item in payload:
            _key = str(_item.get("normalized_name") or _item.get("name") or "").strip().lower()
            if not _key:
                continue
            if _key not in _seen_canonical:
                _seen_canonical[_key] = _item
            else:
                # Keep the one with higher confidence; prefer taxonomy (non-section) source
                _existing = _seen_canonical[_key]
                _conf_new = float(_item.get("confidence") or 0)
                _conf_old = float(_existing.get("confidence") or 0)
                if _conf_new > _conf_old:
                    _seen_canonical[_key] = _item
        payload = list(_seen_canonical.values())

        logger.info(
            "Skills after 4-layer filter: %d (input %d), canonical_names=%d, known_normalized=%d",
            len(filtered_payload),
            len([match.__dict__ for match in matches]),
            len(canonical_names),
            len(known_normalized),
        )

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
            key = normalize_skill_name_for_dedup(item.get("normalized_name") or item.get("name") or "")
            if not key:
                continue
            existing = merged.get(key)
            if not existing:
                merged[key] = dict(item)
                continue
            try:
                existing_conf = float(existing.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                existing_conf = 0.0
            try:
                incoming_conf = float(item.get("confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                incoming_conf = 0.0
            # Merge version lists when deduping (keep higher confidence, merge versions)
            ev = existing.get("version") or []
            iv = item.get("version") or []
            if not isinstance(ev, list):
                ev = []
            if not isinstance(iv, list):
                iv = []
            combined = list(ev)
            for v in iv:
                if v not in combined:
                    combined.append(v)
            version_merged = combined if combined else None
            if incoming_conf > existing_conf:
                merged[key] = {**dict(item), "version": version_merged}
            else:
                merged[key] = {**existing, "version": version_merged}

        payload = list(merged.values())
        before_resume_filter = len(payload)
        payload = filter_skills_by_resume_text(payload, job.raw_text or "", canonical_names)
        logger.info(
            "Skills after dedup: %d, after filter_by_resume_text: %d",
            before_resume_filter,
            len(payload),
        )
        # Industry standard: default confidence 0.75, master category only, ensure source, never guessed years
        default_confidence = 0.75
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                c = float(item.get("confidence") or 0)
                if c < default_confidence:
                    item["confidence"] = default_confidence
            except (TypeError, ValueError):
                item["confidence"] = default_confidence
            raw_cat = item.get("category")
            if raw_cat is not None:
                mapped = map_category_to_master(raw_cat)
                if mapped:
                    item["category"] = mapped
            if item.get("source") is None or item.get("source") == "":
                item["source"] = "technical_skills_section"
            # Do not guess years of experience; only explicit mention should set it
            item["years_experience"] = None
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

        cert_source: str | None = None

        if boundary_result.section_found and boundary_result.extracted_lines:
            cert_text = boundary_result.content
            cert_section_conf = boundary_result.confidence
            cert_source = "boundary"

        # ====================================================
        # 2️⃣ FALLBACK TO SECTION PARSER (SECONDARY)
        #    Check multiple section keys — some resumes use "licenses", "credentials", etc.
        # ====================================================
        if not cert_text and isinstance(sections, dict):
            for sec_key in (
                "certifications",
                "certification",
                "licenses",
                "credentials",
                "professional_credentials",
                "professional_certifications",
                "licenses_and_certifications",
            ):
                cert_section = sections.get(sec_key)
                if isinstance(cert_section, dict):
                    try:
                        cert_section_conf = float(cert_section.get("confidence", 0.0) or 0.0)
                    except (TypeError, ValueError):
                        cert_section_conf = None
                    content = str(cert_section.get("content") or "").strip()
                    if content and len(content) < 3000:
                        cert_text = content
                        cert_source = "section_parser"
                        break

        # ====================================================
        # 3️⃣ SAFE RAW TEXT FALLBACK (CONTROLLED)
        #    NEVER PASS FULL RESUME DIRECTLY
        # ====================================================
        if not cert_text:
            raw_text = job.raw_text or ""

            strong_cert_pattern = re.compile(
                r"\b(certified|certification|certificate|license|licence|associate|professional|specialty|expert|AZ-\d{2,}|SAA-\w+)\b",
                re.IGNORECASE,
            )

            if strong_cert_pattern.search(raw_text):
                # Use boundary extractor again (NOT raw text directly)
                boundary_retry = extract_certifications(raw_text)

                if boundary_retry.section_found and boundary_retry.extracted_lines:
                    cert_text = boundary_retry.content
                    cert_section_conf = boundary_retry.confidence
                    cert_source = "boundary_retry"

        # ====================================================
        # 4️⃣ STILL NOTHING? → SAVE EMPTY SAFELY
        # ====================================================
        if not cert_text:
            debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
            debug_bundle = dict(debug_bundle)
            debug_bundle["certifications"] = {
                "method": "none",
                "source": cert_source,
                "section_confidence": cert_section_conf,
                "cert_text_chars": 0,
                "initial_quality_score": None,
                "final_quality_score": None,
                "candidate_lines_quality_score": None,
                "llm_quality_score": None,
                "improved_from_candidate_lines": False,
                "improved_from_llm": False,
                "reason": "no_safe_section",
            }
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
                        "debug": debug_bundle,
                    },
                ),
            )
            return job_id

        # ====================================================
        # 5️⃣ PARSE USING YOUR HYBRID CERTIFICATION PARSER
        # ====================================================
        parser = CertificationParser()
        print(f"🔍 CERT PARSER INPUT: '{cert_text}'")
        entries = parser.parse(cert_text)
        print(f"🔍 CERT PARSER OUTPUT: {len(entries)} entries")
        for i, entry in enumerate(entries):
            print(f"🔍 CERT PARSER ENTRY {i}: {entry}")

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

        best_validated = validated
        best_score = score_certifications(validated)

        initial_quality_score = best_score
        candidate_lines_quality_score: float | None = None
        llm_quality_score: float | None = None
        improved_from_candidate_lines = False
        improved_from_llm = False

        # MERGE primary + candidate_lines (don't choose by score — avoid losing certs)
        raw_text = (job.raw_text or "").strip()
        if raw_text:
            candidate_lines = CertificationParser.extract_candidate_lines_from_full_text(
                raw_text
            )
            if candidate_lines:
                fallback_text = "\n".join(candidate_lines).strip()
                fallback_entries = parser.parse(fallback_text)
                fallback_payload = [
                    {
                        **entry.__dict__,
                        "issue_date": entry.issue_date.isoformat() if entry.issue_date else None,
                        "expiry_date": entry.expiry_date.isoformat() if entry.expiry_date else None,
                    }
                    for entry in fallback_entries
                ]
                fallback_payload = [
                    item
                    for item in fallback_payload
                    if isinstance(item, dict)
                    and str(item.get("name") or "").strip()
                    and len(str(item.get("name"))) <= 200
                ]
                # Merge primary + candidate_lines, then validate and dedupe
                merged_payload = payload + fallback_payload
                merged_validated = validator.normalize_providers(merged_payload)
                merged_validated = validator.remove_false_positives(merged_validated)
                merged_validated = validator.deduplicate_certifications(merged_validated)
                merged_score = score_certifications(merged_validated)
                candidate_lines_quality_score = merged_score
                if len(merged_validated) >= len(best_validated) or merged_score >= best_score:
                    best_validated = merged_validated
                    best_score = merged_score
                    improved_from_candidate_lines = len(merged_validated) > len(validated)

        # LLM fallback only when quality still low
        settings = get_settings()
        if (
            best_score < 1.0
            and settings.LLM_PROVIDER != "none"
            and settings.PARSING_MODE.lower() != "deterministic"
        ):
            llm = LLMParsingService()
            llm_payload = llm.extract_certifications(cert_text)
            if isinstance(llm_payload, list):
                llm_payload = [
                    item
                    for item in llm_payload
                    if isinstance(item, dict)
                    and str(item.get("name") or "").strip()
                    and len(str(item.get("name"))) <= 200
                ]
                # Merge LLM results with best_validated instead of replacing
                merged_with_llm = best_validated + llm_payload
                llm_validated = validator.normalize_providers(merged_with_llm)
                llm_validated = validator.remove_false_positives(llm_validated)
                llm_validated = validator.deduplicate_certifications(llm_validated)
                llm_score = score_certifications(llm_validated)
                llm_quality_score = llm_score
                if len(llm_validated) >= len(best_validated) or llm_score > best_score:
                    best_validated = llm_validated
                    best_score = llm_score
                    improved_from_llm = len(llm_validated) > len(best_validated)

        validated = best_validated

        validation_info = validator.detect_mismatches(
            section_confidence=cert_section_conf,
            extracted_items=validated,
        )

        debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        debug_bundle = dict(debug_bundle)
        debug_bundle["certifications"] = {
            "method": "parser",
            "source": cert_source,
            "section_confidence": cert_section_conf,
            "cert_text_chars": len(cert_text or ""),
            "initial_quality_score": initial_quality_score,
            "final_quality_score": best_score,
            "candidate_lines_quality_score": candidate_lines_quality_score,
            "llm_quality_score": llm_quality_score,
            "improved_from_candidate_lines": improved_from_candidate_lines,
            "improved_from_llm": improved_from_llm,
            "reason": None,
        }

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
                    "debug": debug_bundle,
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

        per_field, weakest_fields = build_per_field_confidence(parsed)
        breakdown: dict[str, Any] = {
            "weights": weights,
            "signals": fields,
            "fields": per_field,
            "weakest_fields": weakest_fields,
            "overall": score,
        }

        record_quality_metrics(filename=getattr(job, "filename", None), parsed=parsed, overall_score=score)

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
            select(ParsingJob).where(ParsingJob.id == _to_uuid(job_id))
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
        parsed = sanitize_final_output(parsed)

        # If contact name is still empty, try "Name: ..." or "Page X - Name" from raw text so we don't show "Unnamed candidate"
        raw_text = getattr(job, "raw_text", None) or ""
        existing_name = (parsed.get("contact") or {}).get("name") or {}
        if isinstance(existing_name, dict) and not (existing_name.get("name") or "").strip() and raw_text:
            name_label_re = re.compile(r"\bname\b\s*[:\-]\s*(?P<value>.+)$", re.IGNORECASE)
            page_name_re = re.compile(r"^page\s+\d+\s*[-–—]\s*(?P<value>[A-Za-z\s.'\-]{4,60})$", re.IGNORECASE)
            for line in (raw_text or "").splitlines()[:25]:
                stripped = line.strip()
                m = name_label_re.search(stripped)
                if m:
                    val = m.group("value").strip()
                    if val and 2 <= len(val.split()) <= 6 and "@" not in val and not re.search(r"\d", val) and re.match(r"^[A-Za-z\s.'\-]+$", val):
                        parsed.setdefault("contact", {})
                        parsed["contact"]["name"] = {"name": val, "confidence": 0.6}
                        break
                pm = page_name_re.match(stripped)
                if pm:
                    val = pm.group("value").strip()
                    if val and 2 <= len(val.split()) <= 5 and "@" not in val and not re.search(r"\d", val):
                        parsed.setdefault("contact", {})
                        parsed["contact"]["name"] = {"name": val, "confidence": 0.55}
                        break

        def _looks_like_skillish_header(value: str | None) -> bool:
            cleaned = str(value or "").strip()
            if not cleaned:
                return False
            lowered = cleaned.lower()
            if re.fullmatch(
                r"(?:django|flask|fastapi|spring|react|node|docker|kubernetes|terraform|jenkins|gitlab|github|aws|azure|gcp|sql|python|java|postgres|postgresql|mysql|redis|kafka|elasticsearch|splunk|datadog|prometheus|grafana)",
                lowered,
            ) and len(cleaned) <= 24:
                return True
            if "·" in cleaned and len(cleaned) <= 120:
                return True
            if cleaned.count(",") >= 2 and len(cleaned) <= 140:
                return True
            if re.search(
                r"\b(django|flask|fastapi|spring|react|node|docker|kubernetes|terraform|jenkins|gitlab|github|aws|azure|gcp|sql|python|java|postgres|postgresql|mysql|redis|kafka|elasticsearch|splunk|datadog|prometheus|grafana)\b",
                lowered,
            ):
                parts = [p.strip() for p in re.split(r"[,/|·]", lowered) if p.strip()]
                if len(parts) >= 3 and len(cleaned) <= 140:
                    return True
            return False

        def _looks_like_placeholder_org(value: str | None) -> bool:
            cleaned = str(value or "").strip().lower()
            if not cleaned:
                return False
            return bool(
                re.match(
                    r"^(company|client|organization|organisation|employer|designation|title|role|position|job\s*title|n/a|na\b|tbd|tbc|unknown|none|null)\b",
                    cleaned,
                )
            )

        def _work_experience_is_low_quality(value: Any) -> bool:
            if not isinstance(value, list) or not value:
                return True
            good = 0
            for item in value:
                if not isinstance(item, dict):
                    continue
                company = str(item.get("company") or "").strip()
                title = str(item.get("title") or "").strip()
                if not company and not title:
                    continue
                if _looks_like_placeholder_org(company) or _looks_like_placeholder_org(title):
                    continue
                if _looks_like_skillish_header(company) or _looks_like_skillish_header(title):
                    continue
                if len(company) > 180 or len(title) > 180:
                    continue
                good += 1
            return good == 0

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
                            if subkey not in merged_contact or merged_contact.get(subkey) in (
                                None,
                                "",
                                [],
                                {},
                            ):
                                # Never overwrite non-empty name with empty LLM name
                                if subkey == "name" and isinstance(incoming, dict):
                                    incoming_name = str(incoming.get("name") or "").strip()
                                    existing_name = ""
                                    if isinstance(merged_contact.get("name"), dict):
                                        existing_name = str(merged_contact["name"].get("name") or "").strip()
                                    if not incoming_name and existing_name:
                                        continue
                                merged_contact[subkey] = incoming
                        parsed[key] = merged_contact
                    continue
                if isinstance(value, list):
                    if key == "work_experience":
                        existing = parsed.get("work_experience")
                        incoming = value  # from LLM
                        existing_ok = existing and not _work_experience_is_low_quality(existing)
                        incoming_ok = incoming and not _work_experience_is_low_quality(incoming)

                        if existing_ok and not incoming_ok:
                            continue  # Keep deterministic, reject empty/bad LLM data
                        if existing_ok and incoming_ok:
                            continue  # Keep deterministic (it ran first, trust it)
                        if not existing_ok and incoming_ok:
                            parsed[key] = incoming  # Only use LLM if deterministic failed
                        continue
                    # education, skills: don't overwrite non-empty deterministic with empty LLM
                    if key in ("education", "skills"):
                        existing_ok = existing and len(existing) > 0
                        incoming_ok = value and len(value) > 0
                        if existing_ok and not incoming_ok:
                            continue
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

        contact = parsed.get("contact", {}) or {}
        name_obj = contact.get("name")
        if isinstance(name_obj, dict):
            name = (name_obj.get("name") or "").strip() or None
        elif isinstance(name_obj, str) and name_obj.strip():
            name = name_obj.strip()
        else:
            name = None
        emails = contact.get("emails", [])
        phones = contact.get("phones", [])
        location = contact.get("location", {}).get("city") or contact.get("location", {}).get(
            "country"
        )
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

            def _looks_like_tool_list(value: str) -> bool:
                cleaned = str(value or "").strip()
                lowered = cleaned.lower()
                job_hint_re = re.compile(
                    r"\b(engineer|developer|devops|sre|architect|administrator|admin|manager|lead|analyst|consultant|director|specialist|qa|tester|product|data|scientist|intern)\b",
                    re.IGNORECASE,
                )

                tokens = [t.strip() for t in re.split(r"[,/|·]", lowered) if t.strip()]
                if len(tokens) < 2:
                    return False

                if not job_hint_re.search(cleaned):
                    short_tokens = sum(1 for t in tokens if 1 <= len(t) <= 18)
                    if short_tokens / max(1, len(tokens)) >= 0.75:
                        return True

                hits = 0
                for tok in tokens:
                    if tok in {
                        "sonarqube",
                        "checkmarx",
                        "jenkins",
                        "git",
                        "github",
                        "gitlab",
                        "docker",
                        "kubernetes",
                        "terraform",
                        "ansible",
                        "aws",
                        "azure",
                        "gcp",
                        "sql",
                        "django",
                        "flask",
                        "fastapi",
                        "spring",
                        "react",
                        "node",
                        "postgres",
                        "postgresql",
                        "mysql",
                        "redis",
                        "kafka",
                    }:
                        hits += 1
                return hits >= 2

            def _is_plausible_person_name(value: str | None) -> bool:
                if not value:
                    return False
                cleaned = str(value).strip()
                if cleaned.lstrip().startswith(("-", "•", "*", "|")):
                    return False
                if _looks_like_tool_list(cleaned):
                    return False
                if len(cleaned) < 3 or len(cleaned) > 150:
                    return False
                if "@" in cleaned or "http" in cleaned.lower() or "www." in cleaned.lower():
                    return False
                if re.search(r"\d", cleaned):
                    return False
                if "," in cleaned or "/" in cleaned or "|" in cleaned:
                    return False
                if re.search(
                    r"\b(engineer|developer|devops|sre|architect|administrator|admin|manager|lead|analyst|consultant|director|specialist|qa|tester|product|data|scientist|intern)\b",
                    cleaned,
                    re.IGNORECASE,
                ):
                    return False
                verb_check = re.sub(r"^[^A-Za-z0-9]+", "", cleaned.lower())
                if re.match(
                    r"^(implemented|designed|developed|managed|led|built|created|migrated|deployed|optimized|configured|maintained|delivered)\b",
                    verb_check,
                ):
                    return False
                parts = [p for p in cleaned.split() if p]
                if len(parts) == 1 and parts[0][0].isupper() and len(parts[0]) >= 3:
                    return True
                if any(cleaned.startswith(p) for p in ["Dr.", "Mr.", "Ms.", "Prof."]):
                    return True
                if not (2 <= len(parts) <= 6):
                    return False
                lowered = cleaned.lower()
                if re.search(r"\b(and|with|for|to|in|across|optimizing|automating)\b", lowered) and len(parts) >= 5:
                    return False
                if len(parts) == 1 and len(parts[0]) <= 2:
                    return False
                return True

            def _is_plausible_headline(value: str | None) -> bool:
                if not value:
                    return False
                cleaned = str(value).strip()
                if len(cleaned) < 2 or len(cleaned) > 200:
                    return False
                if "@" in cleaned or "http" in cleaned.lower() or "www." in cleaned.lower():
                    return False
                if cleaned.lstrip().startswith(("-", "•", "*", "|")):
                    return False
                verb_check = re.sub(r"^[^A-Za-z0-9]+", "", cleaned.lower())
                if re.match(
                    r"^(implemented|designed|developed|managed|led|built|created|migrated|deployed|optimized|configured|maintained|delivered)\b",
                    verb_check,
                ):
                    return False
                if _looks_like_tool_list(cleaned):
                    return False
                return True

            def _guess_name_from_raw_text(raw_text: str | None) -> str | None:
                if not raw_text or not str(raw_text).strip():
                    return None
                lines = [ln.strip() for ln in str(raw_text).splitlines() if ln.strip()]
                if not lines:
                    return None
                # Explicit "Name: ..." or "Name" on one line and value on next (common in resumes)
                name_label_re = re.compile(r"\bname\b\s*[:\-]\s*(?P<value>.+)$", re.IGNORECASE)
                for i, line in enumerate(lines[:20]):
                    m = name_label_re.search(line)
                    if m:
                        val = m.group("value").strip()
                        if not val:
                            continue
                        if _is_plausible_person_name(val):
                            return val
                        # Use anyway if it looks like a name: 2-6 words, letters/spaces only (e.g. "Nitish Rao B")
                        parts = [p for p in val.split() if p]
                        if 2 <= len(parts) <= 6 and re.match(r"^[A-Za-z\s.'\-]+$", val) and "@" not in val and not re.search(r"\d", val):
                            return val
                    if line.lower().strip(":- ") == "name" and i + 1 < len(lines):
                        val = lines[i + 1].strip()
                        if val and _is_plausible_person_name(val):
                            return val
                        parts = [p for p in (val or "").split() if p]
                        if val and 2 <= len(parts) <= 6 and re.match(r"^[A-Za-z\s.'\-]+$", val) and "@" not in val and not re.search(r"\d", val):
                            return val
                headings = {
                    "summary",
                    "professional summary",
                    "executive summary",
                    "career summary",
                    "career overview",
                    "profile",
                    "professional profile",
                    "objective",
                    "experience",
                    "work experience",
                    "employment",
                    "skills",
                    "technical skills",
                    "projects",
                    "education",
                    "certifications",
                }
                for line in lines[:15]:
                    lowered = line.lower().strip(":- ")
                    if lowered in headings:
                        continue
                    if "@" in line or "http" in lowered or "www." in lowered:
                        continue
                    if line.lstrip().startswith(("-", "•", "*", "|")):
                        continue
                    if "," in line or "/" in line or "|" in line:
                        continue
                    if re.search(r"\d", line):
                        continue
                    if _looks_like_tool_list(line):
                        continue
                    if _looks_like_skillish_header(line):
                        continue
                    parts = [p for p in re.split(r"\s+", line) if p]
                    if not (2 <= len(parts) <= 4):
                        continue
                    alpha_ratio = sum(1 for ch in line if ch.isalpha()) / max(1, len(line))
                    if alpha_ratio < 0.6:
                        continue
                    return line
                return None

            def _guess_summary_from_raw_text(raw_text: str | None) -> str | None:
                if not raw_text or not str(raw_text).strip():
                    return None
                lines = [ln.strip() for ln in str(raw_text).splitlines()]
                headings = {
                    "summary",
                    "professional summary",
                    "executive summary",
                    "career summary",
                    "career overview",
                    "profile",
                    "professional profile",
                    "objective",
                    "experience",
                    "work experience",
                    "employment",
                    "skills",
                    "technical skills",
                    "projects",
                    "education",
                    "certifications",
                }

                collected: list[str] = []
                for line in lines[:60]:
                    if not line.strip():
                        if collected:
                            break
                        continue
                    lowered = line.lower().strip(":- ")
                    if lowered in headings:
                        if collected:
                            break
                        continue
                    if re.search(r"\b(19\d{2}|20\d{2})\b", line):
                        if collected:
                            break
                        continue
                    if _looks_like_skillish_header(line):
                        if collected:
                            break
                        continue
                    if line.lstrip().startswith(("-", "•", "*", "|")):
                        if collected:
                            break
                        continue
                    collected.append(line.strip())
                    if len(" ".join(collected).split()) >= 120:
                        break

                summary = " ".join(collected).strip()
                if len(summary.split()) < 10:
                    return None
                return summary
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
            existing_name = (candidate.full_name or "").strip() if candidate.full_name else ""
            incoming_name = name or _guess_name_from_raw_text(job.raw_text)
            if _is_plausible_person_name(incoming_name) and (
                not existing_name
                or not _is_plausible_person_name(existing_name)
                or _looks_like_tool_list(existing_name)
            ):
                candidate.full_name = str(incoming_name).strip()
            if emails:
                candidate.email = emails[0].get("email")
                if candidate.email:
                    candidate.email_hash = hash_value(candidate.email)
            if phones:
                candidate.phone = phones[0].get("phone")
            candidate.location = location or candidate.location
            candidate.linkedin_url = linkedin or candidate.linkedin_url
            candidate.github_url = github or candidate.github_url
            inferred_summary = summary_section or _guess_summary_from_raw_text(job.raw_text)
            if inferred_summary:
                inferred_summary = clean_summary(inferred_summary)
                candidate.summary = inferred_summary
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

        raw_we = parsed.get("work_experience", [])
        raw_certs = parsed.get("certifications", [])
        raw_edu = parsed.get("education", [])
        logger.info(
            "Saving to DB: work_experience=%d, certifications=%d, education=%d",
            len(raw_we) if isinstance(raw_we, list) else 0,
            len(raw_certs) if isinstance(raw_certs, list) else 0,
            len(raw_edu) if isinstance(raw_edu, list) else 0,
            extra={"job_id": job_id, "candidate_id": str(job.candidate_id) if job.candidate_id else None},
        )
        logger.info(
            "DIAG pre-sanitize count=%d entries=%s",
            len(raw_we) if isinstance(raw_we, list) else 0,
            str(
                [
                    {k: e.get(k) for k in ["company", "title", "start_date", "end_date"]}
                    for e in (raw_we[:3] if isinstance(raw_we, list) else [])
                ]
            ),
        )
        work_entries = sanitize_work_experience_entries(raw_we)
        logger.info(
            "DIAG post-sanitize count=%d dropped=%d",
            len(work_entries),
            (len(raw_we) if isinstance(raw_we, list) else 0) - len(work_entries),
        )
        raw_text_len = len(job.raw_text or "")
        summary_block = (parsed.get("sections") or {}).get("summary") or {}
        if isinstance(summary_block, dict):
            summary_len = len(str(summary_block.get("content") or ""))
        else:
            summary_len = 0
        we_desc_len = sum(
            len(str(e.get("description") or ""))
            for e in (work_entries if isinstance(work_entries, list) else [])
            if isinstance(e, dict)
        )
        logger.info(
            "[DATA-LOSS CHECK] Final extracted vs raw: job_id=%s, raw_text_chars=%d, work_entries=%d, work_desc_total_chars=%d, education=%d, certifications=%d, summary_chars=%d",
            job_id,
            raw_text_len,
            len(work_entries) if isinstance(work_entries, list) else 0,
            we_desc_len,
            len(raw_edu) if isinstance(raw_edu, list) else 0,
            len(raw_certs) if isinstance(raw_certs, list) else 0,
            summary_len,
            extra={
                "job_id": job_id,
                "raw_text_chars": raw_text_len,
                "work_entries": len(work_entries) if isinstance(work_entries, list) else 0,
                "work_desc_total_chars": we_desc_len,
                "education_count": len(raw_edu) if isinstance(raw_edu, list) else 0,
                "certifications_count": len(raw_certs) if isinstance(raw_certs, list) else 0,
                "summary_chars": summary_len,
            },
        )
        for entry in work_entries:
            company = entry.get("company") or entry.get("client")
            session.add(
                WorkHistory(
                    candidate_id=job.candidate_id,
                    company_name=company,
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
            chosen = None
            if isinstance(work_entries, list):
                for item in work_entries:
                    if not isinstance(item, dict):
                        continue
                    title_val = item.get("title")
                    company_val = item.get("company")
                    if title_val and company_val and _is_plausible_headline(title_val) and _is_plausible_headline(company_val):
                        chosen = item
                        break
            if not chosen and isinstance(first, dict):
                chosen = first
            if isinstance(chosen, dict):
                next_title = chosen.get("title")
                next_company = chosen.get("company")
                if (not candidate.current_title or not _is_plausible_headline(candidate.current_title)) and _is_plausible_headline(next_title):
                    candidate.current_title = next_title
                if (not candidate.current_company or not _is_plausible_headline(candidate.current_company)) and _is_plausible_headline(next_company):
                    candidate.current_company = next_company

        education_entries = sanitize_education_entries(
            _coerce_list(
                parsed.get("education_normalized")
                if (
                    len(_coerce_list(parsed.get("education_normalized", [])))
                    >= len(_coerce_list(parsed.get("education", [])))
                )
                else parsed.get("education", [])
            )
        )
        for entry in education_entries:
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

        certifications_entries = sanitize_certifications_entries(parsed.get("certifications", []))
        for entry in certifications_entries:
            cert_name = entry.get("name") if isinstance(entry, dict) else None
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
        skills_before_sanitize = parsed.get("skills", [])
        skill_entries = sanitize_skill_entries(skills_before_sanitize)
        logger.info(
            "Skills before sanitize: %d, after: %d",
            len(skills_before_sanitize) if isinstance(skills_before_sanitize, list) else 0,
            len(skill_entries),
        )
        for entry in skill_entries:
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
            if not normalized:
                normalized = normalize_skill_name_for_dedup(raw_name)

            skill: Skill | None = None
            if normalized:
                skill = session.execute(
                    select(Skill).where(Skill.normalized_name == normalized)
                ).scalars().first()
            if not skill:
                skill = session.execute(select(Skill).where(Skill.name == raw_name)).scalars().first()

            if not skill and normalized:
                skill = session.execute(
                    select(Skill).where(Skill.normalized_name == normalized)
                ).scalars().first()
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
                    ).scalars().first()
                if not skill and normalized:
                    skill = session.execute(
                        select(Skill).where(Skill.normalized_name == normalized)
                    ).scalars().first()

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
            if isinstance(review_flags, dict):
                for flag in review_flags.get("rule_flags") or []:
                    REVIEW_FLAG_TOTAL.labels(flag_name=str(flag)).inc()
                flagged_fields = review_flags.get("flagged_fields")
                if isinstance(flagged_fields, dict):
                    for field_name in flagged_fields.keys():
                        REVIEW_FLAG_TOTAL.labels(flag_name=str(field_name)).inc()
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

        fmt = _source_format_from_path(
            getattr(job, "file_path", None) or getattr(job, "extracted_text_path", None)
        ) or "unknown"
        pipeline_duration = (
            (job.completed_at - job.started_at).total_seconds()
            if job.started_at and job.completed_at
            else None
        )
        emit_parse_metrics(
            parsed=parsed,
            format=fmt,
            queue="persist",
            pipeline_duration_seconds=pipeline_duration,
        )
        return job_id
    except Exception as exc:
        session.rollback()
        try:
            fmt = _source_format_from_path(
                getattr(job, "file_path", None) or getattr(job, "extracted_text_path", None)
            ) or "unknown"
        except NameError:
            fmt = "unknown"
        PARSE_ERRORS.labels(stage="save_to_database", format=fmt).inc()
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
def generate_accuracy_report() -> dict[str, Any]:
    """Generate accuracy report by evaluating parser against ground truth fixtures."""
    from pathlib import Path

    from app.services.accuracy_report import generate_accuracy_report as run_report

    fixtures_dir = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "resumes"
    output_path = Path(__file__).resolve().parents[2] / "tests" / "reports" / "accuracy_report.json"

    report = run_report(fixtures_dir=fixtures_dir, output_path=output_path)

    summary = {
        "case_count": report.case_count,
        "overall": round(report.overall, 4),
        "contact_accuracy": round(report.contact_accuracy, 4),
        "work_accuracy": round(report.work_accuracy, 4),
        "skills_f1": round(report.skills_f1.f1, 4),
        "education_f1": round(report.education_f1.f1, 4),
        "certifications_f1": round(report.certifications_f1.f1, 4),
    }
    logger.info(
        "Accuracy report generated: %d cases, overall=%.3f, contact=%.3f, work=%.3f, skills=%.3f",
        report.case_count,
        report.overall,
        report.contact_accuracy,
        report.work_accuracy,
        report.skills_f1.f1,
    )
    return summary
