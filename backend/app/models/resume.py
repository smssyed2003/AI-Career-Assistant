from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base import Base


class ResumeTypeEnum(str, PyEnum):
    """Resume type variants"""
    MASTER = "master"
    ATS = "ats"
    AI = "ai"
    ML = "ml"
    PYTHON = "python"
    BACKEND = "backend"
    DATA_SCIENTIST = "data_scientist"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    resume_type = Column(Enum(ResumeTypeEnum), nullable=False)
    content = Column(Text, nullable=False)
    optimized_for_job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    ats_score = Column(Integer, nullable=True)  # 0-100 ATS optimization score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Indexes for efficient querying
    __table_args__ = (
        ("idx_candidate_type", "candidate_id", "resume_type"),
    )
