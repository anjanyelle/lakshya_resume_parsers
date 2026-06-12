"""
Validation logging utilities for the Resume Parser API.

This module provides centralized logging for validation events including
failed validations, rejected uploads, invalid requests, and other
validation-related events.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)


class ValidationLogger:
    """
    Centralized logger for validation events.
    
    This class provides structured logging for validation events,
    making it easier to track and analyze validation failures.
    """
    
    @staticmethod
    def log_validation_failure(
        field: str,
        value: Any,
        error_message: str,
        error_code: str = "VALIDATION_ERROR",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a validation failure event.
        
        Args:
            field: Field that failed validation
            value: Value that failed validation
            error_message: Error message
            error_code: Error code
            context: Additional context (user_id, endpoint, etc.)
        """
        log_context = {
            "event_type": "validation_failure",
            "field": field,
            "value": str(value) if value is not None else None,
            "error_message": error_message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_context.update(context)
        
        logger.warning(
            f"Validation failed for field: {field}",
            extra=log_context
        )
    
    @staticmethod
    def log_upload_rejection(
        filename: str,
        reason: str,
        error_code: str = "UPLOAD_REJECTED",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a file upload rejection event.
        
        Args:
            filename: Name of the rejected file
            reason: Reason for rejection
            error_code: Error code
            context: Additional context (user_id, file_size, etc.)
        """
        log_context = {
            "event_type": "upload_rejection",
            "filename": filename,
            "reason": reason,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_context.update(context)
        
        logger.warning(
            f"File upload rejected: {filename} - {reason}",
            extra=log_context
        )
    
    @staticmethod
    def log_invalid_request(
        endpoint: str,
        error_message: str,
        error_code: str = "INVALID_REQUEST",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an invalid request event.
        
        Args:
            endpoint: API endpoint
            error_message: Error message
            error_code: Error code
            context: Additional context (user_id, ip_address, etc.)
        """
        log_context = {
            "event_type": "invalid_request",
            "endpoint": endpoint,
            "error_message": error_message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_context.update(context)
        
        logger.warning(
            f"Invalid request to endpoint: {endpoint}",
            extra=log_context
        )
    
    @staticmethod
    def log_virus_detection(
        filename: str,
        virus_name: Optional[str],
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a virus detection event.
        
        Args:
            filename: Name of the infected file
            virus_name: Name of the detected virus
            context: Additional context (user_id, ip_address, etc.)
        """
        log_context = {
            "event_type": "virus_detection",
            "filename": filename,
            "virus_name": virus_name,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "critical"
        }
        
        if context:
            log_context.update(context)
        
        logger.critical(
            f"Virus detected in file: {filename} - {virus_name}",
            extra=log_context
        )
    
    @staticmethod
    def log_rate_limit_exceeded(
        client_id: str,
        endpoint: str,
        limit: int,
        window: int,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a rate limit exceeded event.
        
        Args:
            client_id: Client identifier (IP or user ID)
            endpoint: API endpoint
            limit: Rate limit
            window: Time window
            context: Additional context
        """
        log_context = {
            "event_type": "rate_limit_exceeded",
            "client_id": client_id,
            "endpoint": endpoint,
            "limit": limit,
            "window": window,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_context.update(context)
        
        logger.warning(
            f"Rate limit exceeded for client: {client_id} on endpoint: {endpoint}",
            extra=log_context
        )
    
    @staticmethod
    def log_validation_success(
        validation_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a validation success event.
        
        Args:
            validation_type: Type of validation (file_upload, schema, etc.)
            context: Additional context
        """
        log_context = {
            "event_type": "validation_success",
            "validation_type": validation_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_context.update(context)
        
        logger.info(
            f"Validation passed: {validation_type}",
            extra=log_context
        )


def log_validation_failure(
    field: str,
    value: Any,
    error_message: str,
    error_code: str = "VALIDATION_ERROR",
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to log validation failures.
    
    Args:
        field: Field that failed validation
        value: Value that failed validation
        error_message: Error message
        error_code: Error code
        context: Additional context
    """
    ValidationLogger.log_validation_failure(
        field, value, error_message, error_code, context
    )


def log_upload_rejection(
    filename: str,
    reason: str,
    error_code: str = "UPLOAD_REJECTED",
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to log upload rejections.
    
    Args:
        filename: Name of the rejected file
        reason: Reason for rejection
        error_code: Error code
        context: Additional context
    """
    ValidationLogger.log_upload_rejection(
        filename, reason, error_code, context
    )


def log_invalid_request(
    endpoint: str,
    error_message: str,
    error_code: str = "INVALID_REQUEST",
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to log invalid requests.
    
    Args:
        endpoint: API endpoint
        error_message: Error message
        error_code: Error code
        context: Additional context
    """
    ValidationLogger.log_invalid_request(
        endpoint, error_message, error_code, context
    )


def log_virus_detection(
    filename: str,
    virus_name: Optional[str],
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to log virus detections.
    
    Args:
        filename: Name of the infected file
        virus_name: Name of the detected virus
        context: Additional context
    """
    ValidationLogger.log_virus_detection(
        filename, virus_name, context
    )


def log_rate_limit_exceeded(
    client_id: str,
    endpoint: str,
    limit: int,
    window: int,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to log rate limit exceeded events.
    
    Args:
        client_id: Client identifier
        endpoint: API endpoint
        limit: Rate limit
        window: Time window
        context: Additional context
    """
    ValidationLogger.log_rate_limit_exceeded(
        client_id, endpoint, limit, window, context
    )


def log_validation_success(
    validation_type: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Convenience function to log validation successes.
    
    Args:
        validation_type: Type of validation
        context: Additional context
    """
    ValidationLogger.log_validation_success(
        validation_type, context
    )


def validation_logger(
    validation_type: str = "validation",
    log_success: bool = True,
    log_failure: bool = True
):
    """
    Decorator to add validation logging to functions.
    
    Args:
        validation_type: Type of validation being performed
        log_success: Whether to log successful validations
        log_failure: Whether to log failed validations
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                if log_success:
                    log_validation_success(
                        validation_type=validation_type,
                        context={"function": func.__name__}
                    )
                
                return result
                
            except Exception as exc:
                if log_failure:
                    log_validation_failure(
                        field=func.__name__,
                        value=str(exc),
                        error_message=str(exc),
                        error_code="VALIDATION_ERROR",
                        context={"function": func.__name__, "exception_type": type(exc).__name__}
                    )
                
                raise
        
        return wrapper
    return decorator
