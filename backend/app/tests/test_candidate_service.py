from app.services.candidate_service import CandidateService
from app.schemas.candidate import CandidateCreate
from app.db.session import SessionLocal, engine
from app.db.base import Base


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)


def test_candidate_create_and_retrieve():
    service = CandidateService()
    candidate_in = CandidateCreate(
        full_name="Jane Doe",
        email="jane@example.com",
        summary="AI product manager with 6 years of experience.",
        skills=["product management", "data strategy"],
    )

    with SessionLocal() as db:
        candidate = service.create(db, candidate_in)
        assert candidate.id is not None
        stored = service.get_by_email(db, "jane@example.com")
        assert stored is not None
        assert stored.full_name == "Jane Doe"
