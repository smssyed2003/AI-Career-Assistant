from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl
from typing import List, Optional, Dict, Any


class EducationEntry(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None


class ExperienceEntry(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ProjectEntry(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = Field(default_factory=list)
    link: Optional[HttpUrl] = None


class CandidatePreferences(BaseModel):
    employment_type: Optional[str] = None
    remote_preference: Optional[str] = None
    locations: Optional[List[str]] = Field(default_factory=list)
    salary_expectation: Optional[str] = None
    industries: Optional[List[str]] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    education: Optional[List[EducationEntry]] = Field(default_factory=list)
    experience: Optional[List[ExperienceEntry]] = Field(default_factory=list)
    projects: Optional[List[ProjectEntry]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    links: Optional[List[HttpUrl]] = Field(default_factory=list)
    preferences: Optional[CandidatePreferences] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ResumeParseResult(BaseModel):
    file_name: str
    file_type: str
    extracted_text: str
    profile: CandidateProfile
    source: Optional[str] = None
    parsed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
