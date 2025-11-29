# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Database models and schema for Agent Aura.
PostgreSQL schema with role-based access control.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class RiskLevel(enum.Enum):
    """Risk level enumeration."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


# ============================================================================
# User Management Tables
# ============================================================================

class User(Base):
    """Base user table for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    admin_profile = relationship("Admin", back_populates="user", uselist=False)
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False)
    student_profile = relationship("Student", back_populates="user", uselist=False)
    sessions = relationship("AgentSession", back_populates="user")


class Admin(Base):
    """Admin profile with full system access."""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    department = Column(String(100))
    phone = Column(String(20))
    
    # Relationships
    user = relationship("User", back_populates="admin_profile")


class Teacher(Base):
    """Teacher profile with batch/class access."""
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    teacher_id = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    subject = Column(String(100))
    grade_level = Column(Integer)
    phone = Column(String(20))
    email_contact = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    classes = relationship("TeacherClass", back_populates="teacher")


class Student(Base):
    """Student profile with personal data access only."""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False)
    gpa = Column(Float, nullable=False)
    attendance = Column(Float, nullable=False)
    performance_score = Column(Float, default=0.0)
    parent_email = Column(String(100))
    parent_phone = Column(String(20))
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    risk_assessments = relationship("RiskAssessment", back_populates="student")
    interventions = relationship("Intervention", back_populates="student")
    progress_records = relationship("ProgressRecord", back_populates="student")
    class_enrollments = relationship("ClassEnrollment", back_populates="student")


class TeacherClass(Base):
    """Classes/batches managed by teachers."""
    __tablename__ = "teacher_classes"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    class_name = Column(String(100), nullable=False)
    grade_level = Column(Integer, nullable=False)
    subject = Column(String(100))
    academic_year = Column(String(20))
    
    # Relationships
    teacher = relationship("Teacher", back_populates="classes")
    enrollments = relationship("ClassEnrollment", back_populates="teacher_class")


class ClassEnrollment(Base):
    """Student enrollment in classes."""
    __tablename__ = "class_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("teacher_classes.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="class_enrollments")
    teacher_class = relationship("TeacherClass", back_populates="enrollments")


# ============================================================================
# Agent Session Tables
# ============================================================================

class AgentSession(Base):
    """Agent interaction sessions with Glass Box trajectory."""
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(Text, nullable=False)
    status = Column(String(20), default="active")  # active, completed, error
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    events = relationship("SessionEvent", back_populates="session", cascade="all, delete-orphan")


class SessionEvent(Base):
    """Individual events in agent trajectory (Think-Act-Observe)."""
    __tablename__ = "session_events"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("agent_sessions.id"), nullable=False)
    event_type = Column(String(20), nullable=False)  # thought, action, observation, response
    content = Column(Text, nullable=False)
    tool_name = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sequence_number = Column(Integer, nullable=False)
    
    # Relationships
    session = relationship("AgentSession", back_populates="events")


# ============================================================================
# Risk Assessment and Intervention Tables
# ============================================================================

class RiskAssessment(Base):
    """Student risk assessment records."""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_factors = Column(Text)  # JSON string of factors
    assessed_at = Column(DateTime, default=datetime.utcnow)
    assessed_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    student = relationship("Student", back_populates="risk_assessments")


class Intervention(Base):
    """Intervention plans for at-risk students."""
    __tablename__ = "interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    intervention_type = Column(String(100), nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    frequency = Column(String(50))
    actions = Column(Text)  # JSON string of actions
    success_rate = Column(Float)
    confidence_level = Column(Integer)
    status = Column(String(20), default="planned")  # planned, active, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="interventions")


class ProgressRecord(Base):
    """Student progress tracking over time."""
    __tablename__ = "progress_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    gpa = Column(Float)
    attendance = Column(Float)
    notes = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="progress_records")


# ============================================================================
# Database Connection and Session Management
# ============================================================================

def get_database_url():
    """Get database URL from settings."""
    from app.config import get_settings
    settings = get_settings()
    return settings.DATABASE_URL


def create_database_engine():
    """Create SQLAlchemy engine."""
    url = get_database_url()
    # If using sqlite file, we need special connect args and avoid pool sizing
    if url.startswith("sqlite"):
        # Using check_same_thread False enables sqlite access from multiple
        # threads in some dev setups (uvicorn). We avoid pool sizing options.
        return create_engine(
            url,
            connect_args={"check_same_thread": False}
        )

    # Default for full DBs like PostgreSQL
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )


def get_session_local():
    """Get database session factory."""
    engine = create_database_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database schema."""
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema created successfully")


def get_db():
    """Dependency for FastAPI routes."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
