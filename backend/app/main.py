from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from sqlalchemy import inspect, text
from app.api import routers
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Create database schema on startup for development
Base.metadata.create_all(bind=engine)


def ensure_dev_schema_columns():
    if not settings.database_url.startswith("sqlite"):
        return

    ownership_tables = [
        "candidates",
        "job_descriptions",
        "resumes",
        "application_packages",
        "interview_prep",
        "career_reports",
        "job_sources",
    ]
    inspector = inspect(engine)
    with engine.begin() as connection:
        if "users" in inspector.get_table_names():
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            if "role" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(32) NOT NULL DEFAULT 'user'"))

        for table in ownership_tables:
            if table not in inspector.get_table_names():
                continue
            columns = {column["name"] for column in inspector.get_columns(table)}
            if "user_id" not in columns:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER"))


ensure_dev_schema_columns()

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
app.include_router(routers.auth.router, prefix="/api")
app.include_router(routers.admin.router, prefix="/api")
app.include_router(routers.dashboard.router, prefix="/api")
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
