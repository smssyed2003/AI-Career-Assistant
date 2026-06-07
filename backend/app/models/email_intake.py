from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from app.db.base import Base


class EmailIntake(Base):
    __tablename__ = "email_intakes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=True, index=True)
    sender_email = Column(String(256), nullable=False, index=True)
    subject = Column(String(512), nullable=True)
    body = Column(Text, nullable=True)
    
    # Extracted components
    resume_content = Column(Text, nullable=True)
    portfolio_url = Column(String(512), nullable=True)
    github_url = Column(String(512), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    certificates = Column(JSON, nullable=True, default=list)
    
    # Extraction metadata
    extraction_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    extraction_errors = Column(JSON, nullable=True, default=list)
    raw_email_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
