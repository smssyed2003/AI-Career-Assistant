from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import ApplicationPackage
from app.models.candidate import Candidate
from app.models.career_report import CareerReport
from app.models.interview_prep import InterviewPrep
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.models.user import User
from app.schemas.dashboard import CandidateDashboardRead

router = APIRouter()


@router.get("/dashboard/candidate", response_model=CandidateDashboardRead, summary="Candidate dashboard summary")
def candidate_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    candidates = (
        db.query(Candidate)
        .filter(Candidate.user_id == current_user.id)
        .order_by(Candidate.updated_at.desc(), Candidate.id.desc())
        .all()
    )
    active_candidate = candidates[0] if candidates else None
    applications = db.query(ApplicationPackage).filter(ApplicationPackage.user_id == current_user.id).all()
    status_counts = Counter(str(package.status.value if hasattr(package.status, "value") else package.status) for package in applications)

    resume_count = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    job_count = db.query(JobDescription).filter(JobDescription.user_id == current_user.id).count()
    interview_count = db.query(InterviewPrep).filter(InterviewPrep.user_id == current_user.id).count()
    report_count = db.query(CareerReport).filter(CareerReport.user_id == current_user.id).count()
    high_match_count = len([package for package in applications if (package.match_score or 0) >= 80])

    next_actions = _next_actions(
        has_candidate=bool(active_candidate),
        profile_completion=_profile_completion(active_candidate),
        resume_count=resume_count,
        job_count=job_count,
        application_count=len(applications),
        interview_count=interview_count,
        report_count=report_count,
    )

    return CandidateDashboardRead(
        profile_count=len(candidates),
        active_candidate_id=active_candidate.id if active_candidate else None,
        profile_completion=_profile_completion(active_candidate),
        resume_versions=resume_count,
        job_count=job_count,
        application_count=len(applications),
        high_match_count=high_match_count,
        interview_prep_count=interview_count,
        career_report_count=report_count,
        application_status_counts=dict(status_counts),
        next_actions=next_actions,
    )


def _profile_completion(candidate: Candidate | None) -> int:
    if not candidate:
        return 0
    checks = [
        bool(candidate.full_name),
        bool(candidate.email),
        bool(candidate.phone),
        bool(candidate.summary),
        bool(candidate.skills),
        bool(candidate.education),
        bool(candidate.experience),
        bool(candidate.projects),
        bool(candidate.certifications),
        bool(candidate.links),
    ]
    return round((sum(checks) / len(checks)) * 100)


def _next_actions(
    has_candidate: bool,
    profile_completion: int,
    resume_count: int,
    job_count: int,
    application_count: int,
    interview_count: int,
    report_count: int,
) -> list[str]:
    actions = []
    if not has_candidate:
        actions.append("Create your candidate profile.")
    if has_candidate and profile_completion < 70:
        actions.append("Add summary, projects, experience, links, or certificates to improve profile completeness.")
    if has_candidate and resume_count == 0:
        actions.append("Generate your master and role-specific resume versions.")
    if job_count == 0:
        actions.append("Ingest at least one job description.")
    if job_count > 0 and application_count == 0:
        actions.append("Prepare a review-ready application package for a strong match.")
    if application_count > 0 and interview_count == 0:
        actions.append("Generate interview questions for your top application.")
    if report_count == 0:
        actions.append("Generate a career coach report after adding jobs and applications.")
    return actions[:5]
