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
import csv
import io
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import asyncio
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from app.config import get_settings

# Load environment file path for API key updates
env_path = Path(".env")

settings = get_settings()

from app.models.database import (
    User, UserRole, Student,
    AgentSession, SessionEvent, RiskAssessment,
    get_db, init_database
)
from app.services.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    require_admin,
    check_student_access, create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user_from_query
)
from app.services.auth import oauth2_scheme, decode_access_token
# Agent imported elsewhere when needed
from app.agent_core.orchestrator import MultiAgentOrchestrator

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-agent AI system for K-12 student intervention with Glass Box UI",
    version=settings.APP_VERSION
)
# Prometheus metrics
REQUEST_COUNT = Counter('agent_aura_request_count', 'Total API requests', ['endpoint'])
AGENT_INVOCATIONS = Counter('agent_aura_agent_invocations_total', 'Agent invocations', ['status'])
ANALYSIS_LATENCY = Histogram('agent_aura_analysis_latency_seconds', 'Latency of agent analysis')


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
    model_override: Optional[str] = None


class ApiKeyRequest(BaseModel):
    api_key: str


class AgentConfigUpdate(BaseModel):
    agent_id: str
    enabled: bool


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
    REQUEST_COUNT.labels(endpoint="/health").inc()
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
        
    except Exception:
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


@app.post("/api/v1/voice/query")
async def voice_query(
    query: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Handle natural language voice queries about students.
    
    Args:
        query: Dictionary containing 'text' field with the transcribed query.
        
    Returns:
        Dictionary with 'response_text', 'data', and optional 'audio_base64'.
    """
    text = query.get("text", "").lower()
    
    # Simple regex-based intent matching for demo purposes
    # In a real app, this would use an LLM or NLU service
    import re
    from app.services.voice import ElevenLabsService
    
    # Intent: "How is [Student Name] doing?"
    match = re.search(r"how is (.+?) doing", text)
    if match:
        student_name = match.group(1)
        # Find student by name (fuzzy match or exact)
        student = db.query(Student).filter(Student.full_name.ilike(f"%{student_name}%")).first()
        
        if student:
            # Get latest risk
            latest_risk = db.query(RiskAssessment).filter(
                RiskAssessment.student_id == student.id
            ).order_by(RiskAssessment.assessed_at.desc()).first()
            
            risk_level = latest_risk.risk_level.value if latest_risk else "Unknown"
            gpa = student.gpa
            
            response_text = f"{student.full_name} is currently at {risk_level} risk level with a GPA of {gpa}. "
            if risk_level in ["CRITICAL", "HIGH"]:
                response_text += "Immediate attention is recommended."
            else:
                response_text += "They are performing well."
            
            # Generate Audio with ElevenLabs
            voice_service = ElevenLabsService()
            audio_base64 = voice_service.generate_audio(response_text)
                
            return {
                "response_text": response_text,
                "audio_base64": audio_base64,
                "data": {
                    "student_id": student.student_id,
                    "name": student.full_name,
                    "risk_level": risk_level
                }
            }
        else:
            response_text = f"I couldn't find a student named {student_name}."
            voice_service = ElevenLabsService()
            audio_base64 = voice_service.generate_audio(response_text)
            
            return {
                "response_text": response_text,
                "audio_base64": audio_base64,
                "data": None
            }
            
    response_text = "I'm sorry, I didn't understand that query. You can ask 'How is John Doe doing?'."
    voice_service = ElevenLabsService()
    audio_base64 = voice_service.generate_audio(response_text)
    
    return {
        "response_text": response_text,
        "audio_base64": audio_base64,
        "data": None
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID must be provided either in the 'student_id' field or in the goal (e.g., 'Analyze student S001')."
            )
    
    # Initialize orchestrator with error handling
    orchestrator = None
    initial_error = None
    try:
        orchestrator = MultiAgentOrchestrator(
            enabled_agents=request.enabled_agents,
            model_override=request.model_override
        )
    except Exception as e:
        initial_error = e

    # Streaming generator
    async def event_generator(initial_error=None):
        """Generate NDJSON stream of agent trajectory."""
        start_time = asyncio.get_event_loop().time()
        sequence = len(events)
        
        # First, send session info
        yield json.dumps({
            "type": "session_start",
            "session_id": session.session_id,
            "goal": request.goal
        }) + "\n"
        
        # Handle initialization errors (like API key issues)
        if initial_error:
            error_str = str(initial_error).lower()
            if "api key" in error_str or "400" in error_str or "429" in error_str or "quota" in error_str:
                # MOCK RESPONSE FALLBACK
                mock_events = [
                    {"type": "thought", "content": "API Key/Quota invalid, switching to MOCK mode. Starting analysis for student..."},
                    {"type": "tool", "tool_name": "Data Collection Agent", "content": "Retrieving academic records..."},
                    {"type": "observation", "content": "Student Data: Grade 11, GPA 3.2, Attendance 95%"},
                    {"type": "thought", "content": "Analyzing risk factors based on retrieved data."},
                    {"type": "tool", "tool_name": "Risk Analysis Agent", "content": "Calculating risk score..."},
                    {"type": "observation", "content": "Risk Level: LOW (Score: 15/100)"},
                    {"type": "response", "content": "Analysis Complete. Student is performing well with low risk. Recommended action: Continue monitoring."}
                ]
                
                for event in mock_events:
                    await asyncio.sleep(0.5)  # Simulate processing time
                    sequence += 1
                    db_event = SessionEvent(
                        session_id=session.id,
                        event_type=event["type"],
                        content=event.get("content", ""),
                        tool_name=event.get("tool_name"),
                        timestamp=datetime.utcnow(),
                        sequence_number=sequence
                    )
                    db.add(db_event)
                    db.commit()
                    yield json.dumps(event) + "\n"
                
                # Mark session as completed
                session.status = "completed"
                session.completed_at = datetime.utcnow()
                db.commit()
                AGENT_INVOCATIONS.labels(status="mock_completed").inc()
                ANALYSIS_LATENCY.observe(asyncio.get_event_loop().time() - start_time)
                return
            else:
                session.status = "error"
                db.commit()
                yield json.dumps({
                    "type": "error",
                    "content": str(initial_error)
                }) + "\n"
                return

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
            AGENT_INVOCATIONS.labels(status="completed").inc()
            ANALYSIS_LATENCY.observe(asyncio.get_event_loop().time() - start_time)
            
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "400" in error_str or "429" in error_str or "quota" in error_str:
                # MOCK RESPONSE FALLBACK (Runtime error)
                mock_events = [
                    {"type": "thought", "content": "API Key/Quota invalid during execution, switching to MOCK mode..."},
                    {"type": "response", "content": "Analysis Complete (Mocked due to API Quota). Student is performing well."}
                ]
                for event in mock_events:
                    await asyncio.sleep(0.5)  # Simulate processing time
                    sequence += 1
                    db_event = SessionEvent(
                        session_id=session.id,
                        event_type=event["type"],
                        content=event.get("content", ""),
                        tool_name=event.get("tool_name"),
                        timestamp=datetime.utcnow(),
                        sequence_number=sequence
                    )
                    db.add(db_event)
                    db.commit()
                    yield json.dumps(event) + "\n"
                
                session.status = "completed"
                session.completed_at = datetime.utcnow()
                db.commit()
                AGENT_INVOCATIONS.labels(status="mock_completed").inc()
                ANALYSIS_LATENCY.observe(asyncio.get_event_loop().time() - start_time)
            else:
                session.status = "error"
                db.commit()
                yield json.dumps({
                    "type": "error",
                    "content": str(e)
                }) + "\n"
                AGENT_INVOCATIONS.labels(status="error").inc()
                ANALYSIS_LATENCY.observe(asyncio.get_event_loop().time() - start_time)
    
    return StreamingResponse(
        event_generator(initial_error=initial_error),
        media_type="application/x-ndjson"
    )


# ============================================================================
# Metrics Endpoint
# ============================================================================

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    REQUEST_COUNT.labels(endpoint="/metrics").inc()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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


@app.delete("/api/v1/sessions/clear-all")
async def clear_all_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete all sessions for the current user."""
    # Get all user sessions
    sessions = db.query(AgentSession).filter(
        AgentSession.user_id == current_user.id
    ).all()
    
    total_deleted = len(sessions)
    
    # Delete events for all sessions
    for session in sessions:
        db.query(SessionEvent).filter(SessionEvent.session_id == session.id).delete()
    
    # Delete all sessions
    db.query(AgentSession).filter(
        AgentSession.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {
        "message": f"Successfully deleted {total_deleted} session(s)",
        "deleted_count": total_deleted
    }


@app.get("/api/v1/sessions/{session_id}/export/pdf")
async def export_session_pdf(
    session_id: str,
    current_user: User = Depends(get_current_active_user_from_query),
    db: Session = Depends(get_db)
):
    """Export session as PDF report."""
    # Get session
    session = db.query(AgentSession).filter(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get events
    events = db.query(SessionEvent).filter(
        SessionEvent.session_id == session.id
    ).order_by(SessionEvent.sequence_number).all()
    
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=30,
    )
    story.append(Paragraph("Agent Aura - Session Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Session Info
    info_data = [
        ["Session ID:", session.session_id],
        ["Goal:", session.goal],
        ["Status:", session.status.upper()],
        ["Created:", session.created_at.strftime("%Y-%m-%d %H:%M:%S")],
        ["Completed:", session.completed_at.strftime("%Y-%m-%d %H:%M:%S") if session.completed_at else "N/A"],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Agent Trajectory
    story.append(Paragraph("Agent Trajectory", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    for event in events:
        event_style = ParagraphStyle(
            'EventStyle',
            parent=styles['Normal'],
            fontSize=9,
            leftIndent=10,
            spaceAfter=8,
        )
        
        event_type = event.event_type.upper()
        content = event.content or event.tool_name or "N/A"
        timestamp = event.timestamp.strftime("%H:%M:%S")
        
        event_text = f"<b>[{timestamp}] {event_type}:</b> {content}"
        story.append(Paragraph(event_text, event_style))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    
    # Return PDF file
    filename = f"agent_aura_session_{session_id[:8]}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/v1/sessions/{session_id}/export/csv")
async def export_session_csv(
    session_id: str,
    current_user: User = Depends(get_current_active_user_from_query),
    db: Session = Depends(get_db)
):
    """Export session as CSV report."""
    # Get session
    session = db.query(AgentSession).filter(
        AgentSession.session_id == session_id,
        AgentSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get events
    events = db.query(SessionEvent).filter(
        SessionEvent.session_id == session.id
    ).order_by(SessionEvent.sequence_number).all()
    
    # Create CSV in memory
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # Write header
    writer.writerow([
        "Sequence",
        "Timestamp",
        "Event Type",
        "Tool Name",
        "Content"
    ])
    
    # Write events
    for event in events:
        writer.writerow([
            event.sequence_number,
            event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            event.event_type,
            event.tool_name or "",
            event.content or ""
        ])
    
    # Return CSV
    csv_buffer.seek(0)
    filename = f"agent_aura_session_{session_id[:8]}.csv"
    
    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ============================================================================
# Agent Configuration Endpoints
# ============================================================================

# Global Agent Configuration State
AGENT_CONFIG = {
    "data_collection": {"name": "Data Collection Agent", "description": "Retrieves comprehensive student profile and academic data", "enabled": True},
    "risk_analysis": {"name": "Risk Analysis Agent", "description": "Evaluates student risk level and identifies warning indicators", "enabled": True},
    "notification_generation": {"name": "Notification Agent", "description": "Generates automated email notifications for stakeholders", "enabled": True},
    "intervention_planning": {"name": "Intervention Planning Agent", "description": "Designs personalized intervention strategies", "enabled": True},
    "outcome_prediction": {"name": "Outcome Prediction Agent", "description": "Forecasts intervention success probability", "enabled": True}
}

@app.get("/api/v1/agent/config")
async def get_agent_config(
    current_user: User = Depends(require_admin)
):
    """Get available agents and their status (Admin only)."""
    return {
        "agents": [
            {
                "id": agent_id,
                "name": config["name"],
                "description": config["description"],
                "enabled": config["enabled"]
            }
            for agent_id, config in AGENT_CONFIG.items()
        ]
    }


@app.post("/api/v1/agent/config")
async def update_agent_config(
    config_update: AgentConfigUpdate,
    current_user: User = Depends(require_admin)
):
    """Update agent status (Admin only)."""
    if config_update.agent_id not in AGENT_CONFIG:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    AGENT_CONFIG[config_update.agent_id]["enabled"] = config_update.enabled
    return {"message": "Agent configuration updated", "agent_id": config_update.agent_id, "enabled": config_update.enabled}



@app.post("/api/v1/settings/apikey")
async def update_api_key(
    request: ApiKeyRequest,
    current_user: User = Depends(require_admin)
):
    """Update Gemini API Key."""
    # Update environment variable
    os.environ["GEMINI_API_KEY"] = request.api_key
    
    # Update .env file if it exists
    if env_path.exists():
        try:
            # Read current content
            with open(env_path, "r") as f:
                lines = f.readlines()
            
            # Update or append key
            key_found = False
            new_lines = []
            for line in lines:
                if line.startswith("GEMINI_API_KEY="):
                    new_lines.append(f"GEMINI_API_KEY={request.api_key}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            
            if not key_found:
                new_lines.append(f"\nGEMINI_API_KEY={request.api_key}\n")
                
            with open(env_path, "w") as f:
                f.writelines(new_lines)
                
        except Exception as e:
            print(f"Error updating .env file: {e}")
            
    # Re-initialize model manager
    try:
        from app.agent_core.model_manager import model_manager
        model_manager.initialize()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize models with new key: {str(e)}")
        
    return {"message": "API Key updated successfully"}



@app.delete("/api/v1/settings/apikey")
async def remove_api_key(
    current_user: User = Depends(require_admin)
):
    """Remove Gemini API Key."""
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
        
    # Update .env file
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                lines = f.readlines()
            
            with open(env_path, "w") as f:
                for line in lines:
                    if not line.startswith("GEMINI_API_KEY="):
                        f.write(line)
        except Exception as e:
            print(f"Error updating .env file: {e}")
            
    return {"message": "API Key removed successfully"}



@app.get("/api/v1/settings/apikey/status")
async def get_api_key_status(
    current_user: User = Depends(require_admin)
):
    """Check if API Key is set."""
    is_set = "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"]
    return {"is_set": is_set}



@app.get("/api/v1/agent/models")
async def get_available_models(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available LLM models."""
    from app.agent_core.model_manager import model_manager
    return {"models": model_manager.get_available_models()}


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
        
        # Seed database with default admin
        from app.models.database import get_session_local, User, UserRole, Admin
        from app.services.auth import get_password_hash
        
        db = get_session_local()()
        try:
            if not db.query(User).first():
                print("🌱 Seeding database with default admin...")
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN
                )
                db.add(admin_user)
                db.flush()
                
                admin_profile = Admin(
                    user_id=admin_user.id,
                    full_name="System Administrator",
                    department="IT"
                )
                db.add(admin_profile)
                db.commit()
                print("✅ Default admin created: admin / admin123")
        except Exception as e:
            print(f"⚠️  Seeding failed: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    print("✅ Agent Aura Backend ready!")


if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0" if os.getenv("BIND_ALL", "0") == "1" else "127.0.0.1"
    uvicorn.run(app, host=host, port=8000)
