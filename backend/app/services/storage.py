from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StorageObject:
    bucket: str
    key: str

    @property
    def uri(self) -> str:
        return f"s3://{self.bucket}/{self.key}"


def _get_s3_client():
    settings = get_settings()
    if not settings.S3_BUCKET:
        raise ValueError("S3_BUCKET is not configured")
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        region_name=settings.S3_REGION,
        use_ssl=settings.S3_USE_SSL,
    )


def upload_bytes_to_s3(data: bytes, key: str) -> StorageObject:
    settings = get_settings()
    client = _get_s3_client()
    try:
        client.upload_fileobj(BytesIO(data), settings.S3_BUCKET, key)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to upload to S3", extra={"key": key})
        raise RuntimeError("Failed to upload file") from exc
    return StorageObject(bucket=settings.S3_BUCKET, key=key)


def save_bytes_to_local(data: bytes, key: str) -> str:
    settings = get_settings()
    base_path = Path(settings.STORAGE_DIR)
    target_path = base_path / key
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(data)
    return str(target_path)


def download_s3_to_file(s3_uri: str, destination: str) -> None:
    if not s3_uri.startswith("s3://"):
        raise ValueError("Invalid S3 URI")
    _, _, path = s3_uri.partition("s3://")
    bucket, _, key = path.partition("/")
    client = _get_s3_client()
    try:
        client.download_file(bucket, key, destination)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to download from S3", extra={"key": key})
        raise RuntimeError("Failed to download file") from exc


def generate_presigned_url(s3_uri: str, expires_in: int = 3600) -> str:
    if not s3_uri.startswith("s3://"):
        raise ValueError("Invalid S3 URI")
    _, _, path = s3_uri.partition("s3://")
    bucket, _, key = path.partition("/")
    client = _get_s3_client()
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to generate presigned URL", extra={"key": key})
        raise RuntimeError("Failed to generate download URL") from exc
