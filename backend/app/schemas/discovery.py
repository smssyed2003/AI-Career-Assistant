from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.job import JobDescriptionRead


class JobSourceType(str, Enum):
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    INDEED = "indeed"
    WELLFOUND = "wellfound"
    REMOTE_OK = "remote_ok"
    COMPANY_CAREERS = "company_careers"
    STARTUP_CAREERS = "startup_careers"
    GOVERNMENT_JOBS = "government_jobs"
    INTERNSHIP_PORTALS = "internship_portals"
    AI_COMPANY_CAREERS = "ai_company_careers"
    MANUAL = "manual"


class DiscoveryIngestRequest(BaseModel):
    source: JobSourceType = JobSourceType.MANUAL
    source_url: Optional[str] = None
    job_texts: List[str] = Field(min_length=1)


class JobSourceRead(BaseModel):
    id: int
    job_description_id: int
    source: JobSourceType
    source_job_id: Optional[str] = None
    source_url: Optional[str] = None
    discovered_at: datetime
    is_duplicate: bool
    duplicate_of_source_id: Optional[int] = None
    is_active: bool
    views_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DiscoveryIngestResult(BaseModel):
    source: JobSourceType
    created_count: int
    duplicate_count: int
    jobs: List[JobDescriptionRead]
    duplicate_job_ids: List[int] = Field(default_factory=list)
