from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "env": settings.env,
        "provider": settings.provider,
        "mock_mode": settings.mock_mode or settings.provider == "mock",
        "llm_enabled": settings.llm_enabled,
        "database": settings.database_url.split(":", 1)[0],
        "version": "1.2.1",
        "app": settings.app_name,
    }
