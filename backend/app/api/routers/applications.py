from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.application import ApplicationPackageRead
from app.services.application_service import ApplicationService

router = APIRouter()
service = ApplicationService()


@router.get("/application-packages", response_model=List[ApplicationPackageRead], summary="List application packages")
def list_application_packages(
    candidate_id: Optional[int] = None,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return service.list(db, candidate_id=candidate_id, job_id=job_id)


@router.get("/application-packages/{package_id}", response_model=ApplicationPackageRead, summary="Get an application package")
def get_application_package(package_id: int, db: Session = Depends(get_db)):
    package = service.get(db, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Application package not found")
    return package


@router.post(
    "/jobs/{job_id}/application-package/{candidate_id}",
    response_model=ApplicationPackageRead,
    summary="Prepare a review-ready application package",
)
def prepare_application_package(job_id: int, candidate_id: int, db: Session = Depends(get_db)):
    try:
        return service.prepare(db, candidate_id=candidate_id, job_id=job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
