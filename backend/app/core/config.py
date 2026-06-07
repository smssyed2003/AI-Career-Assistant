from functools import lru_cache
import json
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

    project_name: str = "AI Career Agent"
    debug: bool = True
    api_prefix: str = "/api"
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
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
    llm_queue_enabled: bool = True
    llm_requests_per_minute: int = 12
    llm_max_retries: int = 3
    sentry_dsn: str = ""

    @property
    def cors_allowed_origins(self) -> list[str]:
        value = self.allowed_origins.strip()
        if value.startswith("["):
            try:
                parsed = json.loads(value)
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in value.split(",") if origin.strip()]

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
