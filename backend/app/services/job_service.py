from sqlalchemy.orm import Session
from app.models.job_description import JobDescription


class JobService:
    def list(self, db: Session, skip: int = 0, limit: int = 25):
        return db.query(JobDescription).offset(skip).limit(limit).all()

    def get(self, db: Session, job_id: int):
        return db.query(JobDescription).filter(JobDescription.id == job_id).first()

    def create(self, db: Session, job_in):
        job = JobDescription(**job_in.model_dump(exclude_none=True))
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
