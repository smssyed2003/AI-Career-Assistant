from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.candidate import CandidateCreate, CandidateRead
from app.db.session import get_db
from app.services.candidate_service import CandidateService

router = APIRouter()
service = CandidateService()

@router.post("/candidates", response_model=CandidateRead, summary="Create candidate profile")
def create_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db)):
    existing = service.get_by_email(db, candidate_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Candidate already exists")
    return service.create(db, candidate_in)

@router.get("/candidates", response_model=List[CandidateRead], summary="List candidates")
def list_candidates(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    return service.list(db, skip=skip, limit=limit)

@router.get("/candidates/{candidate_id}", response_model=CandidateRead, summary="Get a candidate")
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = service.get(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
