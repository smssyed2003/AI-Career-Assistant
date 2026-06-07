from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.interview import InterviewPrepRead
from app.services.interview_service import InterviewService

router = APIRouter()
service = InterviewService()


@router.get("/jobs/{job_id}/interview-prep/{candidate_id}", response_model=List[InterviewPrepRead], summary="List interview prep questions")
def list_interview_prep(job_id: int, candidate_id: int, db: Session = Depends(get_db)):
    return service.list_for_job(db, candidate_id=candidate_id, job_id=job_id)


@router.post("/jobs/{job_id}/interview-prep/{candidate_id}", response_model=List[InterviewPrepRead], summary="Generate interview prep questions")
def generate_interview_prep(
    job_id: int,
    candidate_id: int,
    application_package_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    try:
        return service.generate(
            db,
            candidate_id=candidate_id,
            job_id=job_id,
            application_package_id=application_package_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
