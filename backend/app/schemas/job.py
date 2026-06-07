from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any


class JobDescriptionBase(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    raw_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class JobDescriptionCreate(JobDescriptionBase):
    pass


class JobMatch(BaseModel):
    job_id: int
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    score: float
    skill_match_score: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None


class SkillGapAnalysis(BaseModel):
    job_id: int
    candidate_id: int
    title: str
    company: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    candidate_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    extra_candidate_skills: List[str] = Field(default_factory=list)
    score: float


class ReadinessAnalysis(BaseModel):
    job_id: int
    candidate_id: int
    readiness_score: float
    summary: str
    top_strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    recommended_learning: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


from pydantic import ConfigDict

class JobDescriptionRead(JobDescriptionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
