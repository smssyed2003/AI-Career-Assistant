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

## Getting Started

1. Copy `.env.example` to `backend/.env` and configure values.
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
- Gmail resume ingestion and parsing
- LLM profile extraction into structured JSON
- Candidate master database and resume generation
- Job discovery connectors and matching engine
- Skill gap analysis and interview readiness scoring
- Saved candidate/job history and profile selection workflows
- Dashboard for completeness, ATS score, match stats, and learning recommendations
