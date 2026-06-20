"""
Error Classification System for Resume Parser
Categorizes and analyzes parsing errors for systematic improvement
"""

import logging
import traceback
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """High-level error categories"""
    EXTRACTION_ERROR = "extraction_error"
    SECTION_SPLITTER_ERROR = "section_splitter_error"
    MODEL_INFERENCE_ERROR = "model_inference_error"
    JSON_FORMATTING_ERROR = "json_formatting_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"


class ErrorType(Enum):
    """Specific error types within categories"""
    
    # Extraction Errors
    TEXT_EXTRACTION_FAILED = "text_extraction_failed"
    OCR_QUALITY_LOW = "ocr_quality_low"
    FILE_CORRUPTED = "file_corrupted"
    UNSUPPORTED_FORMAT = "unsupported_format"
    FILE_TOO_LARGE = "file_too_large"
    EMPTY_FILE = "empty_file"
    
    # Section Splitter Errors
    SECTION_DETECTION_FAILED = "section_detection_failed"
    SECTION_BOUNDARY_ERROR = "section_boundary_error"
    MISSING_CRITICAL_SECTION = "missing_critical_section"
    SECTION_OVERLAP = "section_overlap"
    
    # Model Inference Errors
    MODEL_LOADING_FAILED = "model_loading_failed"
    INFERENCE_TIMEOUT = "inference_timeout"
    MODEL_OUTPUT_MALFORMED = "model_output_malformed"
    CONFIDENCE_TOO_LOW = "confidence_too_low"
    MODEL_NOT_AVAILABLE = "model_not_available"
    API_QUOTA_EXCEEDED = "api_quota_exceeded"
    API_RATE_LIMIT = "api_rate_limit"
    
    # JSON Formatting Errors
    JSON_PARSE_FAILED = "json_parse_failed"
    SCHEMA_VALIDATION_FAILED = "schema_validation_failed"
    DATA_TYPE_MISMATCH = "data_type_mismatch"
    REQUIRED_FIELD_MISSING = "required_field_missing"
    INVALID_JSON_STRUCTURE = "invalid_json_structure"
    
    # Validation Errors
    ENTITY_VALIDATION_FAILED = "entity_validation_failed"
    DATE_VALIDATION_FAILED = "date_validation_failed"
    EMAIL_VALIDATION_FAILED = "email_validation_failed"
    PHONE_VALIDATION_FAILED = "phone_validation_failed"
    URL_VALIDATION_FAILED = "url_validation_failed"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    
    # System Errors
    SYSTEM_ERROR = "system_error"
    MEMORY_ERROR = "memory_error"
    DISK_SPACE_ERROR = "disk_space_error"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    CONFIGURATION_ERROR = "configuration_error"
    PERMISSION_ERROR = "permission_error"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Non-critical, can continue
    MEDIUM = "medium"     # May affect quality but not critical
    HIGH = "high"         # Significant impact, needs attention
    CRITICAL = "critical" # Pipeline failure, immediate attention required


class ErrorClassifier:
    """
    Classifies parsing errors into categories and provides recovery suggestions.
    """
    
    # Error type to category mapping
    ERROR_TYPE_MAPPING = {
        # Extraction Errors
        ErrorType.TEXT_EXTRACTION_FAILED: ErrorCategory.EXTRACTION_ERROR,
        ErrorType.OCR_QUALITY_LOW: ErrorCategory.EXTRACTION_ERROR,
        ErrorType.FILE_CORRUPTED: ErrorCategory.EXTRACTION_ERROR,
        ErrorType.UNSUPPORTED_FORMAT: ErrorCategory.EXTRACTION_ERROR,
        ErrorType.FILE_TOO_LARGE: ErrorCategory.EXTRACTION_ERROR,
        ErrorType.EMPTY_FILE: ErrorCategory.EXTRACTION_ERROR,
        
        # Section Splitter Errors
        ErrorType.SECTION_DETECTION_FAILED: ErrorCategory.SECTION_SPLITTER_ERROR,
        ErrorType.SECTION_BOUNDARY_ERROR: ErrorCategory.SECTION_SPLITTER_ERROR,
        ErrorType.MISSING_CRITICAL_SECTION: ErrorCategory.SECTION_SPLITTER_ERROR,
        ErrorType.SECTION_OVERLAP: ErrorCategory.SECTION_SPLITTER_ERROR,
        
        # Model Inference Errors
        ErrorType.MODEL_LOADING_FAILED: ErrorCategory.MODEL_INFERENCE_ERROR,
        ErrorType.INFERENCE_TIMEOUT: ErrorCategory.MODEL_INFERENCE_ERROR,
        ErrorType.MODEL_OUTPUT_MALFORMED: ErrorCategory.MODEL_INFERENCE_ERROR,
        ErrorType.CONFIDENCE_TOO_LOW: ErrorCategory.MODEL_INFERENCE_ERROR,
        ErrorType.MODEL_NOT_AVAILABLE: ErrorCategory.MODEL_INFERENCE_ERROR,
        ErrorType.API_QUOTA_EXCEEDED: ErrorCategory.MODEL_INFERENCE_ERROR,
        ErrorType.API_RATE_LIMIT: ErrorCategory.MODEL_INFERENCE_ERROR,
        
        # JSON Formatting Errors
        ErrorType.JSON_PARSE_FAILED: ErrorCategory.JSON_FORMATTING_ERROR,
        ErrorType.SCHEMA_VALIDATION_FAILED: ErrorCategory.JSON_FORMATTING_ERROR,
        ErrorType.DATA_TYPE_MISMATCH: ErrorCategory.JSON_FORMATTING_ERROR,
        ErrorType.REQUIRED_FIELD_MISSING: ErrorCategory.JSON_FORMATTING_ERROR,
        ErrorType.INVALID_JSON_STRUCTURE: ErrorCategory.JSON_FORMATTING_ERROR,
        
        # Validation Errors
        ErrorType.ENTITY_VALIDATION_FAILED: ErrorCategory.VALIDATION_ERROR,
        ErrorType.DATE_VALIDATION_FAILED: ErrorCategory.VALIDATION_ERROR,
        ErrorType.EMAIL_VALIDATION_FAILED: ErrorCategory.VALIDATION_ERROR,
        ErrorType.PHONE_VALIDATION_FAILED: ErrorCategory.VALIDATION_ERROR,
        ErrorType.URL_VALIDATION_FAILED: ErrorCategory.VALIDATION_ERROR,
        ErrorType.BUSINESS_RULE_VIOLATION: ErrorCategory.VALIDATION_ERROR,
        
        # System Errors
        ErrorType.MEMORY_ERROR: ErrorCategory.SYSTEM_ERROR,
        ErrorType.DISK_SPACE_ERROR: ErrorCategory.SYSTEM_ERROR,
        ErrorType.NETWORK_ERROR: ErrorCategory.SYSTEM_ERROR,
        ErrorType.DATABASE_ERROR: ErrorCategory.SYSTEM_ERROR,
        ErrorType.CONFIGURATION_ERROR: ErrorCategory.SYSTEM_ERROR,
        ErrorType.PERMISSION_ERROR: ErrorCategory.SYSTEM_ERROR,
    }
    
    # Default severity for each error type
    ERROR_SEVERITY_MAPPING = {
        # Critical errors
        ErrorType.MODEL_LOADING_FAILED: ErrorSeverity.CRITICAL,
        ErrorType.MEMORY_ERROR: ErrorSeverity.CRITICAL,
        ErrorType.DISK_SPACE_ERROR: ErrorSeverity.CRITICAL,
        ErrorType.DATABASE_ERROR: ErrorSeverity.CRITICAL,
        
        # High severity
        ErrorType.TEXT_EXTRACTION_FAILED: ErrorSeverity.HIGH,
        ErrorType.MODEL_NOT_AVAILABLE: ErrorSeverity.HIGH,
        ErrorType.API_QUOTA_EXCEEDED: ErrorSeverity.HIGH,
        ErrorType.JSON_PARSE_FAILED: ErrorSeverity.HIGH,
        
        # Medium severity
        ErrorType.OCR_QUALITY_LOW: ErrorSeverity.MEDIUM,
        ErrorType.SECTION_DETECTION_FAILED: ErrorSeverity.MEDIUM,
        ErrorType.MISSING_CRITICAL_SECTION: ErrorSeverity.MEDIUM,
        ErrorType.SCHEMA_VALIDATION_FAILED: ErrorSeverity.MEDIUM,
        ErrorType.INFERENCE_TIMEOUT: ErrorSeverity.MEDIUM,
        
        # Low severity
        ErrorType.FILE_TOO_LARGE: ErrorSeverity.LOW,
        ErrorType.SECTION_BOUNDARY_ERROR: ErrorSeverity.LOW,
        ErrorType.CONFIDENCE_TOO_LOW: ErrorSeverity.LOW,
        ErrorType.DATE_VALIDATION_FAILED: ErrorSeverity.LOW,
    }
    
    # Recovery strategies for each error type
    RECOVERY_STRATEGIES = {
        ErrorType.TEXT_EXTRACTION_FAILED: [
            "Retry with OCR forced",
            "Try alternative extraction method",
            "Request manual intervention"
        ],
        ErrorType.OCR_QUALITY_LOW: [
            "Enhance image preprocessing",
            "Try multiple OCR engines",
            "Request better quality scan"
        ],
        ErrorType.SECTION_DETECTION_FAILED: [
            "Use rule-based fallback",
            "Try alternative section splitter",
            "Process entire document as single section"
        ],
        ErrorType.MISSING_CRITICAL_SECTION: [
            "Use heuristic extraction",
            "Mark for manual review",
            "Infer from other sections"
        ],
        ErrorType.MODEL_LOADING_FAILED: [
            "Restart model service",
            "Check model file integrity",
            "Use fallback model"
        ],
        ErrorType.INFERENCE_TIMEOUT: [
            "Increase timeout threshold",
            "Reduce input size",
            "Use lighter model"
        ],
        ErrorType.JSON_PARSE_FAILED: [
            "Retry with cleaned output",
            "Use alternative parsing method",
            "Implement error recovery"
        ],
        ErrorType.SCHEMA_VALIDATION_FAILED: [
            "Apply schema transformation",
            "Use default values for missing fields",
            "Mark for manual review"
        ],
        ErrorType.API_QUOTA_EXCEEDED: [
            "Switch to alternative API provider",
            "Implement queue system",
            "Use cached results"
        ],
        ErrorType.MEMORY_ERROR: [
            "Reduce batch size",
            "Free memory resources",
            "Process in chunks"
        ],
    }
    
    def __init__(self):
        """Initialize error classifier."""
        self.error_log = []
        
    def classify_error(self, exception: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify an exception into error type and category.
        
        Args:
            exception: The exception to classify
            context: Additional context about when/where error occurred
            
        Returns:
            Dictionary with classification results
        """
        error_type = self._determine_error_type(exception, context)
        error_category = self.ERROR_TYPE_MAPPING.get(error_type, ErrorCategory.SYSTEM_ERROR)
        severity = self.ERROR_SEVERITY_MAPPING.get(error_type, ErrorSeverity.MEDIUM)
        
        error_info = {
            'error_id': str(uuid.uuid4()),
            'error_type': error_type.value,
            'error_category': error_category.value,
            'severity': severity.value,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'stack_trace': traceback.format_exc(),
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
            'recovery_strategies': self.RECOVERY_STRATEGIES.get(error_type, []),
            'can_recover': len(self.RECOVERY_STRATEGIES.get(error_type, [])) > 0
        }
        
        self.error_log.append(error_info)
        logger.error(f"🔍 Error Classified: {error_info}")
        
        return error_info
        
    def _determine_error_type(self, exception: Exception, context: Dict[str, Any] = None) -> ErrorType:
        """
        Determine the specific error type from exception and context.
        
        Args:
            exception: The exception
            context: Additional context
            
        Returns:
            ErrorType enum value
        """
        exception_type = type(exception).__name__
        exception_message = str(exception).lower()
        context = context or {}
        
        # Check context for pipeline stage
        pipeline_stage = context.get('stage', '').lower()
        
        # Memory errors
        if 'memory' in exception_message or 'ram' in exception_message:
            return ErrorType.MEMORY_ERROR
            
        # Disk space errors
        if 'disk' in exception_message or 'space' in exception_message:
            return ErrorType.DISK_SPACE_ERROR
            
        # Network errors
        if 'network' in exception_message or 'connection' in exception_message:
            return ErrorType.NETWORK_ERROR
            
        # Database errors
        if 'database' in exception_message or 'sql' in exception_message:
            return ErrorType.DATABASE_ERROR
            
        # File-related errors
        if 'file' in exception_message or 'io' in exception_type.lower():
            if 'corrupt' in exception_message or 'invalid' in exception_message:
                return ErrorType.FILE_CORRUPTED
            elif 'format' in exception_message or 'unsupported' in exception_message:
                return ErrorType.UNSUPPORTED_FORMAT
            elif 'size' in exception_message or 'large' in exception_message:
                return ErrorType.FILE_TOO_LARGE
            elif 'empty' in exception_message or 'no data' in exception_message:
                return ErrorType.EMPTY_FILE
                
        # JSON parsing errors
        if 'json' in exception_type.lower() or 'json' in exception_message:
            if 'decode' in exception_message or 'parse' in exception_message:
                return ErrorType.JSON_PARSE_FAILED
            elif 'schema' in exception_message or 'validation' in exception_message:
                return ErrorType.SCHEMA_VALIDATION_FAILED
                
        # Timeout errors
        if 'timeout' in exception_message or 'time' in exception_type.lower():
            if pipeline_stage in ['model', 'inference', 'ai']:
                return ErrorType.INFERENCE_TIMEOUT
                
        # API errors
        if 'api' in exception_message or 'quota' in exception_message or 'limit' in exception_message:
            if 'quota' in exception_message:
                return ErrorType.API_QUOTA_EXCEEDED
            elif 'rate' in exception_message:
                return ErrorType.API_RATE_LIMIT
                
        # Model-specific errors
        if pipeline_stage in ['model', 'inference', 'deberta', 'ai']:
            if 'load' in exception_message:
                return ErrorType.MODEL_LOADING_FAILED
            elif 'available' in exception_message:
                return ErrorType.MODEL_NOT_AVAILABLE
            elif 'output' in exception_message or 'malformed' in exception_message:
                return ErrorType.MODEL_OUTPUT_MALFORMED
                
        # Section splitter errors
        if pipeline_stage in ['section', 'splitter']:
            if 'detect' in exception_message or 'find' in exception_message:
                return ErrorType.SECTION_DETECTION_FAILED
            elif 'boundary' in exception_message or 'overlap' in exception_message:
                return ErrorType.SECTION_BOUNDARY_ERROR
            elif 'missing' in exception_message or 'critical' in exception_message:
                return ErrorType.MISSING_CRITICAL_SECTION
                
        # Validation errors
        if 'validation' in exception_message or 'invalid' in exception_message:
            if 'email' in exception_message:
                return ErrorType.EMAIL_VALIDATION_FAILED
            elif 'phone' in exception_message:
                return ErrorType.PHONE_VALIDATION_FAILED
            elif 'date' in exception_message:
                return ErrorType.DATE_VALIDATION_FAILED
            elif 'url' in exception_message:
                return ErrorType.URL_VALIDATION_FAILED
            elif 'entity' in exception_message:
                return ErrorType.ENTITY_VALIDATION_FAILED
                
        # Default to system error if no specific match
        return ErrorType.SYSTEM_ERROR
        
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about classified errors.
        
        Returns:
            Dictionary with error statistics
        """
        if not self.error_log:
            return {
                'total_errors': 0,
                'by_category': {},
                'by_type': {},
                'by_severity': {}
            }
            
        # Count by category
        by_category = {}
        for error in self.error_log:
            category = error['error_category']
            by_category[category] = by_category.get(category, 0) + 1
            
        # Count by type
        by_type = {}
        for error in self.error_log:
            error_type = error['error_type']
            by_type[error_type] = by_type.get(error_type, 0) + 1
            
        # Count by severity
        by_severity = {}
        for error in self.error_log:
            severity = error['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
        return {
            'total_errors': len(self.error_log),
            'by_category': by_category,
            'by_type': by_type,
            'by_severity': by_severity,
            'recoverable_errors': sum(1 for e in self.error_log if e['can_recover']),
            'non_recoverable_errors': sum(1 for e in self.error_log if not e['can_recover'])
        }
        
    def get_common_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most common error types.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of common error types with counts
        """
        error_counts = {}
        for error in self.error_log:
            error_type = error['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'error_type': error_type,
                'count': count,
                'percentage': (count / len(self.error_log)) * 100 if self.error_log else 0
            }
            for error_type, count in sorted_errors[:limit]
        ]
        
    def get_recovery_success_rate(self) -> Dict[str, Any]:
        """
        Calculate recovery success rate for different error types.
        
        Returns:
            Dictionary with recovery statistics
        """
        recovery_stats = {}
        
        for error in self.error_log:
            error_type = error['error_type']
            if error_type not in recovery_stats:
                recovery_stats[error_type] = {
                    'total': 0,
                    'recovered': 0,
                    'failed': 0
                }
                
            recovery_stats[error_type]['total'] += 1
            if error.get('recovery_successful'):
                recovery_stats[error_type]['recovered'] += 1
            else:
                recovery_stats[error_type]['failed'] += 1
                
        # Calculate success rates
        for error_type, stats in recovery_stats.items():
            if stats['total'] > 0:
                stats['success_rate'] = (stats['recovered'] / stats['total']) * 100
            else:
                stats['success_rate'] = 0
                
        return recovery_stats
        
    def clear_error_log(self):
        """Clear the error log."""
        self.error_log.clear()
        
    def export_error_log(self, output_path: str = None) -> str:
        """
        Export error log to JSON file.
        
        Args:
            output_path: Path to save error log
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = f"error_log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'total_errors': len(self.error_log),
            'statistics': self.get_error_statistics(),
            'errors': self.error_log
        }
        
        with open(output_path, 'w') as f:
            import json
            json.dump(export_data, f, indent=2)
            
        logger.info(f"📁 Error log exported to {output_path}")
        return output_path


# Convenience function for quick error classification
def classify_error(exception: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Quick function to classify an error.
    
    Args:
        exception: Exception to classify
        context: Additional context
        
    Returns:
        Classification result
    """
    classifier = ErrorClassifier()
    return classifier.classify_error(exception, context)