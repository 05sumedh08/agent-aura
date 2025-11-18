#!/usr/bin/env python
"""
Agent Aura v2.0 - Complete Demonstration Script
Shows the full workflow and capabilities of the multi-agent system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

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
from agent_aura.utils import get_risk_level_emoji


def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def print_section(title):
    """Print section title."""
    print(f"\n{'-'*80}")
    print(f"{title}")
    print(f"{'-'*80}")


def demo_single_student_analysis(student_id="S001"):
    """Demonstrate complete analysis workflow for one student."""
    
    print_header("AGENT AURA v2.0 - SINGLE STUDENT ANALYSIS DEMO")
    
    print(f"📊 Analyzing Student: {student_id}\n")
    
    # Step 1: Data Collection
    print_section("Step 1: DATA COLLECTION")
    student_data = get_student_data(student_id)
    
    if student_data["status"] == "error":
        print(f"❌ Error: {student_data['error']}")
        return None
    
    print(f"✓ Student Retrieved: {student_data['name']}")
    print(f"  • Grade Level: {student_data['grade']}")
    print(f"  • GPA: {student_data['gpa']:.2f}")
    print(f"  • Attendance: {student_data['attendance']:.1f}%")
    print(f"  • Performance: {student_data['performance']}")
    
    # Step 2: Risk Analysis
    print_section("Step 2: RISK ANALYSIS")
    risk_analysis = analyze_student_risk(student_id)
    
    emoji = get_risk_level_emoji(risk_analysis["risk_level"])
    print(f"✓ Risk Assessment Complete")
    print(f"  • Risk Level: {emoji} {risk_analysis['risk_level']}")
    print(f"  • Risk Score: {risk_analysis['risk_score']:.3f}")
    print(f"  • Risk Factors:")
    for factor in risk_analysis["risk_factors"]:
        print(f"    - {factor}")
    
    # Step 3: Intervention Planning
    print_section("Step 3: INTERVENTION PLANNING")
    plan = generate_intervention_plan(risk_analysis["risk_level"])
    
    print(f"✓ Intervention Plan Generated")
    print(f"  • Type: {plan['type']}")
    print(f"  • Priority: {plan['priority']}")
    print(f"  • Duration: {plan['duration_weeks']} weeks")
    print(f"  • Frequency: {plan['frequency']}")
    print(f"  • Estimated Cost: {plan['estimated_cost']}")
    print(f"  • Key Actions:")
    for i, action in enumerate(plan['actions'][:3], 1):
        print(f"    {i}. {action}")
    
    # Step 4: Success Prediction
    print_section("Step 4: OUTCOME PREDICTION")
    prediction = predict_intervention_success(risk_analysis["risk_level"])
    
    print(f"✓ Success Forecast Generated")
    print(f"  • Expected Success Rate: {prediction['base_success_rate']}%")
    print(f"  • Confidence Level: {prediction['confidence_level']}%")
    print(f"  • Timeline: {prediction['timeline_weeks']} weeks")
    print(f"  • Expected GPA Improvement: +{prediction['expected_gpa_improvement']}")
    print(f"  • Expected Attendance Improvement: +{prediction['expected_attendance_improvement']}%")
    
    # Step 5: Email Notification (for HIGH/CRITICAL only)
    print_section("Step 5: AUTOMATED NOTIFICATION")
    if risk_analysis["risk_level"] in ["CRITICAL", "HIGH"]:
        email = generate_alert_email(student_id)
        print(f"✓ Email Notification Generated")
        print(f"  • Priority: {email['priority']}")
        print(f"  • Email ID: {email['email_id']}")
        print(f"  • Subject: {email['subject']}")
        print(f"  • Recipients: {', '.join(email['recipients'])}")
        print(f"  • Concerns Count: {email['concerns_count']}")
    else:
        print(f"✓ No immediate notification required (Risk Level: {risk_analysis['risk_level']})")
    
    # Step 6: Progress Tracking
    print_section("Step 6: PROGRESS TRACKING")
    progress = track_student_progress(
        student_id,
        risk_analysis["risk_level"],
        float(risk_analysis["risk_score"]),
        student_data["name"]
    )
    
    print(f"✓ Progress Record Created")
    print(f"  • Student ID: {progress['student_id']}")
    print(f"  • Current Risk: {progress['current_risk_level']} ({progress['current_risk_score']:.3f})")
    print(f"  • Trend: {progress['trend']}")
    print(f"  • Total Entries: {progress['total_entries']}")
    print(f"  • Days Tracked: {progress['days_tracked']}")
    
    return {
        "student_data": student_data,
        "risk_analysis": risk_analysis,
        "plan": plan,
        "prediction": prediction
    }


def demo_batch_analysis():
    """Demonstrate batch processing of multiple students."""
    
    print_header("AGENT AURA v2.0 - BATCH ANALYSIS DEMO")
    
    # Select diverse risk levels
    student_ids = ["S001", "S002", "S005", "S011", "S015", "S019", "S004", "S008"]
    
    print(f"📊 Batch Analyzing {len(student_ids)} Students\n")
    
    results = []
    notifications_sent = 0
    
    print(f"{'#':<3} {'Student ID':<12} {'Name':<20} {'Risk':<10} {'Score':<8} {'Notif'}")
    print(f"{'-'*80}")
    
    for i, student_id in enumerate(student_ids, 1):
        # Get data and analyze
        student_data = get_student_data(student_id)
        if student_data["status"] == "error":
            continue
        
        risk = analyze_student_risk(student_id)
        
        # Generate notification if needed
        notif_sent = ""
        if risk["risk_level"] in ["CRITICAL", "HIGH"]:
            generate_alert_email(student_id)
            notifications_sent += 1
            notif_sent = "📧"
        
        # Track progress
        track_student_progress(
            student_id,
            risk["risk_level"],
            float(risk["risk_score"]),
            student_data["name"]
        )
        
        # Display result
        emoji = get_risk_level_emoji(risk["risk_level"])
        print(f"{i:<3} {student_id:<12} {student_data['name']:<20} {emoji} {risk['risk_level']:<8} {risk['risk_score']:<8.3f} {notif_sent}")
        
        results.append({
            "student_id": student_id,
            "name": student_data["name"],
            "risk_level": risk["risk_level"],
            "risk_score": risk["risk_score"]
        })
    
    # Calculate statistics
    risk_distribution = {}
    for result in results:
        level = result["risk_level"]
        risk_distribution[level] = risk_distribution.get(level, 0) + 1
    
    print(f"\n{'-'*80}")
    print(f"BATCH ANALYSIS SUMMARY")
    print(f"{'-'*80}")
    print(f"Total Students Analyzed: {len(results)}")
    print(f"Notifications Sent: {notifications_sent}")
    print(f"\nRisk Distribution:")
    for level in ["CRITICAL", "HIGH", "MODERATE", "LOW"]:
        count = risk_distribution.get(level, 0)
        pct = (count / len(results) * 100) if results else 0
        emoji = get_risk_level_emoji(level)
        print(f"  {emoji} {level:<10}: {count:2d} students ({pct:5.1f}%)")
    
    return results


def demo_progress_tracking():
    """Demonstrate progress tracking over time."""
    
    print_header("AGENT AURA v2.0 - PROGRESS TRACKING DEMO")
    
    student_id = "S001"
    
    print(f"📈 Tracking Progress for Student: {student_id}\n")
    
    # Simulate progress over time (improving risk scores)
    student_data = get_student_data(student_id)
    initial_risk = analyze_student_risk(student_id)
    
    print_section("Tracking Multiple Progress Points")
    
    # Initial entry
    track_student_progress(
        student_id,
        initial_risk["risk_level"],
        float(initial_risk["risk_score"]),
        student_data["name"],
        "Initial assessment - intervention started"
    )
    print(f"✓ Entry 1: Risk Score {initial_risk['risk_score']:.3f} - Intervention Started")
    
    # Simulate improvement over weeks
    improvements = [
        (0.750, "Week 2 - Showing early progress"),
        (0.680, "Week 4 - Continued improvement"),
        (0.600, "Week 6 - Moderate risk level achieved")
    ]
    
    for i, (score, note) in enumerate(improvements, 2):
        # Determine new risk level
        if score >= 0.90:
            level = "CRITICAL"
        elif score >= 0.80:
            level = "HIGH"
        elif score >= 0.60:
            level = "MODERATE"
        else:
            level = "LOW"
        
        track_student_progress(student_id, level, score, student_data["name"], note)
        print(f"✓ Entry {i}: Risk Score {score:.3f} - {note}")
    
    # Get complete timeline
    print_section("Retrieving Progress Timeline")
    timeline = get_student_progress_timeline(student_id)
    
    print(f"✓ Timeline Retrieved")
    print(f"  • Total Records: {timeline['total_records']}")
    print(f"  • Average Risk Score: {timeline['statistics']['average_risk_score']:.3f}")
    print(f"  • Minimum Risk Score: {timeline['statistics']['minimum_risk_score']:.3f}")
    print(f"  • Maximum Risk Score: {timeline['statistics']['maximum_risk_score']:.3f}")
    print(f"  • Risk Level Distribution: {timeline['statistics']['risk_level_distribution']}")
    
    # Export visualization data
    print_section("Exporting Visualization Data")
    viz_data = export_progress_visualization_data(student_id, "json")
    
    print(f"✓ Visualization Data Exported")
    print(f"  • Format: {viz_data['export_format']}")
    print(f"  • Timeline Points: {len(viz_data['timeline_data'])}")
    print(f"  • Current Status: {viz_data['summary']['current_status']['risk_level']} ({viz_data['summary']['current_status']['risk_score']:.3f})")
    print(f"  • Date Range: {viz_data['summary']['date_range']['start']} to {viz_data['summary']['date_range']['end']}")
    
    return timeline, viz_data


def demo_report_export():
    """Demonstrate comprehensive report export."""
    
    print_header("AGENT AURA v2.0 - REPORT EXPORT DEMO")
    
    output_dir = "./output"
    
    print(f"📁 Exporting Reports to: {output_dir}\n")
    
    # Export notifications
    print_section("Exporting Notifications")
    notif_result = save_notifications_to_file(f"{output_dir}/notifications.json")
    if notif_result["success"]:
        print(f"✓ Saved {notif_result['count']} notifications")
        print(f"  • File: {notif_result['filepath']}")
    
    # Export progress database
    print_section("Exporting Progress Database")
    prog_result = save_progress_database_to_file(f"{output_dir}/progress_database.json")
    if prog_result["success"]:
        print(f"✓ Saved {prog_result['students_tracked']} student records")
        print(f"  • File: {prog_result['filepath']}")
    
    # Export summary report
    print_section("Exporting Summary Report")
    summary_result = export_summary_report(output_dir)
    if summary_result["success"]:
        print(f"✓ Summary reports generated")
        print(f"  • JSON: {summary_result['json_report']}")
        print(f"  • CSV: {summary_result['csv_report']}")
        print(f"\nSummary Statistics:")
        for key, value in summary_result['summary'].items():
            if isinstance(value, dict):
                print(f"  • {key}:")
                for k, v in value.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"  • {key}: {value}")
    
    return summary_result


def main():
    """Run complete demonstration."""
    
    print("\n")
    print("="*80)
    print("AGENT AURA v2.0 - COMPREHENSIVE DEMONSTRATION".center(80))
    print("Multi-Agent AI System for K-12 Student Intervention".center(80))
    print("="*80)
    
    # Demo 1: Single Student Analysis
    demo_single_student_analysis("S001")
    
    # Demo 2: Batch Analysis
    demo_batch_analysis()
    
    # Demo 3: Progress Tracking
    demo_progress_tracking()
    
    # Demo 4: Report Export
    demo_report_export()
    
    # Final Summary
    print_header("DEMONSTRATION COMPLETE")
    
    print("✅ All Agent Aura Features Demonstrated:")
    print("   1. ✓ Single Student Analysis (Complete Workflow)")
    print("   2. ✓ Batch Processing (Multiple Students)")
    print("   3. ✓ Progress Tracking (Timeline & Trends)")
    print("   4. ✓ Report Export (JSON, CSV, Notifications)")
    print("\n🎯 Agent Aura v2.0 is fully operational!")
    print(f"\n📁 Check the ./output/ directory for generated reports.\n")


if __name__ == "__main__":
    main()
