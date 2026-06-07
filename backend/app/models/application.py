from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base import Base


class ApplicationStatusEnum(str, PyEnum):
    """Application status tracking"""
    PREPARED = "prepared"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    ARCHIVED = "archived"


class ApplicationPackage(Base):
    __tablename__ = "application_packages"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)
    
    # Optimization scores
    match_score = Column(Integer, nullable=True)  # Overall match percentage (0-100)
    ats_score = Column(Integer, nullable=True)  # ATS score (0-100)
    interview_probability = Column(Integer, nullable=True)  # Interview likelihood (0-100)
    
    # Generated materials
    optimized_resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    cover_letter = Column(Text, nullable=True)
    hr_introduction = Column(Text, nullable=True)
    email_template = Column(Text, nullable=True)
    screening_answers = Column(JSON, nullable=True, default=dict)  # Q&A pairs
    
    # Application details
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.PREPARED)
    applied_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Matching details
    skill_match_details = Column(JSON, nullable=True)
    experience_match_details = Column(JSON, nullable=True)
    project_match_details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
