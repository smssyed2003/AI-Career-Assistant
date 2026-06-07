from io import BytesIO

from fastapi.testclient import TestClient
from docx import Document

from app.main import app


def build_docx_bytes(text_lines):
    document = Document()
    for line in text_lines:
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def test_ingest_resume_endpoint_returns_parsed_profile():
    client = TestClient(app)
    content = build_docx_bytes(["Jane Doe", "Senior Engineer", "jane@example.com"])
    files = {
        "file": (
            "resume.docx",
            content,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }

    response = client.post("/api/ingest/resume", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["file_name"] == "resume.docx"
    assert "Jane Doe" in payload["extracted_text"]
    assert payload["profile"]["full_name"] == "Jane Doe"
