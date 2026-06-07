from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CandidateDashboardRead(BaseModel):
    profile_count: int = 0
    active_candidate_id: Optional[int] = None
    profile_completion: int = Field(default=0, ge=0, le=100)
    resume_versions: int = 0
    job_count: int = 0
    application_count: int = 0
    high_match_count: int = 0
    interview_prep_count: int = 0
    career_report_count: int = 0
    application_status_counts: Dict[str, int] = Field(default_factory=dict)
    next_actions: List[str] = Field(default_factory=list)
