# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Utility functions for Agent Aura.
Helper functions for logging, callbacks, and data processing.
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime


# Configure logging
def setup_logging(log_level: str = "INFO", log_file: str = "agent_aura.log"):
    """
    Set up logging configuration for Agent Aura.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("agent_aura")


# Global logger
logger = setup_logging()


def suppress_output_callback(response: Any) -> None:
    """
    Callback to suppress intermediate agent outputs.
    Used for sub-agents to keep the output clean.
    
    Args:
        response: Agent response object
    """
    # Suppress output but log for debugging
    logger.debug(f"Agent callback: {type(response).__name__}")
    pass


def log_agent_execution(agent_name: str, action: str, details=None):
    """
    Log agent execution for observability and debugging.
    
    Args:
        agent_name: Name of the agent
        action: Action being performed
        details: Additional details to log (dict)
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "action": action,
        "details": details or {}
    }
    logger.info(f"Agent Execution: {log_entry}")
    return log_entry


def validate_student_data(data) -> bool:
    """
    Validate student data structure and completeness.
    
    Args:
        data: Student data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["student_id", "name", "grade", "gpa", "attendance"]
    
    if data.get("status") == "error":
        logger.error(f"Student data contains error: {data.get('error')}")
        return False
    
    for field in required_fields:
        if field not in data:
            logger.error(f"Missing required field: {field}")
            return False
    
    # Validate data ranges
    if not (0.0 <= data.get("gpa", -1) <= 4.0):
        logger.warning(f"GPA out of range: {data.get('gpa')}")
    
    if not (0 <= data.get("attendance", -1) <= 100):
        logger.warning(f"Attendance out of range: {data.get('attendance')}")
    
    return True


def format_risk_summary(risk_analysis) -> str:
    """
    Format risk analysis results into a human-readable summary.
    
    Args:
        risk_analysis: Risk analysis dictionary
        
    Returns:
        Formatted summary string
    """
    if risk_analysis.get("status") == "error":
        return f"Error in risk analysis: {risk_analysis.get('error')}"
    
    summary = f"""
    Risk Assessment Summary
    =======================
    Student: {risk_analysis.get('student_name', 'Unknown')}
    Risk Level: {risk_analysis.get('risk_level', 'N/A')}
    Risk Score: {risk_analysis.get('risk_score', 0.0):.3f}
    
    Risk Factors:
    """
    
    for i, factor in enumerate(risk_analysis.get('risk_factors', []), 1):
        summary += f"    {i}. {factor}\n"
    
    return summary


def calculate_improvement_percentage(initial_score: float, current_score: float) -> float:
    """
    Calculate improvement percentage between two scores.
    
    Args:
        initial_score: Initial risk score
        current_score: Current risk score
        
    Returns:
        Improvement percentage (positive = improvement, negative = worsening)
    """
    if initial_score == 0:
        return 0.0
    
    improvement = (initial_score - current_score) / initial_score * 100
    return round(improvement, 2)


def get_risk_level_emoji(risk_level: str) -> str:
    """
    Get emoji representation for risk level.
    
    Args:
        risk_level: Risk level string
        
    Returns:
        Emoji string
    """
    emoji_map = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MODERATE": "🟡",
        "LOW": "🟢"
    }
    return emoji_map.get(risk_level, "⚪")


def format_intervention_summary(plan) -> str:
    """
    Format intervention plan into a human-readable summary.
    
    Args:
        plan: Intervention plan dictionary
        
    Returns:
        Formatted summary string
    """
    summary = f"""
    Intervention Plan Summary
    =========================
    Type: {plan.get('type', 'N/A')}
    Priority: {plan.get('priority', 'N/A')}
    Duration: {plan.get('duration_weeks', 'N/A')} weeks
    Frequency: {plan.get('frequency', 'N/A')}
    
    Key Actions:
    """
    
    for i, action in enumerate(plan.get('actions', [])[:5], 1):
        summary += f"    {i}. {action}\n"
    
    summary += f"\n    Estimated Cost: {plan.get('estimated_cost', 'N/A')}\n"
    
    return summary


def create_progress_report(student_id: str, progress_data):
    """
    Create a comprehensive progress report for a student.
    
    Args:
        student_id: Student identifier
        progress_data: Progress tracking data dictionary
        
    Returns:
        Formatted progress report dictionary
    """
    report = {
        "student_id": student_id,
        "report_date": datetime.now().isoformat(),
        "summary": progress_data,
        "status": "generated"
    }
    
    return report


class AgentMetrics:
    """Class for tracking agent performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "total_students_processed": 0,
            "risk_assessments_completed": 0,
            "notifications_sent": 0,
            "interventions_planned": 0,
            "predictions_generated": 0,
            "errors_encountered": 0,
            "execution_times": []
        }
    
    def increment(self, metric: str):
        """Increment a metric counter."""
        if metric in self.metrics:
            self.metrics[metric] += 1
    
    def add_execution_time(self, time_seconds: float):
        """Add execution time to metrics."""
        self.metrics["execution_times"].append(time_seconds)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        summary = self.metrics.copy()
        
        if self.metrics["execution_times"]:
            summary["avg_execution_time"] = sum(self.metrics["execution_times"]) / len(self.metrics["execution_times"])
            summary["total_execution_time"] = sum(self.metrics["execution_times"])
        
        return summary


# Global metrics instance
metrics = AgentMetrics()
