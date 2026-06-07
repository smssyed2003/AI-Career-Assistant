from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl
from typing import List, Optional, Dict, Any


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None


class ExperienceEntry(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class ProjectEntry(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    link: Optional[HttpUrl] = None


class CandidatePreferences(BaseModel):
    employment_type: Optional[str] = None
    remote_preference: Optional[str] = None
    locations: Optional[List[str]] = None
    salary_expectation: Optional[str] = None
    industries: Optional[List[str]] = None


class CandidateBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    summary: Optional[str] = None
    education: Optional[List[EducationEntry]] = Field(default_factory=list)
    experience: Optional[List[ExperienceEntry]] = Field(default_factory=list)
    projects: Optional[List[ProjectEntry]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    links: Optional[List[HttpUrl]] = Field(default_factory=list)
    preferences: Optional[CandidatePreferences] = None
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    education: Optional[List[EducationEntry]] = None
    experience: Optional[List[ExperienceEntry]] = None
    projects: Optional[List[ProjectEntry]] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    links: Optional[List[HttpUrl]] = None
    preferences: Optional[CandidatePreferences] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class CandidateRead(CandidateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
