from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def scan_file(path: Path) -> None:
    settings = get_settings()
    if not settings.CLAMAV_ENABLED:
        return

    try:
        result = subprocess.run(
            [settings.CLAMAV_PATH, "--no-summary", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        if settings.ENVIRONMENT.lower() == "development":
            logger.warning(
                "ClamAV not available; skipping scan in development",
                extra={"path": str(path)},
            )
            return
        logger.exception("ClamAV execution failed")
        raise RuntimeError("Virus scan failed") from exc

    if result.returncode == 0:
        return
    if result.returncode == 1:
        logger.warning("Virus detected", extra={"path": str(path)})
        raise RuntimeError("File failed virus scan")

    logger.error(
        "ClamAV returned error",
        extra={"path": str(path), "stderr": result.stderr},
    )
    raise RuntimeError("Virus scan failed")
