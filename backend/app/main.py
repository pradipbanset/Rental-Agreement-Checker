"""
Main FastAPI Application
Clean, organized entry point with database support and OAuth session support
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import router
from app.api.auth_router import router as auth_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered rental contract analysis for Australian tenancy laws"
)

# ===== CORS CONFIG =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== SESSION MIDDLEWARE =====
# Required for OAuth (Google) to work
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

# ===== ROUTERS =====
app.include_router(router, prefix="/api", tags=["contracts"])
app.include_router(auth_router, prefix="/api", tags=["auth"])

# ===== HEALTH CHECKS =====
@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }

@app.get("/health/db")
def database_health():
    """Check database connectivity"""
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# ===== RUN APP =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
