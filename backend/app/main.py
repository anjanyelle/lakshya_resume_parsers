import logging
import time
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
import structlog
from sqlalchemy import text

from app.core.database import engine, SessionLocal
from app.models.candidate import Candidate
from app.models.parsing_job import ParsingJob
from app.core.observability import (
    bind_request_context,
    clear_request_context,
    init_sentry,
    instrument_db,
    observe_request,
    setup_logging,
    start_queue_metrics_poller,
    update_business_metrics,
    update_db_pool_metrics,
    update_queue_metrics,
)

from app.api.v1.api import api_router
from app.core.config import get_settings

settings = get_settings()

setup_logging()
init_sentry()
instrument_db(engine)
logger = structlog.get_logger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class OptionsPreflightMiddleware(BaseHTTPMiddleware):
    """Runs first (added last). Ensures OPTIONS preflight always gets 200 so CORS never gets 400."""

    async def dispatch(self, request: Request, call_next):
        if request.method != "OPTIONS":
            return await call_next(request)
        origin = request.headers.get("origin")
        response = JSONResponse(content={}, status_code=200)
        if origin:
            if not settings.CORS_ORIGINS or origin in settings.CORS_ORIGINS:
                response.headers["Access-Control-Allow-Origin"] = origin
            elif settings.CORS_ORIGINS:
                response.headers["Access-Control-Allow-Origin"] = settings.CORS_ORIGINS[0]
        elif settings.CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = settings.CORS_ORIGINS[0]
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = request.headers.get("access-control-request-headers", "content-type,authorization,x-csrf-token")
        response.headers["Access-Control-Max-Age"] = "86400"
        return response


# Add last so it runs first (outermost)
app.add_middleware(OptionsPreflightMiddleware)


@app.middleware("http")
async def csrf_protect(request: Request, call_next):
    if settings.CSRF_ENABLED and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        csrf_cookie = request.cookies.get("csrftoken")
        csrf_header = request.headers.get("X-CSRF-Token")
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return JSONResponse(status_code=403, content={"detail": "CSRF validation failed"})
    return await call_next(request)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or uuid4().hex
    bind_request_context(request_id=request_id)
    start = time.perf_counter()
    status_code = 500
    try:
        try:
            import sentry_sdk

            sentry_sdk.add_breadcrumb(
                category="request",
                message=f"{request.method} {request.url.path}",
                level="info",
                data={"request_id": request_id},
            )
            sentry_sdk.set_tag("endpoint", request.url.path)
        except Exception:
            pass
        response = await call_next(request)
        status_code = response.status_code
    finally:
        duration = time.perf_counter() - start
        observe_request(request.method, request.url.path, status_code, duration)
        clear_request_context()
    response.headers["X-Request-Id"] = request_id
    return response


@app.on_event("startup")
async def startup() -> None:
    storage_path = Path(settings.STORAGE_DIR)
    storage_path.mkdir(parents=True, exist_ok=True)
    (storage_path / "uploads").mkdir(parents=True, exist_ok=True)
    logger.info("Storage directory ready at %s (uploads: %s)", settings.STORAGE_DIR, storage_path / "uploads")
    start_queue_metrics_poller(interval_seconds=30)


def _add_cors_headers(response: JSONResponse, request: Request) -> JSONResponse:
    """Add CORS headers to error responses so the browser surfaces the real error instead of CORS."""
    origin = request.headers.get("origin")
    if origin and origin in settings.CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
    elif settings.CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = settings.CORS_ORIGINS[0]
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("HTTP exception: %s", exc.detail)
    response = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return _add_cors_headers(response, request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    response = JSONResponse(status_code=500, content={"detail": "Internal server error"})
    return _add_cors_headers(response, request)


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root() -> dict:
    """Root route so GET / returns 200 instead of 404."""
    return {
        "service": settings.APP_NAME,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_STR,
    }


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    db = SessionLocal()
    try:
        update_business_metrics(db)
        update_db_pool_metrics(engine)
        update_queue_metrics()
    finally:
        db.close()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/metrics/summary", include_in_schema=False)
async def metrics_summary() -> dict:
    db = SessionLocal()
    try:
        jobs = (
            db.query(ParsingJob)
            .order_by(ParsingJob.started_at.desc())
            .limit(1000)
            .all()
        )

        conf_by_type: dict[str, list[float]] = {}
        exp_quality: list[float] = []
        section_success: dict[str, dict[str, int]] = {}
        flag_freq: dict[str, int] = {}

        candidate_ids = [j.candidate_id for j in jobs if getattr(j, "candidate_id", None) is not None]
        candidates: dict = {}
        if candidate_ids:
            rows = db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()
            candidates = {c.id: c for c in rows}

        for job in jobs:
            filename = getattr(job, "filename", "") or ""
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"
            conf = getattr(job, "confidence_score", None)
            if isinstance(conf, (int, float)):
                conf_by_type.setdefault(ext, []).append(float(conf))

            parsed = getattr(job, "parsed_data", None) or {}
            debug = parsed.get("debug") if isinstance(parsed.get("debug"), dict) else {}
            we_debug = debug.get("work_experience") if isinstance(debug.get("work_experience"), dict) else {}
            q = we_debug.get("primary_quality_score")
            try:
                if q is not None:
                    exp_quality.append(float(q))
            except (TypeError, ValueError):
                pass

            sections = parsed.get("sections") if isinstance(parsed.get("sections"), dict) else {}
            for sec_name, sec_block in sections.items():
                bucket = section_success.setdefault(str(sec_name), {"present": 0, "success": 0})
                bucket["present"] += 1
                ok = False
                if isinstance(sec_block, dict):
                    content = str(sec_block.get("content") or "").strip()
                    try:
                        sec_conf = float(sec_block.get("confidence", 0.0) or 0.0)
                    except (TypeError, ValueError):
                        sec_conf = 0.0
                    ok = bool(content) and sec_conf >= 0.6
                if ok:
                    bucket["success"] += 1

            cand = candidates.get(getattr(job, "candidate_id", None))
            review_flags = getattr(cand, "review_flags", None) if cand is not None else None
            if isinstance(review_flags, dict):
                for flag in review_flags.get("rule_flags") or []:
                    key = str(flag)
                    flag_freq[key] = flag_freq.get(key, 0) + 1
                flagged_fields = review_flags.get("flagged_fields")
                if isinstance(flagged_fields, dict):
                    for field_name in flagged_fields.keys():
                        key = str(field_name)
                        flag_freq[key] = flag_freq.get(key, 0) + 1

        avg_conf_by_type = {
            ft: (sum(vals) / len(vals)) if vals else None for ft, vals in conf_by_type.items()
        }
        avg_exp_quality = (sum(exp_quality) / len(exp_quality)) if exp_quality else None

        section_success_rate = {
            name: (bucket["success"] / bucket["present"]) if bucket["present"] else 0.0
            for name, bucket in section_success.items()
        }

        return {
            "window": 1000,
            "avg_confidence_by_file_type": avg_conf_by_type,
            "avg_experience_quality_score": avg_exp_quality,
            "section_detection_success_rate": section_success_rate,
            "review_flag_frequency": dict(sorted(flag_freq.items(), key=lambda it: it[1], reverse=True)),
        }
    finally:
        db.close()


@app.get("/health", include_in_schema=False)
async def root_health_check() -> dict[str, str | None]:
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "deployment_id": settings.DEPLOYMENT_ID,
    }


@app.get("/health/live", include_in_schema=False)
async def live_health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", include_in_schema=False)
async def ready_health_check() -> dict[str, str | dict[str, str]]:
    checks: dict[str, str] = {}
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:  # noqa: BLE001
        checks["database"] = "error"
    finally:
        db.close()

    if settings.REDIS_URL:
        try:
            import redis

            client = redis.Redis.from_url(settings.REDIS_URL)
            client.ping()
            checks["redis"] = "ok"
        except Exception:  # noqa: BLE001
            checks["redis"] = "error"
    else:
        checks["redis"] = "skipped"

    if settings.S3_BUCKET:
        try:
            import boto3

            session = boto3.session.Session()
            s3 = session.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                region_name=settings.S3_REGION,
                use_ssl=settings.S3_USE_SSL,
            )
            s3.head_bucket(Bucket=settings.S3_BUCKET)
            checks["s3"] = "ok"
        except Exception:  # noqa: BLE001
            checks["s3"] = "error"
    else:
        checks["s3"] = "skipped"

    status = "ok" if all(value in {"ok", "skipped"} for value in checks.values()) else "error"
    return {
        "status": status,
        "checks": checks,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "deployment_id": settings.DEPLOYMENT_ID,
    }
