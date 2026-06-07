from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.application import ApplicationPackage, ApplicationStatusEnum
from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.services.candidate_service import CandidateService
from app.services.job_service import JobService
from app.services.match_service import MatchService
from app.services.resume_service import ResumeService


class ApplicationService:
    def __init__(self):
        self.candidates = CandidateService()
        self.jobs = JobService()
        self.matcher = MatchService()
        self.resumes = ResumeService()

    def list(self, db: Session, candidate_id: int | None = None, job_id: int | None = None, user_id: int | None = None):
        query = db.query(ApplicationPackage)
        if user_id is not None:
            query = query.filter(ApplicationPackage.user_id == user_id)
        if candidate_id is not None:
            query = query.filter(ApplicationPackage.candidate_id == candidate_id)
        if job_id is not None:
            query = query.filter(ApplicationPackage.job_id == job_id)
        return query.order_by(ApplicationPackage.created_at.desc(), ApplicationPackage.id.desc()).all()

    def get(self, db: Session, package_id: int, user_id: int | None = None):
        query = db.query(ApplicationPackage).filter(ApplicationPackage.id == package_id)
        if user_id is not None:
            query = query.filter(ApplicationPackage.user_id == user_id)
        return query.first()

    def prepare(self, db: Session, candidate_id: int, job_id: int, user_id: int | None = None):
        candidate = self.candidates.get_for_user(db, candidate_id, user_id) if user_id is not None else self.candidates.get(db, candidate_id)
        job = self.jobs.get_for_user(db, job_id, user_id) if user_id is not None else self.jobs.get(db, job_id)
        if not candidate or not job:
            raise ValueError("Candidate or job not found")

        match = self.matcher.score_candidate_job(candidate, job)
        readiness = self.matcher.analyze_interview_readiness(db, candidate_id, job_id, user_id=user_id)
        match_percent = self._percent(match.score)
        ats_score = self.resumes.estimate_ats_score(candidate, self.resumes.DEFAULT_TYPES[1], job)
        optimized_resume = self.resumes.generate_for_job(db, candidate, job, ats_score=ats_score)

        package = ApplicationPackage(
            user_id=user_id,
            candidate_id=candidate.id,
            job_id=job.id,
            match_score=match_percent,
            ats_score=ats_score,
            interview_probability=self._interview_probability(match.score, readiness.readiness_score),
            optimized_resume_id=optimized_resume.id,
            cover_letter=self._cover_letter(candidate, job, match.matched_skills),
            hr_introduction=self._hr_intro(candidate, job, match_percent),
            email_template=self._email_template(candidate, job),
            screening_answers=self._screening_answers(candidate, job, match.matched_skills),
            status=ApplicationStatusEnum.PREPARED,
            skill_match_details={
                "score": self._percent(match.skill_match_score),
                "matched_skills": match.matched_skills,
                "missing_skills": match.missing_skills,
            },
            experience_match_details=self._experience_details(candidate, job),
            project_match_details=self._project_details(candidate, job),
        )
        db.add(package)
        db.commit()
        db.refresh(package)
        return package

    def _interview_probability(self, match_score: float, readiness_score: float) -> int:
        return self._percent((match_score * 0.6) + (readiness_score * 0.4))

    def _cover_letter(self, candidate: Candidate, job: JobDescription, matched_skills: list[str]) -> str:
        company = job.company or "your team"
        skills = ", ".join(matched_skills[:6]) if matched_skills else "the required skills"
        return (
            f"Dear Hiring Team,\n\n"
            f"I am interested in the {job.title} role at {company}. "
            f"My background includes {candidate.summary or 'hands-on work across relevant technical projects'}, "
            f"and I can bring direct experience with {skills}.\n\n"
            f"I would welcome the chance to discuss how my projects, skills, and learning pace align with this role.\n\n"
            f"Regards,\n{candidate.full_name}"
        )

    def _hr_intro(self, candidate: Candidate, job: JobDescription, match_percent: int) -> str:
        return (
            f"Hi, I am {candidate.full_name}. I am applying for {job.title}"
            f"{' at ' + job.company if job.company else ''}. "
            f"My current profile shows a {match_percent}% match based on the parsed JD, with strengths in "
            f"{', '.join((candidate.skills or [])[:5]) or 'the core role requirements'}."
        )

    def _email_template(self, candidate: Candidate, job: JobDescription) -> str:
        company = job.company or "Hiring Team"
        return (
            f"Subject: Application for {job.title} - {candidate.full_name}\n\n"
            f"Hello {company},\n\n"
            f"Please find my application package for the {job.title} role. "
            f"I have attached a tailored resume and included a short cover note for your review.\n\n"
            f"Thank you,\n{candidate.full_name}"
        )

    def _screening_answers(self, candidate: Candidate, job: JobDescription, matched_skills: list[str]) -> dict:
        return {
            "Why are you a good fit?": (
                f"My profile aligns with {job.title} through skills such as "
                f"{', '.join(matched_skills[:5]) or ', '.join((candidate.skills or [])[:5]) or 'the listed requirements'}."
            ),
            "What is your current location preference?": (
                (candidate.preferences or {}).get("remote_preference")
                or ", ".join((candidate.preferences or {}).get("locations") or [])
                or "Open to suitable opportunities based on the role."
            ),
            "What should the recruiter review first?": "The tailored resume, project evidence, and matched skills summary.",
        }

    def _experience_details(self, candidate: Candidate, job: JobDescription) -> dict:
        text = " ".join(str(item) for item in (candidate.experience or []))
        job_text = f"{job.description or ''} {job.raw_text or ''}".lower()
        experience_keywords = ["intern", "junior", "mid", "senior", "lead", "years", "backend", "data", "ai", "ml"]
        matched = [keyword for keyword in experience_keywords if keyword in text.lower() and keyword in job_text]
        return {
            "matched_signals": matched,
            "candidate_entries": len(candidate.experience or []),
            "summary": "Experience evidence found." if matched else "Add stronger experience evidence before submission.",
        }

    def _project_details(self, candidate: Candidate, job: JobDescription) -> dict:
        job_skills = [str(skill).lower() for skill in (job.structured_data or {}).get("skills", [])]
        matched_projects = []
        for project in candidate.projects or []:
            project_text = str(project).lower()
            if any(skill in project_text for skill in job_skills):
                matched_projects.append(project)
        return {
            "matched_project_count": len(matched_projects),
            "summary": "Project evidence found." if matched_projects else "Add one role-relevant project if available.",
        }

    def _percent(self, score: float) -> int:
        return max(0, min(100, round(score * 100)))
