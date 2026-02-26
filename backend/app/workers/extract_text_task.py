from __future__ import annotations

import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.parsing_job import ParsingJob, ParsingJobStatus
from app.services.parser.extract_text import extract_text
from app.services.parser.normalize import _normalize_table_lines_with_stats
from app.core.observability import RESUME_FILE_TYPE_TOTAL
from app.services.storage import download_s3_to_file
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _download_s3_to_temp(s3_uri: str, filename_hint: str | None = None) -> Path:
    """Download S3 object to a temp file, preserving extension for extract_text dispatch."""
    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=Path(filename_hint or "file.bin").suffix or ".bin",
    )
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
    queue="extract",
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
            ext_hint = ""
            if job.filename and "." in job.filename:
                ext_hint = job.filename
            elif "." in file_path:
                ext_hint = Path(file_path).name
            temp_path = _download_s3_to_temp(file_path, filename_hint=ext_hint or None)
            local_path = temp_path
        else:
            local_path = Path(file_path)
            if not local_path.exists():
                raise FileNotFoundError(f"File not found: {local_path}")

        extracted = extract_text(local_path)
        raw_len = len(extracted.text or "")
        logger.info(
            "[DATA-LOSS CHECK] File upload → extraction: job_id=%s, chars=%d, method=%s, ocr=%s",
            job_id,
            raw_len,
            extracted.method,
            extracted.used_ocr,
            extra={"job_id": job_id, "extracted_chars": raw_len, "method": extracted.method},
        )
        if raw_len > 0:
            sample = (extracted.text or "")[: 250].replace("\n", " ")
            logger.info(
                "[DATA-LOSS CHECK] Raw extracted sample (first 250 chars): %s",
                sample if len(sample) <= 250 else sample[: 247] + "...",
                extra={"job_id": job_id},
            )
        source_ext = ""
        try:
            if job.filename and "." in job.filename:
                source_ext = job.filename.rsplit(".", 1)[-1].lower()
            elif job.file_path and "." in job.file_path:
                source_ext = Path(job.file_path).suffix.lower().lstrip(".")
        except Exception:  # noqa: BLE001
            source_ext = ""

        if source_ext:
            RESUME_FILE_TYPE_TOTAL.labels(file_type=source_ext).inc()

        table_norm_applied = False
        table_rows_normalized = 0
        final_text = extracted.text
        before_norm_len = len(final_text or "")
        if source_ext in {"docx", "doc"}:
            final_text, table_norm_applied, table_rows_normalized = _normalize_table_lines_with_stats(
                final_text
            )
        after_norm_len = len(final_text or "")
        logger.info(
            "[DATA-LOSS CHECK] After table norm (docx/doc): before=%d, after=%d, applied=%s, rows_norm=%d",
            before_norm_len,
            after_norm_len,
            table_norm_applied,
            table_rows_normalized,
            extra={
                "job_id": job_id,
                "before_chars": before_norm_len,
                "after_chars": after_norm_len,
                "table_norm_applied": table_norm_applied,
            },
        )

        job.raw_text = final_text
        job.ocr_confidence = extracted.ocr_confidence

        parsed = job.parsed_data or {}
        meta: dict[str, object] = {
            "method": extracted.method,
            "used_ocr": extracted.used_ocr,
        }
        debug = getattr(extracted, "debug", None)
        debug_bundle = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
        debug_bundle = dict(debug_bundle)

        if isinstance(debug, dict) and debug:
            debug_copy = dict(debug)
            if extracted.method == "docx":
                docx_header = str(debug_copy.pop("docx_header", "") or "").strip()
                docx_footer = str(debug_copy.pop("docx_footer", "") or "").strip()
                if docx_header:
                    debug_bundle["docx_header"] = docx_header
                if docx_footer:
                    debug_bundle["docx_footer"] = docx_footer

                stat_keys = {
                    "total_paragraphs",
                    "heading_paragraphs_count",
                    "bullet_paragraphs_count",
                    "table_count",
                    "textbox_count",
                    "had_header_footer",
                }
                for k in list(stat_keys):
                    if k in debug_copy:
                        meta[k] = debug_copy.get(k)

            meta["debug"] = debug_copy
        parsed["text_extraction"] = meta

        text_extraction_debug = {
            **meta,
            "ocr_confidence": extracted.ocr_confidence,
        }

        if source_ext in {"docx", "doc"}:
            text_extraction_debug["table_line_normalization_applied"] = bool(table_norm_applied)
            text_extraction_debug["table_rows_normalized"] = int(table_rows_normalized)

        if extracted.method == "docx" and isinstance(debug, dict) and debug:
            for k in (
                "total_paragraphs",
                "heading_paragraphs_count",
                "bullet_paragraphs_count",
                "table_count",
                "textbox_count",
                "had_header_footer",
            ):
                if k in debug:
                    text_extraction_debug[k] = debug.get(k)

        debug_bundle["text_extraction"] = text_extraction_debug
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
