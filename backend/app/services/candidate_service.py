from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate


class CandidateService:
    def get(self, db: Session, candidate_id: int):
        return db.query(Candidate).filter(Candidate.id == candidate_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(Candidate).filter(Candidate.email == email).first()

    def list(self, db: Session, skip: int = 0, limit: int = 25):
        return db.query(Candidate).offset(skip).limit(limit).all()

    def create(self, db: Session, candidate_in: CandidateCreate):
        payload = candidate_in.model_dump(exclude_none=True)
        candidate = Candidate(**payload)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate
