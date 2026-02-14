import logging
import time
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
import structlog
from sqlalchemy import text

from app.core.database import engine, SessionLocal
from app.core.observability import (
    bind_request_context,
    clear_request_context,
    init_sentry,
    instrument_db,
    observe_request,
    setup_logging,
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
)


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
    Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
    logger.info("Storage directory ready at %s", settings.STORAGE_DIR)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("HTTP exception: %s", exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(api_router, prefix=settings.API_V1_STR)


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
