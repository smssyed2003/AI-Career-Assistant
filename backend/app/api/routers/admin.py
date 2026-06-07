from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.application import ApplicationPackage
from app.models.audit_log import AuditLog
from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.models.user import User
from app.schemas.admin import AdminAnalyticsRead, AdminSettingsRead, SystemSettingRead, SystemSettingUpdate
from app.schemas.audit import AuditLogRead
from app.schemas.auth import UserAdminRead, UserRoleUpdate, UserStatusUpdate
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.llm_queue_service import llm_rate_limiter
from app.services.system_setting_service import SystemSettingService

router = APIRouter()
service = AuthService()
settings_service = SystemSettingService()
audit_service = AuditService()


@router.get("/admin/users", response_model=List[UserAdminRead], summary="List users")
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    return service.list_users(db, skip=skip, limit=limit)


@router.get("/admin/analytics", response_model=AdminAnalyticsRead, summary="Admin analytics overview")
def admin_analytics(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    status_rows = (
        db.query(ApplicationPackage.status, func.count(ApplicationPackage.id))
        .group_by(ApplicationPackage.status)
        .all()
    )
    status_counts = {
        str(status.value if hasattr(status, "value") else status): count
        for status, count in status_rows
    }
    active_users = db.query(User).filter(User.is_active.is_(True)).count()
    admin_users = db.query(User).filter(User.role == "admin").count()
    return AdminAnalyticsRead(
        total_users=db.query(User).count(),
        active_users=active_users,
        admin_users=admin_users,
        candidate_users=db.query(User).filter(User.role == "user").count(),
        candidate_profiles=db.query(Candidate).count(),
        jobs=db.query(JobDescription).count(),
        resumes=db.query(Resume).count(),
        application_packages=db.query(ApplicationPackage).count(),
        audit_log_count=db.query(AuditLog).count(),
        application_status_counts=status_counts,
        system_health={
            "database": "connected",
            "llm_queue": llm_rate_limiter.status(),
            "safe_application_mode": "manual_review_only",
            "auto_apply_enabled": False,
        },
    )


@router.get("/admin/settings", response_model=AdminSettingsRead, summary="List admin-managed settings")
def list_settings(
    category: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AdminSettingsRead(settings=settings_service.list(db, category=category))


@router.patch("/admin/settings/{key}", response_model=SystemSettingRead, summary="Update an admin-managed setting")
def update_setting(
    key: str,
    payload: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    setting = settings_service.update(
        db,
        key=key,
        value=payload.value,
        description=payload.description,
        updated_by_user_id=current_admin.id,
    )
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    audit_service.log(
        db,
        actor_user_id=current_admin.id,
        action="admin.setting.updated",
        target_type="system_setting",
        target_id=setting.key,
        details={"key": setting.key, "category": setting.category},
    )
    return setting


@router.get("/admin/audit-logs", response_model=List[AuditLogRead], summary="List admin audit logs")
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return audit_service.list(db, skip=skip, limit=limit)


@router.patch("/admin/users/{user_id}/role", response_model=UserAdminRead, summary="Update user role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    if user_id == current_admin.id and payload.role != "admin":
        raise HTTPException(status_code=400, detail="You cannot remove your own admin role")
    user = service.update_role(db, user_id, payload.role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    audit_service.log(
        db,
        actor_user_id=current_admin.id,
        action="admin.user.role_updated",
        target_type="user",
        target_id=user.id,
        details={"email": user.email, "role": user.role},
    )
    return user


@router.patch("/admin/users/{user_id}/status", response_model=UserAdminRead, summary="Activate or deactivate user")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    if user_id == current_admin.id and not payload.is_active:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    user = service.update_status(db, user_id, payload.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    audit_service.log(
        db,
        actor_user_id=current_admin.id,
        action="admin.user.status_updated",
        target_type="user",
        target_id=user.id,
        details={"email": user.email, "is_active": user.is_active},
    )
    return user
