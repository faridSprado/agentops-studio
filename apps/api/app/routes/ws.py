import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import TypeAdapter

from app.core.db import SessionLocal
from app.models import AgentEvent, Campaign
from app.schemas import AgentEventRead

router = APIRouter(tags=["ws"])
event_adapter = TypeAdapter(AgentEventRead)
terminal = {"completed", "failed", "needs_review"}


@router.websocket("/ws/campaigns/{campaign_id}")
async def campaign_events(websocket: WebSocket, campaign_id: str):
    await websocket.accept()
    last = 0
    try:
        while True:
            db = SessionLocal()
            try:
                events = db.query(AgentEvent).filter(AgentEvent.campaign_id == campaign_id, AgentEvent.sequence > last).order_by(AgentEvent.sequence.asc()).all()
                campaign = db.get(Campaign, campaign_id)
                for event in events:
                    last = event.sequence
                    payload = event_adapter.validate_python(event).model_dump(mode="json")
                    await websocket.send_json(payload)
                if campaign and campaign.status in terminal and not events:
                    await websocket.send_json({"agent": "system", "status": campaign.status, "campaign_id": campaign_id, "score": campaign.score})
                    await websocket.close()
                    return
            finally:
                db.close()
            await asyncio.sleep(0.8)
    except WebSocketDisconnect:
        return
