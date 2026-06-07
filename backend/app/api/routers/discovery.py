from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.discovery import DiscoveryIngestRequest, DiscoveryIngestResult, JobSourceRead
from app.services.discovery_service import DiscoveryService
from app.services.llm_queue_service import llm_rate_limiter

router = APIRouter()
service = DiscoveryService()


@router.post("/job-discovery/ingest", response_model=DiscoveryIngestResult, summary="Ingest jobs from a safe source")
def ingest_discovered_jobs(request: DiscoveryIngestRequest, db: Session = Depends(get_db)):
    return service.ingest(db, request)


@router.get("/job-discovery/sources", response_model=List[JobSourceRead], summary="List job discovery source records")
def list_job_sources(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return service.list_sources(db, skip=skip, limit=limit)


@router.get("/llm/queue/status", summary="Get LLM rate-limit queue status")
def llm_queue_status():
    return llm_rate_limiter.status()
