# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
FastAPI main application for Agent Aura Backend.
RESTful API with streaming agent responses and role-based access control.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the backend directory (parent of app directory)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

from app.models.database import (
    User, UserRole, Student, Teacher, Admin,
    AgentSession, SessionEvent, RiskAssessment,
    Intervention, ProgressRecord,
    get_db, init_database
)
from app.services.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    require_admin, require_teacher, require_student,
    check_student_access, create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.services.auth import oauth2_scheme, decode_access_token
from app.agent_core.agent import Agent
from app.agent_core.orchestrator import MultiAgentOrchestrator

# Initialize FastAPI app
app = FastAPI(
    title="Agent Aura API",
    description="Multi-agent AI system for K-12 student intervention with Glass Box UI",
    version="2.0.0"
)

# CORS middleware - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================================
# Pydantic Models for API
# ============================================================================

from pydantic import BaseModel, EmailStr
from typing import Optional, List


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    full_name: str
    # Role-specific fields
    student_id: Optional[str] = None
    teacher_id: Optional[str] = None
    grade: Optional[int] = None
    gpa: Optional[float] = None
    attendance: Optional[float] = None
    subject: Optional[str] = None
    department: Optional[str] = None


class AgentGoalRequest(BaseModel):
    goal: str
    session_id: Optional[str] = None
    student_id: Optional[str] = None
    enabled_agents: Optional[List[str]] = None


class StudentResponse(BaseModel):
    student_id: str
    full_name: str
    grade: int
    gpa: float
    attendance: float
    parent_email: Optional[str]


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "agent-aura-backend",
        "version": "2.0.0"
    }


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/v1/auth/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Only admin can create users
):
    """Register a new user (admin only)."""
    
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    try:
        role_map = {"admin": UserRole.ADMIN, "teacher": UserRole.TEACHER, "student": UserRole.STUDENT}
        new_user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=role_map[user_data.role],
            full_name=user_data.full_name,
            student_id=user_data.student_id,
            teacher_id=user_data.teacher_id,
            grade=user_data.grade,
            gpa=user_data.gpa or 0.0,
            attendance=user_data.attendance or 100.0,
            subject=user_data.subject,
            department=user_data.department
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": new_user.role.value,
            "user_id": new_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    # Authenticate user against database
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "user_id": user.id
    }


@app.get("/api/v1/auth/me")
async def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user information from database."""
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        
        # Query user from database
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build user response based on role
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }
        
        # Add role-specific data
        if user.role == UserRole.ADMIN and user.admin_profile:
            user_data["full_name"] = user.admin_profile.full_name
            user_data["department"] = user.admin_profile.department
        elif user.role == UserRole.TEACHER and user.teacher_profile:
            user_data["teacher_id"] = user.teacher_profile.teacher_id
            user_data["full_name"] = user.teacher_profile.full_name
            user_data["subject"] = user.teacher_profile.subject
            user_data["grade_level"] = user.teacher_profile.grade_level
        elif user.role == UserRole.STUDENT and user.student_profile:
            user_data["student_id"] = user.student_profile.student_id
            user_data["full_name"] = user.student_profile.full_name
            user_data["grade"] = user.student_profile.grade
            user_data["gpa"] = user.student_profile.gpa
            user_data["attendance"] = user.student_profile.attendance
        
        return user_data
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# ============================================================================
# Student Data Endpoints
# ============================================================================

@app.get("/api/v1/students")
async def get_students(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get students list based on user role."""
    
    # Admin and Teacher see all students (simplified for demo)
    if current_user.role in [UserRole.ADMIN, UserRole.TEACHER]:
        students = db.query(Student).all()
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = []
    for s in students:
        # Get latest risk assessment
        latest_risk = db.query(RiskAssessment).filter(
            RiskAssessment.student_id == s.id
        ).order_by(RiskAssessment.assessed_at.desc()).first()
        
        result.append({
            "student_id": s.student_id,
            "full_name": s.full_name,
            "grade": s.grade,
            "gpa": s.gpa,
            "attendance": s.attendance,
            "performance_score": s.performance_score,
            "latest_risk": {
                "risk_level": latest_risk.risk_level.value if latest_risk else "LOW",
                "risk_score": latest_risk.risk_score if latest_risk else 0.0,
                "assessed_at": latest_risk.assessed_at.isoformat() if latest_risk else None
            } if latest_risk else None
        })
    
    return {"students": result}


@app.get("/api/v1/students/{student_id}")
async def get_student_detail(
    student_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed student information."""
    
    # Check access permission
    check_student_access(student_id, current_user, db)
    
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get latest risk assessment
    latest_risk = db.query(RiskAssessment).filter(
        RiskAssessment.student_id == student.id
    ).order_by(RiskAssessment.assessed_at.desc()).first()
    
    return {
        "student_id": student.student_id,
        "full_name": student.full_name,
        "grade": student.grade,
        "gpa": student.gpa,
        "attendance": student.attendance,
        "performance_score": student.performance_score,
        "parent_email": student.parent_email,
        "parent_phone": student.parent_phone,
        "latest_risk": {
            "risk_level": latest_risk.risk_level.value if latest_risk else None,
            "risk_score": latest_risk.risk_score if latest_risk else None,
            "assessed_at": latest_risk.assessed_at.isoformat() if latest_risk else None
        } if latest_risk else None
    }


# ============================================================================
# Agent Interaction Endpoint (Core Feature)
# ============================================================================

@app.post("/api/v1/agent/invoke")
async def invoke_agent(
    request: AgentGoalRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Invoke the agent with streaming Glass Box trajectory.
    
    This is the core endpoint that streams the agent's Think-Act-Observe
    process in real-time as newline-delimited JSON (NDJSON).
    """
    
    # Get or create session
    if request.session_id:
        session = db.query(AgentSession).filter(
            AgentSession.session_id == request.session_id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new session
        session = AgentSession(
            session_id=str(uuid.uuid4()),
            user_id=current_user.id,
            goal=request.goal
        )
        db.add(session)
        db.commit()
    
    # Get session history
    events = db.query(SessionEvent).filter(
        SessionEvent.session_id == session.id
    ).order_by(SessionEvent.sequence_number).all()
    
    session_history = [
        {"user": e.content if e.event_type == "user" else "", "agent": e.content if e.event_type == "response" else ""}
        for e in events
    ]
    
    # Extract student ID from goal if not provided
    student_id = request.student_id
    if not student_id:
        # Try to extract from goal (e.g., "Analyze student S001")
        import re
        match = re.search(r'S\d{3}', request.goal)
        if match:
            student_id = match.group(0)
        else:
            student_id = "S001"  # Default for demo
    
    # Create multi-agent orchestrator
    orchestrator = MultiAgentOrchestrator(enabled_agents=request.enabled_agents)
    
    # Streaming generator
    async def event_generator():
        """Generate NDJSON stream of agent trajectory."""
        sequence = len(events)
        
        # First, send session info
        yield json.dumps({
            "type": "session_start",
            "session_id": session.session_id,
            "goal": request.goal
        }) + "\n"
        
        try:
            # Stream multi-agent execution
            async for event in orchestrator.run(student_id, session_history):
                # Save event to database
                sequence += 1
                db_event = SessionEvent(
                    session_id=session.id,
                    event_type=event["type"],
                    content=event.get("content", ""),
                    tool_name=event.get("tool_name"),
                    timestamp=datetime.fromisoformat(event["timestamp"]),
                    sequence_number=sequence
                )
                db.add(db_event)
                db.commit()
                
                # Stream to frontend
                yield json.dumps(event) + "\n"
            
            # Mark session as completed
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            session.status = "error"
            db.commit()
            yield json.dumps({
                "type": "error",
                "content": str(e)
            }) + "\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson"
    )


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.get("/api/v1/sessions")
async def get_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's session history."""
    sessions = db.query(AgentSession).filter(
        AgentSession.user_id == current_user.id
    ).order_by(AgentSession.created_at.desc()).limit(50).all()
    
    return [
        {
            "session_id": s.session_id,
            "goal": s.goal,
            "status": s.status,
            "created_at": s.created_at.isoformat(),
            "completed_at": s.completed_at.isoformat() if s.completed_at else None
        }
        for s in sessions
    ]


@app.get("/api/v1/sessions/{session_id}/events")
async def get_session_events(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get events from a specific session."""
    session = db.query(AgentSession).filter(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    events = db.query(SessionEvent).filter(
        SessionEvent.session_id == session.id
    ).order_by(SessionEvent.sequence_number).all()
    
    return [
        {
            "type": e.event_type,
            "content": e.content,
            "tool_name": e.tool_name,
            "timestamp": e.timestamp.isoformat(),
            "sequence": e.sequence_number
        }
        for e in events
    ]


@app.delete("/api/v1/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a session and its events."""
    session = db.query(AgentSession).filter(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete events first
    db.query(SessionEvent).filter(SessionEvent.session_id == session.id).delete()
    # Delete session
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}


# ============================================================================
# Agent Configuration Endpoints
# ============================================================================

@app.get("/api/v1/agent/config")
async def get_agent_config(
    current_user: User = Depends(require_admin)
):
    """Get available agents and their status (Admin only)."""
    return {
        "agents": [
            {
                "id": "data_collection",
                "name": "Data Collection Agent",
                "description": "Retrieves comprehensive student profile and academic data",
                "enabled": True
            },
            {
                "id": "risk_analysis",
                "name": "Risk Analysis Agent",
                "description": "Evaluates student risk level and identifies warning indicators",
                "enabled": True
            },
            {
                "id": "intervention_planning",
                "name": "Intervention Planning Agent",
                "description": "Designs personalized intervention strategies",
                "enabled": True
            },
            {
                "id": "outcome_prediction",
                "name": "Outcome Prediction Agent",
                "description": "Forecasts intervention success probability",
                "enabled": True
            }
        ]
    }


# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("🚀 Starting Agent Aura Backend...")
    try:
        init_database()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    print("✅ Agent Aura Backend ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
