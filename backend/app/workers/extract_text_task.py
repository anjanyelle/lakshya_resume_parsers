from __future__ import annotations

import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.parsing_job import ParsingJob, ParsingJobStatus
from app.services.parser.extract_text import extract_text
from app.services.storage import download_s3_to_file
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _download_s3_to_temp(s3_uri: str) -> Path:
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp_path = Path(temp.name)
    temp.close()
    download_s3_to_file(s3_uri, str(temp_path))
    return temp_path


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
)
def extract_text_task(self, job_id: str) -> None:  # noqa: ANN001
    session = SessionLocal()
    try:
        job = session.execute(
            select(ParsingJob).where(ParsingJob.id == job_id)
        ).scalar_one_or_none()
        if not job:
            logger.warning("Parsing job not found", extra={"job_id": job_id})
            return

        job.status = ParsingJobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        job.last_stage = "extract_text"
        session.commit()

        temp_path = None
        file_path = job.file_path
        if file_path.startswith("s3://"):
            temp_path = _download_s3_to_temp(file_path)
            local_path = temp_path
        else:
            local_path = Path(file_path)
            if not local_path.exists():
                raise FileNotFoundError(f"File not found: {local_path}")

        extracted = extract_text(local_path)
        job.raw_text = extracted.text
        job.ocr_confidence = extracted.ocr_confidence

        parsed = job.parsed_data or {}
        meta: dict[str, object] = {
            "method": extracted.method,
            "used_ocr": extracted.used_ocr,
        }
        debug = getattr(extracted, "debug", None)
        if isinstance(debug, dict) and debug:
            meta["debug"] = debug
        parsed["text_extraction"] = meta

        debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        debug_bundle = dict(debug_bundle)
        debug_bundle["text_extraction"] = {
            **meta,
            "ocr_confidence": extracted.ocr_confidence,
        }
        parsed["debug"] = debug_bundle
        job.parsed_data = parsed
        session.commit()

        logger.info("Text extraction completed", extra={"job_id": job_id})
        if temp_path:
            temp_path.unlink(missing_ok=True)
    except Exception as exc:
        session.rollback()
        logger.exception("Parsing job failed", extra={"job_id": job_id})
        try:
            job = session.execute(
                select(ParsingJob).where(ParsingJob.id == job_id)
            ).scalar_one_or_none()
            if job:
                job.status = ParsingJobStatus.FAILED
                job.error_message = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                session.commit()
        except Exception:  # noqa: BLE001
            session.rollback()
        raise
    finally:
        session.close()
