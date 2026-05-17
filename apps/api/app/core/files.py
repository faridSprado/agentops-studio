from pathlib import Path

from app.core.config import get_settings


def ensure_dirs() -> None:
    Path(get_settings().export_dir).mkdir(parents=True, exist_ok=True)
