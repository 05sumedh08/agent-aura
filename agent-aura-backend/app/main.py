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

# Initialize FastAPI app
app = FastAPI(
    title="Agent Aura API",
    description="Multi-agent AI system for K-12 student intervention with Glass Box UI",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token (Mock auth for demo)."""
    # Mock authentication for demo (bypass database)
    demo_users = {
        "admin": {"password": "admin123", "role": "admin", "user_id": 1},
        "teacher1": {"password": "teacher123", "role": "teacher", "user_id": 2},
        "STU001": {"password": "student123", "role": "student", "user_id": 3}
    }
    
    if form_data.username in demo_users:
        demo_user = demo_users[form_data.username]
        if form_data.password == demo_user["password"]:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": form_data.username, "role": demo_user["role"]},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "role": demo_user["role"],
                "user_id": demo_user["user_id"]
            }
    
    # If mock auth fails, raise error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/api/v1/auth/me")
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """Get current user information (Mock for demo)."""
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        role = payload.get("role", "student")
        
        # Mock user data based on username
        mock_users = {
            "admin": {
                "id": 1,
                "username": "admin",
                "email": "admin@agentura.com",
                "role": "admin",
                "full_name": "Administrator",
                "department": "IT Administration"
            },
            "teacher1": {
                "id": 2,
                "username": "teacher1",
                "email": "teacher1@agentura.com",
                "role": "teacher",
                "teacher_id": "T001",
                "full_name": "John Smith",
                "subject": "Mathematics",
                "grade_level": 10
            },
            "STU001": {
                "id": 3,
                "username": "STU001",
                "email": "student001@agentura.com",
                "role": "student",
                "student_id": "STU001",
                "full_name": "Jane Doe",
                "grade": 10,
                "gpa": 3.5
            }
        }
        
        if username in mock_users:
            return mock_users[username]
        
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# ============================================================================
# Student Data Endpoints
# ============================================================================

@app.get("/api/v1/students")
async def get_students(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    """Get students list based on user role."""
    
    # Admin sees all students
    if current_user.role == UserRole.ADMIN:
        students = db.query(Student).all()
    # Teacher sees only their class students
    elif current_user.role == UserRole.TEACHER:
        from app.models.database import ClassEnrollment
        teacher_classes = [tc.id for tc in current_user.teacher_profile.classes]
        enrollments = db.query(ClassEnrollment).filter(
            ClassEnrollment.class_id.in_(teacher_classes)
        ).all()
        student_ids = [e.student_id for e in enrollments]
        students = db.query(Student).filter(Student.id.in_(student_ids)).all()
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return [
        {
            "student_id": s.student_id,
            "full_name": s.full_name,
            "grade": s.grade,
            "gpa": s.gpa,
            "attendance": s.attendance
        }
        for s in students
    ]


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
    
    # Create agent
    agent = Agent()
    
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
            # Stream agent execution
            async for event in agent.run(request.goal, session_history):
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
