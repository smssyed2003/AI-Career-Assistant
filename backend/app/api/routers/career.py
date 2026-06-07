from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.career import CareerReportRead
from app.services.career_service import CareerService

router = APIRouter()
service = CareerService()


@router.get("/candidates/{candidate_id}/career-reports", response_model=List[CareerReportRead], summary="List career coach reports")
def list_career_reports(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.list_reports(db, candidate_id, user_id=current_user.id)


@router.post("/candidates/{candidate_id}/career-reports/generate", response_model=CareerReportRead, summary="Generate career coach report")
def generate_career_report(candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.generate(db, candidate_id, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
