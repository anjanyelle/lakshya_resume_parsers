"""
Evaluation Dashboard API Endpoints for Resume Parser
Provides REST API for monitoring, metrics, and evaluation data
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

# Import evaluation components
from utils.evaluation_dashboard import EvaluationDashboard, AlertManager
from utils.error_classifier import ErrorClassifier

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/evaluation", tags=["evaluation"])

# Initialize evaluation components
dashboard = EvaluationDashboard()
alert_manager = AlertManager()


@router.get("/dashboard/overview")
async def get_overview_metrics(time_period: str = Query("7d", description="Time period: 1d, 7d, 30d, all")):
    """
    Get overview metrics for the evaluation dashboard.
    
    Returns:
        Overview metrics including total resumes, success rate, processing times
    """
    try:
        metrics = dashboard.get_overview_metrics(time_period)
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Error getting overview metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/accuracy-trends")
async def get_accuracy_trends(time_period: str = Query("30d", description="Time period for trends")):
    """
    Get accuracy trends over time.
    
    Returns:
        Accuracy trend data including daily metrics and trend analysis
    """
    try:
        trends = dashboard.get_accuracy_trends(time_period)
        return {
            "status": "success",
            "data": trends
        }
    except Exception as e:
        logger.error(f"Error getting accuracy trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/errors")
async def get_error_analysis(time_period: str = Query("7d", description="Time period for error analysis")):
    """
    Get detailed error analysis.
    
    Returns:
        Error breakdown by category, top error types, recovery rates
    """
    try:
        errors = dashboard.get_error_analysis(time_period)
        return {
            "status": "success",
            "data": errors
        }
    except Exception as e:
        logger.error(f"Error getting error analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/performance")
async def get_performance_metrics(time_period: str = Query("7d", description="Time period for performance metrics")):
    """
    Get performance metrics for each pipeline stage.
    
    Returns:
        Stage-level performance data including duration, memory, CPU usage
    """
    try:
        performance = dashboard.get_performance_metrics(time_period)
        return {
            "status": "success",
            "data": performance
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/confidence")
async def get_confidence_analysis(time_period: str = Query("7d", description="Time period for confidence analysis")):
    """
    Get confidence score analysis.
    
    Returns:
        Confidence distribution, field-level scores, review recommendations
    """
    try:
        confidence = dashboard.get_confidence_analysis(time_period)
        return {
            "status": "success",
            "data": confidence
        }
    except Exception as e:
        logger.error(f"Error getting confidence analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/quality-trends")
async def get_quality_trends(time_period: str = Query("30d", description="Time period for quality trends")):
    """
    Get data quality trends over time.
    
    Returns:
        Quality scores, validation pass rates, completeness trends
    """
    try:
        quality = dashboard.get_quality_trends(time_period)
        return {
            "status": "success",
            "data": quality
        }
    except Exception as e:
        logger.error(f"Error getting quality trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/alerts")
async def check_alerts():
    """
    Check for active alerts based on current metrics.
    
    Returns:
        List of active alerts with severity and details
    """
    try:
        metrics = dashboard.get_overview_metrics("1d")
        alerts = alert_manager.check_alerts(metrics)
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "critical_count": sum(1 for a in alerts if a["severity"] == "critical"),
                "warning_count": sum(1 for a in alerts if a["severity"] == "warning")
            }
        }
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/full-report")
async def get_full_dashboard_report():
    """
    Generate complete dashboard report.
    
    Returns:
        Comprehensive dashboard report with all metrics
    """
    try:
        report_path = dashboard.generate_dashboard_report()
        return {
            "status": "success",
            "data": {
                "report_path": report_path,
                "message": "Dashboard report generated successfully"
            }
        }
    except Exception as e:
        logger.error(f"Error generating dashboard report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-classification")
async def get_error_classification():
    """
    Get error classification statistics.
    
    Returns:
        Error classification breakdown and recovery rates
    """
    try:
        classifier = ErrorClassifier()
        stats = classifier.get_error_statistics()
        common_errors = classifier.get_common_errors()
        recovery_rates = classifier.get_recovery_success_rate()
        
        return {
            "status": "success",
            "data": {
                "statistics": stats,
                "common_errors": common_errors,
                "recovery_rates": recovery_rates
            }
        }
    except Exception as e:
        logger.error(f"Error getting error classification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def evaluation_health_check():
    """
    Health check for evaluation framework.
    
    Returns:
        Health status of evaluation components
    """
    return {
        "status": "healthy",
        "components": {
            "dashboard": "operational",
            "alert_manager": "operational",
            "error_classifier": "operational"
        },
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }
