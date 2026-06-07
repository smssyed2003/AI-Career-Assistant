import re

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

    def find_duplicate(self, db: Session, raw_text: str):
        fingerprint = self._fingerprint(raw_text)
        if not fingerprint:
            return None
        for job in db.query(JobDescription).all():
            existing = self._fingerprint(job.raw_text or job.description or "")
            if existing == fingerprint:
                return job
        return None

    def _fingerprint(self, text: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
        return " ".join(normalized.split())[:600]
