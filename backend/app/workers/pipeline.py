from __future__ import annotations

import json
import logging
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any

from celery import chain
from sqlalchemy import delete, select

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
from app.services.parser.certification_parser import CertificationParser
from app.services.parser.contact_extractor import ContactExtractor
from app.services.parser.education_parser import EducationParser
from app.services.parser.section_parser import SectionParser
from app.services.parser.skill_extractor import SkillExtractor
from app.services.parser.work_experience_parser import JobEntry, WorkExperienceParser
from app.services.llm_service import LLMParsingService
from app.utils.pii import hash_value
from app.utils.review import apply_correction_patterns, compute_review_flags, find_date_overlaps
from app.workers.celery_app import celery_app
from app.workers.extract_text_task import extract_text_task

logger = logging.getLogger(__name__)


def start_parsing_workflow(job_id: str) -> str:
    structlog.contextvars.bind_contextvars(job_id=job_id)
    try:
        import sentry_sdk

        sentry_sdk.set_tag("job_id", job_id)
    except Exception:
        pass
    increment_jobs_total()
    workflow = chain(
        task_extract_text.s(job_id),
        task_llm_resume_parse.s(),
        task_detect_sections.s(),
        task_extract_contact_info.s(),
        task_parse_work_experience.s(),
        task_parse_education.s(),
        task_extract_skills.s(),
        task_parse_certifications.s(),
        task_calculate_confidence.s(),
        task_save_to_database.s(),
    )
    settings = get_settings()

    def _run_local() -> str:
        current_job_id = job_id
        for task in (
            task_extract_text,
            task_llm_resume_parse,
            task_detect_sections,
            task_extract_contact_info,
            task_parse_work_experience,
            task_parse_education,
            task_extract_skills,
            task_parse_certifications,
            task_calculate_confidence,
            task_save_to_database,
        ):
            result = task.apply(args=[current_job_id])
            current_job_id = result.get() if result else current_job_id
        return f"local-{job_id}"

    result_id = None
    ran_locally = False
    force_local = settings.ENVIRONMENT.lower() in {"development", "local"}
    if force_local:
        ran_locally = True
        result_id = _run_local()
    else:
        try:
            result = workflow.apply_async()
            result_id = result.id
        except Exception as exc:
            logger.warning(
                "Celery unavailable; running workflow locally",
                extra={"job_id": job_id, "error": str(exc)},
            )
            ran_locally = True
            result_id = _run_local()

    session = SessionLocal()
    try:
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == job_id)
        ).scalar_one_or_none()
        if job:
            job.status = ParsingJobStatus.PROCESSING
            job.task_id = result_id
            job.last_stage = "local" if ran_locally else "queued"
            job.started_at = datetime.now(timezone.utc)
            session.commit()
    finally:
        session.close()

    return result_id


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
        return parsed

    merged = dict(parsed)
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
            cert_items.append(
                {
                    "name": entry.get("name") or entry.get("certification"),
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
        if "work_experience" in parsed:
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
        if "education" in parsed:
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
        if "skills" in parsed:
            return job_id

        sections = parsed.get("sections", {})
        skills_section = sections.get("skills", {}).get("content", "")

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
        matches = extractor.extract_all(skills_section, jobs)
        payload = [match.__dict__ for match in matches]
        _update_job(
            job_id,
            last_stage="extract_skills",
            parsed_data=_merge_parsed(job, {"skills": payload}),
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
    name="app.workers.pipeline.task_parse_certifications",
)
def task_parse_certifications(self, job_id: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    try:
        job = _load_job(job_id)
        parsed = job.parsed_data or {}
        if "certifications" in parsed:
            return job_id

        sections = parsed.get("sections", {})
        cert_text = sections.get("certifications", {}).get("content", job.raw_text or "")
        parser = CertificationParser()
        entries = parser.parse(cert_text)
        payload = [
            {
                **entry.__dict__,
                "issue_date": entry.issue_date.isoformat()
                if entry.issue_date
                else None,
                "expiry_date": entry.expiry_date.isoformat()
                if entry.expiry_date
                else None,
            }
            for entry in entries
        ]
        _update_job(
            job_id,
            last_stage="parse_certifications",
            parsed_data=_merge_parsed(job, {"certifications": payload}),
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
        confidence_values = []
        for section in parsed.get("sections", {}).values():
            confidence_values.append(section.get("confidence", 0.0))
        for entry in parsed.get("work_experience", []):
            confidence_values.append(entry.get("confidence", 0.0))
        for entry in parsed.get("education", []):
            confidence_values.append(entry.get("confidence", 0.0))
        for entry in parsed.get("certifications", []):
            confidence_values.append(entry.get("confidence", 0.0))
        if confidence_values:
            score = sum(confidence_values) / len(confidence_values)
        else:
            score = 0.0

        _update_job(
            job_id,
            last_stage="calculate_confidence",
            confidence_score=score,
            parsed_data=_merge_parsed(job, {"confidence": score}),
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

        parsed = _apply_llm_resume(job.parsed_data or {})
        contact = parsed.get("contact", {})
        name = contact.get("name", {}).get("name")
        emails = contact.get("emails", [])
        phones = contact.get("phones", [])
        location = contact.get("location", {}).get("city") or contact.get("location", {}).get("country")
        linkedin = contact.get("urls", {}).get("linkedin")
        github = contact.get("urls", {}).get("github")

        candidate = session.execute(
            select(Candidate).where(Candidate.id == job.candidate_id)
        ).scalar_one_or_none()
        if candidate:
            set_current_tenant(candidate.tenant_id)
            llm_resume = parsed.get("llm_resume") if isinstance(parsed, dict) else None
            if isinstance(llm_resume, dict):
                professional = llm_resume.get("professional_summary") or {}
                if not candidate.years_experience:
                    years = professional.get("years_of_experience")
                    try:
                        candidate.years_experience = float(years) if years is not None else None
                    except (TypeError, ValueError):
                        pass
                if not candidate.current_title:
                    candidate.current_title = professional.get("primary_role") or candidate.current_title
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
            candidate.status = CandidateStatus.SUCCESS

        session.execute(delete(WorkHistory).where(WorkHistory.candidate_id == job.candidate_id))
        session.execute(delete(Education).where(Education.candidate_id == job.candidate_id))
        session.execute(delete(Certification).where(Certification.candidate_id == job.candidate_id))
        session.execute(delete(CandidateSkill).where(CandidateSkill.candidate_id == job.candidate_id))

        for entry in parsed.get("work_experience", []):
            session.add(
                WorkHistory(
                    candidate_id=job.candidate_id,
                    company_name=entry.get("company"),
                    job_title=entry.get("title"),
                    start_date=_parse_date_str(entry.get("start_date")),
                    end_date=_parse_date_str(entry.get("end_date")),
                    is_current=entry.get("is_current", False),
                    location=entry.get("location"),
                    description=entry.get("description"),
                    display_order=None,
                )
            )

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
            session.add(
                Certification(
                    candidate_id=job.candidate_id,
                    name=entry.get("name"),
                    issuing_organization=entry.get("issuing_organization"),
                    issue_date=_parse_date_str(entry.get("issue_date")),
                    expiry_date=_parse_date_str(entry.get("expiry_date")),
                    credential_id=entry.get("credential_id"),
                )
            )

        for entry in parsed.get("skills", []):
            normalized = entry.get("normalized_name")
            skill = session.execute(
                select(Skill).where(Skill.normalized_name == normalized)
            ).scalar_one_or_none()
            if not skill:
                skill = Skill(
                    name=entry.get("name"),
                    category=entry.get("category"),
                    normalized_name=normalized,
                )
                session.add(skill)
                session.flush()
            session.add(
                CandidateSkill(
                    candidate_id=job.candidate_id,
                    skill_id=skill.id,
                    proficiency_level=_to_proficiency(entry.get("proficiency")),
                    years_experience=entry.get("years_experience"),
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
