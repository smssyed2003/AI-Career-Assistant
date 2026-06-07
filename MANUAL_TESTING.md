# Manual Testing Guide

Use this checklist after a feature group is finished or before deployment.

## 1. Start The App

Backend:

```powershell
.\run-backend.ps1
```

Frontend:

```powershell
.\run-frontend.ps1
```

Open the Vite URL, usually `http://localhost:5173`.

## 2. Authentication And Roles

1. Sign up with your owner email.
2. Confirm you can see the `Admin` navigation item.
3. Log out.
4. Sign up with another email.
5. Confirm the second user cannot see `Admin`.
6. Log back in as admin.
7. Open `Admin`.
8. Change the second user role from `User` to `Admin`, then back to `User`.
9. Deactivate and reactivate the second user.

Expected result: only admin users can access admin controls.

## 3. Candidate Dashboard

1. Login as a normal candidate user.
2. Open `Dashboard`.
3. Confirm profile, resume, job, application, high-match, and interview-prep counters appear.
4. Confirm `Next Actions` shows useful steps when data is missing.

Expected result: dashboard loads without exposing another user's data.

## 4. Candidate Profile And Resume Versions

1. Open `Job Matching`.
2. Create a candidate profile with name, email, summary, and comma-separated skills.
3. Open `Profile`.
4. Edit summary, skills, certifications, or links.
5. Save and confirm the edited profile remains after refresh.
6. Open `Job Matching` again and click `Generate Resume Versions`.
7. Confirm multiple versions appear, such as master, ATS, AI, ML, Python, Backend, and Data Scientist.

Expected result: generated versions are stored and previous versions are not overwritten.

## 4A. Resume Upload History

1. Open `Resumes`.
2. Select a candidate.
3. Upload a `.pdf`, `.docx`, or `.txt` resume.
4. Confirm it appears under `Upload History`.
5. Click the upload row and confirm extracted text appears in preview.

Expected result: resume upload history is stored in the database, not on the backend filesystem.

## 5. Job Ingestion And Matching

1. Paste a real job description into `Job Description`.
2. Click `Ingest Job`.
3. Open `Matches` and click `Refresh matches`.
4. Run `Skill Gap Analysis`.
5. Run `Interview Readiness`.

Expected result: the job is parsed, scored, and searchable for the logged-in user only.

## 6. Application Package And Tracker

1. In `Application Package`, click `Prepare Package`.
2. Confirm cover letter, HR intro, email template, screening answers, match score, ATS score, and interview probability appear.
3. Open `Applications`.
4. Filter by status.
5. Click `View Details` and confirm generated materials appear.
6. Change status from `prepared` to `submitted`.
7. Add private notes and click `Save Notes`.
8. Move the status to `under_review`, `interview_scheduled`, `rejected`, `accepted`, or `archived`.

Expected result: tracking is manual and no job-site auto-apply action happens.

## 7. Interview Prep And Career Coach

1. Return to `Job Matching`.
2. Click `Generate Questions`.
3. Confirm HR, technical, coding, AI, LLM, RAG, and system design questions are listed.
4. Click `Generate Report`.
5. Confirm interview rate, ATS average, skills, trends, suggestions, and roadmap are shown.

Expected result: the candidate can prepare for interviews immediately after a strong match.

## 8. Admin Analytics And Settings

1. Login as admin.
2. Open `Admin`.
3. Confirm analytics show users, profiles, jobs, resumes, applications, LLM RPM, and Auto Apply as `Off`.
4. Confirm `System Health` shows database, manual application mode, and LLM queue availability.
5. Update a prompt or n8n webhook setting.
6. Refresh the page and confirm the setting is still saved.
7. Confirm the `Audit Log` section records admin setting, role, and status changes.

Expected result: admin can manage prompts/integrations without enabling payment, recruiter portals, or risky auto-apply bots.

## 9. Multi-User Isolation

1. Create data as User A.
2. Log out.
3. Login as User B.
4. Open Dashboard, Job Matching, and Applications.

Expected result: User B must not see User A's candidates, jobs, resumes, packages, prep, or reports.

## 10. Deployment Readiness Smoke Check

Before Render/Vercel deployment:

1. Backend `.env` has a strong `AUTH_SECRET_KEY`.
2. `ALLOWED_ORIGINS` includes the Vercel frontend URL.
3. Frontend `VITE_API_BASE_URL` points to the Render backend URL if configured.
4. Admin settings still show Auto Apply as `Off`.
5. A normal candidate can complete the profile to application tracker flow.
