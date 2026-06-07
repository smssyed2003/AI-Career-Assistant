from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.profile import ResumeParseResult
from app.services.gmail_service import GmailService
from app.services.llm_service import ProfileExtractor
from app.services.parse_service import ResumeParser

router = APIRouter()
parser = ResumeParser()
extractor = ProfileExtractor()

@router.post("/ingest/resume", response_model=ResumeParseResult, summary="Ingest a resume file and extract profile data")
async def ingest_resume(file: UploadFile = File(...), source: Optional[str] = None):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Resume file is required")

    extracted_text = parser.extract_text(file)
    profile = extractor.extract_profile(extracted_text)

    return ResumeParseResult(
        file_name=file.filename,
        file_type=file.content_type or "application/octet-stream",
        extracted_text=extracted_text,
        profile=profile,
        source=source,
    )

@router.post("/ingest/gmail/sync", response_model=List[ResumeParseResult], summary="Fetch resume attachments from Gmail and parse them")
def sync_gmail_resumes(query: Optional[str] = "has:attachment"):
    gmail = GmailService()
    messages = gmail.fetch_messages(query=query)
    results: List[ResumeParseResult] = []

    for message in messages:
        message_id = message.get("id")
        if not message_id:
            continue
        attachments = gmail.fetch_attachments(message_id)
        for attachment in attachments:
            filename = attachment["filename"]
            content = attachment["content"]
            try:
                extracted_text = parser.extract_text_from_bytes(content, filename)
                profile = extractor.extract_profile(extracted_text)
                results.append(
                    ResumeParseResult(
                        file_name=filename,
                        file_type=attachment.get("mime_type", "application/octet-stream"),
                        extracted_text=extracted_text,
                        profile=profile,
                        source="gmail",
                    )
                )
            except Exception:
                continue
    return results
