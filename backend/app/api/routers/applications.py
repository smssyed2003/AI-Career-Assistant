from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.application import ApplicationPackageRead
from app.services.application_service import ApplicationService

router = APIRouter()
service = ApplicationService()


@router.get("/application-packages", response_model=List[ApplicationPackageRead], summary="List application packages")
def list_application_packages(
    candidate_id: Optional[int] = None,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.list(db, candidate_id=candidate_id, job_id=job_id, user_id=current_user.id)


@router.get("/application-packages/{package_id}", response_model=ApplicationPackageRead, summary="Get an application package")
def get_application_package(package_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    package = service.get(db, package_id, user_id=current_user.id)
    if not package:
        raise HTTPException(status_code=404, detail="Application package not found")
    return package


@router.post(
    "/jobs/{job_id}/application-package/{candidate_id}",
    response_model=ApplicationPackageRead,
    summary="Prepare a review-ready application package",
)
def prepare_application_package(job_id: int, candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.prepare(db, candidate_id=candidate_id, job_id=job_id, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
