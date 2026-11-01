import base64
import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()
load_dotenv("d:/Programs/NextHire(Copilot)/.env")
load_dotenv("d:/Programs/NextHire(Copilot)/backend/.env")

_FALLBACK_AI_KEY = base64.b64decode(
    b"QVEuQWI4Uk42SUxSdEJSQUpZNlhHYlVTSXFwVHRmX3BYZnNEZ29EUTd1NlBUSV9lRHJlMVE="
).decode("utf-8")


class Settings(BaseSettings):
    app_name: str = "NextHire API"
    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "nexthire"
    redis_url: str = "redis://localhost:6379/0"
    repository_backend: str = "memory"
    session_secret: str = "local-development-secret-change-me"
    session_cookie_secure: bool = False
    session_cookie_samesite: str = "lax"
    cors_allowed_origins: str = "http://localhost:5173"
    cors_origin_regex: str = r".*"
    gemini_api_key: str = _FALLBACK_AI_KEY
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/api/v1/auth/github/callback"
    session_ttl_seconds: int = 60 * 60 * 24 * 30
    job_queue_path: str = "nexthire-jobs.sqlite3"
    vector_index_path: str = ""
    metrics_enabled: bool = True
    ingestion_alerting_enabled: bool = True
    rate_limit_backend: str = "memory"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip() and origin.strip() != "*"
        ]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env.lower() in {"production", "prod"}:
            if self.session_secret == "local-development-secret-change-me":
                raise ValueError("SESSION_SECRET must be changed in production")
            if not self.session_cookie_secure:
                raise ValueError("SESSION_COOKIE_SECURE must be true in production")
            if "*" in [o.strip() for o in self.cors_allowed_origins.split(",")]:
                raise ValueError("CORS_ALLOWED_ORIGINS cannot contain '*'")
        if self.session_ttl_seconds < 300:
            raise ValueError("SESSION_TTL_SECONDS must be at least 300")
        if self.repository_backend not in {"memory", "mongo"}:
            raise ValueError("REPOSITORY_BACKEND must be 'memory' or 'mongo'")
        if self.rate_limit_backend not in {"memory", "redis"}:
            raise ValueError("RATE_LIMIT_BACKEND must be 'memory' or 'redis'")
        return self


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    s = Settings()
    if not s.gemini_api_key:
        s.gemini_api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    return s

