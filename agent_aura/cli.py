# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Command-line interface for Agent Aura.
Provides easy access to all agent functionality from the terminal.
"""

import argparse
import json
import sys
import os
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_aura.tools import (
    get_student_data,
    analyze_student_risk,
    generate_intervention_plan,
    predict_intervention_success,
    generate_alert_email,
    track_student_progress,
    get_student_progress_timeline,
    export_progress_visualization_data,
    save_notifications_to_file,
    save_progress_database_to_file,
    export_summary_report
)
from agent_aura.utils import (
    format_risk_summary,
    format_intervention_summary,
    get_risk_level_emoji
)


def analyze_student(student_id: str, data_file: str = "./data/student_data.csv", verbose: bool = False):
    """Analyze a single student and generate complete report."""
    
    print(f"\n{'='*80}")
    print(f"AGENT AURA - STUDENT ANALYSIS")
    print(f"{'='*80}\n")
    
    # Step 1: Data Collection
    print(f"[1/6] Collecting data for student {student_id}...")
    student_data = get_student_data(student_id, data_file)
    
    if student_data.get("status") == "error":
        print(f"❌ Error: {student_data.get('error')}")
        return
    
    print(f"[OK] Student: {student_data['name']} (Grade {student_data['grade']})")
    if verbose:
        print(f"  GPA: {student_data['gpa']:.2f}")
        print(f"  Attendance: {student_data['attendance']:.1f}%")
        print(f"  Performance: {student_data['performance']}")
    
    # Step 2: Risk Analysis
    print(f"\n[2/6] Analyzing risk factors...")
    risk_analysis = analyze_student_risk(student_id)
    
    emoji = get_risk_level_emoji(risk_analysis["risk_level"])
    print(f"[OK] Risk Level: {emoji} {risk_analysis['risk_level']} (Score: {risk_analysis['risk_score']:.3f})")
    
    if verbose and risk_analysis["risk_factors"]:
        print(f"  Risk Factors:")
        for factor in risk_analysis["risk_factors"]:
            print(f"    • {factor}")
    
    # Step 3: Intervention Planning
    print(f"\n[3/6] Generating intervention plan...")
    plan = generate_intervention_plan(risk_analysis["risk_level"])
    print(f"[OK] Plan Type: {plan['type']}")
    print(f"  Duration: {plan['duration_weeks']} weeks")
    print(f"  Frequency: {plan['frequency']}")
    
    # Step 4: Success Prediction
    print(f"\n[4/6] Predicting intervention success...")
    prediction = predict_intervention_success(risk_analysis["risk_level"])
    print(f"[OK] Expected Success Rate: {prediction['base_success_rate']}%")
    print(f"  Confidence: {prediction['confidence_level']}%")
    print(f"  Timeline: {prediction['timeline_weeks']} weeks")
    
    # Step 5: Generate Notification (if needed)
    print(f"\n[5/6] Checking notification requirements...")
    if risk_analysis["risk_level"] in ["CRITICAL", "HIGH"]:
        email = generate_alert_email(student_id)
        print(f"[OK] Notification generated: {email['priority']} priority")
        if verbose:
            print(f"  Subject: {email['subject']}")
    else:
        print(f"[OK] No immediate notification required")
    
    # Step 6: Track Progress
    print(f"\n[6/6] Tracking progress...")
    progress = track_student_progress(
        student_id,
        risk_analysis["risk_level"],
        float(risk_analysis["risk_score"]),
        student_data["name"]
    )
    print(f"[OK] Progress tracked: {progress['trend']}")
    
    print(f"\n{'='*80}")
    print(f"✅ ANALYSIS COMPLETE")
    print(f"{'='*80}\n")


def batch_analyze(student_ids: List[str], data_file: str = "./data/student_data.csv"):
    """Batch analyze multiple students."""
    
    print(f"\n{'='*80}")
    print(f"AGENT AURA - BATCH ANALYSIS")
    print(f"{'='*80}\n")
    print(f"Analyzing {len(student_ids)} students...\n")
    
    results = []
    notifications = 0
    
    for i, student_id in enumerate(student_ids, 1):
        student_data = get_student_data(student_id, data_file)
        
        if student_data.get("status") == "error":
            print(f"[{i:2d}/{len(student_ids)}] ❌ {student_id} - Error")
            continue
        
        risk = analyze_student_risk(student_id)
        emoji = get_risk_level_emoji(risk["risk_level"])
        
        # Generate notification if needed
        if risk["risk_level"] in ["CRITICAL", "HIGH"]:
            generate_alert_email(student_id)
            notifications += 1
            notif_icon = "📧"
        else:
            notif_icon = "  "
        
        # Track progress
        track_student_progress(
            student_id,
            risk["risk_level"],
            float(risk["risk_score"]),
            student_data["name"]
        )
        
        results.append({
            "student_id": student_id,
            "name": student_data["name"],
            "risk_level": risk["risk_level"],
            "risk_score": risk["risk_score"]
        })
        
        print(f"[{i:2d}/{len(student_ids)}] {emoji} {student_data['name']:20s} | {risk['risk_level']:10s} | {risk['risk_score']:.3f} {notif_icon}")
    
    # Summary statistics
    risk_dist = {}
    for r in results:
        level = r["risk_level"]
        risk_dist[level] = risk_dist.get(level, 0) + 1
    
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total Analyzed: {len(results)}")
    print(f"Notifications Sent: {notifications}")
    print(f"\nRisk Distribution:")
    for level in ["CRITICAL", "HIGH", "MODERATE", "LOW"]:
        count = risk_dist.get(level, 0)
        pct = (count / len(results) * 100) if results else 0
        emoji = get_risk_level_emoji(level)
        print(f"  {emoji} {level:10s}: {count:2d} ({pct:5.1f}%)")
    print(f"{'='*80}\n")


def export_reports(output_dir: str = "./output", format: str = "all"):
    """Export comprehensive reports."""
    
    print(f"\n{'='*80}")
    print(f"AGENT AURA - EXPORT REPORTS")
    print(f"{'='*80}\n")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if format in ["all", "notifications"]:
        print("Exporting notifications...")
        result = save_notifications_to_file(f"{output_dir}/notifications.json")
        if result["success"]:
            print(f"[OK] Saved {result['count']} notifications to {result['filepath']}")
    
    if format in ["all", "progress"]:
        print("Exporting progress database...")
        result = save_progress_database_to_file(f"{output_dir}/progress_database.json")
        if result["success"]:
            print(f"[OK] Saved {result['students_tracked']} student records to {result['filepath']}")
    
    if format in ["all", "summary"]:
        print("Generating summary report...")
        result = export_summary_report(output_dir)
        if result["success"]:
            print(f"[OK] JSON report: {result['json_report']}")
            print(f"[OK] CSV report: {result['csv_report']}")
    
    print(f"\n{'='*80}")
    print(f"✅ EXPORT COMPLETE")
    print(f"{'='*80}\n")


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="Agent Aura v2.0 - Multi-Agent Student Intervention System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single student
  python -m agent_aura.cli analyze --student-id S001
  
  # Batch analyze multiple students
  python -m agent_aura.cli batch --student-ids S001,S002,S003
  
  # Export reports
  python -m agent_aura.cli export --format all --output ./output
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a single student")
    analyze_parser.add_argument("--student-id", required=True, help="Student ID")
    analyze_parser.add_argument("--data-file", default="./data/student_data.csv", help="Path to student data CSV")
    analyze_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch analyze multiple students")
    batch_parser.add_argument("--student-ids", required=True, help="Comma-separated student IDs")
    batch_parser.add_argument("--data-file", default="./data/student_data.csv", help="Path to student data CSV")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export reports")
    export_parser.add_argument("--format", choices=["all", "notifications", "progress", "summary"], default="all", help="Export format")
    export_parser.add_argument("--output", default="./output", help="Output directory")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        analyze_student(args.student_id, args.data_file, args.verbose)
    elif args.command == "batch":
        student_ids = [sid.strip() for sid in args.student_ids.split(",")]
        batch_analyze(student_ids, args.data_file)
    elif args.command == "export":
        export_reports(args.output, args.format)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
