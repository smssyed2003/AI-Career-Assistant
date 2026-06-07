from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApplicationStatus(str, Enum):
    PREPARED = "prepared"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    ARCHIVED = "archived"


class ApplicationPackageRead(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    match_score: Optional[int] = Field(default=None, ge=0, le=100)
    ats_score: Optional[int] = Field(default=None, ge=0, le=100)
    interview_probability: Optional[int] = Field(default=None, ge=0, le=100)
    optimized_resume_id: Optional[int] = None
    cover_letter: Optional[str] = None
    hr_introduction: Optional[str] = None
    email_template: Optional[str] = None
    screening_answers: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: ApplicationStatus
    applied_date: Optional[datetime] = None
    notes: Optional[str] = None
    skill_match_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    experience_match_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    project_match_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
