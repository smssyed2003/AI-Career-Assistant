from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CandidateService:
    def get(self, db: Session, candidate_id: int):
        return db.query(Candidate).filter(Candidate.id == candidate_id).first()

    def get_for_user(self, db: Session, candidate_id: int, user_id: int):
        return db.query(Candidate).filter(Candidate.id == candidate_id, Candidate.user_id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(Candidate).filter(Candidate.email == email).first()

    def get_by_email_for_user(self, db: Session, email: str, user_id: int):
        return db.query(Candidate).filter(Candidate.email == email, Candidate.user_id == user_id).first()

    def list(self, db: Session, skip: int = 0, limit: int = 25, user_id: int | None = None):
        query = db.query(Candidate)
        if user_id is not None:
            query = query.filter(Candidate.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, candidate_in: CandidateCreate, user_id: int | None = None):
        payload = candidate_in.model_dump(exclude_none=True)
        if user_id is not None:
            payload["user_id"] = user_id
        candidate = Candidate(**payload)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate

    def update(self, db: Session, candidate: Candidate, candidate_in: CandidateUpdate):
        payload = candidate_in.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(candidate, key, value)
        db.commit()
        db.refresh(candidate)
        return candidate
