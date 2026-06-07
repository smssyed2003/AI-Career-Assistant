from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ResumeUploadRead(BaseModel):
    id: int
    user_id: int
    candidate_id: Optional[int] = None
    file_name: str
    file_type: str
    source: Optional[str] = None
    extracted_text: str
    parsed_profile: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
