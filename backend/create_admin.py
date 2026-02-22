from app.core.database import SessionLocal, engine, Base
from app.models.user import User

# ❌ இங்கே இருந்த passlib இம்போர்ட் மற்றும் pwd_context வரிகளை நீக்கிவிட்டோம்

def create_initial_admin():
    db = SessionLocal()
    try:
        # டேபிள்களை உருவாக்குதல்
        Base.metadata.create_all(bind=engine)
        
        admin_exists = db.query(User).filter(User.email == "admin@fraudshield.com").first()
        
        if not admin_exists:
            # நேரடியாக ஹேஷிங் இல்லாமல் பாஸ்வேர்டு
            admin = User(
                full_name="System Admin",
                email="admin@fraudshield.com",
                hashed_password="admin123", 
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created SUCCESSFULLY (Plain Text): admin@fraudshield.com / admin123")
        else:
            print("ℹ️ Admin user already exists.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()