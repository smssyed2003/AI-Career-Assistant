from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    company = Column(String(256), nullable=True)
    location = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True, default=lambda: {})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
