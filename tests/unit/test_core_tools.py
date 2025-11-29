import pytest
from agent_aura.tools import (
    get_student_data,
    analyze_student_risk,
    generate_intervention_plan,
    predict_intervention_success,
    generate_alert_email,
    track_student_progress,
    get_student_progress_timeline,
    export_progress_visualization_data,
    RiskThresholds,
)

DATA_PATH = "./data/student_data.csv"

 
@pytest.mark.parametrize("student_id,expected_level,expected_score", [
    ("S011", "CRITICAL", 1.0),           # GPA <2.0 + Attendance <80 + Below Average => capped
    ("S015", "CRITICAL", 0.90),           # Aggregated 0.30 + 0.35 + 0.25
    ("S005", "HIGH", 0.80),               # 0.30 + 0.25 + 0.25
    ("S002", "LOW", 0.20),                # 0.10 attendance borderline + 0.10 average performance
    ("S003", "LOW", 0.50),                # 0.15 + 0.25 + 0.10
])
def test_risk_analysis_levels(student_id, expected_level, expected_score):
    result = analyze_student_risk(student_id)
    assert result["status"] == "success"
    assert result["risk_level"] == expected_level
    assert pytest.approx(result["risk_score"], rel=0.01) == expected_score


def test_student_data_valid():
    data = get_student_data("S001", DATA_PATH)
    assert data["status"] == "success"
    assert data["student_id"] == "S001"
    assert isinstance(data["gpa"], float)


def test_student_data_not_found():
    not_found = get_student_data("S999", DATA_PATH)
    assert not_found["status"] == "error"
    assert "not found" in not_found["error"].lower()


@pytest.mark.parametrize("level,base_success", [
    ("CRITICAL", 75),
    ("HIGH", 82),
    ("MODERATE", 88),
    ("LOW", 92),
])
def test_predict_intervention_success(level, base_success):
    prediction = predict_intervention_success(level)
    assert prediction["risk_level"] == level
    assert prediction["base_success_rate"] == base_success
    assert 0 < prediction["confidence_level"] <= 100


@pytest.mark.parametrize("level,expected_type", [
    ("CRITICAL", "Emergency Intervention"),
    ("HIGH", "Targeted Intervention"),
    ("MODERATE", "Preventive Intervention"),
    ("LOW", "Monitoring & Enrichment"),
])
def test_generate_intervention_plan(level, expected_type):
    plan = generate_intervention_plan(level)
    assert plan["risk_level"] == level
    assert plan["type"] == expected_type
    assert isinstance(plan["actions"], list) and len(plan["actions"]) >= 4


def test_generate_alert_email_structure():
    # Choose a high-risk student to ensure email generation includes concerns
    email = generate_alert_email("S011")
    assert email["email_generated"] is True
    assert email["student_id"] == "S011"
    assert email["priority"] in {"URGENT", "HIGH", "MEDIUM"}
    assert len(email["body"]) > 100
    assert "RISK ASSESSMENT" in email["body"]


def test_progress_tracking_and_timeline():
    # Track multiple entries to produce a timeline
    student_id = "S003"
    risk1 = analyze_student_risk(student_id)
    first = track_student_progress(student_id, risk1["risk_level"], risk1["risk_score"], risk1["student_name"])
    assert first["tracking_success"]

    # Simulate improvement by lowering score
    # Ensure numeric operation by casting risk_score to float
    improved_score = max(float(risk1["risk_score"]) - 0.15, 0.0)
    track_student_progress(student_id, risk1["risk_level"], improved_score, risk1["student_name"], notes="Follow-up session")

    timeline = get_student_progress_timeline(student_id)
    assert timeline["status"] == "success"
    # Ensure numeric comparison by casting potential string values to int
    assert int(timeline["total_records"]) >= 2
    assert "progress_history" in timeline

    export_data = export_progress_visualization_data(student_id)
    assert export_data["status"] == "success"
    # Align comparisons by casting to int in case of string counts
    # Handle cases where summary may be a dict or a list containing a dict
    summary = export_data.get("summary")
    if isinstance(summary, dict):
        total_entries = summary.get("total_entries", 0)
    elif isinstance(summary, list) and summary and isinstance(summary[0], dict):
        total_entries = summary[0].get("total_entries", 0)
    else:
        total_entries = 0
    assert int(total_entries) == int(timeline["total_records"])
    assert len(export_data["timeline_data"]) == int(timeline["total_records"])


def test_risk_threshold_constants():
    assert RiskThresholds.CRITICAL == 0.90
    assert RiskThresholds.HIGH == 0.80
    assert RiskThresholds.MODERATE == 0.60
    assert RiskThresholds.LOW == 0.30
