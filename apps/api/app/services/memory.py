import re
from typing import Any

from sqlalchemy.orm import Session

from app.models import BrandAsset


def tokens(text: str) -> set[str]:
    return {item for item in re.findall(r"[a-záéíóúñü0-9]{3,}", text.lower())}


def project_memory(db: Session, project_id: str, query: str, limit: int = 6) -> list[dict[str, Any]]:
    assets = db.query(BrandAsset).filter(BrandAsset.project_id == project_id).all()
    q = tokens(query)
    ranked = []
    for asset in assets:
        content = asset.content[:4000]
        score = len(q.intersection(tokens(content)))
        ranked.append((score, asset))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [
        {"label": asset.label, "content": asset.content[:1800], "score": score}
        for score, asset in ranked[:limit]
        if asset.content.strip()
    ]
