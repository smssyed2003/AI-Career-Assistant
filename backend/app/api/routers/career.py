from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.career import CareerReportRead
from app.services.career_service import CareerService

router = APIRouter()
service = CareerService()


@router.get("/candidates/{candidate_id}/career-reports", response_model=List[CareerReportRead], summary="List career coach reports")
def list_career_reports(candidate_id: int, db: Session = Depends(get_db)):
    return service.list_reports(db, candidate_id)


@router.post("/candidates/{candidate_id}/career-reports/generate", response_model=CareerReportRead, summary="Generate career coach report")
def generate_career_report(candidate_id: int, db: Session = Depends(get_db)):
    try:
        return service.generate(db, candidate_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
