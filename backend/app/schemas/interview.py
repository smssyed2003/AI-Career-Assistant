from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InterviewQuestionType(str, Enum):
    HR = "hr"
    TECHNICAL = "technical"
    CODING = "coding"
    AI = "ai"
    LLM = "llm"
    RAG = "rag"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"


class InterviewPrepRead(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    application_package_id: Optional[int] = None
    question_type: InterviewQuestionType
    question_text: str
    suggested_answer: Optional[str] = None
    keyword_highlights: List[str] = Field(default_factory=list)
    difficulty_level: str = "medium"
    practice_count: int = 0
    user_answer: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
