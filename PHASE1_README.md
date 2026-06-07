# AI Career Agent — Phase 1 Handoff

This document summarizes Phase 1 implementation work for the AI Career Agent project. It is designed as a handoff guide for another model or engineer to continue with deployment, configuration, and next-phase feature development.

## What has been completed in Phase 1

### 1. Project scaffolding
- Created a clean, modular repository structure with separate backend and frontend directories.
- Added core folders for backend components: `api`, `core`, `db`, `models`, `schemas`, `services`, and `tests`.
- Created frontend scaffold using React + Vite + TypeScript.
- Defined Docker support for backend, frontend, PostgreSQL, and n8n.

### 2. Backend foundation
- Implemented `backend/app/main.py` as the FastAPI app entrypoint.
- Configured CORS and API router registration.
- Added `/api/health` health check endpoint.

### 3. Configuration management
- Created `backend/app/core/config.py` using `pydantic-settings` for typed environment configuration.
- Supported fallback to SQLite for development via `DATABASE_URL`.
- Added config keys for:
  - `DEBUG`
  - `API_PREFIX`
  - `ALLOWED_ORIGINS`
  - `DATABASE_URL`
  - `GMAIL_CLIENT_ID`
  - `GMAIL_CLIENT_SECRET`
  - `GMAIL_REFRESH_TOKEN`
  - `CHROMA_SERVER_URL`
  - `N8N_WEBHOOK_URL`
  - `SENTRY_DSN`

### 4. Database and persistence layer
- Added SQLAlchemy `Base` declarative base.
- Configured SQLAlchemy session with SQLite compatibility for dev.
- Added candidate and job description ORM models.
- Designed candidate model to store:
  - `full_name`
  - `email`
  - `phone`
  - `summary`
  - `education`
  - `experience`
  - `projects`
  - `skills`
  - `certifications`
  - `links`
  - `preferences`
  - `metadata` (stored as JSON)
- Added job description model to store parsed JDs and structured data.

### 5. API and service layer
- Implemented candidate API routes in `backend/app/api/routers/candidates.py`:
  - `POST /api/candidates` to create candidate profiles
  - `GET /api/candidates` to list candidates
  - `GET /api/candidates/{candidate_id}` to retrieve a candidate
- Implemented job routes in `backend/app/api/routers/jobs.py`:
  - `GET /api/jobs` to list jobs
- Added service classes for candidate and job operations.
- Included base router wiring in `backend/app/api/__init__.py`.

### 6. Data schemas and validation
- Added Pydantic schemas for candidate and job payloads.
- Candidate schema types include:
  - education entries
  - experience entries
  - project entries
  - preferences
  - strong email validation
- Added `from_attributes=True` model config for ORMs.

### 7. Frontend starter application
- Created `frontend` React + Vite app.
- Implemented a simple dashboard shell displaying backend health status.
- Configured Vite to proxy `/api` requests to the backend.
- Added basic styling for the starter page.

### 8. Docker and local orchestration
- Added `docker-compose.yml` with services:
  - `postgres`
  - `backend`
  - `frontend`
  - `n8n`
- Added Dockerfiles for backend and frontend.
- Included local volumes for data persistence.

### 9. Testing
- Added backend tests for:
  - health endpoint
  - candidate service create/retrieve flow
- Confirmed initial backend tests pass.

## Current repository structure

```
AI Career Agent
├── backend
│   ├── app
│   │   ├── api
│   │   │   ├── routers
│   │   │   │   ├── health.py
│   │   │   │   ├── candidates.py
│   │   │   │   └── jobs.py
│   │   ├── core
│   │   │   └── config.py
│   │   ├── db
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models
│   │   │   ├── candidate.py
│   │   │   └── job_description.py
│   │   ├── schemas
│   │   │   ├── candidate.py
│   │   │   └── job.py
│   │   ├── services
│   │   │   ├── candidate_service.py
│   │   │   └── job_service.py
│   │   └── tests
│   │       ├── test_health.py
│   │       └── test_candidate_service.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend
│   ├── src
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── style.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Environment variables to configure

The next phase should set up these environment values in `backend/.env` or the deployment environment:

- `DEBUG` — `True` or `False`
- `DATABASE_URL` — e.g. `sqlite:///./data/dev.db` for development or `postgresql://<user>:<pass>@<host>:5432/<db>` for production
- `ALLOWED_ORIGINS` — comma-separated frontend origins
- `GMAIL_CLIENT_ID` — Gmail OAuth client ID for resume intake
- `GMAIL_CLIENT_SECRET` — Gmail OAuth client secret
- `GMAIL_REFRESH_TOKEN` — Gmail refresh token
- `CHROMA_SERVER_URL` — ChromaDB vector store endpoint URL
- `N8N_WEBHOOK_URL` — n8n webhook URL for orchestration events
- `SENTRY_DSN` — Sentry DSN for runtime error monitoring

## Setup instructions for another agent

1. Create or update `backend/.env` from `backend/.env.example`.
2. Ensure the database is available and `DATABASE_URL` is configured.
   - For local dev, the default SQLite path uses `backend/data/dev.db`.
   - For production, use PostgreSQL credentials and set `DATABASE_URL` accordingly.
3. Obtain and configure Gmail OAuth values:
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
   - `GMAIL_REFRESH_TOKEN`
4. Configure Chroma and n8n endpoints.
5. Install backend dependencies:
   ```powershell
   cd backend
   python -m pip install -r requirements.txt
   ```
6. Run the backend:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
7. Install frontend dependencies:
   ```powershell
   cd frontend
   npm install
   npm run dev -- --host
   ```
8. Validate the health endpoint at `http://localhost:8000/api/health`.

## Phase 1 limitations and next actions

This phase is intentionally foundational. The next phase should implement:

- Gmail resume intake and inbox polling
- PDF and DOCX resume parsing
- LLM-based profile extraction into structured JSON
- Candidate master record enrichment and normalization
- Resume generation engine for ATS-optimized output
- Job discovery connectors and JD parsing
- Matching engine and score aggregation
- Skill gap analysis and interview readiness scoring
- Dashboard UI pages for candidate analytics and match insights
- ChromaDB vector storage integration
- n8n workflows for orchestration and event automation

## Notes for the next agent

- The backend is ready for feature expansion; no job matching or parsing logic exists yet.
- The frontend is a starter shell and can immediately show backend health.
- Environment variables for Gmail, Chroma, n8n, and Sentry are declared but not yet used by application logic.

> Update: Phase 3 work has since added candidate-job matching backend support and a dedicated `/match` frontend route for job matching workflows.
- Database models are designed to accept JSON-rich candidate and job data.

---

If you want, I can also generate a second, action-oriented document that maps each next-phase feature into specific implementation tasks and files. 