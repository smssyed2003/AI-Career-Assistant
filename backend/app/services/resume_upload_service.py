from sqlalchemy.orm import Session

from app.models.resume_upload import ResumeUpload


class ResumeUploadService:
    def create(
        self,
        db: Session,
        user_id: int,
        file_name: str,
        file_type: str,
        extracted_text: str,
        parsed_profile: dict,
        source: str | None = None,
        candidate_id: int | None = None,
    ):
        upload = ResumeUpload(
            user_id=user_id,
            candidate_id=candidate_id,
            file_name=file_name,
            file_type=file_type,
            source=source,
            extracted_text=extracted_text,
            parsed_profile=parsed_profile,
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return upload

    def list(self, db: Session, user_id: int, candidate_id: int | None = None):
        query = db.query(ResumeUpload).filter(ResumeUpload.user_id == user_id)
        if candidate_id is not None:
            query = query.filter(ResumeUpload.candidate_id == candidate_id)
        return query.order_by(ResumeUpload.created_at.desc(), ResumeUpload.id.desc()).all()

    def get(self, db: Session, upload_id: int, user_id: int):
        return db.query(ResumeUpload).filter(ResumeUpload.id == upload_id, ResumeUpload.user_id == user_id).first()
