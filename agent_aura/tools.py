# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Tools module for Agent Aura.
Implements 8 intelligent tools for student risk analysis, intervention planning,
notifications, and progress tracking.
"""

import json
import csv
import os
from datetime import datetime
import pandas as pd


# Global progress tracking database
progress_database = {}
notification_log = []


class RiskThresholds:
    """Risk level thresholds for student assessment."""
    CRITICAL = 0.90
    HIGH = 0.80
    MODERATE = 0.60
    LOW = 0.30


# ============================================================================
# FOUNDATION TOOLS (1-4) - Core Functionality
# ============================================================================

def get_student_data(student_id: str, data_source: str = None):
    """
    Tool 1: Retrieve comprehensive student profile.
    
    Args:
        student_id: Unique identifier for the student
        data_source: Path to the student data CSV file (optional, defaults to project data/student_data.csv)
        
    Returns:
        Dictionary containing student information or error
    """
    from pathlib import Path
    
    # If no data source provided, use project default
    if data_source is None:
        # Get project root (parent of agent_aura directory)
        project_root = Path(__file__).parent.parent
        data_source = str(project_root / "data" / "student_data.csv")
    
    try:
        # Load student data
        if os.path.exists(data_source):
            df = pd.read_csv(data_source)
        else:
            return {
                "error": f"Data source not found: {data_source}",
                "status": "error"
            }
        
        # Find student record
        records = df[df['student_id'] == student_id]
        if records.empty:
            return {
                "error": f"Student {student_id} not found",
                "status": "error"
            }
        
        # Extract student data
        student = records.iloc[0]
        return {
            "student_id": str(student.get('student_id', 'N/A')),
            "name": str(student.get('name', 'Unknown')),
            "grade": int(student.get('grade_level', 0)),
            "gpa": float(student.get('gpa', 2.5)),
            "attendance": float(student.get('attendance_rate', 0.9)) * 100,
            "performance": str(student.get('overall_performance', 'Average')),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Error retrieving student data: {str(e)}",
            "status": "error"
        }


def analyze_student_risk(student_id: str):
    """
    Tool 2: Calculate risk score and categorize risk level for a student.
    
    Args:
        student_id: The unique identifier of the student to analyze (e.g., "S001")
        
    Returns:
        Dictionary with risk score, level, and contributing factors
    """
    # First get the student data
    student_data = get_student_data(student_id)
    
    if student_data.get("status") == "error":
        return {
            "error": "Invalid student data provided",
            "status": "error"
        }
    
    score = 0.0
    risk_factors = []
    
    # GPA Analysis (40% weight)
    gpa = float(student_data.get('gpa', 3.0))
    if gpa < 2.0:
        score += 0.40
        risk_factors.append(f"Critical GPA: {gpa:.2f} (Below 2.0)")
    elif gpa < 2.5:
        score += 0.30
        risk_factors.append(f"Low GPA: {gpa:.2f} (Below 2.5)")
    elif gpa < 3.0:
        score += 0.15
        risk_factors.append(f"Borderline GPA: {gpa:.2f}")
    
    # Attendance Analysis (35% weight)
    attendance = float(student_data.get('attendance', 100))
    if attendance < 80:
        score += 0.35
        risk_factors.append(f"Critical Attendance: {attendance:.1f}% (Below 80%)")
    elif attendance < 90:
        score += 0.25
        risk_factors.append(f"Low Attendance: {attendance:.1f}% (Below 90%)")
    elif attendance < 95:
        score += 0.10
        risk_factors.append(f"Borderline Attendance: {attendance:.1f}%")
    
    # Performance Analysis (25% weight)
    performance = student_data.get('performance', 'Average')
    if performance == 'Below Average':
        score += 0.25
        risk_factors.append("Below Average Overall Performance")
    elif performance == 'Average':
        score += 0.10
        risk_factors.append("Average Performance")
    
    # Cap score at 1.0
    score = min(score, 1.0)
    # Normalize for threshold comparison to avoid floating point edge cases
    normalized_score = round(score, 3)
    
    # Determine risk level
    if normalized_score >= RiskThresholds.CRITICAL:
        level = "CRITICAL"
    elif normalized_score >= RiskThresholds.HIGH:
        level = "HIGH"
    elif normalized_score >= RiskThresholds.MODERATE:
        level = "MODERATE"
    else:
        level = "LOW"
    
    return {
        "student_id": student_data.get("student_id"),
        "student_name": student_data.get("name"),
        "risk_score": round(score, 3),
        "risk_level": level,
        "risk_factors": risk_factors,
        "analysis_timestamp": datetime.now().isoformat(),
        "status": "success"
    }


def generate_intervention_plan(risk_level: str):
    """
    Tool 3: Create personalized intervention strategy.
    
    Args:
        risk_level: Risk level (CRITICAL, HIGH, MODERATE, LOW)
        
    Returns:
        Dictionary with intervention plan details
    """
    
    intervention_plans = {
        "CRITICAL": {
            "type": "Emergency Intervention",
            "priority": "URGENT",
            "duration_weeks": 4,
            "frequency": "Daily",
            "actions": [
                "Schedule immediate parent-student-teacher meeting",
                "Assign dedicated academic mentor",
                "Implement daily progress monitoring",
                "Coordinate with school counselor for support",
                "Consider specialized support services (tutoring, counseling)",
                "Create individualized education plan (IEP) if needed",
                "Weekly progress reports to all stakeholders"
            ],
            "resources": [
                "One-on-one tutoring sessions",
                "Study materials and resources",
                "Counseling services",
                "Parent engagement workshops"
            ],
            "success_metrics": [
                "GPA improvement of 0.5+ points",
                "Attendance improvement to 90%+",
                "Completion of all assignments",
                "Positive behavior reports"
            ],
            "estimated_cost": "High ($500-1000/student)",
            "estimated_hours": "10-15 hours/week"
        },
        "HIGH": {
            "type": "Targeted Intervention",
            "priority": "HIGH",
            "duration_weeks": 6,
            "frequency": "3x per week",
            "actions": [
                "Schedule parent-teacher conference within 1 week",
                "Create structured study plan with clear goals",
                "Provide tutoring resources and peer support",
                "Implement weekly check-ins with mentor",
                "Monitor attendance and assignment completion",
                "Bi-weekly progress reports"
            ],
            "resources": [
                "Small group tutoring",
                "Online learning resources",
                "Study guides and materials",
                "Mentorship program"
            ],
            "success_metrics": [
                "GPA improvement of 0.3+ points",
                "Attendance improvement to 92%+",
                "80%+ assignment completion rate",
                "Improved class participation"
            ],
            "estimated_cost": "Medium ($200-500/student)",
            "estimated_hours": "5-8 hours/week"
        },
        "MODERATE": {
            "type": "Preventive Intervention",
            "priority": "MEDIUM",
            "duration_weeks": 8,
            "frequency": "Weekly",
            "actions": [
                "Regular academic check-ins with teacher",
                "Encourage participation in study groups",
                "Provide additional study resources",
                "Foster positive learning environment",
                "Maintain regular parent communication",
                "Monthly progress reviews"
            ],
            "resources": [
                "Study group access",
                "Digital learning resources",
                "After-school programs",
                "Peer mentoring"
            ],
            "success_metrics": [
                "Maintain or improve current GPA",
                "Attendance at 95%+",
                "Consistent assignment completion",
                "Active class participation"
            ],
            "estimated_cost": "Low ($50-200/student)",
            "estimated_hours": "2-4 hours/week"
        },
        "LOW": {
            "type": "Monitoring & Enrichment",
            "priority": "LOW",
            "duration_weeks": 12,
            "frequency": "Monthly",
            "actions": [
                "Continue standard academic monitoring",
                "Celebrate academic successes and achievements",
                "Encourage leadership roles and advanced learning",
                "Support participation in enrichment activities",
                "Maintain positive feedback loop",
                "Quarterly progress reviews"
            ],
            "resources": [
                "Advanced learning materials",
                "Leadership opportunities",
                "Enrichment programs",
                "Recognition programs"
            ],
            "success_metrics": [
                "Maintain high GPA (3.5+)",
                "Perfect or near-perfect attendance",
                "Leadership and mentorship roles",
                "Academic excellence recognition"
            ],
            "estimated_cost": "Minimal ($0-50/student)",
            "estimated_hours": "1-2 hours/week"
        }
    }
    
    plan = intervention_plans.get(risk_level, intervention_plans["LOW"])
    
    # Add timestamp and student context
    plan["created_at"] = datetime.now().isoformat()
    plan["risk_level"] = risk_level
    
    return plan


def predict_intervention_success(risk_level: str):
    """
    Tool 4: Forecast intervention effectiveness and outcomes.
    
    Args:
        risk_level: Risk level (CRITICAL, HIGH, MODERATE, LOW)
        
    Returns:
        Dictionary with success predictions and metrics
    """
    
    # Base success rates by risk level
    success_predictions = {
        "CRITICAL": {
            "base_success_rate": 75,
            "confidence_level": 85,
            "timeline_weeks": 4,
            "expected_gpa_improvement": 0.5,
            "expected_attendance_improvement": 15,
            "factors_affecting_success": [
                "Early intervention timing",
                "Student engagement level",
                "Family support availability",
                "Resource allocation adequacy",
                "Mentor-student relationship quality"
            ],
            "risk_of_failure": [
                "Delayed intervention start",
                "Lack of family engagement",
                "Underlying unaddressed issues",
                "Insufficient resources"
            ]
        },
        "HIGH": {
            "base_success_rate": 82,
            "confidence_level": 85,
            "timeline_weeks": 6,
            "expected_gpa_improvement": 0.4,
            "expected_attendance_improvement": 10,
            "factors_affecting_success": [
                "Consistent tutoring participation",
                "Parent-teacher collaboration",
                "Student motivation level",
                "Peer support engagement"
            ],
            "risk_of_failure": [
                "Inconsistent attendance at support sessions",
                "Lack of study plan adherence",
                "External stressors"
            ]
        },
        "MODERATE": {
            "base_success_rate": 88,
            "confidence_level": 85,
            "timeline_weeks": 8,
            "expected_gpa_improvement": 0.3,
            "expected_attendance_improvement": 5,
            "factors_affecting_success": [
                "Regular check-ins maintained",
                "Study group participation",
                "Positive reinforcement",
                "Resource utilization"
            ],
            "risk_of_failure": [
                "Inconsistent monitoring",
                "Decreased motivation",
                "Competing priorities"
            ]
        },
        "LOW": {
            "base_success_rate": 92,
            "confidence_level": 85,
            "timeline_weeks": 12,
            "expected_gpa_improvement": 0.2,
            "expected_attendance_improvement": 2,
            "factors_affecting_success": [
                "Continued encouragement",
                "Leadership opportunities",
                "Advanced learning access",
                "Recognition and rewards"
            ],
            "risk_of_failure": [
                "Complacency",
                "Boredom from lack of challenge",
                "External life changes"
            ]
        }
    }
    
    prediction = success_predictions.get(risk_level, success_predictions["LOW"])
    
    # Add metadata
    prediction["risk_level"] = risk_level
    prediction["prediction_timestamp"] = datetime.now().isoformat()
    
    return prediction


# ============================================================================
# ENHANCED TOOLS (5-8) - NEW Functionality
# ============================================================================

def generate_alert_email(student_id: str):
    """
    Tool 5 (NEW): Generate professional email notifications for parents/teachers.
    
    Args:
        student_id: The unique identifier of the student (e.g., "S001")
        
    Returns:
        Dictionary with email content and metadata
    """
    # Get student data and risk analysis
    student_data = get_student_data(student_id)
    risk_analysis = analyze_student_risk(student_id)
    intervention_plan = generate_intervention_plan(risk_analysis.get("risk_level", "MODERATE"))
    
    risk_level = risk_analysis.get("risk_level", "MODERATE")
    
    # Email templates by risk level
    email_templates = {
        "CRITICAL": {
            "priority": "URGENT",
            "subject_template": "⚠️ URGENT: {name} - Immediate Academic Support Required",
            "greeting": "Dear Parent/Guardian and Educational Team,",
            "intro": "We are reaching out with urgent concerns about {name}'s academic performance that require immediate attention and collaborative action.",
            "tone": "urgent and direct",
            "call_to_action": "Please contact us IMMEDIATELY to schedule an emergency meeting."
        },
        "HIGH": {
            "priority": "HIGH",
            "subject_template": "📋 Action Required: {name} - Academic Support Recommended",
            "greeting": "Dear Parent/Guardian and Educational Team,",
            "intro": "We are writing regarding {name}'s current academic performance and would like to discuss strategies for improvement.",
            "tone": "concerned but supportive",
            "call_to_action": "Please schedule a meeting with us within the next week to discuss an action plan."
        },
        "MODERATE": {
            "priority": "MEDIUM",
            "subject_template": "📊 Notification: {name} - Academic Progress Update",
            "greeting": "Dear Parent/Guardian,",
            "intro": "We wanted to update you on {name}'s academic progress and share some recommendations for continued success.",
            "tone": "supportive and proactive",
            "call_to_action": "Please review the recommendations and feel free to reach out with any questions."
        }
    }
    
    template = email_templates.get(risk_level, email_templates.get("MODERATE", {}))
    
    # Extract student information
    student_name = student_data.get("name", "Student")
    student_id = student_data.get("student_id", "N/A")
    grade = student_data.get("grade", "N/A")
    gpa = student_data.get("gpa", 0.0)
    attendance = student_data.get("attendance", 0.0)
    
    # Identify specific concerns
    concerns = []
    risk_factors = risk_analysis.get("risk_factors", [])
    
    for factor in risk_factors:
        concerns.append(factor)
    
    # Build email content
    email_subject = template["subject_template"].format(name=student_name)
    
    email_body = f"""{template['greeting']}

{template['intro'].format(name=student_name)}

STUDENT INFORMATION:
• Name: {student_name}
• Student ID: {student_id}
• Grade Level: {grade}
• Current GPA: {gpa:.2f}
• Attendance Rate: {attendance:.1f}%

AREAS OF CONCERN:
"""
    
    for i, concern in enumerate(concerns, 1):
        email_body += f"{i}. {concern}\n"
    
    email_body += f"""
RISK ASSESSMENT:
• Risk Level: {risk_level}
• Risk Score: {risk_analysis.get('risk_score', 0.0):.3f}
• Assessment Date: {datetime.now().strftime('%B %d, %Y')}
"""
    
    # Add intervention plan if available
    if intervention_plan:
        email_body += f"""
RECOMMENDED INTERVENTION:
• Type: {intervention_plan.get('type', 'N/A')}
• Duration: {intervention_plan.get('duration_weeks', 'N/A')} weeks
• Frequency: {intervention_plan.get('frequency', 'N/A')}

KEY ACTIONS:
"""
        actions = intervention_plan.get('actions', [])
        for i, action in enumerate(actions[:5], 1):  # Top 5 actions
            email_body += f"{i}. {action}\n"
    
    email_body += f"""
NEXT STEPS:
{template['call_to_action']}

We are committed to supporting {student_name}'s academic success and appreciate your partnership in this important work.

Sincerely,
Agent Aura Academic Support System

---
This is an automated notification generated by Agent Aura v2.0
For questions, please contact your school's academic support team.
"""
    
    # Create email record
    email_record = {
        "email_generated": True,
        "email_id": f"EMAIL-{student_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "student_id": student_id,
        "student_name": student_name,
        "priority": template["priority"],
        "subject": email_subject,
        "body": email_body,
        "recipients": ["parent/guardian", "teacher", "counselor"],
        "concerns_count": len(concerns),
        "concerns": concerns,
        "risk_level": risk_level,
        "timestamp": datetime.now().isoformat(),
        "status": "generated"
    }
    
    # Log notification
    notification_log.append(email_record)
    
    return email_record


from typing import Union, Dict, Any


def track_student_progress(
    student_id: str,
    risk_level: str,
    risk_score: Union[float, str],
    student_name: str = "",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Tool 6 (NEW): Track and monitor student progress over time.
    
    Args:
        student_id: Student identifier
        risk_level: Current risk level
        risk_score: Current risk score
        student_name: Student name (optional, defaults to empty string)
        notes: Progress notes (optional, defaults to empty string)
        
    Returns:
        Dictionary with tracking status and progress metrics
    """
    
    # Initialize student record if new
    if student_id not in progress_database:
        progress_database[student_id] = {
            "student_id": student_id,
            "student_name": student_name,
            "history": [],
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    # Create progress entry
    # Ensure numeric type for risk_score
    try:
        numeric_score = float(risk_score)
    except (TypeError, ValueError):
        numeric_score = 0.0

    progress_entry = {
        "date": datetime.now().isoformat().split('T')[0],
        "timestamp": datetime.now().isoformat(),
        "risk_level": risk_level,
        "risk_score": numeric_score,
        "notes": notes
    }
    
    # Add to history
    progress_database[student_id]["history"].append(progress_entry)
    progress_database[student_id]["last_updated"] = datetime.now().isoformat()
    
    # Calculate trend analysis
    history = progress_database[student_id]["history"]
    total_entries = len(history)
    
    if total_entries > 1:
        # Get first and last scores
        first_score = float(history[0]["risk_score"]) if history[0]["risk_score"] is not None else 0.0
        current_score = float(history[-1]["risk_score"]) if history[-1]["risk_score"] is not None else 0.0
        
        # Calculate improvement
        score_change = first_score - current_score
        improvement_pct = (score_change / first_score * 100) if first_score > 0 else 0.0
        
        # Determine trend
        if score_change > 0.05:
            trend = "↓ IMPROVING"
            trend_description = f"Risk score decreased by {score_change:.3f}"
        elif score_change < -0.05:
            trend = "↑ WORSENING"
            trend_description = f"Risk score increased by {abs(score_change):.3f}"
        else:
            trend = "→ STABLE"
            trend_description = "Risk score remains relatively stable"
        
        # Calculate days since first entry
        first_date = datetime.fromisoformat(history[0]["timestamp"])
        current_date = datetime.fromisoformat(history[-1]["timestamp"])
        days_tracked = (current_date - first_date).days
    else:
        improvement_pct = 0
        trend = "→ NEW ENTRY"
        trend_description = "First progress entry recorded"
        days_tracked = 0
    
    return {
        "tracking_success": True,
        "student_id": student_id,
        "student_name": student_name,
        "current_risk_level": risk_level,
        "current_risk_score": numeric_score,
        "total_entries": total_entries,
        "days_tracked": days_tracked,
        "improvement_percentage": round(improvement_pct, 1),
        "trend": trend,
        "trend_description": trend_description,
        "last_updated": datetime.now().isoformat(),
        "status": "success"
    }


def get_student_progress_timeline(student_id: str):
    """
    Tool 7 (NEW): Retrieve historical progress data for a student.
    
    Args:
        student_id: Student identifier
        
    Returns:
        Dictionary with complete progress history
    """
    
    if student_id not in progress_database:
        return {
            "error": f"No progress history found for student {student_id}",
            "status": "no_data"
        }
    
    student_record = progress_database[student_id]
    history = student_record["history"]
    
    # Calculate statistics
    if history:
        risk_scores = [float(entry["risk_score"]) for entry in history]
        avg_risk_score = sum(risk_scores) / len(risk_scores)
        min_risk_score = min(risk_scores)
        max_risk_score = max(risk_scores)
        
        # Risk level distribution
        risk_levels = [entry["risk_level"] for entry in history]
        level_counts = {}
        for level in risk_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
    else:
        avg_risk_score = 0
        min_risk_score = 0
        max_risk_score = 0
        level_counts = {}
    
    return {
        "student_id": student_id,
        "student_name": student_record.get("student_name"),
        "total_records": len(history),
        "created_date": student_record["created_date"],
        "last_updated": student_record["last_updated"],
        "progress_history": history,
        "statistics": {
            "average_risk_score": round(avg_risk_score, 3),
            "minimum_risk_score": round(min_risk_score, 3),
            "maximum_risk_score": round(max_risk_score, 3),
            "risk_level_distribution": level_counts
        },
        "status": "success"
    }


def export_progress_visualization_data(student_id: str, format: str = "json"):
    """
    Tool 8 (NEW): Export data formatted for visualization and reporting.
    
    Args:
        student_id: Student identifier
        format: Export format ('json', 'csv', 'chart_data')
        
    Returns:
        Dictionary with formatted visualization data
    """
    
    if student_id not in progress_database:
        return {
            "error": f"No data found for student {student_id}",
            "status": "error"
        }
    
    student_record = progress_database[student_id]
    history = student_record["history"]
    
    # Color mapping for risk levels
    color_map = {
        "CRITICAL": "#FF0000",
        "HIGH": "#FF6B6B",
        "MODERATE": "#FFA500",
        "LOW": "#4CAF50"
    }
    
    # Prepare timeline data
    timeline_points = []
    for entry in history:
        timeline_points.append({
            "date": entry["date"],
            "timestamp": entry["timestamp"],
            "risk_score": entry["risk_score"],
            "risk_level": entry["risk_level"],
            "color": color_map.get(entry["risk_level"], "#999999"),
            "notes": entry.get("notes", "")
        })
    
    # Prepare chart-ready data
    chart_data = {
        "labels": [point["date"] for point in timeline_points],
        "datasets": [
            {
                "label": "Risk Score",
                "data": [point["risk_score"] for point in timeline_points],
                "borderColor": "#3B82F6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "tension": 0.4
            }
        ],
        "risk_levels": [point["risk_level"] for point in timeline_points],
        "colors": [point["color"] for point in timeline_points]
    }
    
    export_data = {
        "student_id": student_id,
        "student_name": student_record.get("student_name"),
        "export_format": format,
        "export_timestamp": datetime.now().isoformat(),
        "timeline_data": timeline_points,
        "chart_data": chart_data,
        "summary": {
            "total_entries": len(timeline_points),
            "date_range": {
                "start": timeline_points[0]["date"] if timeline_points else None,
                "end": timeline_points[-1]["date"] if timeline_points else None
            },
            "current_status": {
                "risk_level": timeline_points[-1]["risk_level"] if timeline_points else None,
                "risk_score": timeline_points[-1]["risk_score"] if timeline_points else None
            }
        },
        "status": "success"
    }
    
    return export_data


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def save_notifications_to_file(filepath: str = "./output/notifications.json"):
    """Save all generated notifications to a file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(notification_log, f, indent=2)
        return {
            "success": True,
            "filepath": filepath,
            "count": len(notification_log)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def save_progress_database_to_file(filepath: str = "./output/progress_database.json"):
    """Save the complete progress database to a file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(progress_database, f, indent=2)
        return {
            "success": True,
            "filepath": filepath,
            "students_tracked": len(progress_database)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def export_summary_report(output_dir: str = "./output"):
    """Export comprehensive summary report in multiple formats."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate summary statistics
        total_students = len(progress_database)
        total_notifications = len(notification_log)
        
        risk_distribution = {}
        for student_id, data in progress_database.items():
            if data["history"]:
                latest_level = data["history"][-1]["risk_level"]
                risk_distribution[latest_level] = risk_distribution.get(latest_level, 0) + 1
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "system": "Agent Aura v2.0",
            "total_students_tracked": total_students,
            "total_notifications_sent": total_notifications,
            "risk_distribution": risk_distribution,
            "progress_database_size": total_students
        }
        
        # Save JSON summary
        json_path = os.path.join(output_dir, "summary_report.json")
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save CSV summary
        csv_path = os.path.join(output_dir, "summary_report.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in summary.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        writer.writerow([f"{key}.{sub_key}", sub_value])
                else:
                    writer.writerow([key, value])
        
        return {
            "success": True,
            "json_report": json_path,
            "csv_report": csv_path,
            "summary": summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
