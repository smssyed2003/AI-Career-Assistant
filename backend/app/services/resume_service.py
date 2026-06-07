from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.resume import Resume, ResumeTypeEnum
from app.schemas.resume import ResumeCreate


class ResumeService:
    DEFAULT_TYPES = [
        ResumeTypeEnum.MASTER,
        ResumeTypeEnum.ATS,
        ResumeTypeEnum.AI,
        ResumeTypeEnum.ML,
        ResumeTypeEnum.PYTHON,
        ResumeTypeEnum.BACKEND,
        ResumeTypeEnum.DATA_SCIENTIST,
    ]

    FOCUS_KEYWORDS = {
        ResumeTypeEnum.MASTER: [],
        ResumeTypeEnum.ATS: ["impact", "metrics", "keywords", "delivery"],
        ResumeTypeEnum.AI: ["ai", "llm", "rag", "machine learning", "model", "prompt"],
        ResumeTypeEnum.ML: ["machine learning", "model", "data", "python", "evaluation"],
        ResumeTypeEnum.PYTHON: ["python", "fastapi", "django", "flask", "automation", "sql"],
        ResumeTypeEnum.BACKEND: ["backend", "api", "database", "cloud", "microservices", "docker"],
        ResumeTypeEnum.DATA_SCIENTIST: ["data", "analytics", "machine learning", "statistics", "sql"],
    }

    def list_for_candidate(self, db: Session, candidate_id: int):
        return (
            db.query(Resume)
            .filter(Resume.candidate_id == candidate_id)
            .order_by(Resume.created_at.desc(), Resume.id.desc())
            .all()
        )

    def get(self, db: Session, resume_id: int):
        return db.query(Resume).filter(Resume.id == resume_id).first()

    def create(self, db: Session, candidate_id: int, resume_in: ResumeCreate):
        payload = resume_in.model_dump(exclude_none=True)
        payload["resume_type"] = ResumeTypeEnum(payload["resume_type"])
        resume = Resume(candidate_id=candidate_id, **payload)
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    def generate_default_versions(self, db: Session, candidate: Candidate):
        created = []
        for resume_type in self.DEFAULT_TYPES:
            content = self.render_resume(candidate, resume_type)
            resume = Resume(
                candidate_id=candidate.id,
                resume_type=resume_type,
                content=content,
                ats_score=self.estimate_ats_score(candidate, resume_type),
            )
            db.add(resume)
            created.append(resume)
        db.commit()
        for resume in created:
            db.refresh(resume)
        return created

    def generate_for_job(self, db: Session, candidate: Candidate, job: JobDescription, ats_score: Optional[int] = None):
        content = self.render_resume(candidate, ResumeTypeEnum.ATS, job=job)
        resume = Resume(
            candidate_id=candidate.id,
            resume_type=ResumeTypeEnum.ATS,
            content=content,
            optimized_for_job_id=job.id,
            ats_score=ats_score or self.estimate_ats_score(candidate, ResumeTypeEnum.ATS, job),
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    def render_resume(
        self,
        candidate: Candidate,
        resume_type: ResumeTypeEnum,
        job: Optional[JobDescription] = None,
    ) -> str:
        focus = self.FOCUS_KEYWORDS.get(resume_type, [])
        job_skills = self._normalize_list((job.structured_data or {}).get("skills", [])) if job else []
        priority_terms = job_skills or focus
        skills = self._prioritize(candidate.skills or [], priority_terms)

        title = resume_type.value.replace("_", " ").title()
        if job:
            title = f"ATS Resume for {job.title}"

        sections = [
            f"{candidate.full_name}",
            f"{title}",
            "",
            "CONTACT",
            self._join_present([candidate.email, candidate.phone]),
            "",
            "SUMMARY",
            self._summary(candidate, resume_type, job),
            "",
            "CORE SKILLS",
            ", ".join(skills) if skills else "Add role-relevant technical and business skills.",
            "",
            "EXPERIENCE",
            self._format_entries(candidate.experience or [], ["title", "company", "description"]),
            "",
            "PROJECTS",
            self._format_entries(candidate.projects or [], ["name", "description", "technologies"]),
            "",
            "EDUCATION",
            self._format_entries(candidate.education or [], ["degree", "institution", "field_of_study"]),
            "",
            "CERTIFICATIONS",
            self._format_simple_list(candidate.certifications or []),
            "",
            "LINKS",
            self._format_simple_list(candidate.links or []),
        ]

        if job:
            sections.extend(
                [
                    "",
                    "TARGET JOB KEYWORDS",
                    ", ".join(job_skills) if job_skills else "No structured job keywords extracted yet.",
                ]
            )

        return "\n".join(sections).strip()

    def estimate_ats_score(
        self,
        candidate: Candidate,
        resume_type: ResumeTypeEnum,
        job: Optional[JobDescription] = None,
    ) -> int:
        candidate_skills = set(self._normalize_list(candidate.skills or []))
        if job:
            job_skills = set(self._normalize_list((job.structured_data or {}).get("skills", [])))
            if job_skills:
                return min(98, 55 + round(len(candidate_skills.intersection(job_skills)) / len(job_skills) * 40))
        base = 70 if candidate.summary else 62
        base += min(15, len(candidate_skills) * 2)
        if resume_type != ResumeTypeEnum.MASTER:
            base += 5
        return min(95, base)

    def _summary(self, candidate: Candidate, resume_type: ResumeTypeEnum, job: Optional[JobDescription]) -> str:
        if job:
            return (
                f"{candidate.summary or 'Candidate profile prepared for targeted application.'} "
                f"Positioned for {job.title} with emphasis on role keywords, measurable impact, and relevant project evidence."
            )
        if resume_type == ResumeTypeEnum.MASTER:
            return candidate.summary or "Master candidate profile summary pending enrichment from intake documents."
        focus_terms = ", ".join(self.FOCUS_KEYWORDS.get(resume_type, [])[:4])
        return (
            f"{candidate.summary or 'Candidate profile summary pending enrichment.'} "
            f"This version emphasizes {focus_terms or 'broad career fit'}."
        )

    def _prioritize(self, items: Iterable, priority_terms: list[str]) -> list[str]:
        normalized_items = [str(item) for item in items if str(item).strip()]
        priority = [term.lower() for term in priority_terms]
        matched = [item for item in normalized_items if any(term in item.lower() for term in priority)]
        remaining = [item for item in normalized_items if item not in matched]
        return matched + remaining

    def _format_entries(self, entries: list, fields: list[str]) -> str:
        if not entries:
            return "Add details from candidate intake."
        lines = []
        for entry in entries:
            if not isinstance(entry, dict):
                lines.append(f"- {entry}")
                continue
            values = []
            for field in fields:
                value = entry.get(field)
                if isinstance(value, list):
                    value = ", ".join(str(item) for item in value)
                if value:
                    values.append(str(value))
            lines.append(f"- {' | '.join(values)}" if values else "- Add details.")
        return "\n".join(lines)

    def _format_simple_list(self, entries: list) -> str:
        values = [str(entry) for entry in entries if str(entry).strip()]
        return "\n".join(f"- {value}" for value in values) if values else "Add details from candidate intake."

    def _normalize_list(self, items: Iterable) -> list[str]:
        return [str(item).strip().lower() for item in items if str(item).strip()]

    def _join_present(self, items: Iterable[Optional[str]]) -> str:
        return " | ".join(str(item) for item in items if item)
