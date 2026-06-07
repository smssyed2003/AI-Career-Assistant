# AI Career Agent

A modular AI-powered career acceleration platform built with FastAPI, React, PostgreSQL, ChromaDB, and n8n.

## Architecture

- `backend/` - FastAPI backend with candidate ingestion, resume parsing, profile extraction, matching, and recommendation APIs.
- `frontend/` - React + Vite dashboard for profile analytics, match insights, and readiness tracking.
- `docker-compose.yml` - local orchestration with PostgreSQL, backend, frontend, n8n, and ChromaDB.

## Phase 2: Ingestion and Parsing

The backend now includes:
- `/api/ingest/resume` POST endpoint for uploading PDF or DOCX resumes
- `/api/ingest/gmail/sync` POST endpoint skeleton to pull attachments from Gmail
- Resume parser service for PDF and DOCX extraction
- LLM profile extraction service with OpenAI fallback parsing
- Phase 3 now builds on this with job ingestion, matching, skill gap analysis, and a dedicated `/match` frontend route
- Phase 4 adds interview readiness scoring, top strengths, improvement areas, and recommended learning guidance
- Phase 5 adds saved candidate/job history, profile selection, and stronger frontend validation feedback
- Candidate dashboard, manual application tracker, admin analytics, and admin-managed prompts/integration settings are included.
- Candidate profile editing, database-backed resume upload history, resume library previews, tracker filters/details, and admin audit logs are included.

## Getting Started

1. Copy `.env.example` to `backend/.env` and configure values.
   Set a strong `AUTH_SECRET_KEY` before sharing the app with other users.
   The first registered account becomes `admin`; later accounts become normal `user` accounts.
2. Install backend dependencies:
   ```powershell
   cd backend
   python -m pip install -r requirements.txt
   ```
3. Run the backend:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   From the project root, you can also run:
   ```powershell
   .\run-backend.ps1
   ```
4. Start the frontend:
   ```powershell
   cd frontend
   npm install
   npm run dev -- --host
   ```
   From the project root, you can also run:
   ```powershell
   .\run-frontend.ps1
   ```

## Project Scope

This repo will incrementally implement:
- User signup/login and per-user data isolation
- Admin-only user management with role and status controls
- Candidate dashboard with profile completion, workflow counters, application pipeline counts, and next actions
- Candidate profile editing for summary, skills, certifications, and links
- Resume upload history stored as parsed database records for the free deployment path
- Resume library page for generated versions and uploaded resume previews
- Manual application tracker with prepared, submitted, review, interview, rejected, accepted, and archived statuses
- Application tracker filters and package detail preview
- Admin analytics for users, profiles, jobs, resumes, applications, LLM queue status, and safe manual application mode
- Admin-managed prompts and integration settings for n8n, AI prompts, and operational configuration
- Admin audit logs for role, status, and setting changes
- Gmail resume ingestion and parsing
- LLM profile extraction into structured JSON
- Candidate master database and resume generation
- Job discovery connectors and matching engine
- Skill gap analysis and interview readiness scoring
- Saved candidate/job history and profile selection workflows
- Dashboard for completeness, ATS score, match stats, and learning recommendations

## Manual Testing

Use `MANUAL_TESTING.md` as the product checklist before deployment or after larger feature groups. It covers authentication, role restrictions, candidate dashboard, resume generation, matching, application tracking, interview prep, career coaching, admin settings, and multi-user isolation.

Use `DEPLOYMENT_CHECKLIST.md` before deploying the free MVP on Vercel and Render.
