from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AdminAnalyticsRead(BaseModel):
    total_users: int = 0
    active_users: int = 0
    admin_users: int = 0
    candidate_users: int = 0
    candidate_profiles: int = 0
    jobs: int = 0
    resumes: int = 0
    application_packages: int = 0
    audit_log_count: int = 0
    application_status_counts: Dict[str, int] = Field(default_factory=dict)
    system_health: Dict[str, Any] = Field(default_factory=dict)


class SystemSettingRead(BaseModel):
    id: int
    key: str
    category: str
    value: Any = None
    description: Optional[str] = None
    is_secret: bool = False
    updated_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemSettingUpdate(BaseModel):
    value: Any = None
    description: Optional[str] = None


class AdminSettingsRead(BaseModel):
    settings: List[SystemSettingRead] = Field(default_factory=list)
