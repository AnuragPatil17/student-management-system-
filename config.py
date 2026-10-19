import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base Application Configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'apex-college-attendance-cloud-secure-key-2026')
    
    # Database: Use cloud database if DATABASE_URL provided (e.g. AWS RDS MySQL / Supabase Postgres),
    # otherwise fallback to local SQLite for seamless zero-setup execution.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # SQLite local fallback
        db_path = os.path.join(BASE_DIR, 'attendance.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    elif SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        # Fix for Heroku/Render legacy postgres prefix
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    } if not SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}

    # College Branding Configuration
    COLLEGE_NAME = os.environ.get('COLLEGE_NAME', 'Apex Institute of Technology & Science')
    COLLEGE_CODE = os.environ.get('COLLEGE_CODE', 'AITS-EDU')
    APP_TITLE = "Cloud-Based Student Attendance Management System"
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds

    # Cloud Configuration
    CLOUD_PROVIDER = os.environ.get('CLOUD_PROVIDER', 'Local / Cloud Ready')
    ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1')

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Enable over HTTPS in production

config_dict = {
    'development': Config,
    'production': ProductionConfig,
    'default': Config
}
