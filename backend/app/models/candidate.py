from sqlalchemy import Column, ForeignKey, Integer, String, Text, JSON, DateTime, Index
from sqlalchemy.sql import func

from app.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    full_name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False, index=True)
    phone = Column(String(64), nullable=True)
    summary = Column(Text, nullable=True)
    education = Column(JSON, nullable=True, default=lambda: [])
    experience = Column(JSON, nullable=True, default=lambda: [])
    projects = Column(JSON, nullable=True, default=lambda: [])
    skills = Column(JSON, nullable=True, default=lambda: [])
    certifications = Column(JSON, nullable=True, default=lambda: [])
    links = Column(JSON, nullable=True, default=lambda: [])
    preferences = Column(JSON, nullable=True, default=lambda: {})
    extra_metadata = Column(JSON, nullable=True, default=lambda: {})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_candidate_user_email", "user_id", "email", unique=True),
    )
