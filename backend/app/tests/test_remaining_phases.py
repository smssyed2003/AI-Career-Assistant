import uuid

from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_discovery_interview_and_career_report_flow():
    client = TestClient(app)

    candidate_response = client.post(
        "/api/candidates",
        json={
            "full_name": "Taylor FreeTier",
            "email": f"taylor-{uuid.uuid4().hex[:8]}@example.com",
            "summary": "Python backend developer building AI and RAG projects.",
            "skills": ["Python", "FastAPI", "SQL", "RAG"],
            "projects": [{"name": "RAG Matcher", "description": "Matched jobs using RAG and FastAPI."}],
        },
    )
    assert candidate_response.status_code == 200
    candidate_id = candidate_response.json()["id"]

    job_text = (
        "AI Backend Engineer\n"
        "Free Startup\n"
        "Location: Remote\n"
        "Skills: Python, FastAPI, SQL, Docker, RAG\n"
        "Responsibilities: Build APIs and retrieval systems."
    )
    discovery_response = client.post(
        "/api/job-discovery/ingest",
        json={"source": "company_careers", "source_url": "https://example.com/careers", "job_texts": [job_text, job_text]},
    )
    assert discovery_response.status_code == 200
    discovery = discovery_response.json()
    assert discovery["created_count"] == 1
    assert discovery["duplicate_count"] == 1
    job_id = discovery["jobs"][0]["id"]

    source_response = client.get("/api/job-discovery/sources")
    assert source_response.status_code == 200
    assert len(source_response.json()) >= 2

    package_response = client.post(f"/api/jobs/{job_id}/application-package/{candidate_id}")
    assert package_response.status_code == 200

    interview_response = client.post(f"/api/jobs/{job_id}/interview-prep/{candidate_id}")
    assert interview_response.status_code == 200
    questions = interview_response.json()
    question_types = {question["question_type"] for question in questions}
    assert {"hr", "technical", "coding", "ai", "llm", "rag", "system_design"}.issubset(question_types)

    report_response = client.post(f"/api/candidates/{candidate_id}/career-reports/generate")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["candidate_id"] == candidate_id
    assert "career_roadmap" in report

    queue_response = client.get("/api/llm/queue/status")
    assert queue_response.status_code == 200
    assert "requests_per_minute" in queue_response.json()
