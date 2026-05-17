from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV = Path(__file__).resolve().parents[4] / ".env"
API_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    app_name: str = "Multimedia AgentOps Studio API"
    env: str = "dev"
    database_url: str = "sqlite:///./agentops.db"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    llm_provider: str = "groq"
    model_provider: str | None = None
    mock_mode: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    max_output_tokens: int = 1200
    quality_threshold: int = 82
    max_revisions: int = 1
    export_dir: str = "storage/exports"
    use_langgraph: bool = False
    max_request_bytes: int = 350_000
    max_brand_asset_bytes: int = 200_000

    model_config = SettingsConfigDict(env_file=(str(ROOT_ENV), str(API_ENV), ".env"), extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def provider(self) -> str:
        provider = self.model_provider or self.llm_provider
        return provider.lower().strip()

    @property
    def llm_enabled(self) -> bool:
        if self.mock_mode or self.provider == "mock":
            return False
        if self.provider == "openai":
            return bool(self.openai_api_key)
        if self.provider == "groq":
            return bool(self.groq_api_key)
        return False

    @property
    def is_production(self) -> bool:
        return self.env.lower() in {"prod", "production"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
