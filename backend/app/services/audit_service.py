from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    def log(
        self,
        db: Session,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str | int | None = None,
        details: dict | None = None,
    ):
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            details=details or {},
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def list(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).offset(skip).limit(limit).all()
