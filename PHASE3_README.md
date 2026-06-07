# AI Career Agent - Phase 3 Handoff

This document summarizes the updated Phase 3 implementation for free-first, safe job discovery and JD handling.

## Phase 3 Completed Work

### 1. Job ingestion and parsing
- Added backend support for ingesting raw job description text via `POST /api/jobs/ingest`.
- Supported file upload or raw text input for JD ingestion.
- Implemented structured JD extraction into `JobDescription` data.
- Jobs are stored permanently in the database.

### 2. Free-first job discovery
- Added safe source-aware job discovery through `POST /api/job-discovery/ingest`.
- Supported source categories:
  - manual
  - company careers
  - startup careers
  - AI company careers
  - RemoteOK
  - Wellfound
  - government jobs
  - internship portals
- Stored discovery source records in `job_sources`.
- Added `GET /api/job-discovery/sources` to review discovery history.

### 3. Duplicate handling
- Added duplicate detection before storing discovered jobs.
- Duplicate jobs are skipped but still recorded as source events.
- This keeps the job database cleaner without needing paid APIs.

### 4. Matching engine
- Built candidate-to-job matching through `backend/app/services/match_service.py`.
- Added `GET /api/jobs/match/{candidate_id}` for ranked job matches.
- Matching now includes:
  - skill match
  - experience match
  - project match
  - location match
  - salary match
  - education match
  - keyword match
  - overall match label
  - interview probability label

### 5. Skill gap and readiness
- Added `GET /api/jobs/{job_id}/skill-gap/{candidate_id}`.
- Added `GET /api/jobs/{job_id}/readiness/{candidate_id}`.
- These support missing skills, strengths, learning recommendations, and interview readiness scoring.

### 6. Frontend support
- Extended the React `/match` workspace with a Discovery section.
- Users can paste a job, choose a safe source, add source URL, and save it with dedupe/source tracking.
- LLM queue status is shown in the workspace.

## Important Files Added/Updated

- `backend/app/models/job_source.py`
- `backend/app/schemas/discovery.py`
- `backend/app/services/discovery_service.py`
- `backend/app/services/job_service.py`
- `backend/app/api/routers/discovery.py`
- `backend/app/services/match_service.py`
- `backend/app/api/routers/jobs.py`
- `frontend/src/pages/MatchPage.tsx`
- `frontend/src/style.css`
- `PHASE3_README.md`

## API Endpoints

- `POST /api/jobs/ingest`
- `GET /api/jobs`
- `GET /api/jobs/{job_id}`
- `POST /api/job-discovery/ingest`
- `GET /api/job-discovery/sources`
- `GET /api/jobs/match/{candidate_id}`
- `GET /api/jobs/{job_id}/skill-gap/{candidate_id}`
- `GET /api/jobs/{job_id}/readiness/{candidate_id}`
- `GET /api/llm/queue/status`

## Free-First Constraint

Phase 3 intentionally avoids bot-based scraping and automated submissions on platforms like LinkedIn, Naukri, and Indeed. The MVP uses manual/public-source/company-career ingestion first, which is safer, cheaper, and easier to deploy on Render + Vercel.
