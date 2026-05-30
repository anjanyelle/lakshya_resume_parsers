"""
File validation utilities for the Resume Parser API.

This module provides comprehensive file validation including:
- File type validation using magic bytes
- File size validation
- MIME type validation
- Allowed file type enforcement
"""

import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Maximum file size: 10MB (10 * 1024 * 1024 bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Allowed file types for resume uploads
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".rtf"}

# Magic byte signatures for file type detection
MAGIC_HEADERS = {
    "pdf": [b"%PDF"],
    "docx": [b"PK\x03\x04"],
    "doc": [b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"],
    "rtf": [b"{\\rtf"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xFF\xD8\xFF"],
    "jpeg": [b"\xFF\xD8\xFF"],
    "txt": [],
}


class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    
    def __init__(self, message: str, error_code: str = "FILE_VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


def detect_file_type(data: bytes) -> Optional[str]:
    """
    Detect file type using magic bytes.
    
    Args:
        data: File content as bytes
        
    Returns:
        Detected file type or None if not recognized
    """
    for file_type, signatures in MAGIC_HEADERS.items():
        for sig in signatures:
            if data.startswith(sig):
                return file_type
    return None


def validate_magic(data: bytes, extension: str) -> bool:
    """
    Validate file magic bytes match the expected extension.
    
    Args:
        data: File content as bytes
        extension: File extension (without dot)
        
    Returns:
        True if magic bytes match, False otherwise
    """
    if extension == "txt":
        return True
    detected = detect_file_type(data)
    if extension == "docx" and detected == "docx":
        return True
    if extension == "doc" and detected == "doc":
        return True
    if extension == "pdf" and detected == "pdf":
        return True
    if extension == "rtf" and data.startswith(b"{\\rtf"):
        return True
    if extension in {"png", "jpg", "jpeg"} and detected in {"png", "jpg", "jpeg"}:
        return True
    return False


def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE) -> None:
    """
    Validate file size does not exceed maximum limit.
    
    Args:
        file_size: Size of the file in bytes
        max_size: Maximum allowed file size in bytes
        
    Raises:
        FileValidationError: If file size exceeds limit
    """
    if file_size > max_size:
        size_mb = file_size / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        logger.warning(
            f"File size {size_mb:.2f}MB exceeds maximum {max_mb:.2f}MB"
        )
        raise FileValidationError(
            f"File size {size_mb:.2f}MB exceeds maximum allowed size of {max_mb:.2f}MB",
            error_code="FILE_SIZE_EXCEEDED"
        )


def validate_file_extension(filename: str, allowed_extensions: set = None) -> str:
    """
    Validate file extension is allowed.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (with dots)
        
    Returns:
        Validated file extension (with dot)
        
    Raises:
        FileValidationError: If extension is not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_RESUME_EXTENSIONS
    
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    
    if not extension:
        logger.warning(f"File has no extension: {filename}")
        raise FileValidationError(
            "File must have an extension",
            error_code="MISSING_EXTENSION"
        )
    
    if extension not in allowed_extensions:
        logger.warning(
            f"File extension {extension} not in allowed extensions: {allowed_extensions}"
        )
        raise FileValidationError(
            f"Unsupported file type '{extension}'. "
            f"Allowed types: {', '.join(allowed_extensions)}",
            error_code="UNSUPPORTED_FILE_TYPE"
        )
    
    return extension


def validate_file_content(
    data: bytes,
    filename: str,
    max_size: int = MAX_FILE_SIZE
) -> dict:
    """
    Comprehensive file validation including size, extension, and magic bytes.
    
    Args:
        data: File content as bytes
        filename: Name of the file
        max_size: Maximum allowed file size in bytes
        
    Returns:
        Dictionary with validation results
        
    Raises:
        FileValidationError: If any validation fails
    """
    # Validate file size
    validate_file_size(len(data), max_size)
    
    # Validate file extension
    extension = validate_file_extension(filename)
    
    # Validate magic bytes (skip for txt files)
    if extension != ".txt":
        extension_without_dot = extension[1:]  # Remove the dot
        if not validate_magic(data, extension_without_dot):
            logger.warning(
                f"Magic bytes do not match extension for file: {filename}"
            )
            raise FileValidationError(
                f"File content does not match the expected format for '{extension}' files. "
                "The file may be corrupted or have an incorrect extension.",
                error_code="MAGIC_BYTES_MISMATCH"
            )
    
    detected_type = detect_file_type(data) if extension != ".txt" else "txt"
    
    logger.info(
        f"File validation passed: {filename}, "
        f"size={len(data)} bytes, type={detected_type or 'unknown'}"
    )
    
    return {
        "valid": True,
        "extension": extension,
        "detected_type": detected_type,
        "size": len(data),
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other security issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name
    
    # Remove null bytes
    filename = filename.replace("\x00", "")
    
    # Limit filename length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename
