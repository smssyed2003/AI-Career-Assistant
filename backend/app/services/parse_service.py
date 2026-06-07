from io import BytesIO
from pathlib import Path
from typing import Optional

import docx
import pdfplumber
from fastapi import HTTPException, UploadFile


class ResumeParser:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

    def extract_text(self, file: UploadFile) -> str:
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported resume type: {file_extension}")

        content = file.file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded resume file is empty")

        if file_extension == ".pdf":
            return self._extract_pdf(content)
        if file_extension == ".docx":
            return self._extract_docx(content)
        if file_extension == ".txt":
            return content.decode("utf-8", errors="ignore")

        raise HTTPException(status_code=400, detail="Unsupported resume format")

    def extract_text_from_bytes(self, content: bytes, filename: str) -> str:
        file_extension = Path(filename).suffix.lower()
        if file_extension == ".pdf":
            return self._extract_pdf(content)
        if file_extension == ".docx":
            return self._extract_docx(content)
        if file_extension == ".txt":
            return content.decode("utf-8", errors="ignore")
        raise HTTPException(status_code=400, detail=f"Unsupported resume type: {file_extension}")

    def _extract_pdf(self, content: bytes) -> str:
        extracted_text = []
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                extracted_text.append(text)
        return "\n\n".join(extracted_text).strip()

    def _extract_docx(self, content: bytes) -> str:
        document = docx.Document(BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
        return "\n".join(paragraphs).strip()
