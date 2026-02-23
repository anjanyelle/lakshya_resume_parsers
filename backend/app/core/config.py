from functools import lru_cache
import json
from typing import Any, Iterable

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Resume Parser API"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 7

    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/resume_parser"
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    SECRET_KEY: str = "change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    STORAGE_DIR: str = "./storage"
    UPLOAD_MAX_SIZE_MB: int = 10
    ALLOWED_UPLOAD_EXTENSIONS: list[str] = Field(
        default_factory=lambda: ["pdf", "doc", "docx", "txt", "rtf", "png", "jpg", "jpeg"]
    )

    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_REGION: str = "us-east-1"
    S3_BUCKET: str | None = None
    S3_USE_SSL: bool = True

    CLAMAV_ENABLED: bool = False
    CLAMAV_PATH: str = "clamscan"

    OCR_MIN_TEXT_CHARS: int = 100
    OCR_MAX_PAGES: int = 15  # Limit OCR to first N pages (safety for very long PDFs)
    PDF_MAX_PAGES: int = 50  # Limit non-OCR PDF extraction (memory/speed for large resumes)
    TESSERACT_CMD: str | None = None
    TESSERACT_LANG: str = "eng"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_RESULT_TTL_SECONDS: int = 86400
    PARSING_JOB_RETENTION_DAYS: int = 30

    PARSING_MODE: str = "full"  # full | text_only | deterministic

    LLM_PROVIDER: str = "local"  # local | none | openai | anthropic
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20240620"

    LOCAL_LLM_BASE_URL: str = "http://localhost:11434"
    LOCAL_LLM_MODEL: str = "llama3.1:8b-instruct"
    LOCAL_LLM_FALLBACK_MODEL: str | None = None
    LLM_RATE_LIMIT_PER_MINUTE: int = 30
    LLM_CACHE_TTL_SECONDS: int = 604800  # 7 days
    LLM_TIMEOUT_SECONDS: int = 90
    LLM_MAX_RETRIES: int = 2
    LLM_MAX_CHARS: int = 12000
    LLM_CHUNK_CHARS: int = 9000
    LLM_CHUNK_OVERLAP: int = 500

    OLLAMA_TEMPERATURE: float = 0.1
    OLLAMA_NUM_CTX: int | None = None
    OLLAMA_NUM_BATCH: int | None = None
    OLLAMA_NUM_THREAD: int | None = None
    OLLAMA_NUM_GPU: int | None = None
    OLLAMA_KEEP_ALIVE: str | None = "5m"

    REDIS_URL: str | None = None
    CSRF_ENABLED: bool = False

    ADMIN_API_KEY: str | None = None

    ENCRYPTION_KEY: str | None = None
    ENCRYPTION_KEYS_JSON: str | None = None
    DEFAULT_TENANT_ID: str = "default"

    REVIEW_CONFIDENCE_THRESHOLD: float = 0.7
    REVIEW_FIELD_THRESHOLD: float = 0.6
    CORRECTION_PATTERN_MIN_COUNT: int = 3

    SKILL_EXPAND_RELATED_SKILLS: bool = False
    SKILL_RELATED_MIN_BASE_CONFIDENCE: float = 0.85

    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_RELEASE: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    APP_VERSION: str = "0.1.0"
    DEPLOYMENT_ID: str | None = None

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_ignore_empty=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return []
            if cleaned.startswith("["):
                try:
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except Exception:  # noqa: BLE001
                    pass
                return [origin.strip().strip('"').strip("'") for origin in cleaned.strip("[]").split(",") if origin]
            return [origin.strip() for origin in cleaned.split(",") if origin.strip()]
        if isinstance(value, Iterable):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        raise ValueError("Invalid CORS_ORIGINS format")

    @field_validator("ALLOWED_UPLOAD_EXTENSIONS", mode="before")
    @classmethod
    def normalize_extensions(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned.startswith("["):
                try:
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return [str(item).strip().strip('"').strip("'").lstrip(".") for item in parsed if str(item).strip()]
                except Exception:  # noqa: BLE001
                    pass
            return [item.strip().strip('"').strip("'").lstrip(".") for item in cleaned.split(",") if item.strip()]
        if isinstance(value, Iterable):
            return [str(item).strip().strip('"').strip("'").lstrip(".") for item in value if str(item).strip()]
        raise ValueError("Invalid ALLOWED_UPLOAD_EXTENSIONS format")


@lru_cache
def get_settings() -> Settings:
    return Settings()
