import logging
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit, get_current_user, get_db
from app.core.config import get_settings
from app.models.candidate import Candidate, CandidateStatus
from app.models.parsing_job import ParsingJob, ParsingJobStatus
from app.schemas.upload import BatchUploadResponse, UploadJobResponse
from app.services.storage import copy_s3_object, save_bytes_to_local, upload_bytes_to_s3
from app.utils.file_validation import validate_magic
from app.utils.audit import log_audit
from app.utils.virus_scan import scan_file
from app.workers.pipeline import start_parsing_workflow

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


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
        log_audit(
            db,
            user_id=str(current_user.id) if current_user else None,
            action="upload_resume",
            resource_type="candidate",
            resource_id=str(candidate.id),
            ip_address=None,
        )
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
        raise HTTPException(status_code=400, detail="File is stored in S3")
    local_path = Path(job.file_path)
    if not local_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(local_path, filename=job.filename)
