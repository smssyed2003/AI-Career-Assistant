from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.resume import ResumeGenerationResult, ResumeRead
from app.services.candidate_service import CandidateService
from app.services.resume_service import ResumeService

router = APIRouter()
candidate_service = CandidateService()
resume_service = ResumeService()


@router.get("/candidates/{candidate_id}/resumes", response_model=List[ResumeRead], summary="List candidate resume versions")
def list_candidate_resumes(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_service.get(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return resume_service.list_for_candidate(db, candidate_id)


@router.post(
    "/candidates/{candidate_id}/resumes/generate",
    response_model=ResumeGenerationResult,
    summary="Generate standard resume versions",
)
def generate_candidate_resumes(candidate_id: int, db: Session = Depends(get_db)):
    candidate = candidate_service.get(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    resumes = resume_service.generate_default_versions(db, candidate)
    return ResumeGenerationResult(candidate_id=candidate_id, generated_count=len(resumes), resumes=resumes)


@router.get("/resumes/{resume_id}", response_model=ResumeRead, summary="Get a resume version")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = resume_service.get(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
