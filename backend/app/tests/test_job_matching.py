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


def test_job_ingestion_and_matching():
    client = TestClient(app)

    candidate_email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    candidate_payload = {
        "full_name": "Alex Candidate",
        "email": candidate_email,
        "phone": "555-1111",
        "summary": "Skilled Python developer with AWS and SQL experience.",
        "skills": ["Python", "AWS", "SQL", "FastAPI"],
    }
    create_candidate = client.post("/api/candidates", json=candidate_payload)
    assert create_candidate.status_code == 200
    candidate_id = create_candidate.json()["id"]

    job_text = (
        "Senior Backend Engineer\n"
        "Awesome Startup\n"
        "Location: Remote\n\n"
        "We are seeking a Senior Backend Engineer experienced in Python, FastAPI, SQL, and AWS.\n"
        "Requirements:\n"
        "- 5+ years of backend development\n"
        "- Experience with relational databases and cloud APIs\n"
        "- Strong Python programming skills\n"
    )

    ingest_response = client.post("/api/jobs/ingest", data={"text": job_text})
    assert ingest_response.status_code == 200
    job_data = ingest_response.json()
    assert job_data["title"] == "Senior Backend Engineer"
    assert "Python" in job_data["description"]

    match_response = client.get(f"/api/jobs/match/{candidate_id}")
    assert match_response.status_code == 200
    matches = match_response.json()
    assert len(matches) >= 1
    assert any(match["job_id"] == job_data["id"] for match in matches)
    job_match = next(match for match in matches if match["job_id"] == job_data["id"])
    assert job_match["score"] >= 0.0

    gap_response = client.get(f"/api/jobs/{job_data['id']}/skill-gap/{candidate_id}")
    assert gap_response.status_code == 200
    gap_data = gap_response.json()
    assert gap_data["candidate_id"] == candidate_id
    assert gap_data["job_id"] == job_data["id"]
    assert "python" in gap_data["candidate_skills"]

    readiness_response = client.get(f"/api/jobs/{job_data['id']}/readiness/{candidate_id}")
    assert readiness_response.status_code == 200
    readiness = readiness_response.json()
    assert readiness["candidate_id"] == candidate_id
    assert readiness["job_id"] == job_data["id"]
    assert 0.0 <= readiness["readiness_score"] <= 1.0
    assert "matched_skills" in readiness
    assert "recommended_learning" in readiness
