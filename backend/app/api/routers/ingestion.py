from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.profile import ResumeParseResult
from app.schemas.resume_upload import ResumeUploadRead
from app.services.gmail_service import GmailService
from app.services.llm_service import ProfileExtractor
from app.services.parse_service import ResumeParser
from app.services.resume_upload_service import ResumeUploadService

router = APIRouter()
parser = ResumeParser()
extractor = ProfileExtractor()
upload_service = ResumeUploadService()

@router.post("/ingest/resume", response_model=ResumeParseResult, summary="Ingest a resume file and extract profile data")
async def ingest_resume(
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    candidate_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Resume file is required")

    extracted_text = parser.extract_text(file)
    profile = extractor.extract_profile(extracted_text)
    upload_service.create(
        db,
        user_id=current_user.id,
        candidate_id=candidate_id,
        file_name=file.filename,
        file_type=file.content_type or "application/octet-stream",
        extracted_text=extracted_text,
        parsed_profile=profile.model_dump(mode="json"),
        source=source,
    )

    return ResumeParseResult(
        file_name=file.filename,
        file_type=file.content_type or "application/octet-stream",
        extracted_text=extracted_text,
        profile=profile,
        source=source,
    )


@router.get("/resume-uploads", response_model=List[ResumeUploadRead], summary="List stored resume upload history")
def list_resume_uploads(
    candidate_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return upload_service.list(db, user_id=current_user.id, candidate_id=candidate_id)


@router.get("/resume-uploads/{upload_id}", response_model=ResumeUploadRead, summary="Get a stored resume upload")
def get_resume_upload(upload_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    upload = upload_service.get(db, upload_id=upload_id, user_id=current_user.id)
    if not upload:
        raise HTTPException(status_code=404, detail="Resume upload not found")
    return upload

@router.post("/ingest/gmail/sync", response_model=List[ResumeParseResult], summary="Fetch resume attachments from Gmail and parse them")
def sync_gmail_resumes(query: Optional[str] = "has:attachment", current_user: User = Depends(get_current_user)):
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
