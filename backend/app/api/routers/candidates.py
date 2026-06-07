from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.candidate import CandidateCreate, CandidateRead, CandidateUpdate
from app.db.session import get_db
from app.services.candidate_service import CandidateService

router = APIRouter()
service = CandidateService()

@router.post("/candidates", response_model=CandidateRead, summary="Create candidate profile")
def create_candidate(
    candidate_in: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = service.get_by_email_for_user(db, candidate_in.email, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Candidate already exists")
    return service.create(db, candidate_in, user_id=current_user.id)

@router.get("/candidates", response_model=List[CandidateRead], summary="List candidates")
def list_candidates(
    skip: int = 0,
    limit: int = 25,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.list(db, skip=skip, limit=limit, user_id=current_user.id)

@router.get("/candidates/{candidate_id}", response_model=CandidateRead, summary="Get a candidate")
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = service.get_for_user(db, candidate_id, current_user.id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/candidates/{candidate_id}", response_model=CandidateRead, summary="Update a candidate profile")
def update_candidate(
    candidate_id: int,
    candidate_in: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = service.get_for_user(db, candidate_id, current_user.id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate_in.email and candidate_in.email != candidate.email:
        existing = service.get_by_email_for_user(db, candidate_in.email, current_user.id)
        if existing and existing.id != candidate.id:
            raise HTTPException(status_code=400, detail="Candidate email already exists")
    return service.update(db, candidate, candidate_in)
