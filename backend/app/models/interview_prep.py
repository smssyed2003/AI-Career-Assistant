from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base import Base


class InterviewQuestionTypeEnum(str, PyEnum):
    """Types of interview questions"""
    HR = "hr"
    TECHNICAL = "technical"
    CODING = "coding"
    AI = "ai"
    LLM = "llm"
    RAG = "rag"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"


class InterviewPrep(Base):
    __tablename__ = "interview_prep"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)
    application_package_id = Column(Integer, ForeignKey("application_packages.id"), nullable=True)
    
    # Questions and answers
    question_type = Column(Enum(InterviewQuestionTypeEnum), nullable=False)
    question_text = Column(Text, nullable=False)
    suggested_answer = Column(Text, nullable=True)
    keyword_highlights = Column(JSON, nullable=True, default=list)  # Key points to mention
    
    # Preparation tracking
    difficulty_level = Column(String(50), default="medium")  # easy, medium, hard
    practice_count = Column(Integer, default=0)
    user_answer = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
