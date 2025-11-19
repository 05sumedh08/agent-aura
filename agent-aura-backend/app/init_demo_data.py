"""
Initialize demo database with student data from CSV.
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

from app.models.database import (
    Base, User, UserRole, Admin, Teacher, Student,
    RiskLevel, RiskAssessment, create_database_engine,
    get_session_local
)


def hash_password(password: str) -> str:
    """Simple password hashing for demo purposes."""
    # Using simple SHA256 for demo (in production use passlib/bcrypt properly)
    return hashlib.sha256(password.encode()).hexdigest()


def load_students_from_csv(csv_path: str):
    """Load students from CSV file."""
    students_data = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            students_data.append({
                'student_id': row['student_id'],
                'name': row['name'],
                'grade': int(row['grade_level']),
                'gpa': float(row['gpa']),
                'attendance': float(row['attendance_rate']) * 100,  # Convert to percentage
                'performance': row['overall_performance']
            })
    
    return students_data


def calculate_risk_score(gpa: float, attendance: float, performance: str) -> tuple:
    """Calculate risk score and level."""
    risk_score = 0.0
    
    # GPA component (0-4 scale)
    if gpa < 2.0:
        risk_score += 0.4
    elif gpa < 2.5:
        risk_score += 0.3
    elif gpa < 3.0:
        risk_score += 0.2
    else:
        risk_score += 0.1
    
    # Attendance component (percentage)
    if attendance < 80:
        risk_score += 0.4
    elif attendance < 90:
        risk_score += 0.3
    elif attendance < 95:
        risk_score += 0.2
    else:
        risk_score += 0.1
    
    # Performance component
    performance_scores = {
        'Below Average': 0.3,
        'Average': 0.15,
        'Above Average': 0.05,
        'Excellent': 0.0
    }
    risk_score += performance_scores.get(performance, 0.2)
    
    # Determine risk level
    if risk_score >= 0.90:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= 0.70:
        risk_level = RiskLevel.HIGH
    elif risk_score >= 0.50:
        risk_level = RiskLevel.MODERATE
    else:
        risk_level = RiskLevel.LOW
    
    return risk_score, risk_level


def init_demo_data():
    """Initialize demo database with users and students."""
    print("🚀 Initializing demo database...")
    
    # Create engine and session
    engine = create_database_engine()
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("⚠️  Database already contains data. Skipping initialization.")
            print(f"   Found {existing_users} existing users.")
            return
        
        print("📝 Creating demo users...")
        
        # Create Admin User
        admin_user = User(
            username="admin",
            email="admin@agentura.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.flush()
        
        admin_profile = Admin(
            user_id=admin_user.id,
            full_name="System Administrator",
            department="IT Administration",
            phone="555-0100"
        )
        db.add(admin_profile)
        print("   ✅ Admin user created: admin / admin123")
        
        # Create Teacher User
        teacher_user = User(
            username="teacher1",
            email="teacher1@agentura.com",
            hashed_password=hash_password("teacher123"),
            role=UserRole.TEACHER,
            is_active=True
        )
        db.add(teacher_user)
        db.flush()
        
        teacher_profile = Teacher(
            user_id=teacher_user.id,
            teacher_id="T001",
            full_name="John Smith",
            subject="Mathematics",
            grade_level=10,
            phone="555-0101",
            email_contact="john.smith@agentura.com"
        )
        db.add(teacher_profile)
        print("   ✅ Teacher user created: teacher1 / teacher123")
        
        # Load student data from CSV
        csv_path = Path(__file__).parent.parent.parent / "data" / "student_data.csv"
        print(f"📊 Loading students from {csv_path}...")
        
        students_data = load_students_from_csv(str(csv_path))
        print(f"   Found {len(students_data)} students in CSV")
        
        # Create student users and profiles
        for idx, student_data in enumerate(students_data, 1):
            # Create user account
            student_user = User(
                username=student_data['student_id'],
                email=f"{student_data['student_id'].lower()}@student.agentura.com",
                hashed_password=hash_password("student123"),
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student_user)
            db.flush()
            
            # Calculate performance score
            perf_scores = {
                'Excellent': 95.0,
                'Above Average': 85.0,
                'Average': 75.0,
                'Below Average': 65.0
            }
            performance_score = perf_scores.get(student_data['performance'], 70.0)
            
            # Create student profile
            student_profile = Student(
                user_id=student_user.id,
                student_id=student_data['student_id'],
                full_name=student_data['name'],
                grade=student_data['grade'],
                gpa=student_data['gpa'],
                attendance=student_data['attendance'],
                performance_score=performance_score,
                parent_email=f"parent.{student_data['student_id'].lower()}@parent.com",
                parent_phone=f"555-{1000 + idx:04d}"
            )
            db.add(student_profile)
            db.flush()
            
            # Calculate and create risk assessment
            risk_score, risk_level = calculate_risk_score(
                student_data['gpa'],
                student_data['attendance'],
                student_data['performance']
            )
            
            risk_assessment = RiskAssessment(
                student_id=student_profile.id,
                risk_level=risk_level,
                risk_score=risk_score,
                risk_factors=f"GPA: {student_data['gpa']}, Attendance: {student_data['attendance']:.0f}%, Performance: {student_data['performance']}",
                assessed_at=datetime.utcnow() - timedelta(hours=idx)
            )
            db.add(risk_assessment)
            
            if idx % 5 == 0:
                print(f"   ... processed {idx} students")
        
        db.commit()
        print(f"✅ Successfully created {len(students_data)} student accounts")
        
        # Print summary
        print("\n📊 Database Summary:")
        print(f"   Total Users: {db.query(User).count()}")
        print(f"   Admins: {db.query(Admin).count()}")
        print(f"   Teachers: {db.query(Teacher).count()}")
        print(f"   Students: {db.query(Student).count()}")
        print(f"   Risk Assessments: {db.query(RiskAssessment).count()}")
        
        # Print risk distribution
        print("\n🎯 Student Risk Distribution:")
        for level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MODERATE, RiskLevel.LOW]:
            count = db.query(RiskAssessment).filter(RiskAssessment.risk_level == level).count()
            print(f"   {level.value}: {count} students")
        
        print("\n✅ Demo database initialized successfully!")
        print("\n🔐 Demo Credentials:")
        print("   Admin:   admin / admin123")
        print("   Teacher: teacher1 / teacher123")
        print("   Student: S001 / student123 (or any student ID)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_demo_data()
