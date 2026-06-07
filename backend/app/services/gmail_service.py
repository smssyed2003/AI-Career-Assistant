import base64
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import settings

GMAIL_TOKEN_URI = "https://oauth2.googleapis.com/token"


class GmailService:
    def __init__(self):
        self.credentials = self._build_credentials()
        self.service = self._build_service()

    def _build_credentials(self) -> Credentials:
        if not all([settings.gmail_client_id, settings.gmail_client_secret, settings.gmail_refresh_token]):
            raise HTTPException(status_code=500, detail="Gmail credentials are not configured")

        creds = Credentials(
            token=None,
            refresh_token=settings.gmail_refresh_token,
            token_uri=GMAIL_TOKEN_URI,
            client_id=settings.gmail_client_id,
            client_secret=settings.gmail_client_secret,
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )
        if creds.expired or not creds.valid:
            creds.refresh(Request())
        return creds

    def _build_service(self):
        return build("gmail", "v1", credentials=self.credentials)

    def fetch_messages(self, query: Optional[str] = "has:attachment") -> List[Dict[str, Any]]:
        response = self.service.users().messages().list(userId="me", q=query, maxResults=20).execute()
        return response.get("messages", [])

    def fetch_attachments(self, message_id: str) -> List[Dict[str, Any]]:
        message = self.service.users().messages().get(userId="me", id=message_id, format="full").execute()
        attachments = []
        for part in message.get("payload", {}).get("parts", []):
            if part.get("filename") and part.get("body", {}).get("attachmentId"):
                attachment_id = part["body"]["attachmentId"]
                attachment_data = self.service.users().messages().attachments().get(
                    userId="me", messageId=message_id, id=attachment_id
                ).execute()
                data = base64.urlsafe_b64decode(attachment_data.get("data", ""))
                attachments.append({
                    "filename": part["filename"],
                    "mime_type": part.get("mimeType"),
                    "content": data,
                })
        return attachments
