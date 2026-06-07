# AI Career Agent - n8n Workflows

This folder contains importable n8n workflow exports for local orchestration.

## Important Deployment Note

The initial hosted deployment target is still:

- Frontend: Vercel
- Backend: Render

n8n is included for local orchestration through `docker-compose.yml`. Hosting n8n online would require a third hosted service or n8n Cloud, so it is not required for the first free-first deployment.

## Local n8n Setup

1. Start services:
   ```powershell
   docker compose up
   ```

2. Open n8n:
   ```text
   http://localhost:5678
   ```

3. Login with:
   ```text
   user: admin
   password: admin
   ```

4. Import workflows from:
   ```text
   n8n/workflows
   ```

The Docker Compose file sets:

```text
BACKEND_API_URL=http://backend:8000/api
```

For a deployed backend, change this env var to:

```text
https://your-render-backend.onrender.com/api
```

## Workflows

### 1. Email Intake Profile Build

File:

```text
n8n/workflows/email-intake-profile-build.json
```

Purpose:

- Runs hourly.
- Calls `POST /api/ingest/gmail/sync`.
- Maps extracted profiles.
- Calls `POST /api/candidates`.
- Calls `POST /api/candidates/{candidate_id}/resumes/generate`.

Requirements:

- Backend Gmail OAuth env vars must be configured:
  - `GMAIL_CLIENT_ID`
  - `GMAIL_CLIENT_SECRET`
  - `GMAIL_REFRESH_TOKEN`

### 2. Job Discovery Webhook

File:

```text
n8n/workflows/job-discovery-webhook.json
```

Purpose:

- Exposes an n8n webhook.
- Accepts a safe job discovery payload.
- Calls `POST /api/job-discovery/ingest`.

Example payload:

```json
{
  "source": "company_careers",
  "source_url": "https://example.com/careers",
  "job_texts": [
    "Backend Engineer\nExample Company\nLocation: Remote\nSkills: Python, FastAPI, SQL"
  ]
}
```

### 3. Weekly Career Reports

File:

```text
n8n/workflows/weekly-career-report.json
```

Purpose:

- Runs weekly.
- Calls `GET /api/candidates`.
- Calls `POST /api/candidates/{candidate_id}/career-reports/generate`.

Email sending is not included yet because it requires SMTP/Gmail credentials. Add a Send Email node after report generation when email credentials are ready.

## Free-First Rule

These workflows do not scrape job portals, simulate clicks, or auto-submit applications. They only orchestrate safe backend APIs.
