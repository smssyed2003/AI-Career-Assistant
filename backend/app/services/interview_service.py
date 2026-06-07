from sqlalchemy.orm import Session

from app.models.interview_prep import InterviewPrep, InterviewQuestionTypeEnum
from app.services.candidate_service import CandidateService
from app.services.job_service import JobService
from app.services.match_service import MatchService


class InterviewService:
    def __init__(self):
        self.candidates = CandidateService()
        self.jobs = JobService()
        self.matcher = MatchService()

    def list_for_job(self, db: Session, candidate_id: int, job_id: int, user_id: int | None = None):
        query = db.query(InterviewPrep).filter(InterviewPrep.candidate_id == candidate_id, InterviewPrep.job_id == job_id)
        if user_id is not None:
            query = query.filter(InterviewPrep.user_id == user_id)
        return (
            query
            .order_by(InterviewPrep.question_type, InterviewPrep.id)
            .all()
        )

    def generate(self, db: Session, candidate_id: int, job_id: int, application_package_id: int | None = None, user_id: int | None = None):
        candidate = self.candidates.get_for_user(db, candidate_id, user_id) if user_id is not None else self.candidates.get(db, candidate_id)
        job = self.jobs.get_for_user(db, job_id, user_id) if user_id is not None else self.jobs.get(db, job_id)
        if not candidate or not job:
            raise ValueError("Candidate or job not found")

        existing = self.list_for_job(db, candidate_id, job_id, user_id=user_id)
        if existing:
            return existing

        match = self.matcher.score_candidate_job(candidate, job)
        skills = match.matched_skills or [str(skill).lower() for skill in (candidate.skills or [])[:5]]
        missing = match.missing_skills[:5]
        company = job.company or "the company"

        questions = [
            (InterviewQuestionTypeEnum.HR, f"Tell me about yourself and why you are interested in {job.title} at {company}.", skills, "easy"),
            (InterviewQuestionTypeEnum.BEHAVIORAL, "Describe a time you handled ambiguity or learned a new skill quickly.", skills, "medium"),
            (InterviewQuestionTypeEnum.TECHNICAL, f"How would you explain your experience with {self._join(skills)} for this role?", skills, "medium"),
            (InterviewQuestionTypeEnum.CODING, "Solve a practical coding problem involving data transformation, edge cases, and clean API-ready output.", ["problem solving", "edge cases", "complexity"], "medium"),
            (InterviewQuestionTypeEnum.AI, "How would you evaluate whether an AI feature is reliable enough for users?", ["evaluation", "metrics", "failure modes"], "medium"),
            (InterviewQuestionTypeEnum.LLM, "How would you design prompts and validation for structured LLM output?", ["json", "validation", "fallbacks"], "medium"),
            (InterviewQuestionTypeEnum.RAG, "How would you build a RAG pipeline for candidate-job matching?", ["retrieval", "embeddings", "reranking"], "hard"),
            (InterviewQuestionTypeEnum.SYSTEM_DESIGN, "Design the AI Career Agent pipeline from email intake to daily candidate report.", ["queues", "database", "rate limiting", "observability"], "hard"),
        ]

        if missing:
            questions.append(
                (
                    InterviewQuestionTypeEnum.TECHNICAL,
                    f"The JD mentions {self._join(missing)}. How would you close this gap before joining?",
                    missing,
                    "medium",
                )
            )

        created = []
        for question_type, question_text, highlights, difficulty in questions:
            prep = InterviewPrep(
                candidate_id=candidate_id,
                user_id=user_id,
                job_id=job_id,
                application_package_id=application_package_id,
                question_type=question_type,
                question_text=question_text,
                suggested_answer=self._suggested_answer(candidate.full_name, job.title, highlights),
                keyword_highlights=highlights,
                difficulty_level=difficulty,
            )
            db.add(prep)
            created.append(prep)

        db.commit()
        for prep in created:
            db.refresh(prep)
        return created

    def _suggested_answer(self, name: str, title: str, highlights: list[str]) -> str:
        return (
            f"Frame the answer around {name}'s relevant projects, measurable impact, and direct fit for {title}. "
            f"Mention: {self._join(highlights)}."
        )

    def _join(self, values: list[str]) -> str:
        return ", ".join(values) if values else "the role requirements"
