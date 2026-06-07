from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.job import JobDescriptionCreate, JobDescriptionRead, JobMatch, SkillGapAnalysis, ReadinessAnalysis
from app.db.session import get_db
from app.services.job_service import JobService
from app.services.match_service import MatchService
from app.services.llm_service import JobDescriptionExtractor
from app.services.parse_service import ResumeParser

router = APIRouter()
service = JobService()
matcher = MatchService()
parser = ResumeParser()
extractor = JobDescriptionExtractor()

@router.get("/jobs", response_model=List[JobDescriptionRead], summary="List parsed job descriptions")
def list_jobs(skip: int = 0, limit: int = 25, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.list(db, skip=skip, limit=limit, user_id=current_user.id)

@router.get("/jobs/{job_id}", response_model=JobDescriptionRead, summary="Get a job description")
def get_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = service.get_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job

@router.post("/jobs/ingest", response_model=JobDescriptionRead, summary="Ingest a job description file or raw text")
async def ingest_job(
    file: UploadFile | None = File(None),
    text: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file is None and not text:
        raise HTTPException(status_code=400, detail="Job description file or text is required")

    if file is not None:
        text = parser.extract_text(file)
    parsed = extractor.extract_job(text)
    job_in = JobDescriptionCreate(**parsed)
    job = service.create(db, job_in, user_id=current_user.id)
    return job

@router.get("/jobs/match/{candidate_id}", response_model=List[JobMatch], summary="Match candidate against job descriptions")
def match_candidate(candidate_id: int, top_k: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    matches = matcher.match_candidate(db, candidate_id, top_k=top_k, user_id=current_user.id)
    return matches

@router.get("/jobs/{job_id}/skill-gap/{candidate_id}", response_model=SkillGapAnalysis, summary="Analyze skill gaps for a candidate against a job")
def skill_gap(job_id: int, candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        gap = matcher.analyze_skill_gap(db, candidate_id, job_id, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return gap

@router.get("/jobs/{job_id}/readiness/{candidate_id}", response_model=ReadinessAnalysis, summary="Evaluate interview readiness for a candidate against a job")
def interview_readiness(job_id: int, candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        readiness = matcher.analyze_interview_readiness(db, candidate_id, job_id, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return readiness
