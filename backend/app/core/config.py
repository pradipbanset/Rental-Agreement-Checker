"""
Application configuration and settings
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    # App settings
    APP_NAME = "Rental Fairness Checker"
    VERSION = "1.0.0"
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000"]
    
    # API Keys
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    
    # Database - Check if running in Docker
    # In Docker, use service name 'postgres', locally use 'localhost'
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://rental_user:rental_password@localhost:5432/rental_checker"
    )
    
    # RAG settings
    RAG_DB_DIR = "rag_system/chroma_db"
    RAG_COLLECTION_NAME = "tenancy_laws"
    
    # Rate limiting
    RATE_LIMIT_SECONDS = 6  # 1 request per 6 seconds
    
    # Supported states
    SUPPORTED_STATES = ["NSW", "VIC", "QLD", "ACT", "SA", "WA", "TAS", "NT"]
    
    # Google OAuth credentials
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:8000/api/login/google/callback"  # Fixed default
    )
    
    # Session secret key (required for SessionMiddleware)
    SESSION_SECRET = os.getenv(
        "SESSION_SECRET",
        "super-secret-key"  # Replace with strong random key in production
    )
    
    # JWT / auth secret key (required for auth_router)
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "another-super-secret-key"  # Replace with strong random key in production
    )

# Instantiate settings
settings = Settings()