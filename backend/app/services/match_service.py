import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.schemas.job import JobMatch, ReadinessAnalysis, SkillGapAnalysis
from app.services.candidate_service import CandidateService
from app.services.job_service import JobService


class MatchService:
    def __init__(self):
        self.candidate_service = CandidateService()
        self.job_service = JobService()

    def match_candidate(self, db: Session, candidate_id: int, top_k: int = 10) -> List[JobMatch]:
        candidate = self.candidate_service.get(db, candidate_id)
        if not candidate:
            return []

        jobs = self.job_service.list(db, skip=0, limit=100)
        matches = [self._score_candidate_job(candidate, job) for job in jobs]
        matches = [match for match in matches if match is not None]
        matches.sort(key=lambda item: item.score, reverse=True)
        return matches[:top_k]

    def score_candidate_job(self, candidate: Candidate, job: JobDescription) -> JobMatch:
        return self._score_candidate_job(candidate, job)

    def analyze_skill_gap(self, db: Session, candidate_id: int, job_id: int) -> SkillGapAnalysis:
        candidate = self.candidate_service.get(db, candidate_id)
        job = self.job_service.get(db, job_id)
        if not candidate or not job:
            raise ValueError("Candidate or job not found")

        match = self._score_candidate_job(candidate, job)
        if not match:
            raise ValueError("Unable to score candidate against job")

        structured = job.structured_data or {}
        required_skills = self._normalize_list(structured.get("skills", []))
        candidate_skills = self._normalize_list(candidate.skills or [])
        missing_skills = sorted(set(required_skills) - set(candidate_skills))
        extra_skills = sorted(set(candidate_skills) - set(required_skills))

        return SkillGapAnalysis(
            job_id=job.id,
            candidate_id=candidate.id,
            title=job.title,
            company=job.company,
            required_skills=required_skills,
            candidate_skills=candidate_skills,
            missing_skills=missing_skills,
            extra_candidate_skills=extra_skills,
            score=match.score,
        )

    def analyze_interview_readiness(self, db: Session, candidate_id: int, job_id: int) -> ReadinessAnalysis:
        candidate = self.candidate_service.get(db, candidate_id)
        job = self.job_service.get(db, job_id)
        if not candidate or not job:
            raise ValueError("Candidate or job not found")

        match = self._score_candidate_job(candidate, job)
        structured = job.structured_data or {}
        required_skills = self._normalize_list(structured.get("skills", []))
        if not required_skills:
            required_skills = self._normalize_list(self._extract_skills_from_text(job.raw_text or job.description or ""))

        candidate_skills = self._normalize_list(candidate.skills or [])
        missing_skills = sorted(set(required_skills) - set(candidate_skills))
        strengths = sorted(set(candidate_skills).intersection(required_skills))
        readiness_score = round(min(1.0, match.score + max(0.0, len(strengths) / max(len(required_skills), 1)) * 0.2), 3)

        if readiness_score >= 0.8:
            summary = "Strong match: the candidate appears well-prepared for this role."
        elif readiness_score >= 0.5:
            summary = "Moderate match: the candidate has key skills but can improve in a few areas."
        else:
            summary = "Low readiness: the candidate should strengthen the missing skills before applying."

        recommended_learning = [skill.title() for skill in missing_skills][:5]

        return ReadinessAnalysis(
            job_id=job.id,
            candidate_id=candidate.id,
            readiness_score=readiness_score,
            summary=summary,
            top_strengths=strengths,
            improvement_areas=missing_skills,
            recommended_learning=recommended_learning,
            matched_skills=match.matched_skills,
            missing_skills=missing_skills,
        )

    def _score_candidate_job(self, candidate: Candidate, job: JobDescription) -> JobMatch:
        candidate_skills = set(self._normalize_list(candidate.skills or []))
        structured = job.structured_data or {}
        job_skills = set(self._normalize_list(structured.get("skills", [])))

        if not job_skills:
            job_skills = set(self._extract_skills_from_text(job.raw_text or job.description or ""))

        matched_skills = sorted(candidate_skills.intersection(job_skills))
        missing_skills = sorted(job_skills - candidate_skills)
        skill_match_score = float(len(matched_skills) / len(job_skills)) if job_skills else 0.0

        location_score = self._score_location(candidate, job)
        experience_score = self._score_experience(candidate, job)
        project_score = self._score_projects(candidate, job)
        salary_score = self._score_salary(candidate, job)
        education_score = self._score_education(candidate, job)
        keyword_score = self._score_keywords(candidate, job)
        score = round(
            skill_match_score * 0.42
            + keyword_score * 0.18
            + project_score * 0.12
            + experience_score * 0.12
            + location_score * 0.08
            + education_score * 0.05
            + salary_score * 0.03,
            3,
        )

        return JobMatch(
            job_id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            score=score,
            skill_match_score=skill_match_score,
            experience_match_score=experience_score,
            project_match_score=project_score,
            location_match_score=location_score,
            salary_match_score=salary_score,
            education_match_score=education_score,
            keyword_match_score=keyword_score,
            overall_label=self._label_score(score),
            interview_probability=self._probability_label(score),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_level=structured.get("experience_level"),
        )

    def _score_location(self, candidate: Candidate, job: JobDescription) -> float:
        location = (job.location or "").lower()
        prefs = candidate.preferences or {}
        candidate_locations = [loc.lower() for loc in (prefs.get("locations") or []) if isinstance(loc, str)]
        if not location or not candidate_locations:
            return 0.5
        for loc in candidate_locations:
            if loc in location or location in loc:
                return 1.0
        return 0.6

    def _score_experience(self, candidate: Candidate, job: JobDescription) -> float:
        candidate_text = self._flatten(candidate.experience or [])
        job_text = self._job_text(job)
        signals = ["intern", "junior", "mid", "senior", "lead", "backend", "data", "ai", "ml", "years"]
        matched = [signal for signal in signals if signal in candidate_text and signal in job_text]
        if matched:
            return min(1.0, 0.5 + len(matched) * 0.1)
        return 0.5 if candidate.experience else 0.25

    def _score_projects(self, candidate: Candidate, job: JobDescription) -> float:
        project_text = self._flatten(candidate.projects or [])
        if not project_text:
            return 0.2
        job_skills = self._normalize_list((job.structured_data or {}).get("skills", []))
        if not job_skills:
            return 0.5
        matched = [skill for skill in job_skills if skill in project_text]
        return min(1.0, len(matched) / max(len(job_skills), 1) + 0.25)

    def _score_salary(self, candidate: Candidate, job: JobDescription) -> float:
        candidate_salary = str((candidate.preferences or {}).get("salary_expectation") or "").lower()
        job_salary = str((job.structured_data or {}).get("salary") or "").lower()
        if not candidate_salary or not job_salary:
            return 0.5
        return 1.0 if candidate_salary in job_salary or job_salary in candidate_salary else 0.4

    def _score_education(self, candidate: Candidate, job: JobDescription) -> float:
        education_text = self._flatten(candidate.education or [])
        required = self._normalize_list((job.structured_data or {}).get("education", []))
        if not required:
            return 0.6 if candidate.education else 0.4
        matched = [item for item in required if item in education_text]
        return len(matched) / max(len(required), 1)

    def _score_keywords(self, candidate: Candidate, job: JobDescription) -> float:
        candidate_text = self._flatten(
            [
                candidate.summary or "",
                candidate.skills or [],
                candidate.projects or [],
                candidate.experience or [],
            ]
        )
        structured = job.structured_data or {}
        keywords = self._normalize_list(structured.get("ats_keywords", []))
        if not keywords:
            keywords = self._normalize_list(structured.get("skills", []))
        if not keywords:
            return 0.4
        matched = [keyword for keyword in keywords if keyword in candidate_text]
        return len(matched) / max(len(keywords), 1)

    def _extract_skills_from_text(self, text: str) -> List[str]:
        normalized = re.sub(r"[^A-Za-z0-9,\s+#+-]", " ", text)
        tokens = re.split(r"[\s,;]+", normalized)
        keywords = [t.strip() for t in tokens if len(t.strip()) > 1]
        common = [w for w in keywords if w.lower() in {
            "python", "sql", "java", "react", "node", "docker", "aws", "azure", "gcp", "linux", "html", "css", "typescript", "javascript",
            "kubernetes", "django", "flask", "fastapi", "spring", "graphql", "rest", "api", "aws", "azure"
        }]
        return sorted(set([w.lower() for w in common]))

    def _normalize_list(self, items: Any) -> List[str]:
        if not items:
            return []
        normalized = []
        for item in items:
            if isinstance(item, str):
                normalized.append(item.strip().lower())
            elif isinstance(item, dict):
                normalized.append(str(item).strip().lower())
        return [item for item in normalized if item]

    def _flatten(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(f"{key} {self._flatten(item)}" for key, item in value.items()).lower()
        if isinstance(value, list):
            return " ".join(self._flatten(item) for item in value).lower()
        return str(value).lower()

    def _job_text(self, job: JobDescription) -> str:
        return self._flatten([job.title, job.description, job.raw_text, job.structured_data])

    def _label_score(self, score: float) -> str:
        if score >= 0.85:
            return "Excellent Match"
        if score >= 0.7:
            return "Strong Match"
        if score >= 0.5:
            return "Moderate Match"
        return "Needs Review"

    def _probability_label(self, score: float) -> str:
        if score >= 0.85:
            return "Very High"
        if score >= 0.7:
            return "High"
        if score >= 0.5:
            return "Medium"
        return "Low"
