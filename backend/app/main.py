from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.api import routers
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Create database schema on startup for development
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Career Agent",
    description="A modular platform to accelerate interviews with AI resume parsing, matching, and readiness scoring.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.health.router, prefix="/api")
app.include_router(routers.candidates.router, prefix="/api")
app.include_router(routers.ingestion.router, prefix="/api")
app.include_router(routers.jobs.router, prefix="/api")
app.include_router(routers.resumes.router, prefix="/api")
app.include_router(routers.applications.router, prefix="/api")
app.include_router(routers.discovery.router, prefix="/api")
app.include_router(routers.interviews.router, prefix="/api")
app.include_router(routers.career.router, prefix="/api")

@app.get("/", summary="Root endpoint")
def root():
    return {"message": "AI Career Agent backend is running."}
