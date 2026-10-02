from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core Application
    app_name: str = "PERSONA-X"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Database & Supabase Infrastructure
    database_url: str = "sqlite:///./data/persona_x.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    supabase_url: Optional[str] = Field(default="")
    supabase_anon_key: Optional[str] = Field(default="")
    supabase_service_role_key: Optional[str] = Field(default="")

    # AI Providers
    groq_api_key: str = Field(default="")
    groq_model: str = "openai/gpt-oss-120b"
    groq_fallback_models: str = "openai/gpt-oss-20b,qwen/qwen3.8-27b"

    gemini_api_key: Optional[str] = Field(default="")
    openai_api_key: Optional[str] = Field(default="")
    anthropic_api_key: Optional[str] = Field(default="")

    default_ai_provider: str = "groq"

    # Security & Auth
    jwt_secret_key: str = "persona-x-production-secret-change-in-prod-super-secure-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    sentry_dsn: Optional[str] = Field(default="")

    # Research Execution & Worker Configuration
    research_max_sources: int = 50
    research_max_depth: int = 3
    research_timeout_seconds: int = 30

    research_worker_count: int = 4
    research_max_queries_per_job: int = 8
    research_max_attempts: int = 3
    research_retry_base_seconds: float = 2.0
    research_rate_limit_per_minute: int = 30
    research_stale_job_seconds: int = 1800
    research_cache_ttl_seconds: int = 86400
    research_auto_start: bool = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def groq_fallback_models_list(self) -> List[str]:
        return [m.strip() for m in self.groq_fallback_models.split(",") if m.strip()]

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and (self.supabase_anon_key or self.supabase_service_role_key))

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()