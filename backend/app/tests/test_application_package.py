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


def test_resume_generation_and_application_package():
    client = TestClient(app)

    candidate_response = client.post(
        "/api/candidates",
        json={
            "full_name": "Sam Builder",
            "email": f"sam-{uuid.uuid4().hex[:8]}@example.com",
            "summary": "Backend developer with Python, FastAPI, SQL, and AI project experience.",
            "skills": ["Python", "FastAPI", "SQL", "Docker", "RAG"],
            "projects": [
                {
                    "name": "Career Agent",
                    "description": "Built a FastAPI and RAG based job matching system.",
                    "technologies": ["Python", "FastAPI", "RAG"],
                }
            ],
            "preferences": {"locations": ["Remote"], "remote_preference": "Remote"},
        },
    )
    assert candidate_response.status_code == 200
    candidate_id = candidate_response.json()["id"]

    job_response = client.post(
        "/api/jobs/ingest",
        data={
            "text": (
                "AI Backend Engineer\n"
                "Practical AI Labs\n"
                "Location: Remote\n"
                "Skills: Python, FastAPI, SQL, Docker, RAG\n"
                "Responsibilities: Build APIs and retrieval augmented generation services."
            )
        },
    )
    assert job_response.status_code == 200
    job_id = job_response.json()["id"]

    resume_response = client.post(f"/api/candidates/{candidate_id}/resumes/generate")
    assert resume_response.status_code == 200
    resume_payload = resume_response.json()
    assert resume_payload["generated_count"] == 7
    assert len(resume_payload["resumes"]) == 7

    package_response = client.post(f"/api/jobs/{job_id}/application-package/{candidate_id}")
    assert package_response.status_code == 200
    package = package_response.json()
    assert package["candidate_id"] == candidate_id
    assert package["job_id"] == job_id
    assert package["optimized_resume_id"] is not None
    assert package["cover_letter"]
    assert package["email_template"]
    assert package["status"] == "prepared"
    assert 0 <= package["interview_probability"] <= 100

    list_response = client.get(f"/api/application-packages?candidate_id={candidate_id}")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
