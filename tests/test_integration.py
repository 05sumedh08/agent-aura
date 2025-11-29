# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Integration tests for Agent Aura multi-agent system.
Tests the complete workflow from data collection to outcome prediction.
"""

import sys
import os

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
    export_progress_visualization_data
)


class TestIntegration:
    """Integration tests for Agent Aura system."""
    
    def test_complete_workflow(self):
        """Test complete analysis workflow for a student."""
        
        # Step 1: Data Collection
        student_data = get_student_data("S001", "./data/student_data.csv")
        assert student_data["status"] == "success"
        assert "student_id" in student_data
        assert "name" in student_data
        
        # Step 2: Risk Analysis
        risk_analysis = analyze_student_risk("S001")
        assert risk_analysis["status"] == "success"
        assert "risk_score" in risk_analysis
        assert "risk_level" in risk_analysis
        assert risk_analysis["risk_level"] in ["CRITICAL", "HIGH", "MODERATE", "LOW"]
        
        # Step 3: Generate Intervention Plan
        plan = generate_intervention_plan(
            risk_analysis["risk_level"]
        )
        assert "type" in plan
        assert "duration_weeks" in plan
        assert "actions" in plan
        
        # Step 4: Predict Success
        prediction = predict_intervention_success(
            risk_analysis["risk_level"]
        )
        assert "base_success_rate" in prediction
        assert "confidence_level" in prediction
        
        # Step 5: Generate Notification (if HIGH/CRITICAL)
        if risk_analysis["risk_level"] in ["HIGH", "CRITICAL"]:
            email = generate_alert_email("S001")
            assert email["email_generated"] is True
            assert "subject" in email
            assert "body" in email
        
        # Step 6: Track Progress
        progress = track_student_progress(
            student_data["student_id"],
            risk_analysis["risk_level"],
            float(risk_analysis["risk_score"]),
            student_data["name"]
        )
        assert progress["tracking_success"] is True
        assert progress["student_id"] == student_data["student_id"]
        
        print("[OK] Complete workflow test passed!")
    
    def test_multiple_students_batch(self):
        """Test batch processing of multiple students."""
        
        student_ids = ["S001", "S002", "S003", "S004", "S005"]
        results = []
        
        for student_id in student_ids:
            # Data collection
            student_data = get_student_data(student_id, "./data/student_data.csv")
            if student_data["status"] == "error":
                continue
            
            # Risk analysis
            risk = analyze_student_risk(student_id)
            
            # Track progress
            progress = track_student_progress(
                student_id,
                risk["risk_level"],
                float(risk["risk_score"]),
                student_data["name"]
            )
            
            results.append({
                "student_id": student_id,
                "risk_level": risk["risk_level"],
                "risk_score": risk["risk_score"],
                "tracking": progress["tracking_success"]
            })
        
        assert len(results) == len(student_ids)
        assert all(r["tracking"] is True for r in results)
        
        print(f"[OK] Batch processing test passed! Processed {len(results)} students")
    
    def test_progress_timeline_retrieval(self):
        """Test retrieving progress timeline after tracking."""
        
        # First track some progress
        student_id = "S006"
        student_data = get_student_data(student_id, "./data/student_data.csv")
        risk = analyze_student_risk(student_id)
        
        # Track progress multiple times
        for i in range(3):
            track_student_progress(
                student_id,
                risk["risk_level"],
                float(risk["risk_score"]) - (i * 0.1),  # Simulate improvement
                student_data["name"]
            )
        
        # Retrieve timeline
        timeline = get_student_progress_timeline(student_id)
        assert timeline["status"] == "success"
        assert timeline["total_records"] == 3
        assert "progress_history" in timeline
        assert len(timeline["progress_history"]) == 3
        
        print("[OK] Progress timeline test passed!")
    
    def test_visualization_data_export(self):
        """Test exporting visualization data."""
        
        # Track some progress first
        student_id = "S007"
        student_data = get_student_data(student_id, "./data/student_data.csv")
        risk = analyze_student_risk(student_id)
        
        track_student_progress(
            student_id,
            risk["risk_level"],
            float(risk["risk_score"]),
            student_data["name"]
        )
        
        # Export visualization data
        viz_data = export_progress_visualization_data(student_id, "json")
        assert viz_data["status"] == "success"
        assert "timeline_data" in viz_data
        assert "chart_data" in viz_data
        assert "summary" in viz_data
        
        print("[OK] Visualization export test passed!")


if __name__ == "__main__":
    # Run tests
    test = TestIntegration()
    
    print("="*80)
    print("AGENT AURA - INTEGRATION TESTS")
    print("="*80)
    print()
    
    test.test_complete_workflow()
    print()
    
    test.test_multiple_students_batch()
    print()
    
    test.test_progress_timeline_retrieval()
    print()
    
    test.test_visualization_data_export()
    print()
    
    print("="*80)
    print("[SUCCESS] ALL INTEGRATION TESTS PASSED!")
    print("="*80)
