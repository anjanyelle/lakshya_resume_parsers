"""
Evaluation Dashboard for Resume Parser
Provides insights, metrics visualization, and monitoring capabilities
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class EvaluationDashboard:
    """
    Comprehensive evaluation dashboard for monitoring resume parser performance,
    accuracy trends, and error patterns.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize evaluation dashboard.
        
        Args:
            db_connection: Database connection for fetching metrics
        """
        self.db_connection = db_connection
        self.cache = {}
        self.cache_timestamp = None
        
    def get_overview_metrics(self, time_period: str = '7d') -> Dict[str, Any]:
        """
        Get overview metrics for the specified time period.
        
        Args:
            time_period: Time period ('1d', '7d', '30d', 'all')
            
        Returns:
            Overview metrics dictionary
        """
        # Calculate time filter
        time_filter = self._get_time_filter(time_period)
        
        # In a real implementation, this would query the database
        # For now, return mock data structure
        metrics = {
            'time_period': time_period,
            'total_resumes_processed': 1250,
            'successful_parses': 1087,
            'failed_parses': 163,
            'success_rate': 0.8696,
            'average_processing_time_ms': 8520,
            'average_confidence_score': 0.82,
            'error_rate': 0.1304,
            'breakdown_by_file_type': {
                'pdf': {'count': 980, 'success_rate': 0.88},
                'docx': {'count': 220, 'success_rate': 0.85},
                'txt': {'count': 50, 'success_rate': 0.92}
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return metrics
        
    def get_accuracy_trends(self, time_period: str = '30d') -> Dict[str, Any]:
        """
        Get accuracy trends over time.
        
        Args:
            time_period: Time period for trends
            
        Returns:
            Accuracy trends data
        """
        # Mock data for accuracy trends
        trends = {
            'time_period': time_period,
            'daily_accuracy': [
                {
                    'date': '2024-06-01',
                    'text_extraction_accuracy': 0.92,
                    'section_detection_accuracy': 0.85,
                    'entity_extraction_accuracy': 0.78,
                    'overall_accuracy': 0.83
                },
                {
                    'date': '2024-06-02',
                    'text_extraction_accuracy': 0.94,
                    'section_detection_accuracy': 0.87,
                    'entity_extraction_accuracy': 0.81,
                    'overall_accuracy': 0.85
                },
                # More days...
            ],
            'trend_analysis': {
                'text_extraction_trend': 'improving',
                'section_detection_trend': 'stable',
                'entity_extraction_trend': 'improving',
                'overall_trend': 'improving'
            },
            'benchmark_comparison': {
                'current_accuracy': 0.85,
                'target_accuracy': 0.90,
                'gap': 0.05,
                'on_track': True
            }
        }
        
        return trends
        
    def get_error_analysis(self, time_period: str = '7d') -> Dict[str, Any]:
        """
        Get detailed error analysis.
        
        Args:
            time_period: Time period for analysis
            
        Returns:
            Error analysis data
        """
        error_analysis = {
            'time_period': time_period,
            'total_errors': 163,
            'error_breakdown': {
                'extraction_error': {
                    'count': 45,
                    'percentage': 27.6,
                    'most_common_type': 'text_extraction_failed'
                },
                'section_splitter_error': {
                    'count': 38,
                    'percentage': 23.3,
                    'most_common_type': 'missing_critical_section'
                },
                'model_inference_error': {
                    'count': 52,
                    'percentage': 31.9,
                    'most_common_type': 'confidence_too_low'
                },
                'json_formatting_error': {
                    'count': 18,
                    'percentage': 11.0,
                    'most_common_type': 'json_parse_failed'
                },
                'validation_error': {
                    'count': 10,
                    'percentage': 6.1,
                    'most_common_type': 'date_validation_failed'
                }
            },
            'top_error_types': [
                {'error_type': 'confidence_too_low', 'count': 35, 'percentage': 21.5},
                {'error_type': 'text_extraction_failed', 'count': 28, 'percentage': 17.2},
                {'error_type': 'missing_critical_section', 'count': 22, 'percentage': 13.5},
                {'error_type': 'json_parse_failed', 'count': 15, 'percentage': 9.2},
                {'error_type': 'section_detection_failed', 'count': 12, 'percentage': 7.4}
            ],
            'error_recovery_rate': {
                'total_errors': 163,
                'recovered': 47,
                'recovery_rate': 0.288,
                'by_error_type': {
                    'text_extraction_failed': {'recovery_rate': 0.35},
                    'missing_critical_section': {'recovery_rate': 0.42},
                    'json_parse_failed': {'recovery_rate': 0.61}
                }
            },
            'emerging_errors': [
                {'error_type': 'api_rate_limit', 'first_seen': '2024-06-15', 'count': 5}
            ]
        }
        
        return error_analysis
        
    def get_performance_metrics(self, time_period: str = '7d') -> Dict[str, Any]:
        """
        Get performance metrics for each pipeline stage.
        
        Args:
            time_period: Time period for metrics
            
        Returns:
            Performance metrics data
        """
        performance_metrics = {
            'time_period': time_period,
            'stage_performance': {
                'text_extraction': {
                    'average_duration_ms': 1250,
                    'max_duration_ms': 3500,
                    'min_duration_ms': 800,
                    'p95_duration_ms': 2800,
                    'memory_usage_mb': 128,
                    'cpu_usage_percent': 45.2
                },
                'section_splitting': {
                    'average_duration_ms': 850,
                    'max_duration_ms': 2200,
                    'min_duration_ms': 400,
                    'p95_duration_ms': 1800,
                    'memory_usage_mb': 64,
                    'cpu_usage_percent': 25.8
                },
                'model_inference': {
                    'average_duration_ms': 5200,
                    'max_duration_ms': 12000,
                    'min_duration_ms': 3800,
                    'p95_duration_ms': 9500,
                    'memory_usage_mb': 512,
                    'cpu_usage_percent': 78.5
                },
                'entity_extraction': {
                    'average_duration_ms': 980,
                    'max_duration_ms': 2500,
                    'min_duration_ms': 600,
                    'p95_duration_ms': 1900,
                    'memory_usage_mb': 96,
                    'cpu_usage_percent': 35.2
                },
                'final_output': {
                    'average_duration_ms': 240,
                    'max_duration_ms': 800,
                    'min_duration_ms': 120,
                    'p95_duration_ms': 550,
                    'memory_usage_mb': 32,
                    'cpu_usage_percent': 15.6
                }
            },
            'total_pipeline_time': {
                'average_ms': 8520,
                'max_ms': 18500,
                'min_ms': 5200,
                'p95_ms': 14200
            },
            'resource_utilization': {
                'average_memory_mb': 832,
                'peak_memory_mb': 1200,
                'average_cpu_percent': 40.1,
                'peak_cpu_percent': 85.3
            }
        }
        
        return performance_metrics
        
    def get_confidence_analysis(self, time_period: str = '7d') -> Dict[str, Any]:
        """
        Get confidence score analysis.
        
        Args:
            time_period: Time period for analysis
            
        Returns:
            Confidence analysis data
        """
        confidence_analysis = {
            'time_period': time_period,
            'overall_confidence_distribution': {
                'excellent': {'count': 425, 'percentage': 34.0, 'range': '>0.9'},
                'good': {'count': 375, 'percentage': 30.0, 'range': '0.8-0.9'},
                'acceptable': {'count': 250, 'percentage': 20.0, 'range': '0.7-0.8'},
                'needs_review': {'count': 125, 'percentage': 10.0, 'range': '0.6-0.7'},
                'poor': {'count': 75, 'percentage': 6.0, 'range': '<0.6'}
            },
            'field_level_confidence': {
                'name': {'average': 0.92, 'min': 0.45, 'max': 0.98},
                'email': {'average': 0.95, 'min': 0.60, 'max': 0.99},
                'phone': {'average': 0.88, 'min': 0.35, 'max': 0.97},
                'work_experience': {'average': 0.82, 'min': 0.25, 'max': 0.95},
                'education': {'average': 0.85, 'min': 0.30, 'max': 0.96},
                'skills': {'average': 0.78, 'min': 0.20, 'max': 0.93}
            },
            'low_confidence_triggers': {
                'missing_critical_section': {'count': 45, 'impact': -0.15},
                'ocr_quality_low': {'count': 38, 'impact': -0.12},
                'model_confidence_low': {'count': 62, 'impact': -0.18},
                'validation_failed': {'count': 28, 'impact': -0.08}
            },
            'review_recommendations': {
                'total_requiring_review': 200,
                'by_confidence_level': {
                    'needs_review': 125,
                    'poor': 75
                },
                'by_field': {
                    'work_experience': 85,
                    'skills': 45,
                    'education': 35,
                    'phone': 25,
                    'email': 10
                }
            }
        }
        
        return confidence_analysis
        
    def get_quality_trends(self, time_period: str = '30d') -> Dict[str, Any]:
        """
        Get data quality trends over time.
        
        Args:
            time_period: Time period for trends
            
        Returns:
            Quality trends data
        """
        quality_trends = {
            'time_period': time_period,
            'data_quality_score': {
                'current': 0.82,
                'trend': 'improving',
                'change_30d': +0.05,
                'change_7d': +0.02
            },
            'validation_pass_rates': {
                'email_validation': {'current': 0.95, 'trend': 'stable'},
                'phone_validation': {'current': 0.88, 'trend': 'improving'},
                'date_validation': {'current': 0.82, 'trend': 'improving'},
                'url_validation': {'current': 0.91, 'trend': 'stable'}
            },
            'completeness_trends': {
                'field_completeness': {
                    'name': 0.98,
                    'email': 0.95,
                    'phone': 0.88,
                    'work_experience': 0.85,
                    'education': 0.82,
                    'skills': 0.78
                },
                'overall_completeness': 0.87,
                'trend': 'stable'
            },
            'user_feedback_patterns': {
                'total_feedback': 125,
                'positive_feedback': 98,
                'negative_feedback': 27,
                'common_issues': [
                    {'issue': 'missing_experience', 'count': 12},
                    {'issue': 'incorrect_dates', 'count': 8},
                    {'issue': 'wrong_company', 'count': 5}
                ]
            }
        }
        
        return quality_trends
        
    def generate_dashboard_report(self, output_path: str = None) -> str:
        """
        Generate comprehensive dashboard report.
        
        Args:
            output_path: Path to save report
            
        Returns:
            Path to generated report
        """
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': 'evaluation_dashboard',
                'time_period': '7d'
            },
            'overview_metrics': self.get_overview_metrics(),
            'accuracy_trends': self.get_accuracy_trends(),
            'error_analysis': self.get_error_analysis(),
            'performance_metrics': self.get_performance_metrics(),
            'confidence_analysis': self.get_confidence_analysis(),
            'quality_trends': self.get_quality_trends(),
            'recommendations': self._generate_dashboard_recommendations()
        }
        
        if output_path is None:
            output_path = f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"📊 Dashboard report generated: {output_path}")
        return output_path
        
    def _generate_dashboard_recommendations(self) -> List[str]:
        """Generate recommendations based on dashboard data."""
        recommendations = []
        
        # Get current metrics
        overview = self.get_overview_metrics()
        errors = self.get_error_analysis()
        confidence = self.get_confidence_analysis()
        
        # Analyze success rate
        if overview['success_rate'] < 0.80:
            recommendations.append("🔴 Success rate below 80% - immediate attention required")
        elif overview['success_rate'] < 0.90:
            recommendations.append("🟡 Success rate below 90% - optimization recommended")
        else:
            recommendations.append("🟢 Success rate is healthy - maintain current performance")
            
        # Analyze error patterns
        top_error = errors['top_error_types'][0]
        if top_error['percentage'] > 15:
            recommendations.append(f"🔴 Address top error type: {top_error['error_type']} ({top_error['percentage']}%)")
            
        # Analyze confidence scores
        poor_quality_percentage = confidence['overall_confidence_distribution']['poor']['percentage']
        if poor_quality_percentage > 10:
            recommendations.append(f"🟡 High percentage of poor quality extractions ({poor_quality_percentage}%)")
            
        # Analyze performance
        performance = self.get_performance_metrics()
        avg_time = performance['total_pipeline_time']['average_ms']
        if avg_time > 10000:
            recommendations.append(f"🟡 Average processing time ({avg_time}ms) is above target")
            
        return recommendations
        
    def _get_time_filter(self, time_period: str) -> datetime:
        """Get datetime filter for specified time period."""
        now = datetime.now()
        
        if time_period == '1d':
            return now - timedelta(days=1)
        elif time_period == '7d':
            return now - timedelta(days=7)
        elif time_period == '30d':
            return now - timedelta(days=30)
        else:
            return datetime.min  # All time


class AlertManager:
    """
    Manages alerts based on evaluation metrics and thresholds.
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self.thresholds = {
            'success_rate': {'warning': 0.85, 'critical': 0.75},
            'error_rate': {'warning': 0.15, 'critical': 0.25},
            'average_processing_time_ms': {'warning': 10000, 'critical': 15000},
            'low_confidence_percentage': {'warning': 0.15, 'critical': 0.25}
        }
        
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check metrics against thresholds and generate alerts.
        
        Args:
            metrics: Current metrics
            
        Returns:
            List of alerts
        """
        alerts = []
        
        # Check success rate
        success_rate = metrics.get('success_rate', 0.0)
        if success_rate < self.thresholds['success_rate']['critical']:
            alerts.append({
                'severity': 'critical',
                'type': 'success_rate',
                'message': f"Success rate critically low: {success_rate:.1%}",
                'current_value': success_rate,
                'threshold': self.thresholds['success_rate']['critical']
            })
        elif success_rate < self.thresholds['success_rate']['warning']:
            alerts.append({
                'severity': 'warning',
                'type': 'success_rate',
                'message': f"Success rate below target: {success_rate:.1%}",
                'current_value': success_rate,
                'threshold': self.thresholds['success_rate']['warning']
            })
            
        # Check error rate
        error_rate = metrics.get('error_rate', 0.0)
        if error_rate > self.thresholds['error_rate']['critical']:
            alerts.append({
                'severity': 'critical',
                'type': 'error_rate',
                'message': f"Error rate critically high: {error_rate:.1%}",
                'current_value': error_rate,
                'threshold': self.thresholds['error_rate']['critical']
            })
        elif error_rate > self.thresholds['error_rate']['warning']:
            alerts.append({
                'severity': 'warning',
                'type': 'error_rate',
                'message': f"Error rate elevated: {error_rate:.1%}",
                'current_value': error_rate,
                'threshold': self.thresholds['error_rate']['warning']
            })
            
        # Check processing time
        processing_time = metrics.get('average_processing_time_ms', 0)
        if processing_time > self.thresholds['average_processing_time_ms']['critical']:
            alerts.append({
                'severity': 'critical',
                'type': 'processing_time',
                'message': f"Processing time critically slow: {processing_time}ms",
                'current_value': processing_time,
                'threshold': self.thresholds['average_processing_time_ms']['critical']
            })
        elif processing_time > self.thresholds['average_processing_time_ms']['warning']:
            alerts.append({
                'severity': 'warning',
                'type': 'processing_time',
                'message': f"Processing time elevated: {processing_time}ms",
                'current_value': processing_time,
                'threshold': self.thresholds['average_processing_time_ms']['warning']
            })
            
        return alerts