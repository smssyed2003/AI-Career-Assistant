# AI Career Agent - Phase 10 Handoff

This document summarizes Phase 10: career coach reports.

## Phase 10 Completed Work

### 1. Career report generation
- Added candidate-level career coach reports.
- Reports include:
  - interview rate
  - ATS average
  - new skills
  - trending jobs
  - resume suggestions
  - certification suggestions
  - salary growth guidance
  - career roadmap

### 2. Persistence
- Reports are stored in `career_reports`.
- Historical reports can be listed per candidate.

### 3. Frontend support
- Added Career Coach section in `/match`.
- Users can generate a weekly-style report for the selected candidate.

### 4. Free-first design
- Reports are computed from existing candidate, job, and application data.
- No paid analytics, external APIs, or background infrastructure are required for the MVP.

## Important Files Added/Updated

- `backend/app/models/career_report.py`
- `backend/app/schemas/career.py`
- `backend/app/services/career_service.py`
- `backend/app/api/routers/career.py`
- `frontend/src/pages/MatchPage.tsx`

## API Endpoints

- `POST /api/candidates/{candidate_id}/career-reports/generate`
- `GET /api/candidates/{candidate_id}/career-reports`

## Next Step

n8n can later call the report generation endpoint on a weekly schedule and email the result to the candidate.
