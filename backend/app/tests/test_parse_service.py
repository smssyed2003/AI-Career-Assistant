from io import BytesIO

import pytest
from fastapi import UploadFile
from docx import Document

from app.services.parse_service import ResumeParser


def build_docx_bytes(text_lines):
    document = Document()
    for line in text_lines:
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def test_docx_resume_parsing():
    parser = ResumeParser()
    content = build_docx_bytes(["Jane Doe", "AI Product Manager", "jane@example.com"])
    file = UploadFile(BytesIO(content), filename="resume.docx")

    extracted = parser.extract_text(file)

    assert "Jane Doe" in extracted
    assert "AI Product Manager" in extracted
    assert "jane@example.com" in extracted


def test_unsupported_resume_type_raises():
    parser = ResumeParser()
    file = UploadFile(BytesIO(b"hello"), filename="resume.txt")

    with pytest.raises(Exception):
        parser.extract_text(file)
