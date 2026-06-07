# AI Career Agent - Phase 6 Handoff

This document summarizes Phase 6: job-specific resume optimization.

## Phase 6 Completed Work

### 1. Job-specific resume generation
- Added application-package flow that creates an optimized ATS resume for a selected candidate and job.
- Each optimized resume is stored as a new `Resume` row.
- Previous resume versions are never overwritten.

### 2. Resume scoring
- Added ATS score estimation for generated resumes.
- Job-specific resumes use extracted JD skills and keywords where available.

### 3. Resume version persistence
- Added resume listing and generation endpoints.
- Standard resume versions remain separate from job-specific optimized resumes.

## Important Files Added/Updated

- `backend/app/models/resume.py`
- `backend/app/schemas/resume.py`
- `backend/app/services/resume_service.py`
- `backend/app/api/routers/resumes.py`
- `backend/app/services/application_service.py`
- `frontend/src/pages/MatchPage.tsx`

## API Endpoints

- `GET /api/candidates/{candidate_id}/resumes`
- `POST /api/candidates/{candidate_id}/resumes/generate`
- `GET /api/resumes/{resume_id}`
- `POST /api/jobs/{job_id}/application-package/{candidate_id}`

## Notes

This phase prepares review-ready optimized resumes. It does not auto-submit applications to job platforms.
