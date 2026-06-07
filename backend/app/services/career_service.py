from collections import Counter

from sqlalchemy.orm import Session

from app.models.application import ApplicationPackage, ApplicationStatusEnum
from app.models.career_report import CareerReport
from app.models.job_description import JobDescription
from app.services.candidate_service import CandidateService


class CareerService:
    def __init__(self):
        self.candidates = CandidateService()

    def list_reports(self, db: Session, candidate_id: int, user_id: int | None = None):
        query = db.query(CareerReport).filter(CareerReport.candidate_id == candidate_id)
        if user_id is not None:
            query = query.filter(CareerReport.user_id == user_id)
        return (
            query
            .order_by(CareerReport.created_at.desc(), CareerReport.id.desc())
            .all()
        )

    def generate(self, db: Session, candidate_id: int, user_id: int | None = None):
        candidate = self.candidates.get_for_user(db, candidate_id, user_id) if user_id is not None else self.candidates.get(db, candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        packages_query = db.query(ApplicationPackage).filter(ApplicationPackage.candidate_id == candidate_id)
        jobs_query = db.query(JobDescription)
        if user_id is not None:
            packages_query = packages_query.filter(ApplicationPackage.user_id == user_id)
            jobs_query = jobs_query.filter(JobDescription.user_id == user_id)
        packages = packages_query.all()
        jobs = jobs_query.all()
        candidate_skills = {str(skill).lower() for skill in (candidate.skills or [])}
        job_skills = self._job_skill_counter(jobs)
        missing_skills = [skill for skill, _ in job_skills.most_common(8) if skill not in candidate_skills]

        interview_count = len(
            [
                package
                for package in packages
                if package.status in {ApplicationStatusEnum.INTERVIEW_SCHEDULED, ApplicationStatusEnum.ACCEPTED}
            ]
        )
        interview_rate = round(interview_count / len(packages) * 100) if packages else 0
        ats_scores = [package.ats_score for package in packages if package.ats_score is not None]
        ats_average = round(sum(ats_scores) / len(ats_scores)) if ats_scores else 0

        report = CareerReport(
            user_id=user_id,
            candidate_id=candidate_id,
            interview_rate=interview_rate,
            ats_average=ats_average,
            new_skills=[skill.title() for skill in missing_skills[:5]],
            trending_jobs=self._trending_jobs(jobs),
            resume_suggestions=self._resume_suggestions(candidate, ats_average),
            certification_suggestions=self._certification_suggestions(missing_skills),
            salary_growth=self._salary_growth(candidate, packages),
            career_roadmap=self._career_roadmap(candidate, missing_skills),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def _job_skill_counter(self, jobs):
        counter = Counter()
        for job in jobs:
            for skill in (job.structured_data or {}).get("skills", []):
                normalized = str(skill).strip().lower()
                if normalized:
                    counter[normalized] += 1
        return counter

    def _trending_jobs(self, jobs):
        titles = Counter(job.title for job in jobs if job.title)
        return [title for title, _ in titles.most_common(5)]

    def _resume_suggestions(self, candidate, ats_average: int):
        suggestions = []
        if not candidate.summary:
            suggestions.append("Add a sharper 3-4 line summary with target role keywords.")
        if len(candidate.projects or []) < 2:
            suggestions.append("Add at least two project entries with technologies and measurable outcomes.")
        if ats_average < 75:
            suggestions.append("Increase ATS keyword coverage before applying to high-priority jobs.")
        if not suggestions:
            suggestions.append("Keep tailoring the top skills and project order for each job.")
        return suggestions

    def _certification_suggestions(self, missing_skills):
        suggestions = []
        for skill in missing_skills[:3]:
            suggestions.append(f"Consider a practical certification or project proof for {skill.title()}.")
        return suggestions or ["No urgent certification gap found from current jobs."]

    def _salary_growth(self, candidate, packages):
        if packages:
            return "Improve interview conversion first, then benchmark salary using roles with 80%+ match scores."
        if (candidate.preferences or {}).get("salary_expectation"):
            return "Keep salary expectation visible and compare it against matched roles after more jobs are added."
        return "Add salary preference later; focus first on match quality and interview rate."

    def _career_roadmap(self, candidate, missing_skills):
        roadmap = [
            "Week 1: Strengthen master profile and ATS resume coverage.",
            "Week 2: Apply only to strong matches and review prepared packages manually.",
            "Week 3: Practice generated interview questions for top roles.",
        ]
        if missing_skills:
            roadmap.append(f"Week 4: Build one small project using {', '.join(skill.title() for skill in missing_skills[:3])}.")
        else:
            roadmap.append("Week 4: Add measurable project outcomes and refine salary targets.")
        return roadmap
