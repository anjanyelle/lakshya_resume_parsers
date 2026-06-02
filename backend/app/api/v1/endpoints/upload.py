import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from starlette.background import BackgroundTask
from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.core.config import get_settings
from app.models import Base
from app.models.candidate import Candidate, CandidateStatus
from app.models.parsing_job import ParsingJob, ParsingJobStatus
from app.schemas.upload import BatchUploadResponse, UploadJobResponse
from app.services.storage import copy_s3_object, save_bytes_to_local, upload_bytes_to_s3
from app.services.storage import download_s3_to_file
from app.utils.file_validation import validate_magic
from app.utils.audit import log_audit
from app.utils.virus_scan import scan_file
from app.workers.pipeline import start_parsing_workflow
from fastapi.responses import HTMLResponse
from app.services.parser.extract_text import extract_text
from app.services.parser.section_parser import SectionParser
from app.services.parser.work_experience_parser import WorkExperienceParser
from app.services.parser.education_parser import EducationParser
from pydantic import BaseModel
from typing import Optional, Any
from fastapi import Form


router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


def _raw_text_to_html(text: str | None) -> str:
    """Turn raw resume text into minimal HTML for preview when debug.html_preview is missing."""
    if not text or not text.strip():
        return "<p>No text available for preview.</p>"
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        clean = (
            clean.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        out.append(f"<p>{clean}</p>")
    return "\n".join(out) if out else "<p>No text available for preview.</p>"


def _extract_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def _build_s3_key(file_id: str, extension: str) -> str:
    now = datetime.utcnow()
    return f"uploads/{now.year}/{now.month:02d}/{file_id}.{extension}"


async def _process_uploads(
    files: list[UploadFile],
    user_email: str,
    current_user,
    db: Session,
    background_tasks: BackgroundTasks,
) -> BatchUploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Max 10 files per upload")
    enforce_rate_limit(user_email)

    jobs: list[UploadJobResponse] = []
    max_bytes = settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024

    for upload in files:
        if not upload.filename:
            raise HTTPException(status_code=400, detail="File name is missing")

        extension = _extract_extension(upload.filename)
        if extension not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        data = await upload.read()
        if len(data) > max_bytes:
            raise HTTPException(status_code=413, detail="File too large")
        if not validate_magic(data, extension):
            raise HTTPException(status_code=400, detail="File content type mismatch")

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(data)
            temp_path = Path(temp_file.name)

        try:
            scan_file(temp_path)
        except RuntimeError as exc:
            logger.warning("Virus scan failed", extra={"file": upload.filename})
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            temp_path.unlink(missing_ok=True)

        file_id = str(uuid4())
        key = _build_s3_key(file_id, extension)

        try:
            if settings.S3_BUCKET:
                upload_bytes_to_s3(data, key)
                file_path = f"s3://{settings.S3_BUCKET}/{key}"
            else:
                file_path = save_bytes_to_local(data, key)
        except RuntimeError as exc:
            if settings.ENVIRONMENT.lower() == "development":
                logger.warning(
                    "S3 upload failed; falling back to local storage",
                    extra={"error": str(exc), "key": key},
                )
                file_path = save_bytes_to_local(data, key)
            else:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
        finally:
            await upload.close()

        def _create_candidate_and_job():
            candidate = Candidate(
                status=CandidateStatus.PENDING,
                tenant_id=current_user.tenant_id if current_user else "default",
            )
            db.add(candidate)
            db.flush()
            job = ParsingJob(
                candidate_id=candidate.id,
                filename=upload.filename,
                file_path=file_path,
                status=ParsingJobStatus.PENDING,
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            return candidate, job

        candidate, job = None, None
        for attempt in range(2):
            try:
                candidate, job = _create_candidate_and_job()
                break
            except ProgrammingError as e:
                db.rollback()
                err_msg = str(getattr(e, "orig", None) or e).lower()
                if "does not exist" in err_msg or "candidates" in err_msg or "parsing_jobs" in err_msg:
                    if attempt == 0:
                        try:
                            engine = db.get_bind()
                            Base.metadata.create_all(bind=engine, checkfirst=True)
                        except Exception as create_err:
                            logger.warning("Could not create missing tables: %s", create_err)
                        continue
                    raise HTTPException(
                        status_code=503,
                        detail="Database schema not ready. Please try again in a moment or contact support.",
                    ) from e
                raise
        if candidate is None or job is None:
            raise HTTPException(
                status_code=503,
                detail="Database schema not ready. Please try again in a moment or contact support.",
            )

        try:
            base_key = f"resumes/{candidate.tenant_id}/{candidate.id}/{job.id}"
            original_key = f"{base_key}/original.{extension}"
            if file_path.startswith("s3://") and settings.S3_BUCKET:
                copied = copy_s3_object(file_path, original_key)
                job.original_file_copy_path = copied.uri
            else:
                src = Path(file_path)
                dst = Path(settings.STORAGE_DIR) / original_key
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    shutil.copy2(src, dst)
                    job.original_file_copy_path = str(dst)
            db.add(job)
            db.commit()
            db.refresh(job)
        except Exception as exc:
            logger.warning(
                "Failed to persist canonical resume copy",
                extra={"job_id": str(job.id), "error": str(exc)},
            )

        if settings.ENVIRONMENT.lower() in {"development", "local"}:
            # Run inline in dev to avoid reloads/background task interruptions.
            background_tasks.add_task(start_parsing_workflow, str(job.id))
        else:
            background_tasks.add_task(start_parsing_workflow, str(job.id))
        try:
            log_audit(
                db,
                user_id=str(current_user.id) if current_user else None,
                action="upload_resume",
                resource_type="candidate",
                resource_id=str(candidate.id),
                ip_address=None,
            )
        except Exception as e:
            logger.warning("Audit log failed (upload still succeeded): %s", e)
        jobs.append(UploadJobResponse(job_id=str(job.id), status=job.status.value))

    return BatchUploadResponse(message="Upload successful", jobs=jobs)


@router.post("/upload", response_model=BatchUploadResponse)
async def upload_single(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BatchUploadResponse:
    return await _process_uploads(
        [file],
        current_user.email,
        current_user,
        db,
        background_tasks,
    )


@router.post("/upload/batch", response_model=BatchUploadResponse)
async def upload_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BatchUploadResponse:
    return await _process_uploads(
        files,
        current_user.email,
        current_user,
        db,
        background_tasks,
    )


@router.get("/files/{job_id}")
def download_file(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    job = (
        db.execute(
            select(ParsingJob)
            .join(Candidate, Candidate.id == ParsingJob.candidate_id)
            .where(
                ParsingJob.id == job_id,
                Candidate.tenant_id == current_user.tenant_id,
            )
        )
        .scalars()
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="File not found")
    if job.file_path.startswith("s3://"):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp_path = Path(temp.name)
        temp.close()
        try:
            download_s3_to_file(job.file_path, str(temp_path))
        except RuntimeError as exc:
            temp_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return FileResponse(
            temp_path,
            filename=job.filename,
            background=BackgroundTask(lambda: os.unlink(str(temp_path))),
        )
    local_path = Path(job.file_path)
    if not local_path.exists() and job.original_file_copy_path:
        copy_path = job.original_file_copy_path
        if not str(copy_path).startswith("s3://"):
            alt = Path(copy_path)
            if alt.exists():
                return FileResponse(alt, filename=job.filename)
    if not local_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(local_path, filename=job.filename)


@router.get("/files/{job_id}/html")
def get_file_html(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return HTML preview for resume with click-to-highlight support."""
    enforce_rate_limit(current_user.email, limit=30, per_seconds=60)
    
    # Debug logging
    logger.info(f"HTML preview requested for job_id: {job_id}")

    job = (
        db.execute(
            select(ParsingJob)
            .join(Candidate, Candidate.id == ParsingJob.candidate_id)
            .where(
                ParsingJob.id == job_id,
                Candidate.tenant_id == current_user.tenant_id,
            )
        )
        .scalars()
        .first()
    )

    if not job:
        logger.warning(f"Job not found for job_id: {job_id}")
        raise HTTPException(status_code=404, detail="File not found")

    # Get html_preview from parsed_data.debug.html_preview
    parsed_data = job.parsed_data or {}
    debug_data = parsed_data.get("debug", {})
    html_preview = debug_data.get("html_preview")
    
    logger.info(f"HTML preview found: {bool(html_preview)}, length: {len(html_preview) if html_preview else 0}")

    if not html_preview and (job.raw_text or "").strip():
        html_preview = _raw_text_to_html(job.raw_text)
        logger.info(f"Using raw_text fallback for HTML preview, length: {len(html_preview)}")
    if not html_preview:
        logger.warning(f"HTML preview not available for job_id: {job_id}")
        raise HTTPException(status_code=404, detail="HTML preview not available")

    logger.info(f"Returning HTML preview for job_id: {job_id}, length: {len(html_preview)}")
    return HTMLResponse(content=html_preview)


@router.get("/files/{job_id}/html-test")
def get_file_html_test(
    job_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Test endpoint to verify HTML content without authentication."""
    job = (
        db.execute(
            select(ParsingJob)
            .where(ParsingJob.id == job_id)
        )
        .scalars()
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="File not found")

    parsed_data = job.parsed_data or {}
    debug_data = parsed_data.get("debug", {})
    html_preview = debug_data.get("html_preview")

    if not html_preview:
        return PlainTextResponse("No HTML preview available")
    
    # Return first 500 chars for testing
    sample = html_preview[:500] if html_preview else "No HTML"
    return PlainTextResponse(f"HTML Preview Test - Length: {len(html_preview)}\n\n{sample}")


class SectionPreviewResponse(BaseModel):
    filename: str
    extraction_method: str
    raw_text_length: int
    raw_text: str
    total_sections: int
    sections: dict[str, dict[str, Any]]
    detected_sections: list[str]
    missing_sections: list[str]
    validation_metadata: dict[str, Any]

@router.post("/preview-sections", response_model=SectionPreviewResponse)
async def preview_sections_endpoint(file: UploadFile = File(...), force_ocr: bool = Form(False)):
    data = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
        temp_file.write(data)
        temp_path = Path(temp_file.name)
    
    try:
        extracted = extract_text(temp_path)
        text = extracted.text
        
        parser = SectionParser()
        parsed_sections = parser.parse(text)
        
        sections_dict = {}
        detected_sections = []
        for key, result in parsed_sections.items():
            if result.content:
                text_content = "\n".join(result.content)
                sections_dict[key] = {
                    "text": text_content,
                    "char_count": len(text_content)
                }
                detected_sections.append(key)
                
        standard_sections = ['summary', 'experience', 'education', 'skills', 'certifications', 'projects', 'contact']
        missing_sections = [s for s in standard_sections if s not in detected_sections]
        
        return SectionPreviewResponse(
            filename=file.filename,
            extraction_method="auto",
            raw_text_length=len(text),
            raw_text=text,
            total_sections=len(sections_dict),
            sections=sections_dict,
            detected_sections=detected_sections,
            missing_sections=missing_sections,
            validation_metadata={"spacy_available": False, "warnings": []}
        )
    finally:
        import os
        os.unlink(temp_path)

class ParseSectionsRequest(BaseModel):
    experience_text: Optional[str] = None
    education_text: Optional[str] = None
    skills_text: Optional[str] = None
    summary_text: Optional[str] = None
    certifications_text: Optional[str] = None
    projects_text: Optional[str] = None
    contact_text: Optional[str] = None
    raw_text: Optional[str] = None

class ParseSectionsResponse(BaseModel):
    status: str
    work_experience: list[dict[str, Any]] = []
    education: list[dict[str, Any]] = []
    skills: list[str] = []
    summary: Optional[str] = None
    certifications: list[str] = []
    projects: list[str] = []
    processing_time_ms: float
    message: str

@router.post("/parse-sections", response_model=ParseSectionsResponse)
async def parse_sections_endpoint(request: ParseSectionsRequest):
    import time
    start_time = time.time()
    
    work_experience = []
    education = []
    
    if request.experience_text:
        parser = WorkExperienceParser()
        result = parser.parse_experience_section(request.experience_text)
        for job in result:
            work_experience.append({
                "job_title": job.title,
                "company_name": job.company,
                "start_date": job.start_date.isoformat() if job.start_date else None,
                "end_date": job.end_date.isoformat() if job.end_date else None,
                "is_current": job.is_current,
                "location": job.location,
                "description": job.description
            })
            
    if request.education_text:
        parser = EducationParser()
        result = parser.parse_education_section(request.education_text)
        for edu in result:
            education.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "start_date": edu.start_date.isoformat() if edu.start_date else None,
                "end_date": edu.end_date.isoformat() if edu.end_date else None,
                "gpa": edu.gpa
            })
            
    processing_time_ms = (time.time() - start_time) * 1000
    return ParseSectionsResponse(
        status="success",
        work_experience=work_experience,
        education=education,
        skills=[],
        summary=request.summary_text if request.summary_text else None,
        certifications=[],
        projects=[],
        processing_time_ms=processing_time_ms,
        message="Parsed successfully"
    )
