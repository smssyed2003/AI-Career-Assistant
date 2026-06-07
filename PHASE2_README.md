# AI Career Agent — Phase 2 Handoff

This document summarizes Phase 2 implementation for the AI Career Agent project. It is designed as a handoff guide for the next model or engineer.

## Phase 2 Completed Work

### 1. Gemini-based LLM extraction
- Added Gemini support to the backend via `google-generativeai`.
- Updated configuration to use:
  - `GEMINI_API_KEY`
  - `GEMINI_MODEL` with default `gemma-4-26b`
- The LLM extraction service now prefers Gemini when `GEMINI_API_KEY` is present.
- OpenAI remains available as a fallback via `OPENAI_API_KEY` and `OPENAI_MODEL`.

### 2. Resume ingestion endpoint
- Added `POST /api/ingest/resume` to upload PDF or DOCX resumes.
- Implemented file-type validation and text extraction.
- Converted extracted resume text into structured profile JSON.

### 3. Gmail attachment ingestion
- Added `POST /api/ingest/gmail/sync` to fetch attachments from Gmail.
- Implemented Gmail OAuth refresh flow using:
  - `GMAIL_CLIENT_ID`
  - `GMAIL_CLIENT_SECRET`
  - `GMAIL_REFRESH_TOKEN`
- The service retrieves attachments and extracts resume text from supported formats.

### 4. Resume parser service
- Added `backend/app/services/parse_service.py`.
- Supports PDF extraction via `pdfplumber`.
- Supports DOCX parsing via `python-docx`.

### 5. Profile schema support
- Added `backend/app/schemas/profile.py`.
- Defines structured candidate profile fields, including:
  - education
  - experience
  - projects
  - skills
  - certifications
  - links
  - preferences
- Added `ResumeParseResult` for ingestion responses.

### 6. Updated environment config
- Added new config values in `backend/app/core/config.py`:
  - `gemini_api_key`
  - `gemini_model`
- Preserved existing OpenAI config values.

### 7. Dependency updates
- Added `google-generativeai` to backend requirements.
- Kept `openai` for fallback extraction.

### 8. Phase 2 tests
- Added tests for resume parsing and ingestion routes.
- Verified parser and ingestion tests pass.

## Important Files Added/Updated

- `backend/app/services/llm_service.py`
- `backend/app/services/parse_service.py`
- `backend/app/services/gmail_service.py`
- `backend/app/api/routers/ingestion.py`
- `backend/app/schemas/profile.py`
- `backend/app/core/config.py`
- `backend/.env.example`
- `backend/requirements.txt`
- `backend/app/tests/test_parse_service.py`
- `backend/app/tests/test_ingestion_router.py`

## Required Environment Variables for Phase 2

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (default `gemma-4-26b`)
- `OPENAI_API_KEY` (optional fallback)
- `OPENAI_MODEL` (optional fallback)
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN`
- `CHROMA_SERVER_URL`
- `N8N_WEBHOOK_URL`

## How to run Phase 2 locally

1. Create `backend/.env` from `backend/.env.example`.
2. Install backend dependencies:
   ```powershell
   cd backend
   python -m pip install -r requirements.txt
   ```
3. Start the backend:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Test the resume ingestion endpoint:
   - `POST http://localhost:8000/api/ingest/resume`
5. Use `POST http://localhost:8000/api/ingest/gmail/sync` to sync Gmail attachments once credentials are configured.

## Notes for the next phase

- This phase focuses on ingestion and profile extraction.
- Next step: build job discovery, job description parsing, matching, skill gap analysis, and interview readiness scoring.
- A Gemini API key is now the preferred path for LLM extraction.

> Update: Phase 3 has added job ingestion, candidate-job matching, skill gap analysis, and a dedicated `/match` UI route.
