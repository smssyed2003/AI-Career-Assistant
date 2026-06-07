from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ResumeType(str, Enum):
    MASTER = "master"
    ATS = "ats"
    AI = "ai"
    ML = "ml"
    PYTHON = "python"
    BACKEND = "backend"
    DATA_SCIENTIST = "data_scientist"


class ResumeCreate(BaseModel):
    resume_type: ResumeType
    content: str
    optimized_for_job_id: Optional[int] = None
    ats_score: Optional[int] = Field(default=None, ge=0, le=100)


class ResumeRead(ResumeCreate):
    id: int
    candidate_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeGenerationResult(BaseModel):
    candidate_id: int
    generated_count: int
    resumes: list[ResumeRead]
