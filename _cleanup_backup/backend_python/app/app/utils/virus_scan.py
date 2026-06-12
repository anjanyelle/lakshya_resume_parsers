"""
Virus scan utilities for the Resume Parser API.

This module provides ClamAV integration for scanning uploaded files
to ensure they are safe before processing.
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class VirusScanError(Exception):
    """Custom exception for virus scan errors."""
    
    def __init__(self, message: str, error_code: str = "VIRUS_SCAN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class VirusDetectedError(Exception):
    """Exception raised when a virus is detected in a file."""
    
    def __init__(self, message: str, virus_name: Optional[str] = None):
        self.message = message
        self.virus_name = virus_name
        super().__init__(self.message)


def scan_file(
    path: Path,
    enabled: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Scan a file for viruses using ClamAV.
    
    Args:
        path: Path to the file to scan
        enabled: Override the CLAMAV_ENABLED setting (optional)
        
    Returns:
        Dictionary with scan results
        
    Raises:
        VirusScanError: If scan fails
        VirusDetectedError: If virus is detected
    """
    settings = get_settings()
    
    # Check if ClamAV is enabled
    clamav_enabled = enabled if enabled is not None else settings.CLAMAV_ENABLED
    if not clamav_enabled:
        logger.info(
            "ClamAV scanning is disabled; skipping virus scan",
            extra={"path": str(path)}
        )
        return {
            "scanned": False,
            "reason": "ClamAV scanning is disabled",
            "safe": True,
        }
    
    # Check if file exists
    if not path.exists():
        logger.error(f"File not found for virus scan: {path}")
        raise VirusScanError(
            f"File not found: {path}",
            error_code="FILE_NOT_FOUND"
        )
    
    # Check if file is readable
    if not path.is_file():
        logger.error(f"Path is not a file: {path}")
        raise VirusScanError(
            f"Path is not a file: {path}",
            error_code="NOT_A_FILE"
        )
    
    logger.info(f"Starting virus scan for file: {path}")
    
    try:
        # Run ClamAV scan
        result = subprocess.run(
            [settings.CLAMAV_PATH, "--no-summary", str(path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
    except OSError as exc:
        # ClamAV not available
        if settings.ENVIRONMENT.lower() == "development":
            logger.warning(
                "ClamAV not available; skipping scan in development",
                extra={"path": str(path), "error": str(exc)}
            )
            return {
                "scanned": False,
                "reason": "ClamAV not available in development",
                "safe": True,
            }
        logger.exception("ClamAV execution failed")
        raise VirusScanError(
            "Virus scan service unavailable",
            error_code="CLAMAV_UNAVAILABLE"
        ) from exc
    except subprocess.TimeoutExpired:
        logger.error(f"Virus scan timed out for file: {path}")
        raise VirusScanError(
            "Virus scan timed out",
            error_code="SCAN_TIMEOUT"
        )
    
    # Parse ClamAV return codes
    # 0: No virus found
    # 1: Virus found
    # 2: Error
    if result.returncode == 0:
        logger.info(f"Virus scan passed for file: {path}")
        return {
            "scanned": True,
            "safe": True,
            "message": "No virus detected",
        }
    elif result.returncode == 1:
        # Virus detected
        virus_name = _extract_virus_name(result.stdout)
        logger.warning(
            f"Virus detected in file: {path}",
            extra={"virus_name": virus_name, "path": str(path)}
        )
        raise VirusDetectedError(
            f"File contains a virus and has been rejected",
            virus_name=virus_name
        )
    else:
        # Error occurred
        logger.error(
            "ClamAV returned error",
            extra={"path": str(path), "returncode": result.returncode, "stderr": result.stderr}
        )
        raise VirusScanError(
            "Virus scan failed",
            error_code="SCAN_ERROR"
        )


def _extract_virus_name(output: str) -> Optional[str]:
    """
    Extract virus name from ClamAV output.
    
    Args:
        output: ClamAV stdout output
        
    Returns:
        Virus name if found, None otherwise
    """
    try:
        # ClamAV output format: "path: FOUND" or "path: <virus_name> FOUND"
        lines = output.split('\n')
        for line in lines:
            if 'FOUND' in line:
                parts = line.split()
                if len(parts) >= 2:
                    # Try to extract virus name
                    for i, part in enumerate(parts):
                        if part == 'FOUND' and i > 0:
                            potential_name = ' '.join(parts[:i])
                            if potential_name.endswith(':'):
                                potential_name = potential_name[:-1]
                            return potential_name
        return None
    except Exception:
        return None


def is_clamav_available() -> bool:
    """
    Check if ClamAV is available and configured.
    
    Returns:
        True if ClamAV is available, False otherwise
    """
    settings = get_settings()
    
    if not settings.CLAMAV_ENABLED:
        return False
    
    try:
        result = subprocess.run(
            [settings.CLAMAV_PATH, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False
