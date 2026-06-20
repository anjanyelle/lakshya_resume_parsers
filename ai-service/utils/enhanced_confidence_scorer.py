"""
Enhanced Confidence Scoring System for Resume Parser
Provides detailed confidence analysis for extracted fields with multi-factor scoring
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ExtractionMethod(Enum):
    """Extraction methods with different confidence levels"""
    RULE_BASED = "rule_based"           # Medium confidence
    DEBERTA_NER = "deberta_ner"         # High confidence
    LLM_EXTRACTION = "llm_extraction"   # Very high confidence
    HYBRID = "hybrid"                   # Highest confidence (multiple methods)
    MANUAL = "manual"                   # Perfect confidence
    FALLBACK = "fallback"               # Low confidence


class QualityLevel(Enum):
    """Overall quality levels"""
    EXCELLENT = "excellent"    # > 0.9
    GOOD = "good"              # > 0.8
    ACCEPTABLE = "acceptable"  # > 0.7
    NEEDS_REVIEW = "needs_review"  # > 0.6
    POOR = "poor"              # <= 0.6


class EnhancedConfidenceScorer:
    """
    Enhanced confidence scoring system that considers multiple factors
    for each extracted field to provide accurate confidence assessments.
    """
    
    # Base confidence scores by extraction method
    METHOD_CONFIDENCE = {
        ExtractionMethod.MANUAL: 1.0,
        ExtractionMethod.HYBRID: 0.95,
        ExtractionMethod.LLM_EXTRACTION: 0.9,
        ExtractionMethod.DEBERTA_NER: 0.85,
        ExtractionMethod.RULE_BASED: 0.7,
        ExtractionMethod.FALLBACK: 0.5
    }
    
    # Validation patterns with confidence weights
    VALIDATION_PATTERNS = {
        'email': {
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'weight': 0.3
        },
        'phone': {
            'pattern': r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$',
            'weight': 0.25
        },
        'url': {
            'pattern': r'^https?://[^\s/$.?#].[^\s]*$',
            'weight': 0.2
        },
        'date': {
            'pattern': r'^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/((19|20)\d{2})$',
            'weight': 0.2
        }
    }
    
    def __init__(self):
        """Initialize enhanced confidence scorer."""
        self.historical_accuracy = {}  # Track historical accuracy by field
        self.field_weights = {
            'name': 1.0,
            'email': 0.9,
            'phone': 0.85,
            'linkedin_url': 0.8,
            'github_url': 0.75,
            'work_experience': 0.95,
            'education': 0.9,
            'skills': 0.85
        }
        
    def calculate_field_confidence(
        self, 
        field_name: str, 
        extracted_value: Any, 
        extraction_method: ExtractionMethod,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence score for a single field.
        
        Args:
            field_name: Name of the field being scored
            extracted_value: The extracted value
            extraction_method: Method used for extraction
            context: Additional context (other fields, raw text, etc.)
            
        Returns:
            Dictionary with confidence score and breakdown
        """
        context = context or {}
        
        # Start with base confidence from extraction method
        base_confidence = self.METHOD_CONFIDENCE.get(extraction_method, 0.5)
        
        # Calculate individual confidence factors
        validation_confidence = self._calculate_validation_confidence(field_name, extracted_value)
        context_confidence = self._calculate_context_confidence(field_name, extracted_value, context)
        historical_confidence = self._get_historical_confidence(field_name)
        data_quality_confidence = self._calculate_data_quality_confidence(field_name, extracted_value)
        
        # Weighted combination
        weights = {
            'base': 0.4,
            'validation': 0.25,
            'context': 0.15,
            'historical': 0.1,
            'data_quality': 0.1
        }
        
        final_confidence = (
            base_confidence * weights['base'] +
            validation_confidence * weights['validation'] +
            context_confidence * weights['context'] +
            historical_confidence * weights['historical'] +
            data_quality_confidence * weights['data_quality']
        )
        
        # Ensure confidence is within valid range
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        confidence_breakdown = {
            'base_confidence': base_confidence,
            'validation_confidence': validation_confidence,
            'context_confidence': context_confidence,
            'historical_confidence': historical_confidence,
            'data_quality_confidence': data_quality_confidence,
            'weights': weights,
            'final_confidence': final_confidence
        }
        
        # Determine if field requires review
        requires_review = final_confidence < 0.8
        
        return {
            'field_name': field_name,
            'confidence_score': final_confidence,
            'extraction_method': extraction_method.value,
            'requires_review': requires_review,
            'confidence_breakdown': confidence_breakdown,
            'validation_results': self._get_validation_details(field_name, extracted_value),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def calculate_overall_confidence(
        self, 
        parsed_data: Dict[str, Any], 
        extraction_methods: Dict[str, ExtractionMethod] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall confidence score for the entire parsed result.
        
        Args:
            parsed_data: Complete parsed data dictionary
            extraction_methods: Dictionary mapping field names to extraction methods
            
        Returns:
            Dictionary with overall confidence and field-level breakdown
        """
        extraction_methods = extraction_methods or {}
        
        field_confidences = {}
        weighted_scores = []
        
        # Calculate confidence for each field
        for field_name, field_value in parsed_data.items():
            if field_name in ['candidate_id', 'status', 'processing_metrics', 'confidence']:
                continue
                
            # Determine extraction method
            method = extraction_methods.get(field_name, ExtractionMethod.HYBRID)
            
            # Handle different field types
            if isinstance(field_value, list):
                # For arrays, calculate average confidence across items
                item_confidences = []
                for item in field_value:
                    if isinstance(item, dict):
                        # For structured items, calculate confidence for each sub-field
                        item_confidence = self._calculate_structured_item_confidence(
                            field_name, item, method, parsed_data
                        )
                        item_confidences.append(item_confidence)
                
                if item_confidences:
                    avg_confidence = sum(item_confidences) / len(item_confidences)
                    field_confidences[field_name] = avg_confidence
                    
                    # Apply field weight
                    field_weight = self.field_weights.get(field_name, 0.8)
                    weighted_scores.append(avg_confidence * field_weight)
                    
            elif isinstance(field_value, dict):
                # For single structured item
                item_confidence = self._calculate_structured_item_confidence(
                    field_name, field_value, method, parsed_data
                )
                field_confidences[field_name] = item_confidence
                
                field_weight = self.field_weights.get(field_name, 0.8)
                weighted_scores.append(item_confidence * field_weight)
                
            elif field_value:  # Simple field with value
                field_confidence_result = self.calculate_field_confidence(
                    field_name, field_value, method, parsed_data
                )
                field_confidences[field_name] = field_confidence_result['confidence_score']
                
                field_weight = self.field_weights.get(field_name, 0.8)
                weighted_scores.append(field_confidence_result['confidence_score'] * field_weight)
        
        # Calculate overall confidence
        if weighted_scores:
            overall_confidence = sum(weighted_scores) / sum(self.field_weights.get(f, 0.8) for f in field_confidences.keys())
        else:
            overall_confidence = 0.5  # Default if no fields
            
        overall_confidence = max(0.0, min(1.0, overall_confidence))
        
        # Determine quality level
        quality_level = self._get_quality_level(overall_confidence)
        
        # Count fields requiring review
        fields_needing_review = [
            field for field, conf in field_confidences.items() if conf < 0.8
        ]
        
        return {
            'overall_confidence': overall_confidence,
            'quality_level': quality_level.value,
            'needs_review': overall_confidence < 0.8,
            'field_confidences': field_confidences,
            'fields_needing_review': fields_needing_review,
            'total_fields': len(field_confidences),
            'review_percentage': (len(fields_needing_review) / len(field_confidences)) * 100 if field_confidences else 0,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def _calculate_validation_confidence(self, field_name: str, value: Any) -> float:
        """Calculate confidence based on validation rules."""
        if not value:
            return 0.0
            
        value_str = str(value).strip()
        if not value_str:
            return 0.0
            
        # Check if field has validation pattern
        field_key = field_name.lower().replace('_', '')
        for pattern_name, pattern_config in self.VALIDATION_PATTERNS.items():
            if pattern_name in field_key:
                if re.match(pattern_config['pattern'], value_str):
                    return pattern_config['weight']
                else:
                    return 0.0
                    
        # Default validation confidence based on basic checks
        if len(value_str) < 2:  # Too short
            return 0.3
        elif len(value_str) > 500:  # Too long
            return 0.5
        else:
            return 0.7
            
    def _calculate_context_confidence(self, field_name: str, value: Any, context: Dict[str, Any]) -> float:
        """Calculate confidence based on context consistency."""
        if not context:
            return 0.5
            
        context_score = 0.5
        
        # Check email consistency
        if field_name == 'email' and 'name' in context:
            name_parts = context['name'].split()
            if name_parts and any(part.lower() in str(value).lower() for part in name_parts):
                context_score += 0.2
                
        # Check phone consistency
        if field_name == 'phone' and 'location' in context:
            # Simple check - could be enhanced with country code validation
            context_score += 0.1
            
        # Check work experience consistency
        if field_name in ['company', 'job_title'] and 'work_experience' in context:
            work_exp = context['work_experience']
            if isinstance(work_exp, list) and len(work_exp) > 0:
                context_score += 0.2
                
        # Check education consistency
        if field_name in ['institution', 'degree'] and 'education' in context:
            education = context['education']
            if isinstance(education, list) and len(education) > 0:
                context_score += 0.2
                
        return min(1.0, context_score)
        
    def _get_historical_confidence(self, field_name: str) -> float:
        """Get historical accuracy for this field."""
        if field_name not in self.historical_accuracy:
            return 0.7  # Default historical confidence
            
        return self.historical_accuracy[field_name]
        
    def _calculate_data_quality_confidence(self, field_name: str, value: Any) -> float:
        """Calculate confidence based on data quality indicators."""
        if not value:
            return 0.0
            
        value_str = str(value).strip()
        quality_score = 0.5
        
        # Check for special characters that might indicate errors
        special_chars = r'[<>{}|\\^~[\]]'
        if re.search(special_chars, value_str):
            quality_score -= 0.2
            
        # Check for repeated characters (potential errors)
        if len(set(value_str)) < len(value_str) * 0.3 and len(value_str) > 5:
            quality_score -= 0.1
            
        # Check for mixed case consistency
        if field_name in ['name', 'company', 'institution']:
            if value_str[0].isupper():
                quality_score += 0.1
                
        # Check for reasonable length
        if 2 <= len(value_str) <= 100:
            quality_score += 0.1
        elif len(value_str) > 100:
            quality_score -= 0.1
            
        return max(0.0, min(1.0, quality_score))
        
    def _calculate_structured_item_confidence(
        self, 
        field_name: str, 
        item: Dict[str, Any], 
        method: ExtractionMethod, 
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence for a structured item (like work experience entry)."""
        if not item or not isinstance(item, dict):
            return 0.0
            
        item_confidences = []
        
        # Calculate confidence for each sub-field
        for sub_field, sub_value in item.items():
            if sub_value:  # Only score non-empty fields
                sub_field_confidence = self.calculate_field_confidence(
                    f"{field_name}.{sub_field}", 
                    sub_value, 
                    method, 
                    {**context, field_name: item}
                )
                item_confidences.append(sub_field_confidence['confidence_score'])
                
        # Average confidence across sub-fields
        if item_confidences:
            return sum(item_confidences) / len(item_confidences)
        else:
            return 0.5
            
    def _get_validation_details(self, field_name: str, value: Any) -> Dict[str, Any]:
        """Get detailed validation results for a field."""
        validation_details = {
            'is_valid': True,
            'validation_rules': [],
            'warnings': []
        }
        
        if not value:
            validation_details['is_valid'] = False
            validation_details['warnings'].append('Field is empty')
            return validation_details
            
        value_str = str(value).strip()
        
        # Check length
        if len(value_str) < 2:
            validation_details['is_valid'] = False
            validation_details['warnings'].append('Value too short')
        elif len(value_str) > 500:
            validation_details['warnings'].append('Value unusually long')
            
        # Check for validation patterns
        field_key = field_name.lower().replace('_', '')
        for pattern_name, pattern_config in self.VALIDATION_PATTERNS.items():
            if pattern_name in field_key:
                is_valid = bool(re.match(pattern_config['pattern'], value_str))
                validation_details['validation_rules'].append({
                    'rule': pattern_name,
                    'passed': is_valid,
                    'pattern': pattern_config['pattern']
                })
                if not is_valid:
                    validation_details['is_valid'] = False
                    
        return validation_details
        
    def _get_quality_level(self, confidence_score: float) -> QualityLevel:
        """Map confidence score to quality level."""
        if confidence_score >= 0.9:
            return QualityLevel.EXCELLENT
        elif confidence_score >= 0.8:
            return QualityLevel.GOOD
        elif confidence_score >= 0.7:
            return QualityLevel.ACCEPTABLE
        elif confidence_score >= 0.6:
            return QualityLevel.NEEDS_REVIEW
        else:
            return QualityLevel.POOR
            
    def update_historical_accuracy(self, field_name: str, was_correct: bool):
        """
        Update historical accuracy based on feedback.
        
        Args:
            field_name: Name of the field
            was_correct: Whether the extraction was correct
        """
        if field_name not in self.historical_accuracy:
            self.historical_accuracy[field_name] = 0.7
            
        # Update with exponential moving average
        alpha = 0.1  # Learning rate
        current_accuracy = self.historical_accuracy[field_name]
        new_accuracy = current_accuracy + alpha * (1.0 if was_correct else 0.0 - current_accuracy)
        self.historical_accuracy[field_name] = new_accuracy
        
    def set_field_weight(self, field_name: str, weight: float):
        """
        Set custom weight for a field.
        
        Args:
            field_name: Name of the field
            weight: Weight value (0.0 to 1.0)
        """
        self.field_weights[field_name] = max(0.0, min(1.0, weight))
        
    def get_confidence_threshold(self, quality_level: QualityLevel) -> float:
        """Get confidence threshold for a quality level."""
        thresholds = {
            QualityLevel.EXCELLENT: 0.9,
            QualityLevel.GOOD: 0.8,
            QualityLevel.ACCEPTABLE: 0.7,
            QualityLevel.NEEDS_REVIEW: 0.6,
            QualityLevel.POOR: 0.0
        }
        return thresholds.get(quality_level, 0.7)