from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import structlog
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.observability import (
    DOC_CONVERSION_DURATION_SECONDS,
    DOC_CONVERSION_FAILURES_TOTAL,
    DOC_CONVERSIONS_TOTAL,
)
from app.models.parsing_job import ParsingJob
from app.services.storage import download_s3_to_file, upload_bytes_to_s3
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    if not s3_uri.startswith("s3://"):
        raise ValueError("Invalid S3 URI")
    _, _, path = s3_uri.partition("s3://")
    bucket, _, key = path.partition("/")
    if not bucket or not key:
        raise ValueError("Invalid S3 URI")
    return bucket, key


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
    name="app.workers.doc_convert_task.convert_doc_to_docx_task",
    queue="doc_convert",
)
def convert_doc_to_docx_task(self, job_id: str, file_path: str) -> str:  # noqa: ANN001
    start_time = time.perf_counter()
    DOC_CONVERSIONS_TOTAL.inc()

    structlog.contextvars.bind_contextvars(job_id=job_id)
    logger.info(
        "DOC conversion started",
        extra={"job_id": job_id, "file_path": file_path},
    )

    session = SessionLocal()
    temp_dir: Path | None = None
    try:
        job = session.execute(select(ParsingJob).where(ParsingJob.id == job_id)).scalar_one_or_none()
        if not job:
            return file_path

        source_path = file_path or job.file_path
        if not source_path:
            raise ValueError("Missing file_path")

        ext = Path(source_path).suffix.lower()
        if ext != ".doc":
            return source_path

        temp_dir = Path(tempfile.mkdtemp(prefix="doc_convert_"))
        local_doc_path = temp_dir / f"{job_id}.doc"

        if source_path.startswith("s3://"):
            download_s3_to_file(source_path, str(local_doc_path))
        else:
            src_local = Path(source_path)
            if not src_local.exists():
                raise FileNotFoundError(f"File not found: {src_local}")
            shutil.copy2(src_local, local_doc_path)

        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "docx",
                "--outdir",
                str(temp_dir),
                str(local_doc_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )

        converted_path = temp_dir / f"{job_id}.docx"
        if not converted_path.exists():
            fallback = temp_dir / f"{local_doc_path.stem}.docx"
            if fallback.exists():
                converted_path = fallback
            else:
                raise RuntimeError("DOC conversion did not produce output")

        converted_bytes = converted_path.read_bytes()

        if source_path.startswith("s3://"):
            _, key = _parse_s3_uri(source_path)
            dest_key = str(key)
            if dest_key.lower().endswith(".doc"):
                dest_key = dest_key[: -len(".doc")] + ".docx"
            else:
                dest_key = dest_key + ".docx"
            stored = upload_bytes_to_s3(converted_bytes, dest_key)
            new_path = stored.uri
        else:
            dest_path = Path(source_path).with_suffix(".docx")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(converted_bytes)
            new_path = str(dest_path)

        job.file_path = new_path
        job.last_stage = "doc_convert"
        session.add(job)
        session.commit()

        duration = time.perf_counter() - start_time
        DOC_CONVERSION_DURATION_SECONDS.observe(duration)
        logger.info(
            "DOC conversion succeeded",
            extra={
                "job_id": job_id,
                "source_path": source_path,
                "new_path": new_path,
                "duration_seconds": duration,
            },
        )
        return new_path
    except Exception as exc:
        DOC_CONVERSION_FAILURES_TOTAL.inc()
        duration = time.perf_counter() - start_time
        DOC_CONVERSION_DURATION_SECONDS.observe(duration)
        logger.exception(
            "DOC conversion failed",
            extra={
                "job_id": job_id,
                "file_path": file_path,
                "duration_seconds": duration,
                "error": str(exc),
            },
        )
        session.rollback()
        raise
    finally:
        session.close()
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)
