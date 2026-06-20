"""
Debug Logging Pipeline for Resume Parser Evaluation Framework
Captures all intermediate results for comprehensive debugging and analysis
"""

import json
import logging
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class DebugLogger:
    """
    Comprehensive debug logging system that captures all intermediate
    results in the resume parsing pipeline for evaluation and debugging.
    """
    
    def __init__(self, request_id: str = None, enabled: bool = True):
        """
        Initialize debug logger for a specific parsing request.
        
        Args:
            request_id: Unique identifier for the parsing request
            enabled: Whether debug logging is enabled
        """
        self.request_id = request_id or str(uuid.uuid4())
        self.enabled = enabled
        self.logs = []
        self.start_time = time.time()
        self.pipeline_stages = []
        
    def log_input(self, stage: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """
        Log input data at any pipeline stage.
        
        Args:
            stage: Pipeline stage name (e.g., 'text_extraction', 'section_splitting')
            data: Input data to log
            metadata: Additional metadata (file size, format, etc.)
        """
        if not self.enabled:
            return
            
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': self.request_id,
            'stage': stage,
            'log_type': 'input',
            'data': self._sanitize_data(data),
            'metadata': metadata or {},
            'elapsed_time_ms': (time.time() - self.start_time) * 1000
        }
        
        self.logs.append(log_entry)
        logger.debug(f"📥 INPUT LOG [{stage}]: {json.dumps(log_entry, indent=2)}")
        
    def log_processing(self, stage: str, operation: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """
        Log intermediate processing results.
        
        Args:
            stage: Pipeline stage name
            operation: Specific operation being performed
            data: Processing data
            metadata: Additional metadata
        """
        if not self.enabled:
            return
            
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': self.request_id,
            'stage': stage,
            'operation': operation,
            'log_type': 'processing',
            'data': self._sanitize_data(data),
            'metadata': metadata or {},
            'elapsed_time_ms': (time.time() - self.start_time) * 1000
        }
        
        self.logs.append(log_entry)
        logger.debug(f"⚙️  PROCESSING LOG [{stage} - {operation}]: {json.dumps(log_entry, indent=2)}")
        
    def log_output(self, stage: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """
        Log output data from any pipeline stage.
        
        Args:
            stage: Pipeline stage name
            data: Output data to log
            metadata: Additional metadata
        """
        if not self.enabled:
            return
            
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': self.request_id,
            'stage': stage,
            'log_type': 'output',
            'data': self._sanitize_data(data),
            'metadata': metadata or {},
            'elapsed_time_ms': (time.time() - self.start_time) * 1000
        }
        
        self.logs.append(log_entry)
        logger.debug(f"📤 OUTPUT LOG [{stage}]: {json.dumps(log_entry, indent=2)}")
        
    def log_error(self, stage: str, error: Exception, context: Dict[str, Any] = None):
        """
        Log error with full context for debugging.
        
        Args:
            stage: Pipeline stage where error occurred
            error: Exception object
            context: Additional context data
        """
        if not self.enabled:
            return
            
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': self.request_id,
            'stage': stage,
            'log_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': self._get_stack_trace(),
            'context': context or {},
            'elapsed_time_ms': (time.time() - self.start_time) * 1000
        }
        
        self.logs.append(log_entry)
        logger.error(f"❌ ERROR LOG [{stage}]: {json.dumps(log_entry, indent=2)}")
        
    def log_model_input(self, model_name: str, input_text: str, prompt: str = None, metadata: Dict[str, Any] = None):
        """
        Log model input for AI/ML model debugging.
        
        Args:
            model_name: Name of the model (e.g., 'deberta-v3', 'gpt-4')
            input_text: Text input to the model
            prompt: Prompt used for LLM models
            metadata: Additional metadata
        """
        if not self.enabled:
            return
            
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': self.request_id,
            'stage': 'model_input',
            'model_name': model_name,
            'log_type': 'input',
            'input_text_length': len(input_text),
            'input_text_hash': self._hash_text(input_text),
            'input_text_preview': input_text[:500] if len(input_text) > 500 else input_text,
            'prompt': prompt,
            'prompt_length': len(prompt) if prompt else 0,
            'metadata': metadata or {},
            'elapsed_time_ms': (time.time() - self.start_time) * 1000
        }
        
        self.logs.append(log_entry)
        logger.debug(f"🤖 MODEL INPUT LOG [{model_name}]: {json.dumps(log_entry, indent=2)}")
        
    def log_model_output(self, model_name: str, raw_output: Any, parsed_output: Dict[str, Any], metadata: Dict[str, Any] = None):
        """
        Log model output for AI/ML model debugging.
        
        Args:
            model_name: Name of the model
            raw_output: Raw output from model
            parsed_output: Parsed/processed output
            metadata: Additional metadata
        """
        if not self.enabled:
            return
            
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': self.request_id,
            'stage': 'model_output',
            'model_name': model_name,
            'log_type': 'output',
            'raw_output': str(raw_output)[:1000] if raw_output else None,  # Truncate large outputs
            'parsed_output': self._sanitize_data(parsed_output),
            'output_size': len(json.dumps(parsed_output)) if parsed_output else 0,
            'metadata': metadata or {},
            'elapsed_time_ms': (time.time() - self.start_time) * 1000
        }
        
        self.logs.append(log_entry)
        logger.debug(f"🎯 MODEL OUTPUT LOG [{model_name}]: {json.dumps(log_entry, indent=2)}")
        
    def log_section_extraction(self, sections: Dict[str, str], metadata: Dict[str, Any] = None):
        """
        Log section extraction results specifically.
        
        Args:
            sections: Dictionary of section names to content
            metadata: Additional metadata
        """
        if not self.enabled:
            return
            
        section_info = {
            'sections_detected': list(sections.keys()),
            'section_count': len(sections),
            'section_sizes': {name: len(content) for name, content in sections.items()},
            'has_experience': any('experience' in name.lower() for name in sections.keys()),
            'has_education': any('education' in name.lower() for name in sections.keys()),
            'has_skills': any('skill' in name.lower() for name in sections.keys())
        }
        
        self.log_processing('section_splitting', 'section_extraction', section_info, metadata)
        
        # Log individual section previews
        for section_name, section_content in sections.items():
            section_preview = {
                'section_name': section_name,
                'content_length': len(section_content),
                'content_preview': section_content[:300] if len(section_content) > 300 else section_content
            }
            self.log_processing('section_splitting', f'section_{section_name}', section_preview)
            
    def log_final_result(self, result: Dict[str, Any], metadata: Dict[str, Any] = None):
        """
        Log final parsing result.
        
        Args:
            result: Final parsed result
            metadata: Additional metadata
        """
        if not self.enabled:
            return
            
        # Create summary of result
        result_summary = {
            'candidate_id': result.get('candidate_id'),
            'status': result.get('status'),
            'name': result.get('name'),
            'email': result.get('email'),
            'phone': result.get('phone'),
            'work_experience_count': len(result.get('work_experience', [])),
            'education_count': len(result.get('education', [])),
            'skills_count': len(result.get('skills', [])),
            'confidence_score': result.get('confidence', {}).get('overall'),
            'processing_metrics': result.get('processing_metrics', {}),
            'needs_review': result.get('confidence', {}).get('needs_review', False)
        }
        
        self.log_output('final_output', result_summary, metadata)
        
        # Also log full result (separately for detailed analysis)
        full_result_log = {
            'full_result': self._sanitize_data(result),
            'result_size': len(json.dumps(result))
        }
        self.log_processing('final_output', 'complete_result', full_result_log, metadata)
        
    def get_logs(self, stage: str = None, log_type: str = None) -> List[Dict[str, Any]]:
        """
        Get filtered logs based on criteria.
        
        Args:
            stage: Filter by pipeline stage
            log_type: Filter by log type
            
        Returns:
            List of matching log entries
        """
        filtered_logs = self.logs
        
        if stage:
            filtered_logs = [log for log in filtered_logs if log.get('stage') == stage]
            
        if log_type:
            filtered_logs = [log for log in filtered_logs if log.get('log_type') == log_type]
            
        return filtered_logs
        
    def export_logs(self, output_path: str = None) -> str:
        """
        Export all logs to JSON file.
        
        Args:
            output_path: Path to save logs (default: auto-generated)
            
        Returns:
            Path to exported log file
        """
        if not self.enabled:
            return None
            
        if output_path is None:
            output_path = f"debug_logs_{self.request_id}_{int(time.time())}.json"
            
        export_data = {
            'request_id': self.request_id,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'total_duration_ms': (time.time() - self.start_time) * 1000,
            'total_logs': len(self.logs),
            'logs': self.logs
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"📁 Debug logs exported to {output_path}")
        return output_path
        
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """
        Get summary of pipeline execution.
        
        Returns:
            Dictionary with pipeline summary
        """
        stage_timings = {}
        error_count = 0
        
        for log in self.logs:
            stage = log.get('stage')
            if stage and stage not in stage_timings:
                stage_timings[stage] = {'count': 0, 'errors': 0}
            
            if stage:
                stage_timings[stage]['count'] += 1
                
            if log.get('log_type') == 'error':
                error_count += 1
                if stage:
                    stage_timings[stage]['errors'] += 1
                    
        return {
            'request_id': self.request_id,
            'total_duration_ms': (time.time() - self.start_time) * 1000,
            'total_logs': len(self.logs),
            'total_errors': error_count,
            'stage_summary': stage_timings,
            'pipeline_stages': list(stage_timings.keys())
        }
        
    def _sanitize_data(self, data: Any) -> Any:
        """
        Sanitize data for logging (remove sensitive info, limit size).
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Sanitize potentially sensitive fields
                if key.lower() in ['email', 'phone', 'ssn', 'social_security']:
                    sanitized[key] = self._mask_sensitive(str(value))
                elif key.lower() in ['resume_text', 'raw_text', 'content']:
                    # Truncate large text fields
                    if isinstance(value, str) and len(value) > 1000:
                        sanitized[key] = value[:1000] + '...[truncated]'
                    else:
                        sanitized[key] = value
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # Truncate very long strings
            if len(data) > 2000:
                return data[:2000] + '...[truncated]'
            return data
        else:
            return data
            
    def _mask_sensitive(self, value: str) -> str:
        """
        Mask sensitive information for logging.
        
        Args:
            value: Sensitive value to mask
            
        Returns:
            Masked value
        """
        if len(value) <= 4:
            return '*' * len(value)
        return value[:2] + '*' * (len(value) - 4) + value[-2:]
        
    def _hash_text(self, text: str) -> str:
        """
        Hash text for comparison without storing actual content.
        
        Args:
            text: Text to hash
            
        Returns:
            Hash string
        """
        return hashlib.sha256(text.encode()).hexdigest()[:16]
        
    def _get_stack_trace(self) -> str:
        """
        Get current stack trace.
        
        Returns:
            Stack trace string
        """
        import traceback
        return traceback.format_exc()


class DebugLoggerFactory:
    """
    Factory for creating and managing debug loggers.
    """
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, request_id: str = None, enabled: bool = True) -> DebugLogger:
        """
        Get or create a debug logger for a request.
        
        Args:
            request_id: Unique request identifier
            enabled: Whether debug logging is enabled
            
        Returns:
            DebugLogger instance
        """
        if request_id is None:
            request_id = str(uuid.uuid4())
            
        if request_id not in cls._loggers:
            cls._loggers[request_id] = DebugLogger(request_id, enabled)
            
        return cls._loggers[request_id]
        
    @classmethod
    def remove_logger(cls, request_id: str):
        """
        Remove a debug logger from cache.
        
        Args:
            request_id: Request identifier
        """
        if request_id in cls._loggers:
            del cls._loggers[request_id]
            
    @classmethod
    def clear_all(cls):
        """Clear all cached loggers."""
        cls._loggers.clear()