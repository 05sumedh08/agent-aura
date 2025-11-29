# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Authentication and authorization for Agent Aura.
JWT-based auth with role-based access control (RBAC).
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models.database import User, UserRole, get_db

from app.config import get_settings

settings = get_settings()

# Security configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ============================================================================
# Password Hashing
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (simple SHA256 for demo)."""
    hashed_plain = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed_plain == hashed_password


def get_password_hash(password: str) -> str:
    """Hash a password (simple SHA256 for demo)."""
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# User Authentication
# ============================================================================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.
    
    Args:
        db: Database session
        username: Username
        password: Plain text password
        
    Returns:
        User object if authenticated, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from token.
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user not found or token invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_from_query(
    token: str = Query(...),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from query parameter token.
    Used for file downloads where headers cannot be set.
    """
    return await get_current_user(token, db)


async def get_current_active_user_from_query(
    current_user: User = Depends(get_current_user_from_query)
) -> User:
    """
    Get current active user from query parameter token.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ============================================================================
# Role-Based Access Control (RBAC)
# ============================================================================

class RoleChecker:
    """Dependency class for checking user roles."""
    
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {[r.value for r in self.allowed_roles]}"
            )
        return current_user


# Role-specific dependencies
require_admin = RoleChecker([UserRole.ADMIN])
require_teacher = RoleChecker([UserRole.ADMIN, UserRole.TEACHER])
require_student = RoleChecker([UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT])


def check_student_access(
    student_id: str,
    current_user: User,
    db: Session
) -> bool:
    """
    Check if user has access to view/modify student data.
    
    Args:
        student_id: Student ID to check
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        True if access allowed
        
    Raises:
        HTTPException: If access denied
    """
    # Admin has access to everything
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Student can only access their own data
    if current_user.role == UserRole.STUDENT:
        if current_user.student_profile and current_user.student_profile.student_id == student_id:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own student data"
        )
    
    # Teacher can access students in their classes
    if current_user.role == UserRole.TEACHER:
        from app.models.database import Student, ClassEnrollment
        
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check if student is in any of teacher's classes
        teacher_classes = [tc.id for tc in current_user.teacher_profile.classes]
        student_in_class = db.query(ClassEnrollment).filter(
            ClassEnrollment.student_id == student.id,
            ClassEnrollment.class_id.in_(teacher_classes)
        ).first()
        
        if student_in_class:
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access students in your classes"
        )
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


# ============================================================================
# User Registration
# ============================================================================

def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: UserRole,
    full_name: str,
    **kwargs
) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        username: Username
        email: Email address
        password: Plain text password
        role: User role
        full_name: Full name
        **kwargs: Additional role-specific fields
        
    Returns:
        Created user
    """
    from app.models.database import Admin, Teacher, Student
    
    # Create base user
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    db.flush()  # Get user ID
    
    # Create role-specific profile
    if role == UserRole.ADMIN:
        admin_profile = Admin(
            user_id=db_user.id,
            full_name=full_name,
            department=kwargs.get("department"),
            phone=kwargs.get("phone")
        )
        db.add(admin_profile)
    
    elif role == UserRole.TEACHER:
        teacher_profile = Teacher(
            user_id=db_user.id,
            teacher_id=kwargs.get("teacher_id"),
            full_name=full_name,
            subject=kwargs.get("subject"),
            grade_level=kwargs.get("grade_level"),
            phone=kwargs.get("phone"),
            email_contact=email
        )
        db.add(teacher_profile)
    
    elif role == UserRole.STUDENT:
        student_profile = Student(
            user_id=db_user.id,
            student_id=kwargs.get("student_id"),
            full_name=full_name,
            grade=kwargs.get("grade"),
            gpa=kwargs.get("gpa", 0.0),
            attendance=kwargs.get("attendance", 100.0),
            parent_email=kwargs.get("parent_email"),
            parent_phone=kwargs.get("parent_phone")
        )
        db.add(student_profile)
    
    db.commit()
    db.refresh(db_user)
    return db_user
