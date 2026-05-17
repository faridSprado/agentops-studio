from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import AgentEvent


class EventLog:
    def __init__(self, db: Session, campaign_id: str):
        self.db = db
        self.campaign_id = campaign_id

    def emit(self, agent: str, status: str, payload: dict[str, Any] | None = None) -> None:
        last = self.db.query(func.max(AgentEvent.sequence)).filter(AgentEvent.campaign_id == self.campaign_id).scalar() or 0
        event = AgentEvent(
            campaign_id=self.campaign_id,
            sequence=last + 1,
            agent=agent,
            status=status,
            payload=payload or {},
        )
        self.db.add(event)
        self.db.commit()
