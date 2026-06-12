"""
Standardized error responses for the Resume Parser API.

This module provides consistent error response formats across all endpoints,
ensuring clients receive clear, actionable error messages with proper structure.
"""

import logging
from typing import Any, Dict, Optional, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ValidationErrorDetail(BaseModel):
    """Detail for a specific validation error."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    error_code: str = Field(default="VALIDATION_ERROR", description="Error code")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = Field(default=False, description="Always false for error responses")
    message: str = Field(..., description="Human-readable error message")
    error_code: str = Field(default="ERROR", description="Machine-readable error code")
    errors: Optional[Dict[str, str]] = Field(default=None, description="Field-specific errors")
    validation_errors: Optional[List[ValidationErrorDetail]] = Field(
        default=None, 
        description="Detailed validation errors"
    )
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class ErrorCodes:
    """Standard error codes for the API."""
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_EMAIL = "INVALID_EMAIL"
    INVALID_PHONE = "INVALID_PHONE"
    INVALID_URL = "INVALID_URL"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
    MAGIC_BYTES_MISMATCH = "MAGIC_BYTES_MISMATCH"
    MISSING_EXTENSION = "MISSING_EXTENSION"
    
    # File errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    VIRUS_DETECTED = "VIRUS_DETECTED"
    VIRUS_SCAN_FAILED = "VIRUS_SCAN_FAILED"
    
    # Authentication errors
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # Authorization errors
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # Server errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    
    # Parsing errors
    PARSING_FAILED = "PARSING_FAILED"
    PARSING_TIMEOUT = "PARSING_TIMEOUT"
    UNSUPPORTED_FILE_FORMAT = "UNSUPPORTED_FILE_FORMAT"


def create_error_response(
    message: str,
    error_code: str = ErrorCodes.VALIDATION_ERROR,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[Dict[str, str]] = None,
    validation_errors: Optional[List[ValidationErrorDetail]] = None,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        errors: Field-specific errors (key: field name, value: error message)
        validation_errors: Detailed validation errors
        details: Additional error details
        
    Returns:
        JSONResponse with standardized error format
    """
    error_response = ErrorResponse(
        message=message,
        error_code=error_code,
        errors=errors,
        validation_errors=validation_errors,
        details=details
    )
    
    logger.warning(
        f"API Error: {error_code} - {message}",
        extra={
            "error_code": error_code,
            "status_code": status_code,
            "errors": errors,
            "details": details
        }
    )
    
    return JSONResponse(
        content=error_response.model_dump(),
        status_code=status_code
    )


def validation_error_response(
    message: str = "Validation failed",
    errors: Optional[Dict[str, str]] = None,
    validation_errors: Optional[List[ValidationErrorDetail]] = None,
) -> JSONResponse:
    """
    Create a validation error response (400 Bad Request).
    
    Args:
        message: Human-readable error message
        errors: Field-specific errors
        validation_errors: Detailed validation errors
        
    Returns:
        JSONResponse with validation error format
    """
    return create_error_response(
        message=message,
        error_code=ErrorCodes.VALIDATION_ERROR,
        status_code=status.HTTP_400_BAD_REQUEST,
        errors=errors,
        validation_errors=validation_errors
    )


def unauthorized_response(
    message: str = "Authentication required",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create an unauthorized error response (401 Unauthorized).
    
    Args:
        message: Human-readable error message
        details: Additional error details
        
    Returns:
        JSONResponse with unauthorized error format
    """
    return create_error_response(
        message=message,
        error_code=ErrorCodes.UNAUTHORIZED,
        status_code=status.HTTP_401_UNAUTHORIZED,
        details=details
    )


def forbidden_response(
    message: str = "Access denied",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a forbidden error response (403 Forbidden).
    
    Args:
        message: Human-readable error message
        details: Additional error details
        
    Returns:
        JSONResponse with forbidden error format
    """
    return create_error_response(
        message=message,
        error_code=ErrorCodes.FORBIDDEN,
        status_code=status.HTTP_403_FORBIDDEN,
        details=details
    )


def not_found_response(
    message: str = "Resource not found",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a not found error response (404 Not Found).
    
    Args:
        message: Human-readable error message
        details: Additional error details
        
    Returns:
        JSONResponse with not found error format
    """
    return create_error_response(
        message=message,
        error_code=ErrorCodes.RESOURCE_NOT_FOUND,
        status_code=status.HTTP_404_NOT_FOUND,
        details=details
    )


def conflict_response(
    message: str = "Resource conflict",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a conflict error response (409 Conflict).
    
    Args:
        message: Human-readable error message
        details: Additional error details
        
    Returns:
        JSONResponse with conflict error format
    """
    return create_error_response(
        message=message,
        error_code=ErrorCodes.RESOURCE_CONFLICT,
        status_code=status.HTTP_409_CONFLICT,
        details=details
    )


def rate_limit_response(
    message: str = "Rate limit exceeded",
    retry_after: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a rate limit error response (429 Too Many Requests).
    
    Args:
        message: Human-readable error message
        retry_after: Seconds until retry is allowed
        details: Additional error details
        
    Returns:
        JSONResponse with rate limit error format
    """
    if details is None:
        details = {}
    if retry_after is not None:
        details["retry_after"] = retry_after
    
    response = create_error_response(
        message=message,
        error_code=ErrorCodes.RATE_LIMIT_EXCEEDED,
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        details=details
    )
    
    if retry_after is not None:
        response.headers["Retry-After"] = str(retry_after)
    
    return response


def server_error_response(
    message: str = "Internal server error",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a server error response (500 Internal Server Error).
    
    Args:
        message: Human-readable error message
        details: Additional error details
        
    Returns:
        JSONResponse with server error format
    """
    return create_error_response(
        message=message,
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details
    )


def handle_pydantic_validation_error(exc: Exception) -> JSONResponse:
    """
    Handle Pydantic validation errors and convert to standard format.
    
    Args:
        exc: Pydantic validation exception
        
    Returns:
        JSONResponse with validation error format
    """
    try:
        # Try to extract validation errors from Pydantic exception
        if hasattr(exc, 'errors'):
            pydantic_errors = exc.errors()
            field_errors: Dict[str, str] = {}
            validation_errors_list: List[ValidationErrorDetail] = []
            
            for error in pydantic_errors:
                field = '.'.join(str(loc) for loc in error['loc'] if loc != 'body')
                message = error['msg']
                error_type = error['type']
                
                field_errors[field] = message
                validation_errors_list.append(
                    ValidationErrorDetail(
                        field=field,
                        message=message,
                        error_code=error_type.upper()
                    )
                )
            
            return validation_error_response(
                message="Validation failed",
                errors=field_errors,
                validation_errors=validation_errors_list
            )
    except Exception:
        pass
    
    # Fallback to generic error
    return validation_error_response(
        message=str(exc) if str(exc) else "Validation failed"
    )


def handle_file_validation_error(exc: Exception) -> JSONResponse:
    """
    Handle file validation errors and convert to standard format.
    
    Args:
        exc: File validation exception
        
    Returns:
        JSONResponse with file validation error format
    """
    error_message = str(exc)
    
    if "size" in error_message.lower():
        return validation_error_response(
            message=error_message,
            errors={"file": error_message},
            validation_errors=[
                ValidationErrorDetail(
                    field="file",
                    message=error_message,
                    error_code=ErrorCodes.FILE_SIZE_EXCEEDED
                )
            ]
        )
    elif "extension" in error_message.lower() or "type" in error_message.lower():
        return validation_error_response(
            message=error_message,
            errors={"file": error_message},
            validation_errors=[
                ValidationErrorDetail(
                    field="file",
                    message=error_message,
                    error_code=ErrorCodes.INVALID_FILE_TYPE
                )
            ]
        )
    elif "magic" in error_message.lower():
        return validation_error_response(
            message=error_message,
            errors={"file": error_message},
            validation_errors=[
                ValidationErrorDetail(
                    field="file",
                    message=error_message,
                    error_code=ErrorCodes.MAGIC_BYTES_MISMATCH
                )
            ]
        )
    
    return validation_error_response(
        message=error_message,
        errors={"file": error_message}
    )


def handle_virus_scan_error(exc: Exception) -> JSONResponse:
    """
    Handle virus scan errors and convert to standard format.
    
    Args:
        exc: Virus scan exception
        
    Returns:
        JSONResponse with virus scan error format
    """
    from app.utils.virus_scan import VirusDetectedError, VirusScanError
    
    if isinstance(exc, VirusDetectedError):
        return create_error_response(
            message=exc.message,
            error_code=ErrorCodes.VIRUS_DETECTED,
            status_code=status.HTTP_403_FORBIDDEN,
            details={"virus_name": exc.virus_name}
        )
    elif isinstance(exc, VirusScanError):
        return create_error_response(
            message=exc.message,
            error_code=exc.error_code,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": exc.error_code}
        )
    
    return server_error_response(
        message="Virus scan failed",
        details={"error": str(exc)}
    )
