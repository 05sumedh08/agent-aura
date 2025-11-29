import sys
import os

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import get_session_local, User, UserRole, Admin
from app.services.auth import get_password_hash

def create_admin():
    db = get_session_local()()
    try:
        print("Checking for admin user...")
        user = db.query(User).filter(User.username == "admin").first()
        
        if user:
            print("Admin user exists. Resetting password...")
            user.hashed_password = get_password_hash("admin123")
            user.is_active = True
            db.commit()
            print("✅ Password reset to 'admin123'")
        else:
            print("Creating new admin user...")
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
            print("✅ Admin user created: admin / admin123")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
