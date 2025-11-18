#!/usr/bin/env python3
"""
Simple demo server for Agent Aura - No authentication required
Loads student data and provides simple API endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import json
from pathlib import Path

# Initialize FastAPI
app = FastAPI(title="Agent Aura Demo API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load student data
STUDENT_DATA_FILE = Path(__file__).parent / "data" / "student_data.csv"
students_df = None

try:
    students_df = pd.read_csv(STUDENT_DATA_FILE)
    print(f"✅ Loaded {len(students_df)} students from CSV")
except Exception as e:
    print(f"⚠️  Error loading student data: {e}")
    students_df = pd.DataFrame()


# Pydantic models
class Student(BaseModel):
    student_id: str
    name: str
    grade_level: int
    gpa: float
    attendance_rate: float
    overall_performance: str
    risk_level: str
    risk_score: float


def calculate_risk(row):
    """Calculate risk level for a student."""
    score = 0.0
    
    # GPA risk (40%)
    if row['gpa'] < 2.0:
        score += 0.40
    elif row['gpa'] < 2.5:
        score += 0.30
    elif row['gpa'] < 3.0:
        score += 0.15
    
    # Attendance risk (40%)
    if row['attendance_rate'] < 0.80:
        score += 0.40
    elif row['attendance_rate'] < 0.85:
        score += 0.30
    elif row['attendance_rate'] < 0.90:
        score += 0.15
    
    # Performance risk (20%)
    perf_map = {
        'Below Average': 0.20,
        'Average': 0.10,
        'Above Average': 0.05,
        'Excellent': 0.0
    }
    score += perf_map.get(row['overall_performance'], 0.10)
    
    # Determine level
    if score >= 0.75:
        level = 'CRITICAL'
    elif score >= 0.60:
        level = 'HIGH'
    elif score >= 0.40:
        level = 'MODERATE'
    else:
        level = 'LOW'
    
    return level, round(score, 2)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agent Aura Demo API",
        "version": "2.0.0",
        "students": len(students_df) if students_df is not None else 0
    }


@app.get("/api/students", response_model=List[Student])
async def get_all_students():
    """Get all students with risk assessments."""
    if students_df is None or students_df.empty:
        return []
    
    students = []
    for _, row in students_df.iterrows():
        risk_level, risk_score = calculate_risk(row)
        students.append({
            "student_id": row['student_id'],
            "name": row['name'],
            "grade_level": int(row['grade_level']),
            "gpa": float(row['gpa']),
            "attendance_rate": float(row['attendance_rate']),
            "overall_performance": row['overall_performance'],
            "risk_level": risk_level,
            "risk_score": risk_score
        })
    
    return students


@app.get("/api/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    """Get specific student details."""
    if students_df is None or students_df.empty:
        return {"error": "No student data available"}
    
    student_row = students_df[students_df['student_id'] == student_id]
    
    if student_row.empty:
        return {"error": "Student not found"}
    
    row = student_row.iloc[0]
    risk_level, risk_score = calculate_risk(row)
    
    return {
        "student_id": row['student_id'],
        "name": row['name'],
        "grade_level": int(row['grade_level']),
        "gpa": float(row['gpa']),
        "attendance_rate": float(row['attendance_rate']),
        "overall_performance": row['overall_performance'],
        "risk_level": risk_level,
        "risk_score": risk_score
    }


@app.get("/api/stats")
async def get_statistics():
    """Get overall statistics."""
    if students_df is None or students_df.empty:
        return {"error": "No data"}
    
    # Calculate risk for all students
    risks = []
    for _, row in students_df.iterrows():
        level, score = calculate_risk(row)
        risks.append(level)
    
    from collections import Counter
    risk_counts = Counter(risks)
    
    return {
        "total_students": len(students_df),
        "average_gpa": float(students_df['gpa'].mean()),
        "average_attendance": float(students_df['attendance_rate'].mean()),
        "risk_distribution": dict(risk_counts),
        "critical_count": risk_counts.get('CRITICAL', 0),
        "high_count": risk_counts.get('HIGH', 0),
        "moderate_count": risk_counts.get('MODERATE', 0),
        "low_count": risk_counts.get('LOW', 0)
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Agent Aura Demo Server...")
    print(f"📊 Loaded {len(students_df)} students")
    print("🌐 Server running at http://localhost:5001")
    print("📖 API docs at http://localhost:5001/docs")
    uvicorn.run(app, host="0.0.0.0", port=5001)
