from functools import lru_cache
from pathlib import Path
from pydantic import AnyUrl
from pydantic_settings import BaseSettings
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    project_name: str = "AI Career Agent"
    debug: bool = True
    api_prefix: str = "/api"
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    database_url: str = "sqlite:///" + str(BASE_DIR / "data" / "dev.db")
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_refresh_token: str = ""
    chroma_server_url: str = "http://localhost:8000"
    n8n_webhook_url: str = "http://localhost:5678/webhook"
    gemini_api_key: str = ""
    gemini_model: str = "gemma-4-26b"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    sentry_dsn: str = ""

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
