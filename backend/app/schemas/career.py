from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CareerReportRead(BaseModel):
    id: int
    candidate_id: int
    interview_rate: Optional[int] = None
    ats_average: Optional[int] = None
    new_skills: List[str] = Field(default_factory=list)
    trending_jobs: List[str] = Field(default_factory=list)
    resume_suggestions: List[str] = Field(default_factory=list)
    certification_suggestions: List[str] = Field(default_factory=list)
    salary_growth: Optional[str] = None
    career_roadmap: List[str] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
