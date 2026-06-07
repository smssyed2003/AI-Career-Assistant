from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func

from app.db.base import Base


class CareerReport(Base):
    __tablename__ = "career_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    interview_rate = Column(Integer, nullable=True)
    ats_average = Column(Integer, nullable=True)
    new_skills = Column(JSON, nullable=True, default=list)
    trending_jobs = Column(JSON, nullable=True, default=list)
    resume_suggestions = Column(JSON, nullable=True, default=list)
    certification_suggestions = Column(JSON, nullable=True, default=list)
    salary_growth = Column(Text, nullable=True)
    career_roadmap = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
