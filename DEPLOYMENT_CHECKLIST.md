# Free Deployment Checklist

Use this before deploying the MVP on Vercel and Render.

## Frontend On Vercel

- Deploy `frontend/`.
- Set the frontend API URL if your Vite config/environment requires it.
- Confirm the Vercel URL is added to backend `ALLOWED_ORIGINS`.
- Keep the app on the Hobby plan while validating the MVP.

## Backend On Render

- Deploy `backend/` as a Python web service.
- Set a strong `AUTH_SECRET_KEY`.
- Set `ALLOWED_ORIGINS` to your Vercel URL and local dev URL only.
- Set `LLM_REQUESTS_PER_MINUTE=12` to stay below the 15 RPM free-provider limit.
- Do not use local SQLite for real users on Render because free web service files are not permanent.

## Database

- For testing only: Render free Postgres is acceptable, but it expires after 30 days.
- For longer MVP usage: use a free external database tier such as Supabase, then export backups regularly.
- Do not store resume files on Render local disk.
- This project stores resume upload history as parsed database records for the free MVP path.

## Resume Uploads

- Supported upload types: `.pdf`, `.docx`, `.txt`.
- Uploaded resume text is stored in the database as upload history.
- Keep file-size limits conservative for the free tier.

## Admin Setup

- Create your account first so it becomes admin.
- If needed, manually update your local database user role to `admin`.
- Confirm normal users cannot access `/admin`.
- Confirm audit logs record role, status, and setting changes.

## Safety

- Keep auto-apply disabled.
- Keep application submission as manual review only.
- Do not store API keys in frontend code.
- Keep `.env`, `backend/data/`, and `local_tests/` out of GitHub.
- Add a privacy note before allowing real users to upload resumes.

## Manual Smoke Flow

1. Sign up as admin.
2. Sign up as candidate.
3. Create/edit candidate profile.
4. Upload a resume.
5. Generate resume versions.
6. Ingest a job.
7. Prepare an application package.
8. Update application tracker status.
9. Open Admin analytics and audit logs.
