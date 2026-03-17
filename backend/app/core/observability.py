from __future__ import annotations

import logging
import logging.config
import time

logger = logging.getLogger(__name__)
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import structlog
from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy import event, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Candidate, CandidateSkill, ParsingJob, Skill
from app.models.parsing_job import ParsingJobStatus

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "API request latency in seconds",
    ["method", "path"],
)
REQUEST_ERRORS = Counter(
    "api_request_errors_total",
    "Total API error responses",
    ["method", "path", "status"],
)

PARSING_JOBS_TOTAL = Counter(
    "parsing_jobs_total",
    "Total parsing jobs created",
)
PARSING_JOBS_FAILED = Counter(
    "parsing_jobs_failed_total",
    "Total parsing jobs failed",
)
PARSING_PROCESSING_TIME = Histogram(
    "parsing_job_processing_seconds",
    "Parsing job processing time in seconds",
)
PARSING_STAGE_DURATION = Histogram(
    "parsing_stage_duration_seconds",
    "Parsing stage duration in seconds",
    ["stage"],
)
CONFIDENCE_SCORES = Histogram(
    "parsing_confidence_score",
    "Parsing confidence scores",
    buckets=(0.1, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0),
)

QUEUE_DEPTH = Gauge(
    "queue_depth",
    "Celery queue depth",
    ["queue"],
)

CELERY_QUEUE_DEPTH = Gauge(
    "celery_queue_depth",
    "Celery queue depth by queue",
    ["queue"],
)
WORKER_UTILIZATION = Gauge(
    "worker_utilization",
    "Celery worker utilization ratio",
    ["worker"],
)

DB_POOL_SIZE = Gauge(
    "db_connection_pool_size",
    "Database connection pool size",
)
LLM_CACHE_HITS = Counter(
    "llm_cache_hits_total",
    "LLM cache hits",
)
LLM_CACHE_MISSES = Counter(
    "llm_cache_misses_total",
    "LLM cache misses",
)
DB_QUERY_LATENCY = Histogram(
    "db_query_latency_seconds",
    "Database query latency in seconds",
)

BUSINESS_CANDIDATES_PARSED_TODAY = Gauge(
    "candidates_parsed_today",
    "Candidates parsed today",
)
BUSINESS_AVG_EXPERIENCE_YEARS = Gauge(
    "avg_experience_years",
    "Average years of experience across candidates",
)
TOP_SKILLS = Gauge(
    "top_skills_extracted",
    "Top skills extracted",
    ["skill"],
)
PARSING_JOBS_BY_FILETYPE = Gauge(
    "parsing_jobs_by_file_type",
    "Parsing jobs by file type and status",
    ["file_type", "status"],
)

RESUME_FILE_TYPE_TOTAL = Counter(
    "resume_file_type_total",
    "Total resumes processed by file type",
    ["file_type"],
)

RESUME_PARSE_QUALITY_SCORE = Histogram(
    "resume_parse_quality_score",
    "Overall resume parse confidence score",
    ["file_type"],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

EXPERIENCE_PARSE_QUALITY_SCORE = Histogram(
    "experience_parse_quality_score",
    "Work experience parse quality score",
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

SECTION_DETECTION_CONFIDENCE = Histogram(
    "section_detection_confidence",
    "Section detection confidence by section",
    ["section"],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

OCR_TRIGGER_TOTAL = Counter(
    "ocr_trigger_total",
    "Total OCR fallbacks triggered",
)

DOC_CONVERSIONS_TOTAL = Counter(
    "doc_conversions_total",
    "Total DOC to DOCX conversions attempted",
)
DOC_CONVERSION_FAILURES_TOTAL = Counter(
    "doc_conversion_failures_total",
    "Total DOC to DOCX conversion failures",
)
DOC_CONVERSION_DURATION_SECONDS = Histogram(
    "doc_conversion_duration_seconds",
    "DOC to DOCX conversion duration in seconds",
)

CLIENT_EXTRACTIONS_TOTAL = Counter(
    "client_extractions_total",
    "Total client extraction attempts",
    ["method"],
)

CLIENT_EXTRACTION_TOTAL = Counter(
    "client_extraction_total",
    "Total client extraction attempts by method",
    ["method"],
)

REVIEW_FLAG_TOTAL = Counter(
    "review_flag_total",
    "Total review flags emitted",
    ["flag_name"],
)

FALLBACK_SEGMENTER_TOTAL = Counter(
    "fallback_segmenter_total",
    "Total times fallback segmenter was executed",
)

DB_UPSERT_CONFLICTS_TOTAL = Counter(
    "db_upsert_conflicts_total",
    "Total database upsert conflicts",
    ["table"],
)

SECTION_DETECTION_FALLBACK_TOTAL = Counter(
    "section_detection_fallback_total",
    "Total times deterministic section detection fallback segmenter activated",
)

# Pipeline parse metrics (emitted after task_save_to_database)
PARSE_DURATION = Histogram(
    "resume_parse_duration_seconds",
    "Parse time",
    ["format", "queue"],
)
SECTION_CONFIDENCE = Histogram(
    "resume_section_confidence",
    "Section detection confidence",
    ["section"],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)
FIELD_EXTRACTED = Counter(
    "resume_field_extracted_total",
    "Fields extracted",
    ["field", "format"],
)
PARSE_ERRORS = Counter(
    "resume_parse_errors_total",
    "Parse errors",
    ["stage", "format"],
)


def emit_parse_metrics(
    *,
    parsed: dict,
    format: str,  # noqa: A002
    queue: str = "persist",
    pipeline_duration_seconds: float | None = None,
) -> None:
    """Emit per-parse Prometheus metrics after successful save."""
    fmt = format or "unknown"
    if pipeline_duration_seconds is not None and pipeline_duration_seconds >= 0:
        PARSE_DURATION.labels(format=fmt, queue=queue).observe(pipeline_duration_seconds)

    sections = parsed.get("sections") if isinstance(parsed.get("sections"), dict) else {}
    for section, data in sections.items():
        if isinstance(data, dict):
            conf = data.get("confidence")
            try:
                val = float(conf) if conf is not None else 0.0
            except (TypeError, ValueError):
                val = 0.0
            SECTION_CONFIDENCE.labels(section=str(section)).observe(max(0.0, min(1.0, val)))

    contact = parsed.get("contact") if isinstance(parsed.get("contact"), dict) else {}
    work = parsed.get("work_experience") if isinstance(parsed.get("work_experience"), list) else []
    education = parsed.get("education") if isinstance(parsed.get("education"), list) else []

    email_val = None
    for e in (contact.get("emails") or []):
        if isinstance(e, dict) and str(e.get("email") or "").strip():
            email_val = e.get("email")
            break
    if email_val:
        FIELD_EXTRACTED.labels(field="email", format=fmt).inc()

    phone_val = None
    for p in (contact.get("phones") or []):
        if isinstance(p, dict) and str(p.get("phone") or "").strip():
            phone_val = p.get("phone")
            break
    if phone_val:
        FIELD_EXTRACTED.labels(field="phone", format=fmt).inc()

    company_val = work[0].get("company") if work and isinstance(work[0], dict) else None
    if company_val and str(company_val).strip():
        FIELD_EXTRACTED.labels(field="company", format=fmt).inc()

    title_val = work[0].get("title") if work and isinstance(work[0], dict) else None
    if title_val and str(title_val).strip():
        FIELD_EXTRACTED.labels(field="title", format=fmt).inc()

    degree_val = education[0].get("degree") if education and isinstance(education[0], dict) else None
    if degree_val and str(degree_val).strip():
        FIELD_EXTRACTED.labels(field="degree", format=fmt).inc()


def setup_logging() -> None:
    settings = get_settings()
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamper = structlog.processors.TimeStamper(fmt="iso")
    add_logger_name = getattr(structlog.processors, "add_logger_name", None)
    if add_logger_name is None:
        add_logger_name = getattr(structlog.stdlib, "add_logger_name", None)
    if add_logger_name is None:
        add_logger_name = lambda _logger, _method, event_dict: event_dict  # noqa: E731

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        timestamper,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    def _handler(filename: str, level: str) -> dict[str, Any]:
        return {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_dir / filename),
            "maxBytes": settings.LOG_MAX_BYTES,
            "backupCount": settings.LOG_BACKUP_COUNT,
            "level": level,
            "formatter": "json",
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "structlog.stdlib.ProcessorFormatter",
                    "processor": structlog.processors.JSONRenderer(),
                    "foreign_pre_chain": shared_processors,
                }
            },
            "handlers": {
                "app_file": _handler("app.log", settings.LOG_LEVEL),
                "error_file": _handler("error.log", "ERROR"),
                "celery_file": _handler("celery.log", settings.LOG_LEVEL),
                "audit_file": _handler("audit.log", settings.LOG_LEVEL),
            },
            "root": {
                "handlers": ["app_file", "error_file"],
                "level": settings.LOG_LEVEL,
            },
            "loggers": {
                "celery": {
                    "handlers": ["celery_file", "error_file"],
                    "level": settings.LOG_LEVEL,
                    "propagate": False,
                },
                "audit": {
                    "handlers": ["audit_file", "error_file"],
                    "level": settings.LOG_LEVEL,
                    "propagate": False,
                },
            },
        }
    )


def init_sentry() -> None:
    settings = get_settings()
    if not settings.SENTRY_DSN:
        return
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        release=settings.SENTRY_RELEASE,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[FastApiIntegration(), CeleryIntegration(), SqlalchemyIntegration()],
    )


def bind_request_context(
    *,
    request_id: str,
    user_id: str | None = None,
    candidate_id: str | None = None,
    job_id: str | None = None,
) -> None:
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        user_id=user_id,
        candidate_id=candidate_id,
        job_id=job_id,
    )


def clear_request_context() -> None:
    structlog.contextvars.clear_contextvars()


def observe_request(method: str, path: str, status: int, duration: float) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
    if status >= 400:
        REQUEST_ERRORS.labels(method=method, path=path, status=str(status)).inc()


def observe_parsing_success(confidence: float | None, started_at: datetime | None) -> None:
    if confidence is not None:
        CONFIDENCE_SCORES.observe(confidence)
    if started_at:
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        if elapsed >= 0:
            PARSING_PROCESSING_TIME.observe(elapsed)


def observe_stage_duration(stage: str, duration: float) -> None:
    PARSING_STAGE_DURATION.labels(stage=stage).observe(duration)


def observe_parsing_failure() -> None:
    PARSING_JOBS_FAILED.inc()


def increment_jobs_total() -> None:
    PARSING_JOBS_TOTAL.inc()


def instrument_db(engine: Engine) -> None:
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # noqa: ANN001
        conn.info.setdefault("query_start_time", []).append(time.perf_counter())

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # noqa: ANN001
        start_time = conn.info.get("query_start_time", []).pop(-1)
        DB_QUERY_LATENCY.observe(time.perf_counter() - start_time)


def update_db_pool_metrics(engine: Engine) -> None:
    try:
        pool_size = engine.pool.size()
        DB_POOL_SIZE.set(pool_size)
        checked_out = engine.pool.checkedout()
        if pool_size > 0 and checked_out >= pool_size:
            logger.warning(
                "DB connection pool exhausted",
                extra={"pool_size": pool_size, "checked_out": checked_out},
            )
    except Exception:
        return


_queue_poller_started = False


def start_queue_metrics_poller(*, interval_seconds: int = 30) -> None:
    global _queue_poller_started
    if _queue_poller_started:
        return
    _queue_poller_started = True

    import threading

    def _loop() -> None:
        while True:
            try:
                update_queue_metrics()
            except Exception:
                pass
            time.sleep(max(5, int(interval_seconds)))

    t = threading.Thread(target=_loop, name="queue-metrics-poller", daemon=True)
    t.start()


def update_business_metrics(db: Session) -> None:
    today = date.today()
    start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

    parsed_today = db.execute(
        select(func.count()).select_from(ParsingJob).where(
            ParsingJob.status == ParsingJobStatus.SUCCESS,
            ParsingJob.completed_at >= start,
            ParsingJob.completed_at <= end,
        )
    ).scalar_one()
    avg_exp = db.execute(
        select(func.avg(Candidate.years_experience)).select_from(Candidate)
    ).scalar_one()

    BUSINESS_CANDIDATES_PARSED_TODAY.set(parsed_today or 0)
    BUSINESS_AVG_EXPERIENCE_YEARS.set(float(avg_exp or 0))

    TOP_SKILLS.clear()
    top_skills = (
        db.execute(
            select(Skill.name, func.count())
            .select_from(CandidateSkill)
            .join(Skill, Skill.id == CandidateSkill.skill_id)
            .group_by(Skill.name)
            .order_by(func.count().desc())
            .limit(10)
        )
        .all()
    )
    for skill_name, count in top_skills:
        TOP_SKILLS.labels(skill=str(skill_name)).set(int(count))

    PARSING_JOBS_BY_FILETYPE.clear()
    jobs_by_type = (
        db.execute(
            select(ParsingJob.filename, ParsingJob.status)
        )
        .all()
    )
    counts: dict[tuple[str, str], int] = {}
    for filename, status in jobs_by_type:
        extension = ""
        if filename and "." in filename:
            extension = filename.rsplit(".", 1)[-1].lower()
        key = (extension or "unknown", str(status))
        counts[key] = counts.get(key, 0) + 1
    for (file_type, status), count in counts.items():
        PARSING_JOBS_BY_FILETYPE.labels(file_type=file_type, status=status).set(count)


def update_queue_metrics() -> None:
    settings = get_settings()
    broker = settings.CELERY_BROKER_URL
    if broker.startswith("redis://"):
        try:
            import redis

            client = redis.Redis.from_url(broker)
            queues = [
                "doc_convert",
                "ocr",
                "extract",
                "parse",
                "llm",
                "persist",
                "celery",
            ]
            for q in queues:
                try:
                    queue_len = int(client.llen(q))
                except Exception:
                    queue_len = 0
                QUEUE_DEPTH.labels(queue=q).set(queue_len)
                CELERY_QUEUE_DEPTH.labels(queue=q).set(queue_len)
        except Exception:
            return

    try:
        from app.workers.celery_app import celery_app

        insp = celery_app.control.inspect()
        stats = insp.stats() or {}
        for worker, payload in stats.items():
            if not payload:
                continue
            active = payload.get("pool", {}).get("max-concurrency") or 1
            running = payload.get("pool", {}).get("processes") or active
            utilization = min(1.0, running / active) if active else 0.0
            WORKER_UTILIZATION.labels(worker=worker).set(utilization)
    except Exception:
        return
