from sqlalchemy import create_engine, text
import os

# Database URL
DATABASE_URL = "postgresql://postgres:Mani12345@db:5432/fraudshield"

engine = create_engine(DATABASE_URL)

def force_create_admin():
    # நேரடி SQL குயரி மூலம் அட்மினை உருவாக்குதல்
    sql = """
    INSERT INTO users (full_name, email, hashed_password, role, is_active)
    VALUES ('System Admin', 'admin@fraudshield.com', 'admin123', 'admin', true)
    ON CONFLICT (email) DO NOTHING;
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
            print("✅ Admin created successfully using direct SQL!")
    except Exception as e:
        print(f"❌ SQL Error: {e}")

if __name__ == "__main__":
    force_create_admin()