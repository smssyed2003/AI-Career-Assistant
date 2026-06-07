import re

from sqlalchemy.orm import Session
from app.models.job_description import JobDescription


class JobService:
    def list(self, db: Session, skip: int = 0, limit: int = 25, user_id: int | None = None):
        query = db.query(JobDescription)
        if user_id is not None:
            query = query.filter(JobDescription.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def get(self, db: Session, job_id: int):
        return db.query(JobDescription).filter(JobDescription.id == job_id).first()

    def get_for_user(self, db: Session, job_id: int, user_id: int):
        return db.query(JobDescription).filter(JobDescription.id == job_id, JobDescription.user_id == user_id).first()

    def create(self, db: Session, job_in, user_id: int | None = None):
        payload = job_in.model_dump(exclude_none=True)
        if user_id is not None:
            payload["user_id"] = user_id
        job = JobDescription(**payload)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def find_duplicate(self, db: Session, raw_text: str, user_id: int | None = None):
        fingerprint = self._fingerprint(raw_text)
        if not fingerprint:
            return None
        query = db.query(JobDescription)
        if user_id is not None:
            query = query.filter(JobDescription.user_id == user_id)
        for job in query.all():
            existing = self._fingerprint(job.raw_text or job.description or "")
            if existing == fingerprint:
                return job
        return None

    def _fingerprint(self, text: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
        return " ".join(normalized.split())[:600]
