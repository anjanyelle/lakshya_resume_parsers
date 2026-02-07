from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings
from app.core.observability import init_sentry, setup_logging

settings = get_settings()
setup_logging()
init_sentry()

celery_app = Celery(
    "resume_parser",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=600,
    task_soft_time_limit=540,
    result_expires=settings.CELERY_RESULT_TTL_SECONDS,
    beat_schedule={
        "retry-failed-jobs-daily": {
            "task": "app.workers.pipeline.retry_failed_jobs",
            "schedule": crontab(hour=2, minute=0),
        },
        "cleanup-old-jobs-weekly": {
            "task": "app.workers.pipeline.cleanup_old_jobs",
            "schedule": crontab(day_of_week="sun", hour=3, minute=0),
        },
        "generate-accuracy-report-weekly": {
            "task": "app.workers.pipeline.generate_accuracy_report",
            "schedule": crontab(day_of_week="sun", hour=4, minute=0),
        },
    },
)
