from sqlalchemy.orm import Session

from app.models.job_source import JobSource, JobSourceEnum
from app.schemas.discovery import DiscoveryIngestRequest
from app.schemas.job import JobDescriptionCreate
from app.services.job_service import JobService
from app.services.llm_service import JobDescriptionExtractor


class DiscoveryService:
    def __init__(self):
        self.jobs = JobService()
        self.extractor = JobDescriptionExtractor()

    def ingest(self, db: Session, request: DiscoveryIngestRequest):
        created_jobs = []
        duplicate_job_ids = []

        for text in request.job_texts:
            duplicate = self.jobs.find_duplicate(db, text)
            if duplicate:
                duplicate_job_ids.append(duplicate.id)
                self._record_source(db, duplicate.id, request, is_duplicate=True)
                continue

            parsed = self.extractor.extract_job(text)
            job = self.jobs.create(db, JobDescriptionCreate(**parsed))
            self._record_source(db, job.id, request, is_duplicate=False)
            created_jobs.append(job)

        return {
            "source": request.source,
            "created_count": len(created_jobs),
            "duplicate_count": len(duplicate_job_ids),
            "jobs": created_jobs,
            "duplicate_job_ids": duplicate_job_ids,
        }

    def list_sources(self, db: Session, skip: int = 0, limit: int = 50):
        return db.query(JobSource).order_by(JobSource.created_at.desc()).offset(skip).limit(limit).all()

    def _record_source(self, db: Session, job_id: int, request: DiscoveryIngestRequest, is_duplicate: bool):
        source = JobSource(
            job_description_id=job_id,
            source=JobSourceEnum(request.source.value),
            source_url=request.source_url,
            is_duplicate=is_duplicate,
            is_active=True,
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source
