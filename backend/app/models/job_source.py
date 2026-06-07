from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, Boolean, ForeignKey
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base import Base


class JobSourceEnum(str, PyEnum):
    """Job discovery sources"""
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    INDEED = "indeed"
    WELLFOUND = "wellfound"
    REMOTE_OK = "remote_ok"
    COMPANY_CAREERS = "company_careers"
    STARTUP_CAREERS = "startup_careers"
    GOVERNMENT_JOBS = "government_jobs"
    INTERNSHIP_PORTALS = "internship_portals"
    AI_COMPANY_CAREERS = "ai_company_careers"
    MANUAL = "manual"


class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True, index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)
    source = Column(Enum(JobSourceEnum), nullable=False)
    source_job_id = Column(String(256), nullable=True)  # External job ID from source
    source_url = Column(String(512), nullable=True)
    
    # Discovery metadata
    discovered_at = Column(DateTime(timezone=True), default=func.now())
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_source_id = Column(Integer, ForeignKey("job_sources.id"), nullable=True)
    
    # Tracking
    is_active = Column(Boolean, default=True)
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
