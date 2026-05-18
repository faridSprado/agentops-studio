from fastapi import APIRouter, Response

from app.core.config import get_settings

router = APIRouter(tags=["health"])


def build_health_payload() -> dict[str, object]:
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


@router.get("/health")
def health() -> dict[str, object]:
    return build_health_payload()


@router.head("/health", include_in_schema=False)
def health_head() -> Response:
    return Response(status_code=200)
