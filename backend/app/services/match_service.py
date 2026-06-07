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

    def analyze_skill_gap(self, db: Session, candidate_id: int, job_id: int) -> SkillGapAnalysis:
        candidate = self.candidate_service.get(db, candidate_id)
        job = self.job_service.get(db, job_id)
        if not candidate or not job:
            raise ValueError("Candidate or job not found")

        match = self._score_candidate_job(candidate, job)
        if not match:
            raise ValueError("Unable to score candidate against job")

        required_skills = self._normalize_list(job.structured_data.get("skills", []))
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
        required_skills = self._normalize_list(job.structured_data.get("skills", []))
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
        job_skills = set(self._normalize_list(job.structured_data.get("skills", [])))

        if not job_skills:
            job_skills = set(self._extract_skills_from_text(job.raw_text or job.description or ""))

        matched_skills = sorted(candidate_skills.intersection(job_skills))
        missing_skills = sorted(job_skills - candidate_skills)
        skill_match_score = float(len(matched_skills) / len(job_skills)) if job_skills else 0.0

        location_score = self._score_location(candidate, job)
        score = round(skill_match_score * 0.7 + location_score * 0.3, 3)

        return JobMatch(
            job_id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            score=score,
            skill_match_score=skill_match_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience_level=job.structured_data.get("experience_level"),
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
